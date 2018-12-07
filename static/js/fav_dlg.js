$('.fav-title').on('click', function() {
  $('.fav-wrapper').toggleClass('show-fav');
});

$('body').on('click','.fav',function() {
  var uid = $(this).data('uid');
  $.post( "/fav-player", { uid: uid }, function( data ) {
    $('*[data-uid="'+uid+'"]').toggleClass('done');
    $('.fav-body').html(data);
  });
});

$('body').on('click','.fav-remove',function() {
  var r = confirm("Are you sure to remove all favorites?");
  if (r == true) {
    $.post( "/fav-player", { uid: -1 }, function( data ) {
      location.reload();
    });
  }
});

$(document).ready(function () {
  var pos = $('.fav-title').position();
  $('.fav-wrapper').css({ 
    left: pos.left - 200,
    top: pos.top + 41
  });

  $.post( "/fav-player", {}, function( data ) {
    $('.fav-body').html(data);
  });
})
