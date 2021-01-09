// Loading default parameters
// let now = new Date()
// let day = ("0" + now.getDate()).slice(-2)
// let month = ("0" + (now.getMonth() + 1)).slice(-2)
// let today = now.getFullYear()+"-"+(month)+"-"+(day)
// let firstDay = now.getFullYear()+"-"+(month)+"-01"
// $("#processStartDate").val(firstDay)
// $("#processEndDate").val(today)

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
            let newTd9 = document.createElement("td")

            let newBtn = document.createElement("button")
            newBtn.classList.add("closeBtn")
            newBtn.classList.add("btn")
            newBtn.classList.add("btn-outline-dark")
            newRow.classList.add("robot_table_row")

            newTd1.classList.add("robotName")

            newTd1.innerText = robot["name"]
            newTd2.innerHTML = robot["strategy"]
            newTd3.innerHTML = robot["security"]
            newTd4.innerHTML = robot["time_frame"]
            newTd5.innerHTML = robot["broker"]
            newTd6.innerHTML = robot["env"]
            newTd7.innerHTML = robot["status"]
            newTd8.innerHTML = robot["account_number"]
            newBtn.innerText = "Close"

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)
            newRow.append(newTd6)
            newRow.append(newTd7)
            newRow.append(newTd8)
            newRow.append(newTd9)
            newTd9.append(newBtn)
            robotTable.append(newRow)
        }
        // Deleting robot from database
        $('.closeBtn').click(function () {
            if (confirm("Do you want to delete this robot?")) {
                let currentRow = this.parentElement.parentElement
                let currentRobot = currentRow.getElementsByClassName("robotName")

                // Check if robot has balance
                $.ajax({
                    type: "POST",
                    url: "delete_robot/",
                    data: {
                        csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
                        robot_name: currentRobot[0].innerHTML,
                    },
                    success: function (response) {
                        alert("Robot was deleted!")
                    }
                })
                loadRobots()
            } else {
                console.log("Not Deleted")
            }
        })
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
