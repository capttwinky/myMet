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
import xml.etree.ElementTree as ET
import urllib2, cStringIO, time, datetime

class pyMet(object):
  def __init__(self,appId = ""):
	self.appId = appId
	self.lstOut = []
	self.stopName = []
	self.stopDir = []
	if self.connect() == False:
	  raise Exception('no connection')

  def connect(self):
	if self.appId != "":			#this is a placeholder for "real" appId validation
	  #print("appId is: %s" %self.appId)
	  return None
	raise Exception("no appId")
	return False

  def getArrivals(self,stopId=""):
	if stopId =="":
	  raise Exception('no stopId')
	strUrl = "http://developer.trimet.org/ws/V1/arrivals/locIDs/%s/appID/%s"%(stopId,self.appId)
	fileXml = urlToFile(strUrl)
	metTree = ET.ElementTree().parse(fileXml)
	fileXml.close()
	return metTree
	
  def getTripPlan(self,strStart,strEnd):
	  
	  #strUtl ="http://developer.trimet.org/ws/V1/trips/tripplanner/fromplace/pdx/toplace/rose%20quarter/appId/D93C6F933BC90C056D4EE8406"
	  strUtl ="http://developer.trimet.org/ws/V1/trips/tripplanner/fromplace/%s/toplace/%s/appId/%s"%(strStart,strEnd,self.appId)
	  pass

  def parseArrivalsShort(self, metTree = ""):
	lstOut=[]
	if metTree == "":
	  raise Exception("No Arrivals")
	errTree = metTree.getiterator('{urn:trimet:arrivals}errorMessage')
	locTree = metTree.getiterator('{urn:trimet:arrivals}location')
	arrivalTree = metTree.getiterator('{urn:trimet:arrivals}arrival')
	if len(errTree) != 0:
		for thing in errTree:
			self.lstOut.append(thing.text)
		return False
	dictLoc = locTree[0].attrib
	self.stopName = dictLoc['desc']
	self.stopDir = dictLoc['dir']
	self.stopLat = dictLoc['lat']
	self.stopLng = dictLoc['lng']
	for lstArrivalinfo in arrivalTree:
	  dictArrival = lstArrivalinfo.attrib
	  if dictArrival['status'] == 'estimated':
		strArrival = dictArrival['estimated'][:-3]+"."+dictArrival['estimated'][-3:-2]
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
		strArrival = dictArrival['scheduled'][:-3]+"."+dictArrival['scheduled'][-3:-2]
		fltArv = float(strArrival) - (8* 3600) #gotta make GMT into PST
		tmLocal = time.gmtime(fltArv)
		#tmLocal[2] = tmLocal[2] -8
		strTime = time.strftime('%d%b%H%M', tmLocal)
	  strSign = reduceDoubles(dictArrival['shortSign'], ' ')
	  lstSign = strSign.split(" ")
	  if lstSign[1] == 'To': del(lstSign[1])
	  strSign = " ".join(lstSign)
	  strOut = "%s %s" %(strSign, strTime)
	  lstOut.append(strOut)
	self.lstOut = lstOut
	return True

  def showStopSMS(self, stopId):
	self.arrivalTree = self.getArrivals(stopId)
	return self.parseArrivalsShort(self.arrivalTree)

def urlToFile(strUrl):
  return cStringIO.StringIO(urllib2.urlopen(strUrl).read())

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
  myConnection = pyMet('D93C6F933BC90C056D4EE8406')
  myConnection.showStopSMS('13243')
  myConnection.showStopSMS('bob')
#  for line in myConnection.lstOut:
#	print line
  #strOut = shortenToSMS(myConnection.lstOut)
  #print ((strOut), len(strOut))
  #print("%s going %s"%(myConnection.stopName,myConnection.stopDir))
