################
# Python script to read a list of video
# id's collected using get_videos.py
# and collect comments and user info
# Alex Rutherford 2014
################

import csv
import requests
import time,collections
import re,sys
from utils import *
import glob

restartSkip=False
# To restart from a specific video in a file
writeAppendFlag='w'
# Write to file anew by default, if restarting then append
restartId=''
# Id to restart in specific video

if '-r' in sys.argv:
  index=(sys.argv).index('-r')
  restartId=sys.argv[index+1]
  restartSkip=True
  writeAppendFlag='a'
#print restartId
#sys.exit(1)

if sys.argv[1]=='-i':
  videoFile=csv.reader(open(sys.argv[2],'r'),delimiter='\t')
  outFileName=sys.argv[2].partition('videos_')[2]
  outFileName='out_'+outFileName
  print 'WRITING COMMENTS TO',outFileName
  outFile=csv.writer(open(outFileName,writeAppendFlag),delimiter='\t')
  dictFileName=outFileName.replace('out_','dict_')

else:
  videoFile=csv.reader(open('videos.csv','r'),delimiter='\t')
  outFile=csv.writer(open('out.csv',writeAppendFlag),delimiter='\t')
  dictFileName='dict.csv'
  print 'WRITING COMMENTS TO out.csv'
videoFile.next()
# Get header

logFile=csv.writer(open('log.csv','a'),delimiter='\t')
# Log file for requests

startTime=time.mktime(time.localtime())

if dictFileName in glob.glob('*csv'):
  authors=readDict(dictFileName)
  print 'READING IN AUTHORS...'
else:
  authors=collections.OrderedDict()
  print 'NO AUTHORS FILE TO READ IN...'

verbose=True
#verbose=False
#vverbose=True
vverbose=False

nLine=0

###############################
for line in videoFile:

  if line[0]==restartId and restartSkip:
    print 'RESTARTING',restartId
    restartSkip=False
  elif restartSkip:
    print 'SKIPPING',line[0]

  if not restartSkip:

    print '-------------------------'
    print line[0],getTime(startTime)
    outFile.writerow(['VIDEO',line[0]])
    errorSkip=False
    nError=0

    nComments=0

    commentsLink='https://gdata.youtube.com/feeds/api/videos/'+line[0]+'/comments?v=2'

    print 'VIDEO #',nLine,commentsLink

    try:
      commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
      logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50'])
    except:
      print 'REQUEST FAILED'
      print '(URL='+commentsLink+')'
      logFile.writerow([getTime(startTime),'REQUEST FAILED',commentsLink])

    if re.search(r'Commenting is disabled for this video|User authentication required|ResourceNotFoundException',commentsRaw.text,flags=re.UNICODE):
      print 'COMMENTS DISABLED OR AUTHENTICATION REQUIRED OR VIDEO REMOVED',commentsRaw.text
      logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50','COMMENTS DISABLED/VIDEO REMOVED',commentsRaw.status_code])
      errorSkip=True
    else:

      while commentsRaw.status_code in [403,404,500,503,400]:
        print 'TOO MANY REQUESTS OR API UNAVAILABLE! SLEEPING....'
        print commentsRaw.text
        print commentsRaw.status_code,
        print getTime(startTime)
        logFile.writerow([getTime(startTime),commentsRaw.status_code,commentsRaw.text,commentsLink+'&alt=json&max-results=50'])
        time.sleep(60)
        if nError==10:
          errorSkip=True
          break
        nError+=1
        commentsRaw=requests.get(commentsLink+'&alt=json&max-results=50')
        logFile.writerow([getTime(startTime),commentsLink+'&alt=json&max-results=50'])
      if not errorSkip:
        try:
          comments=commentsRaw.json()
        except:
          print 'EXCEPTION'
          print commentsRaw
          sys.exit(1)
    if not errorSkip:
        if 'entry' in comments['feed'].keys():
        # If there are any comments

          if verbose:print '\t\t',len(comments['feed']['entry']),'COMMENTS IN TOTAL'

          for c,comm in enumerate(comments['feed']['entry']):

            #sys.exit(1)
            if 'author' in comm.keys():
              if verbose:print '\t\t\tCOMMENT #',c
              if verbose:print '\t\t\tAUTHOR',#comm['author'],type(comm['author']),type(comm['author'][0])
              if verbose:print comm['author'][0]['name']['$t'],comm['author'][0]['yt$userId']['$t']
              if not comm['author'][0]['yt$userId']['$t']=='__NO_YOUTUBE_ACCOUNT__':
                if not comm['author'][0]['yt$userId']['$t'] in list(authors.keys()):
                  authorInfo=getAuthorInfo(comm['author'][0]['yt$userId']['$t'],logFile,startTime)
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
              outFile.writerow(['COMMENT',comm['content']['$t'].replace('\n','|').encode('utf-8'),comm['author'][0]['name']['$t'].encode('utf-8'),comm['author'][0]['yt$userId']['$t'].encode('utf-8'),comm[u'published'][u'$t']])

            if vverbose:print '\t\t\tCONTENT',comm['content']['$t']
            if verbose:print ' '
            # Get comment text
            nComments+=1
        elif errorSkip:
          print 'FAILED TOO MANY TIMES: SKIPPING'
        else:
          if verbose:print '\t\tNO COMMENTS YET '#'- entry NOT IN KEYS',comments['feed'].keys()
  nLine+=1
print 'WRITING AUTHORS...',dictFileName
writeDict(authors,dictFileName)
print 'FINISHED'
