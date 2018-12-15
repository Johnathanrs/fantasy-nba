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
  body = "Are you sure to remove all favorites?";
  $('#confirmModal .modal-body').html(body);
  $('#confirmModal').modal();
  $('#confirmModal .btn-ok').on('click', function () {
    $.post( "/fav-player", { uid: -1 }, function( data ) {
      location.reload();
    });
  })
});

function change_point (obj) {
  var pid = $(obj).data('id'),
      val = $(obj).val();
  $.post( "/update-point", { pid: pid, val: val }, function( data ) {})
}

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
