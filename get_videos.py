# coding: utf-8
##################
# Script using YouTube API v3
# to collect videos matching a keyword search
# Cycles through each day/month of a date range to
# avoid hitting API limit and missing videos
# Alex Rutherford 2014
##################
import json
import requests
import time
import sys
import csv
from utils import *
from datetime import date,datetime
from dateutil.rrule import rrule, DAILY, HOURLY

startTime=time.mktime(time.localtime())

outFile=None

logFile=csv.writer(open('log.csv','a'),delimiter='\t')
# Log file for requests

verbose=True
verbose=False

nPages=0
videos=[]

#######
def writeVideo(video):
#######
  global outFile
  outFile.writerow([video['id']['videoId'],video['snippet']['channelTitle'].encode('utf-8'),video['snippet']['title'].encode('utf-8'),video['snippet']['publishedAt']])
# ID, channel title, video title, time

#################
def main():
#################

  global outFile

  startDate=date(2014,1,1)
  endDate=date(2014,4,7)

  if False:
  # Daily filtering
    startDates=[d for d in rrule(DAILY,dtstart=date(2014,1,1),until=date(2014,4,6))]
    startDates=[d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in startDates]
    endDates=[d for d in rrule(DAILY,dtstart=date(2014,1,2),until=date(2014,4,7))]
    endDates=[d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in endDates]
  else:
  # Hourly filtering; in case query overflows past 500
    startDates=[d for d in rrule(HOURLY,dtstart=datetime(2014,1,1,0,0,0),until=datetime(2014,4,6,22,0,0))]
    startDates=[d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in startDates]
    endDates=[d for d in rrule(HOURLY,dtstart=datetime(2014,1,1,1,0,0),until=datetime(2014,4,7,23,0,0))]
    endDates=[d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in endDates]

  print startDates[0:10]
  print endDates[0:10]
#  sys.exit(1)

  QUERY=u'Italy'

  KEY=''

  outFile=csv.writer(open('videos_'+QUERY.encode('utf-8')+'.csv','w'),delimiter='\t')
  print 'WRITING VIDEO IDs TO','videos_'+QUERY.encode('utf-8')+'.csv'

  outFile.writerow([getTime(startTime),QUERY.encode('utf-8'),startDate,endDate])
  # Write details of query as a header

  for startDate,endDate in zip(startDates,endDates):
  # Loop over days and get videos
    nResults=0
    nDuplicate=0
    nPages=0

    print 'DATES',startDate,' - ',endDate
    print 'QUERY',QUERY
    ##############
    requestString='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&publishedBefore='+endDate+'&publishedAfter='+startDate
    data=requests.get(requestString)
    logFile.writerow([getTime(startTime),requestString.encode('utf-8')])

    d=data.json()

    if data.status_code in [403,500,503]:
      print data.text
      sys.exit(1)

    for v,video in enumerate(d['items']):
      if verbose: print '\tADDED',v,video['id']
      videos.append(video['id']['videoId'])
      writeVideo(video)
      nResults+=1

    print nResults,'RESULTS',nDuplicate,'DUPLICATES'
    ##############
    while 'nextPageToken' in d.keys():
      if len(d['items'])>0:print nPages,'NEXT',d['nextPageToken'],nDuplicate,d['items'][0]['id']['videoId']
      requestString='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&'+'pageToken='+d['nextPageToken']+'&publishedBefore='+endDate+'&publishedAfter='+startDate
      data=requests.get(requestString)
      logFile.writerow([getTime(startTime),requestString.encode('utf-8')])

      while u'error' in data.json().keys():
        print 'ERROR GETTING RESULTS. SLEEPING...'
        time.sleep(60)
        data=requests.get(requestString)
        logFile.writerow([getTime(startTime),requestString.encode('utf-8')])

      d=data.json()

      print '\t',len(d['items'])

      for v,video in enumerate(d['items']):
        if False:print '\t',v,video['id'],'('+str(len(videos))+')'
        if video['id']['videoId'] in videos:
          if verbose:print '******DUPLICATE',video['id']['videoId']
#          break
          nDuplicate+=1
        else:
          videos.append(video['id']['videoId'])
          writeVideo(video)
        nResults+=1
      nPages+=1
    print 'SUMMARY',nResults,'RESULTS',nDuplicate,'DUPLICATES',getTime(startTime)
    print '----------------'
  print 'FINISHED'

if __name__=='__main__':
  main()
