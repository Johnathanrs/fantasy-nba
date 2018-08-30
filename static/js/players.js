$(function() {
  // click first tab
  $('.nav-link:first').click();

  $('.btn-export').click(function() {
    var num_players = $('input[type="checkbox"]:checked').length;
    if (num_players == 0) {
      alert('Please choose players.');
      return false;
    }

    $('#dlg-export').modal();
  });

  $('.btn-calc').click(function() {
    var num_players = $('input[type="checkbox"]:checked').length;
    if (num_players == 0) {
      alert('Please choose players.');
      return
    }

    $('#div-result').html('<span class="font-weight-bold ml-5">Calculating ...</span>');
    $.post( "/gen-lineups", $('#frm-player').serialize(), function( data ) {
      $( "#div-result" ).html( data );
    });
  });

  $('.btn-clear').click(function() {
    $('#div-result').html('');
  });

  // filter players
  $("#search-player").on("keyup", function() {
    var value = $(this).val().toLowerCase();    
    $("#div-players tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
    
    $("#div-players thead tr").filter(function() {
      $(this).toggle(true);
    });
  });  
})

function pr_click(obj) {
  var checked = $(obj).parent().find('input').prop("checked");
  $(obj).parent().find('input').prop("checked", !checked);
}

function choose_all (obj) {
  $('input[type="checkbox"]').prop("checked", $(obj).prop('checked'));
}

function change_point (obj) {
  var pid = $(obj).data('id'),
      val = $(obj).val();
  $.post( "/update-point", { pid: pid, val: val }, function( data ) {})
}

function chooseDS (tab) {
  $.post( "/get-players", { ds: tab }, function( data ) {
    $( "#div-players" ).html( data );
  });
}  

function toggleLock(obj) {
  $(obj).toggleClass('fa-lock-open');
  $(obj).toggleClass('fa-lock');
}
