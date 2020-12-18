from django.http import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .functions import check_if_data, refresh_data #from firstUI.functions import check_if_data, refresh_data
import datetime
import pandas as pd
import numpy as np
from .models import FinanceData # from firstUI.models import FinanceData
from .models import Country # from firstUI.models import Country

d_wmap = pd.read_json('https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')

updated_data = 0

def indexPage(request):
    is_debt_distress = 1
    is_post = 0
    is_native_barp = 0
    global updated_data
    region_name = "Developing Countries"
    if updated_data == 1:
        alrt = 1
        updated_data = 0
    else:
        alrt = 0
    if request.method =='POST':
        is_post = 1
        # this is for the bar plot
        whc_plt = request.POST['which_plt'] 
        if whc_plt == 'bPlot':
            is_native_barp = 1    
            f_year = int(request.POST['year'])
            data = check_if_data(f_year)
            for_which = str(request.POST['barPlts'])
            rgn = request.POST['region']
            is_debt_distress = 1
            data = check_if_data(f_year)
            if 'show' in data.columns:
                data = data[data['show'] == True]
            country_name = []
            barplotVal = []

            if rgn == 'global':
                data = data
            elif rgn == 'eastAsia':
                data = data[data.region == "East Asia and Pacific"]
                region_name = "East Asia and Pacific"
            elif rgn == 'europe':
                data = data[data.region == "Europe and Central Asia"]
                region_name = "Europe and Central Asia"
            elif rgn == 'latinAmerica':
                data = data[data.region == "Latin America & the Caribbean"]
                region_name = "Latin America & the Caribbean"
            elif rgn == 'middleEast':
                data = data[data.region == "Middle East and North Africa"]
                region_name = "Middle East and North Africa"
            # elif rgn == 'northAmerica':
            #     data = data[data.region == "North America"]
            elif rgn == 'southAsia':
                data = data[data.region == "South Asia"]
                region_name = "South Asia"
            elif rgn == 'saharanAfrica':
                data = data[data.region == "Sub-Saharan Africa"]
                region_name = "Sub-Saharan Africa"

            if for_which == 'debtDistressProb':
                data = data[['country_name','Debt_Distress_prob']].sort_values(by=['Debt_Distress_prob'], ascending=False).dropna()
                country_name = data.country_name.to_list()
                barplotVal = data.Debt_Distress_prob.to_list()
                barplotVal = list(pd.Series(barplotVal).apply(lambda x: np.round(x, decimals=2)))
            elif for_which == 'specGradeProb':
                data = data[['country_name','Speculative_Grade_Prob']].sort_values(by=['Speculative_Grade_Prob'], ascending=False).dropna()
                country_name = data.country_name.to_list()
                barplotVal = data.Speculative_Grade_Prob.to_list()
                barplotVal = list(pd.Series(barplotVal).apply(lambda x: np.round(x, decimals=2)))
                is_debt_distress = 0

            dataForMapGraph = []
            f_year2 = datetime.date.today().year
            data2 = check_if_data(f_year2)
            if 'show' in data2.columns:
                data2 = data2[data2['show'] == True]
            data2 = data2[['country_code','Debt_Distress_prob']].rename(columns={'country_code':'code3','Debt_Distress_prob':'value'})
            is_spec_worldPlot = 0
            data2.value = data2.value * 100
            data2.value = data2.value.apply(lambda x: np.round(x, decimals=2))
            ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
            
            for i in range(len(ft)):
                dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                    "name": ft.iloc[i]['name'],
                    "value": ft.iloc[i]['value'],
                    "code": ft.iloc[i]['code']})

            context = {'region_name':region_name, 'alrt':alrt, 'is_native_barp':is_native_barp, 'is_post':is_post, 'is_debt_distress':is_debt_distress, 'barplotVal':barplotVal, 'country_name':country_name, 'year':f_year, 'is_spec_worldPlot':is_spec_worldPlot,'dataForMapGraph':dataForMapGraph} #, 'maxVal':maxVal}    
            # context = {'year':f_year, 'country_name':country_name, 'barplotVal':barplotVal, 'is_debt_distress':is_debt_distress}
        elif whc_plt == 'wPlot':
            which_wplot = str(request.POST['worldPlot'])
            f_year = int(request.POST['year'])
            data = check_if_data(f_year)
            if 'show' in data.columns:
                data = data[data['show'] == True]
            is_spec_worldPlot = 1
            dataForMapGraph = []

            if which_wplot == 'specGradeProb':
            # f_year = int(request.POST['year'])
                
                data.Speculative_Grade_Prob	= data.Speculative_Grade_Prob * 100
                data2 = data[['country_code','Speculative_Grade_Prob']].rename(columns={'country_code':'code3','Speculative_Grade_Prob':'value'})
                data2.value = data2.value.apply(lambda x: np.round(x, decimals=2))
                ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
                
                for i in range(len(ft)):
                    dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                        "name": ft.iloc[i]['name'],
                        "value": ft.iloc[i]['value'],
                        "code": ft.iloc[i]['code']})

            elif which_wplot == 'debtDistressProb':
                is_spec_worldPlot = 0
                data.Debt_Distress_prob = data.Debt_Distress_prob * 100
                data2 = data[['country_code','Debt_Distress_prob']].rename(columns={'country_code':'code3','Debt_Distress_prob':'value'})
                data2.value = data2.value.apply(lambda x: np.round(x, decimals=2))
                ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
                
                for i in range(len(ft)):
                    dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                        "name": ft.iloc[i]['name'],
                        "value": ft.iloc[i]['value'],
                        "code": ft.iloc[i]['code']})
            f_year2 = datetime.date.today().year
            data2 = check_if_data(f_year2)
            if 'show' in data2.columns:
                data2 = data2[data2['show'] == True]
            data2 = data2[['country_name','Debt_Distress_prob']].sort_values(by=['Debt_Distress_prob'], ascending=False).dropna()
            country_name2 = data2.country_name.to_list()
            debt_barplotVal2 = data2.Debt_Distress_prob.fillna(0).to_list()
            debt_barplotVal2 = list(pd.Series(debt_barplotVal2).apply(lambda x: np.round(x, decimals=2)))
            context = {'region_name':region_name, 'alrt':alrt, 'is_native_barp':is_native_barp, 'is_post':is_post, 'is_debt_distress':is_debt_distress, 'barplotVal':debt_barplotVal2, 'country_name':country_name2, 'year':f_year, 'is_spec_worldPlot':is_spec_worldPlot,'dataForMapGraph':dataForMapGraph} #, 'maxVal':maxVal}    
    else:
        f_year = datetime.date.today().year
        data = check_if_data(f_year)
        if 'show' in data.columns:
            data = data[data['show'] == True]
        dataForMapGraph = []
        data2 = data[['country_code','Debt_Distress_prob']].rename(columns={'country_code':'code3','Debt_Distress_prob':'value'})
        data = data[['country_name','Debt_Distress_prob']].sort_values(by=['Debt_Distress_prob'], ascending=False).dropna()
        country_name = data.country_name.to_list()
        debt_barplotVal = data.Debt_Distress_prob.fillna(0).to_list()
        debt_barplotVal = list(pd.Series(debt_barplotVal).apply(lambda x: np.round(x, decimals=2)))
        
        is_spec_worldPlot = 0
        data2.value = data2.value * 100
        data2.value = data2.value.apply(lambda x: np.round(x, decimals=2))
        ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
        
        for i in range(len(ft)):
            dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                "name": ft.iloc[i]['name'],
                "value": ft.iloc[i]['value'],
                "code": ft.iloc[i]['code']})
        context = {'region_name':region_name, 'alrt':alrt, 'is_native_barp':is_native_barp, 'is_post':is_post, 'is_debt_distress':is_debt_distress, 'barplotVal':debt_barplotVal, 'country_name':country_name, 'year':f_year, 'is_spec_worldPlot':is_spec_worldPlot,'dataForMapGraph':dataForMapGraph}    
        # context = {'year':f_year, 'country_name':country_name, 'barplotVal':debt_barplotVal, 'is_debt_distress':is_debt_distress}
    return render(request, 'index.html' , context=context)

