# Generated by Django 4.2.6 on 2024-01-18 16:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='MyGroup',
        ),
        migrations.DeleteModel(
            name='MyPermission',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]