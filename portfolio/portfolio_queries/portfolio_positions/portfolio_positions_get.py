from django.db import connection
from django.http import JsonResponse


def get_transactions_by_date_gte(request, date):
    if request.method == "GET":
        cursor = connection.cursor()
        query = """""".format()
        cursor.execute(query)
        row = cursor.fetchall()
        response = []
        id = 0
        for record in row:
            response.append({'id': id, 'name': record[0], 'value': record[1]})
            id = id + 1
        return JsonResponse(response, safe=False)