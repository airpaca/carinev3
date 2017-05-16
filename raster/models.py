import json
from django.contrib.gis.db import models


# Create your models here.
class Expertise(models.Model):
    daterun = models.DateField()
    pol = models.CharField(max_length=10)
    ech = models.IntegerField()
    delta = models.IntegerField()
    geom = models.GeometryField(srid=4326)

    def __str__(self):
        return (f"Expertise({self.daterun:%Y-%m-%d}, {self.pol}, ech {self.ech}"
                f", delta={self.delta}, {self.geom})")

    @property
    def json(self):
        """Object as JSON data."""
        return dict(delta=self.delta, geom=json.loads(self.geom.json))
