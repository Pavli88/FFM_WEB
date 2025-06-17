import pandas as pd
from portfolio.models import Portfolio, Nav
from .policy import PortfolioConfiguration

"""
A kontextus osztály betölt egy központi objektumba változókat amiket használnak később a további osztályok.
Ebben módosítanak és lekérhetnek változókat.

Ebben az osztályban kezelődnek a teljes futás során a hiba üzenetek
"""

class ValuationContext:
    def __init__(self, portfolio_code, request_date):

        # GENERAL
        self.portfolio_code = portfolio_code
        self.request_date = request_date
        self.calc_date = None
        self.previous_date = None
        self.portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.configuration = PortfolioConfiguration(self.portfolio_data)
        self.user_id = self.portfolio_data.user_id
        self.base_currency = self.portfolio_data.currency

        # MESSAGING
        self.response_list = []
        self.error_list = []
        self.skip_processing = False
        self.error_message = ""
        self.start_date_type = None

        # ASSET VALUATION
        self.fx_rates = None
        self.final_holding_table = pd.DataFrame({})

        # NAV
        self.subscriptions = 0.0
        self.redemptions = 0.0
        self.total_nav = 0.0

        # INITIAL PROCESSES
        self.validate_portfolio()

        # Start date beállítása ha a validálás sikeres
        if self.skip_processing == False:
            self.set_start_date()

    # VALIDATIONS
    def validate_portfolio(self):
        """
        Ellenőrzi az indulási dátumot és a funding státuszt.
        Beállítja a self.skip_processing és self.error_message attribútumokat.
        """
        self.skip_processing = False
        self.error_message = ""

        if self.portfolio_data.status == 'Not Funded' and self.portfolio_data.portfolio_type not in ['Portfolio Group',
                                                                                                     'Business']:
            self.add_error_message({
                'portfolio_code': self.portfolio_code,
                'date': self.request_date,
                'process': 'Valuation',
                'exception': 'Not Funded',
                'status': 'Error',
                'comment': 'Portfolio is not funded. Valuation is not possible'
            })
            self.skip_processing = True
            self.error_message = 'Portfolio is not funded'

    def set_start_date(self):
        if self.request_date < self.portfolio_data.inception_date and self.portfolio_data.portfolio_type != 'Portfolio Group':
            self.calc_date = self.portfolio_data.inception_date
            self.start_date_type = 'Inception'
            return

        latest_nav = Nav.objects.filter(portfolio_code=self.portfolio_code).order_by('-date').first()

        if latest_nav and latest_nav.date < self.request_date:
            self.calc_date = latest_nav.date
            self.start_date_type = 'Latest NAV Date'
        elif not latest_nav:
            self.calc_date = self.portfolio_data.inception_date
            self.start_date_type = 'No NAV, Inception'
        else:
            self.calc_date = self.request_date
            self.start_date_type = 'Request Date'

    def add_error_message(self, message):
        self.error_list.append(message)

    def send_responses(self):
        df = pd.DataFrame(self.error_list)
        df_unique = df.drop_duplicates()
        self.error_list = df_unique.to_dict('records')
        return self.error_list