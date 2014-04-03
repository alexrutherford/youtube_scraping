# coding: utf-8
######################
# Script to extract YouTube comment text
# from videos matching a keyword search
# Alex Rutherford 2014
######################
import json
import sys
import requests
import time
import csv
import collections

logFile=csv.writer(open('log.csv','a'),delimiter='\t')
# Log file for requests

outFile=csv.writer(open('out.csv','w'),delimiter='\t')
# Out file for saving content

videos=[]
nComments=0

authors=collections.OrderedDict()

v=False
vv=False
# Flags for printing extra info to console
# v is verbose, vv is very verbose

QUERY='Italy'
# q parameter matches 'titles, keywords, descriptions, authors' usernames, and categories'
# https://developers.google.com/youtube/2.0/developers_guide_protocol_api_query_parameters#qsp
# Version 3 doesn't support comments, version 2 currently deprecated

# http://gdata.youtube.com/feeds/api/videos?v=2&alt=json&location=36.29,33.51!&location-radius=100km
# Location search

startTime=time.mktime(time.localtime())

secsInHour=60*60

######
def getTime():
######
  global startTime
  global secsInHour
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

########
def main():
########

  global nComments
  global authors

  d=requests.get('https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index=1')
  logFile.writerow([getTime(),'https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index=1'])

  nextLink='FIRST'
  nPage=0

  while nextLink:
  # Loops through all matching videos in batches of 50

    if not nextLink=='FIRST':
      d=requests.get(nextLink)
      logFile.writerow([getTime(),nextLink])
    else:
      nextLink='https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index=1'
    # Follow the link to next page
    # If not first page

    success=False
    nFail=0

    while not success:
    # If API returns an error; retry
      try:
        data=d.json()
        success=True
      except:
        print 'ERROR',
        print d,d.text,
        logFile.writerow([getTime(),'API ERROR',d,d.text])
        time.sleep(60)
        print 'RETRYING'
        nFail+=1
        if nFail==10:
          print 'SKIPPING'
          print 'https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index='+str(START)
          logFile.writerow([getTime(),'SKIPPING','https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index='+str(START)])
          sys.exit(1)

    nextLink=None

    for n,e in enumerate(data['feed']['entry']):
      videoID=e['id']['$t'].split('video:')[-1]
      # Get each video ID => https://www.youtube.com/watch?v=<videoId>
      if v or (not v and n%50==0):
        print '-----------------------------'
        print '\tVIDEO NUMBER',n+nPage*50,videoID
        print getTime()
      outFile.writerow('\n')
      outFile.writerow(['VIDEO NUMBER',n+nPage*50,videoID,getTime()])

      if v:print '\t',nComments,'COMMENTS SO FAR',
      try:
        coords=e['georss$where']['gml$Point']['gml$pos']['$t']
        if v:print '\n\tCOORDS',coords
        outFile.writerow(['COORDS',coords])
      except:
        if v:print 'NO COORDS'

      if 'gd$comments' in e.keys():

        commentsLink=e['gd$comments']['gd$feedLink']['href']

        try:
          commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
          logFile.writerow([getTime(),commentsLink+'&alt=json&max-results=50'])
        except:
          print 'REQUEST FAILED'
          print '(URL='+commentsLink+')'
          logFile.writerow([getTime(),'REQUEST FAILED',commentsLink])

        while commentsRaw.status_code in [403,500,503]:
          print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....',
          print commentsRaw.status_code
          print commentsRaw.text
          print getTime()
          time.sleep(60)
          commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
          logFile.writerow([getTime(),commentsLink+'&alt=json&max-results=50'])

        try:
          comments=commentsRaw.json()
        except:
          print commentsRaw
          sys.exit(1)

        if 'entry' in comments['feed'].keys():
        # If there are any comments

          if v:print '\t\t',len(comments['feed']['entry']),'COMMENTS IN TOTAL'

          for c,comm in enumerate(comments['feed']['entry']):
            if 'author' in comm.keys():
              if v:print '\t\t\tCOMMENT',c
              if v:print '\t\t\tAUTHOR',#comm['author'],type(comm['author']),type(comm['author'][0])
              if v:print comm['author'][0]['name']['$t'],comm['author'][0]['yt$userId']['$t']
              if not comm['author'][0]['yt$userId']['$t']=='__NO_YOUTUBE_ACCOUNT__':
                if not comm['author'][0]['yt$userId']['$t'] in list(authors.keys()):
                  authorInfo=getAuthorInfo(comm['author'][0]['yt$userId']['$t'])
                  authors[comm['author'][0]['yt$userId']['$t']]=authorInfo
                else:
                  authorInfo=authors[comm['author'][0]['yt$userId']['$t']]
                  logFile.writerow([getTime(),'AUTHOR TAKEN FROM DICT'])
                  if v:print '\t\t\t(GOT FROM DICT)'
                if vv:print '\t\t\t',authorInfo
              # Get author info

                outFile.writerow(['AUTHOR INFO',authorInfo.encode('utf-8').replace('\n','|')])
              else:
                outFile.writerow(['AUTHOR INFO','__NO_YOUTUBE_ACCOUNT__'])
              outFile.writerow(['COMMENT',comm['content']['$t'].replace('\n','|').encode('utf-8'),comm['author'][0]['name']['$t'].encode('utf-8'),comm['author'][0]['yt$userId']['$t'].encode('utf-8')])

            if vv:print '\t\t\tCONTENT',comm['content']['$t']
            if v:print ' '
            # Get comment text
            nComments+=1
        else:
          if v:print '\t\tNO COMMENTS YET '#'- entry NOT IN KEYS',comments['feed'].keys()
      else:
        if v:print '\t\tNO COMMENTS - gd$comments NOT IN KEYS'
        #### Does this just mean comment not available via API yet?
        #### Or need permissions?

      if not videoID in videos:
        videos.append(videoID)
        # Store all new videos
      else:
        if True:print 'DUPLICATE',n,videoID
#        sys.exit(1)
        # Ignore duplicates
    try:
      nextLink=data['feed']['link'][-1]['href']
      nPage+=1
      if v:print 'GOING TO NEXT PAGE....'
    except:
      if v:print 'NO NEXT PAGE :-(',data['feed']['link']
      time.sleep(60)

########
if __name__=='__main__':
  main()
