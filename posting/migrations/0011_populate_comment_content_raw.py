# Generated data migration to populate Comment.content_raw from existing content
from django.db import migrations


def forwards(apps, schema_editor):
    Comment = apps.get_model('posting', 'Comment')
    # Import locally to avoid app registry issues
    from django.utils.html import strip_tags

    qs = Comment.objects.all()
    for c in qs:
        try:
            # 如果已经有值则跳过
            if getattr(c, 'content_raw', None):
                continue
            # 将现有渲染后的 HTML 去标签后作为备用的 raw 文本
            c.content_raw = strip_tags(c.content or '')
            c.save(update_fields=['content_raw'])
        except Exception:
            # 容错：若单条出问题，记录为空并继续，避免迁移中断
            try:
                c.content_raw = ''
                c.save(update_fields=['content_raw'])
            except Exception:
                pass


def backwards(apps, schema_editor):
    Comment = apps.get_model('posting', 'Comment')
    qs = Comment.objects.all()
    for c in qs:
        try:
            c.content_raw = ''
            c.save(update_fields=['content_raw'])
        except Exception:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('posting', '0010_comment_content_raw'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
