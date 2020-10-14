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
            trdSignal: {'robot_name': 'silver_h1', 'trade_side': 'buy', 'quantity': '2', 'action': 'BUY'},
        },
        success: function (trdSignal) {
            console.log("success")
        }
    })
}