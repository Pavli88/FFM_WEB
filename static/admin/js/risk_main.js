// Updating robot risk parameters
const riskSaveButton = $("#updateDailyRiskBtn")

riskSaveButton.click(function () {

    console.log(this)
    $.ajax({
        type: "POST",
        url: "update_robot_risk/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            robot: $("#robotNameRisk").val(),
            daily_risk: $("#dailyRobotRisk").val(),
            daily_nmb_trades: $("#dailyNmbTrades").val(),
            risk_per_trade: $("#riskPerTrade").val()
            },
        success: function (response) {
            alert("Risk data is updated!")
            loadRobotRisk()
        }
    })
})

// Loading robot risk data on selection change
const robotRiskTableBody = $("#robotRiskTableBody")
loadRobotRisk()

function loadRobotRisk() {
    $.get('get_robot_risk/', function (data) {

        try {
            robotRiskTableBody.empty()
        } catch (err) {

        }
        for (let robot of data["message"]){

            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newTd5 = document.createElement("td")
            let newBtn = document.createElement("button")

            newTd1.innerText = robot["robot"]
            newTd2.innerHTML = robot["daily_risk_perc"]
            newTd3.innerHTML = robot["daily_trade_limit"]
            newTd4.innerHTML = robot["risk_per_trade"]
            newBtn.innerText = "Update"

            newBtn.classList.add("robRiskAmendBtn")
            newBtn.classList.add("btn")
            newBtn.classList.add("btn-outline-dark")
            newTd1.classList.add("robotName")
            newTd2.classList.add("dailyRisk")
            newTd3.classList.add("dailyTrades")

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)
            newTd5.append(newBtn)

            robotRiskTableBody.append(newRow)
        }
        $('.robRiskAmendBtn').click(function () {
            let robotName = this.parentElement.parentElement.querySelector(".robotName").innerHTML
            console.log(robotName)
            $("#robotNameRisk").val(robotName)
            $("#amendRobotRisk").modal();
        })
    })
}
