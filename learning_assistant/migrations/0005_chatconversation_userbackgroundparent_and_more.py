# Generated by Django 5.0.3 on 2024-04-05 14:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_assistant', '0004_usergeneraltutorparent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_anon_user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('question', models.CharField(max_length=3000)),
                ('question_prompt', models.TextField()),
                ('response', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_auth_obj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_assistant.useroauth')),
            ],
        ),
        migrations.CreateModel(
            name='UserBackgroundParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_anon_user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('final_response', models.TextField(blank=True, null=True)),
                ('user_auth_obj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_assistant.useroauth')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserBackgroundConversation',
            fields=[
                ('chatconversation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='learning_assistant.chatconversation')),
                ('chat_parent_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_assistant.userbackgroundparent')),
            ],
            bases=('learning_assistant.chatconversation',),
        ),
    ]