from urllib.parse import urlparse
from django import forms


class AddPropertyForm(forms.Form):
    url = forms.URLField(
        label="Link do oferty Otodom",
        widget=forms.URLInput(attrs={
            'placeholder': 'https://www.otodom.pl/pl/oferta/...',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm'
        })
    )

    def clean_url(self):
        """Validate that the submitted URL originates from otodom.pl."""
        url = self.cleaned_data.get('url')
        parsed = urlparse(url)
        if 'otodom.pl' not in parsed.netloc:
            raise forms.ValidationError("Podany adres URL musi pochodzić z serwisu otodom.pl")
        return url