def year(request):
    f_year = int(request.POST['year'])
    data = check_if_data(f_year)
    try:
        if 'show' in data.columns:
            data = data[data['show'] == True]
        data_as_str = data.applymap(str)
        html = data_as_str.to_html()
        text_file = open("firstUI/template/df.html", "w")
        text_file.write("{% extends 'base.html' %} {% block content %}")
        text_file.write(html)
        text_file.write("{% endblock %}")
        text_file.close()
        
        # context = {'year':f_year, 'html':html}    
        return render(request,'df.html')
    except:
        return render(request, 'index.html')

def graph(request):
    f_year = int(request.POST['year'])
    data = check_if_data(f_year)
    if 'show' in data.columns:
        data = data[data['show'] == True]
    data = data[['country_name','Debt_Distress_prob']].sort_values(by=['Debt_Distress_prob'], ascending=False).dropna()
    country_name = data.country_name.to_list()
    debt_barplotVal = data.Debt_Distress_prob.fillna(0).to_list()
    is_barPlot = True
    is_debt_distress = 1
    context = {'year':f_year, 'country_name':country_name, 'barplotVal':debt_barplotVal, 'is_barPlot':is_barPlot, 'is_debt_distress':is_debt_distress}
    return render(request, 'result.html', context)

def graph2(request):
    vals = str(request.GET['barPlts'])
    for_which = vals.split(',')[0]
    f_year = int(vals.split(',')[1])
    rgn = request.GET['region']
    is_barPlot = True
    is_debt_distress = 1
    data = check_if_data(f_year)
    if 'show' in data.columns:
        data = data[data['show'] == True]
    country_name = []
    barplotVal = []

    if rgn == 'global':
        data = data
    elif rgn == 'eastAsia':
        data = data[data.region == "East Asia and Pacific"]
    elif rgn == 'europe':
        data = data[data.region == "Europe and Central Asia"]
    elif rgn == 'latinAmerica':
        data = data[data.region == "Latin America & the Caribbean"]
    elif rgn == 'middleEast':
        data = data[data.region == "Middle East and North Africa"]
    elif rgn == 'northAmerica':
        data = data[data.region == "North America"]
    elif rgn == 'southAsia':
        data = data[data.region == "South Asia"]
    elif rgn == 'saharanAfrica':
        data = data[data.region == "Sub-Saharan Africa"]

    if for_which == 'debtDistressProb':
        data = data[['country_name','Debt_Distress_prob']].sort_values(by=['Debt_Distress_prob'], ascending=False).dropna()
        country_name = data.country_name.to_list()
        barplotVal = data.Debt_Distress_prob.to_list()
    elif for_which == 'specGradeProb':
        data = data[['country_name','Speculative_Grade_Prob']].sort_values(by=['Speculative_Grade_Prob'], ascending=False).dropna()
        country_name = data.country_name.to_list()
        barplotVal = data.Speculative_Grade_Prob.to_list()
        is_debt_distress = 0
    context = {'year':f_year, 'country_name':country_name, 'barplotVal':barplotVal, 'is_barPlot':is_barPlot, 'is_debt_distress':is_debt_distress}
    return render(request, 'result.html', context)

