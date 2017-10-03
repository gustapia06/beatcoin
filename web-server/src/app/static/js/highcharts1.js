function getBuysChart(data,product){
    var Series = [];
    var keys = Object.keys(data);
    
    for (var I = 0; I < keys.length; I++)
    {
        var market = {'name': keys[I], 'data': data[keys[I]]};
        Series.push(market)
    }
    
  var myChart = Highcharts.chart('chartBuys', {
  chart: {
    type: 'areaspline',
    spacingBottom: 40
  },
  title: {
    text: 'Bids'
  },
  legend: {
    layout: 'horizontal',
    align: 'center',
    verticalAlign: 'bottom',
    x: 0,
    y: 30,
    floating: true,
    borderWidth: 1,
    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
  },
  xAxis: {
    title: {
      text: 'Price $USD'
    },
  },
  yAxis: {
    title: {
      text: 'Amount'
    }
  },
  tooltip: {
    headerFormat: '<span style="color:{point.color}; font-size: 13px">\u25CF {series.name}</span><br/>',
    pointFormat: '<b>{point.y:,.2f}</b> '+ product + ' <br/>at USD$<b>{point.x:,.2f}</b><br/>'
  },
  credits: {
    enabled: false
  },
  plotOptions: {
    areaspline: {
      fillOpacity: 0.5
    }
  },
  series: Series
});

return myChart;
};

//chart.spacingBottom

