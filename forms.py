from django import forms
from bolti.models import Player, Practice, Match
from bolti import widgets
from django.core.urlresolvers import reverse

class RegisterForm(forms.Form):
    player = forms.CharField(label='', widget=widgets.JQueryAutoComplete(reverse('autocomplete')))
        
    def clean_player(self):
        val = self.cleaned_data['player']
        try:
            player = Player.objects.get(name__iexact=val)
        except Player.DoesNotExist:
            raise forms.ValidationError('Player does not exist')
        return player
        
class RemoveForm(RegisterForm):
    email = forms.EmailField()
    
    def clean(self):
        cleaned_data = super(RemoveForm, self).clean()
        player = cleaned_data.get('player')
        email = cleaned_data.get('email')
        if isinstance(player, Player):
            if not player.email == email:
                raise forms.ValidationError('E-mail does not match')
        return cleaned_data
                
    
class NewPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        
class RegisterScoresForm(forms.ModelForm):
    class Meta:
        model = Match