# Generated by Django 4.2.23 on 2025-06-11 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransaction',
            name='performed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff'),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item'),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='purchase_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.purchaseorder'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='ordered_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier'),
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.category'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.category'),
        ),
    ]
