// Refreshing and loading robot stats to dashboard
const statRefreshButton = $('#loadRobotStats')
const statTableBody = $("#robotStatTable")
const demoRobotButton = $("#demoRobots")
const liveRobotButton = $("#liveRobots")

function loadStats(environment){
    $.get("load_robot_stats/", {'env': environment}, function (data) {
        console.log(data)
        console.log(data["robots"])

        let series = [{
            data: data["dtd"]
        }, {
            data: data["mtd"]
        }, {
            data: data["ytd"]
        }]

        let series2 = [{
            data: data["balance"]
        }]

        let series3 = [{
            data: data["pnls"]
        }]

        BarChart("#dtdPerfChart", series, data["robots"], 'bar', true, true)
        BarChart("#robotBalChart", series2, data["robots"], 'bar', true, true)
        BarChart("#pnlChart", series3, ["DTD", "MTD", "YTD"], 'bar', true, false)
    })
}

loadStats("live")

demoRobotButton.click(function (){
    loadStats("demo")
})

liveRobotButton.click(function (){
    loadStats("live")
})

function BarChart(id, series, category, type, stacked, horizontal){
    let options = {
          series: series,
          chart: {
          type: type,
              width: '100%',
              height: '100%',
              stacked: stacked,
        },
        plotOptions: {
          bar: {
            horizontal: horizontal,
            dataLabels: {
              position: 'top',
            },
          }
        },
        dataLabels: {
          enabled: true,
          offsetX: -6,
          style: {
            fontSize: '12px',
            colors: ['#fff']
          }
        },
        stroke: {
          show: true,
          width: 1,
          colors: ['#fff']
        },
        xaxis: {
          categories: category,
        },
        };
    let chart = new ApexCharts(document.querySelector(id), options);
    chart.render();
}








