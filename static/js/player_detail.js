var options = {
  series: {
    lines: { show: true },
    points: {
      radius: 3,
      show: true
    }
  },
  grid: { hoverable: true, clickable: true },
  xaxis: {
    mode: "time"
  },
  legend: {
    noColumns: 0,
    labelBoxBorderColor: "#000000",
    position: "nw"
  },
};

var previousPoint = null,
    prevSeason = '';

$(document).ready(function () {
  $("#flot-placeholder").UseTooltip();

  loadGame();
});

$.fn.UseTooltip = function () {
  $(this).bind("plotclick", function (event, pos, item) {
    if (item) {
      if (previousPoint != item.dataIndex) {
        previousPoint = item.dataIndex;
        $("#tooltip").remove();

        var x = item.datapoint[0],
            y = item.datapoint[1],
            color = item.series.color,
            date = new Date(x);

        console.log(item.pageX, item.pageY);
        
        if (item.seriesIndex == 0) {
          showTooltip(item.pageX,
          item.pageY,
          color,
          `<strong>FPTS</strong><br>${date.getMonth()+1}/${date.getDate()}/${date.getYear()+1900}: <strong>${y}</strong>`);
        }
      }
    } else {
      $("#tooltip").remove();
      previousPoint = null;
    }
  });
};

function showTooltip(x, y, color, contents) {
  $('<div id="tooltip">' + contents + '</div>').css({
    position: 'absolute',
    display: 'none',
    top: y - 40,
    left: x - 120,
    border: '2px solid ' + color,
    padding: '5px 10px',
    'font-size': '12px',
    'border-radius': '5px',
    'background-color': '#fff',
    'font-family': 'Verdana, Arial, Helvetica, Tahoma, sans-serif',
    opacity: 0.9
  }).appendTo("body").fadeIn(200);
}

function setSeason(obj) {
  $('.filters .season').removeClass('active');
  $(obj).addClass('active');
  loadGame();
}

function loadGame() {
  var season = $('.filters .season.active').data('season'),
      data = { 
        pid: pid, 
        loc: $('.filters select.loc').val(), 
        opp: $('.filters select.opp').val(),
        season: season
      };

  // get all games for new season
  if (prevSeason != season) {
    data.loc = 'all';
    data.opp = '';
  }

  $.post( "/player-games", data, function( data ) {
    // table
    $('.games').html(data.game_table);
    if (prevSeason != season) {
      prevSeason = season;
      // opp select
      $('.filters select.opp').html(data.opps);
      // chart 
      var vdata = [];
      for (ii in data.chart) {
        vdata.push([new Date(data.chart[ii][0]), data.chart[ii][1]])
      }
      var dataset = [{ data: vdata }];
      $.plot($("#flot-placeholder"), dataset, options);
    }
  });
}

function getStats() {
  var selection = document.getSelection().toString(),
      sum = 0,
      avg = 0,
      num = 0;
  
  if (!selection.match(/[A-Z%//@]/g)) {
    cells = selection.split('\n');
    for (var i in cells) {
      if (cells[i]) {
        num++;
        if (cells[i] != '-') {
          sum += parseFloat(cells[i]);
        }        
      }
    }

    if (num > 0) {
      avg = Math.round(sum * 100 / num) / 100;
      $('#sum').html(Math.round(sum * 100) / 100);
      $('#avg').html(avg);
    } else {
      $('#sum').html('');
      $('#avg').html('');
    }
  }
}