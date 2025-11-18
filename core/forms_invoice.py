from django import forms
from .models import Invoice


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices."""
    
    class Meta:
        model = Invoice
        fields = ['status', 'due_date', 'tax_amount', 'discount_amount', 'notes', 'payment_terms']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or terms'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Due upon receipt'
            }),
        }
