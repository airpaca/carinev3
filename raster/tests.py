import json
import datetime
from django.test import TestCase, Client
from .models import Expertise,Source,TypeSourceRaster,DatePrev,Prev,IndiceCom
from libcarine3 import timestamp,raster,merge_tools,colors
import libcarine3
import add_sources
import os
import config
import raster.views
import numpy as np
tt=1508364000
class TestUtils(TestCase):
    def test_tsp(self):
        tsp=timestamp.getTimestamp(0)
        self.assertEqual(tsp,tt)
    def test_tsp_negatif(self):
        tsp=timestamp.getTimestamp(-1)
        self.assertEqual(tsp,tt+86400)
class TestInitModel(TestCase):
    def setUp(self):
        self.tsp=timestamp.getTimestamp(0)
        self.nb_default_source = add_sources.add_tsr()
        self.nb_jours_init= -1 
        self.nb_jours_avant = 0
        #self.res_prevss=add_sources.init_today(0)
    def test_check_tsr(self):
        tsr = TypeSourceRaster.objects.all()
        #len tsr = echs * run * polls * types
        self.assertEqual(len(tsr),(4*3*4*4))
    def test_today_prev(self):
        #4 * nb polls
        # on test aujourd'hui, doit etre valable pr ts les jours
        for i in range(self.nb_jours_init,self.nb_jours_avant):
            add_sources.init_today(i)

        nb_prev = len(Prev.objects.all())
        self.assertEqual(nb_prev ,(self.nb_jours_avant-self.nb_jours_init)*16)
    def test_nb_dateprev(self):
        assert(len(DatePrev.objects.all()),self.nb_jours_init)
    def test_tsr(self):
        tsr = TypeSourceRaster.objects.filter(pol='PM10',type='ada')
        self.assertEqual(len(tsr),12)
        
class TestRaster(TestCase):
    def setUp(self):
        self.nb_default_source = add_sources.add_tsr()
        self.ah=add_sources.init_today(2)
        self.h=add_sources.init_today(1)
        self.auj=add_sources.init_today(0)

        #checkage du pm10 d'aujourd'hui à j0, ada
        self.tsp=timestamp.getTimestamp(0)
        self.tsr = TypeSourceRaster.objects.get(pol='PM10',type='ada',intrun=0,ech=0)
        self.src=Source.objects.get(daterun=self.tsp,tsr = self.tsr)
    def test_url(self):
        url = self.src.url()
        self.assertEqual(url,os.path.join(config.DIR_RASTERS,'AURA_PM10_'+str(self.tsp)+'_jp0_ada.tif'))
        
    def test_ing_raster(self):

        # Read raster
        ob=self.src
        fnrst =ob.url()
        
        r = libcarine3.Raster(fnrst, pol=config.from_name(ob.tsr.pol),source=ob)
        # r.add_expertises(expertises)

        data=r.get_array()
       
        if (ob.tsr.pol!='MULTI'):
            #log.debug(" ------ STARTING ss_indice ---------")
            data=libcarine3.merge_tools.sous_indice(data,config.from_name(ob.tsr.pol))
        self.assertEqual(data.shape,(300,400))
        
    # def test_json(self):
        # e = Expertise.objects.all()

# class TestRaster(TestCase):
    # def setUp(self):
        # self.tsp=timestamp.getTimestamp(0)
        # self.id_source=5
    # def test_idsource(self):
        # source = Source.objects.get(id=self.id_source)
        
    

