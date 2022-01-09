# Generated by Django 3.2.4 on 2021-11-03 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imd', models.ImageField(upload_to='imge/')),
                ('detail', models.CharField(max_length=300)),
                ('link', models.CharField(max_length=300)),
            ],
        ),
    ]
