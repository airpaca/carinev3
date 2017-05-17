import json
from django.contrib.gis.db import models


# Create your models here.
class Expertise(models.Model):
    daterun = models.DateField()
    pol = models.CharField(max_length=10)
    ech = models.IntegerField()
    delta = models.IntegerField()
    mn = models.IntegerField(default=None, null=True)  # limit min
    mx = models.IntegerField(default=None, null=True)  # limit max
    geom = models.GeometryField(srid=4326)

    def __str__(self):
        return (f"Expertise({self.daterun:%Y-%m-%d}, {self.pol}, ech {self.ech}"
                f", delta={self.delta}, min={self.mn}, max={self.mx}, "
                f"{self.geom})")

    @property
    def json(self):
        """Object as JSON data."""
        return dict(delta=self.delta, mn=self.mn, mx=self.mx,
                    geom=json.loads(self.geom.json))
