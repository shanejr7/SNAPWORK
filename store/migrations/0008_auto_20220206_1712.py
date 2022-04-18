# Generated by Django 3.2.5 on 2022-02-06 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_user_quality_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='accepted_bid',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='highest_bid',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='quantity',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='stakeholder',
            name='quantity',
            field=models.IntegerField(null=True),
        ),
    ]