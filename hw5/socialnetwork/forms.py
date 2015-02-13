from django import forms

from django.contrib.auth.models import User
from models import *

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=200,
                                 label='Password',
                                 widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=200,
                                 label='Confirm password',
                                 widget=forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'created_date',
            'user',
        )
        widgets = {
          'post_content': forms.Textarea(attrs={'rows':4, 'cols':50}),
        }
        
    def clean_post_content(self):
        post_content = self.cleaned_data.get('post_content')
        if len(post_content) > 160:
            raise forms.ValidationError("The post content is too long.")
        
        if post_content is ' ':
            raise forms.ValidationError("The post content cannot be empty.")
            
        return post_content
