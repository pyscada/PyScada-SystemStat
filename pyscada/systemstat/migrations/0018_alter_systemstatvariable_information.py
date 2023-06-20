# Generated by Django 4.2.1 on 2023-06-19 10:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("systemstat", "0017_add_device_protocol"),
    ]

    operations = [
        migrations.AlterField(
            model_name="systemstatvariable",
            name="information",
            field=models.PositiveSmallIntegerField(
                choices=[
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
                    (100, "APCUPSD Online Status (True/False)"),
                    (101, "APCUPSD Line Voltage"),
                    (102, "APCUPSD Battery Voltage"),
                    (103, "APCUPSD Battery Charge in %"),
                    (104, "APCUPSD Battery Time Left in Minutes"),
                    (105, "APCUPSD Load in %"),
                    (200, "List first X/last X/all items of a directory"),
                    (201, "List first X/last X/all items of a ftp directory"),
                    (250, "Systemd service is enabled"),
                    (251, "Systemd service is active"),
                    (300, "timestamp (UTC). Use parameter to set offset."),
                ],
                help_text="For item list create a VP for each path.",
            ),
        ),
    ]
