from operator import index
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
from firstUI.models import FinanceData
from firstUI.models import Country
import sqlite3



THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'data/new_final_df.pkl')

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
    month = datetime.datetime.today().month
    if month >=10 or month < 4:
        month = '10'
    elif month >= 4 or month < 10:
        month = '04'

    data = dbnomics.fetch_series("IMF", f'WEO:{year}-{month}', series_code=sr_code, max_nb_series=1000)

    current_year_data = data.query('period=='+str(year))
    before_1_year_data = data.query('period=='+str(year-1))
    # before_2_year_data = data.query('period=='+str(year-2))
    # before_3_year_data = data.query('period=='+str(year-3))

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
        # cd3 = before_2_year_data[before_2_year_data['weo-country'] == country]
        # cd4 = before_3_year_data[before_3_year_data['weo-country'] == country]
        if cd1.empty:
            v1 = [None,None,None,None,None]
        else:
            v1 = list(cd1['value'].values)
        if cd2.empty:
            v2 = [None,None,None,None,None]
        else:
            v2 = list(cd2['value'].values)

        for num, ver in enumerate([v1,v2]):
            if ver[0] == None or str(ver[0]) == 'nan':
                if num ==1:
                    dict_values_ggxc[country] = ver[0]  
                else:
                    continue
            else:
                dict_values_ggxc[country] = ver[0]
                break

        for num, ver in enumerate([v1,v2]):
            if ver[1] == None or str(ver[1]) == 'nan':
                if num ==1:
                    dict_values_ggxw[country] = ver[1]
                else:
                    continue
            else:
                dict_values_ggxw[country] = ver[1]
                break

        for num, ver in enumerate([v1,v2]):
            if ver[2] == None or str(ver[2]) == 'nan':
                if num ==1:
                    dict_values_ngsd[country] = ver[2]
                else:
                    continue
            else:
                dict_values_ngsd[country] = ver[2]
                break

        for num, ver in enumerate([v1,v2]):
            if ver[3] == None or str(ver[3]) == 'nan':
                if num ==1:
                    dict_values_pcpi[country] = ver[3]
                else:
                    continue
            else:
                dict_values_pcpi[country] = ver[3]
                break

        for num, ver in enumerate([v1,v2]):
            if ver[4] == None or str(ver[4]) == 'nan':
                if num ==1:
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

        if dt0 != None and dt0[0]['total']!=0:
            for item in dt0[1]:
                cr_yr_dict[item['country']['id']] = item['value']
        if dt1 != None and dt1[0]['total']!=0:
            for item in dt1[1]:
                before_1_yr_dict[item['country']['id']] = item['value']

    for cntry in final_df['country_id']:
        if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
            values_ed.append(cr_yr_dict[cntry])
        elif len(before_1_yr_dict)>0 and before_1_yr_dict[cntry] != None:
            values_ed.append(before_1_yr_dict[cntry])
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
    # before_2_yr_dict = {}
    # before_3_yr_dict = {} 
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
        
        if dt0 != None:
            for item in dt0['source']['data']:
                cr_yr_dict[item['variable'][0]['id']] = item['value']
        if dt1 != None:
            for item in dt1['source']['data']:
                before_1_yr_dict[item['variable'][0]['id']] = item['value']
        
    for cntry in final_df['country_code']:
        if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
            # values_ed[cntry] = cr_yr_dict[cntry]
            values_ed.append(cr_yr_dict[cntry])
        elif len(before_1_yr_dict)>0 and before_1_yr_dict[cntry] != None:
            # values_ed[cntry] = before_1_yr_dict[cntry]
            values_ed.append(before_1_yr_dict[cntry])
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
        
        if dt0 != None:
            for item in dt0['source']['data']:
                cr_yr_dict[item['variable'][0]['id']] = item['value']
        if dt1 != None:
            for item in dt1['source']['data']:
                before_1_yr_dict[item['variable'][0]['id']] = item['value']
        
    for cntry in final_df['country_code']:
        if len(cr_yr_dict)>0 and cr_yr_dict[cntry] != None:
            # values_ed[cntry] = cr_yr_dict[cntry]
            values_ed.append(cr_yr_dict[cntry])
        elif len(before_1_yr_dict)>0 and before_1_yr_dict[cntry] != None:
            values_ed.append(before_1_yr_dict[cntry])
        else:
            values_ed.append(None)
    return values_ed

'''
    Fetch_data function fetches all the data and returns values by combining all the values
'''

