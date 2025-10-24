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

import os, re
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pygame
from pydub import AudioSegment
import speech_recognition as sr

# Variables
dataset_file_path = ""
audio_file_path = ""
audio_file = ""
audio_actiu = ""
transcription_text = ""
selected_language = "ca-ES"  # Idioma per defecte
base_dir = "/home/rafael/projectes/Transcripcio"
dir_resources = "resources"
browse_initialdir = f"{base_dir}/{dir_resources}/common-voice"
#arxiu de configuració: conté les dades de la darrera execució
cfg_file = f"{base_dir}/{dir_resources}/transcripcio.cfg"
images = {}
attr_gender = ""
registre = ""
nou_registre = None
old_file = None
line = 0
espera = True
is_playing = False
default_state = "Selecciona el conjunt de dades de Mozilla Common Voice"
status_text = default_state
languages = {
   "Català": "ca-ES",
   "Español": "es-ES",
   "English": "en-US"
}

# Auxiliary functions
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
      cfg = "{" + "'line':" + str(line) + ",'file':'" + dataset_file_path.get() +"'}"
      with open(cfg_file, 'w', encoding='utf-8') as file:
         file.write(cfg)
   except Exception as e:
      status_text.set(f"Error en escriure l'arxiu de configuració: {str(e)}")


