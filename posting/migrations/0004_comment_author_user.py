# Generated manually for data migration
from django.db import migrations, models
import django.db.models.deletion


def migrate_comment_authors(apps, schema_editor):
    """将评论作者从字符串迁移到用户外键"""
    Comment = apps.get_model('posting', 'Comment')
    User = apps.get_model('users', 'User')
    
    # 删除所有现有评论（因为无法准确映射字符串到用户）
    Comment.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('posting', '0003_post_views_count'),
        ('users', '0003_user_bg'),
    ]

    operations = [
        # 添加新的 author_user 字段（临时，允许为空）
        migrations.AddField(
            model_name='comment',
            name='author_user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comments_new',
                to='users.user'
            ),
        ),
        # 迁移数据
        migrations.RunPython(migrate_comment_authors, migrations.RunPython.noop),
        # 删除旧的 author 字段
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        # 重命名 author_user 为 author
        migrations.RenameField(
            model_name='comment',
            old_name='author_user',
            new_name='author',
        ),
        # 设置为不可为空
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comments',
                to='users.user'
            ),
        ),
    ]
