from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from main.models import WorldBorder, River
from main.models import FloodIncidents as fds
from django.core.serializers import serialize
from main.forms import ReportFloodForm, AddFloodProneAreaForm, FloodProneArea as fdp
from django.contrib.gis import geos
from rest_framework.response import Response
from rest_framework.views import APIView

#shapely imports
from shapely.geometry import Point, Polygon, shape, mapping
from functools import partial
import pyproj
from shapely.ops import transform
from django.contrib.gis import geos

#For eolearn
from eolearn.io import S2L1CWCSInput, DEMWCSInput
from eolearn.core import EOTask, EOPatch, LinearWorkflow, Dependency, FeatureType, LoadFromDisk, SaveToDisk
from sentinelhub import BBox, CRS
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt

#concurencies
import asyncio

#datetime imprts
from datetime import datetime, timedelta, date
from django.utils import timezone
# Create your views here.

#IBM weather api
import weatherapi.app as weatherapi
class IndexView(TemplateView):
	def __init__(self):
		self.world_borders = None
		self.active_country = None
		self.active_country_geojson = None
		self.active_country_name = 'Kenya'
		self.reported_incidents = []
		self.center = (0,0)
		

	template_name = "main/index.html"
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		today = timezone.now()
		three_days_before = today+timedelta(days=-3)
		date_str = 'today'
		self.world_borders = WorldBorder.objects.all()
		self.active_country = self.world_borders.filter(name=self.active_country_name)
		self.active_country_geojson = serialize('geojson', self.active_country)
		self.reported_incidents = fds.objects.filter(geom__within=self.active_country[0].geom)
		self.recent_incidents = fds.objects.filter(date__range=[str(three_days_before), str(today)])
		self.prone_ares = fdp.objects.all()
		geom = geos.GEOSGeometry(self.active_country[0].geom)
		context['center'] = geom.centroid.coords
		context['latitude']=geom.centroid.coords[1]
		context['longitude']=geom.centroid.coords[0]
		context['countries']=self.world_borders
		context['selected_country'] = self.active_country[0]
		context['selected_country_geojson'] = self.active_country_geojson
		context['incidents'] = self.reported_incidents
		context['recent_incidents'] = self.recent_incidents
		context['prone_area'] = self.prone_ares
		return context

class RegisterView(generic.CreateView):
	form_class = UserCreationForm
	template_name = 'main/register.html'
	success_url = 'login'
	
class LoginView(TemplateView):
	template_name = "main/login.html"

	def get_context_data(self, **kwargs):
		context = super(LoginView, self).get_context_data(**kwargs)
		print(self.request.user.id)
		#User.objects.filter(pk=self.request.user.id)
		context['user'] = User

class ReportFlood(generic.CreateView):
	template_name = "main/report-flood.html"
	form_class = ReportFloodForm
	success_url = 'success/'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = ReportFloodForm
		return context

class AddFloodProneAreaView(generic.CreateView):
	template_name = "main/add-flood-prone-area.html"
	form_class = AddFloodProneAreaForm
	success_url = 'success/'

class InspectFlood(APIView):
	def __init__(self):
		self.area = ""
		self.nearby_rivers = []
		self.longitude = 0.0
		self.latitude = 0.0
		self.geometry = Point(0,0)
		self.proj_wgs84 = pyproj.Proj(init='epsg:4326')
		self.radius = 3
		self.response = {}

	def geodesic_point_buffer(self, lat, lng, km):
		aeqd_proj = '+proj=aeqd + lat_0={lat} +lon_0={lng} +x_0=0 +y_0=0'
		project = partial(pyproj.transform, pyproj.Proj(aeqd_proj.format(lat=lat, lng=lng)), self.proj_wgs84)
		buff = Point(0,0).buffer(km*1000)
		return transform(project, buff).exterior.coords[:]

	def get(self, request, **kwargs):
		params = request.GET
		if params:
			print()
			self.latitude = round(float(params.get('lat')), 4)
			self.longitude = round(float(params.get('lng')), 4)
			self.radius = int(params.get('radius'))
			self.geometry = self.geodesic_point_buffer(self.latitude, self.longitude, self.radius)
			geosGeom = geos.Polygon(self.geometry)
			self.near_rivers = River.objects.filter(geom__intersects=geosGeom)
			self.nearby_rivers = serialize('geojson',self.near_rivers)
			self.response['lat'] = self.latitude
			self.response['lng'] = self.longitude
			self.response['nearby_rivers'] = self.nearby_rivers
			self.response['geometry'] = mapping(Polygon(self.geometry))
			self.response['flood_prone'] = self.is_flood_prone_area(geosGeom)
			#eopatch = self.get_elevation(Polygon(self.geometry).bounds)
			#eopatch_sq = eopatch.data_timeless['MAPZEN_DEM'].squeeze()
			self.response['mean_slope'] = np.random.rand()#self.calclute_slope(eopatch_sq).mean()
			self.response['msl'] = np.random.uniform(low=600, high=4000, size=None)#self.calculate_mean_sea_level(eopatch_sq)
			self.response['rain_prediction'] = self.get_rain_prediction(self.latitude, self.longitude)
			self.response['remarks']=self.determine_flood_safe()
			"""plt.figure(figsize=(10,10))
			plt.imshow(eopatch.data_timeless['MAPZEN_DEM'].squeeze())
			plt.show()"""
			
		else:
			print("No query params")

		return Response(self.response)

	def get_elevation(self, bounds):
		INSTANCE_ID = '4aaea2ec-3a2c-4e1c-8a51-851e220d0273'
		roi = BBox(bbox=bounds, crs=CRS.WGS84)
		layer = 'MAPZEN_DEM'
		time_interval = ('2019-01-01', '2019-06-01')
		add_dem = DEMWCSInput(layer=layer, instance_id=INSTANCE_ID)
		input_task = S2L1CWCSInput(layer=layer, resx='30m', resy='30m', instance_id=INSTANCE_ID)
		workflow = LinearWorkflow(input_task, add_dem)
		result = workflow.execute({input_task:{'bbox':roi, 'time_interval':time_interval}})
		eopatch = list(result.values())[0]
		
		return eopatch

	def calclute_slope(self, dem_array):
		slope = np.gradient(dem_array[0], dem_array[1])
		return slope[~np.isnan(slope)]


	def calculate_mean_sea_level(self, dem_array):
		dem_no_nan = dem_array[~np.isnan(dem_array)]
		return dem_no_nan.mean()


	def is_flood_prone_area(self, area):
		return True if fdp.objects.filter(geom__intersects=area) else False

	def get_rain_prediction(self, lat, lon):
		return weatherapi.callWhenWillItRain(str(lat), str(lon))

	def determine_flood_safe(self):
		rivers_width_greater_than_20 = [river for river in self.near_rivers if river.width > 20]
		dangerous_rivers = [river for river in rivers_width_greater_than_20 if river.discharge < 1]
		dangerous_slope = self.response['msl'] < 1
		alert = ''
		if(self.response['rain_prediction']['precip_time_iso'] and self.response['flood_prone']):
			alert = 'Flooding may occur in the next 6 hours'
		
		remarks = {
			'wide_rivers':len(rivers_width_greater_than_20),
			'dangerous_rivers':len(dangerous_rivers),
			'dangerous_slope':dangerous_slope,
			'alert':alert
		}
		return remarks