def crear_app():
   app = Flask(__name__) #instancia de Flask
   socketio = SocketIO(app)
   #key_secret = os.getenv("API_KEY")

   # Inicialitzar pygame per a la reproducció d'àudio
   pygame.mixer.init()
   carrega_configuracio()

   @app.route("/index")
   def index():
      return render_template("index.tpl")

   @app.route("/transcripcio", methods = ["GET", "POST"])
   def upload_mcv_file():
      global dataset_file_path, selected_language, line
      dataset_file_path = arxiu = request.files['arxiu']

      if arxiu.filename == '':
         return 'No has seleccionat cap arxiu'

      idioma = request.form.get("seleccio_idioma")
      if idioma:
         selected_language = idioma

      # verificació de la recuperació de l'estat anterior (últim registre processat)
      if not old_file or dataset_file_path.get() != old_file:
         line = 0

      # Executar en un fil separat per a no bloquejar l'interfase
      thread = threading.Thread(target=processar_dataset)
      thread.daemon = True
      thread.start()

   def processar_dataset():
      global line, transcripcio, dataset_file_path, audio_file_path
      try:
         contingut = dataset_file_path.read().decode('utf-8')
         linies = contingut.splitlines()

         for n_rec, registre in enumerate(linies, line):
            line += 1
            if line == 1:
               continue

            espera = True
            # mira si transcription està buit
            transcripcio = registre.split("\t")[6]
            arxiu = registre.split("\t")[2]
            audio_file_path = os.path.dirname(dataset_file_path) + "/audios/" + arxiu
            audio_file.set(arxiu)
            audio_actiu.set("("+str(line)+") "+audio_file.get())
            #text_area.delete(1.0, tk.END)
            #text_area.insert(1.0, transcripcio)

            while espera:
               pass

      except Exception as e:
            status_text.set(f"Error llegint l'arxiu: {str(e)}")

   """
   Permet saltar a l'àudio següent. Prèviament desa, si existeix, el registre actual
   """
   """
   def next_audio():
      text = text_area.get(1.0, tk.END).strip()
      if text:
         if genera_registre(registre, text):
            #Ahora hay que guardar (append) el registro en un nuevo archivo
            save_record(list_to_csv(nou_registre))

      # desbloquea el bucle para pasar al siguiente registro
      espera = False
   """

   def genera_registre(reg, text):
      nou_registre = reg.split("\t")
      nou_registre[6] = text
      if not nou_registre[9]:
         if attr_gender:
            nou_registre[9] = normalize_gender(attr_gender)
         else:
            socketio.emit('new_line', {'frase':"No has seleccionat l'atribut de gènere de l'àudio", 'estat':"stop"})
            return False
      return True

   """Reprodueix l'arxiu d'àudio seleccionat"""
   def play_audio():
      global is_playing
      if not audio_file_path:
         is_playing = False
         socketio.emit('new_line', {'frase':"Error: No hi ha cap arxiu d'àudio actiu", 'estat':"stop"})
         return

      try:
         pygame.mixer.music.load(audio_file_path)
         pygame.mixer.music.play()
         is_playing = True
         socketio.emit('new_line', {'frase':"Reproduint àudio... [Idioma: {language_combo}]", 'estat':"stop"})
         # Executar en un fil separat per a no bloquejar l'interfase
         thread = threading.Thread(target=check_if_play_audio)
         thread.daemon = True
         thread.start()

      except Exception as e:
         status_text.set(f"Error en reproduir l'àudio: {str(e)}")

   def check_if_play_audio(self):
      while is_playing and pygame.mixer.music.get_busy():
         pass

   """Atura la reproducció d'àudio"""
   def stop_audio():
      global is_playing
      pygame.mixer.music.stop()
      is_playing = False
      toggle_buttons_state(True)
      socketio.emit('new_line', {'frase':"Àudio finalitzat", 'estat':"stop"})

   def start_transcription():
      """Inicia el procés de transcripció en un fil separat"""
      if not audio_file_path:
         status_text.set("Error: No hi ha cap arxiu d'àudio actiu")
         return

      # Deshabilitar botons durant la transcripció
      toggle_buttons_state(False)
      socketio.emit('new_line', {'frase':"Transcribint l'àudio [{language_combo}]... Pot trigar una estona.", 'estat':"stop"})

      # Executar en un fil separat per a no bloquejar l'interfase
      thread = threading.Thread(target=transcribe_audio)
      thread.daemon = True
      thread.start()

   """
   Converteix l'arxiu d'àudio a text utilitzant SpeechRecognition
   """
   def transcribe_audio():
      try:
         # Convertir MP3 a WAV si és necessari
         audio_path = audio_file_path
         if audio_path.lower().endswith('.mp3'):
            wav_path = audio_path.replace('.mp3', '_temp.wav')
            audio = AudioSegment.from_mp3(audio_path)
            audio.export(wav_path, format="wav")
         else:
            wav_path = audio_path

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
         root.after(0, update_transcription, text, f"Transcripció [{language_combo.get()}] completada amb éxit")

      except sr.UnknownValueError:
         root.after(0, update_transcription, "", f"Error: No he pogut entendre l'àudio [{language_combo.get()}]")
      except sr.RequestError as e:
         root.after(0, update_transcription, "", f"Error en el servei: {str(e)}")
      except Exception as e:
         root.after(0, update_transcription, "", f"Error inesperat: {str(e)}")
      finally:
         # Eliminar, si existeix, l'arxiu temporal
         if audio_path.lower().endswith('.mp3') and os.path.exists(wav_path):
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
      global dataset_file_path, nou_registre
      dataset_file_path = ""
      #text_area.delete(1.0, tk.END)
      nou_registre = None
      stop_audio()
      status_text.set(default_state)

   """Desa el registre en l'arxiu de sortida"""
   """
   def save_record(self, nou_registre=None):
      if not nou_registre:
         text = text_area.get(1.0, tk.END).strip()
         if genera_registre(registre, text):
            nou_registre = list_to_csv(nou_registre)

      if nou_registre:
         file_path = dataset_file_path.get().replace("-corpus-", "-reported-audios-")

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

   """
   def list_to_csv(reg):
      return '\t'.join(str(x) for x in reg)


   return app

if __name__ == "__main__":
   app = crear_app()
   '''
   Inicia los servicios flask en la terminal, lo cual, activa el acceso web
   equivale a ejecutar en una terminal el comando: flask run
   así, se activa el reconocimento de las aplicaciones Python en el puerto 5000 de localhost
   '''
   app.run(host='localhost', port=5000, debug=False)

