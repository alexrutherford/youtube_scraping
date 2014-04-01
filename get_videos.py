# coding: utf-8
import json
import sys
import requests
import time

videos=[]

QUERY='football'
# q parameter matches 'titles, keywords, descriptions, authors' usernames, and categories'
# https://developers.google.com/youtube/2.0/developers_guide_protocol_api_query_parameters
# Version 3 doesn't support comments, version 2 currently deprecated

# http://gdata.youtube.com/feeds/api/videos?v=2&alt=json&location=36.29,33.51!&location-radius=100km
# Location search

######
def getAuthorInfo(id):
######

  d=requests.get('http://gdata.youtube.com/feeds/api/users/'+id+'?v=2&alt=json').json()

  returnString=d['entry']['yt$location']['$t']+'\n'+d['entry']['summary']['$t']

  return returnString

########
def main():
########

  for START in [1+(i*50) for i in range(100)]:

    print 'FROM',START

    d=requests.get('https://gdata.youtube.com/feeds/api/videos?q='+QUERY+'&orderby=published&max-results=50&v=2&alt=json&start-index='+str(START))

    success=False

    while not success:

      try:
        data=d.json()
        success=True
      except:
        print 'ERROR',
        print d,
        print d.json()
        time.sleep(10)
        print 'RETRYING'

    for n,e in enumerate(data['feed']['entry']):
      videoID=e['id']['$t'].split('video')[-1]

      print '-----------------------------'
      print '\tVIDEO NUMBER',n,videoID
#    for k,v in e.items():
#      print 'KEY=>',k

      try:
# Are comments enabled?
        commentsLink=e['gd$comments']['gd$feedLink']['href']
        x=requests.get(commentsLink+'&alt=json&max-results=50').json()
        if 'entry' in x['feed'].keys():
# If there are any comments
#        print len(x['feed']['entry'])
#        print type(x['feed']['entry'])
#        print ' '
          print '\t\t',len(x['feed']['entry']),'COMMENTS IN TOTAL'
          for c,comm in enumerate(x['feed']['entry']):
#          print '!!!!',type(comm)
            if 'author' in comm.keys():
              print '\t\t\tCOMMENT',c
              print '\t\t\tAUTHOR',#comm['author'],type(comm['author']),type(comm['author'][0])
              print comm['author'][0]['name']['$t'],comm['author'][0]['yt$userId']['$t']
              print '\t\t\t',getAuthorInfo(comm['author'][0]['yt$userId']['$t'])
#            for k,v in comm['author'][0].items():
#              print '\t\tAUTHOR KEY',k

#          print 'COMM',c#,comm
#          for k,v in comm.items():
#            print '\tKEY=>',k
            print '\t\t\tCONTENT',comm['content']['$t']
            print ' '
#        sys.exit(1)
        else:
          print '\t\tNO COMMENTS'
      except:
        print '\t\tCOMMENTS DISABLED' 
      if not videoID in videos:
        videos.append(videoID)
      else:
        print 'DUPLICATE'
#        sys.exit(1)

######## 
if __name__=='__main__':
  main()   
