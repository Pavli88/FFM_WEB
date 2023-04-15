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
            risk_per_trade: $("#riskPerTrade").val(),
            pyramiding_level: $("#pyramidingLevel").val(),
            quantity_type: $("#quantityType").val(),
            quantity: $("#quantity").val()
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
            let newTd6 = document.createElement("td")
            let newTd7 = document.createElement("td")
            let newTd8 = document.createElement("td")
            let newBtn = document.createElement("button")

            newTd1.innerText = robot["robot"]
            newTd2.innerHTML = robot["daily_risk_perc"]
            newTd3.innerHTML = robot["daily_trade_limit"]
            newTd4.innerHTML = robot["risk_per_trade"]
            newTd5.innerHTML = robot["pyramiding_level"]
            newTd6.innerHTML = robot["quantity_type"]
            newTd7.innerHTML = robot["quantity"]
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
            newRow.append(newTd6)
            newRow.append(newTd7)
            newRow.append(newTd8)
            newTd8.append(newBtn)

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
