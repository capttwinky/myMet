'''
Created on Jul 10, 2010

@author: JP McGrady

--setup connection to triMet data service with appId
--return xml parsed into elementTree from function call
----construct request URL
----make request
----parse XML
--print out elementTree
'''
from lxml import etree
import urllib2
import time
import datetime
import os

TSTRFMT = '%d%b%H%M'

class pyMet(object):
    def __init__(self,appId = None):
        if not appId:
            try:
                with open('{0}/{1}'.format(os.path.dirname(__file__),'appkey.app')) as ofile:
                    appId = ofile.read().strip('\n')
            except Exception as e:
                print str(e)
                raise Exception('must have an appkey.app')
        self.appId = appId
        self.lstOut = []
        self.stopName = []
        self.stopDir = []
        if self.connect() == False:
          raise Exception('no connection')

    def connect(self):
        if self.appId != "":            #this is a placeholder for "real" appId validation
          return None
        raise Exception("no appId")

    def getArrivals(self,stopId=""):
        if stopId =="":
          raise Exception('no stopId')
        strUrl = "http://developer.trimet.org/ws/V1/arrivals/locIDs/%s/appID/%s"%(stopId,self.appId)
        return etree.fromstring(urlToStr(strUrl).replace('xmlns="urn:trimet:arrivals"',''))

    def getTripPlan(self,strStart,strEnd):
      
      #strUtl ="http://developer.trimet.org/ws/V1/trips/tripplanner/fromplace/pdx/toplace/rose%20quarter/appId/D93C6F933BC90C056D4EE8406"
      strUtl ="http://developer.trimet.org/ws/V1/trips/tripplanner/fromplace/%s/toplace/%s/appId/%s"%(strStart,strEnd,self.appId)
      pass

    def parseArrivalsShort(self, metTree = ''):
        lstOut=[]
        if metTree == '':
          raise Exception("No Arrivals")
        errTree = metTree.findall('errorMessage')
        locTree = metTree.findall('location')
        arrivalTree = metTree.findall('arrival')
        for thing in errTree:
            self.lstOut.append(thing.text)
        if self.lstOut: return False
        dictLoc = locTree[0].attrib
        self.stopName = dictLoc['desc']
        self.stopDir = dictLoc['dir']
        self.stopLat = dictLoc['lat']
        self.stopLng = dictLoc['lng']
        strTime = datetime.datetime.strftime(datetime.datetime.now(),TSTRFMT)
        for arrival_info in arrivalTree:
            if arrival_info.attrib['status'] == 'estimated':
                strArrival = arrival_info.attrib['estimated'][:-3]+"."+arrival_info.attrib['estimated'][-3:-2]
                fltArv = float(strArrival)
                tdArv = datetime.timedelta(seconds=fltArv)
                tdNow = datetime.timedelta(seconds=time.time())
                tdWait = tdArv-tdNow
                tmDelta = datetime.time(hour=tdWait.seconds//3600, minute=tdWait.seconds//60)
                if tmDelta.hour > 0:
                  strTime = tmDelta.strftime('%Hh%Mm').lstrip('0')
                else:
                  strTime = tmDelta.strftime('%Mm').lstrip('0') 
                  if len(strTime) == 1:
                    strTime = "now"
            else:
                strArrival = arrival_info.attrib['scheduled'][:-3]+"."+arrival_info.attrib['scheduled'][-3:-2]
                fltArv = float(strArrival) - (8* 3600) #gotta make GMT into PST
                tmLocal = datetime.datetime.fromtimestamp(fltArv)
                diff = tmLocal - datetime.datetime.now()
                if diff.days < 0:
                    tmLocal = tmLocal+datetime.timedelta(hours=1)
                strTime = datetime.datetime.strftime(tmLocal,TSTRFMT)
            lstSign = reduceDoubles(arrival_info.attrib['shortSign'], ' ').split(" ")
            if len(lstSign)>=2 and lstSign[1] == 'To': del(lstSign[1])
            lstOut.append("%s %s" %(" ".join(lstSign), strTime))
        self.lstOut = lstOut
        return True

    def showStopSMS(self, stopId):
        self.arrivalTree = self.getArrivals(stopId)
        return self.parseArrivalsShort(self.arrivalTree)

def urlToStr(strUrl):
  return urllib2.urlopen(strUrl).read()

def shortenToSMS(lstTarget):
  strOut = ", ".join(lstTarget)
  if len(strOut) > 159:
    strOut = shortenToSMS(lstTarget[:-1])
  return strOut

def reduceDoubles(strTarget, strGetridof):
  strOut = strTarget.replace(2*strGetridof,strGetridof)
  if strOut.find(2*strGetridof) != -1:
    strOut = reduceDoubles(strOut, strGetridof)
  return strOut

if __name__ == '__main__':
  myConnection = pyMet()
  myConnection.showStopSMS('13243')
  myConnection.showStopSMS('bob')
