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
robotSelector.on("change", loadRobotRisk)
loadRobotRisk()
function loadRobotRisk(){
    $.get('get_robot_risk/', {'robot': robotSelector.val()},  function (data) {
        dailyRiskLimit.val(data["message"][0]["daily_risk_perc"])
    })
}
