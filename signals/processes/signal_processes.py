from robots.models import *


class TradeSignal:

    def __init__(self, strategy_name, security):
        self.strategy_name = strategy_name
        self.security = security
        self.robot_exist = ""
        self.robot = ""

    def get_robot(self):

        # Checking if robot exists in database
        self.robot_exist = Robots.objects.filter(strategy=self.strategy_name, security=self.security).exists()

        if self.robot_exist is True:
            print("Robot with", self.strategy_name, "exists in database:", self.robot_exist)
            self.robot = Robots.objects.get(strategy=self.strategy_name, security=self.security)
        else:
            print("Robot with", self.strategy_name, "does not exists in database:", self.robot_exist)
            self.robot = False

        return self.robot


