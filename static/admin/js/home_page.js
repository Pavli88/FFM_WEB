

function getRobotChartData() {
    alert("button clicked")
}

// Charting function
function chart(id, dataSet) {
    let ctx = document.querySelector(id).getContext('2d');
    let chart = new Chart(ctx, dataSet)
}

// Switching between account and its robot data
let accountSelector = document.querySelector('#account_selector')
accountSelector.addEventListener("change", switchAccount)

// Function switch between account
function switchAccount() {
    $.ajax({
        type: "POST",
        url: "switch_account/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), data: accountSelector.value},
        success: function (data) {
            let env = document.querySelector('#env')
            let broker = document.querySelector('#broker')
            let robots = document.querySelector('#robot_selector')

            // Amending main account labels
            // env.innerHTML = data["account data"][0]["env"]
            // broker.innerHTML = data["account data"][0]["broker_name"]

            let allRobotOptions = robots.querySelectorAll('.robot_option')
            allRobotOptions.forEach(n => n.remove())

            // Loading robots
            for (let robot of data["robots"]){
                let newOption = document.createElement("option")
                newOption.innerHTML = robot["name"]
                newOption.classList.add("robot_option")
                robots.appendChild(newOption)
            }

            // Building up robot table header
            try {
                let activeRobotTableCols = Object.keys(data["robots"][0])
                let arTableHead = document.querySelector("#a_r_header")

                for (let i = 0; i < activeRobotTableCols.length; i++){
                    let newTh = document.createElement("th")
                    newTh.innerHTML = activeRobotTableCols[i]
                    arTableHead.appendChild(newTh)
                }
            // Updating robots table
                let arTableBody = document.querySelector("#a_r_body")

                let allBodyRows = arTableBody.querySelectorAll('.body_row')
                allBodyRows.forEach(n => n.remove())

                for (i = 0; i < data["robots"].length; i++){
                    let newTr = document.createElement("tr")
                    newTr.classList.add("body_row")

                    for (let record in data["robots"][i]){
                        let newTd = document.createElement("td")
                        newTd.innerHTML = data["robots"][i][record]
                        newTr.appendChild(newTd)

                    }

                    arTableBody.appendChild(newTr)
                }
            }
            catch (err) {
                let allBodyRows = arTableBody.querySelectorAll('.body_row')
                allBodyRows.forEach(n => n.remove())
                console.log("No robot for this account")
            }

        }
    })
}

// Fetching robot related chart data from back end

// Loading Charts
let data_set = {
    type: 'bar',
    data: {
        labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
        datasets: [{
            label: '# of Votes',
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
}

chart("#bar_chart_2", data_set)


    // type = 'bar',
    // labels = "{{robot_perf.robot_label|safe}}",
    // label = 'P&L by Robots',
    // bgColor = "{{ robot_perf.color|safe }}",
    // borderColor = '#19393D', data = "{{ robot_perf.robot_pnl }}"

