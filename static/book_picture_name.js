function myFunction(){
    var x = document.getElementById("fileElem");
    var txt = "";
    if ('files' in x) {
      for (var i = 0; i < x.files.length; i++) {
        var file = x.files[i];
        if ('name' in file) {
          txt += file.name;
        }
      }
      
    } 
    document.getElementById("demo").innerHTML = txt;
    document.getElementById("inp").value = txt;
  }