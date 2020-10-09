// Updating Securities on selected security type

let secTypeSelector = document.querySelector("#sec_select")
secTypeSelector.addEventListener("change", loadSecurities)

let price = $("#price")
let quantity = $("#qty")
let marketValue = $("#mv")
let availableCash = $("#available_cash")
let portfolio = $("#port_selector")
let security = $("#secs")
let tradePanel = $("#trade_panel")

// Adding All option to portfolio drop down menu
let newOpt = document.createElement("option")
newOpt.innerHTML = "All"
portfolio.append(newOpt)

price.keyup(calcMv)
quantity.keyup(calcMv)

// Allowing trading on portfolio and disable on All
portfolio.change(function () {
    if (portfolio.val() === "All"){
        tradePanel.hide()
    }else {
        tradePanel.show()
    }

})

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

// Executing portfolio trade
let tradeButton = $("#trade_btn")
tradeButton.click(trade)

function trade() {
    $.ajax({
        type: "POST",
        url: "trade_port/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            quantity: quantity.val(),
            price:price.val(),
            portfolio: portfolio.val(),
            security: security.val(),
            secType: secTypeSelector.value},
        success: function (quantity, price, portfolio, security, secType) {
            console.log("success")
        }
    })
}


