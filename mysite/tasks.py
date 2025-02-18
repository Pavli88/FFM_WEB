from celery import shared_task
import time

@shared_task
def long_running_task():
    print("TEST TASK")
    time.sleep(10)  # Simulating a long-running task
    return "Task Complete!"