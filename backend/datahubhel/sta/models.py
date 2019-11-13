from django.db import models

from datahubhel.core.models import Datastream


class Observation(models.Model):
    id = models.TextField(db_column="id", primary_key=True)
    time = models.BigIntegerField(db_column="time", blank=True, null=True)
    datastream = models.ForeignKey(
        Datastream,
        db_column="datastream",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    value = models.TextField(db_column="value", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "observation"
