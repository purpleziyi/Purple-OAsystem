# Generated by Django 5.0.4 on 2024-05-04 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('absent', '0002_alter_absent_response_content'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='absent',
            options={'ordering': ('-create_time',)},
        ),
    ]
