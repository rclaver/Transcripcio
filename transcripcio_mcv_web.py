#!/usr/bin/python3
# -*- coding: UTF8 -*-
"""
@created: 17-10-2025
@author: rafael
@description: Transcripció d'àudios del conjunt de dades Mozilla Common Voice

Instalació prèvia:
pip install flask flask-socketio
pip install -r requirements.txt
pip install --user pygame pydub speechrecognition pyaudio
"""

import os, threading, time
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pygame
from pydub import AudioSegment
import speech_recognition as sr

# -----------------
# variables globals
#
C_NONE="\033[0m"
CB_YLW="\033[1;33m"
CB_BLU="\033[1;34m"

base_dir = "/home/rafael/projectes/Transcripcio"
# Les rutes son relatives
dir_static = "static"
dir_templates = "templates"
dir_audios = "common-voice/audios"
cfg_file = f"{base_dir}/transcripcio.cfg" #arxiu de configuració: conté les dades de la darrera execució

old_file = None
line = 0	#linia actual de l'arxiu del conjunt de dades mcv

dataset_file = ""
audio_file_path = ""
registres = ""
duration = 0
transcription = ""
transcriptionless = "ATENCIÓ: Aquest registre no conté cap transcripció. Escolta l'àudio i crea una nova transcripció. Si no s'escolta cap àudio, ignora'l i passa al registre següent."
selected_language = "ca-ES"  # Idioma per defecte
languages = {
   "ca-ES": "Català",
   "es-ES": "Español",
   "en-US": "English"
}
attr_gender = ""
registre_actual = ""
thread = None
espera = True
is_playing = False
default_state = "Selecciona el conjunt de dades de Mozilla Common Voice"

