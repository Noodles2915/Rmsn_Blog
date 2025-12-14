from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posting', '0004_comment_author_user'),
    ]

    operations = [
        # 删除所有 posting 相关的表
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS posting_comment",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS posting_post_tags",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS posting_post",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS posting_tag",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
