from django import forms


class ProfileForm(forms.Form):
    walking_dates = forms.CharField(widget=forms.HiddenInput(), required=False)
