{% include "head.tpl" %}
  <!--script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.min.js"></script-->
  <script src="/static/js/socket-io.js"></script>
</head>
<body bgcolor="#FFFFFF">
  {% if idioma is defined %}
     {% set info_i = "idioma: " ~ idioma %}
  {% endif %}
  {% if arxiu is defined %}
     {% set info_a = " - arxiu del dataset: " ~ arxiu %}
  {% endif %}

  <div>
    <div class="contenidor">
      <div class="titol">Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice</div>

      <div class="bloc_files">
        <div id="dataset">{{info_i}} {{info_a}}</div>
        <div id="arxiu_actual"></div>
      </div>

      <div class="bloc">
        <textarea id="area_transcripcio" name="transcripcio" rows="20" cols="89" placeholder="Aquí hauria d'aparèixer la transcripció corresponent del dataset"></textarea>
      </div>

      <div class="activity">
        <div class="grid_info">
          <div id="div_info" class="info text"></div>
          <div id="div_error" class="error text"></div>
        </div>

        <div class="grid_genre info text">
          <div class="info text float_left"><span>Gènere de l'àudio</span></div>
          <div id="div_genre" class="info text float_left">
            <input type="radio" id="home" name="r_genre" value="HTML"><label for="home">home</label><br>
            <input type="radio" id="dona" name="r_genre" value="HTML"><label for="dona">dona</label><br>
          </div>
        </div>

        <div id="grid_buttons" class="div_botons">
          <img id="bt_next" class="imatge" src="{{url_for('static', filename='img/next.png')}}" title="next record in dataset">
          <img id="bt_play_audio" class="imatge" src="{{url_for('static', filename='img/play_audio.png')}}" title="play audio current record">
          <img id="bt_stop" class="imatge" src="{{url_for('static', filename='img/stop.png')}}" title="stop audio playback">
          <img id="bt_transcripcio" class="imatge" src="{{url_for('static', filename='img/transcripcio.png')}}" title="start audio transcription">
          <img id="bt_save" class="imatge invisible" src="{{url_for('static', filename='img/save.png')}}" title="save record">
          <img id="bt_exit" class="imatge" src="{{url_for('static', filename='img/exit.png')}}" title="exit">
        </div>
      </div>

    </div>
  </div>

  <script>
    document.addEventListener("DOMContentLoaded", () => {
      socket.emit('start');
    });
  </script>
  <script src="/static/js/connexio.js"></script>
</body>
