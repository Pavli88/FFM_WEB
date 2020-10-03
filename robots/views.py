from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from robots.models import *
import os


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

        print("New robot creation request received.")

        # String fields
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

        string_parameter_dict = {"robot name": robot_name,
                                 "strategy name": strategy_name,
                                 "security": security,
                                 "broker": broker,
                                 "status": status,
                                 "environment": env,
                                 "time_fame:": time_frame,
                                 "account_number": account_number,
                                 "sl_policy": sl_policy,
                                 "precision": precision}

        # Float fields
        pyramiding_level = float(request.POST.get("pyramiding_level"))
        init_exp = float(request.POST.get("init_exp"))
        quantity = float(request.POST.get("quantity"))

        print("Robot parameters:", string_parameter_dict)

        # Checking if robot name exists in data base
        print("Checking if new record exists in database")
        try:
            data_exists = Robots.objects.get(name=robot_name).name
        except:
            data_exists = "does not exist"

        if data_exists == robot_name:
            print("Robot exists in data base.")
            return render(request, 'robots_app/create_robot.html', {"exist_robots": "exists"})

        # Inserting new robot data to database
        print("Inserting new record to database")
        robot = Robots(name=robot_name,
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
                       prec=precision)

        try:
            robot.save()
            print("New record was created with parameters:", string_parameter_dict)
            return render(request, 'robots_app/create_robot.html', {"exist_robots": "created"})
        except:
            print("Error occured while inserting data to database. "
                  "Either data type or server configuration is not correct.")
            return render(request, 'robots_app/create_robot.html',
                          {"exist_robots": "Incorrect data type was given in one of the fields!"})


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
    print("New request has arrived to delete existing robot from database")

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


