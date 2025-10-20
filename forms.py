from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import BudgetEntry, Donation, SavingGoal, Transaction, UserProfile, CURRENCY_CHOICES


class StyledDateInput(forms.DateInput):
    input_type = "date"
    format = "%Y-%m-%d"


class MonthInput(forms.DateInput):
    input_type = "month"
    format = "%Y-%m"


class StyledDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"
    format = "%Y-%m-%dT%H:%M"


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            "country",
            "quantity",
            "frequency",
            "message",
            "name",
            "email",
        ]
        widgets = {
            "country": forms.Select(attrs={"class": "field"}),
            "quantity": forms.NumberInput(attrs={"class": "field", "min": 1}),
            "frequency": forms.Select(attrs={"class": "field"}),
            "message": forms.TextInput(attrs={"class": "field", "placeholder": "With love"}),
            "name": forms.TextInput(attrs={"class": "field"}),
            "email": forms.EmailInput(attrs={"class": "field"}),
        }


class BudgetEntryForm(forms.ModelForm):
    class Meta:
        model = BudgetEntry
        fields = ["category", "planned_amount", "actual_amount", "month"]
        widgets = {
            "category": forms.TextInput(attrs={"class": "field"}),
            "planned_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "actual_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "month": MonthInput(attrs={"class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["month"].input_formats = ["%Y-%m"]


class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ["name", "target_amount", "current_amount", "due_date", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field"}),
            "target_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "current_amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "due_date": StyledDateInput(attrs={"class": "field"}),
            "status": forms.Select(attrs={"class": "field"}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["description", "amount", "currency", "kind", "category", "occurred_at"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "field"}),
            "amount": forms.NumberInput(attrs={"class": "field", "step": "0.01"}),
            "currency": forms.Select(attrs={"class": "field"}),  # CHANGED: TextInput to Select
            "kind": forms.Select(attrs={"class": "field"}),
            "category": forms.TextInput(attrs={"class": "field"}),
            "occurred_at": StyledDateTimeInput(attrs={"class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["occurred_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        # Set currency choices from the model
        self.fields['currency'].choices = CURRENCY_CHOICES


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "membership_level",
            "preferred_currency",
            "country",
            "city",
            "address",
            "postal_code",
            "phone_number",
            "language",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "field"}),
            "membership_level": forms.TextInput(attrs={"class": "field"}),
            "preferred_currency": forms.Select(attrs={"class": "field"}),  # CHANGED: TextInput to Select
            "country": forms.TextInput(attrs={"class": "field"}),
            "city": forms.TextInput(attrs={"class": "field"}),
            "address": forms.TextInput(attrs={"class": "field"}),
            "postal_code": forms.TextInput(attrs={"class": "field"}),
            "phone_number": forms.TextInput(attrs={"class": "field"}),
            "language": forms.TextInput(attrs={"class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from the model
        self.fields['preferred_currency'].choices = CURRENCY_CHOICES


class MoneyTransferForm(forms.Form):
    recipient_phone = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={
            'class': 'field',
            'placeholder': 'Recipient phone number',
            'required': True
        })
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'field',
            'placeholder': '0.00',
            'step': '0.01',
            'required': True
        })
    )
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial='USD',
        widget=forms.Select(attrs={
            'class': 'field',
            'required': True
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'field',
            'placeholder': 'Optional description'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def clean_recipient_phone(self):
        phone = self.cleaned_data.get('recipient_phone')
        if self.request and phone == self.request.user.profile.phone_number:
            raise forms.ValidationError("You cannot send money to yourself.")
        return phone
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount


class StyledAuthenticationForm(AuthenticationForm):
    """Wrap Django's auth form so templates can use a consistent CSS class."""

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "field"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "field"}))