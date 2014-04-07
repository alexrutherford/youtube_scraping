# coding: utf-8
##################
# Script using YouTube API v3
# to collect videos matching a keyword search
# Cylces through each day of a date range to
# avoid hitting API limit and missing videos
# Alex Rutherford 2014
##################
import json
import requests
import time
import sys
import csv
from utils import *
from datetime import date
from dateutil.rrule import rrule, DAILY

startTime=time.mktime(time.localtime())

outFile=csv.writer(open('videos.csv','w'),delimiter='\t')

logFile=csv.writer(open('log_.csv','a'),delimiter='\t')
# Log file for requests

verbose=True
verbose=False

nPages=0
videos=[]

#######
def writeVideo(video):
#######
  outFile.writerow([video['id']['videoId'],video['snippet']['channelTitle'].encode('utf-8'),video['snippet']['title'].encode('utf-8'),video['snippet']['publishedAt']])
# ID, channel title, video title, time
#################

startDate=date(2014,1,1)
endDate=date(2014,4,7)

startDates=[d for d in rrule(DAILY,dtstart=date(2014,1,1),until=date(2014,4,6))]
startDates=[d.strftime("%Y-%m-%dT00:00:00Z") for d in startDates]
endDates=[d for d in rrule(DAILY,dtstart=date(2014,1,2),until=date(2014,4,7))]
endDates=[d.strftime("%Y-%m-%dT00:00:00Z") for d in endDates]

print startDates

QUERY=u''

KEY=''

outFile.writerow([getTime(startTime),QUERY.encode('utf-8'),startDate,endDate])
# Write details of query as a header

for startDate,endDate in zip(startDates,endDates):
# Loop over days and get videos
  nResults=0
  nDuplicate=0

  print 'DATES',startDate,' - ',endDate

##############
  requestString='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&publishedBefore='+endDate+'&publishedAfter='+startDate
  data=requests.get(requestString)
  logFile.writerow([getTime(startTime),requestString.encode('utf-8')])

  d=data.json()

  for v,video in enumerate(d['items']):
    if verbose: print '\tADDED',v,video['id']
    videos.append(video['id']['videoId'])
    writeVideo(video)
    nResults+=1

  print nResults,'RESULTS',nDuplicate,'DUPLICATES'
##############
  while 'nextPageToken' in d.keys():
    print nPages,'NEXT',d['nextPageToken'],nDuplicate,d['items'][0]['id']['videoId']
    requestString='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&'+'pageToken='+d['nextPageToken']+'&publishedBefore='+endDate+'&publishedAfter='+startDate
    data=requests.get(requestString)
    logFile.writerow([getTime(startTime),requestString.encode('utf-8')])

    d=data.json()

    print '\t',len(d['items'])

    for v,video in enumerate(d['items']):
      if False:print '\t',v,video['id'],'('+str(len(videos))+')'
      if video['id']['videoId'] in videos:
        if verbose:print '******DUPLICATE',video['id']['videoId']
        break
        nDuplicate+=1
      else:
        videos.append(video['id']['videoId'])
        writeVideo(video)
      nResults+=1
    nPages+=1
  print 'SUMMARY',nResults,'RESULTS',nDuplicate,'DUPLICATES'
  print '----------------'
