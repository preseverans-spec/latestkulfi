import re

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Product, Sales, OperationsExpense, OperationsIncome



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

    DEFAULT_CATEGORIES = ['Kulfi Corner', 'Indian Kulfi']
    CATEGORY_PREFIX_MAP = {
        'Kulfi Corner': 'KC',
        'Indian Kulfi': 'IK',
    }

    category = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[],
        required=True,
        label='Category'
    )

    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'current_stock', 'reorder_level', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated from category (e.g., IK001)'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost Price', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Stock'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Reorder Level'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    @classmethod
    def get_category_prefix(cls, category_name):
        category_name = (category_name or '').strip()
        if not category_name:
            return 'PR'

        if category_name in cls.CATEGORY_PREFIX_MAP:
            return cls.CATEGORY_PREFIX_MAP[category_name]

        words = [word for word in re.split(r'\s+', category_name) if word]
        initials = ''.join(word[0].upper() for word in words[:2])
        return initials or 'PR'

    @classmethod
    def generate_next_sku(cls, category_name):
        prefix = cls.get_category_prefix(category_name)
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

        existing_categories = list(
            Product.objects.exclude(category__isnull=True)
            .exclude(category__exact='')
            .values_list('category', flat=True)
            .distinct()
        )

        category_values = []
        seen = set()

        for category in self.DEFAULT_CATEGORIES + existing_categories:
            category_name = str(category).strip()
            if category_name and category_name not in seen:
                seen.add(category_name)
                category_values.append(category_name)

        current_value = ''
        if self.instance and self.instance.pk and self.instance.category:
            current_value = self.instance.category.strip()
            if current_value and current_value not in seen:
                category_values.append(current_value)

        self.fields['category'].choices = [(value, value) for value in sorted(category_values)]

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        sku = (cleaned_data.get('sku') or '').strip().upper()

        if self.instance and self.instance.pk:
            cleaned_data['sku'] = sku or self.instance.sku
            return cleaned_data

        if not sku:
            cleaned_data['sku'] = self.generate_next_sku(category)
        else:
            cleaned_data['sku'] = sku

        return cleaned_data

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
