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

      <div id="arxiu_actual">{{info_i}} {{info_a}}</div>

      <!--div id="transcripcio" class="bloc transcripcio text"></div-->
      <div class="bloc">
        <textarea id="area_transcripcio" name="transcripcio" rows="20" cols="89" placeholder="Aquí hauria d'aparèixer la transcripció corresponent del dataset"></textarea>
      </div>

      <div id="div_botons" class="div_botons">
        <img id="bt_next" class="imatge" src="{{url_for('static', filename='img/next.png')}}" title="next record in dataset">
        <img id="bt_play_audio" class="imatge" src="{{url_for('static', filename='img/play_audio.png')}}" title="play audio current record">
        <img id="bt_stop" class="imatge" src="{{url_for('static', filename='img/stop.png')}}" title="stop audio playback">
        <img id="bt_transcripcio" class="imatge" src="{{url_for('static', filename='img/transcripcio.png')}}" title="start audio transcription">
        <img id="bt_clear" class="imatge" src="{{url_for('static', filename='img/clear.png')}}" title="clear all items">
      </div>
      <img id="bt_save" class="invisible" src="{{url_for('static', filename='img/save.png')}}">
      <audio id="audio" autoplay="autoplay" preload="none" type="audio/wav"></audio>
      <div id="div_error" class="error text"></div>

    </div>
  </div>

  <script>
    document.addEventListener("DOMContentLoaded", () => {
      socket.emit('start');
    });
  </script>
  <script src="/static/js/connexio.js"></script>
</body>
