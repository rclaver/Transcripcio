# -*- coding: utf-8 -*-
"""
Connexió: Accés a OpenAI
"""

from openai import OpenAI


def read_api_key():
   f = open("API_Key_OpenAI", "r")
   key = f.read()
   f.close()
   return key

client = OpenAI(apikey = read_api_key())
prompt = "Lee el texto de un archivo de disco"
contexto = "Eres un creador de voces artificiales"
completion = client.chat.completions.create(
   model = "TTS",
   messages = [{"role":"system", "content":contexto},
               {"role":"user", "content":prompt}
              ]
   )
