import pandas as pd
from datetime import datetime, date
from calculations.processes.loggers.ProcessAuditLogger import ProcessAuditLogger
from .context import ValuationContext
from .engine import ValuationEngine

def portfolio_valuation(portfolio_code, calc_date=date.today(), manual_request=False):
    pd.set_option('display.width', 200)

    calc_date = datetime.strptime(str(calc_date), '%Y-%m-%d').date()
    context = ValuationContext(portfolio_code=portfolio_code, request_date=calc_date)

    print('')
    print('REQUEST START DATE', calc_date)
    print("CALC RANGE:", context.calc_date, date.today(), context.start_date_type)

    if context.skip_processing:
        process_audit_logger = ProcessAuditLogger(process_name='Valuation', portfolio=context.portfolio_data, valuation_date=calc_date)
        process_audit_logger.complete(status='Error', message='Not funded portfolio', exception_list=context.send_responses())
    else:
        engine = ValuationEngine(context)
        engine.run()