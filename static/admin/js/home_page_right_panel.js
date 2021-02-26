// Refreshing and loading robot stats to dashboard
const statRefreshButton = $('#loadRobotStats')
const statTableBody = $("#robotStatTable")
const demoRobotButton = $("#demoRobots")
const liveRobotButton = $("#liveRobots")
const dtdTotalPnl = $("#dtdTotalPnl")

function loadStats(environment){
    $.get("load_robot_stats/", {'env': environment}, function (data) {
        console.log(data)
        console.log(data["robots"])

        let series = [{
            data: data["ytd"]
        }]

        let series2 = [{data: data["ytd_pnl"]}]

        BarChart("#dtdPerfChart", [{data: data["dtd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#mtdPerfChart", [{data: data["mtd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#ytdPerfChart", [{data: data["ytd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#robotBalChart", [{data: data["balance"]}], data["robots"], 'bar', true, true, ['#3498DB'])

        console.log(data["pnls"][0])
        dtdTotalPnl.val(data["pnls"][0])
    })
}

loadStats("live")

demoRobotButton.click(function (){
    loadStats("demo")
})

liveRobotButton.click(function (){
    loadStats("live")
})

function BarChart(id, series, category, type, stacked, horizontal, colors){
    let options = {
        series: series,
        colors: colors,
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
            position: 'top',
            style: {
                fontSize: '10px',
                colors: ['#17202A']
            }
        },
        stroke: {
            show: true,
            width: 1,
            colors: ['#fff']
        },
        legend: {
            show: false
        },
        xaxis: {
            categories: category,
            axisTicks:{
                show:false
            },
            labels: {
                style: {
                    fontSize: '8px'
                }
            }

        },
        yaxis: {
            labels: {
                style: {
                    fontSize: '8px'
                }
            }
        }
    };
    let chart = new ApexCharts(document.querySelector(id), options);
    chart.render();
}








