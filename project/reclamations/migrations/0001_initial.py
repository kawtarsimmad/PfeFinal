# Generated by Django 5.0.4 on 2024-05-16 18:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reclamation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recl_type', models.CharField(choices=[('Payment', 'Payment Issue'), ('Posts', 'Posts Issue'), ('Other', 'Other Issue')], default='Other', max_length=100)),
                ('description', models.TextField(default='Your default description here', max_length=100)),
                ('status', models.CharField(default='Pending', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
