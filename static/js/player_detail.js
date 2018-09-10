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

$(document).ready(function () {
  $("#flot-placeholder").UseTooltip();

  loadGame(true);
});

var previousPoint = null, previousLabel = null;

$.fn.UseTooltip = function () {
  $(this).bind("plothover", function (event, pos, item) {
    if (item) {
      if ((previousLabel != item.series.label) || (previousPoint != item.dataIndex)) {
        previousPoint = item.dataIndex;
        previousLabel = item.series.label;
        $("#tooltip").remove();

        var x = item.datapoint[0];
        var y = item.datapoint[1];

        var color = item.series.color;
        var date = new Date(x);

        if (item.seriesIndex == 0) {
          showTooltip(item.pageX,
          item.pageY,
          color,
          `<strong>PTS</strong><br>${date.getMonth()+1}/${date.getDate()}/${date.getYear()+1900}: <strong>${y}</strong>`);
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
  loadGame(true);
}

var prevSeason = '';

function loadGame(updateOpp) {
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