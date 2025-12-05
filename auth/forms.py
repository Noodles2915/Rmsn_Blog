from typing import Any
from django.forms import Form, CharField, EmailField, PasswordInput
from .models import User

class RegistrationForm(Form):
    username = CharField(label="用户名",max_length=150, required=True)
    email = EmailField(label="邮箱",required=True)
    password = CharField(label="密码",widget=PasswordInput, required=True)
    confirm_password = CharField(label="确认密码",widget=PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "两次输入的密码不匹配.")

        return cleaned_data
    


class LoginForm(Form):
    username = CharField(label="用户名",max_length=150, required=True)
    password = CharField(label="密码",widget=PasswordInput, required=True)
