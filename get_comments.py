################
# Python script to read a list of video
# id's collected using get_videos.py
# and collect comments and user info
# Alex Rutherford 2014
################

import csv
import requests
import time,collections
import re
from utils import *

videoFile=csv.reader(open('videos.csv','r'),delimiter='\t')

logFile=csv.writer(open('log_.csv','a'),delimiter='\t')
# Log file for requests

outFile=csv.writer(open('out_.csv','w'),delimiter='\t')
# Out file for saving content

startTime=time.mktime(time.localtime())

authors=collections.OrderedDict()

verbose=True
vverbose=True

###############################
for line in videoFile:

  print line[0]

  nComments=0

  commentsLink='https://gdata.youtube.com/feeds/api/videos/'+line[0]+'/comments?v=2'

  print commentsLink

  try:
    commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
    logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50'])
  except:
    print 'REQUEST FAILED'
    print '(URL='+commentsLink+')'
    logFile.writerow([getTime(startTime),'REQUEST FAILED',commentsLink])

  if re.search(r'Commenting is disabled for this video.',commentsRaw.text):
    print 'COMMENTS DISABLED'
    logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50','COMMENTS DISABLED'])
  else:

    while commentsRaw.status_code in [403,500,503]:
      print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....',
      print commentsRaw.status_code
      print commentsRaw.text
      print getTime(startTime)
      time.sleep(60)
      commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
      logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50'])

    try:
      comments=commentsRaw.json()
    except:
      print commentsRaw
      sys.exit(1)

    if 'entry' in comments['feed'].keys():
    # If there are any comments

      if verbose:print '\t\t',len(comments['feed']['entry']),'COMMENTS IN TOTAL'

      for c,comm in enumerate(comments['feed']['entry']):
        if 'author' in comm.keys():
          if verbose:print '\t\t\tCOMMENT',c
          if verbose:print '\t\t\tAUTHOR',#comm['author'],type(comm['author']),type(comm['author'][0])
          if verbose:print comm['author'][0]['name']['$t'],comm['author'][0]['yt$userId']['$t']
          if not comm['author'][0]['yt$userId']['$t']=='__NO_YOUTUBE_ACCOUNT__':
            if not comm['author'][0]['yt$userId']['$t'] in list(authors.keys()):
              authorInfo=getAuthorInfo(comm['author'][0]['yt$userId']['$t'])
              authors[comm['author'][0]['yt$userId']['$t']]=authorInfo
            else:
              authorInfo=authors[comm['author'][0]['yt$userId']['$t']]
              logFile.writerow([getTime(startTime),'AUTHOR TAKEN FROM DICT'])
              if verbose:print '\t\t\t(GOT FROM DICT)'
            if vverbose:print '\t\t\t',authorInfo
          # Get author info

            outFile.writerow(['AUTHOR INFO',comm['author'][0]['name']['$t'].encode('utf-8'),authorInfo.encode('utf-8').replace('\n','|')])
          else:
            outFile.writerow(['AUTHOR INFO','__NO_YOUTUBE_ACCOUNT__'])
          outFile.writerow(['COMMENT',comm['content']['$t'].replace('\n','|').encode('utf-8'),comm['author'][0]['name']['$t'].encode('utf-8'),comm['author'][0]['yt$userId']['$t'].encode('utf-8')])

        if vverbose:print '\t\t\tCONTENT',comm['content']['$t']
        if verbose:print ' '
        # Get comment text
        nComments+=1
    else:
      if verbose:print '\t\tNO COMMENTS YET '#'- entry NOT IN KEYS',comments['feed'].keys()
