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
dir_static = "static"
dir_templates = "templates"
#arxiu de configuració: conté les dades de la darrera execució
cfg_file = f"{base_dir}/transcripcio.cfg"

dataset_file = ""
registres = ""
duration = 0
audio_path = "common-voice/audios"
audio_file_path = ""
audio_file = ""
transcription = ""
transcriptionless = "ATENCIÓ: Aquest registre no conté cap transcripció. Escolta l'àudio i crea una nova transcripció."
selected_language = "ca-ES"  # Idioma per defecte
languages = {
   "ca-ES": "Català",
   "es-ES": "Español",
   "en-US": "English"
}
attr_gender = ""
registre = ""
nou_registre = None
old_file = None
line = 0	#linia actual de l'arxiu del conjunt de dades mcv
thread = None
espera = True
is_playing = False
channel = None
default_state = "Selecciona el conjunt de dades de Mozilla Common Voice"
status_text = default_state

# -------------------
# Auxiliary functions
#
""" Converteix una llista en un string separat per tabulador """
def list_to_tsv(reg):
   return '\t'.join(str(x) for x in reg)

"""
Llegeix de l'arxiu de configuració les dades de la darrera execució:
- la ruta de l'arxiu del conjunt de dades
- la darrera línia precessada de l'arxiu del conjunt de dades
"""
def carrega_configuracio():
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
         status_text.set(f"Error en llegir l'arxiu de configuració: {str(e)}")

"""
Desa a l'arxiu de configuració les dades de la darrera execució:
- la ruta de l'arxiu del conjunt de dades
- la darrera línia precessada de l'arxiu del conjunt de dades
"""
def desa_configuracio():
   try:
      cfg = "{" + "'line':" + str(line) + ",'file':'" + dataset_file.filename +"'}"
      with open(cfg_file, 'w', encoding='utf-8') as file:
         file.write(cfg)
   except Exception as e:
      status_text.set(f"Error en escriure l'arxiu de configuració: {str(e)}")


