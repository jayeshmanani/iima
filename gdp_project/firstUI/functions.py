import pandas as pd
import requests
import dbnomics
import pickle
import numpy as np
import datetime
import math 
import os
import ray
import time
from os import path

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'new_final_df.pkl')

final_df = pd.read_pickle(my_file)


''' 

weo_data() function can fetch the data for Following variables

1) General government net lending/borrowing - GGXCNL_NGDP
2) General government gross debt - GGXWDG_NGDP
3) Inflation, average consumer prices	- PCPIPCH
4) Volume of exports of goods and services - TX_RPCH
5) Gross national savings	= NGSD_NGDP

returns as list contains values as follows in sequence [GGXCNL_NGDP, GGXWDG_NGDP, NGSD_NGDP, PCPIPCH, TX_RPCH]

'''
@ray.remote
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
@ray.remote
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


'''

15) Political Stability Estimate - PV.EST
16) Rule of Law Estimate - RL.EST
17) Govt Effectiveness Estimate - GE.EST

'''
@ray.remote
def pol_data(year, indicatr):
    cr_yr_dict = {}
    before_1_yr_dict = {}
    before_2_yr_dict = {}
    before_3_yr_dict = {} 
    values_ed = []
    for i in range(5):
        try:
            dt0 = requests.get('http://api.worldbank.org/v2/sources/3/country/all/series/'+indicatr+'/time/yr'+str(year)+'?format=json&page='+str(i+1)).json()
        except:
            dt0 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year, i+1))
        try:
            dt1 = requests.get('http://api.worldbank.org/v2/sources/3/country/all/series/'+indicatr+'/time/yr'+str(year-1)+'?format=json&page='+str(i+1)).json()
        except:
            dt1 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-1, i+1))
        try:
            dt2 = requests.get('http://api.worldbank.org/v2/sources/3/country/all/series/'+indicatr+'/time/yr'+str(year-2)+'?format=json&page='+str(i+1)).json()
        except:
            dt2 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-2, i+1))
        try:
            dt3 = requests.get('http://api.worldbank.org/v2/sources/3/country/all/series/'+indicatr+'/time/yr'+str(year-3)+'?format=json&page='+str(i+1)).json()
        except:
            dt3 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-3, i+1))
        
        if dt0 != None:
            for item in dt0['source']['data']:
                cr_yr_dict[item['variable'][0]['id']] = item['value']
        if dt1 != None:
            for item in dt1['source']['data']:
                before_1_yr_dict[item['variable'][0]['id']] = item['value']
        if dt2 != None:
            for item in dt2['source']['data']:
                before_2_yr_dict[item['variable'][0]['id']] = item['value']
        if dt3 != None:
            for item in dt3['source']['data']:
                before_3_yr_dict[item['variable'][0]['id']] = item['value']
        
    for cntry in final_df['country_code']:
        if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
            # values_ed[cntry] = cr_yr_dict[cntry]
            values_ed.append(cr_yr_dict[cntry])
        elif len(before_1_yr_dict)>0 and before_1_yr_dict[cntry] != None:
            # values_ed[cntry] = before_1_yr_dict[cntry]
            values_ed.append(before_1_yr_dict[cntry])
        elif len(before_2_yr_dict)>0 and before_2_yr_dict[cntry] != None:
            values_ed.append(before_2_yr_dict[cntry])
        elif len(before_3_yr_dict) and before_3_yr_dict[cntry] != None:
            values_ed.append(before_3_yr_dict[cntry])
        else:
            values_ed.append(None)
    return values_ed


