$(document).ready(function () {
  loadBoard();
})

function loadBoard() {
  var data = { 
        loc: $('.filters select.loc').val(), 
        ds: $('.filters select.ds').val(),
        pos: $('.filters select.pos').val(),
      };

  $('.player-board').html('<div class="board-loading ml-1 mt-5">Loading ...</div>');
  $.post( "/player-match-up", data, function( data ) {
    $('.player-board').html(data);
  });
}
