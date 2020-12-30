// Loading open trades
const openTradeTableBody = $('#openTradeTableBody')
LoadOpenTrades()

function LoadOpenTrades(){
    $.get("load_trades/", function (data) {
        for (let trade of data["trades"]){
            let newRow = document.createElement("tr")

            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newTd5 = document.createElement("td")
            let newTd6 = document.createElement("td")

            let newBtn = document.createElement("button")
            newBtn.classList.add("closeBtn")
            newTd6.classList.add("robot_row")
            newTd1.classList.add("id_row")
            newBtn.value = trade["broker_id"]

            newTd1.innerText = trade["id"]
            newTd6.innerText = trade["robot"]
            newTd2.innerHTML = trade["security"]
            newTd3.innerHTML = trade["quantity"]
            newTd4.innerHTML = trade["side"]
            newTd5.innerHTML = trade["broker_id"]
            newBtn.innerText = "Close"

            newRow.append(newTd1)
            newRow.append(newTd6)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)
            newRow.append(newBtn)

            openTradeTableBody.append(newRow)
            console.log(trade)
        }
        // This part is responsible for closing the open trade based on broker ID. It sends broker ID to back end
        $('.closeBtn').click(function () {
            let currentRow = this.parentElement
            let currentRobot = currentRow.getElementsByClassName("robot_row")
            let currentId = currentRow.getElementsByClassName("id_row")

            $.ajax({
                type: "POST",
                url: "close_trade/",
                data: {
                    csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
                    broker_id: this.value,
                    robot: currentRobot[0].innerHTML,
                    trd_id: currentId[0].innerHTML

                },
                success: function (response) {
                    console.log("Trade was closed!")
                }
            })
        })
    })
}
console.log("open")