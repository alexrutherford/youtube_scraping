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

outFile=csv.writer(open('videos.csv','w'),delimiter='\t')

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

startDate='2014-03-01T00:00:00Z'
print startDate

startDates=[str(y)+'-03-01T00:00:00Z' for y in range(2000,2013)]
endDates=[str(y)+'-03-01T00:00:00Z' for y in range(2001,2014)]
# Years

startDates=['2013-'+str(m)+'-01T00:00:00Z' for m in range(1,12)]
endDates=['2013-'+str(m)+'-01T00:00:00Z' for m in range(2,13)]
# Months

startDates=['2014-03-'+str(d).zfill(2)+'T00:00:00Z' for d in range(1,30)]
endDates=['2014-03-'+str(d).zfill(2)+'T00:00:00Z' for d in range(2,31)]
# Days - March

# First 6 days of april gave 426 results

QUERY=u'Italy'
KEY=''
# API key

for startDate,endDate in zip(startDates,endDates):

  nResults=0
  nDuplicate=0

  print 'DATES',startDate,' - ',endDate

##############
  data=requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key='+KEY+'&maxResults=50&type=video&publishedBefore='+endDate+'&publishedAfter='+startDate)

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

    data=requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&q='+QUERY+'&key=AIzaSyDJK0-GmyE9re8ahNGu5bR5cvqWATXlh44&maxResults=50&type=video&'+'pageToken='+d['nextPageToken']+'&publishedBefore='+endDate+'&publishedAfter='+startDate)

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
