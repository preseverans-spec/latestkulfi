import re

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Manufacturer, Product, Sales, OperationsExpense, OperationsIncome


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manufacturer name'}),
            'code': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].required = False

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if not name:
            raise forms.ValidationError('Manufacturer name is required.')
        if Manufacturer.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('A manufacturer with this name already exists.')
        return name

    def clean_code(self):
        code = (self.cleaned_data.get('code') or '').strip().upper()
        if not code:
            name = (self.cleaned_data.get('name') or '').strip()
            code = name.upper().replace(' ', '_')[:50]
        return code

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.code:
            instance.code = instance.name.strip().upper().replace(' ', '_')[:50]
        if commit:
            instance.save()
        return instance



class ProductForm(forms.ModelForm):
    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is not None and cost_price < 0:
            raise forms.ValidationError('Cost price cannot be negative.')
        return cost_price

    def clean_selling_price(self):
        selling_price = self.cleaned_data.get('selling_price')
        if selling_price is not None and selling_price < 0:
            raise forms.ValidationError('Selling price cannot be negative.')
        return selling_price

    def clean_current_stock(self):
        current_stock = self.cleaned_data.get('current_stock')
        if current_stock is not None and current_stock < 0:
            raise forms.ValidationError('Current stock cannot be negative.')
        return current_stock

    def clean_reorder_level(self):
        reorder_level = self.cleaned_data.get('reorder_level')
        if reorder_level is not None and reorder_level < 0:
            raise forms.ValidationError('Reorder level cannot be negative.')
        return reorder_level

    DEFAULT_CATEGORY = 'Indian Kulfi'

    category = forms.CharField(
        widget=forms.HiddenInput(),
        initial=DEFAULT_CATEGORY,
        required=False,
    )

    class Meta:
        model = Product
        fields = ['name', 'sku', 'manufacturer', 'category', 'cost_price', 'selling_price', 'current_stock', 'reorder_level', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated from manufacturer (e.g., BR001)'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost Price', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Stock'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Reorder Level'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    @staticmethod
    def resolve_manufacturer_name(manufacturer_value):
        if manufacturer_value is None:
            return ''

        if isinstance(manufacturer_value, Manufacturer):
            return (manufacturer_value.name or '').strip()

        value = str(manufacturer_value).strip()
        if not value:
            return ''

        try:
            manufacturer_id = int(value)
        except ValueError:
            manufacturer_id = None

        if manufacturer_id is not None:
            manufacturer = Manufacturer.objects.filter(pk=manufacturer_id).only('name', 'code').first()
            if manufacturer:
                return (manufacturer.name or '').strip()

        manufacturer = Manufacturer.objects.filter(name__iexact=value).only('name', 'code').first()
        if manufacturer:
            return (manufacturer.name or '').strip()

        return value

    @classmethod
    def get_manufacturer_prefix(cls, manufacturer_name):
        manufacturer_name = cls.resolve_manufacturer_name(manufacturer_name)
        manufacturer_name = (manufacturer_name or '').strip()
        if not manufacturer_name:
            return 'PR'

        manufacturer = Manufacturer.objects.filter(name__iexact=manufacturer_name).only('code').first()
        if manufacturer and manufacturer.code:
            return manufacturer.code.strip().upper()[:10]

        words = [word for word in re.split(r'\s+', manufacturer_name) if word]
        initials = ''.join(word[0].upper() for word in words[:2])
        return initials or 'PR'

    @classmethod
    def generate_next_sku(cls, manufacturer_name):
        manufacturer_name = cls.resolve_manufacturer_name(manufacturer_name)
        prefix = cls.get_manufacturer_prefix(manufacturer_name)
        pattern = re.compile(rf'^{re.escape(prefix)}(\d+)$', re.IGNORECASE)

        max_number = 0
        for existing_sku in Product.objects.filter(sku__istartswith=prefix).values_list('sku', flat=True):
            match = pattern.match((existing_sku or '').strip())
            if match:
                max_number = max(max_number, int(match.group(1)))

        return f'{prefix}{max_number + 1:03d}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sku'].required = False
        Manufacturer.ensure_defaults()
        self.fields['manufacturer'].queryset = Manufacturer.objects.filter(is_active=True).order_by('name')
        self.fields['manufacturer'].empty_label = 'Select Manufacturer'
        self.fields['manufacturer'].required = True

        if self.instance and self.instance.manufacturer_id:
            self.fields['category'].initial = self.instance.manufacturer.name
        else:
            self.fields['category'].initial = self.DEFAULT_CATEGORY

    def clean(self):
        cleaned_data = super().clean()
        manufacturer = cleaned_data.get('manufacturer')
        sku = (cleaned_data.get('sku') or '').strip().upper()
        cleaned_data['category'] = manufacturer.name if manufacturer else self.DEFAULT_CATEGORY

        if sku:
            duplicate_sku = Product.objects.filter(sku__iexact=sku)
            if self.instance and self.instance.pk:
                duplicate_sku = duplicate_sku.exclude(pk=self.instance.pk)
            if duplicate_sku.exists():
                raise forms.ValidationError('A product with this SKU already exists.')

        if self.instance and self.instance.pk:
            cleaned_data['sku'] = sku or self.instance.sku
            return cleaned_data

        if not sku:
            cleaned_data['sku'] = self.generate_next_sku(manufacturer.name if manufacturer else '')
        else:
            cleaned_data['sku'] = sku

        return cleaned_data


class ProductMoveForm(forms.Form):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Target Manufacturer',
    )
    cost_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Cost Price',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Manufacturer.ensure_defaults()
        self.fields['manufacturer'].queryset = Manufacturer.objects.filter(is_active=True).order_by('name')

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['sale_date', 'product', 'quantity', 'notes']  # Removed unit_price from fields
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity', 'id': 'quantity-input'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set today's date as initial value
        self.fields['sale_date'].initial = timezone.now().date()

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set unit_price from the selected product's selling_price
        if instance.product:
            instance.unit_price = instance.product.selling_price
        if commit:
            instance.save()
        return instance

class DateRangeForm(forms.Form):
    """Form for filtering reports by date range"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='End Date'
    )


class OperationsExpenseForm(forms.ModelForm):
    class Meta:
        model = OperationsExpense
        fields = ['operation_date', 'details', 'amount']
        widgets = {
            'operation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Details of operation'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation_date'].initial = timezone.now().date()


class OperationsIncomeForm(forms.ModelForm):
    class Meta:
        model = OperationsIncome
        fields = ['income_date', 'details', 'amount']
        widgets = {
            'income_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Income source details'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['income_date'].initial = timezone.now().date()

class UserManagementForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep current password"
    )
    is_staff = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="Staff Status (Can access admin)"
    )
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="Active"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
