Python script to extract comment text from videos matching a keyword search.

Uses YouTube API v2 (currently deprecated), doesn't require API key

##Pseudocode

Basic program flow is as follows

```
for video in search(keyword):
  log(video,getLocation(video))

  for comment in getComments(video):
    log(getAuthor(comment),getLocation(getAuthor(comment)),comment)
```
Most code is to catch API errors and to sleep if too many requests are being made

##Options
Variable|Description
--------|------------
QUERY|Keyword(s) to build list of videos, can include Boolean operators [documentation](https://developers.google.com/youtube/2.0/developers_guide_protocol_api_query_parameters#qsp)
v,vv|Flags to log verbosely(v) and very verbosely (vv) to screen. For debugging

##Output Files

*log.csv* stores record of API requests for debugging and understanding API behaviour
*out.csv* stores 

1.Video title, author and id (URL is youtube.com/watch?v=<id>)
2.Comment, comment author information (summary, location and display name)

##Known Issues

The search API will often return duplicate videos when paging through the search results past the first 500 videos. It is possible that the same video is listed twice; once as an original and again when placed in a playlist. There may be new results listed on later pages however ([discussion here](https://code.google.com/p/gdata-issues/issues/detail?id=3979))

##Requirements

Requires [requests](http://docs.python-requests.org/en/latest/) library
