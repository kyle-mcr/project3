# Generated by Django 2.1.5 on 2020-06-18 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20200618_2149'),
    ]

    operations = [
        migrations.RenameField(
            model_name='extra',
            old_name='price',
            new_name='prize',
        ),
        migrations.RenameField(
            model_name='menuitem',
            old_name='price',
            new_name='prize',
        ),
    ]
