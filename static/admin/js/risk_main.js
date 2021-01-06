// Updating robot risk parameters
const riskSaveButton = $("#riskSaveBtn")
const robotSelector = $("#robotSelector")
const dailyRiskLimit = $("#dailyLossLimit")

riskSaveButton.click(function () {
    console.log(robotSelector.val())
    console.log(dailyRiskLimit.val())
    $.ajax({
        type: "POST",
        url: "update_robot_risk/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            robot: robotSelector.val(),
            daily_risk: dailyRiskLimit.val()
            },
        success: function (response) {
            console.log(response["message"])
        }
    })
})
