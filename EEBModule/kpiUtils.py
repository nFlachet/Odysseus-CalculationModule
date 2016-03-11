from suds.client import Client
from suds import WebFault
import urllib2 as u2
from suds.transport.http import HttpTransport, Reply, TransportError
import httplib
import operator
import copy
import time
import datetime
from collections import defaultdict
from pip._vendor.html5lib.constants import spaceCharacters

class FactoredMeter:
    def __init__(self,signalid,factor):
        self.signalid = signalid
        self.factor = factor
        self.values = dict()
     
    # alternative equals method to be able to compare based on content and not object id   
    def __eq__(self, other):
        return self.signalid == other.signalid and self.factor == other.factor
        
    def addValue(self, period, value):
        if period not in self.values:
            self.values.setdefault(period, float) 
        self.values[period] = value  
           
class HTTPSClientAuthHandler(u2.HTTPSHandler):
    def __init__(self, key, cert):
        u2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key,
                                       cert_file=self.cert)


class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, proxy_settings=None, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert
        self.proxy_settings = proxy_settings

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2 request.
        @type u2request: urllib2.Requet.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout

        https_client_auth_handler = HTTPSClientAuthHandler(self.key,self.cert)

        # Add a proxy handler if the proxy settings is specified.
        # Otherwise, just use the HTTPSClientAuthHandler.
        if self.proxy_settings:
            proxy_handler = u2.ProxyHandler(self.proxy_settings)
            url = u2.build_opener(proxy_handler, https_client_auth_handler)
        else:
            url = u2.build_opener(https_client_auth_handler)

        url = u2.build_opener()

        return url.open(u2request, timeout=tm)


