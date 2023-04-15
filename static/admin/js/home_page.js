// GENERAL VARIABLES ***************************************************************************************************
let now = new Date()
let day = ("0" + now.getDate()).slice(-2)
let month = ("0" + (now.getMonth() + 1)).slice(-2)
let today = now.getFullYear()+"-"+(month)+"-"+(day)
let firstDay = now.getFullYear()+"-"+(month)+"-01"
$(".endDay").val(today)
$(".startDay").val(firstDay)

// GENERAL FUNCTION ****************************************************************************************************
// Function to get portfolio data
function getDataFromServer(url, requestData){
    let responseData = null
    $.ajax({
        url: url,
        type: 'GET',
        data: requestData, // {"port_type": portType}
        async: false,
        success: function (data) {
            responseData = data;
        }
    });
    return responseData;
}

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


// System message dashboard
const messageTable = $("#msgTableBody")
const loadMessagesBtn = $("#loadMsgsBtn")

loadMessagesBtn.on("click", loadMessages)
loadMessages()

function loadMessages(){
    let msgData = getDataFromServer('get_messages/', )
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

// ROBOT PANEL *********************************************************************************************************

// Variables
const robotSelector = $("#robotSelector")
const startDate = $("#startDate")
const endDate = $("#endDate")

// Function on change calls main loader function
robotSelector.on("change", robotDataLoader)
startDate.on("change", robotDataLoader)
endDate.on("change", robotDataLoader)

// Main ROBOT data loader function
function robotDataLoader(){

    // Clearing chart canvases
    // let canvas1 = $('#dailyReturnChart')[0]; // or document.getElementById('canvas');
    // canvas1.width = canvas1.width;
    let dataSet = {"robot": robotSelector.val(), "start_date": startDate.val(), "end_date": endDate.val()}
    let robotBalanceData = getData('get_robot_data/balance', dataSet)
    let robotTradesData = getData('get_robot_data/trade', dataSet)
    let cumRobotReturn = getData('get_robot_data/cumulative_return/', dataSet)
    let drawDown = getData('get_robot_data/drawdown/', dataSet)

    // Loading daily robot returns
    DataChart(robotBalanceData, "#dailyReturnChart", "Daily Returns", "bar", "ret")

    // Loading cumulative robot returns
    DataChart(cumRobotReturn, "#cumReturnChart", "Cumulative Returns", "line", "data")

    // Robot balance chart
    DataChart(robotBalanceData, "#balanceChart", "Balance", "line", "close_balance")

    // Robot cash flow chart
    DataChart(robotBalanceData, "#cashFlowChart", "Cash Flow", "bar", "cash_flow")

    // Robot trade pnl chart
    DataChart(robotTradesData, "#tradesChart", "Trades", "bar", "pnl")

    // Drawdown
    DataChart(drawDown, "#drawdownChart", "Drawdown", "bar", "data")
}

// ACCOUNT PANEL *******************************************************************************************************
const accountSelector = $("#accountSelector")
const startdateAcc = $("#startDateAcc")
const endDateAcc = $("#endDateAcc")

accountSelector.on("change", accountDataLoader)
startdateAcc.on("change", accountDataLoader)
endDateAcc.on("change", accountDataLoader)

// Main ACCOUNT data loader function
function accountDataLoader(){
    let dataSet = {"account": accountSelector.val(), "start_date": startdateAcc.val(), "end_date": endDateAcc.val()}
    let accountBalanceData = getData('accounts/get_account_data/balance', dataSet)
    console.log(accountBalanceData)
     // Account balance chart
    DataChart(accountBalanceData, "#balanceChartAcc", "Balance", "line", "value")

}

// Get data via url request from database
function getData(myUrl, dataSet){
    let responseData = null
    $.ajax({
        url: myUrl,
        type: 'GET',
        data: dataSet,
        async: false,
        success: function (data) {
            responseData = data;
        }
    });
    return responseData;
}

// Balance data chart creator function
function DataChart(data, id, title, type, dataValue){
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










