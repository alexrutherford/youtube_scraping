###################
# Some convenience functions used
# in get_comments.py
# Alex Rutherford 2014
###################

import requests
import time

secsInHour=60*60

######
def getTime(startTime):
######
  diff=int(time.mktime(time.localtime())-startTime)
  hours=int(diff/(secsInHour))
  minutes=int((diff-(secsInHour*hours))/60)
  secs=diff-((hours*secsInHour)+(minutes*60))
  return time.strftime("%d %B %H:%M:%S", time.localtime())+' ('+str(hours)+':'+str(minutes)+':'+str(secs)+')'
######
def getAuthorInfo(id):
######
# Takes a user id and returns location and summary

  try:
    dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json')
    logFile.writerow([getTime(),'http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json'])
  except:
    print '\t\tAUTHOR INFO REQUEST FAILED'

#  while dRaw.status_code in [403,503]:
  while not dRaw.status_code in [200,201]:
    print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....',
    logFile.writerow([getTime(),'API UNAVAILABLE',dRaw.status_code,dRaw.text])
    print dRaw.status_code
    print dRaw.text
    print getTime()
    time.sleep(60)
    dRaw=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json')
    logFile.writerow([getTime(),'http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json'])

  d=dRaw.json()

  if 'yt$location' in d['entry'].keys():
    returnString=d['entry']['yt$location']['$t']
  else:
    returnString='<NO LOCATION>'

  if 'summary' in d['entry'].keys() and '$t' in d['entry']['summary'].keys():
    returnString=returnString+'\n'+d['entry']['summary']['$t']
  else:
    returnString=returnString+'<NO SUMMARY>'
  return returnString
