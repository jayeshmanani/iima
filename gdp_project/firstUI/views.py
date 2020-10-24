from django.shortcuts import render
import pandas as pd
import requests
import dbnomics
import pickle
import numpy as np
import datetime
import math 
from firstUI.functions import fetch_data, check_if_data
from django import forms

# Create your views here.

df3 = pd.read_json('https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')
def indexPage(request):
    year = 2020
    data = check_if_data(year)
    country_name = data.country_name.to_list()
    barvalues = data.Prob_out_1.fillna(0).to_list()
    dataForMap = mapDataCal(data)
    showMap = 'True'
    context = {'year':year, 'CountryNames': country_name, 'BarplotVal':barvalues, 'dataForMap':dataForMap, 'showMap':showMap}    
    return render(request,'index.html',context) 

def mapDataCal(data_value):
    dataForMaps = []
    dataForMaps = []
    for i in data_value[['country_code','country_name','Prob_out_1','country_id']].fillna(0).values:
        try:
            temp_dc = {}
            temp_df = df3[df3['code3'] == i[0]]
            temp_dc['code3'] = temp_df['code3'].values[0]
            temp_dc['name'] = temp_df['name'].values[0]
            temp_dc['value'] = i[2]
            temp_dc['code'] = temp_df['code'].values[0]
            dataForMaps.append(temp_dc)
        except:
            pass
    return dataForMaps

def indiCountryData(request):
    year = 2020
    data = check_if_data(year)
    country_name = data.country_name.to_list()
    barvalues = data.Prob_out_1.fillna(0).to_list()
    showMap = 'False'
    context = {'year':year, 'CountryNames': country_name, 'BarplotVal':barvalues, 'showMap':showMap}   

class year_dropdown(forms.Form):
    year_dropdown_list = []
    for y in range(1960, (datetime.datetime.now().year)):
        year_dropdown_list.append((y))
    todays_date= forms.IntegerField(label="You want Data for Year?", widget=forms.Select(choices=year_dropdown_list))

