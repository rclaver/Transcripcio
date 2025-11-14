{% include "head.tpl" %}
</head>

<body>
  <div>
    <div class="contenidor">
      <div class="titol" id="titol">Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice</div>

      <form id="id_formulari" method="post" action="transcripcio" enctype="multipart/form-data">
        <div class="bloc">
          <div id="div_seleccio_idioma">
            <span id="ss_idioma" class="gran">Selecció d'idioma </span>
            <select name="seleccio_idioma" id="id_seleccio_idioma">
              <option value="ca-ES">Català</option>
              <option value="es-ES">Español</option>
              <option value="en-US">English</option>
            </select>
          </div>
        </div>

        <div class="bloc">
          <span id="sel_arxiu" class="gran">Selecciona un arxiu del conjunt de dades</span>
          <input type="file" id="id_arxiu_dataset" name="arxiu_dataset" accept="text/csv,.tsv" required>
          <label for="id_arxiu_dataset"><img src="{{url_for('static', filename='img/search.png')}}"></label>
        </div>
      </form>
      <div id="div_error"></div>

    </div>
  </div>

   <script src="/static/js/inicial.js"></script>
</body>
