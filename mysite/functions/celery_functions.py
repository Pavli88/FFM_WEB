from celery.app.control import Inspect
from mysite.celery import app

def is_worker_listening_on_queue(queue_name: str) -> bool:
    """
    Ellenőrzi, hogy van-e worker, amely figyeli a megadott queue-t.
    """
    try:
        inspector = Inspect(app=app)
        active_queues = inspector.active_queues()
        if not active_queues:
            return False

        for worker, queues in active_queues.items():
            for queue in queues:
                if queue.get('name') == queue_name:
                    return True
        return False
    except Exception:
        return False
