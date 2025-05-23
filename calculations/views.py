from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from mysite.my_functions.general_functions import *
from calculations.processes.performance.total_return import total_return_calc
from calculations.processes.valuation.valuation import calculate_holdings
from datetime import datetime, timedelta
from calculations.models import ProcessAudit, ProcessException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@csrf_exempt
def valuation(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        for portfolio_code in request_body['portfolios']:
            calculate_holdings(portfolio_code=portfolio_code, calc_date=request_body['start_date'])

        return JsonResponse([], safe=False)


@csrf_exempt
def total_return(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        response_list = []

        for portfolio_code in request_body['portfolios']:
            if request_body['calc_type'] == 'adhoc':
                print('adhoc')
                responses = total_return_calc(portfolio_code=portfolio_code,
                                              period='adhoc',
                                              end_date=request_body['end_date'],
                                              start_date=request_body['start_date']
                                              )
                for resp in responses:
                    response_list.append(resp)
            elif request_body['calc_type'] == 'multiple':
                print('multiple')
                for period in request_body['periods']:
                    responses = total_return_calc(portfolio_code=portfolio_code, period=period,
                                                  end_date=request_body['end_date'])
                    for resp in responses:
                        response_list.append(resp)
            else:
                print('multi dates')
                start_date = datetime.strptime(request_body['start_date'], "%Y-%m-%d")
                end_date = datetime.strptime(request_body['end_date'], "%Y-%m-%d")
                for period in request_body['periods']:
                    current_date = start_date
                    while current_date <= end_date:
                        responses = total_return_calc(portfolio_code=portfolio_code,
                                                      period=period,
                                                      end_date=current_date.strftime("%Y-%m-%d"))
                        for resp in responses:
                            response_list.append(resp)
                        current_date += timedelta(days=1)
                        #
        # # for portfolio_code in request_body['portfolios']:
        #     for period in request_body['periods']:
        #         responses = total_return_calc(portfolio_code=portfolio_code, period=period, end_date=request_body['date'])
        #         for resp in responses:
        #             response_list.append(resp)
        return JsonResponse(response_list, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def audit_records(request):
    try:
        portfolios = request.data.get('portfolios', [])
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not isinstance(portfolios, list) or not portfolios:
            return JsonResponse(
                {'error': 'A „portfolios” mező kötelező, és listát kell tartalmaznia.'},
                status=400
            )

        audits = ProcessAudit.objects.filter(portfolio__portfolio_code__in=portfolios)

        # Dátumszűrés
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                audits = audits.filter(valuation_date__gte=start_date)
            except ValueError:
                return JsonResponse(
                    {'error': 'Hibás start_date formátum. Használja a YYYY-MM-DD formátumot.'},
                    status=400
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                audits = audits.filter(valuation_date__lte=end_date)
            except ValueError:
                return JsonResponse(
                    {'error': 'Hibás end_date formátum. Használja a YYYY-MM-DD formátumot.'},
                    status=400
                )

        audits = audits.order_by('-run_at')

        results = [
            {
                'id': audit.id,
                'portfolio_code': audit.portfolio.portfolio_code,
                'portfolio_name': audit.portfolio.portfolio_name,
                'process': audit.process,
                'valuation_date': audit.valuation_date,
                'status': audit.status,
                'run_at': audit.run_at.strftime('%Y-%m-%d %H:%M:%S'),
                'message': audit.message or '',
            }
            for audit in audits
        ]

        return JsonResponse({'data': results}, status=200)

    except Exception as e:
        return JsonResponse(
            {'error': f'Server error: {str(e)}'},
            status=500
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_exceptions_by_audit_ids(request):
    try:
        audit_ids = request.data.get('ids', [])

        if not isinstance(audit_ids, list) or not all(isinstance(i, int) for i in audit_ids):
            return JsonResponse(
                {'error': '"ids" must be a list of integers.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exceptions = (
            ProcessException.objects
            .select_related('audit__portfolio')  # lekéri az audit és azon belül a portfolio kapcsolatot is
            .filter(audit_id__in=audit_ids)
            .order_by('-audit__run_at')
        )

        results = [
            {
                'id': exception.id,
                'audit_id': exception.audit_id,
                'portfolio_code': exception.audit.portfolio.portfolio_code if exception.audit.portfolio else None,
                'exception_type': exception.exception_type,
                'message': exception.message,
                'severity': exception.severity,
                'process_date': exception.process_date
            }
            for exception in exceptions
        ]

        return JsonResponse({'data': results}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse(
            {'error': f'Server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )