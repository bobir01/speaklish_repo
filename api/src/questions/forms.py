from django import forms
from api.models import Part1Question, Part2Question, Part3Question

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class Part1QuestionForm(forms.ModelForm):
    class Meta:
        model = Part1Question
        fields = ['question_txt', 'question_category']

class Part2QuestionForm(forms.ModelForm):
    class Meta:
        model = Part2Question
        fields = ['question_txt']

class Part3QuestionForm(forms.ModelForm):
    class Meta:
        model = Part3Question
        fields = ['question_txt', 'part2_question']
