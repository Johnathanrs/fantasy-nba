$(document).ready(function () {
  $('.position-filter .nav-item a').on('click', function() {
    $('.position-filter .nav-item a').removeClass('active');
    $(this).toggleClass('active');
    loadBoard();
  })

  loadBoard();
})

function loadBoard() {
  var data = { 
        loc: $('.filters select.loc').val(), 
        ds: $('.filters select.ds').val(),
        pos: $('.position-filter .nav-item a.active').html()
      };

  $('.player-board').html('<div class="board-loading ml-1 mt-5">Loading ...</div>');
  $.post( "/player-match-up", data, function( data ) {
    $('.player-board').html(data);
  });
}
