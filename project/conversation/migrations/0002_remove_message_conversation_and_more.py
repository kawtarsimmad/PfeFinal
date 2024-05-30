# Generated by Django 5.0.6 on 2024-05-30 09:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='conversation',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='body',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='message',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='message',
            name='subject',
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name='Conversation',
        ),
    ]