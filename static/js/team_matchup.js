$(document).ready(function () {
  $('.game-item').on('click', function() {
    $('.game-item').removeClass('active');
    $(this).addClass('active');
    loadBoard($(this).data('game'));
  });

  $('.nav-tabs.slate a').on('shown.bs.tab', function(event) {
    var slate = $(event.target).text();
    $('#tab-'+slate+' .game-item:first').click();
  });
  
  $('.nav-tabs.slate .nav-link:first').click();
})

function loadBoard(game) {
  $('.team-board').html('<div class="board-loading ml-1 mt-5">Loading ...</div>');
  $.post( "/team-match-up", { game: game }, function( data ) {
    $('.team-board').html(data);
  });
}
