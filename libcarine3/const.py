#!/usr/bin/env python3
# coding: utf-8

"""Carine v3 :: definitions."""


NO2 = 1
O3 = 2
PM10 = 3
PM25 = 4
IQA = 10


POLLUTANTS = [NO2, O3, PM10, PM25, IQA]


VLS = {NO2: 200, O3: 180, PM10: 50}


def from_name(name):
    """Constante from pollutant name."""
    if name == 'NO2':
        return NO2
    elif name == 'O3':
        return O3
    elif name == 'PM10':
        return PM10
    elif name == 'PM25' or name == 'PM2.5':
        return PM25
    elif name == 'IQA':
        return IQA
    return None
