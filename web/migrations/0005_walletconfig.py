# Generated by Django 2.2.5 on 2019-09-22 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20190922_0626'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('private_key', models.CharField(max_length=1024)),
                ('address', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
