// Updating Securities on selected security type

let secTypeSelector = document.querySelector("#sec_select")
secTypeSelector.addEventListener("change", loadSecurities)

let price = $("#price")
let quantity = $("#qty")
let marketValue = $("#mv")
let availableCash = $("#available_cash")

price.keyup(calcMv)
quantity.keyup(calcMv)

// Calculates market value of the trade
function calcMv() {
    let mv = quantity.val()*price.val()
    marketValue.html(mv)

    if (mv > Number(availableCash.html())){
        alert("Market value is greater than available cash in the portfolio!")
        price.val(1)
    }
}

// Loading securities for the selected security type
function loadSecurities() {
    $.ajax({
        type: "POST",
        url: "sec_types/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), data: secTypeSelector.value},
        success: function (data) {

            let securities = document.querySelector('#secs')
            let allSecurities = securities.querySelectorAll('.securities')

            allSecurities.forEach(k => k.remove())

            for (let sec of data["securities"]){
                console.log(sec)
                let opt = document.createElement("option")
                opt.innerHTML = sec["instrument_name"]
                opt.classList.add("securities")
                securities.appendChild(opt)
            }

            if (secTypeSelector.value === "Robot"){
                console.log("price")
                $("#price").val(1)
            }
        }
    })

}


