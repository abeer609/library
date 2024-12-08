from typing import Any
from django import forms
from library.models import ShippingAddress


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ["name", "region", "city", "upazila", "post_code",  "address",  "phone"]

    # region = forms.ModelChoiceField(queryset=Region.objects.all())
    # city = ChoiceField(initial="Select")
    # upazila = ChoiceField(required=True)
    # address = forms.CharField(max_length=256)
    # phone = forms.CharField(
    #     max_length=13,
    #     validators=[MinLengthValidator(11, message="Enter a valid phone number")],
    # )

    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        self.fields["region"].empty_label = "Select Region"
        self.fields["city"].empty_label = "Select City"
        self.fields["upazila"].empty_label = "Select Upazila"
