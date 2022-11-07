# Generated by Django 3.2.13 on 2022-11-07 12:01

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_image_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]