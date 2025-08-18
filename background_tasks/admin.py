import io
from django.contrib import admin
from .models import Task, Schedule, KV
import gzip
import pickle
# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin View for Task"""

    list_display = ("queue", "priority", "data")
    # list_filter = ("",)
    # raw_id_fields = ("",)
    # readonly_fields = ("",)
    # search_fields = ("",)
    # date_hierarchy = ""
    # ordering = ("",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Admin View for Schedule"""

    list_display = ("queue", "timestamp", "data")
    # list_filter = ("",)
    # raw_id_fields = ("",)
    # readonly_fields = ("",)
    # search_fields = ("",)
    # date_hierarchy = ""
    # ordering = ("",)


@admin.register(KV)
class KVAdmin(admin.ModelAdmin):
    """Admin View for KV"""

    list_display = ("key", "queue", "decoded_value", "is_result")
    list_filter = ["is_result"]

    @admin.display()
    def decoded_value(self, obj):
        value: bytes = obj.value
        # decompressed_value = gzip.decompress(io.BytesIO(value))
        deserialised_value = pickle.loads(value)

        return deserialised_value

    # list_filter = ("",)
    # raw_id_fields = ("",)
    # readonly_fields = ("",)
    # search_fields = ("",)
    # date_hierarchy = ""
    # ordering = ("",)
