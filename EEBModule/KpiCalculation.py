from kpiUtils import *
from EEBModule.serializers import claculKpiSerializer
from rest_framework.response import Response
from rest_framework import status

def calculateKpi(request, num='0'):
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            startTime = request.GET['start_time']
            endTime = request.GET['end_time']
            timeScope = request.GET['time_scope']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'paremeters should be start_time, end_time, time_scope and elem_id'}, status=status.HTTP_400_BAD_REQUEST)

        if num == '13':  # only interested in annual results
            return Response({'Request' : 'kpi 13 is not implemented yet'}, status=status.HTTP_200_OK)

        if num =='10':
            timeScope = '3'

        responseKpi = calculateDispatchedKpi(num, scope, tenant, startTime, endTime, timeScope, elementID)

        cks = claculKpiSerializer()
        cks.add_kpiName(num)
        cks.add_tenant(tenant)
        cks.add_scope(scope)
        cks.add_data('startTime', startTime)
        cks.add_data('endTime', endTime)
        cks.add_timeScope(timeScope)
        cks.add_data('ID', elementID)
        cks.add_results(responseKpi)

        response = Response(cks.getResult(), status=status.HTTP_200_OK)
        return response

def calculateDispatchedKpi(num, scope, tenant, start_time, end_time, time_scope, element_id):

    handler = KpiHandlers(scope, tenant, start_time, end_time, time_scope, element_id)
    if num == '1':
        return handler.calculKpi1()

    elif num == '2':
        return handler.calculKpi2()

    elif num == '3':
        return handler.calculKpi3()

    elif num == '4':
        return handler.calculKpi4()

    elif num == '5':
        return handler.calculKpi5()

    elif num == '6':
        return handler.calculKpi6()

    elif num == '7':
        return handler.calculKpi7()

    elif num == '8':
        return handler.calculKpi8()

    elif num == '9':
        return handler.calculKpi9()

    elif num == '10':
        return handler.calculKpi10()

    elif num == '11':
        return handler.calculKpi11()

    elif num == '12':
        return handler.calculKpi12()

    elif num == '13':
        return handler.calculKpi13()

    elif num == '14':
        return handler.calculKpi14()

    return None
