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
   var ph = "Aquí hauria d'aparèixer la transcripció corresponent del dataset"
   document.getElementById("area_transcripcio").innerHTML = (data.text) ? data.text : "";
   document.getElementById("area_transcripcio").placeholder = (data.placeholder) ? data.placeholder : ph;
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
document.getElementById('bt_save').onclick = function() {
   var text = document.getElementById("area_transcripcio").innerText;
   socket.emit('save', {'text':text});
};

document.getElementById("div_genre").onclick = function() {
   let genre = document.querySelector('input[name="r_genre"]:checked');
   if (genre) {
      socket.emit('seleccioGenere', {'genre':genre.value});
   }
}

/* https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal */
const cancelButton = document.getElementById("cancel");
const dialog = document.getElementById("question");
dialog.returnValue = "favAnimal";

function openCheck(dialog) {
  if (dialog.open) {
    console.log("Dialog open");
  } else {
    console.log("Dialog closed");
  }
}

// Update button opens a modal dialog
updateButton.addEventListener("click", () => {
  dialog.showModal();
  openCheck(dialog);
});

// Form cancel button closes the dialog box
cancelButton.addEventListener("click", () => {
  dialog.close("animalNotChosen");
  openCheck(dialog);
});
