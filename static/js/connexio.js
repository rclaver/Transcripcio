/***
 Gestiona la comunicació entre el servidor i el client
*/
var estat;
var boto = "play";

function getTranscriptionArea() {
   const area = document.getElementById("area_transcripcio");
   return (area.value) ? area.value : area.innerHTML;
}

// Connectar-se al servidor WebSocket
const socket = io.connect("http://" + document.domain + ":" + location.port);

// Esdeveniment que es dispara quan el servidor envia una informació
socket.on('information', function(data) {
   document.getElementById("div_info").innerText = (data.info) ? data.info : "";
   document.getElementById("div_error").innerText = (data.error) ? data.error : "";
   if (data.arxiu_audio) {
      document.getElementById("arxiu_actual").innerText = data.arxiu_audio
   }
});

socket.on('new_transcription', function(data) {
   const ph = "Aquí hauria d'aparèixer la transcripció corresponent del dataset"
   document.getElementById("area_transcripcio").innerHTML = (data.text) ? data.text : "";
   document.getElementById("area_transcripcio").value = (data.text) ? data.text : "";
   document.getElementById("area_transcripcio").placeholder = (data.placeholder) ? data.placeholder : ph;
   document.getElementById("div_error").innerText = (data.error) ? data.error : "";
});

socket.on('set_gender', function(data) {
   if (data.gender == "male_masculine") {
      document.getElementById('home').checked = true;
   }else if (data.gender == "female_feminine") {
      document.getElementById('dona').checked = true;
   }else {
      document.getElementById('home').checked = false;
      document.getElementById('dona').checked = false;
   }
});

const bt_next = document.getElementById('bt_next');
const bt_playStop = document.getElementById('bt_play_stop');
const bt_transcription = document.getElementById('bt_transcription');
const bt_save = document.getElementById('bt_save');
const bt_exit = document.getElementById('bt_exit');

socket.on('toggle_buttons', function(data) {
   switch (data.estat) {
      case "play":
         bt_next.src = "static/img/web-next-off.png";
         bt_next.alt = bt_next.title;
         bt_next.title = "inactive";
         boto = "stop";
         bt_playStop.src = "static/img/web-stop-on.png";
         bt_playStop.title ="stop audio playback";
         bt_transcription.src = "static/img/web-transcription-off.png";
         bt_transcription.alt = bt_transcription.title;
         bt_transcription.title = "inactive";
         bt_save.src = "static/img/web-save-off.png";
         bt_save.alt = bt_save.title;
         bt_save.title = "inactive";
         bt_exit.src = "static/img/web-exit-off.png";
         bt_exit.alt = bt_exit.title;
         bt_exit.title = "inactive";
         break;
      case "stop":
         bt_next.src = "static/img/web-next-on.png";
         bt_next.title = bt_next.alt;
         boto = "play";
         bt_playStop.src = "static/img/web-play-on.png";
         bt_playStop.title ="play audio current record";
         bt_transcription.src = "static/img/web-transcription-on.png";
         bt_transcription.title = bt_transcription.alt;
         bt_save.src = "static/img/web-save-on.png";
         bt_save.title = bt_save.alt;
         bt_exit.src = "static/img/web-exit-on.png";
         bt_exit.title = bt_exit.alt;
         break;
      case "transcription":
         bt_next.src = "static/img/web-next-off.png";
         bt_next.alt = bt_next.title;
         bt_next.title = "inactive";
         bt_playStop.src = "static/img/web-play-off.png";
         bt_playStop.alt = bt_playStop.title;
         bt_playStop.title = "inactive";
         bt_save.src = "static/img/web-save-off.png";
         bt_save.alt = bt_save.title;
         bt_save.title = "inactive";
         bt_exit.src = "static/img/web-exit-off.png";
         bt_exit.alt = bt_exit.title;
         bt_exit.title = "inactive";
         break;
      case "end_transcription":
         bt_next.src = "static/img/web-next-on.png";
         bt_next.title = bt_next.alt;
         bt_playStop.src = "static/img/web-play-on.png";
         bt_playStop.title = bt_playStop.alt;
         bt_save.src = "static/img/web-save-on.png";
         bt_save.title = bt_save.alt;
         bt_exit.src = "static/img/web-exit-on.png";
         bt_exit.title = bt_exit.alt;
         break;
   }
});

bt_next.onclick = function() {
   if (bt_next.title != "inactive") {
      const text = getTranscriptionArea() ;
      socket.emit('next', text);
   }
};
bt_playStop.onclick = function() {
   if (bt_playStop.title != "inactive") {
      socket.emit(boto);  //envia esdeveniment al servidor
      boto = (boto == "play") ? "stop" : "play";
   }
};
bt_transcription.onclick = function() {
   if (bt_transcription.title != "inactive") {
      socket.emit('transcription');
   }
};
bt_save.onclick = function() {
   if (bt_save.title != "inactive") {
      const text = getTranscriptionArea() ;
      socket.emit('save', text);
   }
};
bt_exit.onclick = function() {
   if (bt_exit.title != "inactive") {
      location.href = '/index';
      socket.emit('exit');
   }
};

document.getElementById("div_gender").onclick = function() {
   const gender = document.querySelector('input[name="r_gender"]:checked');
   if (gender) {
      socket.emit('seleccioGenere', gender.id);
   }
}

/* https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal */
const dialog = document.getElementById("dlg_question");
const dialogText = document.getElementById("dlg_text");
const acceptButton = document.getElementById("dlg_accept");
const cancelButton = document.getElementById("dlg_cancel");

socket.on('dialog', function(data) {
   if (data.text) {
      dialogText.innerHTML = data.text;
      dialog.showModal();
   }
});

acceptButton.addEventListener("click", () => {
   dialog.close("S");
   socket.emit('dialog', "S");
});
cancelButton.addEventListener("click", () => {
   dialog.close("N");
   socket.emit('dialog', "N");
});
