from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm
)
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("email",)
        # fields = UserCreationForm.Meta.fields + ("email", "role", "team")
    
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = UserChangeForm.Meta.fields