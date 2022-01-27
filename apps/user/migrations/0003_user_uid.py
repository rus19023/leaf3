# Generated by Django 4.0.1 on 2022-01-24 20:17

from django.db import migrations

import shortuuid.django_fields


class Migration(migrations.Migration):

  dependencies = [
      ('user', '0002_user_created_user_updated'),
  ]

  operations = [
      migrations.AddField(
          model_name='user',
          name='uid',
          field=shortuuid.django_fields.ShortUUIDField(
              alphabet='23456789abcdefghijkmnopqrstuvwxyz',
              length=10,
              max_length=40,
              prefix='',
              unique=True),
      ),
  ]