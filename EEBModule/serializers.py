from rest_framework import serializers
from EEBModule.models import Kpi

# class KpiScope(enum.Enum):
#     BUILDING = 0
#     ROOM = 1
#
# class KpiTenant(enum.Enum):
#     MANCHESTER = 1
#     ROMA = 0

class kpiSerializer(serializers.ModelSerializer):

    # url = serializers.SerializerMethodField('get_url')
    # def get_url(self, obj):
    #     return 'truite'
    # kpi_url = serializers.SerializerMethodField('get_kpi_url')
    #
    # def get_kpi_url(self, obj):
    #     return obj.kpi_name

    # def __init__(self, *args, **kwargs):
    #     self.request = context['request']
    #     super(kpiSerializer, self).__init__(*args, **kwargs)


    kpi_url = serializers.SerializerMethodField()
    def get_kpi_url(self, obj):
        chains = self.context['request'].get_full_path().replace('kpiList', obj.kpi_name )
        return '%s://%s%s' % (self.context['request'].scheme, self.context['request'].get_host(), chains)

    class Meta:
        model = Kpi
        fields = ('kpi_name', 'kpi_description', 'kpi_scope_building', 'kpi_scope_room', 'kpi_tenant_Roma', 'kpi_tenant_Manchester', 'kpi_url')


class claculKpiSerializer(object):
    def __init__(self):
        self.data = {}

    def add_kpiName(self, numKpi):
        self.data['kpi_name'] = 'KPI-' + str(numKpi)

    def add_data(self, key, val):
        self.data[key] = str(val)

    def add_tenant(self, tenant):
        readable_tenant = ''
        if tenant == '0' or tenant == '98':
            readable_tenant = 'Roma'
        elif tenant == '1' or tenant == '99':
            readable_tenant = 'Manchester'
        self.add_data('kpi_tenant', readable_tenant)

    def add_scope(self, scope):
        readable_scope = ''
        if scope == '0':
            readable_scope = 'Building'
        elif scope == '1':
            readable_scope = 'Room'
        self.add_data('kpi_scope', readable_scope)

    def add_timeScope(self, timeScope):
        readable_scope = 'None'
        if timeScope == '1':
            readable_scope = 'Day'
        elif timeScope == '2':
            readable_scope = 'Month'
        elif timeScope == '3':
            readable_scope = 'Year'
        self.add_data('time_scope', readable_scope)

    def add_results(self, values):
        list_result = []
        for itemKey, itemValue in values.iteritems():
            list_result.append( {'date':itemKey, 'value':itemValue} )
        self.data['Results'] = list_result

    def getResult(self):
        return self.data

