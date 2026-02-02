from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils import formats
from django.db.models import Q
from clients.models import *
from nodes.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from croppie.fields import CroppieField


class ProfileForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': _('Display name')}))
#    picture = forms.ImageField(widget=AvatarPictureWidget(attrs={'id': 'avatarinput'}), required=False, label= _('Change'))
    picture = CroppieField(required=False, label= _('Change'),
        options={
            'enableExif': True,
            'viewport':
            {
                'width': 160,
                'height': 160,
                'type': 'circle'
            },
            'boundary':
            {
                'width': 160,
                'height': 160,
            },
            'showZoomer': True,
        },
    )

    class Meta:
        model = UserProfile
        fields = ("name", "picture", "country", "city")



class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # first_name = forms.TextField(required=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True

    def clean_email(self):
        uemail = self.cleaned_data.get("email")
        if User.objects.filter(email=uemail).exists():
            raise forms.ValidationError(_("User with this email already exists!"))
        else:
            return uemail

    def save(self, commit=True):
        print("Start SAfe")
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        print("Before email")
        user.username = user.email
        # self.clean_email(user.email)

        if commit:
            user.save()
        return user
