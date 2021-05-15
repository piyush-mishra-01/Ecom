# Generated by Django 3.2 on 2021-05-15 12:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0045_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='date_ordered',
        ),
        migrations.RemoveField(
            model_name='product',
            name='available',
        ),
        migrations.RemoveField(
            model_name='purchaseditems',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='date_added',
        ),
        migrations.AddField(
            model_name='product',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='purchasedorder',
            name='date_ordered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]