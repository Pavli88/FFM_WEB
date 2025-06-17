# Ez az osztály fog felelni magáért az al folyamatok kezeléséért és meghívásáért
from datetime import datetime, date
from datetime import timedelta
from calculations.processes.loggers.ProcessAuditLogger import ProcessAuditLogger
from calculations.processes.valuation.context import ValuationContext
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .calculator import AssetValuation, NavCalculation

def serialize_exceptions(exceptions):
    for e in exceptions:
        if isinstance(e.get("date"), date):
            e["date"] = e["date"].isoformat()
    return exceptions

"""
Ez az osztály felelős az értékelési folyamat vezérlésért mikor melyik folyamat fusson és mi után.
"""

class ValuationEngine:
    def __init__(self, context: ValuationContext):
        self.context = context

    def run(self, manual_request=False):
        channel_layer = get_channel_layer()
        current_iteration_date = self.context.calc_date
        while current_iteration_date <= date.today():

            # New Process Audit
            process_audit_logger = ProcessAuditLogger(process_name='Valuation',
                                                      portfolio=self.context.portfolio_data,
                                                      valuation_date=current_iteration_date)

            # --- VALUATION FUTTATÁSA ---
            # Ezt a részt ki kell szervezni a policy osztályba -------------------------------
            if self.context.portfolio_data.weekend_valuation is False and (
                    current_iteration_date.weekday() == 6 or current_iteration_date.weekday() == 5):
                print('---', current_iteration_date, current_iteration_date.strftime('%A'), 'Not calculate')
            else:
                if self.context.portfolio_data.weekend_valuation is False and current_iteration_date.weekday() == 0:
                    time_back = 3
                else:
                    time_back = 1

                self.context.previous_date = current_iteration_date - timedelta(days=time_back)
                self.context.calc_date = current_iteration_date

            # ------------------------------------------------------------------------------------
                if self.context.portfolio_data.portfolio_type == 'Portfolio Group' or self.context.portfolio_data.portfolio_type == 'Business':
                    NavCalculation(self.context).run()
                else:
                    AssetValuation(self.context).run()
                    NavCalculation(self.context).run()

            current_iteration_date = current_iteration_date + timedelta(days=1)

            # ----------------------------- End of process audit -----------------------------------------------------

            process_audit_logger.complete(status='Alert' if len(self.context.error_list) > 0 else 'Completed',
                                          message=f"{len(self.context.send_responses())} issues" if self.context.send_responses() else f"NAV: {self.context.total_nav} {self.context.base_currency}",
                                          exception_list=self.context.send_responses())

            # Sending Notification if this is a Dashboard request
            if manual_request == False and len(self.context.send_responses()) > 0:
                async_to_sync(channel_layer.group_send)(
                    f"user_{self.context.user_id}",
                    {
                        "type": "process.notification",
                        "payload": {
                            "process": 'valuation',
                            "message": "Valuation completed with exceptions.",
                            "exceptions": serialize_exceptions(self.context.send_responses())
                        }
                    }
                )