# -----------------
# funció principal
#
def crear_app():
   app = Flask(__name__) #instancia de Flask
   socketio = SocketIO(app)
   #key_secret = os.getenv("API_KEY")

   # Inicialitzar pygame per a la reproducció d'àudio
   pygame.mixer.init(11025)  # raises exception on fail
   carrega_configuracio()

   @app.route("/index")
   def index():
      return render_template("index.tpl")

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


   def processar_dataset():
      global registres, espera, line, transcription, transcriptionless, duration, audio_path, audio_file_path, audio_file, dataset_file
      try:
         linies = registres.splitlines()

         for n_rec, registre in enumerate(linies, line):
            line += 1
            if line == 1:
               continue
            print(f"{CB_YLW}processar_dataset\n\t{CB_BLU}line:{CB_YLW}{line}\n\t{CB_BLU}registre: {C_NONE}{registre}.")

            espera = True
            fields = registre.split("\t")
            # mira si transcription està buit
            transcription = fields[6]
            if transcription:
               socketio.emit('new_transcription', {'text':transcription})
            else:
               socketio.emit('new_transcription', {'text':transcriptionless})
            arxiu = fields[2]
            duration = int(fields[3])//1000 if fields[3] else 0
            if arxiu:
               audio_actiu = f"àudio actiu: ({str(line)}) {arxiu}"
               socketio.emit('information', {'arxiu_audio':f"àudio actiu: ({str(line)}) {arxiu}"})
               #audio_file_path = os.path.dirname(dataset_file.filename) + "/audios/" + arxiu
               audio_file_path = f"{audio_path}/{arxiu}"
               audio_file = arxiu
               print(f"\t{CB_BLU}audio_file_path: {CB_YLW}{audio_file_path}\n\t{CB_BLU}duration: {CB_YLW}{duration}s{C_NONE}.")

            while espera:
               pass

      except Exception as e:
         socketio.emit('information', {'error':f"Error llegint l'arxiu: {str(e)}"})

   """
   Permet saltar a l'àudio següent. Prèviament desa, si existeix, el registre actual
   """
   def next_audio(text):
      global espera, nou_registre
      if text:
         if genera_registre(registre, text):
            #Ahora hay que guardar (append) el registro en un nuevo archivo
            save_record(list_to_tsv(nou_registre))

      # desbloquea el bucle para pasar al siguiente registro
      espera = False

   def genera_registre(reg, text):
      global nou_registre
      nou_registre = reg.split("\t")
      nou_registre[6] = text
      if not nou_registre[9]:
         if attr_gender:
            nou_registre[9] = normalize_gender(attr_gender)
         else:
            socketio.emit('information', {'error':"No has seleccionat l'atribut de gènere de l'àudio"})
            return False
      return True

   """Reprodueix l'arxiu d'àudio seleccionat"""
   def play_audio():
      global is_playing, channel
      if not audio_file_path:
         is_playing = False
         socketio.emit('information', {'error':"Error: No hi ha cap arxiu d'àudio actiu"})
         return

      try:
         #pygame.mixer.music.load(audio_file_path)
         #pygame.mixer.music.play()
         sound = pygame.mixer.Sound(audio_file_path)
         channel = sound.play()
         is_playing = True
         socketio.emit('information', {'info':"Reproduint àudio..."})
         # Executar en un fil separat per a no bloquejar l'interfase
         fil = threading.Thread(target=check_if_play_audio)
         fil.daemon = True
         fil.start()

      except Exception as e:
         socketio.emit('information', {'error':f"Error en reproduir l'àudio: {str(e)}"})

   def check_if_play_audio():
      global is_playing, duration, channel
      def temporitzador(temps):
         while temps and is_playing and channel.get_busy():
            time.sleep(1)
            socketio.emit('information', {'info':f"playing audio ({temps})"})
            temps -=1
         estat = " playing" if channel.get_busy() else " stop"
         socketio.emit('information', {'info':"Fi de la reproducció de l'àudio.", 'estat':estat})
         pygame.mixer.music.unload()

      temporitzador(duration)

   """Atura la reproducció d'àudio"""
   def stop_audio():
      global is_playing
      pygame.mixer.music.stop()
      pygame.mixer.music.unload()
      is_playing = False
      toggle_buttons_state(True)
      socketio.emit('information', {'info':"Àudio finalitzat", 'estat':"stop"})

   def start_transcription():
      global thread
      if not audio_file_path:
         socketio.emit('information', {'error':"Error: No hi ha cap arxiu d'àudio actiu"})
         return

      # Deshabilitar botons durant la transcripció
      toggle_buttons_state(False)
      socketio.emit('information', {'info':"Transcribint l'àudio... Pot trigar una estona.", 'estat':"transcripcio"})

      # Executar en un fil separat per a no bloquejar l'interfase
      if not thread or not thread.is_alive():
         thread = threading.Thread(target=transcribe_audio)
         thread.daemon = True
         thread.start()

   """
   Converteix l'arxiu d'àudio a text utilitzant SpeechRecognition
   """
   def transcribe_audio():
      try:
         # Convertir MP3 a WAV si és necessari
         if audio_file_path.lower().endswith('.mp3'):
            wav_path = f"{base_dir}/static/tmp/" + os.path.basename(audio_file_path).replace('.mp3', '_temp.wav')
            audio = AudioSegment.from_mp3(audio_file_path)
            audio.export(wav_path, format="wav")
         else:
            wav_path = audio_file_path

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
         text = recognizer.recognize_google(audio_data, language=f"{selected_language.get()}")

         # Actualitzar l'interfase en el fil principal
         update_transcription(text, "Transcripció completada amb éxit")

      except sr.UnknownValueError:
         update_transcription("", "Error: No he pogut entendre l'àudio")
      except sr.RequestError as e:
         update_transcription("", f"Error en el servei: {str(e)}")
      except Exception as e:
         update_transcription("", f"Error inesperat: {str(e)}")
      finally:
         # Eliminar, si existeix, l'arxiu temporal
         if audio_file_path.lower().endswith('.mp3') and os.path.exists(wav_path):
            os.remove(wav_path)

   """Actualitza l'interfase amb el resultat de la transcripció"""
   def update_transcription(text, status):
      toggle_buttons_state(True)

      #if text:
         #text_area.delete(1.0, tk.END)
         #text_area.insert(1.0, text)

      status_text.set(status)

   def normalize_gender(gender):
      match gender:
         case "home": return "male_masculine"
         case "dona": return "female_feminine"

   def toggle_buttons_state(enabled):
      """Habilita o deshabilita botons durant la transcripció"""
      # En una implementació real, aquí es deshabilitarien els botons
      # Per simplificar, només actualizem l'estat
      pass

   """Neteja tota l'interfase"""
   def clear_all():
      global dataset_file, nou_registre
      dataset_file = ""
      #text_area.delete(1.0, tk.END)
      nou_registre = None
      stop_audio()
      status_text.set(default_state)

   """Desa el registre en l'arxiu de sortida"""
   def save_record(self, nou_registre=None):
      global espera
      #if not nou_registre:
      #   text = text_area.get(1.0, tk.END).strip()
      #   if genera_registre(registre, text):
      #      nou_registre = list_to_tsv(nou_registre)

      if nou_registre:
         file_path = dataset_file.replace("-corpus-", "-reported-audios-")

         try:
            with open(file_path, 'a', encoding='utf-8') as file:
               file.write(nou_registre)
            status_text.set(f"Transcripció desada a: {file_path}")
            desa_configuracio()
            espera = False
         except Exception as e:
            status_text.set(f"Error en desar el registre: {str(e)}")
      else:
         status_text.set("no hi ha text")


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

   @socketio.on('next')
   def handle_next(text):
      global estat, espera, thread
      print(f"{CB_YLW}botó següent{C_NONE}")
      estat = "next"
      if not thread or not thread.is_alive():
         espera = False
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")

   @socketio.on('play_audio')
   def handle_play_audio():
      global thread, estat, stop
      print(f"{CB_YLW}botó play_audio{C_NONE}")
      estat = "play"
      stop = False
      if not thread or not thread.is_alive():
         thread = threading.Thread(target=play_audio)
         thread.start()
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")

   @socketio.on('stop')
   def handle_stop():
      global estat, stop
      print(f"{CB_YLW}botó stop{C_NONE}")
      estat = "stop"
      stop = True
      stop_audio()

   @socketio.on('transcripcio')
   def handle_transcripcio():
      global thread, estat, stop
      print(f"{CB_YLW}botó transcripcio{C_NONE}")
      estat = "transcripcio"
      stop = False
      if not thread or not thread.is_alive():
         start_transcription()
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")



   return app

if __name__ == "__main__":
   app = crear_app()
   '''
   Inicia los servicios flask en la terminal, lo cual, activa el acceso web
   equivale a ejecutar en una terminal el comando: flask run
   así, se activa el reconocimento de las aplicaciones Python en el puerto 5000 de localhost
   '''
   app.run(host='localhost', port=5000, debug=False)
