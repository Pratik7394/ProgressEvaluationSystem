# Generated by Django 2.1.7 on 2019-04-26 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0002_auto_20190426_2135'),
    ]

    operations = [
        migrations.RenameField(
            model_name='research',
            old_name='Defence_Status',
            new_name='Defense_Status',
        ),
    ]