'''

15) Liquid Liabilities to GDP - GFDD.DI.05

'''
@ray.remote
def LL_GDP_data(year):
    indicatr = 'GFDD.DI.05'
    cr_yr_dict = {}
    before_1_yr_dict = {}
    before_2_yr_dict = {}
    before_3_yr_dict = {} 
    values_ed = []
    for i in range(5):
        try:
            dt0 = requests.get('http://api.worldbank.org/v2/sources/32/country/all/series/GFDD.DI.05/time/yr'+str(year)+'?format=json&page='+str(i+1)).json()
        except:
            dt0 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year, i+1))
        try:
            dt1 = requests.get('http://api.worldbank.org/v2/sources/32/country/all/series/GFDD.DI.05/time/yr'+str(year-1)+'?format=json&page='+str(i+1)).json()
        except:
            dt1 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-1, i+1))
        try:
            dt2 = requests.get('http://api.worldbank.org/v2/sources/32/country/all/series/GFDD.DI.05/time/yr'+str(year-2)+'?format=json&page='+str(i+1)).json()
        except:
            dt2 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-2, i+1))
        try:
            dt3 = requests.get('http://api.worldbank.org/v2/sources/32/country/all/series/GFDD.DI.05/time/yr'+str(year-3)+'?format=json&page='+str(i+1)).json()
        except:
            dt3 = None
            print("No data available for {} for year {} in page {}".format(indicatr, year-3, i+1))
        
        if dt0 != None:
            for item in dt0['source']['data']:
                cr_yr_dict[item['variable'][0]['id']] = item['value']
        if dt1 != None:
            for item in dt1['source']['data']:
                before_1_yr_dict[item['variable'][0]['id']] = item['value']
        if dt2 != None:
            for item in dt2['source']['data']:
                before_2_yr_dict[item['variable'][0]['id']] = item['value']
        if dt3 != None:
            for item in dt3['source']['data']:
                before_3_yr_dict[item['variable'][0]['id']] = item['value']
        
    for cntry in final_df['country_code']:
        if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
            # values_ed[cntry] = cr_yr_dict[cntry]
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


# ''' 

# 16) Exchange Rates, Real Effective Exchange Rate based on Consumer Price Index, Index - EREER_IX

# '''
# @ray.remote
# def EREER_IX_data(year):
#     fnc = 'EREER_IX'
#     values_ed = []

#     sr_code = 'A..'+fnc
#     data = dbnomics.fetch_series("IMF", "IFS", series_code=sr_code, max_nb_series=1000)

#     current_year_data = data.query('period=='+str(year))
#     before_1_year_data = data.query('period=='+str(year-1))
#     before_2_year_data = data.query('period=='+str(year-2))
#     before_3_year_data = data.query('period=='+str(year-3))

#     for country in final_df.country_id:
#         country_data = current_year_data[current_year_data['REF_AREA'] == country]
#         if country_data.empty:
#             value = None
#         else:
#             ind = country_data.index[0]
#         value = country_data['value'][ind]

#         if str(value) == 'nan' or type(value) == type(None):
#             print("Could Not Find the Data {} for year {} for country {}".format(fnc, year, country))
#             print("Try to Fetching the Data {} for year {} for country {}".format(fnc, year-1, country))
#             country_data = before_1_year_data[before_1_year_data['REF_AREA'] == country]
#             if country_data.empty:
#                 value = None
#             else:
#                 ind = country_data.index[0]
#                 value = country_data['value'][ind]
        
#             if str(value) == 'nan' or type(value) == type(None):
#                 print("Could Not Find the Data {} for year {} for country {}".format(fnc, year-1, country))
#                 print("Try to Fetching the Data {} for year {} for country {}".format(fnc, year-2, country))
#                 country_data = before_2_year_data[before_2_year_data['REF_AREA'] == country]
#                 if country_data.empty:
#                     value = None
#                 else:
#                     ind = country_data.index[0]
#                 value = country_data['value'][ind]
            
#                 if str(value) == 'nan' or type(value) == type(None):
#                     print("Could Not Find the Data {} for year {} for country {}".format(fnc, year-2, country))
#                     print("Try to Fetching the Data {} for year {} for country {}".format(fnc, year-3, country))
#                     country_data = before_3_year_data[before_3_year_data['REF_AREA'] == country]
#                     if country_data.empty:
#                         value = None
#                     else:
#                         ind = country_data.index[0]
#                         value = country_data['value'][ind]

#                     if str(value) == 'nan' or type(value) == type(None):
#                         print("Could Not Find the Data {} for year {} for country {}".format(fnc, year-3, country))
#                         values_ed.append(value)
#                     else:
#                         values_ed.append(value)
#                 else:
#                     values_ed.append(value)
#             else:
#                 values_ed.append(value)
#         else:
#             values_ed.append(value)
#     return values_ed


'''
    Fetch_data function fetches all the data and returns values by combining all the values
'''

clms = ['fiscal_balance_gdp', 'government_grossdebt_gdp', 'inflation_data', 'exports_growth', 'savings_gdp', 'externaldebt',
               'exports', 'reserves', 'real_gdppc', 'imports', 'real_gdpgrowth', 'real_gnipc', 'nominal_gdp', 'political_stability', 'rule_of_law',
               'govt_effectiveness', 'm3_gdp'] #, 'reer']

