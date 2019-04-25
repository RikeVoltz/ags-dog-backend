from django import forms


class ProfileForm(forms.Form):
    walking_dates = forms.CharField(widget=forms.HiddenInput(), required=False)


class BookWalkingForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput(), required=True)
    breed = forms.CharField(widget=forms.HiddenInput(), required=True)
    hour = forms.CharField(widget=forms.HiddenInput(), required=True)
    address = forms.CharField(widget=forms.HiddenInput(), required=True)
    day = forms.CharField(widget=forms.HiddenInput(), required=True)
