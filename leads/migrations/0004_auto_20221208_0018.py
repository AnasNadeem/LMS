# Generated by Django 3.2.15 on 2022-12-07 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0003_alter_leadattribute_attribute_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='leads.account'),
        ),
        migrations.AlterField(
            model_name='member',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together={('user', 'account')},
        ),
    ]
