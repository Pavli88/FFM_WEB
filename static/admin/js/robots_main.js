// Robot process calculation panel
let calcButton = $("#calc_btn")
let process = $("#robot_proc_selector")
let robot = $("#robot")
let startDate = $("#start")

calcButton.click(robotProcess)
function robotProcess() {
    $.ajax({
        type: "POST",
        url: "process_hub/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            process: process.val(),
            robot: robot.val(),
            date: startDate.val(),
        },
        success: function (process, robot, date) {
            console.log("success")
        }
    })
}

// Loading robots to table
let loadButton = $("#load_robots")
let robotTable = $("#robot_table_body")
loadButton.click(loadRobots)

function loadRobots() {

    try{
        let allRobotRows = robotTable.empty()
    }
    catch (err) {
    }

    $.get("get_robots/", function (data) {
        for (let robot of data["securities"]){

            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newTd5 = document.createElement("td")
            let newTd6 = document.createElement("td")
            let newTd7 = document.createElement("td")
            let newTd8 = document.createElement("td")

            newRow.classList.add("robot_table_row")

            newTd1.innerText = robot["name"]
            newTd2.innerHTML = robot["strategy"]
            newTd3.innerHTML = robot["security"]
            newTd4.innerHTML = robot["time_frame"]
            newTd5.innerHTML = robot["broker"]
            newTd6.innerHTML = robot["env"]
            newTd7.innerHTML = robot["status"]
            newTd8.innerHTML = robot["account_number"]

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)
            newRow.append(newTd6)
            newRow.append(newTd7)
            newRow.append(newTd8)
            robotTable.append(newRow)
        }
    })
}

// New Robot
let newRobotButton = $("#create_robot_btn")
newRobotButton.click(newRobot)

function newRobot() {
    $.ajax({
        type: "POST",
        url: "new_robot/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            robot_name: robotNameField.val(),
            strategy: strategyNameField.val(),
            broker: broker.val(),
            env: envSelector.val(),
            security: secSelector.val(),
            account: accSelector.val(),

        },
        success: function (response){
            if (response["message"] === "alert"){
                alert("Robot exists in database!")
            }
            else{
                alert("New robot was created successfully!")
                $("#newRobot").modal('hide')
            }
        }
    })

}

// Trade process
let tradeButton = $("#trade_btn")
tradeButton.click(trade)

function trade() {

    $.ajax({
        type: "POST",
        url: "signals/trade/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            mydata: "silver_test_live buy 1 BUY",
        },
        success: function (mydata){
        }
    })
}

// New Robot form js
let robotNameField = $("#id_robot_name")
let strategyNameField = $("#id_strategy")
let accSelector = $("#id_account_number")
let secSelector = $("#id_security")
let broker = $("#id_broker")
let envSelector = $("#id_environment")

window.onload = function () {

    // Default broker data load from database
    loadBrokers()
}

function loadBrokers() {

    $.get('get_securities/', {'broker': 'oanda'},  function (data) {
        for (let sec of data["securities"]){
            let newOpt = document.createElement("option")
            newOpt.innerHTML = sec["instrument_name"]
            newOpt.setAttribute("id", sec["id"])
            secSelector.append(newOpt)
        }
    })

    $.get('get_accounts/', {'broker': 'oanda', 'env': 'live'},  function (data) {
        for (let acc of data["accounts"]){
            let newOpt = document.createElement("option")
            newOpt.innerHTML = acc["account_number"]
            newOpt.setAttribute("id", acc["id"])
            accSelector.append(newOpt)
        }
    })
}

// Switching environment for broker in new robot entry
envSelector.on("change", switchAccounts)

function switchAccounts() {

    accSelector.empty()

    $.get('get_accounts/', {'broker': broker.val(), 'env': envSelector.val()},  function (data) {
        for (let acc of data["accounts"]){
            let newOpt = document.createElement("option")
            newOpt.innerHTML = acc["account_number"]
            newOpt.setAttribute("id", acc["id"])
            accSelector.append(newOpt)
        }
    })
}
