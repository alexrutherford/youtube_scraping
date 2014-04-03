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
##Requirements

Requires requests library
