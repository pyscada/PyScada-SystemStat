# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device, Dictionary, DataSource
from . import PROTOCOL_ID

from django.forms.models import BaseInlineFormSet
from django.db import models
import datetime
from time import time
import logging

logger = logging.getLogger(__name__)



class TimestampDataSource(models.Model):
    datasource = models.OneToOneField(DataSource, on_delete=models.CASCADE)

    def __str__(self):
        return f"TimestampDataSource"

    def last_value(self, **kwargs):
        read_time = None
        read_value = None

        if "variable" in kwargs:
            variable = kwargs.pop("variable")

            if hasattr(variable, "systemstatvariable") and getattr(variable, "systemstatvariable") is not None:

                value = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
                try:
                    value += datetime.timedelta(
                        seconds=int(variable.systemstatvariable.parameter),
                        milliseconds=int(
                            (float(variable.systemstatvariable.parameter) - int(variable.systemstatvariable.parameter)) * 1000
                        ),
                    )
                except (ValueError, TypeError):
                    pass
                read_value = value.timestamp()
                read_time = datetime.datetime.now().timestamp()

        return [read_time, read_value]

    def read_multiple(self, **kwargs):

        output = {"timestamp": time() * 1000, "date_saved_max": time() * 1000}

        variable_ids = kwargs.pop("variable_ids") if "variable_ids" in kwargs else []
        variable_ids = self.datasource.datasource_check(
            variable_ids, items_as_id=True, ids_model=Variable
        )

        for v_id in variable_ids:
            try:
                v = Variable.objects.get(id=v_id)
                output[v_id] = self.last_value(variable=v)
            except Variable.DoesNotExist:
                logger.info(f"variable id {v_id} not found.")

        return output

    def write_multiple(self, **kwargs):
        pass

    def get_first_element_timestamp(self, **kwargs):
        pass

    def get_last_element_timestamp(self, **kwargs):
        pass


class SystemStatDevice(models.Model):
    system_stat_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    system_type_choices = (
        (0, "local"),
        (1, "remote (ssh)"),
    )
    system_type = models.PositiveSmallIntegerField(
        default=0,
        choices=system_type_choices,
        help_text="Choose the local system hosting PyScada"
        " or a remote system accessible by SSH",
    )
    # SSH
    host = models.CharField(default="test.com", max_length=200)
    port = models.PositiveSmallIntegerField(default=22)
    username = models.CharField(default="", blank=True, max_length=50)
    password = models.CharField(default="", blank=True, max_length=50)
    timeout = models.PositiveSmallIntegerField(default=5)

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.system_stat_device
        except:
            return None

    class FormSet(BaseInlineFormSet):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            form.fields["system_type"].widget.attrs = {
                # all hidden by default
                "--hideshow-fields": "host, port, username, password, timeout",
                # host, port, username, password visible when "1" (ssh) is selected
                "--show-on-1": "host, port, username, password, timeout",
            }


