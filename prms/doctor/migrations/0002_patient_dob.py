# Generated by Django 5.1.2 on 2024-10-13 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='dob',
            field=models.DateField(default="2000-01-01"),
            preserve_default=False,
        ),
    ]