class KpiHandlers:
    def __init__(self, scope, tenant, start_time, end_time, time_scope, element_id):
        self._scope = scope
        self._tenant = tenant
        self._start_time = start_time
        self._end_time = end_time
        self._time_scope = time_scope
        self._element_id = element_id
        self._kpi_values = {}
        self._kpi_ordered_values = []
        self._sensors = []
        self._sensorsAccumulative = []
        self._sensorsIncremental = []
        self._sensorsInstant = []
        self._VMsensors = []
        self._VMs = {}
        self._VMsAccumulative = []
        self._VMsIncremental = []
        self._VMsInstant = []
        self._occupancy = 0.0
        self._area = 0.0
        self._buyPrice = 0.0
        self._soldPrice = 0.0
        self._buyGasPrice = 0.0

    def getOccupancy(self):
        self._getStaticDatas("006")
        return self._occupancy

    def getArea(self):
        if self._area == 0.0:
            self._getStaticDatas("006")
        return self._area

    def getBuyPrice(self):
        if (self._tenant == 0):   #Roma
            if self._buyPrice == 0.0:
                self._getStaticDatas("009")
            return self._buyPrice
        else: #Manchester
            if self._buyGasPrice == 0.0:
                self._getStaticDatas("009")
            return self._buyGasPrice

    def getSoldPrice(self):
        if (self._tenant == 0):   #Roma
            if self._soldPrice == 0.0:
                self._getStaticDatas("009")
            return self._soldPrice
        else: #Manchester
            if self._buyGasPrice == 0.0:
                self._getStaticDatas("009")
            return 0

    def _getStaticDatas(self, reqType):
        # 006 building static values
        # 007 room static values
        url = "https://hamster.tno.nl/SemanticServerDataProxy/endpoints/SelectStaticGatewaysMsgService.wsdl"
        client = Client(url, location="https://hamster.tno.nl/SemanticServerDataProxy/endpoints")

        reqlist = client.factory.create('requests')
        req = client.factory.create('request')
        req.requestSubject = self._element_id
        req.requestType = reqType
        reqlist.request = [req]

        try:
            result = client.service.SelectStaticGatewayMessage(reqlist, self._tenant, "evecity", "3v3C1ty.2486")
            for itemA in result.qeuryResultLines:
                for item in result.qeuryResultLines.queryResultLine:
                    for item2 in item.qeuryResultField:
                        if item2.columnName == 'typicalWorktimeOccupancy' and item2.value != "n.a." and item2.value != "null":
                            self._occupancy = self._occupancy + float(item2.value)
                        elif item2.columnName == 'planSurfaceArea' and item2.value != "n.a." and item2.value != "null":
                            self._area = self._area + float(item2.value)

                        # 1/4 low price * 3/4 high price (elec)
                        elif item2.columnName == 'electBuyHigh' and item2.value != "n.a." and item2.value != "null":
                            self._buyPrice = self._buyPrice +(3 * float(item2.value))
                        elif item2.columnName == 'electBuyLow' and item2.value != "n.a." and item2.value != "null":
                            self._buyPrice = self._buyPrice + float(item2.value)
                        elif item2.columnName == 'electSellLow' and item2.value != "n.a." and item2.value != "null":
                            self._soldPrice = self._soldPrice + float(item2.value)
                        elif item2.columnName == 'electSellHigh' and item2.value != "n.a." and item2.value != "null":
                            self._soldPrice = self._soldPrice + (3 *float(item2.value))
                        elif item2.columnName == 'gasBuyKWH' and item2.value != "n.a." and item2.value != "null":
                            self._buyGasPrice = float(item2.value)

            self._buyPrice = self._buyPrice / 4.0
            self._soldPrice = self._soldPrice / 4.0
            
        except WebFault, e:
            print client.last_sent()
            print e


    def _getSensors(self, sensor_type, filter):
        """ get all sensors associated to this request.
        Take into account scope, tenant, and element_id for this handler.
        Scope :
            000 : get City information based on tentantcode
            002 : get sensors for building ID
            003 : get sensors for room (space) ID
            004 : get neigbourhoods based on tentantcode
            005 : get sensors based on neighbourhood ID

        Also take into account sensor_type, witch is the sensor type :
            cmo:temperature
            depc:relativeHumidity
            depc:co2Concentration
            depc:irradiance
            depc:illuminance
            cmo:voltage
            cmo:electricCurrent
            cmo:power
            depc:eFlow
            depc:irradianceUVA

        filer:
            "Consumption"
            "Production"
        """

        # key= r'C:\key_nopass.pem'
        # cert = r'C:\cert.pem'
        # proxy_settings = {'https': 'http://user:password@host:port'}
        # transport = HTTPSClientCertTransport(key, cert, proxy_settings)

        # service_url = 'https://services.domain.com/test/hello.wsdl'
        # client = Client(service_url, transport=transport)
        # print client

        url = "https://hamster.tno.nl/SemanticServerDataProxy/endpoints/SelectStaticGatewaysMsgService.wsdl"
        client = Client(url, location="https://hamster.tno.nl/SemanticServerDataProxy/endpoints")

        reqlist = client.factory.create('requests')
        req = client.factory.create('request')
        req.requestSubject = self._element_id

        req.requestSensorType = sensor_type

        if self._scope == '0':
            req.requestType = "002"
        elif self._scope == '1':
            req.requestType = "003"
        reqlist.request = [req]

        try:
            result = client.service.SelectStaticGatewayMessage(reqlist, self._tenant, "evecity", "3v3C1ty.2486")
            #print client.last_sent().str()
            for itemA in result.qeuryResultLines:
                for item in list(result.qeuryResultLines.queryResultLine):
                    useThisSensor = False
                    isVirtual = False
                    for item2 in list(item.qeuryResultField):
                        if item2.columnName == 'isVirtual' and item2.value == "true":
                            isVirtual = True
                        if item2.columnName == 'factoredSignalId':
                            factoredSignalId = item2.value
                        if item2.columnName == 'factor':
                            factor = item2.value
                        if item2.columnName == 'space':
                            space = item2.value
                        if item2.columnName == 'signalid':
                            sensorid = item2.value
                        if item2.columnName == 'measurementKind':
                            measurementKind = item2.value                        
                        elif item2.columnName == 'energyLC': # and item2.value != "n.a." and item2.value != "null" and item2.value != "NotSpecified" and item2.value != "NotApplicable":
                            if filter == item2.value or filter == "None":
                                useThisSensor = True

                    if sensorid!= "n.a." and sensorid != "null" and useThisSensor == True and isVirtual == False:
                        if sensorid not in self._sensors:
                            self._sensors.append(sensorid)
                        if measurementKind == 'Incremental' and sensorid not in self._sensorsIncremental:
                            self._sensorsIncremental.append(sensorid)
                        if measurementKind == 'Accumulative  ' and sensorid not in self._sensorsAccumulative:
                            self._sensorsAccumulative.append(sensorid)
                        if measurementKind == 'Instant  ' and sensorid not in self._sensorsInstant:
                            self._sensorsInstant.append(sensorid)
                    if sensorid!= "n.a." and sensorid != "null" and useThisSensor == True and isVirtual == True:
                        factoredMeter = FactoredMeter(factoredSignalId, factor)
                        self._sensors.append(factoredSignalId)
                        self._VMsensors.append(factoredSignalId)
                        if measurementKind == 'Incremental' and sensorid not in self._VMsIncremental:
                            self._VMsIncremental.append(sensorid)
                        if measurementKind == 'Accumulative  ' and sensorid not in self._VMsAccumulative:
                            self._VMsAccumulative.append(sensorid)
                        if measurementKind == 'Instant  ' and sensorid not in self._VMsInstant:
                            self._VMsInstant.append(sensorid)                        
                        if sensorid not in self._VMs:
                            self._VMs.setdefault(sensorid, [])
                        if factoredMeter not in self._VMs[sensorid]:
                            self._VMs[sensorid].append(factoredMeter)
                        
        except WebFault, e:
            print client.last_sent()
            print e


    def _getSensorsValues(self, sensor_id, reqType, operation):
        
        """ get sensors values.
        Take into account scope, tenant, sensor_id (sensors list), start & end time,
        and time scope (group period) for this kpi :
            000 = none
            001 = day
            002 = month
            003 = year

        Parameters, sensor_id: sensor unique id from witch to get value

        reqType :
            001 = all values
            002 = average
            003 = sum

        operation : Algebric operation from 'ops' to do with previous sensors data available
        """

        url = 'https://hamster.tno.nl/SemanticServerDataProxy/endpoints/SelectGatewaysMsgService.wsdl'
        client = Client(url)

        reqList = client.factory.create('requests')
        req = client.factory.create('request')

        reqHead = client.factory.create('requestHead')
        reqHead.requestType = reqType
        reqHead.groupPeriod = str(self._time_scope).zfill(3)
        reqHead.requestSubject = sensor_id
        req.requestHead = reqHead

        reqPeriod = client.factory.create('requestPeriod')
        reqPeriod.fromTimeStamp = self._start_time
        #reqPeriod.fromTimeStamp = "2015-01-25T00:15:00"
        reqPeriod.toTimeStamp = self._end_time
        #reqPeriod.toTimeStamp = "2015-11-26T23:45:00"
        req.requestPeriod = reqPeriod

        reqList.request = [req]

        try:
            result = client.service.SelectGatewayMessage(reqList, self._tenant, "evecity", "3v3C1ty.2486")
            #print client.last_sent().str()
            for itemA in result.qeuryResultLines:
                val = 0.0
                for item in list(result.qeuryResultLines.queryResultLine):
                    for item2 in list(item.qeuryResultField):
                        if item2.columnName == 'timestamp' or item2.columnName =='period':
                            period = item2.value
                        elif item2.columnName == 'value' or item2.columnName == 'ProfileSignal' or item2.columnName == 'Sum':
                            if item2.value != "n.a." and item2.value != "null":
                                val = float(item2.value)

                    if operation == ">":
                        self._kpi_ordered_values.append(val)
                    else:
                        inVal = 0.0
                        if period != "n.a." and period != "null":
                            if period in self._kpi_values.keys():
                                inVal = self._kpi_values[period]

                            self._kpi_values[period] = self._get_val(inVal, operation, val)

        except WebFault, e:
            print client.last_sent()
            print e

    def _getMultipleSensorsValues(self, reqType, operation):
        
        """ get sensors values.
        Take into account scope, tenant, sensor_id (sensors list), start & end time,
        and time scope (group period) for this kpi :
            000 = none
            001 = day
            002 = month
            003 = year

        Parameters, sensor_id: sensor unique id from witch to get value

        reqType :
            001 = all values
            002 = average
            003 = sum

        operation : Algebric operation from 'ops' to do with previous sensors data available
        """

        url = 'https://hamster.tno.nl/SemanticServerDataProxy/endpoints/SelectGatewaysMsgService.wsdl'
        client = Client(url)

        reqList = client.factory.create('requests')
    
        # remove all factoremeter id's'
        
        for sensor in self._sensors:
            req = client.factory.create('request')
            reqHead = client.factory.create('requestHead')
            reqHead.requestType = reqType
            reqHead.groupPeriod = str(self._time_scope).zfill(3)
            reqHead.requestSubject = sensor
            req.requestHead = reqHead
            reqPeriod = client.factory.create('requestPeriod')
            reqPeriod.fromTimeStamp = self._start_time
            reqPeriod.toTimeStamp = self._end_time
            req.requestPeriod = reqPeriod
            reqList.request.append(req)
            
            if (len(reqList.request) >= 10):
                try:
                    result = client.service.SelectGatewayMessage(reqList, self._tenant, "evecity", "3v3C1ty.2486")
                    #print client.last_sent().str()
                    for itemA in result.qeuryResultLines:
                        val = 0.0
                        for item in list(result.qeuryResultLines.queryResultLine):
                            for item2 in list(item.qeuryResultField):
                                if item2.columnName == 'timestamp' or item2.columnName =='period':
                                    period = item2.value
                                if item2.columnName == 'signalid' :
                                    signalid = item2.value
                                elif item2.columnName == 'value' or item2.columnName == 'Average' or item2.columnName == 'Sum':
                                    if item2.value != "n.a." and item2.value != "null":
                                        val = float(item2.value)
                            if signalid in self._VMsensors:
                                #print signalid
                                for vm in self._VMs:
                                    for factoredMeter in self._VMs[vm]:
                                        if factoredMeter.signalid == signalid:
                                            factoredMeter.addValue(period,val)
                            else: 
                                if operation == ">":
                                    self._kpi_ordered_values.append(val)
                                else:
                                    inVal = 0.0
                                    if period != "n.a." and period != "null":
                                        if period in self._kpi_values.keys():
                                            inVal = self._kpi_values[period]
            
                                        self._kpi_values[period] = self._get_val(inVal, operation, val)
            
     
                except WebFault, e:
                    print client.last_sent()
                    print e

                reqList.request = []
                
        if (len(reqList.request) > 0): 
            try:
                result = client.service.SelectGatewayMessage(reqList, self._tenant, "evecity", "3v3C1ty.2486")
                #print client.last_sent().str()
                for itemA in result.qeuryResultLines:
                    val = 0.0
                    for item in list(result.qeuryResultLines.queryResultLine):
                        for item2 in list(item.qeuryResultField):
                            if item2.columnName == 'timestamp' or item2.columnName =='period':
                                period = item2.value
                            if item2.columnName == 'signalid' :
                                signalid = item2.value
                            elif item2.columnName == 'value' or item2.columnName == 'Average' or item2.columnName == 'Sum':
                                if item2.value != "n.a." and item2.value != "null":
                                    val = float(item2.value)
                       
                        if signalid in self._VMsensors:
                            #print signalid# store
                            for vm in self._VMs:
                                for factoredMeter in self._VMs[vm]:
                                    if factoredMeter.signalid == signalid:
                                        factoredMeter.addValue(period,val)
                        else:                         
                            if operation == ">":
                                self._kpi_ordered_values.append(val)
                            else:
                                inVal = 0.0
                                if period != "n.a." and period != "null":
                                    if period in self._kpi_values.keys():
                                        inVal = self._kpi_values[period]

                                self._kpi_values[period] = self._get_val(inVal, operation, val)
                                    
            except WebFault, e:
                print client.last_sent()
                print e
                 
        for vm in self._VMs:
            vmValues = {}
            for fm in self._VMs[vm]:
                for period in fm.values:
                    if period not in vmValues:
                        vmValues.setdefault(period, float(0.0)) 
                    vmValues[period] = self._get_val(vmValues[period],"+",(float(fm.factor) * fm.values[period]))    
            for period in vmValues:
                if operation == ">":
                    self._kpi_ordered_values.append(val)
                else:
                    inVal = 0.0
                    if period != "n.a." and period != "null":
                        if period in self._kpi_values.keys():
                            inVal = self._kpi_values[period]
                    self._kpi_values[period] = self._get_val(inVal, operation, vmValues[period])
                               
    @classmethod
    def _get_val(self, inp, oper, out):
        val = 0.0
        if oper == '+':
            val = operator.add(inp, out)
        return val


    # Energy consumption
    def calculKpi1(self):
        self._getSensors("depc:eFlow", "Consumption")
        #for sensor in self._sensors:
        #    self._getSensorsValues(sensor, "003", "+")
        self._getMultipleSensorsValues("003", "+")
        return self._kpi_values

    def calculKpi2(self):
        self._getSensors("depc:eFlow", "Production")
        #for sensor in self._sensors:
        #    self._getSensorsValues(sensor, "003", "+")
        self._getMultipleSensorsValues("003", "+")
        return self._kpi_values

    def getCo2Factor(self):
        if self._tenant == 0:
            return 0.59     #http://www.econologie.com/europe-emissions-de-co2-par-pays-et-par-kwh-electrique-articles-3722.html
        else:
            return 0.225    #Gas

    def calculKpi3(self):
        kpi1Dic = copy.deepcopy( self.calculKpi1() ) # consommation
        self._kpi_values.clear()
        kpi2Dic = copy.deepcopy( self.calculKpi2() )  # production
        self._kpi_values.clear()
        for key, val in kpi1Dic.viewitems():
            if (val == 0) or (key not in kpi2Dic):
                self._kpi_values[key] = 'n.a.n'
            else:
                self._kpi_values[key] = kpi2Dic[key] / val
        return self._kpi_values

    def calculKpi4(self):
        area = self.getArea()
        self.calculKpi1()
        if area == 0.0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v/area) for k,v in self._kpi_values.items())
        return self._kpi_values

    def calculKpi5(self):
        occupancy = self.getOccupancy()
        self.calculKpi1()
        if occupancy == 0.0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v/occupancy) for k,v in self._kpi_values.items())
        return self._kpi_values

    def calculKpi6(self):
        self.calculKpi1()
        occupancyArea = self.getOccupancy() * self.getArea()
        if occupancyArea == 0.0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v/(occupancyArea)) for k,v in self._kpi_values.items())
        return self._kpi_values

    def calculKpi7(self):
        kpi2Dic = copy.deepcopy( self.calculKpi2() )  # production
        self._kpi_values.clear()
        kpi1Dic = copy.deepcopy(self.calculKpi1())
        for key, val in kpi2Dic.viewitems():
            self._kpi_values[key] = abs(val - kpi1Dic.get(key, 0))
        return self._kpi_values


    def calculKpi8(self):
        self.calculKpi7()
        area = self.getArea()
        if area == 0.0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v/(area)) for k,v in self._kpi_values.items())
        return self._kpi_values

    def calculKpi9(self):
        kpi2Dic = copy.deepcopy( self.calculKpi2() ) # production
        self._kpi_values.clear()
        kpi7Dic = copy.deepcopy( self.calculKpi7() )  # surplus
        self._kpi_values.clear()
        for key, val in kpi2Dic.viewitems():
            if (val == 0) or (key not in kpi7Dic):
                self._kpi_values[key] = 'n.a.n'
            else:
                self._kpi_values[key] = kpi7Dic[key] / val
        return self._kpi_values

    def calculKpi10(self):
        self._getSensors("depc:eFlow", "Consumption")
        for sensor in self._sensors:
            self._getSensorsValues(sensor, "001", "+")

        kpi1Dic = copy.deepcopy( self._kpi_values )
        self._kpi_values.clear()

        self._getSensors("depc:eFlow", "Production")
        for sensor in self._sensors:
            self._getSensorsValues(sensor, "001", "+")

        cpt = 0
        for key, val in self._kpi_values.viewitems():
            if val > kpi1Dic.get(key, 0):
                cpt += 1

        return {"2015" : cpt/(4.0 * 8760.0)}


    def calculKpi11(self):
        co2Factor = self.getCo2Factor()
        self.calculKpi1()
        if co2Factor == 0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v*co2Factor) for k,v in self._kpi_values.items())
        return self._kpi_values


    def calculKpi12(self):
        area = self.getArea()
        self.calculKpi11()
        if area == 0.0:
            self._kpi_values = dict.fromkeys( self._kpi_values.iterkeys(), 'n.a.n' )
        else:
            self._kpi_values.update((k,v/(area)) for k,v in self._kpi_values.items())


    def calculKpi13(self):
        pass
        # self._getSensors("depc:co2Concentration", "None")
        # for sensor in self._sensors:
        #     self._getSensorsValues(sensor, "001", ">")
        #
        #     absence = [False] * (len(self._kpi_ordered_values)-4)
        #     listValeur = [0,0,0,0]
        #     for idx, val in enumerate(self._kpi_ordered_values):
        #         if idx-2 >=0 and idx+2<= len(self._kpi_ordered_values)-1:
        #             listValeur[0] = self._kpi_ordered_values[idx-1] - self._kpi_ordered_values[idx-2]
        #             listValeur[1] = val - self._kpi_ordered_values[idx-1]
        #             listValeur[2] = self._kpi_ordered_values[idx+1] - val
        #             listValeur[3] = self._kpi_ordered_values[idx+2] - self._kpi_ordered_values[idx+1]
        #             absence[idx-2] = (max(listValeur) < 3.0) and (self._kpi_ordered_values[idx+2] <= self._kpi_ordered_values[idx-2])
        #         self._kpi_ordered_values.clear()
        #
        #         self._getSensors("depc:irradianceUVA", "None")
        #         for sensorUV in self._sensors:
        #             self._getSensorsValues(sensorUV, "001", ">")
        #             uvRadiation = copy.deepcopy(self._kpi_ordered_values)
        #
        #         self._getSensors("depc:illuminance", "None")
        #         for sensor in self._sensors:
        #             self._getSensorsValues(sensor, "001", ">")
        #             artificialLight = [False] * (len(self._kpi_ordered_values)-4)
        #
        # return self._kpi_values

    def calculKpi14(self):
        buyPrice = self.getBuyPrice()
        soldPrice = self.getSoldPrice()

        kpi1Dic = copy.deepcopy( self.calculKpi1() ) # production
        self._kpi_values.clear()
        kpi2Dic = copy.deepcopy( self.calculKpi2() )  # surplus
        self._kpi_values.clear()

        for key, val in kpi1Dic.viewitems():
            self._kpi_values[key] = val*buyPrice - kpi2Dic.get(key,0)*soldPrice

        return self._kpi_values
