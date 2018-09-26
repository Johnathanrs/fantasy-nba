$(document).ready(function () {
  $('.tab-pane.slate input').on('change', function() {
    loadBoard();
  });

  $('.nav-tabs.slate .nav-link:first').click();
})

function loadBoard() {
  games = '';
  $('#tab-'+slate).find('input:checked').each(function() {
    games += $(this).val()+';';
  })

  var data = { 
        games: games
      };

  $('.team-board').html('<div class="board-loading ml-1 mt-5">Loading ...</div>');
  $.post( "/team-match-up", data, function( data ) {
    $('.team-board').html(data);
  });
}
