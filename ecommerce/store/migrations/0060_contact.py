# Generated by Django 3.2 on 2021-05-19 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0059_auto_20210517_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('mobile', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('message', models.TextField(null=True)),
            ],
        ),
    ]
