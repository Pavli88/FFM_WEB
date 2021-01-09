// Refreshing and loading robot stats to dashboard
const statRefreshButton = $('#loadRobotStats')
const statTableBody = $("#robotStatTable")
const demoRobotButton = $("#demoRobots")
const liveRobotButton = $("#liveRobots")

function loadStats(environment){
    $.get("load_robot_stats/", {'env': environment}, function (data) {

        let allStats = document.querySelectorAll(".statRow")
        allStats.forEach(k => k.remove())

        for (let robot of data["robots"]){
            let newRow = document.createElement("tr")
            newRow.classList.add("statRow")

            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newTd5 = document.createElement("td")
            let newTd6 = document.createElement("td")
            let newTd7 = document.createElement("td")

            newTd1.innerText = robot["robot"]
            newTd2.innerHTML = robot["security"]
            newTd3.innerHTML = robot["env"]
            newTd4.innerHTML = robot["balance"]
            newTd5.innerHTML = robot["dtd"]
            newTd6.innerText = robot["mtd"]
            newTd7.innerText = robot["ytd"]

            if (parseFloat(robot["dtd"]) > 0.0){
                newTd5.style.color = "green"
            }
            else {
                newTd5.style.color = "red"
            }

            if (parseFloat(robot["mtd"]) > 0.0){
                newTd6.style.color = "green"
            }
            else {
                newTd6.style.color = "red"
            }

            if (parseFloat(robot["ytd"]) > 0.0){
                newTd7.style.color = "green"
            }
            else {
                newTd7.style.color = "red"
            }

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)
            newRow.append(newTd6)
            newRow.append(newTd7)

            statTableBody.append(newRow)
        }
    })
}

loadStats("live")

demoRobotButton.click(function (){
    loadStats("demo")
})

liveRobotButton.click(function (){
    loadStats("live")
})

// System message dashboard
const messageTable = $("#msgTableBody")
const loadMessagesBtn = $("#loadMsgsBtn")

loadMessagesBtn.on("click", loadMessages)
loadMessages()

function loadMessages(){
    $.get('get_messages/', function (data) {

        try {
            messageTable.empty()
        } catch (err) {
        }

        for (msg of data["message"]){
            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")

            newTd1.innerText = msg["msg_type"]
            newTd2.innerHTML = msg["msg"]
            newTd3.innerHTML = msg["date"]

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)

            messageTable.append(newRow)
        }
    })
}