# -----------------
# funció principal
#
def crear_app():
   app = Flask(__name__) #instancia de Flask
   socketio = SocketIO(app)
   #key_secret = os.getenv("API_KEY")

   # -------------------
   # Auxiliary functions
   #

   def carrega_configuracio():
      # Llegeix de l'arxiu de configuració les dades de la darrera execució:
      # - la ruta de l'arxiu del conjunt de dades
      # - la darrera línia precessada de l'arxiu del conjunt de dades
      global line, old_file
      try:
         with open(cfg_file, 'r', encoding='utf-8') as file:
            reg = file.readline().strip("{}").split(",")
         for e in reg:
            match e[0]:
               case "line": line = e[1]-1
               case "file": old_file = e[1]
      except IOError as e:
         if (e.errno != 2): #file not found
            socketio.emit('information', {'error':f"Error en llegir l'arxiu de configuració: {str(e)}"})

   def desa_configuracio():
      # Desa a l'arxiu de configuració les dades de la darrera execució:
      # - la ruta de l'arxiu del conjunt de dades
      # - la darrera línia precessada de l'arxiu del conjunt de dades
      try:
         cfg = "{" + "'line':" + str(line) + ",'file':'" + dataset_file.filename +"'}"
         with open(cfg_file, 'w', encoding='utf-8') as file:
            file.write(cfg)
      except Exception as e:
         socketio.emit('information', {'error':f"Error en escriure l'arxiu de configuració: {str(e)}"})

   def normalize_gender(gender):
      match gender:
         case "home": return "male_masculine"
         case "dona": return "female_feminine"

   def toggle_buttons_state(enabled):
      # Habilita o deshabilita botons durant la transcripció
      pass

   def list_to_tsv(reg):
      # Converteix una llista en un string separat per tabulador
      return '\t'.join(str(x) for x in reg)

   pygame.mixer.init(11025)  # raises exception on fail
   carrega_configuracio()

   @app.route("/index")
   def index():
      return render_template("index.tpl")

   # ---
   # GUI
   #
   @app.route("/transcripcio", methods = ["GET", "POST"])
   def upload_mcv_file():
      global dataset_file, registres, selected_language
      if request.method == "POST":
         dataset_file = request.files['arxiu_dataset']
         idioma = request.form.get("seleccio_idioma")
         if idioma:
            selected_language = idioma

      if dataset_file:
         print(f"{CB_YLW}arxiu_dataset:{C_NONE} {dataset_file}.")
         registres = dataset_file.read().decode('utf-8')
         dataset_file.seek(0)  # Volver al inicio por si necesitas el objeto file completo
         return render_template("transcripcio.tpl", arxiu=dataset_file.filename, idioma=languages[selected_language])
      else:
         return render_template("index.tpl")

   # -----------------
   # Process functions
   #
   def processar_dataset():
      global registres, registre_actual
      global espera, line
      global transcription, transcriptionless, duration
      global dir_audios, audio_file_path
      try:
         linies = registres.splitlines()

         for n, registre_actual in enumerate(linies, line):
            line += 1
            if line == 1:
               continue
            print(f"{CB_YLW}processar_dataset():\n\t{CB_BLU}line:{CB_YLW}{line}\n\t{CB_BLU}registre_actual: {C_NONE}{registre_actual}.")

            espera = True
            fields = registre_actual.split("\t")
            arxiu = fields[2]
            if arxiu:
               transcription = fields[6]
               if transcription:
                  socketio.emit('new_transcription', {'text':transcription})
               else:
                  socketio.emit('new_transcription', {'placeholder':transcriptionless})
                  duration = int(fields[3])//1000 if fields[3] else 0

               socketio.emit('information', {'arxiu_audio':f"àudio actiu: ({str(line)}) {arxiu}"})
               audio_file_path = f"{dir_audios}/{arxiu}"
               print(f"\t{CB_BLU}audio_file_path: {CB_YLW}{audio_file_path}\n\t{CB_BLU}duration: {CB_YLW}{duration}s{C_NONE}.")
            else:
               espera = False
               continue

            while espera:
               pass

      except Exception as e:
         socketio.emit('information', {'error':f"Error processant el dataset: {str(e)}"})

   def next_audio(text):
      # Salta a l'àudio següent. Prèviament desa el registre actual
      global espera, thread
      #if save_record(text):
      save_record(text)
      # desbloquea el bucle para pasar al siguiente registro
      if not thread or not thread.is_alive():
         espera = False
      else:
         print(f"{CB_BLU}\tthread.is_alive{C_NONE}")
         socketio.emit('information', {'error':"thread.is_alive"})

   def genera_registre(text):
      global registre_actual, attr_gender
      cont = True if (text) else False
      if text:
         new_rec = registre_actual.split("\t")
         new_rec[6] = text
         cont = True if (new_rec[9]) else False
         if not new_rec[9]:
            if attr_gender:
               new_rec[9] = normalize_gender(attr_gender)
               cont = True
            else:
               socketio.emit('information', {'error':"No has seleccionat l'atribut de gènere de l'àudio"})
         else:
            socketio.emit('information', {'error':"No hi ha cap text transcrit"})

      return list_to_tsv(new_rec) if cont else False

   def play_audio():
      # Reprodueix l'arxiu d'àudio seleccionat
      global is_playing, duration
      if not audio_file_path:
         is_playing = False
         socketio.emit('information', {'error':"Error: No hi ha cap arxiu d'àudio actiu"})
         return

      try:
         pygame.mixer.music.load(audio_file_path)
         pygame.mixer.music.play()
         is_playing = True
         socketio.emit('information', {'info':"Reproduint àudio..."})

         def check_if_play_audio(temps):
            global is_playing
            while temps and is_playing and pygame.mixer.music.get_busy():
               time.sleep(1)
               socketio.emit('information', {'info':f"Reproduint àudio... ({temps})"})
               temps -=1
            stop_audio()

         # executar en un fil separat per a no bloquejar l'interfase
         fil = threading.Thread(target=check_if_play_audio(duration))
         fil.daemon = True
         fil.start()

      except Exception as e:
         is_playing = False
         socketio.emit('information', {'error':f"Error en reproduir l'àudio: {str(e)}"})

   def stop_audio():
      # Atura la reproducció d'àudio
      global is_playing
      if pygame.mixer.music.get_busy():
         pygame.mixer.music.fadeout(100)
         time.sleep(0.1)
      pygame.mixer.music.unload()
      is_playing = False
      toggle_buttons_state(True)
      socketio.emit('information', {'info':"Àudio finalitzat"})

   def start_transcription():
      global thread
      if not audio_file_path:
         socketio.emit('information', {'error':"Error: No hi ha cap arxiu d'àudio actiu"})
         return

      # Deshabilitar botons durant la transcripció
      toggle_buttons_state(False)
      socketio.emit('information', {'info':"Transcribint l'àudio... pot trigar una estona.", 'estat':"transcripcio"})

      # executar en un fil separat per a no bloquejar l'interfase
      if not thread or not thread.is_alive():
         thread = threading.Thread(target=transcribe_audio)
         thread.daemon = True
         thread.start()

   def transcribe_audio():
      # Converteix l'arxiu d'àudio a text utilitzant SpeechRecognition
      try:
         # Convertir MP3 a WAV si és necessari
         if audio_file_path.lower().endswith('.mp3'):
            wav_path = f"{base_dir}/static/tmp/" + os.path.basename(audio_file_path).replace('.mp3', '.wav')
            audio = AudioSegment.from_mp3(audio_file_path)
            audio.export(wav_path, format="wav")
         else:
            wav_path = audio_file_path
         #print(f"{CB_YLW}transcribe_audio():\n\t{CB_BLU}audio_file_path: {CB_YLW}{audio_file_path}\n\t{CB_BLU}wav_path: {CB_YLW}{wav_path}{C_NONE}")

         # Inicialitzar reconeixedor
         recognizer = sr.Recognizer()

         # Carregar l'arxiu d'àudio
         with sr.AudioFile(wav_path) as source:
            # Ajustar pel soroll ambient
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)

         # Realitzar transcripció
         # for testing purposes, we're just using the default API key
         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
         text = recognizer.recognize_google(audio_data, language=f"{selected_language}")

         # actualitzar l'interfase en el fil principal
         update_transcription(text, "Transcripció completada amb éxit", "")

      except sr.UnknownValueError:
         update_transcription("", "", "Error: No he pogut entendre l'àudio")
      except sr.RequestError as e:
         update_transcription("", "", f"Error en el servei: {str(e)}")
      except Exception as e:
         update_transcription("", "", f"Error inesperat: {str(e)}")
      finally:
         # eliminar, si existeix, l'arxiu temporal
         if audio_file_path.lower().endswith('.mp3') and os.path.exists(wav_path):
            os.remove(wav_path)

   def update_transcription(text, status, error):
      # Actualitza l'interfase amb el resultat de la transcripció
      toggle_buttons_state(True)
      if text:
         socketio.emit('new_transcription', {'text':text})
         socketio.emit('information', {'info':status})
      elif error:
         socketio.emit('information', {'error':error})
      else:
         socketio.emit('information', {'error':"No hi ha text transcrit"})

   def save_record(text):
      # Desa el registre en l'arxiu de sortida (append)
      global espera
      nou_registre = genera_registre(text)

      if nou_registre:
         file_path = dataset_file.replace("-corpus-", "-reported-audios-")

         try:
            with open(file_path, 'a', encoding='utf-8') as file:
               file.write(nou_registre)
            socketio.emit('information', {'info':f"Transcripció desada a: {file_path}"})
            desa_configuracio()
            espera = False
            return True
         except Exception as e:
            socketio.emit('information', {'error':f"Error en desar el registre: {str(e)}"})
      else:
         socketio.emit('information', {'error':"No hi ha cap transcripció"})

      return False

   # Retorna a l'inici
   def sortir():
      global dataset_file
      dataset_file = ""
      stop_audio()

