# Generated by Django 4.2.5 on 2024-04-10 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounts',
            name='uid',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
    ]
