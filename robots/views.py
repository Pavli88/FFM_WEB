from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from robots.models import *
from portfolio.models import *


# Main site for robot configuration
def robots_main(request):

    robots = Robots.objects.filter().values('name')
    robot_list = []
    for robot in robots:
        robot_list.append(robot["name"])

    print("Robot list:", robot_list)

    return render(request, 'robots_app/create_robot.html', {"robot_list": robot_list})


def create_robot(request):

    """
    This function creates new robot entry in the data base
    :param request:
    :return:
    """

    if request.method == "POST":

        print("==================")
        print("NEW ROBOT CREATION")
        print("==================")

        robot_name = request.POST.get("robot_name")
        strategy_name = request.POST.get("strategy_name")
        security = request.POST.get("security")
        broker = request.POST.get("broker")
        status = request.POST.get("status")
        env = request.POST.get("env")
        time_frame = request.POST.get("time_frame")
        account_number = request.POST.get("account_number")
        sl_policy = request.POST.get("sl_policy")
        precision = request.POST.get("precision")
        pyramiding_level = float(request.POST.get("pyramiding_level"))
        init_exp = float(request.POST.get("init_exp"))
        quantity = float(request.POST.get("quantity"))

        try:
            Robots(name=robot_name,
                   strategy=strategy_name,
                   security=security,
                   broker=broker,
                   status=status,
                   pyramiding_level=pyramiding_level,
                   in_exp=init_exp,
                   env=env,
                   quantity=quantity,
                   time_frame=time_frame,
                   account_number=account_number,
                   sl_policy=sl_policy,
                   prec=precision).save()

            print("Inserting new robot to database")

            Balance(robot_name=robot_name,
                    daily_pnl=0.0,
                    daily_cash_flow=0.0).save()

            print("Setting up initial balance to 0")

            Instruments(instrument_name=robot_name,
                        instrument_type="Robot",
                        source=broker).save()

            print("Saving down robot to instruments table")

        except:
            print("Robot exists in database")
            return render(request, 'robots_app/create_robot.html', {"robot_exists": "yes"})

        return redirect('robots main')


def get_all_robots(request):

    """
    Queries out all robots from database and passes it back to the html
    :param request:
    :return:
    """

    print("Request received to load all robot data on Robots page.")
    print("Loading robot data")

    robots = Robots.objects.filter().values()

    print("ROBOTS:")
    print(robots)

    # Create code to give the data back in json
    if len(robots) == 0:
        return render(request, 'robots_app/create_robot.html')
    else:
        return render(request, 'robots_app/create_robot.html', {"robots": robots})


def delete_robot(request):

    """
    Deletes existing robot from database
    :param request:
    :return:
    """

    print("")
    print("============")
    print("DELETE ROBOT")
    print("============")

    if request.method == "POST":

        message = request.body
        message = str(message.decode("utf-8"))

        robot_id = request.POST.get("robot_id")

        print("Robot ID:", robot_id)
        print("Deleting from database...")

        Robots.objects.filter(id=robot_id).delete()

        print("Record has been deleted")

    return render(request, 'robots_app/create_robot.html', {"robots": Robots.objects.filter().values()})


def amend_robot(request):

    if request.method == "POST":

        """
        Function to amend existing robot data in the database.
        """
        message = request.body
        message = str(message.decode("utf-8"))

        # Gets data from html table
        robot_name = request.POST.get("robot_name")
        env = request.POST.get("env")
        status = request.POST.get("status")
        pyramiding_level = request.POST.get("pyramiding_level")
        init_exp = request.POST.get("init_exp")
        quantity = request.POST.get("quantity")
        account_number = request.POST.get("account_number")
        precision = request.POST.get("precision")

        print("Request received to amend robot record for", robot_name)
        print("New Robot Parameters:")
        print("Robot Name:", robot_name)
        print("Environment:", env)
        print("Status:", status)
        print("P Level:", pyramiding_level)
        print("Initial Exp:", init_exp)
        print("Quantity:", quantity)
        print("Account Number:", account_number)
        print("Precision:", precision)

        # Retrieves back amended robot info and refreshes table
        robot = Robots.objects.get(name=robot_name)
        robot.quantity = quantity
        robot.env = env
        robot.status = status
        robot.pyramiding_level = pyramiding_level
        robot.init_exp = init_exp
        robot.quantity = quantity
        robot.account_number = account_number
        robot.prec = precision
        robot.save()
        print("Amended parameters were saved to database.")

        return render(request, 'robots_app/create_robot.html', {"robots": Robots.objects.filter().values()})