# class TestViews(TestCase):
    # """Test views."""
    # def setUp(self):
        # self.c = Client()
        # self.drun = datetime.date.today()

    # def test_view_index(self):
        # r = self.c.get('/raster/')
        # self.assertEqual(r.status_code, 200)
        # self.assertIn(b'<title>Carine v3</title>', r.content)

    # def test_view_application_js(self):
        # r = self.c.get('/raster/application.map.js')
        # self.assertEqual(r.status_code, 200)
        # self.assertIn(b"var map = L.map", r.content)

    # def test_view_img_raster(self):
        # r = self.c.get('/raster/img/raster_NO2_ech0.png')
        # self.assertEqual(r.status_code, 200)
        # self.assertTrue(r.content.startswith(b'\x89PNG'))

    # def test_view_bbox_raster(self):
        # r = self.c.get('/raster/bbox/raster_NO2_ech0.json')
        # self.assertEqual(r.status_code, 200)
        # self.assertIn('xmin', r.json())
        # self.assertIn('ymin', r.json())
        # self.assertIn('xmax', r.json())
        # self.assertIn('ymax', r.json())

    # def test_view_list_modification_1_point(self):
        # Test data
        # pol, ech = 'NO2', 1
        # delta, x, y = 10, 5, 44

        # Insert data
        # Expertise.objects.all().delete()
        # e = Expertise(daterun=self.drun, pol=pol, ech=ech, delta=delta,
                      # geom=f'POINT({x} {y})')
        # e.save()

        # Check the view
        # r = self.c.get(f'/raster/modifications/{pol}/ech{ech}/list.json')
        # self.assertEqual(r.status_code, 200)

        # data = r.json()
        # self.assertEqual(data['daterun'], self.drun.strftime('%Y-%m-%d'))
        # self.assertEqual(data['pol'], pol)
        # self.assertEqual(data['ech'], ech)
        # self.assertEqual(len(data['modifs']), 1)
        # self.assertEqual(data['modifs'][0]['delta'], delta)
        # self.assertEqual(data['modifs'][0]['geom']['type'], 'Point')
        # self.assertEqual(data['modifs'][0]['geom']['coordinates'], [x, y])

    # def test_view_list_modification_multiples_objects(self):
        # Test data
        # pol, ech = 'PM10', 2
        # geoms = [
            # delta, geom_type, coords
            # (-5, 'POLYGON', [[1, 1], [5, 1], [5, 5], [1, 5], [1, 1]]),
            # (6, 'POLYGON', [[10, 10], [5, 10], [5, 5], [10, 5], [10, 10]]),
            # (10, 'POINT', [6, 6]),
        # ]

        # Insert datas
        # Expertise.objects.all().delete()
        # for delta, geomtype, coords in geoms:
            # if geomtype == 'POINT':
                # geom = f'POINT({coords[0]} {coords[1]})'

            # else:
                # strcoord = ", ".join([f"{x} {y}" for (x, y) in coords])
                # geom = f'POLYGON(({strcoord}))'

            # e = Expertise(daterun=self.drun, pol=pol, ech=ech, delta=delta,
                          # geom=geom)
            # e.save()

        # Check the view
        # r = self.c.get(f'/raster/modifications/{pol}/ech{ech}/list.json')
        # self.assertEqual(r.status_code, 200)

        # data = r.json()
        # self.assertEqual(data['daterun'], self.drun.strftime('%Y-%m-%d'))
        # self.assertEqual(data['pol'], pol)
        # self.assertEqual(data['ech'], ech)
        # self.assertEqual(len(data['modifs']), len(geoms))
        # for i, (delta, geomtype, coords) in enumerate(geoms):
            # self.assertEqual(data['modifs'][i]['delta'], delta)
            # self.assertEqual(data['modifs'][i]['geom']['type'].upper(),
                             # geomtype)
            # if geomtype == 'POINT':
                # self.assertEqual(data['modifs'][i]['geom']['coordinates'],
                                 # coords)
            # else:
                # self.assertEqual(data['modifs'][i]['geom']['coordinates'],
                                 # [coords])

    # def test_view_alter_raster_get_error(self):
        # r = self.c.get('/raster/alter_raster/')
        # self.assertEqual(r.status_code, 405)

    # def test_view_alter_raster_post_missing_data(self):
        # r = self.c.post('/raster/alter_raster/', data={},
                        # content_type='application/json')
        # self.assertEqual(r.status_code, 400)
        # self.assertEqual(r.json()['status'], 'error')

    # def test_view_alter_raster_post_data_ok(self):
        # Clean database
        # Expertise.objects.all().delete()

        # objs = Expertise.objects.all()
        # self.assertEqual(len(objs), 0)

        # Insert data
        # data = {
            # "pol": "NO2",
            # "ech": 0,
            # "modifs": [{
                # "delta": 5,
                # "geom": {
                    # "type": "Point",
                    # "coordinates": [5, 45]
                # }}, {
                # "delta": -10,
                # "geom": {
                    # "type": "Polygon",
                    # "coordinates": [[[6, 46], [7, 48], [8, 42], [6, 46]]]
                # }}
            # ]
        # }

        # r = self.c.post('/raster/alter_raster/', json.dumps(data),
                        # content_type='application/json')
        # self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.json()['status'], 'ok')

        # Check database
        # objs = Expertise.objects.all().order_by('delta')
        # self.assertEqual(len(objs), 2)

        # self.assertEqual(objs[1].pol, 'NO2')
        # self.assertEqual(objs[1].ech, 0)
        # self.assertEqual(objs[1].delta, 5)
        # self.assertEqual(objs[1].geom.geom_type, 'Point')
        # self.assertEqual(objs[1].geom.coords, (5., 45.))

        # self.assertEqual(objs[0].pol, 'NO2')
        # self.assertEqual(objs[0].ech, 0)
        # self.assertEqual(objs[0].delta, -10)
        # self.assertEqual(objs[0].geom.geom_type, 'Polygon')
        # self.assertEqual(objs[0].geom.coords[0],
                         # ((6, 46), (7, 48), (8, 42), (6, 46)))




