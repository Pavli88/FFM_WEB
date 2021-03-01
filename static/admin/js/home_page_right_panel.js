// Refreshing and loading robot stats to dashboard
const statRefreshButton = $('#loadRobotStats')
const statTableBody = $("#robotStatTable")
const demoRobotButton = $("#demoRobots")
const liveRobotButton = $("#liveRobots")
const dtdTotalPnl = $("#dtdTotalPnl")

function loadStats(environment){
    $.get("load_robot_stats/", {'env': environment}, function (data) {

        let series = [{
            data: data["ytd"]
        }]

        let series2 = [{data: data["ytd_pnl"]}]

        BarChart("#dtdPerfChart", [{data: data["dtd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#mtdPerfChart", [{data: data["mtd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#ytdPerfChart", [{data: data["ytd"]}], data["robots"], 'bar', false, true, ['#3498DB'])
        BarChart("#robotBalChart", [{data: data["balance"]}], data["robots"], 'bar', true, true, ['#3498DB'])

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

// get robot risk
function loadRobotRisk(){
    $.get("get_robot_risk/", function (data) {

        try {
            riskTableBody.empty()
        } catch (err) {
        }
        for (let risk of data["message"]){
            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newInput = document.createElement("input")
            let inputAttributes = {'type':'range', 'min':0.0, 'max':0.2, 'class':'slider', 'step':0.005}

            for (let key in inputAttributes){
                newInput.setAttribute(key, inputAttributes[key])
            }

            newInput.setAttribute('value', risk['daily_risk_perc'])

            newInput.addEventListener('input', updateRisk)

            newTd1.innerText = risk["robot"]
            newTd1.setAttribute('class', 'robotName')
            newTd1.setAttribute('value', risk["robot"])
            newTd3.innerText = risk["daily_risk_perc"]
            newTd3.setAttribute('class', 'riskValue')
            newTd2.append(newInput)
            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)

            riskTableBody.append(newRow)
        }

    })
}
let riskTableBody = $("#riskTableBody")
loadRobotRisk()

function updateRisk(){
    let row = this.parentElement.parentElement
    let riskValue = row.querySelector(".riskValue")
    let robotName = row.querySelector(".robotName")
    riskValue.innerHTML = this.value

    $.ajax({
        type: "POST",
        url: "update/risk_per_trade/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            robot: robotName.innerHTML,
            risk_per_trade: riskValue.innerHTML,
        },
        success: function (response) {

        },
        error: function (){
            alert("Risk was not updated due to an error!")
        }
    })
}

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








