
function Charting(id, data) {
    let ctx = document.getElementById(id).getContext('2d');
    let chart = new Chart(ctx, data);
}

let chartButton = document.querySelector("#get_chart")
chartButton.addEventListener("click",loadChartData)

function loadChartData() {
    let portfolio = document.querySelector("#port_selector").value

    let sentData = {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), portfolio: portfolio, chartname: "pie"}

    // Submitting request to backend
    $.ajax({
        type: "POST",
        url: "load_chart/",
        data: sentData,
        success: function (data) {

            // Here comes the execution if ajax is succesfull
            console.log(data)
            let data1 = {
                // The type of chart we want to create
                type: 'pie',

                // The data for our dataset
                data: {
                    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
                    datasets: [{
                        label: 'My First dataset',

                        data: data["account data"]
                    }]
                },

                // Configuration options go here
                options: {}
            }
            Charting('pie_chart', data1)
        }
    })
}



