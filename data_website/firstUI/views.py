from django.shortcuts import render
from django.http import HttpResponse
from firstUI.functions import check_if_data
import datetime
import pandas as pd
from firstUI.models import FinanceData
from firstUI.models import Country


d_wmap = pd.read_json('https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')

def indexPage(request):
    cntry = Country.objects.all()
    country_list = []
    for i in cntry:
        country_list.append(i.country_name)
    context = {'country_list':country_list}
    return render(request, 'index.html', context)

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
    
    # print(rgn)
    # print(for_which)
    # print(f_year)
    
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
