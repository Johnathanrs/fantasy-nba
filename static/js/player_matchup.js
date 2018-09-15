$(document).ready(function () {
  loadBoard();
})

function loadBoard() {
  var data = { 
        loc: $('.filters select.loc').val(), 
        ds: $('.filters select.ds').val(),
        pos: $('.filters select.pos').val(),
      };

  $.post( "/player-match-up", data, function( data ) {
    $('.player-board').html(data);
  });
}
