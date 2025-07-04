# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from . import __app_name__

import logging

logger = logging.getLogger(__name__)


class PyScadaSystemstatConfig(AppConfig):
    name = "pyscada.systemstat"
    verbose_name = _("PyScada System Statistics")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyscada.systemstat.signals


    def pyscada_app_init(self):
        logger.debug(f"{__app_name__} init app")

        init_timestamp_datasource()

def init_timestamp_datasource():
    dsm = ds = ldse = None

    try:
        from pyscada.models import DataSourceModel, DataSource
        from .models import TimestampDataSource

        dsm, _ = DataSourceModel.objects.update_or_create(
            inline_model_name="TimestampDataSource",
            defaults={
                "name": "Timestamp data source",
                "can_add": False,
                "can_change": False,
                "can_select": True,
            },
        )

        if DataSource.objects.filter(datasource_model=dsm).count():
            ds = DataSource.objects.filter(datasource_model=dsm).first()
        else:
            ds, _ = DataSource.objects.get_or_create(datasource_model=dsm)

        ldse, _ = TimestampDataSource.objects.get_or_create(datasource=ds)

    except ProgrammingError:
        pass
    except OperationalError:
        pass

    return dsm, ds, ldse