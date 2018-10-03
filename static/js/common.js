$('.fav-header').on('click', function() {
  $('.fa-window-maximize').toggleClass('d-none');
  $('.fa-window-minimize').toggleClass('d-none');
  $('.fav-wrapper').toggleClass('show-fav');
});

$('body').on('click','.fav',function() {
  var self = this;
  $.post( "/fav-player", { uid: $(this).data('uid') }, function( data ) {
    $(self).toggleClass('done');
    $('.fav-body').html(data);
  });
});

$(document).ready(function () {
  $.post( "/fav-player", {}, function( data ) {
    $('.fav-body').html(data);
  });  
})
