// Updating robot risk parameters
const riskSaveButton = $("#riskSaveBtn")
const robotSelector = $("#robotSelector")
const dailyRiskLimit = $("#dailyLossLimit")

riskSaveButton.click(function () {
    $.ajax({
        type: "POST",
        url: "update_robot_risk/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            robot: robotSelector.val(),
            daily_risk: dailyRiskLimit.val()
            },
        success: function (response) {
            alert("Risk data is updated!")
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
            console.log(robot)
            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newBtn = document.createElement("button")

            newTd1.innerText = robot["robot"]
            newTd2.innerHTML = robot["daily_risk_perc"]
            newTd3.innerHTML = robot["daily_trade_limit"]
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
            newTd4.append(newBtn)

            robotRiskTableBody.append(newRow)
        }
        $('.robRiskAmendBtn').click(function () {
            console.log(this.parentElement.parentElement)
            $("#amendRobotRisk").modal();
        })
    })
}
