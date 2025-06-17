from portfolio.models import Portfolio

class PortfolioConfiguration:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        # self.settings = self._load_settings()