var idioma, arxiu;
var resposta = document.getElementById("arxiu_actual");
var arxiu_dataset = document.getElementById("id_arxiu_dataset");
arxiu_dataset.validity.valueMissing = false;
arxiu_dataset.validationMessage = "Selecciona un arxiu del conjunt de dades";
arxiu_dataset.addEventListener("change", seleccioArxiu);
document.getElementById("id_seleccio_idioma").addEventListener("change", seleccioIdioma);

function seleccioArxiu() {
  var input = document.querySelector("input");
  arxiu = input.files[0];
  var filepath = input.files[0].webkitRelativePath;
  resposta.innerHTML = arxiu.name;
  retornFormulari();
}

function seleccioIdioma() {
   var s_idioma = document.getElementById("id_seleccio_idioma");
   var i = s_idioma.selectedIndex;
   idioma = s_idioma.options[i].value;
   retornFormulari();
}

function retornFormulari() {
   if (arxiu.name) {
      if (validFileType(arxiu)) {
         form = document.getElementById("id_formulari");
         form.value = [arxiu.name, idioma];
         form.submit();
      }else {
         resposta.innerHTML = "Tipus d'arxiu no vàlid";
      }
   }else {
      resposta.innerHTML = "No has seleccionat cap arxiu";
   }
}

function formulari() {
   seleccioIdioma();
   seleccioArxiu();
}

const fileTypes = [
  "text/tab-separated-values",
  "text/tsv",
  "text/csv"
];

function validFileType(file) {
  return fileTypes.includes(file.type);
}
