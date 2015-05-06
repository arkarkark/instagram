#!/usr/bin/python

import BaseHTTPServer
import PyRSS2Gen
import argparse
import datetime
import instagram # pip install python-instagram
import json
import jsonpickle # pip install jsonpickle
import logging
import os
import subprocess
import urllib
import urlparse
import jinja2

jinja_env = jinja2.Environment(
  loader=jinja2.PackageLoader('mirror', 'templates'),
)

def ParseArgs():
  """Parse all the command line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--data", help="Directory to write the data to.", default="data")
  parser.add_argument("-r", "--rss", help="Directory to write the rss feed to.", default="rss")
  parser.add_argument("-a", "--all", help="Loop through all posts by the user.",
                      action="store_true")

  parser.add_argument("user", nargs="+", help="Instagram user to get mirror for.")

  return parser.parse_args()

def SetupLogging():
  """Setup the logging system."""
  logging.basicConfig()
  logging.getLogger().setLevel(logging.ERROR)

  logger = logging.getLogger("instagram")
  logger.setLevel(logging.DEBUG)
  return logger

args = ParseArgs() # pylint: disable=invalid-name
log = SetupLogging() # pylint: disable=invalid-name


ALL_DONE_WITH_HTTPD = False

def GetUser(api, username):
  """Get a user object for a given username."""
  answers = api.user_search(q=username, count=10)
  for answer in answers:
    if answer.username == username:
      log.info("Found: %r", username)
      return answer
  return None

def PrettyJson(j):
  """Turn ugly json into pretty JSON."""
  return json.dumps(json.loads(j), sort_keys=True, indent=2, separators=(",", ": "))

def StoreMedia(dirname, recent_media):
  """Store each media item in dirname."""
  for media in recent_media:
    print media.id + ((media.caption and (" " + media.caption.text)) or "")
    filename = os.path.join(dirname, media.id + ".json")
    open(filename, "w").write(PrettyJson(jsonpickle.encode(media)))
    url = media.get_standard_resolution_url()
    extension = os.path.splitext(url)[1] or ".bin"
    filename = os.path.join(dirname, media.id + extension)
    if not os.path.exists(filename):
      open(filename, "w").write(urllib.urlopen(url).read())

def GenerateRss(filename, user, recent_media):
  """Generate an rss feed for this user."""
  rss = PyRSS2Gen.RSS2(
      title=user.full_name,
      link="https://instagram.com/%s" % user.username,
      description="Instagram RSS feed for %s (%s)" % (user.username, user.full_name),
      lastBuildDate=datetime.datetime.now(),
      items=[GenerateRssItem(item) for item in recent_media])

  rss.write_xml(open(filename, "w"))

def GenerateRssItem(item):
  """Make an rss item from a media object."""
  x = PrettyJson(jsonpickle.encode(item))
  if "Wheee" in x:
    print x
  title = [item.user.username]
  if item.caption:
    title.append(item.caption.text)
  return PyRSS2Gen.RSSItem(
      title=":".join(title),
      link=item.link,
      description=GenerateItemHtml(item),
      guid=item.id,
      pubDate=item.created_time or datetime.datetime().now()
  )

def GenerateItemHtml(item):
  """Turn an media item into html."""
  return jinja_env.get_template("item.html").render(item=item)

def GetItems(api, username):
  """Get all the items for a username."""
  user = GetUser(api, username)
  if user and user.id:
    dirname = os.path.join(args.data, username)
    if not os.path.exists(dirname):
      os.makedirs(dirname)

    next_ = None
    rss_items = []
    while True:
      recent_media, next_ = api.user_recent_media(user_id=user.id, count=100, with_next_url=next_)
      rss_items.extend(recent_media)
      StoreMedia(dirname, recent_media)
      if not args.all or not next_:
        break
    if args.rss:
      GenerateRss(os.path.join(args.rss, username + ".xml"), user, rss_items)


def Mirror(api):
  log.info("I'm going to mirror now!")
  for user in args.user:
    GetItems(api, user)


def InstagramAuthenticate(callback):
  """Get some instagram access codes either from a file or via oauth type dance."""

  access_token = None

  if os.path.exists("access_token"):
    access_token = open("access_token").read().strip()

  port = 1968
  client_id, secret = open("client.secret").read().strip().split(",")
  url = "http://localhost:%d/authorized" % port

  if access_token:
    log.info("re using access token from disk")

    callback(instagram.client.InstagramAPI(client_id=client_id, client_secret=secret, access_token=access_token))
  else:
    log.info("getting access token via web browser")

    scope = ["basic"]

    api = instagram.client.InstagramAPI(client_id=client_id, client_secret=secret, redirect_uri=url)
    authorize_url = api.get_authorize_login_url(scope=scope)

    log.info("Opening: %s", authorize_url)
    subprocess.call(["open", authorize_url])

    def UseCode(code):
      """Turn the code from the oauth dance into an access token, store it and call the callback."""
      log.info("Go code! %r", code)
      access_token, user_info = api.exchange_code_for_access_token(code)
      log.info("user_info: %r", user_info)
      open("access_token", "w").write(access_token)
      callback(instagram.client.InstagramAPI(client_id=client_id, client_secret=secret, access_token=access_token))

    class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
      """Simple http server to do the oauth dance."""
      def do_GET(self):  # pylint: disable=invalid-name
        """handle a get reuqest method to parse out the code."""
        if self.path.startswith("/authorized"):
          self.wfile.write("<script>window.close();</script>")
          log.info(urlparse.urlparse(self.path).query)
          code = urlparse.parse_qs(urlparse.urlparse(self.path).query)["code"][0]
          global ALL_DONE_WITH_HTTPD  # pylint: disable=global-statement
          ALL_DONE_WITH_HTTPD = True
          UseCode(code)

    httpd = BaseHTTPServer.HTTPServer(("localhost", port), MyHandler)
    while not ALL_DONE_WITH_HTTPD:
      httpd.handle_request()

def Main():
  """Main."""
  InstagramAuthenticate(Mirror)


if __name__ == "__main__":
  Main()
