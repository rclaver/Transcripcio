/***
 Model XMLHttpRequest
*/
function play(escena) {
   var xhr;
   var contenidoRecibido = '';

   if (escena.length===0) {
      document.getElementById("escena_actual").innerHTML = "";
      return;
   }
   xhr = new XMLHttpRequest();

   xhr.onreadystatechange = function() {
      if (xhr.readyState===4 && xhr.status===200) {
         contenidoRecibido = xhr.responseText;
         document.getElementById("escena_actual").innerHTML = contenidoRecibido;
      }
   };
   xhr.open("POST","apuntador.py?escena="+escena);
   xhr.send();
}

/***
 Obtenció de propietats
*/
function get_parametres(param) {
   let params = new URLSearchParams(document.location.search);
   let value = params.get(param);
   return value;
}

function visible(e, es_visible) {
   let d = ((es_visible) ? "block" : "none");
   let v = ((es_visible) ? "visible" : "hidden");
   document.getElementById(e).style.display = d;
   document.getElementById(e).style.visibility = v;
}

function get_propietat(e) {
   return "weight: " + document.getElementById(e).style.fontWeight + ".";
}

function get_screen_sizes(selection) {
   var sizes;
   if (selection === "min") {
      sizes = "- body.clientHeight: " + document.body.clientHeight + "<br>" +
              "- window.screen.height: " + window.screen.height + "<br>" +
              "- window.innerHeight: " + window.innerHeight + "<br>" +
              "- body.clientWidth: " + document.body.clientWidth + "<br>" +
              "- window.screen.width: " + window.screen.width + "<br>" +
              "- window.innerWidth: " + window.innerWidth;
   }else {
      sizes = "- body.scrollHeight: " + document.body.scrollHeight + "<br>" +
              "- documentElement.scrollHeight: " + document.documentElement.scrollHeight + "<br>" +
              "- body.offsetHeight: " + document.body.offsetHeight + "<br>" +
              "- documentElement.offsetHeight: " + document.documentElement.offsetHeight + "<br>" +
              "- body.clientHeight: " + document.body.clientHeight + "<br>" +
              "- documentElement.clientHeight: " + document.documentElement.clientHeight + "<br>" +
              "- body.scrollWidth: " + document.body.scrollWidth + "<br>" +
              "- documentElement.scrollWidth: " + document.documentElement.scrollWidth + "<br>" +
              "- body.offsetWidth: " + document.body.offsetWidth + "<br>" +
              "- documentElement.offsetWidth: " + document.documentElement.offsetWidth + "<br>" +
              "- body.clientWidth: " + document.body.clientWidth + "<br>" +
              "- documentElement.clientWidth: " + document.documentElement.clientWidth;
   }
   return sizes;
}

/***
 Mostra els tipus mime d'audio i video suportats
*/
function getSupportedMimeTypes(media, types, codecs) {
  const isSupported = MediaRecorder.isTypeSupported;
  const supported = [];
  types.forEach((type) => {
    const mimeType = `${media}/${type}`;
    codecs.forEach((codec) => [
        `${mimeType};codecs=${codec}`,
        `${mimeType};codecs=${codec.toUpperCase()}`,
      ].forEach(variation => {
        if(isSupported(variation))
            supported.push(variation);
    }));
    if (isSupported(mimeType))
      supported.push(mimeType);
  });
  return supported;
};

const videoTypes = ["webm", "ogg", "mp4", "x-matroska"];
const audioTypes = ["webm", "ogg", "mp3", "x-matroska"];
const codecs = ["should-not-be-supported","vp9", "vp9.0", "vp8", "vp8.0", "avc1", "av1", "h265", "h.265", "h264", "h.264", "opus", "pcm", "aac", "mpeg", "mp4a"];

const supportedVideos = getSupportedMimeTypes("video", videoTypes, codecs);
const supportedAudios = getSupportedMimeTypes("audio", audioTypes, codecs);

//console.log('-- All supported Videos : ', supportedVideos)
console.log('-- All supported Audios : ', supportedAudios)


/***
 Reproduce un fichero de audio; teóricamente hasta que finaliza
*/
let audio = new Audio();
function playAudio(opcio) {
   function audioPlay() {
      if (!opcio) {
         audio.removeEventListener('ended', audioPlay);
         return;
      }
      audio.src = "static/tmp/temp.wav";
      audio.play();
   }
   audio.addEventListener('ended', audioPlay);
   audioPlay();
}

/***
 Grava l'audio captat pel micròfon en un arxiu d'audio
*/
var gravacio = false;

if (navigator.mediaDevices) {
   navigator.mediaDevices
      .getUserMedia({audio:true})
      .then(stream => { gestorMicrofon(stream) })
      .catch((err) => {
         alert("error getUserMedia: "+ err)
      });

   function gestorMicrofon(stream) {
      const options = {
        mimeType: 'audio/webm',
        numberOfAudioChannels: 1,
        sampleRate: 16000,
      };
      rec = new MediaRecorder(stream, options);
      rec.ondataavailable = e => {
         audioChunks.push(e.data);
         if (rec.state == "inactive") {
            let blob = new Blob(audioChunks, {type: 'audio/webm'});
            sendData(blob);
         }
      }
   }

   function sendData(data) {
       var form = new FormData();
       form.append('file', data, 'static/tmp/gravacio.mp3');
       $.ajax({
           type: 'POST',
           url: '/desa-gravacio',
           data: form,
           cache: false,
           processData: false,
           contentType: false
       }).done(function(data) {
           console.log(data);
       });
   }

   bt_gravacio.onclick = e => {
       if (gravacio) {
          setTimeout(2000);
          gravacio = false;
          rec.stop();
       }else {
          document.getElementById("div_error").innerText = "iniciant gravació ...";
          gravacio = true;
          audioChunks = [];
          rec.start();
       }
   };
}

