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

import os, threading, time, logging, shutil
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
dir_lang = "static/lang"
dir_dataset = "common-voice"
dir_audios = f"{dir_dataset}/audios"
cfg_file = f"{base_dir}/transcripcio.cfg" #arxiu de configuració: conté les dades de la darrera execució

old_file = None
line = 0	#linia actual de l'arxiu del conjunt de dades mcv

dataset_file = None
audio_file_path = ""
registres = ""
duration = 0
attr_gender = None
transcriptionless = "ATENCIÓ:\nAquest registre no conté cap transcripció.\nFes clic al botó 'transcripció'.\nEscolta l'àudio i crea una nova transcripció.\nSi no s'escolta cap àudio, ignora'l i passa al registre següent."
selected_language = "ca-ES"  # Idioma per defecte
languages = {
   "ca-ES": "Català",
   "es-ES": "Español",
   "en-US": "English"
}
main_dictionary = None
dictionary = None
registre_actual = ""
thread = None
espera = True       # thread control flag
is_playing = False  # play audio control flag
resposta = None     # dialog response value

# -------------------
# Auxiliary functions
#

def load_main_dictionary():
   global main_dictionary
   i = selected_language[0:2]
   with open(f"{dir_lang}/{i}", 'r', encoding='utf-8') as f:
      main_dictionary = list(f)

def load_selected_dictionary():
   global dictionary
   i = selected_language[0:2]
   with open(f"{dir_lang}/{i}", 'r', encoding='utf-8') as f:
      dictionary = list(f)

