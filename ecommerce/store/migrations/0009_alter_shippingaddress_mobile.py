# Generated by Django 3.2 on 2021-04-22 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_shippingaddress_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='mobile',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
