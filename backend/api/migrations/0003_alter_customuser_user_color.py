# Generated by Django 4.2.3 on 2024-06-11 00:39

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_customuser_user_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_color',
            field=colorfield.fields.ColorField(default='#E91E63', image_field=None, max_length=25, samples=[('#E91E63', 'Color1'), ('#3F51B5', 'Color2'), ('#009688', 'Color3'), ('#CDDC39', 'Color4')]),
        ),
    ]
