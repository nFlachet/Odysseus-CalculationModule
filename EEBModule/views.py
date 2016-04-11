from rest_framework import status
from rest_framework.decorators import api_view

from EEBModule.serializers import kpiSerializer
from EEBModule.models import Kpi
from EEBModule.KpiCalculation import *


@api_view(['GET'])
def kpiList(request):
    """
    List all kpi available for scope and tenant.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
        except:
            return Response({'parameters errors' : 'only available parameters arer kpi_scope and kpi_tenant'}, status=status.HTTP_400_BAD_REQUEST)

        kwargs = {}
        if scope == '0': #Building
            kwargs ['kpi_scope_building'] = True
        elif scope == '1': #Room
            kwargs ['kpi_scope_room'] = True
        else:
            return Response({'parameters errors' : 'kpi_scope only acceptable values are 0 or 1'}, status=status.HTTP_400_BAD_REQUEST)

        if tenant == '1' or tenant == '99': #Manchester
            kwargs ['kpi_tenant_Manchester'] = True
        elif tenant == '0' or tenant == '98': #Roma
             kwargs ['kpi_tenant_Roma'] = True
        else:
            return Response({'parameters errors' : 'kpi_tenant only acceptable values are 1 for Manchester or 0 for Roma'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Kpi.objects.filter(**kwargs)
        if not queryset:
            return Response({'Warning' : 'no kpi found for tenant = {} and scope = {}'.format(scope,tenant)}, status=status.HTTP_204_NO_CONTENT)

        serializer = kpiSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

@api_view(['GET'])
def occupancy(request):
    """
    get Occupancy for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Occupancy" : handler.getOccupancy()}, status=status.HTTP_200_OK)

@api_view(['GET'])
def kpi1(request):
    return calculateKpi(request, '1')

@api_view(['GET'])
def kpi2(request):
    return calculateKpi(request, '2')

@api_view(['GET'])
def kpi3(request):
    return calculateKpi(request, '3')

@api_view(['GET'])
def kpi4(request):
    return calculateKpi(request, '4')

@api_view(['GET'])
def kpi5(request):
    return calculateKpi(request, '5')

@api_view(['GET'])
def kpi6(request):
    return calculateKpi(request, '6')

@api_view(['GET'])
def kpi7(request):
    return calculateKpi(request, '7')

@api_view(['GET'])
def kpi8(request):
    calculateKpi(request, '8')

@api_view(['GET'])
def kpi9(request):
    return calculateKpi(request, '9')

@api_view(['GET'])
def kpi10(request):
    return calculateKpi(request, '10')

@api_view(['GET'])
def kpi11(request):
    return calculateKpi(request, '11')

@api_view(['GET'])
def kpi12(request):
    return calculateKpi(request, '12')

@api_view(['GET'])
def kpi13(request):
    return calculateKpi(request, '13')

@api_view(['GET'])
def kpi14(request):
    return calculateKpi(request, '14')


@api_view(['GET'])
def planArea(request):
    """
    get plan area for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Area" : handler.getArea()}, status=status.HTTP_200_OK)

@api_view(['GET'])
def planArea(request):
    """
    get plan area for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Area" : handler.getArea()}, status=status.HTTP_200_OK)

@api_view(['GET'])
def buyPrice(request):
    """
    get pricing buy cost for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Buy Price" : handler.getBuyPrice()}, status=status.HTTP_200_OK)

@api_view(['GET'])
def soldPrice(request):
    """
    get pricing sold cost for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Sold Price" : handler.getSoldPrice()}, status=status.HTTP_200_OK)

@api_view(['GET'])
def co2Factor(request):
    """
    get co2Factor for an element.
    """
    if request.method == 'GET':
        try:
            scope = request.GET['kpi_scope']
            tenant = request.GET['kpi_tenant']
            elementID = request.GET['elem_id']
        except:
            return Response({'parameters errors' : 'only available parameters are kpi_scope, kpi_tenant and element_id'}, status=status.HTTP_400_BAD_REQUEST)

        handler = KpiHandlers(scope, tenant, "", "", "", elementID)
        return Response({"Co2 Factor" : handler.getCo2Factor()}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def errorHandling(request):
    return Response({'Error' : 'wrong request, {}'.format(request.get_full_path())}, status=status.HTTP_400_BAD_REQUEST)