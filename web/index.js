
eel.expose
async function dateipicker() {
    var csv_daten = await eel.datei_auswahl()()
    console.log(csv_daten)
    if (csv_daten===null) {
        alert("Achtung: Teilnehmendenliste entspricht nicht dem richtigen Format")
    }
    else {
        document.getElementById("checkmark").classList.add('tick-icon');
        document.getElementById("anzahl_studierende").innerHTML = `Anzahl Studierender in TN-Liste: ${csv_daten}`;
        document.getElementById("anzahl_studierende").value = csv_daten;
        document.querySelectorAll('.button').forEach(elem => {
            elem.disabled = false;
          });
        document.getElementById("copybutton").disabled=true
    }
}

async function addrow() {
    var row = document.getElementById("d1"); // find row to copy

    /*
    var table = document.getElementById("belegung"); // find table to append to
    var clone = row.cloneNode(true); // copy children too
    var anzahl_rows = document.getElementById("belegung").rows.length
    clone.id = `d${anzahl_rows}`; // change id or other attributes/contents
    clone.getElementById("durchgang").innerHTML = `Durchgang ${anzahl_rows}`;
    table.appendChild(clone); // add new row to end of table
    */
    var table = document.getElementById("belegung"); // find table to append to
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var anzahl_rows = document.getElementById("belegung").rows.length
    cell1.innerHTML = `Durchgang ${anzahl_rows}:`;
    cell2.innerHTML = `<INPUT TYPE="Checkbox" ID="eec1_${anzahl_rows}" Value="EEC1"><LABEL FOR="eec1_${anzahl_rows}">EEC1</LABEL> <INPUT TYPE="Checkbox" ID="eec2_${anzahl_rows}" Value="EEC2"><LABEL FOR="eec2_${anzahl_rows}">EEC2</LABEL>`;
}

async function deleterow() {
    var table = document.getElementById("belegung");
    var rowCount = table.rows.length;
    table.deleteRow(rowCount -1);

}

async function get_configuration() {
    var table = document.getElementById("belegung");
    var anzahl_rows = table.rows.length;

    var konfiguration = {};
    for (let i = 0; i < anzahl_rows; i++) {
        var durchgang = `Durchgang ${i+1}`
        var eec1 = document.getElementById(`eec1_${i+1}`).checked
        var eec2 = document.getElementById(`eec2_${i+1}`).checked

        var auswahl=false
        if (eec1){
            auswahl+=1
        }
        if (eec2){
            auswahl+=2
        }
        if (eec1 && eec2) {
            auswahl=3
        }
        if (auswahl!=false){
        konfiguration[durchgang]=auswahl
        }
      }

    if (Object.keys(konfiguration).length===0) {
        alert("Keine Räume ausgewählt")
    }
    else {
        var anzahl_studierende=document.getElementById("anzahl_studierende").value
        var puffergröße=document.getElementById("auswahl_puffer").value
        console.log(puffergröße)
        verteilung(konfiguration,anzahl_studierende,puffergröße)
    }
}

async function verteilung(konfiguration,anzahl_studierende,puffergröße){
    ergebnis = await eel.verteilung_python(konfiguration,anzahl_studierende,puffergröße)()
    
    if (ergebnis===false) {
        alert("Die Zahl der Teilnehmenden übersteigt die ausgewählten Räume. \nWählen Sie mehr Räume aus oder fügen Sie weitere Durchgänge hinzu!")
    }
    else if (ergebnis===true) {
        alert("Zur Verhinderung von Nachnamenüberschneidungen in verschiedenen Räumen wurden Plätze freigelassen: Anzahl der Teilnehmenden übersteigt nun die Anzahl verfügbarer Plätze. \nWählen Sie mehr Räume aus oder fügen Sie weitere Durchgänge hinzu!")
    }
    else {
        document.getElementById("emailtext").innerHTML=ergebnis
        if (ergebnis!="") {
            document.getElementById("copybutton").disabled=false
        }
        confirm("CSV-Output erstellt")
    }
}

async function populate_puffer() {
    var min = 1,
    max = 30,
    select = document.getElementById('auswahl_puffer');

    for (var i = min; i<=max; i++){
        var opt = document.createElement('option');
        opt.value = i;
        opt.innerHTML = i;
        select.appendChild(opt);
    }
}
populate_puffer()

function copy_to_clipboard(){
    var Text = document.getElementById("emailtext").innerHTML;
  
    /* Select the text inside text area. Text.select();*/
    
    Text = Text.replace(/<style([\s\S]*?)<\/style>/gi, '');
    Text = Text.replace(/<script([\s\S]*?)<\/script>/gi, '');
    Text = Text.replace(/<\/div>/ig, '\n');
    Text = Text.replace(/<\/li>/ig, '\n');
    Text = Text.replace(/<li>/ig, '- ');
    Text = Text.replace(/<\/ul>/ig, '\n');
    Text = Text.replace(/<\/p>/ig, '\n');
    Text = Text.replace(/<br\s*[\/]?>/gi, "\n");
    Text = Text.replace(/<[^>]+>/ig, "");
    Text = Text.replace(" -", "-");
    /*  */
    navigator.clipboard.writeText(Text);
    document.getElementById("copybutton").innerHTML="&#x2713; kopiert &nbsp; &nbsp;"
}


async function reset() {
    location.reload(true);
}