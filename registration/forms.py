from django import forms
from registration.models import userInfo, User, studentProfile
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator

class userInfoForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    username = forms.CharField(widget=forms.HiddenInput, initial="default")
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password',)

    def clean(self):
        cleaned_data = super(userInfoForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        # print(password)
        # print(confirm_password)
        if password != confirm_password:
            raise forms.ValidationError("Password does not match")

    def clean_username(self):
        default = "default"
        username = self.cleaned_data['username']
        if username != default:
            raise forms.ValidationError("Dont try to play with site security")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        email = email.lower()
        domain = email.split('@')[1]
        domain_list = ["albany.edu", ]

        if domain not in domain_list:
            raise forms.ValidationError("Please enter an Email Address with a albany.edu domain")

        try:
            User.objects.get(email=email)
            # print("we are in")
            raise forms.ValidationError('This email address is already in use.')
        except User.DoesNotExist:
            # print("we are out")
            pass

        return email

        ####WHITELISTING CODE (SAVED FOR FUTURE)####
        # try:
        #     User.objects.get(email=email)
        #     raise forms.ValidationError('This email address is already in use.')
        # except User.DoesNotExist:
        #     try:
        #         studentWhiteList.objects.get(email=email)
        #     except studentWhiteList.DoesNotExist:
        #         try:
        #             professorWhiteList.objects.get(email=email)
        #         except professorWhiteList.DoesNotExist:
        #             raise forms.ValidationError('This email address not white listed yet. Please contact administrator')
        # return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if CommonPasswordValidator().validate(password):
            raise forms.ValidationError("Password too common, Please chose some other password")
        elif MinimumLengthValidator().validate(password):
            raise forms.ValidationError("Password must be of minimum 9 characters length")
        else:
            return password


class userInfoForm2(forms.ModelForm):
    studentOrProfessor = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta():
        model = userInfo
        fields = ('studentOrProfessor',)


class DateInput(forms.DateInput):
    input_type = 'date'

class studentProfileForm(forms.ModelForm):

    class Meta():
        model = studentProfile
        fields = ('first_name', 'last_name', 'SUNY_ID', 'native_country', 'program_joining_date',)
        widgets = {
            'program_joining_date': DateInput()
        }

    def clean_program_joining_date(self):
        program_joining = self.cleaned_data['program_joining_date']
        date = str(program_joining)
        # print('date -->' + date)
        if date == 'None':
            # print("inside")
            raise forms.ValidationError("Programming Joining Date can not be empty")

        return program_joining

class professorProfileForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('first_name', 'last_name',)
