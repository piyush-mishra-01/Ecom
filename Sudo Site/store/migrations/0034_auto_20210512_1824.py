# Generated by Django 3.2 on 2021-05-12 12:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_auto_20210506_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchasedOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, default=None, max_length=500, null=True, unique=True)),
                ('date_ordered', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('cart_quantity', models.IntegerField(blank=True, default=0, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('payment_status', models.IntegerField(choices=[(1, 'SUCCESS'), (2, 'PENDING/FAILURE')], default=2)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=500, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=500, null=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=500, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.customer')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='razorpay_order_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='razorpay_payment_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='razorpay_signature',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='purchaseditems',
            name='order',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='order',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='date_ordered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name='Purchased',
        ),
        migrations.AddField(
            model_name='purchaseditems',
            name='purchased_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.purchasedorder'),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='purchased_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.purchasedorder'),
        ),
    ]
