from huey import Huey
from datetime import UTC
from huey.storage import BaseStorage, EmptyData
from django import db
from django.db import transaction


class DjangoOrmStorage(BaseStorage):
    blocking = False  # Does dequeue() block until ready, or should we poll?
    priority = True

    def __init__(self, name="huey", **storage_kwargs):
        self.name = name

    @property
    def task_qs(self):
        from background_tasks.models import Task

        return Task.objects.filter(queue=self.name)

    @property
    def schedule_qs(self):
        from background_tasks.models import Schedule

        return Schedule.objects.filter(queue=self.name)

    @property
    def kv_qs(self):
        from background_tasks.models import KV

        return KV.objects.filter(queue=self.name)

    def close(self):
        """
        Close or release any objects/handles used by storage layer.

        :returns: (optional) boolean indicating success
        """
        for conn_name in db.connections:
            conn = db.connections[conn_name]
            conn.close()

    def enqueue(self, data, priority=None):
        """
        Given an opaque chunk of data, add it to the queue.

        :param bytes data: Task data.
        :param float priority: Priority, higher priorities processed first.
        :return: No return value.

        Some storage may not implement support for priority. In that case, the
        storage may raise a NotImplementedError for non-None priority values.
        """
        self.task_qs.create(queue=self.name, data=data, priority=priority or 0.0)

    def dequeue(self):
        """
        Atomically remove data from the queue. If no data is available, no data
        is returned.

        :return: Opaque binary task data or None if queue is empty.
        """
        qs = self.task_qs.select_for_update(skip_locked=True).order_by("-priority")
        with transaction.atomic():
            task = qs.first()
            if task:
                task.delete()
                return task.data
            return None

    def queue_size(self):
        """
        Return the length of the queue.

        :return: Number of tasks.
        """
        return self.task_qs.count()

    def enqueued_items(self, limit=None):
        """
        Non-destructively read the given number of tasks from the queue. If no
        limit is specified, all tasks will be read.

        :param int limit: Restrict the number of tasks returned.
        :return: A list containing opaque binary task data.
        """
        qs = self.task_qs.order_by("-priority", "id")
        if limit is not None:
            qs = qs[:limit]
        tasks = [t.data for t in qs]
        return tasks

    def flush_queue(self):
        """
        Remove all data from the queue.

        :return: No return value.
        """
        self.task_qs.delete()

    def add_to_schedule(self, data, ts):
        """
        Add the given task data to the schedule, to be executed at the given
        timestamp.

        :param bytes data: Task data.
        :param datetime ts: Timestamp at which task should be executed.
        :return: No return value.
        """
        self.schedule_qs.create(
            queue=self.name,
            data=data,
            timestamp=ts.replace(tzinfo=UTC),
        )

    def read_schedule(self, ts):
        """
        Read all tasks from the schedule that should be executed at or before
        the given timestamp. Once read, the tasks are removed from the
        schedule.

        :param datetime ts: Timestamp
        :return: List containing task data for tasks which should be executed
                 at or before the given timestamp.
        """
        qs = self.schedule_qs.select_for_update(skip_locked=True).filter(timestamp__lte=ts.replace(tzinfo=UTC))
        with transaction.atomic():
            data = []
            for task in qs:
                data.append(task.data)
                task.delete()
            return data

    def schedule_size(self):
        """
        :return: The number of tasks currently in the schedule.
        """
        return self.schedule_qs.count()

    def scheduled_items(self, limit=None):
        """
        Non-destructively read the given number of tasks from the schedule.

        :param int limit: Restrict the number of tasks returned.
        :return: List of tasks that are in schedule, in order from soonest to
                 latest.
        """
        qs = self.schedule_qs.order_by("timestamp")
        if limit is not None:
            qs = qs[:limit]
        return [task.data for task in qs]

    def flush_schedule(self):
        """
        Delete all scheduled tasks.

        :return: No return value.
        """
        self.schedule_qs.delete()

    def put_data(self, key, value, is_result=False):
        """
        Store an arbitrary key/value pair.

        :param bytes key: lookup key
        :param bytes value: value
        :param bool is_result: indicate if we are storing a (volatile) task
            result versus metadata like a task revocation key or lock.
        :return: No return value.
        """
        self.kv_qs.update_or_create(
            queue=self.name,
            key=key,
            defaults={"value": value, "is_result": is_result},
        )

    def peek_data(self, key):
        """
        Non-destructively read the value at the given key, if it exists.

        :param bytes key: Key to read.
        :return: Associated value, if key exists, or ``EmptyData``.
        """
        kv = self.kv_qs.filter(key=key).first()
        if kv:
            return kv.value
        return EmptyData

    def pop_data(self, key):
        """
        Destructively read the value at the given key, if it exists.

        :param bytes key: Key to read.
        :return: Associated value, if key exists, or ``EmptyData``.
        """
        qs = self.kv_qs.select_for_update(skip_locked=True).filter(key=key)
        with transaction.atomic():
            kv = qs.first()
            if kv:
                kv.delete()
                return kv.value
            return EmptyData

    def delete_data(self, key):
        """
        Delete the value at the given key, if it exists.

        :param bytes key: Key to delete.
        :return: boolean success or failure.
        """
        return self.pop_data(key) is not EmptyData

    def has_data_for_key(self, key):
        """
        Return whether there is data for the given key.

        :return: Boolean value.
        """
        return self.kv_qs.filter(key=key).exists()

    def put_if_empty(self, key, value):
        """
        Atomically write data only if the key is not already set.

        :param bytes key: Key to check/set.
        :param bytes value: Arbitrary data.
        :return: Boolean whether key/value was set.
        """
        with transaction.atomic():
            if self.has_data_for_key(key):
                return False
            self.put_data(key, value)
            return True

    def result_store_size(self):
        """
        :return: Number of key/value pairs in the result store.
        """
        return self.kv_qs.count()

    def result_items(self):
        """
        Non-destructively read all the key/value pairs from the data-store.

        :return: Dictionary mapping all key/value pairs in the data-store.
        """
        data = {item.key: item.value for item in self.kv_qs}
        return data

    def flush_results(self):
        """
        Delete all key/value pairs from the data-store.

        :return: No return value.
        """
        self.kv_qs.delete()

    def flush_all(self):
        """
        Remove all persistent or semi-persistent data.

        :return: No return value.
        """
        self.flush_queue()
        self.flush_schedule()
        self.flush_results()


class DjangoOrmHuey(Huey):
    storage_class = DjangoOrmStorage
