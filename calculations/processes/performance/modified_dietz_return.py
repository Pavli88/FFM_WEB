from datetime import datetime
import calendar

def modified_dietz_return(initial_value, final_value, cash_flows, cash_flow_dates, start_date, end_date):
    # If there is a cash flow on the start date, add it to the initial value
    for i, cf_date in enumerate(cash_flow_dates):
        if cf_date == start_date:
            # initial_value -= cash_flows[i]  # Adjust initial value
            cash_flows.pop(i)  # Remove the start date cash flow from further calculations
            cash_flow_dates.pop(i)
            break  # Only handle the first cash flow on the start date

    # Calculate the number of days in the period
    T = (end_date - start_date).days
    print(T)
    # Calculate weighted cash flows
    weighted_cash_flows = 0
    total_cash_flow = 0
    for cf, cf_date in zip(cash_flows, cash_flow_dates):
        days_invested = (end_date - cf_date).days + 1  # Treat all other cash flows normally
        weight = days_invested / T
        weighted_cash_flows += cf * weight
        total_cash_flow += cf

    # Weight for DTD calculation
    if T == 1:
        weighted_cash_flows = 0

    # Calculate Modified Dietz return
    numerator = final_value - initial_value - total_cash_flow
    denominator = initial_value + weighted_cash_flows

    # Return the result as a percentage
    return numerator / denominator


# # Example usage
# initial_value = 370 # Initial portfolio value
# final_value = 268.74  # Final portfolio value
# cash_flows = [370, 50]  # Cash inflows/outflows (positive is inflow, negative is outflow)
# cash_flow_dates = [datetime(2024, 9, 10), datetime(2024, 9, 15)]  # Dates of cash flows
# start_date = datetime(2024, 9, 10)  # Start date of the period
# end_date = datetime(2024, 10, 16)  # End date of the period
#
# # Calculate the return
# return_value = modified_dietz_return(initial_value, final_value, cash_flows, cash_flow_dates, start_date, end_date)
# print(return_value)
# # Print the result as a percentage
# print(f"Modified Dietz Return: {return_value * 100:.2f}%")

# from datetime import datetime
# from dateutil.relativedelta import relativedelta


# def one_month_earlier(input_date):
#     # Ensure the input_date is a datetime object
#     if isinstance(input_date, str):
#         input_date = datetime.strptime(input_date, '%Y-%m-%d')  # Adjust format as needed
#
#     # Calculate the date one month earlier
#     new_date = input_date - relativedelta(months=1)
#
#     return new_date
#
#
# def month_end_dates(month, month_range, year=None):
#     if year is None:
#         year = datetime.now().year
#
#     if month < 1 or month > 12:
#         raise ValueError("Month must be between 1 and 12.")
#
#     last_day_of_month = calendar.monthrange(year, month)[1]
#     end_date_of_month = datetime(year, month, last_day_of_month)
#
#     if month == 1:
#         previous_month_end_date = datetime(year - 1, 12, 31)
#     else:
#         last_day_of_previous_month = calendar.monthrange(year, month - 1)[1]
#         previous_month_end_date = datetime(year, month - month_range, last_day_of_previous_month)
#
#     return end_date_of_month, previous_month_end_date
#
# month_input = 10  # October
# year_input = 2024  # You can specify a year or leave it as None for the current year
# current_month_end, previous_month_end = month_end_dates(month_input, year_input)
#
# print("End Date of Current Month:", current_month_end.strftime('%Y-%m-%d'))
# print("End Date of Previous Month:", previous_month_end.strftime('%Y-%m-%d'))