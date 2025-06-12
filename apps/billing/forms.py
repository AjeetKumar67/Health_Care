from django import forms
from .models import Invoice, InvoiceItem, Payment

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'due_date', 'discount', 'tax', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_type', 'description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and unit_price:
            cleaned_data['total_price'] = quantity * unit_price
        
        return cleaned_data
    
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, invoice=None, **kwargs):
        super().__init__(*args, **kwargs)
        if invoice:
            remaining = invoice.final_amount - invoice.payments.aggregate(
                models.Sum('amount'))['amount__sum'] or 0
            self.fields['amount'].widget = forms.NumberInput(attrs={
                'max': remaining,
                'step': '0.01'
            })
