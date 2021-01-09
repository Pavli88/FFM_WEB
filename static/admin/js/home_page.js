// Loading default parameters
let now = new Date()
let day = ("0" + now.getDate()).slice(-2)
let month = ("0" + (now.getMonth() + 1)).slice(-2)
let today = now.getFullYear()+"-"+(month)+"-"+(day)
let firstDay = now.getFullYear()+"-"+(month)+"-01"
$(".endDay").val(today)
$(".startDay").val(firstDay)

// Loading all robot chart data
let robotBtn = $("#getChartBtn")
robotBtn.click(getRobotChartData)

function getRobotChartData() {
    $("#robotChartsDiv").show()
    let robot = $("#robot_selector").val()
    let startDate = $("#start").val()
    let endDate = $("#end").val()

    console.log(robot, startDate, endDate)
    $.get("robot_chart_data/", {"robot": robot, "start_date": startDate, "end_date": endDate}, function (response) {
        let realizedPnlList = [] // List for realized Pnl
        let dateList = []
        let closeBalList = []
        let colorList = []
        for (let balData of response["balance"]){
            console.log(balData)
            dateList.push(balData["date"])
            realizedPnlList.push(balData["realized_pnl"])
            closeBalList.push(balData["close_balance"])

            if (balData["realized_pnl"] > 0){
                colorList.push('#6A9300')
            }else{
                colorList.push('#FF4950')
            }
        }

        $("#robotStrategy").text(response["robot"][0]["strategy"])
        $("#robotInceptionDate").text(response["robot"][0]["inception_date"])
        $("#robotSecurity").text(response["robot"][0]["security"])
        $("#robotStatus").text(response["robot"][0]["status"])
        chart("#robotChart1", realizedPnlList, dateList, "Realized P&L", 'bar', colorList)
        chart("#robotChart2", closeBalList, dateList, "Closing Balance", 'line', '#6C845D')
    })
}

// Charting function
function chart(id, data, dates, title, type, colorList) {
    let ctx = document.querySelector(id).getContext('2d');
    console.log(data)
    // Loading Charts
    let dataSet = {
        type: type,
        data: {
            labels: dates,
            datasets: [{
                label: title,
                data: data,
                backgroundColor : colorList,

            }]
        },
        // options: {
        //     scales: {
        //         yAxes: [{
        //             ticks: {
        //                 // beginAtZero: true
        //             }
        //         }]
        //     }
        // }
    }

    let chart = new Chart(ctx, dataSet)
}

// Switching between account and its robot data
let accountSelector = document.querySelector('#account_selector')
accountSelector.addEventListener("change", switchAccount)

// Function switch between account
function switchAccount() {
    $.ajax({
        type: "POST",
        url: "switch_account/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), data: accountSelector.value},
        success: function (data) {
            let env = document.querySelector('#env')
            let broker = document.querySelector('#broker')
            let robots = document.querySelector('#robot_selector')

            // Amending main account labels
            // env.innerHTML = data["account data"][0]["env"]
            // broker.innerHTML = data["account data"][0]["broker_name"]

            let allRobotOptions = robots.querySelectorAll('.robot_option')
            allRobotOptions.forEach(n => n.remove())

            // Loading robots
            for (let robot of data["robots"]){
                let newOption = document.createElement("option")
                newOption.innerHTML = robot["name"]
                newOption.classList.add("robot_option")
                robots.appendChild(newOption)
            }

            // Building up robot table header
            try {
                let activeRobotTableCols = Object.keys(data["robots"][0])
                let arTableHead = document.querySelector("#a_r_header")

                for (let i = 0; i < activeRobotTableCols.length; i++){
                    let newTh = document.createElement("th")
                    newTh.innerHTML = activeRobotTableCols[i]
                    arTableHead.appendChild(newTh)
                }
            // Updating robots table
                let arTableBody = document.querySelector("#a_r_body")

                let allBodyRows = arTableBody.querySelectorAll('.body_row')
                allBodyRows.forEach(n => n.remove())

                for (i = 0; i < data["robots"].length; i++){
                    let newTr = document.createElement("tr")
                    newTr.classList.add("body_row")

                    for (let record in data["robots"][i]){
                        let newTd = document.createElement("td")
                        newTd.innerHTML = data["robots"][i][record]
                        newTr.appendChild(newTd)

                    }

                    arTableBody.appendChild(newTr)
                }
            }
            catch (err) {
                let allBodyRows = arTableBody.querySelectorAll('.body_row')
                allBodyRows.forEach(n => n.remove())
                console.log("No robot for this account")
            }

        }
    })
}

// Fetching robot related chart data from back end





