# Generated by Django 2.2.5 on 2019-09-16 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_on_wallet', '0002_auto_20190914_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='salt',
            field=models.CharField(default='', max_length=30),
        ),
    ]
