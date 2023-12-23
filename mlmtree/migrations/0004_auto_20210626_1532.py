# Generated by Django 3.2.3 on 2021-06-26 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlmtree', '0003_auto_20210621_2352'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='email',
            new_name='userid',
        ),
        migrations.AlterField(
            model_name='person',
            name='userid',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Benutzeridentifikation'),
        ),
    ]