def fetch_data(year):
    s_time = time.time()
    ray.init()
    c_year = datetime.datetime.today().year 
    # year = year - 1
    final_dfd = pd.read_pickle(my_file)
    if c_year >= year:
        ret_id1 = weo_data.remote(year)
        ret_id2 = wb_data.remote(year, 'DT.DOD.DECT.CD')
        ret_id3 = wb_data.remote(year, 'NE.EXP.GNFS.CD')
        ret_id4 = pol_data.remote(year, 'PV.EST')
        ret_id5 = wb_data.remote(year, 'FI.RES.TOTL.CD')
        ret_id6 = wb_data.remote(year, 'NY.GDP.PCAP.KD')
        ret_id7 = pol_data.remote(year, 'RL.EST')
        ret_id8 = wb_data.remote(year, 'NE.IMP.GNFS.CD')
        ret_id9 = wb_data.remote(year, 'NY.GDP.MKTP.KD.ZG')
        ret_id10 = pol_data.remote(year, 'GE.EST')

        ret_id11 = wb_data.remote(year, 'NY.GNP.PCAP.KD')
        ret_id12 = wb_data.remote(year, 'NY.GDP.MKTP.CD')

        ret_id13 = LL_GDP_data.remote(year)

        [fiscal_balance_gdp, government_grossdebt_gdp, savings_gdp, inflation_data, exports_growth], externaldebt, exports, political_stability, reserves, real_gdppc, rule_of_law, imports, real_gdpgrowth, govt_effectiveness, real_gnipc, nominal_gdp, m3_gdp = ray.get([ret_id1, ret_id2, ret_id3, ret_id4, ret_id5, ret_id6, ret_id7, ret_id8, ret_id9, ret_id10, ret_id11, ret_id12, ret_id13])

        lt_118 = []
        ind_lst = [fiscal_balance_gdp, government_grossdebt_gdp, inflation_data, exports_growth, savings_gdp, externaldebt,
                exports, reserves, real_gdppc, imports, real_gdpgrowth, real_gnipc, nominal_gdp, political_stability, rule_of_law,
                govt_effectiveness, m3_gdp] #, reer]

        for nm, indctr in enumerate(ind_lst):
            if len(indctr) < 118:
                lt_118.append(clms[nm])
    
        for col,vals in zip(clms, ind_lst):
            if vals not in lt_118:
                final_dfd[col] = vals
        
        final_dfd['externaldebt/exports'] = (final_dfd['externaldebt']/final_dfd['exports'])*100
        final_dfd['reserves/import'] = (final_dfd['reserves']/final_dfd['imports'])*100
        final_dfd['reserves/gdp'] = (final_dfd['reserves']/final_dfd['nominal_gdp'])*100
        final_dfd['log_real_gnipc'] = final_dfd['real_gnipc'].apply(lambda x: math.log(x))
        final_dfd['predicted_specgrade'] = (final_dfd['log_real_gnipc']*(-5.3914)+final_dfd['savings_gdp']*(-0.1321)+final_dfd['rule_of_law']*(-4.9736)+final_dfd['government_grossdebt_gdp']*(0.1253)+46.7664)/math.sqrt(1+(7.463)**2)
        final_dfd['prob_specgrade=1'] = final_dfd['predicted_specgrade'].apply(lambda x: math.exp(x)/(1+math.exp(x)))
        final_dfd['y_hat'] = final_dfd['externaldebt/exports']*( -0.0081)+final_dfd['real_gdppc']*(0.0005)+final_dfd['reserves/import']*(0.02867)+final_dfd['fiscal_balance_gdp']*(0.06526)+final_dfd['political_stability']*(1.09237)+final_dfd['default_hist']*(-0.50728)+final_dfd['govt_effectiveness']*(1.3579)+final_dfd['real_gdpgrowth']*(0.09908)+final_dfd['inflation_data']*(-0.03967)
        final_dfd['(Threshold_Yhat)/sigma']= final_dfd['y_hat'].apply(lambda x: ((-5.2355)-x)/math.sqrt(27.252))
        final_dfd['Prob_out_1'] = final_dfd['(Threshold_Yhat)/sigma'].apply(lambda x: math.exp(x)/(1+math.exp(x)))
        ray.shutdown()
        print("Process time: {}".format(time.time() - s_time))
        return final_dfd 
    else:
        print("The Year You have Passed is in Future, Please use the Current Year or Past Year for Made this Working")


def check_if_data(year):
    year = year - 1

    my_data_folder = os.path.join(THIS_FOLDER, 'data')
    data_file = my_data_folder+"/"+str(year)+".pkl"

    if path.exists(data_file):
        data = pd.read_pickle(data_file)
    else:
        print("Data is not there so, fetching from API's")
        data = fetch_data(year)
        data.to_pickle(data_file)
    
    return data



