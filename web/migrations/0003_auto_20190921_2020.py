# Generated by Django 2.2.5 on 2019-09-21 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='file',
            field=models.ImageField(max_length=255, upload_to='photo'),
        ),
    ]
