from django import forms


class CouponApplyForm(forms.Form):
    """
    A form for applying coupon to cart. This form accepts coupon code.

    Attributes:
        code: CharField - The code given by user
    """
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}))