def worldPlot(request):
    vals = str(request.GET['worldPlot'])
    f_year = int(vals.split(',')[1])
    which_wplot = vals.split(',')[0]
    data = check_if_data(f_year)
    if 'show' in data.columns:
        data = data[data['show'] == True]
    is_spec_worldPlot = 1
    dataForMapGraph = []

    if which_wplot == 'specGradeProb':
    # f_year = int(request.POST['year'])
        
        data.Speculative_Grade_Prob	= data.Speculative_Grade_Prob * 100
        data2 = data[['country_code','Speculative_Grade_Prob']].rename(columns={'country_code':'code3','Speculative_Grade_Prob':'value'})
        ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
        # maxVal = ft['value'].max()
        
        for i in range(len(ft)):
            dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                "name": ft.iloc[i]['name'],
                "value": ft.iloc[i]['value'],
                "code": ft.iloc[i]['code']})

    elif which_wplot == 'debtDistressProb':
        is_spec_worldPlot = 0
        data.Debt_Distress_prob = data.Debt_Distress_prob * 100
        data2 = data[['country_code','Debt_Distress_prob']].rename(columns={'country_code':'code3','Debt_Distress_prob':'value'})
        ft = d_wmap.drop(columns=['value']).merge(data2, on='code3', how='left')[['code3','name','value','code']].fillna(0)
        # maxVal = ft['value'].max()
        
        for i in range(len(ft)):
            dataForMapGraph.append({"code3": ft.iloc[i]['code3'],
                "name": ft.iloc[i]['name'],
                "value": ft.iloc[i]['value'],
                "code": ft.iloc[i]['code']})

    context = {'year':f_year, 'is_spec_worldPlot':is_spec_worldPlot,'dataForMapGraph':dataForMapGraph} #, 'maxVal':maxVal}    
    return render(request, 'result.html', context)

def updateStatus(request):
    global updated_data
    if request.method =='POST':
        yr = int(request.POST['year'])
        yr -= 1
        cntr = request.POST['country']
        tf = request.POST['truef']
        if tf == "true":
            tf = True
        else:
            tf = False
        cnn = Country.objects.filter(country_name = cntr)
        for i in cnn:    
            cnn_id = i.id
        updated_data = 1
        FinanceData.objects.filter(data_year=yr, country_id=cnn_id).update(show=tf)
        # context = {'alrt':alrt}
        # return render(request, 'index.html',context)    
        return redirect(indexPage)
    else:
        country_l = list(Country.objects.all().values())
        context = {'country_l':country_l}
        return render(request,'updateStatus.html', context)