clms = ['fiscal_balance_gdp', 'government_grossdebt_gdp', 'inflation_data', 'exports_growth', 'savings_gdp', 'externaldebt',
               'exports', 'reserves', 'real_gdppc', 'imports', 'real_gdpgrowth', 'real_gnipc', 'nominal_gdp', 'political_stability', 'rule_of_law',
               'govt_effectiveness', 'm3_gdp'] #, 'reer']

def fetch_data(year):
    s_time = time.time()
    try:
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
            # final_dfd['externaldebt/exports'] = (final_dfd['externaldebt'].fillna(0)/final_dfd['exports'].fillna(0))*100
            final_dfd['reserves/import'] = (final_dfd['reserves']/final_dfd['imports'])*100
            # final_dfd['reserves/import'] = (final_dfd['reserves'].fillna(0)/final_dfd['imports'].fillna(0))*100
            final_dfd['reserves/gdp'] = (final_dfd['reserves']/final_dfd['nominal_gdp'])*100
            # final_dfd['reserves/gdp'] = (final_dfd['reserves'].fillna(0)/final_dfd['nominal_gdp'].fillna(0))*100
            final_dfd['log_real_gnipc'] = final_dfd['real_gnipc'].apply(lambda x: math.log(x))
            # final_dfd['log_real_gnipc'] = final_dfd['real_gnipc'].fillna(0).apply(lambda x: math.log(x))
            final_dfd['predicted_specgrade'] = (final_dfd['log_real_gnipc']*(-5.3914)+final_dfd['savings_gdp']*(-0.1321)+final_dfd['rule_of_law']*(-4.9736)+final_dfd['government_grossdebt_gdp']*(0.1253)+46.7664)/math.sqrt(1+(7.463)**2)
            # final_dfd['predicted_specgrade'] = (final_dfd['log_real_gnipc'].fillna(0)*(-5.3914)+final_dfd['savings_gdp'].fillna(0)*(-0.1321)+final_dfd['rule_of_law'].fillna(0)*(-4.9736)+final_dfd['government_grossdebt_gdp'].fillna(0)*(0.1253)+46.7664)/math.sqrt(1+(7.463)**2)
            final_dfd['Speculative_Grade_Prob'] = final_dfd['predicted_specgrade'].apply(lambda x: math.exp(x)/(1+math.exp(x)))
            # final_dfd['Speculative_Grade_Prob'] = final_dfd['predicted_specgrade'].fillna(0).apply(lambda x: math.exp(x)/(1+math.exp(x)))
            final_dfd['y_hat'] = final_dfd['externaldebt/exports']*( -0.0081)+final_dfd['real_gdppc']*(0.0005)+final_dfd['reserves/import']*(0.02867)+final_dfd['fiscal_balance_gdp']*(0.06526)+final_dfd['political_stability']*(1.09237)+final_dfd['default_hist']*(-0.50728)+final_dfd['govt_effectiveness']*(1.3579)+final_dfd['real_gdpgrowth']*(0.09908)+final_dfd['inflation_data']*(-0.03967)
            # final_dfd['y_hat'] = final_dfd['externaldebt/exports'].fillna(0)*( -0.0081)+final_dfd['real_gdppc'].fillna(0)*(0.0005)+final_dfd['reserves/import'].fillna(0)*(0.02867)+final_dfd['fiscal_balance_gdp'].fillna(0)*(0.06526)+final_dfd['political_stability'].fillna(0)*(1.09237)+final_dfd['default_hist'].fillna(0)*(-0.50728)+final_dfd['govt_effectiveness'].fillna(0)*(1.3579)+final_dfd['real_gdpgrowth'].fillna(0)*(0.09908)+final_dfd['inflation_data'].fillna(0)*(-0.03967)
            final_dfd['(Threshold_Yhat)/sigma']= final_dfd['y_hat'].apply(lambda x: ((-5.2355)-x)/math.sqrt(27.252))
            # final_dfd['(Threshold_Yhat)/sigma']= final_dfd['y_hat'].fillna(0).apply(lambda x: ((-5.2355)-x)/math.sqrt(27.252))
            final_dfd['Debt_Distress_prob'] = final_dfd['(Threshold_Yhat)/sigma'].apply(lambda x: math.exp(x)/(1+math.exp(x)))
            # final_dfd['Debt_Distress_prob'] = final_dfd['(Threshold_Yhat)/sigma'].fillna(0).apply(lambda x: math.exp(x)/(1+math.exp(x)))
            ray.shutdown()
            print("Process time: {}".format(time.time() - s_time))

            return final_dfd 
        else:
            print("The Year You have Passed is in Future, Please use the Current Year or Past Year for Made this Working")
    except:
        print("Some Error Occured")
        ray.shutdown()
    finally:
        ray.shutdown()

