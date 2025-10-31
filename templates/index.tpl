{% include "head.tpl" %}
</head>

<body>
  <div>
    <div class="contenidor">
      <div class="titol">Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice</div>

      <form id="id_formulari" method="post" action="transcripcio" enctype="multipart/form-data" onBlur="Q_formulari();">
        <div class="bloc">
          <div id="div_seleccio_idioma">
            <span>Selecció d'idioma: </span>
            <select name="seleccio_idioma" id="id_seleccio_idioma">
              <option value="ca-ES">Català</option>
              <option value="es-ES">Español</option>
              <option value="en-US">English</option>
            </select>
          </div>
        </div>

        <div class="bloc">
          <label for="id_arxiu_dataset">Selecciona l'arxiu del dataset</label>
          <input type="file" id="id_arxiu_dataset" name="arxiu_dataset" accept="text/csv,.tsv" required>
          <span id="arxiu_actual">Selecciona un arxiu</span>
        </div>
      </form>

    </div>
  </div>

   <script src="/static/js/script.js"></script>
</body>
