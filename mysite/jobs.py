from robots.processes.robot_processes import *
from mysite.my_functions.general_functions import *


def robot_balance_calculation():
    print("-----------------------------")
    print("ROBOT BALANCE CALCULATION JOB")
    print("-----------------------------")
    print("Loading robots from database")

    robots = pd.DataFrame(list(Robots.objects.filter().values()))

    print(robots)
    print("")
    print("Calculating balances")

    for robot in robots["name"]:
        bal_calc_msg = balance_calc(robot=robot, calc_date=str(get_today()))
        print(datetime.now(), bal_calc_msg)

    SystemMessages(msg_type="Robot Balance Calculation",
                   msg="Robot balance calculation job run successfully for all robots at " + str(datetime.now())).save()
