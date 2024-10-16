import numpy as np


# Function to calculate drawdowns and maximum drawdown
def calculate_drawdowns(nav_values):
    """
    Calculate the drawdowns and maximum drawdown based on NAV values.

    Parameters:
    nav_values (list or np.array): List or array of NAV values over time.

    Returns:
    drawdowns (np.array): Array of drawdowns at each time point.
    max_drawdown (float): The maximum drawdown over the period.
    """
    # Convert nav_values to a numpy array for easier calculations
    nav_values = np.array(nav_values)

    # Calculate the running maximum (peak NAV up to each point in time)
    peak_nav = np.maximum.accumulate(nav_values)

    # Calculate drawdowns at each time point
    drawdowns = (nav_values - peak_nav) / peak_nav

    # Calculate the maximum drawdown
    max_drawdown = drawdowns.min()

    return drawdowns, max_drawdown
