from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        min_length=4,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名不能少于4位"
        },
        widget=forms.widgets.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "用户名",
                "aria-describedby": "basic-addon1",
            }
        )
    )
    password = forms.CharField(
        label="密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "密码",
            }
        )
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        min_length=4,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名不能少于4位"
        },
        widget=forms.widgets.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "用户名",
            }
        )
    )
    password = forms.CharField(
        label="密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "密码",
            }
        )
    )
    re_password = forms.CharField(
        label="确认密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "确认密码",
            }
        )
    )

    # phone = forms.CharField(
    #     label='手机号',
    #     error_messages={
    #         "required": "手机号不能为空",
    #     },
    #     validators=[RegexValidator(r'1[3-9]\d{9}', "手机号码格式不正确")],
    #     widget=forms.widgets.TextInput(
    #         attrs={"class": "form-control"}
    #     )
    # )

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("password")
        re_pwd = self.cleaned_data.get("re_password")
        if re_pwd and re_pwd == pwd:
            return self.cleaned_data
        else:
            self.add_error('re_password', "两次密码不一致")
            raise ValidationError("两次密码不一致")