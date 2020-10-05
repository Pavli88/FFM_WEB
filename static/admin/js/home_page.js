let accountSelector = document.querySelector('#account_selector')
accountSelector.addEventListener("change", switchAccount)

function switchAccount() {
    $.ajax({
        type: "POST",
        url: "switch_account/",
        data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), data: accountSelector.value},
        success: function (data) {
            let accountNumber = document.querySelector('#acc_name')
            let env = document.querySelector('#env')
            let broker = document.querySelector('#broker')

            accountNumber.innerHTML = data["account data"][0]["account_number"]
            env.innerHTML = data["account data"][0]["env"]
            broker.innerHTML = data["account data"][0]["broker_name"]
            console.log(data["account data"][0]["account_number"])
        }
    })
}

