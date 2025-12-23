# Generated migration for adding theme field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='theme',
            field=models.CharField(
                choices=[('light', '日间模式'), ('dark', '夜间模式'), ('auto', '自动')],
                default='auto',
                max_length=10
            ),
        ),
    ]