def pieChart(request):
    is_pie_Debt = 1
    country_l = list(Country.objects.all().values())
    debt_labels = ['External Debt/Exports', 'Realgdp_pc', 'Reserves/imports', 'Fiscalbalance/gdp', 'Political stability', 'Default history', 'Government effectiveness', 'Real GDP growth', 'Inflation'] #9 variable
    debt_data = [0.1601, 0.1534, 0.1141, 0.0681, 0.0374, 0.0479, 0.3417, 0.0143, 0.0631]
    labels = debt_labels
    data = debt_data
    fontColour = ["black"]
    fontColour = fontColour*10
    passed_cntr = 0
    context = {'is_pie_Debt':is_pie_Debt, 'labels':labels, 'data':data, 'fontColour':fontColour, 'country_l':country_l, 'passed_cntr':passed_cntr}
    
    if request.method == 'POST':
        passed_cntr = 1
        yr = int(request.POST['year'])
        # yr -= 1
        cntr = request.POST['country']
        cnn = Country.objects.filter(country_name = cntr)
        for i in cnn:    
            cnn_id = i.id
        # dtt = FinanceData.objects.filter(data_year=yr, country_id=cnn_id).get()
        dtt = check_if_data(yr)
        dtt = dtt[dtt.id == cnn_id]
        # print(dtt.country_name.values[0])
        # print(type(dtt.Speculative_Grade_Prob) == type(None))
        # print(dtt.Debt_Distress_prob)
        vals = request.POST['piePlts']
        if vals == 'specGradeProb':
            is_pie_Debt = 0
            spec_labels = ['LogrealGNI_pc', 'Savings/gdp', 'Rule of law', 'Govt gross debt'] #4 variable
            spec_data = [0.2483, 0.1514, 0.2925, 0.1199]
            
            # first model in spec grade
            # spec_val = dtt.Speculative_Grade_Prob.values[0]
            # if type(spec_val) != type(None) and str(spec_val) != 'nan':
            #     # print(spec_val)
            #     spec_data = list(np.array(spec_data) * spec_val)
            # data = spec_data # first model - multiple constant value by spec data value

            # second model in spec grade
            data2 = []
            spec_fetched = [dtt.log_real_gnipc, dtt.savings_gdp, dtt.rule_of_law, dtt.government_grossdebt_gdp]
            for enm, spc in enumerate(spec_fetched):
                if (type(spc.values[0]) != type(None)) and (str(spc.values[0]) != 'nan'):
                    print(spc.values[0])
                    data2.append(spec_data[enm] * spc.values[0])
                else:
                    data2.append(spec_data[enm])
            data = data2 #second model - individual values multiply
            
            labels = spec_labels

            print("This is spec data : ", data)

        elif vals == 'debtDistressProb':
            # first model in debt distress
            # if type(dtt.Debt_Distress_prob.values[0]) != type(None):
            #     # print(debt_data)
            #     debt_data = list(np.array(debt_data) * dtt.Debt_Distress_prob.values[0])
            # data = debt_data

            # second model in debt distress
            data2 = []
            debt_fetched = [dtt.externaldebt_exports, dtt.real_gdppc, dtt.reserves_import, dtt.fiscal_balance_gdp, dtt.political_stability, dtt.default_hist, dtt.govt_effectiveness, dtt.real_gdpgrowth, dtt.inflation_data]
            for enm, debt in enumerate(debt_fetched):
                if enm == 5:
                    if debt.values[0]:
                        data2.append(debt_data[enm] * 1)
                    else:
                        data2.append(debt_data[enm] * 0)
                elif (type(debt.values[0]) != type(None)) and (str(debt.values[0]) != 'nan'):
                    print(debt.values[0])
                    data2.append(debt_data[enm] * debt.values[0])
                else:
                    data2.append(debt_data[enm])
            data = data2 #second model - individual values multiply

            print("This is debt data : ",data)
        context = {'is_pie_Debt':is_pie_Debt, 'labels':labels, 'data':data, 'fontColour':fontColour, 'country_l':country_l, 'cntr':str(cntr), 'passed_cntr':passed_cntr, 'yr':yr}
    return render(request, 'pieChart.html', context=context)

def refreshData(request):
    if request.method == 'POST':
        f_year = int(request.POST['year'])
        tf_status = refresh_data(f_year)
        context = {'tf_status':tf_status}
    else:
        context = {'tf_statis':0}
    return render(request, 'index.html', context)
    


