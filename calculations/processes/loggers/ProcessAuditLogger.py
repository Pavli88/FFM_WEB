from calculations.models import ProcessAudit, ProcessException
from django.utils.timezone import now

class ProcessAuditLogger:
    def __init__(self, process_name, portfolio, valuation_date, trigger_type="Manual"):
        self.audit_entry, _ = ProcessAudit.objects.update_or_create(
            portfolio=portfolio,
            process=process_name,
            valuation_date=valuation_date,
            defaults={
                'status': 'Started',
                'run_at': now(),
                'trigger_type': trigger_type,
                'message': '',
            }
        )
        self.audit_entry.exceptions.all().delete()

    def complete(self, status, message, exception_list):
        self.audit_entry.status = status
        self.audit_entry.message = message
        self.audit_entry.save()

        exceptions = [
            ProcessException(
                audit=self.audit_entry,
                exception_type=e['exception'],
                message=e['comment'],
                process_date=e['date']
            )
            for e in exception_list
        ]
        if exceptions:
            ProcessException.objects.bulk_create(exceptions)