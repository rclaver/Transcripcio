/***
 Gestiona la comunicació entre el servidor i el client
*/
var boto = "inici";

// Connectar-se al servidor WebSocket
const socket = io.connect("https://" + document.domain + ":" + location.port);

// Esdeveniment que es dispara quan el servidor envia una nova línia
socket.on('new_line', function(data) {
   const error = document.getElementById("div_error");
   const escena = document.getElementById("escena_actual");
   escena.innerText = data.frase;
   error.innerText = (data.error) ? data.error : "";
});

const multiboto = document.getElementById('bt_multiboto');
multiboto.onclick = function() {
   const boto_actiu = boto;
   boto = (boto == "inici") ? "pausa" : "inici";
   this.src = "static/img/web-" + boto + ".png";
   socket.emit(boto_actiu);  //envia esdeveniment al servidor
};

document.getElementById('bt_stop').onclick = function() {
   boto = "inici";
   multiboto.src = "static/img/web-" + boto + ".png";
   socket.emit('stop');
};
document.getElementById('bt_anterior').onclick = function() {
   socket.emit('anterior');
};
document.getElementById('bt_seguent').onclick = function() {
   socket.emit('seguent');
};
