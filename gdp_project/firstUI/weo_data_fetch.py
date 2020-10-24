import pandas as pd
import requests
import dbnomics
import pickle
import numpy as np
import datetime
import math 

# final_df = pd.read_pickle('new_final_df.pkl')

''' 

weo_data() function can fetch the data for Following variables

1) General government net lending/borrowing - GGXCNL_NGDP
2) General government gross debt - GGXWDG_NGDP
3) Inflation, average consumer prices	- PCPIPCH
4) Volume of exports of goods and services - TX_RPCH
5) Gross national savings	= NGSD_NGDP

returns as list contains values as follows in sequence [GGXCNL_NGDP, GGXWDG_NGDP, NGSD_NGDP, PCPIPCH, TX_RPCH]

'''

def weo_data(year):
  values_ed = []
  country_string = ''
  for country in final_df['country_code']:
    country_string+="+"+country
  country_string = country_string[1:]

  fnc = 'GGXCNL_NGDP+GGXWDG_NGDP+PCPIPCH+TX_RPCH+NGSD_NGDP'
  sr_code = country_string+'.'+fnc

  data = dbnomics.fetch_series("IMF", "WEO", series_code=sr_code, max_nb_series=1000)

  current_year_data = data.query('period=='+str(year))
  before_1_year_data = data.query('period=='+str(year-1))
  before_2_year_data = data.query('period=='+str(year-2))
  before_3_year_data = data.query('period=='+str(year-3))

  '''
  country_name as key and values as list contains [GGXCNL_NGDP, GGXWDG_NGDP, NGSD_NGDP, PCPIPCH, TX_RPCH]
  '''

  dict_values_ggxc = {}
  dict_values_ggxw = {}
  dict_values_ngsd = {}
  dict_values_pcpi = {}
  dict_values_txrp = {}


  vlist1 = []
  vlist2 = []
  vlist3 = []
  vlist4 = []
  vlist5 = []

  for country in final_df.country_code:
    cd1 = current_year_data[current_year_data['weo-country'] == country]
    cd2 = before_1_year_data[before_1_year_data['weo-country'] == country]
    cd3 = before_2_year_data[before_2_year_data['weo-country'] == country]
    cd4 = before_3_year_data[before_3_year_data['weo-country'] == country]
    if cd1.empty:
      v1 = [None,None,None,None,None]
    else:
      v1 = list(cd1['value'].values)
    if cd2.empty:
      v2 = [None,None,None,None,None]
    else:
      v2 = list(cd2['value'].values)
    if cd3.empty:
      v3 = [None,None,None,None,None]
    else:
      v3 = list(cd3['value'].values)
    if cd4.empty:
      v4 = [None,None,None,None,None]
    else:
      v4 = list(cd4['value'].values)

    for num, ver in enumerate([v1,v2,v3,v4]):
      if ver[0] == None or str(ver[0]) == 'nan':
        if num ==3:
          dict_values_ggxc[country] = ver[0]  
        else:
          continue
      else:
        dict_values_ggxc[country] = ver[0]
        break

    for num, ver in enumerate([v1,v2,v3,v4]):
      if ver[1] == None or str(ver[1]) == 'nan':
        if num ==3:
          dict_values_ggxw[country] = ver[1]
        else:
          continue
      else:
        dict_values_ggxw[country] = ver[1]
        break

    for num, ver in enumerate([v1,v2,v3,v4]):
      if ver[2] == None or str(ver[2]) == 'nan':
        if num ==3:
          dict_values_ngsd[country] = ver[2]
        else:
          continue
      else:
        dict_values_ngsd[country] = ver[2]
        break

    for num, ver in enumerate([v1,v2,v3,v4]):
      if ver[3] == None or str(ver[3]) == 'nan':
        if num ==3:
          dict_values_pcpi[country] = ver[3]
        else:
          continue
      else:
        dict_values_pcpi[country] = ver[3]
        break

    for num, ver in enumerate([v1,v2,v3,v4]):
      if ver[4] == None or str(ver[4]) == 'nan':
        if num ==3:
          dict_values_txrp[country] = ver[4]
        else:
          continue
      else:
        dict_values_txrp[country] = ver[4]
        break

    vlist1.append(dict_values_ggxc[country])
    vlist2.append(dict_values_ggxw[country])
    vlist3.append(dict_values_ngsd[country])
    vlist4.append(dict_values_pcpi[country])
    vlist5.append(dict_values_txrp[country])

  return [vlist1, vlist2, vlist3, vlist4, vlist5]