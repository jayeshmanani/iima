import pandas as pd
import requests
import dbnomics
import pickle
import numpy as np
import datetime
import math 

'''

7) External debt stocks, total (DOD, current US$) - DT.DOD.DECT.CD
8) Exports of goods and services (current US$) - NE.EXP.GNFS.CD
9) Total reserves (includes gold, current US$) - FI.RES.TOTL.CD
10) GDP per capita (constant 2010 US$) - NY.GDP.PCAP.KD
11) Imports of goods and services (current US$) - NE.IMP.GNFS.CD
12) GDP growth (annual %) - NY.GDP.MKTP.KD.ZG
13) GNI per capita (constant 2010 US$) - NY.GNP.PCAP.KD
14) GDP (current US$) - NY.GDP.MKTP.CD

'''

def wb_data(year, indicatr):

  cr_yr_dict = {}
  before_1_yr_dict = {}
  before_2_yr_dict = {}
  before_3_yr_dict = {} 

  values_ed = []
  for i in range(6):
    try:
      dt0 = requests.get('http://api.worldbank.org/v2/country/all/indicator/'+indicatr+'?date='+str(year)+'&format=json&page='+str(i+1)).json()
    except:
      dt0 = None
    try:
      dt1 = requests.get('http://api.worldbank.org/v2/country/all/indicator/'+indicatr+'?date='+str(year-1)+'&format=json&page='+str(i+1)).json()
    except:
      dt1 = None
    try:
      dt2 = requests.get('http://api.worldbank.org/v2/country/all/indicator/'+indicatr+'?date='+str(year-2)+'&format=json&page='+str(i+1)).json()
    except:
      dt2 = None
    try:
      dt3 = requests.get('http://api.worldbank.org/v2/country/all/indicator/'+indicatr+'?date='+str(year-3)+'&format=json&page='+str(i+1)).json()
    except:
      dt3 = None

    if dt0 != None and dt0[0]['total']!=0:
      for item in dt0[1]:
        cr_yr_dict[item['country']['id']] = item['value']
    if dt1 != None and dt1[0]['total']!=0:
      for item in dt1[1]:
        before_1_yr_dict[item['country']['id']] = item['value']
    if dt2 != None and dt2[0]['total']!=0:
      for item in dt2[1]:
        before_2_yr_dict[item['country']['id']] = item['value']
    if dt3 != None and dt3[0]['total']!=0:
      for item in dt3[1]:
        before_3_yr_dict[item['country']['id']] = item['value']

  for cntry in final_df['country_id']:
    if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
      values_ed.append(cr_yr_dict[cntry])
    elif len(before_1_yr_dict)>0 and before_1_yr_dict[cntry] != None:
      values_ed.append(before_1_yr_dict[cntry])
    elif len(before_2_yr_dict)>0 and before_2_yr_dict[cntry] != None:
      values_ed.append(before_2_yr_dict[cntry])
    elif len(before_3_yr_dict) and before_3_yr_dict[cntry] != None:
      values_ed.append(before_3_yr_dict[cntry])
    else:
      values_ed.append(None)
  
  return values_ed