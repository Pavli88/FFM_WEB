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
window.onload = function () {
    loadBrokers()
    console.log("Page is loaded")
}

function loadBrokers() {
    let broker = $("#id_broker")
    console.log(broker)
}
