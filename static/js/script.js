var idioma, arxiu;
var resposta = document.getElementById("arxiu_actual");
document.getElementById("id_arxiu_dataset").addEventListener("change", seleccioArxiu);
document.getElementById("id_seleccio_idioma").addEventListener("change", seleccioIdioma);

function seleccioArxiu() {
  var input = document.querySelector("input");
  arxiu = input.files[0];
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

function updateFileNameDisplay() {
  const curFiles = input.files;
  if (curFiles.length != 0) {
    document.getElementById("arxiu_actual").innerHTML = curFiles;
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

/* --------------------------------
const input = document.querySelector("input");
const preview = document.querySelector(".preview");

input.style.opacity = 0;
input.addEventListener("change", updateFileNameDisplay);

function updateFileNameDisplay() {
  while (preview.firstChild) {
    preview.removeChild(preview.firstChild);
  }

  const curFiles = input.files;
  if (curFiles.length === 0) {
    const para = document.createElement("p");
    para.textContent = "No hay archivos seleccionados actualmente para subir";
    preview.appendChild(para);
  } else {
    const list = document.createElement("ol");
    preview.appendChild(list);

    for (const file of curFiles) {
      const listItem = document.createElement("li");
      const para = document.createElement("p");
      if (validFileType(file)) {
        para.textContent = `Nombre del archivo ${file.name}, tamaño del archivo ${returnFileSize(
          file.size,
        )}.`;
        const image = document.createElement("img");
        image.src = URL.createObjectURL(file);
        image.alt = image.title = file.name;

        listItem.appendChild(image);
        listItem.appendChild(para);
      } else {
        para.textContent = `Nombre del archivo ${file.name}: Tipo de archivo no válido. Actualiza tu selección.`;
        listItem.appendChild(para);
      }

      list.appendChild(listItem);
    }
  }
}
// https://developer.mozilla.org/es/docs/Web/Media/Formats/Image_types
const fileTypes = [
  "image/apng",
  "image/bmp",
  "image/gif",
  "image/jpeg",
  "image/pjpeg",
  "image/png",
  "image/svg+xml",
  "image/tiff",
  "image/webp",
  "image/x-icon",
];

function validFileType(file) {
  return fileTypes.includes(file.type);
}
function returnFileSize(number) {
  if (number < 1e3) {
    return `${number} bytes`;
  } else if (number >= 1e3 && number < 1e6) {
    return `${(number / 1e3).toFixed(1)} KB`;
  } else {
    return `${(number / 1e6).toFixed(1)} MB`;
  }
}
const button = document.querySelector("form button");
button.addEventListener("click", (e) => {
  e.preventDefault();
  const para = document.createElement("p");
  para.append("Image uploaded!");
  preview.replaceChildren(para);
});
-------------------------------- */
