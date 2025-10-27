import pandas as pd
import os
# Exemple d'ensinistrament bàsic amb Mozilla TTS
from TTS.utils.training import Trainer
from TTS.config import load_config
from TTS.tts.datasets import DatasetLoader


def llegir_data_set():
   #client_id
   #audio_id
   #audio_file
   #duration_ms
   #prompt_id
   #prompt (pregunta)
   #transcription (respuesta de audio)
   #votes
   #age
   #gender
   #language
   #split
   #char_per_sec
   #quality_tags
   return pd.read_csv('ss-corpus-ca.tsv', sep='\t')

# Filtrar dades de qualitat
def filtrar_dades(dades):
   #high_quality_data = metadata[
   #    (dades['up_votes'] > metadata['down_votes']) &
   #    (dades['client_id'].duplicated(keep=False))
   #]
   return metadata[(not dades['transcription'])]

# Configuració del model d'ensisitrament
def cofiguracio():
   config = load_config("tts_model_config.json")
   config.data_path = "./sps-corpus-1.0-2025-09-05-ca"

   trainer = Trainer(config)
   trainer.fit()

# Preparar estructura para entrenamiento
def preparacio():
   for index, row in high_quality_data.iterrows():
       audio_path = f"audios/{row['audio_file']}"
       text = row['transcription']
       # Procesar para tu modelo TTS

if __name__ == "__main__":
   dades = llegir_data_set()
   dades = filtrar_dades(dades)
   preparacio(dades)

# fi