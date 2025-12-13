from django import forms
from .models import Post, Comment
from markdownx.fields import MarkdownxFormField
import bleach

# 允许的 HTML 标签和属性，适用于将 Markdown 渲染为 HTML 后进行清理
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
    'h1', 'h2', 'h3', 'p', 'pre', 'img', 'br'
]
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height']
}


class PostForm(forms.ModelForm):
    content = MarkdownxFormField()

    class Meta:
        model = Post
        fields = ['title', 'content']

    def clean_content(self):
        raw = self.cleaned_data.get('content', '')
        # 返回原始 Markdown，由视图层在渲染为 HTML 后进行清理（以免移除 Markdown 语法）
        return raw.strip()


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        raw = self.cleaned_data.get('content', '')
        return raw.strip()
