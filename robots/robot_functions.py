from robots.models import *


def get_robots(status=None):

    """
    Queries out all robots from database and passes it back to the html
    :param request:
    :return:
    """

    print("Fetching robot data from database")

    if status is not None:
        return Robots.objects.filter(status=status).values()
    else:
        return Robots.objects.filter().values()
