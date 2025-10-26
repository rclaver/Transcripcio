{% include "head.tpl" %}
</head>

<body bgcolor="#FFFFFF">
  <div>
    <div class="contenidor">
      <div class="titol">Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice</div>
      <div class="bloc">
        <form id="id_formulari" class="formulari" method="post" onClick="Q_formulari();" action="transcripcio">
          <div id="div_seleccio_idioma">
            <span>Selecció d'idioma {{idioma}}: </span>
            <select name="seleccio_idioma" id="id_seleccio_idioma">
              <option value="ca-ES">Català</option>
              <option value="es-ES">Español</option>
              <option value="en-US">English</option>
            </select>
          </div>
        </form>
      </div>

      <div class="bloc">
        <form method="POST" action="transcripcio" enctype="multipart/form-data">
          <label for="id_arxiu">Selecciona l'arxiu del dataset</label>
          <input type="file" id="id_arxiu" name="arxiu" accept="text/csv,.tsv" required>
          <!--button type="submit">Acceptar</button-->
        </form>
      </div>

      <div id="arxiu_actual">Selecciona un arxiu del conjunt de dades</div>
      <!--div id="transcripcio" class="bloc transcripcio text"></div-->

      <div class="bloc">
        <textarea id="transcripcio" name="transcripcio" rows="20" cols="89" placeholder="Aquí hauria d'aparèixer la transcripció corresponent del dataset"></textarea>
      </div>

      <div id="div_botons" class="div_botons">
        <img id="bt_next" class="imatge" src="{{url_for('static', filename='img/next.png')}}" title="next record in dataset">
        <img id="bt_play" class="imatge" src="{{url_for('static', filename='img/play_audio.png')}}" title="play audio current record">
        <img id="bt_stop" class="imatge" src="{{url_for('static', filename='img/stop.png')}}" title="stop audio playback">
        <img id="bt_transcripcio" class="imatge" src="{{url_for('static', filename='img/transcripcio.png')}}" title="start audio transcription">
        <img id="bt_clear" class="imatge" src="{{url_for('static', filename='img/clear.png')}}" title="clear all items">
      </div>
      <img id="bt_save" class="invisible" src="{{url_for('static', filename='img/save.png')}}">
      <audio id="audio" autoplay="autoplay" preload="none" type="audio/wav"></audio>
      <div id="div_error" class="error text"></div>

    </div>
  </div>

<script src="/static/js/script.js"></script>
<!--script>
  const input = document.querySelector("input");
  //input.style.opacity = 0;
</script-->
</body>
