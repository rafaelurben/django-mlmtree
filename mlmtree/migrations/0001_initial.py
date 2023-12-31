# Generated by Django 3.2.3 on 2021-06-14 21:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='Name')),
                ('email', models.EmailField(blank=True, default='', max_length=25, verbose_name='E-Mail')),
                ('info', models.TextField(blank=True, default='', verbose_name='Info')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='mlmtree.person', verbose_name='Sponsor')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'Personen',
            },
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Titel')),
                ('description', models.TextField(verbose_name='Beschreibung')),
                ('top', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mlmtree.person')),
            ],
            options={
                'verbose_name': 'Baum',
                'verbose_name_plural': 'Bäume',
            },
        ),
        migrations.AddField(
            model_name='person',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='people', to='mlmtree.tree', verbose_name='Baum'),
        ),
        migrations.AddField(
            model_name='person',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mlmtree_identities', to=settings.AUTH_USER_MODEL, verbose_name='Benutzer'),
        ),
    ]
