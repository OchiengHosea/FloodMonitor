from django.contrib.gis.db import models
from decimal import Decimal

# Create your models here.
class WorldBorder(models.Model):
	"""World borders"""
	fips = models.CharField(max_length=2)
	iso2 = models.CharField(max_length=2)
	iso3 = models.CharField(max_length=3)
	un = models.IntegerField()
	name = models.CharField(max_length=50)
	area = models.IntegerField()
	pop2005 = models.BigIntegerField()
	region = models.IntegerField()
	subregion = models.IntegerField()
	lon = models.FloatField()
	lat = models.FloatField()
	geom = models.MultiPolygonField(srid=4326)

class FloodIncidents(models.Model):
	name = models.CharField(max_length=125)
	description = models.CharField(max_length=600, blank=True)
	geom = models.GeometryField(srid=4326)
	date = models.DateTimeField(auto_now_add=True, null=True)
	level = models.DecimalField(max_digits=4, decimal_places=4, default=Decimal('0.0000'))
	confirmed = models.BooleanField(default=False)

	def save(self):
		super(FloodIncidents, self).save()
		
	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Flood Areas"

class FloodProneArea(models.Model):
	name = models.CharField(max_length=55)
	description = models.CharField(max_length=1000)
	avg_rainfall = models.DecimalField(decimal_places=4, max_digits=10, help_text="Average rainfall per month", blank=True, null=True)
	msl = models.DecimalField(decimal_places=4, max_digits=10, help_text="Mean Sea Level", blank=True, null=True)
	peak = models.PointField(srid=4326, help_text="The highest point of this area", blank=True, null=True)
	#folder = models.URLField(help_text="File folder for this area", blank=True, null=True)
	geom = models.PolygonField(srid=4326)


	def __str__(self):
		return self.name

class River(models.Model):
    cat = models.BigIntegerField()
    area = models.FloatField()
    up_cells = models.BigIntegerField()
    discharge = models.FloatField()
    width = models.FloatField()
    width5 = models.FloatField()
    width95 = models.FloatField()
    depth = models.FloatField()
    depth5 = models.FloatField()
    depth95 = models.FloatField()
    arcid = models.BigIntegerField()
    geom = models.MultiLineStringField(srid=4326)
    