import urllib2, os, pyMet
import blocks

from google.appengine.api import users
import webapp2
from google.appengine.ext import db
from datetime import datetime
import time
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class BusStop(db.Model):
    stopId = db.StringProperty()
    stopPosition = db.ListProperty(str)
    stopDesc = db.StringProperty()
    reqDate = db.DateTimeProperty(auto_now_add=True)
    reqUser = db.UserProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):      
        rendTemp(self)
        
class AboutPage(webapp2.RequestHandler):
    def get(self):
        dictout=dict(infoBlock = blocks.strInfo)
        rendTemp(self, dictout)
        
class ErrPage(webapp2.RequestHandler):
    def get(self):
        dictout = dict(errMsg = self.request.get('oops'))
        rendTemp(self, dictout)

class CheckStop(webapp2.RequestHandler):

    def post(self):
        self.stopToCheck = self.request.get('content').strip()
        myConnection = pyMet.pyMet()  ###put your trimet app-id as the only line in a file called appkey.app 
        if self.stopToCheck != "":
            dictOut = {'req_time':datetime.strftime(datetime.now(),pyMet.TSTRFMT)}
            bArrival = myConnection.showStopSMS(self.stopToCheck)                       
            if bArrival == False:   #trimet reported an error
                strErUrl = '/oops?oops=%s'%(urllib2.quote(",".join(myConnection.lstOut)))
                self.redirect(strErUrl)
            else:
                 

                dictOut['chkdStop'] = self.stopToCheck
                dictOut['stpInfo'] = ",".join([myConnection.stopName,myConnection.stopDir])
                if len(myConnection.lstOut) > 0:
                    dictOut['strArvls'] = '<br>'.join(myConnection.lstOut)
                else:
                    dictOut['strArvls'] = ' No arrivals found for this stop at this time '
                rendTemp(self,dictOut)
                recStop = BusStop(key_name='{0}{1}'.format(self.stopToCheck, time.time()))
                recStop.stopId = self.stopToCheck
                recStop.stopPosition = [str(myConnection.stopLat), str(myConnection.stopLng)]
                recStop.stopDesc = "%s, %s"%(myConnection.stopName,myConnection.stopDir)
                if self.curUser:
                    recStop.reqUser = self.curUser
                recStop.put() 
        else:  #no stop to check - load error
            self.redirect('/oops?oops=Please%20enter%20a%20stop') 
    def get(self):
        self.post()
        

def rendTemp(self,dictOut = {}):
    dictOut['loginBlock'] = blocks.getUserinfo(self.request.uri, self)
    dictOut['strLicence'] = blocks.strLicence
    if self.curUser:
        dictOut['statTab'] = blocks.makeStopTable(self.curUser)
    else:
        dictOut['statTab'] = blocks.makeStopTable("")   
    template = jinja_environment.get_template('myMet.html')
    self.response.out.write(template.render(dictOut))    

app = webapp2.WSGIApplication(
                                     [
                                      ('/stop', CheckStop),
                                      ('/about', AboutPage),
                                      ('/oops', ErrPage),
                                      ('/', MainPage)
                                      ],
                                     debug=True)    

    
