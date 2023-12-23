# Generated by Django 3.2.3 on 2021-06-21 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlmtree', '0002_alter_tree_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='E-Mail'),
        ),
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
    ]
