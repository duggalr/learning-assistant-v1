# Generated by Django 5.0.3 on 2024-04-28 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_assistant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playgroundcode',
            name='user_code_output',
            field=models.TextField(blank=True, null=True),
        ),
    ]
