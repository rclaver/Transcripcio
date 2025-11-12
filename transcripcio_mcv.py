#!/usr/bin/python3
# -*- coding: UTF8 -*-
"""
@created: 17-10-2025
@author: rafael
@description: Converteix àudios a text a partir del conjunt de dades Mozilla Common Voice

Instalació prèvia:
sudo apt-get install python-tk
sudo apt-get install python3-pil python3-pil.imagetk
pip install --user pygame pydub speechrecognition pyaudio
"""

import os, re
import tkinter as tk
from tkinter import filedialog, ttk
import pygame
from pydub import AudioSegment
import speech_recognition as sr
import threading


class AudioTranscriber:
   def __init__(self, root):
      self.root = root
      self.root.title("Transcripció d'àudios del conjunt de dades Mozilla Common Voice")
      self.root.minsize(800, 600)

      # Variables
      self.dataset_file_path = tk.StringVar()
      self.audio_file_path = tk.StringVar()
      self.audio_file = tk.StringVar()
      self.audio_actiu = tk.StringVar()
      self.transcription_text = tk.StringVar()
      self.selected_language = tk.StringVar(value="ca-ES")  # Idioma per defecte
      self.base_dir = "/home/rafael/projectes/Transcripcio"
      self.dir_images = "static/img"
      self.browse_initialdir = f"{self.base_dir}/common-voice"
      #arxiu de configuració: conté les dades de la darrera execució
      self.cfg_file = f"{self.base_dir}/transcripcio.cfg"
      self.images = {}
      self.attr_gender = tk.StringVar()
      self.registre = tk.StringVar()
      self.nou_registre = None
      self.old_file = None
      self.fila = 0
      self.espera = True
      self.is_playing = False
      self.default_state = "Selecciona el conjunt de dades de Mozilla Common Voice"
      self.status_text = tk.StringVar(value=self.default_state)
      self.languages = {
         "Català": "ca-ES",
         "Español": "es-ES",
         "English": "en-US"
      }

      # Inicialitzar pygame per a la reproducció d'àudio
      pygame.mixer.init()

      self.carrega_configuracio()
      self.carrega_imatges()
      self.create_widgets()

   def carrega_imatges(self):
      #self.images = [ImageTk.PhotoImage(Image.open(os.path.join(self.dir_images, nom))) for nom in os.listdir(self.dir_images)]
      self.images['search'] = tk.PhotoImage(file=f"{self.dir_images}/search.png")
      self.images['next'] = tk.PhotoImage(file=f"{self.dir_images}/next.png")
      self.images['reproduccio'] = tk.PhotoImage(file=f"{self.dir_images}/play_audio.png")
      self.images['stop'] = tk.PhotoImage(file=f"{self.dir_images}/stop.png")
      self.images['transcripcio'] = tk.PhotoImage(file=f"{self.dir_images}/transcripcio.png")
      self.images['clear'] = tk.PhotoImage(file=f"{self.dir_images}/clear.png")
      self.images['save'] = tk.PhotoImage(file=f"{self.dir_images}/save.png")
      self.images['exit'] = tk.PhotoImage(file=f"{self.dir_images}/exit.png")

   def create_widgets(self):
      # Frame principal
      main_frame = ttk.Frame(self.root, padding="10")
      main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

      # Configurar grid weights
      self.root.columnconfigure(0, weight=1)
      self.root.rowconfigure(0, weight=1)
      main_frame.columnconfigure(1, weight=1)
      main_frame.rowconfigure(4, weight=1)

      # Títol
      ttk.Label(main_frame, text="Transcripció d'àudio a text", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))

      # Selecció d'arxiu del dataset
      ttk.Label(main_frame, text="Selecció del dataset:",font=("Arial",9,"bold")).grid(row=1, column=0, sticky=tk.W, pady=5)

      file_frame = ttk.Frame(main_frame)
      file_frame.grid(row=1, column=1, columnspan=4, sticky=(tk.W, tk.E), pady=5)
      file_frame.columnconfigure(0, weight=1)

      self.file_entry = ttk.Entry(file_frame, textvariable=self.dataset_file_path, font=("Arial",9), state="readonly")
      self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

      ttk.Button(file_frame, image=self.images['search'], command=self.browse_file).grid(row=0, column=3, padx=0)

      # Selector d'idioma
      ttk.Label(main_frame, text="Idioma àudios:", font=("Arial",9,"bold")).grid(row=2, column=0, sticky=(tk.N,tk.W), pady=(5,15))
      language_frame = ttk.Frame(main_frame)
      language_frame.grid(row=2, column=1, sticky=(tk.N,tk.W), pady=(5,15))
      language_frame.columnconfigure(0, weight=1)

      # Combobox per seleccionar idioma
      self.language_combo = ttk.Combobox(
         language_frame,
         values=list(self.languages.keys()),
         state="readonly",
         font=("Arial",9),
         width=12
      )
      self.language_combo.grid(row=0, column=0, sticky=tk.W, padx=0)
      self.language_combo.set("Català")  # Valor per defecte

      # Vincular l'event de canvi de selecció
      self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)

      # Etiqueta de l'àudio actualment seleccionat
      ttk.Label(main_frame, text="àudio actiu:", font=("Arial",9,"bold")).grid(row=2, column=2, sticky=(tk.N,tk.E), pady=(5,15))
      audio_label = ttk.Label(main_frame, textvariable=self.audio_actiu, font=("Arial",9,"italic"))
      audio_label.grid(row=2, column=3, sticky=(tk.N,tk.W), pady=(5,15))

      # Àrea de text per a la transcripció
      ttk.Label(main_frame, text="Text transcrit:",font=("Arial",9,"bold")).grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(5, 0))
      self.text_area = tk.Text(main_frame, wrap=tk.WORD, width=80, height=20)
      self.text_area.grid(row=3, column=1, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

      # Scrollbar de l'àrea de text
      scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.text_area.yview)
      scrollbar.grid(row=3, column=5, sticky=(tk.N, tk.S), pady=(5, 0))
      self.text_area.configure(yscrollcommand=scrollbar.set)

      # Àrea de atributs de la veu
      ttk.Label(main_frame, text="Atributs de l'àudio", font=("Arial",9,"bold")).grid(row=4, column=0, sticky=(tk.N,tk.W), pady=15)
      atrib_frame = ttk.Frame(main_frame)
      atrib_frame.grid(row=4, column=1, sticky=(tk.N,tk.W), pady=15)
      tk.Radiobutton(atrib_frame, text="home", font=("Arial",9), variable=self.attr_gender, value="home").grid(row=0, column=0, sticky=tk.W)
      tk.Radiobutton(atrib_frame, text="dona", font=("Arial",9), variable=self.attr_gender, value="dona").grid(row=1, column=0, sticky=tk.W)

      # Botons de control
      button_frame = ttk.Frame(main_frame)
      button_frame.grid(row=4, column=2, columnspan=3, sticky=tk.N, pady=15)

      ttk.Button(button_frame, image=self.images['next'], command=self.next_audio).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, image=self.images['reproduccio'], command=self.play_audio).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, image=self.images['stop'], command=self.stop_audio).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, image=self.images['transcripcio'], command=self.start_transcription).pack(side=tk.LEFT, padx=15)
      ttk.Button(button_frame, image=self.images['clear'], command=self.clear_all).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, image=self.images['save'], command=self.save_record).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, image=self.images['exit'], command=self.root.destroy).pack(side=tk.LEFT, padx=(10,0))

      # Barra de progrés
      self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
      self.progress.grid(row=5, column=0, columnspan=5, sticky=(tk.N, tk.W, tk.E), pady=0)

      # Estat
      ttk.Label(main_frame, textvariable=self.status_text, font=("Arial",9,"italic")).grid(row=6, column=0, columnspan=5, sticky=(tk.N,tk.W))


   def on_language_change(self, event):
      """Actualitza l'etiqueta del codi d'idioma quan canvia la selecció"""
      selected_language_name = self.language_combo.get()
      language_code = self.languages[selected_language_name]
      self.selected_language.set(language_code)
      self.language_code_label.config(text=f"Codi: {language_code}")
      self.status_text.set(f"Idioma cambiat a: {selected_language_name}")

   def browse_file(self):
      """Obre el cuadre de diàleg per seleccionar l'arxiu del conjunt de dades Mozilla Common Voice"""
      file_path = filedialog.askopenfilename(
         title="Selecciona l'arxiu del conjunt de dades Mozilla Common Voice",
         initialdir=self.browse_initialdir,
         filetypes=[
            ("Arxius TSV", "*.tsv"),
            ("Tots els arxius", "*.*")
         ]
      )

      if file_path:
         self.dataset_file_path.set(file_path)
         self.status_text.set(f"Arxiu del conjunt de dades: {os.path.basename(file_path)} - Idioma: {self.language_combo.get()}")

         # verificació de la recuperació de l'estat anterior (últim registre processat)
         if not self.old_file or self.dataset_file_path.get() != self.old_file:
            self.fila = 0

         # Executar en un fil separat per a no bloquejar l'interfase
         thread = threading.Thread(target=self.processar_dataset)
         thread.daemon = True
         thread.start()

   def processar_dataset(self):
      file_path = self.dataset_file_path.get()
      if file_path:
         try:
            with open(file_path, 'r', encoding='utf-8') as file:
               for self.registre in file:
                  self.fila += 1
                  if self.fila == 1:
                     continue

                  self.espera = True
                  # mira si transcription està buit
                  transcripcio = self.registre.split("\t")[6]
                  arxiu = self.registre.split("\t")[2]
                  self.audio_file_path = os.path.dirname(file_path) + "/audios/" + arxiu
                  self.audio_file.set(arxiu)
                  self.audio_actiu.set("("+str(self.fila)+") "+self.audio_file.get())
                  self.text_area.delete(1.0, tk.END)
                  self.text_area.insert(1.0, transcripcio)

                  while self.espera:
                     pass

         except Exception as e:
            self.status_text.set(f"Error llegint l'arxiu: {str(e)}")

   """
   Permet saltar a l'àudio següent. Prèviament desa, si existeix, el registre actual
   """
   def next_audio(self):
      text = self.text_area.get(1.0, tk.END).strip()
      if text:
         if self.genera_registre(self.registre, text):
            #Ahora hay que guardar (append) el registro en un nuevo archivo
            self.save_record(self.list_to_csv(self.nou_registre))

      # desbloquea el bucle para pasar al siguiente registro
      self.espera = False

   def genera_registre(self, reg, text):
      self.nou_registre = reg.split("\t")
      self.nou_registre[6] = text
      if not self.nou_registre[9]:
         if self.attr_gender:
            self.nou_registre[9] = self.normalize_gender(self.attr_gender)
         else:
            self.status_text.set("No has seleccionat l'atribut de gènere de l'àudio")
            return False
      return True

   def play_audio(self):
      """Reprodueix l'arxiu d'àudio seleccionat"""
      if not self.audio_file_path:
         self.is_playing = False
         self.status_text.set("Error: No hi ha cap arxiu d'àudio actiu")
         return

      try:
         pygame.mixer.music.load(self.audio_file_path)
         pygame.mixer.music.play()
         self.is_playing = True
         self.progress.start()
         self.status_text.set(f"Reproduint àudio... [Idioma: {self.language_combo.get()}]")
         # Executar en un fil separat per a no bloquejar l'interfase
         thread = threading.Thread(target=self.check_if_play_audio)
         thread.daemon = True
         thread.start()

      except Exception as e:
         self.status_text.set(f"Error en reproduir l'àudio: {str(e)}")

   def check_if_play_audio(self):
      while self.is_playing and pygame.mixer.music.get_busy():
         pass
      self.root.after(0, self.stop_audio)


   def stop_audio(self):
      """Atura la reproducció d'àudio"""
      pygame.mixer.music.stop()
      self.is_playing = False
      self.progress.stop()
      self.toggle_buttons_state(True)
      self.status_text.set("Àudio finalitzat")

   def start_transcription(self):
      """Inicia el procés de transcripció en un fil separat"""
      if not self.audio_file_path:
         self.status_text.set("Error: No hi ha cap arxiu d'àudio actiu")
         return

      # Deshabilitar botons durant la transcripció
      self.toggle_buttons_state(False)
      self.progress.start()
      self.status_text.set(f"Transcribint l'àudio [{self.language_combo.get()}]... Pot trigar una estona.")

      # Executar en un fil separat per a no bloquejar l'interfase
      thread = threading.Thread(target=self.transcribe_audio)
      thread.daemon = True
      thread.start()

   def transcribe_audio(self):
      """Converteix l'arxiu d'àudio a text utilitzant SpeechRecognition"""
      try:
         # Convertir MP3 a WAV si és necessari
         audio_path = self.audio_file_path
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
         text = recognizer.recognize_google(audio_data, language=f"{self.selected_language.get()}")

         # Actualitzar l'interfase en el fil principal
         self.root.after(0, self.update_transcription, text, f"Transcripció [{self.language_combo.get()}] completada amb éxit")

      except sr.UnknownValueError:
         self.root.after(0, self.update_transcription, "", f"Error: No he pogut entendre l'àudio [{self.language_combo.get()}]")
      except sr.RequestError as e:
         self.root.after(0, self.update_transcription, "", f"Error en el servei: {str(e)}")
      except Exception as e:
         self.root.after(0, self.update_transcription, "", f"Error inesperat: {str(e)}")
      finally:
         # Eliminar, si existeix, l'arxiu temporal
         if audio_path.lower().endswith('.mp3') and os.path.exists(wav_path):
            os.remove(wav_path)

   def update_transcription(self, text, status):
      """Actualitza l'interfase amb el resultat de la transcripció"""
      self.progress.stop()
      self.toggle_buttons_state(True)

      if text:
         self.text_area.delete(1.0, tk.END)
         self.text_area.insert(1.0, text)

      self.status_text.set(status)

   def normalize_gender(self, gender):
      match gender:
         case "home": return "male_masculine"
         case "dona": return "female_feminine"

   def toggle_buttons_state(self, enabled):
      """Habilita o deshabilita botons durant la transcripció"""
      # En una implementació real, aquí es deshabilitarien els botons
      # Per simplificar, només actualizem l'estat
      pass

   def clear_all(self):
      """Neteja tota l'interfase"""
      self.dataset_file_path.set("")
      self.text_area.delete(1.0, tk.END)
      self.nou_registre = None
      self.stop_audio()
      self.status_text.set(self.default_state)

   def save_record(self, nou_registre=None):
      """Desa el registre en l'arxiu de sortida"""
      if not nou_registre:
         text = self.text_area.get(1.0, tk.END).strip()
         if self.genera_registre(self.registre, text):
            nou_registre = self.list_to_csv(self.nou_registre)

      if nou_registre:
         file_path = self.dataset_file_path.get().replace("-corpus-", "-reported-audios-")

         try:
            with open(file_path, 'a', encoding='utf-8') as file:
               file.write(nou_registre)
            self.status_text.set(f"Transcripció desada a: {file_path}")
            self.desa_configuracio()
            self.espera = False
         except Exception as e:
            self.status_text.set(f"Error en desar el registre: {str(e)}")
      else:
         self.status_text.set("no hi ha text")

   def list_to_csv(self, reg):
      return '\t'.join(str(x) for x in reg)

   def save_only_transcription(self):
      """Desa la transcripció en un arxiu de text"""
      text = self.text_area.get(1.0, tk.END).strip()
      if not text:
         self.status_text.set("Error: No hi ha text per desar")
         self.espera = False
         return

      file_path = re.sub("\..{3}$", ".txt", self.dataset_file_path.get())

      if file_path:
         try:
            with open(file_path, 'w', encoding='utf-8') as file:
               file.write(text)
            self.status_text.set(f"Transcripció desada a: {file_path}")
            self.espera = False
         except Exception as e:
            self.status_text.set(f"Error en desar: {str(e)}")

   """
   Llegeix de l'arxiu de configuració les dades de la darrera execució:
   - la ruta de l'arxiu del conjunt de dades
   - la darrera línia precessada de l'arxiu del conjunt de dades
   """
   def carrega_configuracio(self):
      try:
         with open(self.cfg_file, 'r', encoding='utf-8') as file:
            reg = file.readline().strip("{}").split(",")
         for e in reg:
            match e[0]:
               case "line": self.fila = e[1]-1
               case "file": self.old_file = e[1]
      except IOError as e:
         if (e.errno != 2): #file not found
            self.status_text.set(f"Error en llegir l'arxiu de configuració: {str(e)}")

   """
   Desa a l'arxiu de configuració les dades de la darrera execució:
   - la ruta de l'arxiu del conjunt de dades
   - la darrera línia precessada de l'arxiu del conjunt de dades
   """
   def desa_configuracio(self):
      try:
         cfg = "{" + "'line':" + str(self.fila) + ",'file':'" + self.dataset_file_path.get() +"'}"
         with open(self.cfg_file, 'w', encoding='utf-8') as file:
            file.write(cfg)
      except Exception as e:
         self.status_text.set(f"Error en escriure l'arxiu de configuració: {str(e)}")

def main():
   root = tk.Tk()
   AudioTranscriber(root)
   root.mainloop()

if __name__ == "__main__":
   main()
