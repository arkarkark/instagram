#!/usr/bin/python
# Copyright 2014 Alex K (wtwf.com)
"""
get a whole bunch of instagram api calls

I've used it to get feeds for my subscriber list like this

get a curl command from network tab in chrome dev console

then call this like this

./api_get_all.py  -u 'https://www.instagram.com/graphql/query/?query_id=1...&id=1...&first=20'  -- \
  -H 'accept-encoding: gzip, deflate, sdch, br' -H 'x-req.............

NOTE the -- and all the curl arguments come after that...

```
for fil in out*.json; do wgrep -mq "$.data.user.edge_follow.edges[*].node.username" $fil; done |
while read un; do if [ ! -z "$un" ]; then
  if wget -O /tmp/$$.wget "https://www.instagram.com/$un/media/" && [ "$(wc -c </tmp/$$.wget)" -ge 99 ]; then
    open "https://feedly.com/i/subscription/feed/http://feeds.wtwf.com/public/data/instagram/feed/$un";
    open "https://www.instagram.com/$un/"
  fi
fi; done
```

"""

__author__ = 'wtwf.com (Alex K)'

import getopt
import logging
import os
import sys
import urllib
import urlparse
import json
import subprocess

def Usage(code, msg=''):
  """Show a usage message."""
  if code:
    output = sys.stderr
  else:
    output = sys.stdout
  PROGRAM = os.path.basename(sys.argv[0]) # pylint: disable=invalid-name,unused-variable
  print >> output, __doc__ % locals()
  if msg:
    print >> output, msg
  sys.exit(code)

def Main():
  """Run."""
  logging.basicConfig()
  logging.getLogger().setLevel(logging.DEBUG)

  args = []
  curl_args = None

  for arg in sys.argv[1:]:
    if arg == "--":
      curl_args = []
    else:
      if curl_args is None:
        args.append(arg)
      else:
        curl_args.append(arg)

  try:
    opts, args = getopt.getopt(args, 'hu:', 'help,url'.split(','))
  except getopt.error, msg:
    Usage(1, msg)

  if args:

    Usage(1, "don't know what to do with: %r" % args)

  url = None
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      Usage(0)
    if opt in ('-u', '--url'):
      url = arg

  if not url:
    Usage(2, 'you must provide a url')

  Run(url, curl_args)

def Run(url, curl_args=None, file_num=0):
  """Get the json for a url and maybe recurse if there is an end_cursor."""
  logging.info('url is: %r', url)

  if curl_args is None:
    curl_args = []

  output = 'out%02d.json' % file_num
  cmd = ['curl', '-o', output, url] + curl_args
  subprocess.call(cmd)

  result = json.load(open(output))
  end_cursor = None
  try:
    end_cursor = result["data"]["user"]["edge_follow"]["page_info"]["end_cursor"]
  except (KeyError, TypeError):
    print "no more"

  if end_cursor:
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query['first'] = 10
    query['after'] = end_cursor
    url_parts[4] = urllib.urlencode(query)
    url = urlparse.urlunparse(url_parts)
    Run(url, curl_args, file_num + 1)

if __name__ == '__main__':
  Main()
