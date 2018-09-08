var dataset = [{label: "PTS",data: rdata}];

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
  $.plot($("#flot-placeholder"), dataset, options);
  $("#flot-placeholder").UseTooltip();

  loadGame('all', '');

  $('.filters select').change(function () {
    loadGame($('.filters select.loc').val(), $('.filters select.opp').val());
  });
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
          `<strong>${item.series.label}</strong><br>${date.getMonth()+1}/${date.getDate()}/${date.getYear()+1900}: <strong>${y}</strong>`);
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

function loadGame(loc, opp) {
  var data = { pid: pid, loc: loc, opp: opp };

  $.post( "/player-games", data, function( data ) {
    $('.games').html(data);
  });
}