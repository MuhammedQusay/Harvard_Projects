# Generated by Django 5.1.2 on 2025-05-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_auction_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='img',
            field=models.URLField(blank=True, default='https://www.svgrepo.com/show/340721/no-image.svg'),
        ),
    ]
