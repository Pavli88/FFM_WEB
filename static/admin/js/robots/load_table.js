// scroll down for ES6 features.

	// using regular methods.

function myFunct(){
        alert("hello")
    }

    function tableFromJson() {
		// the json data. (you can change the values for output.)
        var myBooks = [{'id': 1, 'name': 'test_1', 'strategy': 'test_strategy', 'security': 'EUR_USD', 'broker': 'oanda', 'status': 'active', 'env': '', 'pyramiding_level': 2.0, 'in_exp': 0.02, 'quantity': 0.0}, {'id': 2, 'name': 'test_2', 'strategy': 'strat_1', 'security': 'EUR_USD', 'broker': 'oanda', 'status': 'active', 'env': '', 'pyramiding_level': 3.0, 'in_exp': 0.03, 'quantity': 0.0}, {'id': 3, 'name': 'test_3', 'strategy': 'strat_3', 'security': 'EUR_JPY', 'broker': 'oanada', 'status': 'active', 'env': '', 'pyramiding_level': 3.0, 'in_exp': 0.05, 'quantity': 0.0}, {'id': 4, 'name': 'test_4', 'strategy': 'strat_4', 'security': 'EUR_GBP', 'broker': 'oanda', 'status': 'active', 'env': '', 'pyramiding_level': 4.0, 'in_exp': 0.09, 'quantity': 0.0}, {'id': 5, 'name': 'test_6', 'strategy': 'strategy', 'security': 'EUR_USD', 'broker': 'oanada', 'status': 'active', 'env': 'live', 'pyramiding_level': 2.0, 'in_exp': 0.03, 'quantity': 1000.0}, {'id': 6, 'name': 'live_1', 'strategy': 'strat', 'security': 'SPX', 'broker': 'oanda', 'status': 'active', 'env': 'live', 'pyramiding_level': 1.0, 'in_exp': 0.02, 'quantity': 3000.0}, {'id': 7, 'name': 'test', 'strategy': 'rsr', 'security': 'sr', 'broker': 'hdfgh', 'status': 'active', 'env': 'live', 'pyramiding_level': 0.0, 'in_exp': 0.0, 'quantity': 0.0}, {'id': 8, 'name': 'test_9', 'strategy': 'ssd', 'security': 'EUR', 'broker': 'oanda', 'status': 'active', 'env': 'live', 'pyramiding_level': 0.0, 'in_exp': 0.0, 'quantity': 0.0}]

        // Extract value from table header.
        // ('Book ID', 'Book Name', 'Category' and 'Price')
        var col = [];
        for (var i = 0; i < myBooks.length; i++) {
            for (var key in myBooks[i]) {
                if (col.indexOf(key) === -1) {
                    col.push(key);
                }
            }
        }

        // Create a table.
        var table = document.createElement("table");

        // Create table header row using the extracted headers above.
        var tr = table.insertRow(-1);                   // table row.

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // table header.
            th.innerHTML = col[i];
            tr.appendChild(th);
        }

        // add json data to the table as rows.
        for (var i = 0; i < myBooks.length; i++) {

            tr = table.insertRow(-1);

            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = myBooks[i][col[j]];
            }
        }

        // Now, add the newly created table with json data, to a container.
        var divShowData = document.getElementById('showData');
        divShowData.innerHTML = "";
        divShowData.appendChild(table);