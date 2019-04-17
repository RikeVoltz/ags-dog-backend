from django import forms


class ProfileForm(forms.Form):
    walking_dates = forms.CharField(widget=forms.HiddenInput(), required=False)


class BookWalkingForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput(), required=False)
    breed = forms.CharField(widget=forms.HiddenInput(), required=False)
    hour = forms.CharField(widget=forms.HiddenInput(), required=False)
    address = forms.CharField(widget=forms.HiddenInput(), required=False)
    day = forms.CharField(widget=forms.HiddenInput(), required=False)
