from google.appengine.api import users                      ##
from google.appengine.ext import db

class BusStop(db.Model):
    stopId = db.StringProperty()
    stopPosition = db.ListProperty(str)
    stopDesc = db.StringProperty()
    reqDate = db.DateTimeProperty(auto_now_add=True)
    reqUser = db.UserProperty()

def getUserinfo(strUrl, self=False):
    
    thsUser = users.get_current_user()
    if thsUser:
        strLogOut = users.create_logout_url(strUrl)
        strOut = 'Hi there, %s. <a href="%s">logout.</a>'%(thsUser.nickname(),strLogOut)
    else:
        strOut = '<a href="%s">Log in with your Google account.</a>'%(users.create_login_url(strUrl))
    if self:
        self.curUser = thsUser
    return strOut
    
def frmButton(stpId,strLabel):
    strFrm = """<div><form action="/stop" method="post">
                <input type="hidden" name="content" value="%s" />
                <label>
                <input type="submit" value="%s" />
                %s
                </label>
              </form></div>"""%(stpId,stpId,strLabel)
    return strFrm
    
def makeStopTable(usrUser):
    dictOuts={}
    stops = BusStop.all()
    if usrUser:
        stops.filter('reqUser =',usrUser)
        strPoss = "Your"
    else:
        strPoss = "The"
    stops.order("-reqDate")
    
    lcStops = stops.fetch(100)
    #~ quser = 'WHERE reqUser = {0}'.format(usrUser) if usrUser else ''
    #~ strPoss = 'Your' if usrUser else 'The'
    #~ stqry = 'SELECT * FROM BusStop {0} ORDER BY reqDate DESC LIMIT 100'.format(quser)
    #~ lcStops = db.GqlQuery(stqry, db.Key.from_path('BusStop', 1))
    #~ print lcStops
    strOut = "%s last 10 stops requested:<br>"%strPoss
    lstTp = list(lcStops[:10])
    for tpStop in lstTp:
        stDate = str(tpStop.reqDate)
        strOut +="%s"%(frmButton(tpStop.stopId,tpStop.stopDesc.replace('bound','')))
    strOut +="<hr>"
    for lclStop in lcStops:
        if lclStop.stopId not in dictOuts.keys():
            dictOuts[lclStop.stopId] = [lclStop.stopDesc.replace('bound',''), 1]
        else:
            dictOuts[lclStop.stopId][1] += 1
    dictOften = {}
    strOut += "The most frequent stops in %s last 100:<br>"%strPoss.lower()
    for stpId, stpInfo in dictOuts.items():
        if stpInfo[1] not in dictOften.keys():
            dictOften[stpInfo[1]] = [stpId]
        else:
            dictOften[stpInfo[1]].append(stpId)
    lstFreq = []
    for intCount in sorted(dictOften.keys())[::-1]:
        for stId in dictOften[intCount]:
            if len(lstFreq) < 10:
                lstFreq.append(frmButton(stId, dictOuts[stId][0]))
    strOut += "".join(lstFreq)
    return strOut

strInfo = """
<ul>
    <li>
        <p style="margin-bottom: 0in;">What is myMet?<br>
        MyMet is a simple way to track and record the Tri-Met stops you use
        most often.
        </p>
    </li>
    <li>
        <p style="margin-bottom: 0in;">How do I use myMet?<br>
        There are two ways: First, you can use it without logging in, enter a
        stopId and press "check stop". The next arrivals for that stop will be
        listed, along with statistics shared between all users. If you log in,
        the statistics shown will be for you specifically. In either case,
        pressing on a button with a stopId brings up that stop's next arrivals.
        </p>
    </li>
    <li>
        <p>How can I contact the developer? <br>
        <a href="mailto:mcgrady.jp@gmail.com">mcgrady.jp@gmail.com</a>
        </p>
    </li>
    <li>
        <p style="margin-bottom: 0in;">What's going on here? <br>
        This is my first Google App Engine project, adapted from a wsgi web
        service and tri-met access library written as sample code in python and
        django template code. Contact me if you want to see the files. </p>
    </li>
    <li>
        <p style="margin-bottom: 0in;">Why did you make those choices? <br>
        App Engine scales well, without the need for additional developer or
        administrator training and is competitively priced compared with more
        traditional service models. I think App Engine could be an ideal
        platform for many business applications, including core requirements of
        24/7 availability everywhere there is Google. </p>
    </li>
    <li>
        <p style="margin-bottom: 0in;">How do I know if this will work for
        me?<br>
        Contact me at <a href="mailto:mcgrady.jp@gmail.com">mcgrady.jp@gmail.com</a>
        for more information. </p>
    </li>
</ul>
"""

strLicence = '<a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-ShareAlike 3.0 Unported License</a>'
