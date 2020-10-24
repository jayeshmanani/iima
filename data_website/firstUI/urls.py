from django.urls import path

from . import views

urlpatterns = [
    path('', views.indexPage, name='index'),
    path('year', views.year, name='year'),
    path('graph', views.graph, name='graph'),
    path('graph2', views.graph2, name='graph2'),
    path('worldPlot', views.worldPlot, name='worldPlot'),
    path('updateStatus', views.updateStatus, name='updateStatus'),
    # path('debt_WorldPlot', views.debt_WorldPlot, name='debt_WorldPlot'),
]