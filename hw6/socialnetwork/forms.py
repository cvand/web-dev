from django import forms

from django.contrib.auth.models import User
from models import *

MAX_UPLOAD_SIZE = 2500000

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
        if username == ' ':
            raise forms.ValidationError("Please enter a valid username.")
        
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
            'comments',
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

class EditInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        exclude = (
            'user',
            'content_type',
            'following',
        )
        widgets = {
          'short_bio': forms.Textarea(attrs={'rows':5, 'cols':20}),
        }
    
    def clean(self):
        cleaned_data = super(EditInfoForm, self).clean()
        
        age = cleaned_data.get('age')
        if age:
            if age <= 0:
                raise forms.ValidationError("Your age is not valid.")
        
        
        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data['image']
        if not image:
            return None
        if not image.content_type or not image.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return image

class EditUserForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=200,
                                 label='Password',
                                 widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=200,
                                 label='Confirm password',
                                 widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        
    def clean(self):
        cleaned_data = super(EditUserForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        cleaned_data['changed_password'] = False
        if (password1 and (not password2)) or ((not password1) and password2):
            raise forms.ValidationError("Please reenter password.")
        
        if password1 and password2:
            cleaned_data['changed_password'] = True

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = (
            'first_name',
            'last_name',
        )
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = (
            'creation_date',
            'user',
        )
        widgets = {
          'comment': forms.Textarea(attrs={'rows':1, 'cols':80}),
        }
        
    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        return cleaned_data
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment) > 160:
            raise forms.ValidationError("The comment is too long.")
        
        if comment is ' ':
            raise forms.ValidationError("The comment cannot be empty.")
            
        return comment
