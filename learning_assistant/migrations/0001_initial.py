# Generated by Django 5.0.3 on 2024-04-14 18:01

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('acc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatConversation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=3000)),
                ('question_prompt', models.TextField()),
                ('response', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acc.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='PlaygroundCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code_unique_name', models.CharField(max_length=2000)),
                ('user_code', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acc.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='UserGeneralTutorParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_anon_user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acc.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='UserGeneralTutorConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_anon_user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('question', models.CharField(max_length=3000)),
                ('question_prompt', models.TextField()),
                ('response', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chat_parent_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_assistant.usergeneraltutorparent')),
            ],
        ),
        migrations.CreateModel(
            name='PlaygroundConversation',
            fields=[
                ('chatconversation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='learning_assistant.chatconversation')),
                ('code_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_assistant.playgroundcode')),
            ],
            bases=('learning_assistant.chatconversation',),
        ),
    ]
