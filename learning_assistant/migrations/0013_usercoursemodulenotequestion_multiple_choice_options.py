# Generated by Django 5.0.3 on 2024-04-08 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_assistant', '0012_usercoursemodulenotequestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoursemodulenotequestion',
            name='multiple_choice_options',
            field=models.TextField(blank=True, null=True),
        ),
    ]
