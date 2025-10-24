{% include "head.tpl" %}
  <!--script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.min.js"></script-->
  <script src="/static/js/socket-io.js"></script>
</head>

<body bgcolor="#FFFFFF">
  {% if sentencia is not defined %}
     {% set sentencia = "Escenes per a: " ~ actor %}
  {% endif %}

  <div class="contenidor">
    <div class="titol">Transcripció</div>
    <div id="div_error" class="error text"></div>
    <div id="escena_actual" class="escena text">{{sentencia}}</div>
    <div id="div_botons" class="div_botons contenidor">
      <img id="bt_anterior" class="imatge" src="{{url_for('static', filename='img/web-anterior.png')}}">
      <img id="bt_stop" class="imatge" src="{{url_for('static', filename='img/web-stop.png')}}">
      <img id="bt_multiboto" class="imatge" src="{{url_for('static', filename='img/web-inici.png')}}">
      <img id="bt_seguent" class="imatge" src="{{url_for('static', filename='img/web-seguent.png')}}">
    </div>
    <img id="bt_gravacio" class="invisible" src="{{url_for('static', filename='img/web-gravacio.png')}}">
    <audio id="audio" autoplay="autoplay" preload="none" type="audio/wav"></audio>
  </div>
  <script src="/static/js/apuntador.js"></script>
</body>
