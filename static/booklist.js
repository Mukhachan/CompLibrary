// Когда пользователь нажимает на <div>, открыть popup
function myFunction(id) {
    var popup = document.getElementById(id);
    popup.classList.toggle("show");
}

var modal = $modal({
    title: 'Вы уверены что хотите удалить?',
    content: 'Восстановить книгу уже не удастся',
    footerButtons: [
      { class: 'btn btn__cancel', text: 'Отмена', handler: 'modalHandlerCancel' },
      { class: 'btn btn__yes', text: 'Да', handler: 'modalHandlerYes' }
    ]
  });