from django.core.exceptions import ObjectDoesNotExist
from portfolio.models import Transaction, Portfolio, Instruments, Tickers

# Define transaction categories
CASH_TRANSACTIONS = {"Subscription", "Redemption", "Commission", "Financing"}


def create_transaction(transaction_data):
    """
    Reusable function to create a transaction in Django.
    This function can be used inside views, Celery tasks, or other Django processes.

    Args:
        transaction_data (dict): The transaction details in a dictionary.

    Returns:
        dict: A JSON-serializable response with status and message.
    """
    try:
        # Extract transaction_type
        transaction_type = transaction_data.get("transaction_type")

        # Identify transaction category
        if transaction_type in CASH_TRANSACTIONS:
            transaction_category = "Capital Transaction"
        else:
            if "parent_id" in transaction_data:
                transaction_category = "Child Transaction"
            else:
                transaction_category = "Parent Transaction"

        # Required fields check
        if transaction_category == "Capital Transaction":
            required_fields = ["portfolio_code", "portfolio_id", "security", "quantity", "trade_date",
                               "transaction_type"]
        elif transaction_category == "Parent Transaction":
            required_fields = ["portfolio_code", "portfolio_id", "security", "quantity", "price", "fx_rate",
                               "trade_date", "transaction_type", "broker"]
        elif transaction_category == "Child Transaction":
            required_fields = ["parent_id", "quantity", "price", "fx_rate", "trade_date"]

        missing_fields = [field for field in required_fields if field not in transaction_data]

        if missing_fields:
            return {"status": "error", "msg": f"Missing required fields: {', '.join(missing_fields)}",
                    "category": transaction_category}

        # Instrument and Portfolio Validation
        if transaction_category in ["Capital Transaction", "Parent Transaction"]:
            try:
                instrument = Instruments.objects.get(id=transaction_data['security'])
            except ObjectDoesNotExist:
                return {"status": "error", "msg": f"Instrument ID ({transaction_data['security']}) does not exist",
                        "category": transaction_category}

            try:
                portfolio = Portfolio.objects.get(id=transaction_data['portfolio_id'])
            except ObjectDoesNotExist:
                return {"status": "error", "msg": f"Portfolio ({transaction_data['portfolio_id']}) does not exist",
                        "category": transaction_category}

        # Handle Capital Transactions
        if transaction_category == "Capital Transaction":
            if instrument.group != 'Cash' and instrument.type != 'Cash':
                return {"status": "error", "msg": "Instrument is not a Cash/Cash security",
                        "category": "Capital Transaction"}

            if instrument.currency != portfolio.currency and not portfolio.multicurrency_allowed:
                return {"status": "error",
                        "msg": f"Multicurrency not allowed: Port ({portfolio.currency}) Inst ({instrument.currency})",
                        "category": "Capital Transaction"}

            Transaction(
                portfolio_code=transaction_data["portfolio_code"],
                portfolio_id=transaction_data['portfolio_id'],
                security_id=transaction_data['security'],
                quantity=transaction_data['quantity'],
                trade_date=transaction_data['trade_date'],
                currency=instrument.currency,
                transaction_type=transaction_type
            ).capital_transaction()

            return {"status": "success", "msg": f"New capital transaction ({transaction_type}) created",
                    "category": transaction_category}

        # Handle Parent Transactions
        if transaction_category == "Parent Transaction":
            optional_data = transaction_data.get("optional", {})

            broker_id = optional_data.get("broker_id")
            account_id = optional_data.get("account_id")
            is_active = optional_data.get("is_active")

            # Create transaction object with optional broker_id
            transaction = {
                "portfolio_code": transaction_data["portfolio_code"],
                "portfolio_id": transaction_data['portfolio_id'],
                "security_id": transaction_data['security'],
                "quantity": transaction_data['quantity'],
                "trade_date": transaction_data['trade_date'],
                "price": transaction_data['price'],
                "fx_rate": transaction_data['fx_rate'],
                "broker": transaction_data['broker'],
                "transaction_type": transaction_type,
                "currency": instrument.currency,
            }

            # Only add broker_id if it's present in the request
            if broker_id is not None:
                transaction["broker_id"] = broker_id
            if account_id is not None:
                transaction["account_id"] = account_id
            if is_active is not None:
                transaction["is_active"] = is_active

            # transaction = Transaction.objects.filter(
            #     portfolio_id=body_data['portfolio_id'],
            #     broker=self.broker,
            #     broker_id=self.broker_id)
            #
            # if transaction.exists():
            #     return {
            #         "status": "error",
            #         "msg": f"Transaction already exists for portfolio {self.portfolio_id} at broker {self.broker} with broker id {self.broker_id}",
            #         "category": "Parent Instrument Transaction",
            #         "transaction_type": self.transaction_type,
            #     }

            # Instrument Validation
            if instrument.group == 'Cash':
                return {
                    "status": "error",
                    "msg": f"Instrument ({transaction_data['security']}) is a Cash security",
                    "category": transaction_category,
                    "transaction_type": transaction_type,
                }

            # Ticker valudation if needed
            if instrument.group == "CFD":
                try:
                    ticker = Tickers.objects.get(
                        inst_code=transaction_data['security'],
                        source=transaction_data['broker'])
                except ObjectDoesNotExist:
                    return {
                        "status": "error",
                        "msg": f"Ticker for Inst ({transaction_data['security']}) does not exist at {transaction_data['broker']}",
                        "category": transaction_category,
                        "transaction_type": transaction_type,
                    }
                transaction["margin_rate"] = ticker.margin
            else:
                transaction["margin_rate"] = 1

            Transaction(**transaction).instrument_transaction()

            return {
                "status": "success",
                "msg": f"New parent transaction ({transaction_type}) is created",
                "category": transaction_category,
                "transaction_type": transaction_type
            }

        # Handle Child Transactions
        if transaction_category == "Child Transaction":
            optional_data = transaction_data.get("optional", {})
            broker_id = optional_data.get("broker_id")
            transaction = {
                "quantity": transaction_data['quantity'],
                "price": transaction_data['price'],
                "fx_rate": transaction_data['fx_rate'],
                "trade_date": transaction_data['trade_date'],
            }

            if broker_id is not None:
                transaction["broker_id"] = broker_id

            # Check if parent exists
            try:
                parent_transaction = Transaction.objects.get(id=transaction_data["parent_id"])
            except ObjectDoesNotExist:
                return {
                    "status": "error",
                    "msg": f"Parent transaction ({transaction_data['parent_id']}) does not exist",
                    "category": transaction_category,
                }

            if parent_transaction.transaction_type in CASH_TRANSACTIONS:
                return {
                    "status": "error",
                    "msg": f"Parent is capital transaction ({parent_transaction.transaction_type})",
                    "category": transaction_category,
                }

            Transaction(**transaction).instrument_transaction(parent=parent_transaction)

            return {
                "status": "success",
                "msg": f"New child transaction ({transaction_type}) is created",
                "category": transaction_category,
                "transaction_type": transaction_type
            }

    except Exception as e:
        return {"status": "error", "msg": f"An error occurred: {str(e)}"}


