from datetime import datetime
import time
import random

from demoapp.models import LongRunningModel


def task_create_long_running_model(data: str, requested_on: datetime) -> LongRunningModel:
    # simulate long running task
    time.sleep(random.randint(10, 60))

    model = LongRunningModel()
    model.data = data
    model.requested_on = requested_on
    model.save()
    return model
