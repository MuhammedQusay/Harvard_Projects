# Generated by Django 5.1.2 on 2025-05-07 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_auction_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='img',
            field=models.ImageField(blank=True, default='default.png', upload_to=''),
        ),
    ]