class SystemStatVariable(models.Model):
    system_stat_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    information_choices = (
        (0, "cpu_percent"),
        (1, "virtual_memory_usage_total"),
        (2, "virtual_memory_usage_available"),
        (3, "virtual_memory_usage_percent"),
        (4, "virtual_memory_usage_used"),
        (5, "virtual_memory_usage_free"),
        (6, "virtual_memory_usage_active"),
        (7, "virtual_memory_usage_inactive"),
        (8, "virtual_memory_usage_buffers"),
        (9, "virtual_memory_usage_cached"),
        (10, "swap_memory_total"),
        (11, "swap_memory_used"),
        (12, "swap_memory_free"),
        (13, "swap_memory_percent"),
        (14, "swap_memory_sin"),
        (15, "swap_memory_sout"),
        (17, "disk_usage_systemdisk_percent"),
        (18, "disk_usage_percent"),
        (19, "network_ip_address"),
        (20, "process_pid"),
        (21, "run command"),
        (22, "ssh availability"),
        (40, "file or directory last modification time"),
        (41, "is directory mounted"),
        (100, "APCUPSD Online Status (True/False)"),
        (101, "APCUPSD Line Voltage"),  # Volts
        (102, "APCUPSD Battery Voltage"),  # Volts
        (103, "APCUPSD Battery Charge in %"),  # %
        (104, "APCUPSD Battery Time Left in Minutes"),  # Minutes
        (105, "APCUPSD Load in %"),  # %
        (200, "List first X/last X/all items of a directory"),
        (201, "List first X/last X/all items of a ftp directory"),
        # Systemd services
        (250, "Systemd service is enabled"),
        (251, "Systemd service is active"),
        (300, "timestamp (UTC). Use parameter to set offset."),
    )
    information = models.PositiveSmallIntegerField(
        choices=information_choices,
        help_text="For item list create a VP for each path.",
    )
    parameter = models.CharField(
        default="",
        max_length=400,
        blank=True,
        null=True,
        help_text="For 'disk_usage' insert the path.<br>"
        "For 'timestamp' define an offset in seconds (positive means in the future)"
        "(accept a decimal number up to the millisecond).<br>"
        "For 'network_ip_address' specify the interface name.<br>"
        "For process_id : specify the process name<br>"
        "Examples for items list (local) : first 10 / last 5 / all.<br>"
        "Examples for items list (ftp) : "
        "127.0.0.1 first 10 / "
        "ftp.test.com last 5 / "
        "192.168.1.5 all.<br>",
    )

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.system_stat_variable.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        # List from https://www.freedesktop.org/software/systemd/man/systemctl.html
        # Result of systemctl is-enabled PROCESS_NAME
        systemd_service_enabled = {
            0: "enabled",
            1: "enabled-runtime",
            2: "linked",
            3: "linked-runtime",
            4: "alias",
            5: "masked",
            6: "masked-runtime",
            7: "static",
            8: "indirect",
            9: "disabled",
            10: "generated",
            11: "transient",
            12: "bad",
            13: "not-found",
        }
        de, created = Dictionary.objects.get_or_create(name="systemd_is_enabled")
        if created:
            for i in systemd_service_enabled:
                de.append(systemd_service_enabled[i], i, True)

        # List from https://www.freedesktop.org/software/systemd/man/systemctl.html
        # Result of systemctl is-active PROCESS_NAME
        systemd_service_states = {
            0: "inactive",
            1: "maintenance",
            2: "active",
            3: "deactivating",
            4: "failed",
            5: "error",
            6: "reloading",
            7: "not-found",  # added if not result from the command
        }
        da, created = Dictionary.objects.get_or_create(name="systemd_is_active")
        if created:
            for i in systemd_service_states:
                da.append(systemd_service_states[i], i, True)

        psutil_process_exceptions = {
            -1: "ZombieProcess",
            -2: "AccessDenied",
            -3: "NoSuchProcess",
        }
        dp, created = Dictionary.objects.get_or_create(name="psutil_process_exceptions")
        if created:
            for i in psutil_process_exceptions:
                dp.append(psutil_process_exceptions[i], i, True)

        if self.information == 250:
            self.system_stat_variable.dictionary = de
            self.system_stat_variable.save()
        elif self.information == 251:
            self.system_stat_variable.dictionary = da
            self.system_stat_variable.save()
        elif self.information == 20:
            self.system_stat_variable.dictionary = dp
            self.system_stat_variable.save()
        elif self.information == 300:
            from .apps import init_timestamp_datasource
            dsm, ds, ldse = init_timestamp_datasource()
            self.system_stat_variable.datasource = ds
            self.system_stat_variable.save()


class ExtendedSystemStatDevice(Device):
    class Meta:
        proxy = True
        verbose_name = "SystemStat Device"
        verbose_name_plural = "SystemStat Devices"


class ExtendedSystemStatVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = "SystemStat Variable"
        verbose_name_plural = "SystemStat Variables"