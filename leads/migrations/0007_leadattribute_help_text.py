# Generated by Django 3.2.15 on 2023-01-04 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0006_alter_member_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadattribute',
            name='help_text',
            field=models.TextField(blank=True),
        ),
    ]
