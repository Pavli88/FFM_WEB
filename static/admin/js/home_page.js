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
function chart(id, dataList, dateList, title, type, colorList) {
    let ctx = document.querySelector(id).getContext('2d');

    // Loading Charts
    let dataSet = {
        type: type,
        data: {
            labels: dateList,
            datasets: [{
                label: title,
                data: dataList,
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

// System message dashboard
const messageTable = $("#msgTableBody")
const loadMessagesBtn = $("#loadMsgsBtn")

loadMessagesBtn.on("click", loadMessages)
loadMessages()

function loadMessages(){
    $.get('get_messages/', function (data) {

        try {
            messageTable.empty()
        } catch (err) {
        }

        for (msg of data["message"]){
            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")

            newTd1.innerText = msg["msg_type"]
            newTd2.innerHTML = msg["msg"]
            newTd3.innerHTML = msg["date"]

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)

            messageTable.append(newRow)
        }
    })
}

// Loading data to robot panel

    // Variables

const robotSelector = $("#robotSelector")
const startDate = $("#startDate")
const endDate = $("#endDate")

    // Function on change calls main loader function
robotSelector.on("change", robotDataLoader)
startDate.on("change", robotDataLoader)
endDate.on("change", robotDataLoader)

    // Main loader function
function robotDataLoader(){
    console.log("Robot Data Loader")

    // Clearing chart canvases
    // let canvas1 = $('#dailyReturnChart')[0]; // or document.getElementById('canvas');
    // canvas1.width = canvas1.width;

    let robotBalanceData = getRobotBalance()

    // Loading daily robot returns
    BalanceDataChart(robotBalanceData, "#dailyReturnChart", "Daily Returns", "bar", "ret")

    // Robot balance chart
    BalanceDataChart(robotBalanceData, "#balanceChart", "Balance", "line", "close_balance")

    // Robot cash flow chart
    BalanceDataChart(robotBalanceData, "#cashFlowChart", "Cash Flow", "bar", "cash_flow")
}
// Load robot balance data function
function getRobotBalance() {
    let responseData = null
    $.ajax({
        url: 'get_robot_returns/',
        type: 'GET',
        data: {
            "robot": robotSelector.val(),
            "start_date": startDate.val(),
            "end_date": endDate.val()
        },
        async: false,
        success: function (data) {
            responseData = data;
        }
    });
    return responseData;
}

// Balance data chart creatior function
function BalanceDataChart(data, id, title, type, dataValue){
    let dates = []
    let values = []
    let colorList = []

    for (record of data["message"]){
        dates.push(record["date"])
        values.push(record[dataValue])

        if (record[dataValue] < 0){
            colorList.push("red")
        }else {
            colorList.push("green")
        }
    }
    chart(id, values, dates, title, type, colorList)
}







