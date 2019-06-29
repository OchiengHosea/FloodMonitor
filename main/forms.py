from django import forms
from leaflet.forms.widgets import LeafletWidget
from main.models import FloodIncidents, FloodProneArea
class ReportFloodForm(forms.ModelForm):
    
    class Meta:
        model = FloodIncidents
        fields = ['name', 'description', 'geom']
        widgets = {'geom': LeafletWidget()}

class AddFloodProneAreaForm(forms.ModelForm):
    #geomFile = forms.FileField()

    class Meta:
        model = FloodProneArea
        fields = '__all__'
        widgets = {
            'description':forms.Textarea(attrs={'width':'100%', 'min-height':'250px'}),
            'geom': LeafletWidget()
        }
        