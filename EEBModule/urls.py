from django.conf.urls import patterns, url
from EEBModule import views


urlpatterns = patterns(
    'EEBModule.views',
    url(r'^kpi/kpiList$', views.kpiList),
    url(r'^kpi/KPI-1$', views.kpi1),
    url(r'^kpi/KPI-2$', views.kpi2),
    url(r'^kpi/KPI-3$', views.kpi3),
    url(r'^kpi/KPI-4$', views.kpi4),
    url(r'^kpi/KPI-5$', views.kpi5),
    url(r'^kpi/KPI-6$', views.kpi6),
    url(r'^kpi/KPI-7$', views.kpi7),
    url(r'^kpi/KPI-8$', views.kpi8),
    url(r'^kpi/KPI-9$', views.kpi9),
    url(r'^kpi/KPI-10$', views.kpi10),
    url(r'^kpi/KPI-11$', views.kpi11),
    url(r'^kpi/KPI-12$', views.kpi12),
    url(r'^kpi/KPI-13$', views.kpi13),
    url(r'^kpi/KPI-14$', views.kpi14),
    url(r'^kpi/getOccupancy$', views.occupancy),
    url(r'^kpi/getPlanArea$', views.planArea),
    url(r'^kpi/getBuyPrice$', views.buyPrice),
    url(r'^kpi/getSoldPrice$', views.soldPrice),
    url(r'^kpi/getCo2Factor$', views.co2Factor),
    url(r'^.*/$', views.errorHandling)
)