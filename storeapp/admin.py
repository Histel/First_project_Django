from PIL import Image

from django.contrib import admin
from django import forms
from django.forms import ModelForm, ValidationError

from .models import *


class SmartphoneAdmonModel(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance.sd:
            self.fields['sd_values_max'].widget.attrs.update({

            })
        if instance.unstandart_resolution:
            self.fields['input_resolution'].widget.attrs.update({
                'disabled': True,
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_values_max'] == None
        if not self.cleaned_data['unstandart_resolution']:
            self.cleaned_data['input_resolution'] == None
        return self.cleaned_data



class NotebooksCategoryChoiceField(forms.ModelChoiceField):
    pass

class SmartphonesCategoryChoiceField(forms.ModelChoiceField):
    pass


class NotebooksAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return NotebooksCategoryChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):

    change_form_template = 'storeapp/admin.html'
    form = SmartphoneAdmonModel

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return SmartphonesCategoryChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Noteboocks, NotebooksAdmin)
admin.site.register(Smartphones, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)