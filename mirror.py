#!/usr/bin/python

import logging
import os
import subprocess
import BaseHTTPServer
import urlparse
import jsonpickle
import urllib

import instagram

logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

log = logging.getLogger("instagram")  # pylint: disable=invalid-name
log.setLevel(logging.DEBUG)


ALL_DONE_WITH_HTTPD = False

def GetUser(api, username):
  answers = api.user_search(q=username, count=10)
  for answer in answers:
    if answer.username == username:
      log.info('Found: %r', username)
      return answer
  return None

def GetItems(api, username):
  user = GetUser(api, username)
  if user and user.id:
    dirname = os.path.join("data", username)
    if not os.path.exists(dirname):
      os.makedirs(dirname)
    recent_media, next_ = api.user_recent_media(user_id=user.id, count=100)
    for media in recent_media:
      print " ".join([username, media.id, (media.caption and (" " + media.caption.text)) or ""])
      filename = os.path.join(dirname, media.id)
      if not os.path.exists(filename):
        open(filename, "w").write(jsonpickle.encode(media))
      url = media.get_standard_resolution_url()
      extension = os.path.splitext(url)[1] or ".bin"
      filename = os.path.join(dirname, media.id + extension)
      if not os.path.exists(filename):
        open(filename, "w").write(urllib.urlopen(url).read())


def Mirror(api):
  log.info("I'm going to mirror now!")


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

    callback(instagram.client.InstagramAPI(client_id=client_id, client_secret=secret, access_token=access_token, redirect_uri=url))
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
      log.info('user_info: %r', user_info)
      open("access_token", "w").write(access_token)
      callback(instagram.client.InstagramAPI(client_id=client_id, client_secret=secret, access_token=access_token, redirect_uri=url))

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


if __name__ == '__main__':
  Main()
