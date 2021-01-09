// Loading default parameters
let now = new Date()
let day = ("0" + now.getDate()).slice(-2)
let month = ("0" + (now.getMonth() + 1)).slice(-2)
let today = now.getFullYear()+"-"+(month)+"-"+(day)
let firstDay = now.getFullYear()+"-"+(month)+"-01"
$("#processStartDate").val(firstDay)
$("#processEndDate").val(today)

// Robot process calculation panel
let calcButton = $("#calc_btn")
let process = $("#robot_proc_selector")

let robot = $("#robot")
let startDate = $("#processStartDate")
let endDate = $("#processEndDate")
let calcLoadingDiv = $("#calcLoadingDiv")
let robotMessageTable = $("#robotTableMessageBody")

calcLoadingDiv.hide()
calcButton.click(robotProcess)

function robotProcess() {
    calcLoadingDiv.show()
    try {
        robotMessageTable.empty()
    } catch (err) {
    }
    $.ajax({
        type: "POST",
        url: "process_hub/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            process: process.val(),
            robot: robot.val(),
            date: startDate.val(),
            endDate: endDate.val(),
        },
        success: function (response) {

            for (let msg of response["message"]){
                let newMessagTr = document.createElement("tr")
                let newMessage = document.createElement("td")
                let icon = document.createElement("td")

                newMessagTr.classList.add("robot_table_row")
                newMessage.innerText = msg
                newMessagTr.append(icon)
                newMessagTr.append(newMessage)
                robotMessageTable.append(newMessagTr)

            }
            calcLoadingDiv.hide()
        }
    })
}