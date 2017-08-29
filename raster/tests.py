import json
import datetime
from django.test import TestCase, Client
from .models import Expertise


class TestModels(TestCase):
    """Test models."""
    def setUp(self):
        self.drun = datetime.date.today()

    def test_init(self):
        e = Expertise(daterun=self.drun, pol='NO2', ech=0, delta=5,
                      geom='POINT(5 45)')
        self.assertIsInstance(e, Expertise)
        self.assertIn('Expertise', str(e))
        self.assertEqual(e.geom.coords, (5.0, 45.0))

    def test_json(self):
        e = Expertise(daterun=self.drun, pol='NO2', ech=0, delta=15,
                      geom='POINT(4 46)')
        self.assertEqual(e.json['delta'], 15)
        self.assertEqual(e.json['geom']['type'], 'Point')
        self.assertEqual(e.json['geom']['coordinates'], [4., 46.])

    def test_save(self):
        # Clean before
        Expertise.objects.all().delete()
        self.assertEqual(len(Expertise.objects.all()), 0)

        # Insert 2 rows
        e1 = Expertise(daterun=self.drun, pol='NO2', ech=1, delta=10,
                       geom='POINT(5 44)')
        e1.save()

        e2 = Expertise(daterun=self.drun, pol='PM10', ech=0, delta=-5,
                       geom='POLYGON((1 1, 5 1, 5 5, 1 5, 1 1))')
        e2.save()

        # Check
        self.assertEqual(len(Expertise.objects.all()), 2)


class TestViews(TestCase):
    """Test views."""
    def setUp(self):
        self.c = Client()
        self.drun = datetime.date.today()

    def test_view_index(self):
        r = self.c.get('/raster/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'<title>Carine v3</title>', r.content)

    def test_view_application_js(self):
        r = self.c.get('/raster/application.map.js')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"var map = L.map", r.content)

    def test_view_img_raster(self):
        r = self.c.get('/raster/img/raster_NO2_ech0.png')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b'\x89PNG'))

    def test_view_bbox_raster(self):
        r = self.c.get('/raster/bbox/raster_NO2_ech0.json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('xmin', r.json())
        self.assertIn('ymin', r.json())
        self.assertIn('xmax', r.json())
        self.assertIn('ymax', r.json())

    def test_view_list_modification_1_point(self):
        # Test data
        pol, ech = 'NO2', 1
        delta, x, y = 10, 5, 44

        # Insert data
        Expertise.objects.all().delete()
        e = Expertise(daterun=self.drun, pol=pol, ech=ech, delta=delta,
                      geom=f'POINT({x} {y})')
        e.save()

        # Check the view
        r = self.c.get(f'/raster/modifications/{pol}/ech{ech}/list.json')
        self.assertEqual(r.status_code, 200)

        data = r.json()
        self.assertEqual(data['daterun'], self.drun.strftime('%Y-%m-%d'))
        self.assertEqual(data['pol'], pol)
        self.assertEqual(data['ech'], ech)
        self.assertEqual(len(data['modifs']), 1)
        self.assertEqual(data['modifs'][0]['delta'], delta)
        self.assertEqual(data['modifs'][0]['geom']['type'], 'Point')
        self.assertEqual(data['modifs'][0]['geom']['coordinates'], [x, y])

    def test_view_list_modification_multiples_objects(self):
        # Test data
        pol, ech = 'PM10', 2
        geoms = [
            # delta, geom_type, coords
            (-5, 'POLYGON', [[1, 1], [5, 1], [5, 5], [1, 5], [1, 1]]),
            (6, 'POLYGON', [[10, 10], [5, 10], [5, 5], [10, 5], [10, 10]]),
            (10, 'POINT', [6, 6]),
        ]

        # Insert datas
        Expertise.objects.all().delete()
        for delta, geomtype, coords in geoms:
            if geomtype == 'POINT':
                geom = f'POINT({coords[0]} {coords[1]})'

            else:
                strcoord = ", ".join([f"{x} {y}" for (x, y) in coords])
                geom = f'POLYGON(({strcoord}))'

            e = Expertise(daterun=self.drun, pol=pol, ech=ech, delta=delta,
                          geom=geom)
            e.save()

        # Check the view
        r = self.c.get(f'/raster/modifications/{pol}/ech{ech}/list.json')
        self.assertEqual(r.status_code, 200)

        data = r.json()
        self.assertEqual(data['daterun'], self.drun.strftime('%Y-%m-%d'))
        self.assertEqual(data['pol'], pol)
        self.assertEqual(data['ech'], ech)
        self.assertEqual(len(data['modifs']), len(geoms))
        for i, (delta, geomtype, coords) in enumerate(geoms):
            self.assertEqual(data['modifs'][i]['delta'], delta)
            self.assertEqual(data['modifs'][i]['geom']['type'].upper(),
                             geomtype)
            if geomtype == 'POINT':
                self.assertEqual(data['modifs'][i]['geom']['coordinates'],
                                 coords)
            else:
                self.assertEqual(data['modifs'][i]['geom']['coordinates'],
                                 [coords])

    def test_view_alter_raster_get_error(self):
        r = self.c.get('/raster/alter_raster/')
        self.assertEqual(r.status_code, 405)

    def test_view_alter_raster_post_missing_data(self):
        r = self.c.post('/raster/alter_raster/', data={},
                        content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()['status'], 'error')

    def test_view_alter_raster_post_data_ok(self):
        # Clean database
        Expertise.objects.all().delete()

        objs = Expertise.objects.all()
        self.assertEqual(len(objs), 0)

        # Insert data
        data = {
            "pol": "NO2",
            "ech": 0,
            "modifs": [{
                "delta": 5,
                "geom": {
                    "type": "Point",
                    "coordinates": [5, 45]
                }}, {
                "delta": -10,
                "geom": {
                    "type": "Polygon",
                    "coordinates": [[[6, 46], [7, 48], [8, 42], [6, 46]]]
                }}
            ]
        }

        r = self.c.post('/raster/alter_raster/', json.dumps(data),
                        content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ok')

        # Check database
        objs = Expertise.objects.all().order_by('delta')
        self.assertEqual(len(objs), 2)

        self.assertEqual(objs[1].pol, 'NO2')
        self.assertEqual(objs[1].ech, 0)
        self.assertEqual(objs[1].delta, 5)
        self.assertEqual(objs[1].geom.geom_type, 'Point')
        self.assertEqual(objs[1].geom.coords, (5., 45.))

        self.assertEqual(objs[0].pol, 'NO2')
        self.assertEqual(objs[0].ech, 0)
        self.assertEqual(objs[0].delta, -10)
        self.assertEqual(objs[0].geom.geom_type, 'Polygon')
        self.assertEqual(objs[0].geom.coords[0],
                         ((6, 46), (7, 48), (8, 42), (6, 46)))




