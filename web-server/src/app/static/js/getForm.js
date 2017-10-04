$(function() {
//  var chart = null;
  var submit_form = function() {
  
  var marketsArray = [];
  $("input[name='markets']:checked").each(function(){
                                                   marketsArray.push($(this).val());
                                                   });
  if(!marketsArray.length) {
  alert("You must check at least one checkbox.");
  $("#coinbase").prop("checked", true);
  return false;
  }
  
  $.getJSON($SCRIPT_ROOT + '/_get_book', {
            markets: marketsArray.toString(),
            currency: $('input[name="currency"]:checked').val(),
            num: $('#numTop').val()
            }, function(data) {

//            console.log(data);
            
            for (var I = 0; I < 2; I++)
            {
                key = Object.keys(data)[I];
                $('#'+key).empty();
                $('#'+key).append('<ol id="' + key + 'Col"></ol>');
                for (var J = 0;  J < data[key].length; J++)
                {
                    nameList = "<li>" + data[key][J] + "</li>";
                    $('#'+key+'Col').append(nameList);
                }
            }
            /*
            if (typeof chart === 'undefined') {
                chart = getBuysChart(data.Buys);
            } else {
                var keys = Object.keys(data.Buys);
                for (var I = 0; I < keys.length; I++)
                {
                    chart.series[I].setData(data.Buys[keys[I]],false,false);
                }
                chart.redraw();
           }*/
            });
  return false;
  };
  
  setInterval(submit_form, 1000);
  });
