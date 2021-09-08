// Loading accounts
const accountsTable = $("#accountTableBody")

loadAccounts()

function loadAccounts() {

    try{
        accountsTable.empty()
    }
    catch (err) {
    }

    $.get("load_accounts/", function (data) {
        for (let account of data["accounts"]){

            let newRow = document.createElement("tr")
            let newTd1 = document.createElement("td")
            let newTd2 = document.createElement("td")
            let newTd3 = document.createElement("td")
            let newTd4 = document.createElement("td")
            let newTd5 = document.createElement("td")

            newTd1.innerText = account["id"]
            newTd2.innerHTML = account["broker_name"]
            newTd3.innerHTML = account["account_number"]
            newTd4.innerHTML = account["access_token"]
            newTd5.innerHTML = account["env"]

            newRow.append(newTd1)
            newRow.append(newTd2)
            newRow.append(newTd3)
            newRow.append(newTd4)
            newRow.append(newTd5)

            accountsTable.append(newRow)
        }

    })
}

// New account creation
const accountCreateBtn = $("#accountCreateBtn")
const brokerName = $("#brokerName")
const accNumber = $("#accNumber")
const env = $("#env")
const token = $("#token")

accountCreateBtn.on("click", createNewAccount)

function createNewAccount() {
    $.ajax({
        type: "POST",
        url: "create_account/",
        data: {
            csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),
            broker_name: brokerName.val(),
            account_number: accNumber.val(),
            env: env.val(),
            token: token.val(),
        },
        success: function (response) {
            if (response === "exists") {
                alert("Account exists in database!")
            } else {
                alert("New account was created successfully!")
                $("#newAccount").modal('hide')
            }
            loadAccounts()
        }
    })
}