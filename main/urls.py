from django.urls import path
from main.views import (
	RegisterView, IndexView, LoginView,
	ReportFlood, AddFloodProneAreaView, InspectFlood,
	)
from django.views.generic import TemplateView

app_name='fldast'
urlpatterns = [
	path('', IndexView.as_view(), name='index'),
	path('register', RegisterView.as_view(), name='register'),
	path('login', LoginView.as_view(), name='login'),
	path('report-flood', ReportFlood.as_view(), name='report-flood'),
	path('flood-state/', InspectFlood.as_view(), name='flood-state'),
	path('add-flood-prone-area', AddFloodProneAreaView.as_view(), name='add-flood-prone-area'),
	path('success/', TemplateView.as_view(template_name='main/success.html'), name='success')
]