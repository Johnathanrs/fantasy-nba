var game;

$(document).ready(function () {
  $( ".slider-range" ).slider({
    range: true,
    min: 1,
    step: 0.1,
    max: 100,
    values: [ 1, 100 ],
    change: function( event, ui ) {
      $(this).parent().find('.slider-val').val(ui.values[ 0 ] + " - " + ui.values[ 1 ]);
      loadBoard();
    }
  });

  $( ".slider-val" ).val("1 - 100");
  
  $('.game-item').on('click', function() {
    $('.game-item').removeClass('active');
    $(this).addClass('active');
    game = $(this).data('game');
    loadBoard();
  });

  $('.nav-tabs.slate a').on('shown.bs.tab', function(event) {
    var slate = $(event.target).text();
    $('#tab-'+slate+' .game-item:first').click();
  });
  
  $('.nav-tabs.slate .nav-link:first').click();
})

function loadBoard() {
  var data = { 
          min_afp: $('.afp').slider("values")[0],
          max_afp: $('.afp').slider("values")[1],
          game: game
      }

  $('.team-board').html('<div class="board-loading ml-1 mt-5">Loading ...</div>');

  $.post( "/team-match-up", data, function( data ) {
    $('.team-board').html(data);
  });
}
