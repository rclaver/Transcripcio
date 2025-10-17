#!/bin/bash

#
# Comandos de descarga para CommonVoice Datasets
#

# ID de cliente: mdc_c7ec12a9df7ac255388b9460355441ab
# Clave API    : 09617bdd29c311d3509d3336b76b9e0a2aea16b90b92bbd63a4892c3bf207112
API=09617bdd29c311d3509d3336b76b9e0a2aea16b90b92bbd63a4892c3bf207112
arxiuJson=downloadToken.json

# «crear sesión de descarga» para obtener un token de descarga
curl -X POST "https://datacollective.mozillafoundation.org/api/datasets/cmflnuzz3xviy833er0w8x5o0/download"\
   -H "Authorization: Bearer ${API}" -H "Content-Type: application/json" > $arxiuJson

# Extreu l'URL amb TOKEN de l'arxiu prèviament obtingut
read -r downloadToken < $arxiuJson

partToken=${downloadToken//,\"expiresAt\":*}    # elimina la part posterior a l'expressió
httpToken=${partToken#\{*\"downloadUrl\":}      # elimina la primera part que conté l'expressió
httpToken=${httpToken//\"}                      # elimina todas las comillas

# «descargar» para obtener el archivo del conjunto de datos
curl -X GET $httpToken -H "Authorization: Bearer ${API}" -o "Common Voice Spontaneous Speech 1.0 - Catalan.tar.gz"
