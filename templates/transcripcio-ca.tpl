{% include "head.tpl" %}
  <!--script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.min.js"></script-->
  <script src="/static/js/socket-io.js"></script>
</head>
<body>
  {% if idioma is defined %}
     {% set info_i = "idioma: " ~ idioma %}
  {% endif %}
  {% if arxiu is defined %}
     {% set info_a = "arxiu del dataset: " ~ arxiu %}
  {% endif %}

  <div>
    <div class="contenidor">
      <div class="titol">Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice</div>

      <div class="bloc_files">
        <div>{{info_a}}<br>{{info_i}}</div>
        <div id="arxiu_actual"></div>
      </div>

      <div class="bloc">
        <textarea id="area_transcripcio" name="transcripcio" rows="20" cols="89" placeholder="Aquí hauria d'aparèixer la transcripció corresponent del conjunt de dades"></textarea>
      </div>

      <dialog id="dlg_question">
        <form method="dialog">
          <p id="dlg_text"></p>
          <div>
            <button id="dlg_accept" type="submit">Sí</button>
            <button id="dlg_cancel" type="submit">No</button>
          </div>
        </form>
      </dialog>

      <div class="activity">
        <div class="grid_info">
          <div id="div_info" class="info text"></div>
          <div id="div_error" class="error text"></div>
        </div>

        <div class="grid_gender text">
          <div class="info bold float_left"><span>Gènere de l'àudio</span></div>
          <div id="div_gender" class="text info float_left">
            <input type="radio" id="home" name="r_gender"><label for="home">home</label><br>
            <input type="radio" id="dona" name="r_gender"><label for="dona">dona</label>
          </div>
        </div>

        <div class="grid_buttons">
          <img id="bt_next" class="imatge" src="{{url_for('static', filename='img/web-next-on.png')}}" title="registre següent">
          <img id="bt_play_stop" class="imatge" src="{{url_for('static', filename='img/web-play-on.png')}}" title="reproducció de l'àudio">
          <img id="bt_transcription" class="imatge" src="{{url_for('static', filename='img/web-transcription-on.png')}}" title="inici de la transcripció">
          <img id="bt_save" class="imatge" src="{{url_for('static', filename='img/web-save-on.png')}}" title="desa el registre">
          <img id="bt_exit" class="imatge" src="{{url_for('static', filename='img/web-exit-on.png')}}" title="sortir">
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
