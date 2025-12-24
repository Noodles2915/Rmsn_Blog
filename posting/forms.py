from django import forms
from .models import Post, Comment
import bleach

# 允许的 HTML 标签和属性，适用于将 Markdown 渲染为 HTML 后进行清理
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
    'h1', 'h2', 'h3', 'p', 'pre', 'img', 'br', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'hr'
]
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height']
}


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'id_content',
            'placeholder': '在此输入文章内容，支持 Markdown 格式',
            'rows': 10,
            'required': False  # 由 JavaScript 验证，避免浏览器原生验证问题
        }),
        required=False  # 由 JavaScript 验证
    )

    class Meta:
        model = Post
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'id': 'id_title',
                'placeholder': '请输入文章标题',
                'required': False  # 由 JavaScript 验证
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑时，从 content_raw 填充 content 字段
        if self.instance and self.instance.pk:
            self.fields['content'].initial = self.instance.content_raw
        # 移除 required 属性以避免浏览器验证问题
        for field in self.fields.values():
            if 'required' in field.widget.attrs:
                field.widget.attrs['required'] = False

    def clean(self):
        cleaned_data = super().clean()
        # 不在这里验证 content，因为它会由 JavaScript 和视图层处理
        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data.get('title', '') or ''
        title = title.strip()
        # 允许中文、字母、数字、空格及常见标点 - 防止特殊控制字符
        import re
        if title and not re.match(r'^[\w\u4e00-\u9fff\s\-_:,\.\(\)]+$', title):
            raise forms.ValidationError('标题包含不允许的字符（仅允许字母、数字、中文、空格及 - _ : , . () 等）')
        return title

    def clean_content(self):
        # 允许空值，由 JavaScript 验证
        return self.cleaned_data.get('content', '')



class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        raw = self.cleaned_data.get('content', '')
        return raw.strip()
