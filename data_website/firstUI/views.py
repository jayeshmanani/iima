from django.http import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from firstUI.functions import check_if_data, refresh_data
import datetime
import pandas as pd
from firstUI.models import FinanceData
from firstUI.models import Country


d_wmap = pd.read_json('https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')

def indexPage(request):
    # tf_status = 0
    # cntry = Country.objects.all()
    # country_list = []
    # for i in cntry:
    #     country_list.append(i.country_name)
    # context = {'country_list':country_list, 'tf_status':tf_status}
    return render(request, 'index.html') #, context)

def year(request):
    f_year = int(request.POST['year'])
    data = check_if_data(f_year)
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
        alrt = 1
        FinanceData.objects.filter(data_year=yr, country_id=cnn_id).update(show=tf)
        context = {'alrt':alrt}
        return render(request, 'index.html',context)    
    else:
        country_l = list(Country.objects.all().values())
        context = {'country_l':country_l}
        return render(request,'updateStatus.html', context)

def pieChart(request):
    is_pie_Debt = 1
    debt_labels = ['L.totexp~p','L.realgd~c','L.totres~p','L.fiscal~o','L.pv_est','dum_def_~5','L.ge_est','L.realgd~r','L.cpich~o'] #8 variable
    debt_data = [0.1355, 0.1287, 0.1105, 0.0686, 0.0406, 0.0809, 0.3447, 0.0200, 0.0705]
    labels = debt_labels
    data = debt_data
    fontColour = ["black"]
    fontColour = fontColour*10
    if request.method == 'POST':
        vals = request.POST['piePlts']
        if vals == 'specGradeProb':
            is_pie_Debt = 0
            spec_labels = ['L.logrea~c','L.saving~o','L.totres~b','L.rl_est','L.dum_de~s','L.govtgr~o','L.m3gdp_~d','L.export~o','L.fiscal~o'] #9 variable
            spec_data = [0.2483, 0.1514, 0.0304, 0.2925, 0.0406, 0.1199, 0.0611, 0.0025, 0.0534]
            labels = spec_labels
            data = spec_data

    context = {'is_pie_Debt':is_pie_Debt, 'labels':labels, 'data':data, 'fontColour':fontColour}
    return render(request, 'pieChart.html', context=context)

def refreshData(request):
    if request.method == 'POST':
        f_year = int(request.POST['year'])
        tf_status = refresh_data(f_year)
        context = {'tf_status':tf_status}
    else:
        context = {'tf_statis':0}
    return render(request, 'index.html', context)
    


