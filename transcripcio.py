#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Creat: 16-10-2025
@author: rafael
@description: Converteix àudio a text

Instalació prèvia:
sudo apt-get install python-tk
pip install --user pygame pydub speechrecognition pyaudio
"""

import os, re
import tkinter as tk
from tkinter import filedialog, ttk
#from tkinter import PhotoImage
import pygame
from pydub import AudioSegment
import speech_recognition as sr
import threading


class AudioTranscriberApp:
   def __init__(self, root):
      self.root = root
      self.root.title("Transcripció d'àudio a text")
      self.root.minsize(800, 680)
      self.selected_language = tk.StringVar(value="ca-ES")  # Idioma per defecte

      # Inicialitzar pygame per a la reproducció d'àudio
      pygame.mixer.init()

      # Variables
      self.audio_file_path = tk.StringVar()
      self.transcription_text = tk.StringVar()
      self.status_text = tk.StringVar(value="Preparat per començar")

      self.languages = {
         "Català": "ca-ES",
         "Español": "es-ES",
         "English": "en-US"
      }

      self.create_widgets()

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
      title_label = ttk.Label(main_frame, text="Transcripció d'àudio a text", font=("Arial", 16, "bold"))
      title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

      # Selecció d'arxiu
      ttk.Label(main_frame, text="Arxiu d'àudio:",font=("Arial",9,"bold")).grid(row=1, column=0, sticky=tk.W, pady=5)

      file_frame = ttk.Frame(main_frame)
      file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
      file_frame.columnconfigure(0, weight=1)

      self.file_entry = ttk.Entry(file_frame, textvariable=self.audio_file_path, state="readonly")
      self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

      ttk.Button(file_frame, text="Cercar arxiu",command=self.browse_file).grid(row=0, column=1)

      # Selector d'e 'idioma
      ttk.Label(main_frame, text="Idioma de l'àudio:", font=("Arial",9,"bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
      language_frame = ttk.Frame(main_frame)
      language_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
      language_frame.columnconfigure(0, weight=1)

      # Combobox per seleccionar idioma
      self.language_combo = ttk.Combobox(
         language_frame,
         values=list(self.languages.keys()),
         state="readonly",
         width=20
      )
      self.language_combo.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
      self.language_combo.set("Català")  # Valor per defecte

      # Etiqueta que mostra el codi de l'idioma seleccionat
      self.language_code_label = ttk.Label(
         language_frame,
         text=f"Codi: {self.languages['Català']}",
         font=("Arial", 9),
         foreground="red"
      )
      self.language_code_label.grid(row=0, column=1, sticky=tk.W)

      # Vincular l'event de canvi de selecció
      self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)

      # Separador
      #separator = ttk.Separator(main_frame, orient='horizontal')
      #separator.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

      # Botons de control
      button_frame = ttk.Frame(main_frame)
      button_frame.grid(row=3, column=0, columnspan=3, pady=10)

      #ico = PhotoImage(file='resources/audio32.png')
      ttk.Button(button_frame, text="Reprodució", command=self.play_audio).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, text="Aturar", command=self.stop_audio).pack(side=tk.LEFT, padx=5)
      ttk.Button(button_frame, text="Transcripció", command=self.start_transcription).pack(side=tk.LEFT, padx=15)
      ttk.Button(button_frame, text="Netejar", command=self.clear_all).pack(side=tk.LEFT, padx=5)

      # Àrea de text per a la transcripció
      ttk.Label(main_frame, text="Text transcrit:",font=("Arial",9,"bold")).grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
      self.text_area = tk.Text(main_frame, wrap=tk.WORD, width=80, height=20)
      self.text_area.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 5))

      # Scrollbar de l'àrea de text
      scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.text_area.yview)
      scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S), pady=(10, 5))
      self.text_area.configure(yscrollcommand=scrollbar.set)

      # Barra de progrés
      self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
      self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

      # Estat
      status_label = ttk.Label(main_frame, textvariable=self.status_text, font=("Arial",9,"italic"))
      status_label.grid(row=6, column=0, columnspan=3, sticky=tk.W)

      # Botó per desar la transcripció
      ttk.Button(main_frame, text="Desar la Transcripció", command=self.save_transcription).grid(row=7, column=2, sticky=tk.E, pady=5)

   def on_language_change(self, event):
      """Actualitza l'etiqueta del codi d'idioma quan canvia la selecció"""
      selected_language_name = self.language_combo.get()
      language_code = self.languages[selected_language_name]
      self.selected_language.set(language_code)
      self.language_code_label.config(text=f"Codi: {language_code}")
      self.status_text.set(f"Idioma cambiat a: {selected_language_name}")

   def browse_file(self):
      """Obre el cuadre de diàleg per seleccionar l'arxiu d'àudio"""
      file_path = filedialog.askopenfilename(
         title="Seleccionar l'arxiu d'àudio",
         initialdir="/home/rafael/projectes",
         filetypes=[
            ("Arxius MP3", "*.mp3"),
            ("Arxius WAV", "*.wav"),
            ("Tots els arxius", "*.*")
         ]
      )

      if file_path:
         self.audio_file_path.set(file_path)
         self.status_text.set(f"Arxiu seleccionat: {os.path.basename(file_path)} - Idioma: {self.language_combo.get()}")

   def play_audio(self):
      """Reprodueix l'arxiu d'àudio seleccionat"""
      if not self.audio_file_path.get():
         self.status_text.set("Error: No hi ha cap arxiu seleccionat")
         return

      try:
         pygame.mixer.music.load(self.audio_file_path.get())
         pygame.mixer.music.play()
         self.status_text.set(f"Reproduint àudio... [Idioma: {self.language_combo.get()}]")
      except Exception as e:
         self.status_text.set(f"Error en reproduir l'àudio: {str(e)}")

   def stop_audio(self):
      """Atura la reproducció d'àudio"""
      pygame.mixer.music.stop()
      self.status_text.set("Àudio aturat")

   def start_transcription(self):
      """Inicia el procés de transcripció en un fil separat"""
      if not self.audio_file_path.get():
         self.status_text.set("Error: No hi ha cap arxiu seleccionat")
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
         audio_path = self.audio_file_path.get()
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

   def toggle_buttons_state(self, enabled):
      """Habilita o deshabilita botons durant la transcripció"""
      # En una implementació real, aquí es deshabilitarien els botons
      # Per simplificar, només actualizem l'estat
      pass

   '''
   def detect_language(self, audio_path):
      """Intenta detectar l'idioma de làudio automàticament"""
      try:
         # Convertir a WAV si cal
         if audio_path.lower().endswith('.mp3'):
            wav_path = audio_path.replace('.mp3', '_temp.wav')
            audio = AudioSegment.from_mp3(audio_path)
            audio.export(wav_path, format="wav")
         else:
            wav_path = audio_path

         recognizer = sr.Recognizer()

         with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source, duration=10)  # Solo primeros 10 segundos

         # Intentar detectar con idioma auto
         language_code = self.selected_language.get()
         text = recognizer.recognize_google(audio_data, language=language_code)

         # Aquí podrías agregar lógica per a detectar el idioma basado en el texto
         # Por simplicidad, retornamos el idioma detectado o por defecto
         return language_code

      except:
         return self.selected_language.get()  # Idioma por defecto si no se puede detectar
   '''

   def clear_all(self):
      """Neteja tota l'interfase"""
      self.audio_file_path.set("")
      self.text_area.delete(1.0, tk.END)
      self.stop_audio()
      self.status_text.set("Preparat per començar")

   def save_transcription(self):
      """Guarda la transcripció en un arxiu de text"""
      text = self.text_area.get(1.0, tk.END).strip()
      if not text:
         self.status_text.set("Error: No hi ha text per desar")
         return

      # Diàlog per definir la ruta i nom de l'arxiu a desar
      #file_path = filedialog.asksaveasfilename(
      #   title="Desar la transcripció",
      #   defaultextension=".txt",
      #   filetypes=[("Arxius de text", "*.txt"), ("Tots els arxius", "*.*")]
      #)

      file_path = re.sub("\..{3}$", ".txt", self.audio_file_path.get())

      if file_path:
         try:
            with open(file_path, 'w', encoding='utf-8') as file:
               #current_language = self.language_combo.get()
               #file.write(f"Transcripció d'àudio - Idioma: {current_language}\n")
               #file.write(f"Arxiu: {os.path.basename(self.audio_file_path.get())}\n")
               #file.write("=" * 50 + "\n\n")
               file.write(text)
            self.status_text.set(f"Transcripció desada a: {file_path}")
         except Exception as e:
            self.status_text.set(f"Error en desar: {str(e)}")


def main():
   root = tk.Tk()
   AudioTranscriberApp(root)
   root.mainloop()

if __name__ == "__main__":
   main()
