from django.db import models


# Create your models here.
class LongRunningModel(models.Model):
    """Model definition for LongRunningModel."""

    data = models.CharField(max_length=255)
    requested_on = models.DateTimeField(editable=False)
    created_on = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        """Meta definition for LongRunningModel."""

        verbose_name = "LongRunningModel"
        verbose_name_plural = "LongRunningModels"