# -------------
# socket events
#
   # Esdeveniment que es dispara quan un client es connecta
   @socketio.on('connect')
   def handle_connect():
      print(f"{CB_YLW}Client connectat{C_NONE}")

   @socketio.on('start')
   def handle_start():
      global line, old_file, dataset_file
      print(f"{CB_YLW}START{C_NONE}")
      # verificació de la recuperació de l'estat anterior (últim registre processat)
      if not old_file or dataset_file != old_file:
         line = 0

      # Executar en un fil separat per a no bloquejar l'interfase
      thread = threading.Thread(target=processar_dataset)
      thread.daemon = True
      thread.start()

   @socketio.on('seleccioGenere')
   def handle_genre(g):
      global attr_gender
      print(f"{CB_YLW}seleccio de gènere{C_NONE}")
      attr_gender = g

   @socketio.on('next')
   def handle_next(text):
      print(f"{CB_YLW}botó següent{C_NONE}")
      next_audio(text)

   @socketio.on('play_audio')
   def handle_play_audio():
      global thread
      print(f"{CB_YLW}botó play_audio{C_NONE}")
      if not thread or not thread.is_alive():
         thread = threading.Thread(target=play_audio)
         thread.start()
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")

   @socketio.on('stop')
   def handle_stop():
      print(f"{CB_YLW}botó stop{C_NONE}")
      stop_audio()

   @socketio.on('transcripcio')
   def handle_transcripcio():
      global thread
      print(f"{CB_YLW}botó transcripcio{C_NONE}")
      if not thread or not thread.is_alive():
         start_transcription()
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")

   @socketio.on('save')
   def handle_save(text):
      print(f"{CB_YLW}botó save{C_NONE}")
      save_record(text)

   @socketio.on('exit')
   def handle_exit():
      sortir()

   return app

if __name__ == "__main__":
   app = crear_app()
   # Inicia los servicios flask en la terminal, lo cual, activa el acceso web
   # equivale a ejecutar en una terminal el comando: flask run
   # así, se activa el reconocimento de las aplicaciones Python en el puerto 5000 de localhost
   app.run(host='localhost', port=5000, debug=False)