def check_if_data(year):
    year = year - 1

    # my_data_folder = os.path.join(THIS_FOLDER, 'data')
    # data_file = my_data_folder+"/"+str(year)+".pkl"

    cnt = FinanceData.objects.filter(data_year=year, show=True).count()
    # print(cnt)
    if cnt >0:
        df = pd.DataFrame(list(FinanceData.objects.filter(data_year=year, show=True).all().values()))
        df.drop(columns=['id'], inplace=True)
        df.rename(columns={'country_id_id':'id'}, inplace=True)
        df2 = pd.DataFrame(list(Country.objects.all().values()))
        data = pd.merge(df2,df,how='outer', on='id')
        # return data
    else:
        print("Data is not there so, fetching from API's")
        data = fetch_data(year)
        
        # data.to_pickle(data_file)
        
        dts = data.values
        for enm, test in enumerate(dts):    
            cnn = Country.objects.filter(country_name = test[2])
            # try:
            #     cnn2 = FinanceData.objects.filter(country_id=cnn.get(), data_year=year).get()
            # except:
            fn, created  = FinanceData.objects.update_or_create(country_id=cnn.get(),
                        data_year = year,
                        fiscal_balance_gdp = test[5],
                        government_grossdebt_gdp = test[6],
                        inflation_data = test[7],
                        exports_growth = test[8],
                        savings_gdp = test[9],
                        externaldebt = test[10],
                        exports = test[11],
                        reserves = test[12],
                        real_gdppc = test[13],
                        imports = test[14],
                        real_gdpgrowth = test[15],
                        real_gnipc = test[16],
                        nominal_gdp = test[17],
                        political_stability = test[18],
                        rule_of_law = test[19],
                        govt_effectiveness = test[20],
                        m3_gdp = test[21],
                        externaldebt_exports = test[22],
                        reserves_import = test[23],
                        reserves_gdp = test[24],
                        log_real_gnipc = test[25],
                        predicted_specgrade = test[26],
                        Speculative_Grade_Prob = test[27],
                        y_hat = test[28],
                        Threshold_Yhat_sigma = test[29],
                        Debt_Distress_prob = test[30],
                        show = True                                                                                            
                        )  
            fn.save()
    return data

def refresh_data(year):
    year = year - 1
    c_year = datetime.datetime.today().year 
    # try:
    if year in [c_year, c_year-1, c_year-2, c_year-3, c_year-4, c_year-5]:
        print("Refreshing the Data for Year, {}".format(year+1))
        data = fetch_data(year)
        dts = data.values

        for enm, test in enumerate(dts):    
            print("enm is {} and data value is {}".format(enm, test))
            cnn = Country.objects.filter(country_name = test[2])
            print("cnn is {}".format(cnn))
            print("cnn value is {}".format(cnn.get()))
        #     fn, created  = FinanceData.objects.update(country_id=cnn.get(),
        #                 data_year = year,
        #                 fiscal_balance_gdp = test[5],
        #                 government_grossdebt_gdp = test[6],
        #                 inflation_data = test[7],
        #                 exports_growth = test[8],
        #                 savings_gdp = test[9],
        #                 externaldebt = test[10],
        #                 exports = test[11],
        #                 reserves = test[12],
        #                 real_gdppc = test[13],
        #                 imports = test[14],
        #                 real_gdpgrowth = test[15],
        #                 real_gnipc = test[16],
        #                 nominal_gdp = test[17],
        #                 political_stability = test[18],
        #                 rule_of_law = test[19],
        #                 govt_effectiveness = test[20],
        #                 m3_gdp = test[21],
        #                 externaldebt_exports = test[22],
        #                 reserves_import = test[23],
        #                 reserves_gdp = test[24],
        #                 log_real_gnipc = test[25],
        #                 predicted_specgrade = test[26],
        #                 Speculative_Grade_Prob = test[27],
        #                 y_hat = test[28],
        #                 Threshold_Yhat_sigma = test[29],
        #                 Debt_Distress_prob = test[30],
        #                 show = True                                                                                            
        #                 )  
        #     fn.save()
        print("Refreshed the Data for {}".format(year+1))
    else:
        print("The data can't be Refreshed as it is not of Last Three Years")
    # return 1
    return
    # except:
    #     print("Some Error Occured While Refreshing the Data for Year {}".format(year+1))
    #     return 0