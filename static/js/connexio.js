/***
 Gestiona la comunicació entre el servidor i el client
*/
var estat;
var boto = "next";

// Connectar-se al servidor WebSocket
const socket = io.connect("http://" + document.domain + ":" + location.port);

// Esdeveniment que es dispara quan el servidor envia una informació
socket.on('information', function(data) {
   estat = (data.estat) ? data.estat : "";
   document.getElementById("div_info").innerText = (data.info) ? data.info+estat : "";
   document.getElementById("div_error").innerText = (data.error) ? data.error : "";
   if (data.arxiu_audio) {
      document.getElementById("arxiu_actual").innerText = data.arxiu_audio
   }
});

socket.on('new_transcription', function(data) {
   document.getElementById("area_transcripcio").innerHTML = data.text;
   document.getElementById("div_error").innerText = (data.error) ? data.error : "";
});

document.getElementById('bt_next').onclick = function() {
   var text = document.getElementById("area_transcripcio").innerText;
   socket.emit('next', {'text':text});
};
document.getElementById('bt_play_audio').onclick = function() {
   socket.emit('play_audio');
};
document.getElementById('bt_stop').onclick = function() {
   socket.emit('stop');
};
document.getElementById('bt_transcripcio').onclick = function() {
   socket.emit('transcripcio');
};
document.getElementById('bt_exit').onclick = function() {
   location.href = '/index';
   socket.emit('exit');
};

