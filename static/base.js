document.querySelector('#elastic').oninput = function () {
    let val = this.value.trim().toLowerCase();
    let elasticItems = document.querySelectorAll('.elastic li');
    if (val != '') {
        elasticItems.forEach(function (elem) {
            if (elem.innerText.toLowerCase().search(val) == -1) {
                elem.classList.remove('hide');
            } 
            else {
                elem.classList.add('hide');
            }
        });
    }
    else{
        elasticItems.forEach(function(elem){
            elem.classList.remove('hide')
        });
    }
}

function insertMark () {
    
}