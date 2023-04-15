// Add new cashflow
const accSelector = $("#accSelector")
const accCf = $("#accCf")
const accCfBtn = $("#accCfBtn")

accCfBtn.on("click", accountCashFlow)

function accountCashFlow(){
    $.ajax({
        type: "POST",
        url: "new_cash_flow/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            account: accSelector.val(),
            cash_flow: accCf.val(),
        },
        success: function (response) {
            alert(response)
            accCf.val(0.0)
        }
    })
}