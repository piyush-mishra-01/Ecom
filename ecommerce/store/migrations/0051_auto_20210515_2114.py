# Generated by Django 3.0.14 on 2021-05-15 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0050_auto_20210515_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='detail',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='specs',
            field=models.TextField(null=True),
        ),
    ]
