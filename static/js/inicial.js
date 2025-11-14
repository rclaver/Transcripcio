var idioma, arxiu;
const divError = document.getElementById("div_error");
const arxiu_dataset = document.getElementById("id_arxiu_dataset");
//arxiu_dataset.validity.valueMissing = false;
//arxiu_dataset.validationMessage = "Selecciona un arxiu del conjunt de dades";
arxiu_dataset.addEventListener("change", seleccioArxiu);
document.getElementById("id_seleccio_idioma").addEventListener("change", seleccioIdioma);

function seleccioArxiu() {
  var input = document.querySelector("input");
  arxiu = input.files[0];
  var filepath = input.files[0].webkitRelativePath;
  divError.innerHTML = arxiu.name;
  retornFormulari();
}

function seleccioIdioma() {
   var s_idioma = document.getElementById("id_seleccio_idioma");
   var i = s_idioma.selectedIndex;
   idioma = s_idioma.options[i].value;
   switch (idioma) {
      case "ca-ES":
         document.getElementById("titol").innerHTML = "Transcripció d'àudios d'un conjunt de dades Mozilla Common Voice";
         document.getElementById("ss_idioma").innerHTML = "Selecció d'idioma ";
         document.getElementsByTagName("label").innerHTML = "Selecciona un arxiu";
         document.getElementById("sel_arxiu").innerHTML = "Selecciona un arxiu del conjunt de dades";
         //arxiu_dataset.validationMessage = "Selecciona un arxiu del conjunt de dades";
         break;
      case "en-US":
         document.getElementById("titol").innerHTML = "Audio transcription from a Mozilla Common Voice dataset";
         document.getElementById("ss_idioma").innerHTML = "Languaje selection ";
         document.getElementsByTagName("label").innerHTML = "Select file";
         document.getElementById("sel_arxiu").innerHTML = "Select dataset file";
         //arxiu_dataset.validationMessage = "Select dataset file";
         break;
      case "es-ES":
         document.getElementById("titol").innerHTML = "Transcripción de audios de un conjunto de datos Mozilla Common Voice";
         document.getElementById("ss_idioma").innerHTML = "Selección de idioma ";
         document.getElementsByTagName("label").innerHTML = "Selecciona un archivo";
         document.getElementById("sel_arxiu").innerHTML = "Selecciona un archivo del conjunto de datos";
         //arxiu_dataset.validationMessage = "Selecciona un archivo del conjunto de datos";
         break;
   }

   retornFormulari();
}

function retornFormulari() {
   if (arxiu.name) {
      if (validFileType(arxiu)) {
         form = document.getElementById("id_formulari");
         form.value = [arxiu.name, idioma];
         form.submit();
      }else {
         divError.innerHTML = "Tipus d'arxiu no vàlid";
      }
   }else {
      divError.innerHTML = "No has seleccionat cap arxiu";
   }
}

const fileTypes = [
  "text/tab-separated-values",
  "text/tsv",
  "text/csv"
];

function validFileType(file) {
  return fileTypes.includes(file.type);
}