def i(text):
   global main_dictionary, dictionary
   tag = None
   ret = text
   text = text.replace("\n", "\\n")
   print(f"{CB_YLW}Dictionary: {C_NONE}'{text}'")
   # search tag in the main dictionary
   for d in main_dictionary:
      s = d.split(":",1)
      if (s[1].strip('" \r\n') == text):
         tag = s[0]
         break

   if tag:
      # search the corresponding text
      for d in dictionary:
         s = d.split(":",1)
         if (s[0] == tag):
            ret = s[1].strip('" \r\n').replace("\\n", "\n")
            break
   return ret

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
            socketio.emit('information', {'error':f"{i('Error llegint la configuració:')} {str(e)}"})

   def desa_configuracio():
      # Desa a l'arxiu de configuració les dades de la darrera execució:
      # - la ruta de l'arxiu del conjunt de dades
      # - la darrera línia precessada de l'arxiu del conjunt de dades
      try:
         cfg = "{" + "'line':" + str(line) + ",'file':'" + dataset_file.filename +"'}"
         with open(cfg_file, 'w', encoding='utf-8') as file:
            file.write(cfg)
      except Exception as e:
         socketio.emit('information', {'error':f"{i('Error escrvint la configuració:')} {str(e)}"})

   def normalize_gender(gender):
      match gender:
         case "home": return "male_masculine"
         case "dona": return "female_feminine"

   def toggle_buttons(boto):
      # Habilita o deshabilita botons durant la transcripció
      socketio.emit('toggle_buttons', {'estat':boto})

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
         load_selected_dictionary()

      if dataset_file:
         #print(f"{CB_YLW}dataset file:{C_NONE} {dataset_file}.")
         registres = dataset_file.read().decode('utf-8')
         #dataset_file.seek(0)  # Volver al inicio por si necesitas el objeto file completo
         return render_template(f"transcripcio-{selected_language[0:2]}.tpl", arxiu=dataset_file.filename, idioma=languages[selected_language])
      else:
         return render_template("index.tpl")

   # -----------------
   # Process functions
   #
   def processar_dataset():
      global registres, registre_actual
      global espera, line
      global transcriptionless, duration
      global dir_audios, audio_file_path

      try:
         sync_lines = 1 if (line == 0) else line - 1
         lines = registres.splitlines()

         for n, registre_actual in enumerate(lines, line):
            line += 1
            if line == 1:
               continue

            if (line - n != sync_lines):
               print(f"{CB_YLW}\nERROR de SINCRONITZACIÓ: {CB_BLU}line={C_NONE}{str(line)}{CB_BLU} - n={C_NONE}{str(n)}")
               err = f"{i('Error de sincronització:')} line={str(line)} - n={str(n)}\n" + \
                     f"{i('Potser cal revisar larxiu de sortida.')}\n{i('Vols continuar?')}"
               socketio.emit('dialog', {'text':err})
               while not resposta:
                  pass
               if (resposta == "N"):
                  espera = False
                  sortir()

            espera = True
            fields = registre_actual.split("\t")
            print(f"{CB_YLW}processar_dataset():\n\t{CB_BLU}n:{CB_YLW}{n}\n\t{CB_BLU}line:{CB_YLW}{line}\n\t{CB_BLU}transcripció: {C_NONE}{fields[6]}\n\t{CB_BLU}gènere: {C_NONE}{fields[9]}")
            audio_file = fields[2]
            if audio_file:
               gender = fields[9]
               socketio.emit('set_gender', {'gender':gender})
               transcription = fields[6]
               if transcription:
                  socketio.emit('new_transcription', {'text':transcription})
               else:
                  socketio.emit('new_transcription', {'placeholder':i(transcriptionless)})
                  duration = int(fields[3])//1000 if fields[3] else 0

               socketio.emit('information', {'arxiu_audio':f"{i('àudio actiu:')} ({str(line-1)}) {audio_file}"})
               audio_file_path = f"{dir_audios}/{audio_file}"
               print(f"\t{CB_BLU}audio_file_path: {CB_YLW}{audio_file_path}\n\t{CB_BLU}duration: {CB_YLW}{duration}s{C_NONE}.")
            else:
               espera = False
               continue

            while espera:
               pass

      except Exception as e:
         socketio.emit('information', {'error':f"{i('Error processant el conjunt de dades:')} {str(e)}"})

   def next_audio(text):
      # Salta a l'àudio següent. Prèviament desa el registre actual
      global espera, thread, resposta
      if text and text != "":
         print(f"{CB_YLW}next_audio: {C_NONE}{text}")
         save_record(text)
         print(f"{CB_BLU}\tnext_audio -> save_record: {CB_YLW}resposta:{C_NONE}{resposta} - {CB_YLW}espera:{C_NONE}{espera}")
      else:
         print(f"{CB_BLU}next_audio: {C_NONE}(dialog) sense transcripció")
         resposta = None
         socketio.emit('dialog', {'text':f"{i('No hi ha transcripció. Vols passar al registre següent?')}"})
         #tic = time.perf_counter()
         while not resposta:  # and time.perf_counter()-tic < 10:
            pass

         if (resposta == "S"):
            # desbloquea el bucle para pasar al siguiente registro
            if not thread or not thread.is_alive():
               espera = False
            else:
               print(f"{CB_BLU}\tthread.is_alive{C_NONE}")
               socketio.emit('information', {'error':f"{i('No puc passar al registre següent: el fil encara és actiu')}"})

         print(f"{CB_BLU}\tnext_audio resposta: {CB_YLW}{resposta}{C_NONE}")

   def genera_registre(text):
      global registre_actual, attr_gender
      print(f"{CB_YLW}genera_registre():{C_NONE}")
      valid = True if (text) else False
      if text:
         print(f"\t{CB_BLU}text: {C_NONE}{text}")
         new_rec = registre_actual.split("\t")
         new_rec[6] = text
         valid = True if (new_rec[9]) else False
         if not new_rec[9]:
            if attr_gender:
               new_rec[9] = normalize_gender(attr_gender)
               attr_gender = None
               valid = True
            else:
               err = i("No has seleccionat el gènere de l'àudio")
               socketio.emit('information', {'error':err})
      else:
         socketio.emit('information', {'error':f"{i('No hi ha cap text transcrit')}"})

      return list_to_tsv(new_rec) if valid else None

   def play_audio():
      # Reprodueix l'arxiu d'àudio seleccionat
      global is_playing, duration
      if not audio_file_path:
         is_playing = False
         err = i("Error: No hi ha cap arxiu d'àudio actiu")
         socketio.emit('information', {'error':err})
         return

      try:
         toggle_buttons("play")
         pygame.mixer.music.load(audio_file_path)
         pygame.mixer.music.play()
         is_playing = True
         #socketio.emit('information', {'info':f"{i('Reproduint àudio...')}"})

         def check_if_play_audio(temps):
            global is_playing
            while temps and is_playing and pygame.mixer.music.get_busy():
               time.sleep(1)
               socketio.emit('information', {'info':f"{i('Reproduint àudio...')} ({temps})"})
               temps -=1
            stop_audio()

         # executar en un fil separat per a no bloquejar l'interfase
         fil = threading.Thread(target=check_if_play_audio(duration))
         fil.daemon = True
         fil.start()

      except Exception as e:
         is_playing = False
         err = i("Error en la reproducció de l'àudio:")
         socketio.emit('information', {'error':f"{err} {str(e)}"})

   def stop_audio():
      # Atura la reproducció d'àudio
      global is_playing
      if pygame.mixer.music.get_busy():
         pygame.mixer.music.fadeout(100)
         time.sleep(0.1)
      pygame.mixer.music.unload()
      is_playing = False
      toggle_buttons("stop")
      socketio.emit('information', {'info':f"{i('Àudio finalitzat')}"})
      print(f"{CB_YLW}stop_audio: {C_NONE}Àudio finalitzat")

   def start_transcription():
      if not audio_file_path:
         err = i("Error: No hi ha cap arxiu d'àudio actiu")
         socketio.emit('information', {'error':err})
         return

      # Deshabilitar botons durant la transcripció
      toggle_buttons("transcription")
      err = i("Transcrivint l'àudio... pot trigar una estona.")
      socketio.emit('information', {'info':err})
      transcribe_audio()

   def transcribe_audio():
      # Converteix l'arxiu d'àudio a text utilitzant SpeechRecognition

      def update_transcription_area(text, status, error):
         # Actualitza l'interfase amb el resultat de la transcripció
         toggle_buttons("end_transcription")
         if text:
            socketio.emit('new_transcription', {'text':text})
            socketio.emit('information', {'info':status})
         elif error:
            socketio.emit('information', {'error':error})
         else:
            socketio.emit('information', {'error':"No hi ha text transcrit"})

      try:
         # Convertir MP3 a WAV si és necessari
         if audio_file_path.lower().endswith('.mp3'):
            wav_path = f"{base_dir}/tmp/" + os.path.basename(audio_file_path).replace('.mp3', '.wav')
            audio = AudioSegment.from_mp3(audio_file_path)
            audio.export(wav_path, format="wav")
         else:
            wav_path = audio_file_path
         print(f"{CB_YLW}transcribe_audio():\n\t{CB_BLU}audio_file_path: {CB_YLW}{audio_file_path}\n\t{CB_BLU}wav_path: {CB_YLW}{wav_path}{C_NONE}")

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
         update_transcription_area(text, i("Transcripció completada"), "")

      except sr.UnknownValueError:
         update_transcription_area("", "", i("Error: No he pogut entendre l'àudio"))
      except sr.RequestError as e:
         update_transcription_area("", "", f"{i('Error en el servei:')} {str(e)}")
      except Exception as e:
         update_transcription_area("", "", f"{i('Error inesperat:')} {str(e)}")
      finally:
         # eliminar, si existeix, l'arxiu temporal
         if audio_file_path.lower().endswith('.mp3') and os.path.exists(wav_path):
            os.remove(wav_path)

   def save_record(text):
      # Desa el registre en l'arxiu de sortida (append)
      global espera, resposta

      nou_registre = genera_registre(text)
      if nou_registre:
         print(f"{CB_YLW}save_record: {C_NONE}(dialog) Vols desar?")
         resposta = None
         socketio.emit('dialog', {'text':f"{i('Vols desar el nou registre?')}"})
         while not resposta:
            pass
         if (resposta == "S"):
            reported_dataset_file_path = f"{dir_dataset}/" + dataset_file.filename.replace("-corpus-", "-reported-audios-")
            reported_dataset_template_file_path = f"{dir_dataset}/template_" + dataset_file.filename.replace("-corpus-", "-reported-audios-")
            try:
               if (not os.path.isfile(reported_dataset_file_path)):
                  # si encara no existeix l'arxiu resultant generat per l'aplicació, es crea a partir de la plantilla
                  shutil.copy(reported_dataset_template_file_path, reported_dataset_file_path)

               with open(reported_dataset_file_path, 'a', encoding='utf-8') as file:
                  file.write(f"{nou_registre}\r\n")
               socketio.emit('information', {'info':f"Transcripció desada a: {reported_dataset_file_path}"})
               print(f"\t{CB_BLU}save_record: {C_NONE}Transcripció desada a: {reported_dataset_file_path}")
               desa_configuracio()
               espera = False
            except Exception as e:
               socketio.emit('information', {'error':f"Error en desar el registre: {str(e)}"})
         else:
            espera = False

         print(f"{CB_BLU}\tsave_record {CB_YLW}resposta:{C_NONE}{resposta} - {CB_YLW}espera:{C_NONE}{espera}")

   # Retorna a l'inici
   def sortir():
      global dataset_file
      dataset_file = None
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
      if not old_file or dataset_file.filename != old_file:
         line = 0

      # Executar en un fil separat per a no bloquejar l'interfase
      thread = threading.Thread(target=processar_dataset)
      thread.daemon = True
      thread.start()

   @socketio.on('seleccioGenere')
   def handle_gender(g):
      global attr_gender
      print(f"{CB_YLW}seleccio de gènere{C_NONE}")
      attr_gender = g

   @socketio.on('next')
   def handle_next(text):
      print(f"{CB_YLW}botó següent")
      next_audio(text)

   @socketio.on('play')
   def handle_play():
      global thread
      print(f"{CB_YLW}botó play_audio{C_NONE}")
      if not thread or not thread.is_alive():
         thread = threading.Thread(target=play_audio)
         thread.start()
      else:
         print(f"{CB_BLU}\tfil.is_alive{C_NONE}")

   @socketio.on('stop')
   def handle_stop():
      global is_playing
      print(f"{CB_YLW}botó stop_audio{C_NONE}")
      is_playing = False

   @socketio.on('transcription')
   def handle_transcription():
      global thread
      print(f"{CB_YLW}botó transcription{C_NONE}")
      if not thread or not thread.is_alive():
         start_transcription()
      else:
         print(f"{CB_BLU}\tthread.is_alive{C_NONE}")

   @socketio.on('save')
   def handle_save(text):
      print(f"{CB_YLW}botó save{C_NONE}")
      save_record(text)

   @socketio.on('dialog')
   def handle_dialog(resp):
      global resposta
      print(f"{CB_YLW}dialog: {CB_BLU}resposta: {C_NONE}{resp}")
      resposta = resp

   @socketio.on('exit')
   def handle_exit():
      sortir()

   return app

if __name__ == "__main__":
   load_main_dictionary()
   app = crear_app()
   #disable console messages
   logging.getLogger('werkzeug').disabled = True
   #os.environ['WERKZEUG_RUN_MAIN'] = 'true'
   # Inicia los servicios flask en la terminal, lo cual, activa el acceso web
   # equivale a ejecutar en una terminal el comando: flask run
   # así, se activa el reconocimento de las aplicaciones Python en el puerto 5000 de localhost
   app.run(host='localhost', port=5000, debug=False)
