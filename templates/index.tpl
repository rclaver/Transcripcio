{% include "head.tpl" %}
  <script src="/static/js/script.js"></script>
</head>

<body bgcolor="#FFFFFF">
  <div>
    <div class="contenidor">
      <div class="titol">Transcripció d'àudios del conjunt de dades Mozilla Common Voice</div>
      <div class="bloc">
        <form method="POST" action="/download" enctype="multipart/form-data">
          <label for="id_arxiu">Selecciona l'arxiu del dataset</label>
          <input type="file" id="id_arxiu" name="arxiu" accept=".txt,.tsv,.csv" required>
          <button type="submit">Acceptar</button>
        </form>
      </div>

      <div class="bloc">
        <form id="formulari" class="formulari" method="post" onClick="formulari();" action="apuntador">
          <div id="div_seleccio_idioma">
            <span>Selecció d'idioma {{idioma}}: </span>
            <select name="seleccio_idioma" id="seleccio_idioma">
              <option value="ca-ES">Català</option>
              <option value="es-ES">Español</option>
              <option value="en-US">English</option>
            </select>
          </div>
        </form>
      </div>

      <div id="arxiu_actual" class="escena text">{{sentencia}}</div>

      <div class="bloc">
        <textarea id="transcripcio" name="transcripcio" rows="20" cols="89" placeholder="Aquí hauria d'aparèixer la transcripció corresponent del dataset"></textarea>
      </div>

      <div id="div_botons" class="div_botons contenidor">
        <img id="bt_next" class="imatge" src="{{url_for('static', filename='img/next.png')}}">
        <img id="bt_play" class="imatge" src="{{url_for('static', filename='img/play_audio.png')}}">
        <img id="bt_stop" class="imatge" src="{{url_for('static', filename='img/stop.png')}}">
        <img id="bt_transcripcio" class="imatge" src="{{url_for('static', filename='img/transcripcio.png')}}">
        <img id="bt_clear" class="imatge" src="{{url_for('static', filename='img/clear.png')}}">
      </div>
      <img id="bt_gravacio" class="invisible" src="{{url_for('static', filename='img/web-gravacio.png')}}">
      <audio id="audio" autoplay="autoplay" preload="none" type="audio/wav"></audio>
      <div id="div_error" class="error text"></div>

    </div>
  </div>

<script>
  const input = document.querySelector("input");
  input.style.opacity = 0;
</script>
</body>
