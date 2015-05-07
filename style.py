import os
import urllib

# pylint: disable=invalid-name
table = "width: 640px; font-family: 'proxima-nova','Helvetica Neue',Arial,Helvetica,sans-serif;"
td = "border-bottom: 1px solid #ddd; box-shadow: 0 1px 1px rgba(0,0,0,.06); padding: 11px 0 12px 0;"
profile_img = "float: left; width: 80px; height: 80px; margin-right: 20px; margin-bottom: 20px;"
user_link = "font-size: 18px; font-weight: 700; text-decoration: none;"
time_text = "font-size: 18px; font-weight: 500; color: #81868a;"
caption_text = "font-size: 18px; font-weight: 500;"
like_user_text = "font-size: 18px; font-weight: 500; text-decoration: none;"
comment_profile_img = "float: left; width: 40px; height: 40px; margin-right: 10px; margin-bottom: 20px;"
comment_user_link = "font-size: 18px; font-weight: 700; color: #3f729b; text-decoration: none"
comment_text = "margin-left: 50px;"

heart_html = """<span style="color: #81868a;">&hearts;</span>"""

map_api_key = None

if os.path.exists("map_api_key"):
  map_api_key = open("map_api_key").read().strip()

def map_html(lat, lon):
  """Make a map link."""
  latlon = ",".join(map(str, [lat, lon]))
  values = {
      "api_url": "https://maps.googleapis.com/maps/api/staticmap",
      "latlon": latlon,
      "params": urllib.urlencode({
          "center": latlon,
          "key": map_api_key,
          "zoom": 12,
          "markers": latlon,
          "size": "320x320",
      }),
      "map_url": "http://maps.google.com/maps",
      "maps_params": urllib.urlencode({
          "ll": latlon,
          "t": "m",
          "z": 12,
          "q": latlon,
      }),
  }
  html = """<a target="_blank" href="%(map_url)s?%(maps_params)s"><img src="%(api_url)s?%(params)s"></a>"""
  return html % values

def streetview_html(lat, lon, heading):
  """Make a streetview link."""
  latlon = ",".join(map(str, [lat, lon]))
  values = {
      "api_url": "https://maps.googleapis.com/maps/api/streetview",
      "latlon": latlon,
      "params": urllib.urlencode({
          "heading": heading,
          "key": map_api_key,
          "location": latlon,
          "markers": latlon,
          "size": "160x160",
          "zoom": 12,
      }),
      "map_url": "http://maps.google.com/maps",
      "maps_params": urllib.urlencode({
          "q": latlon,
          "layer": "c",
          "cbll": latlon,
          "cbp": "12,%d,0,0,5" % heading
      }),
  }
  html = """<a target="_blank" href="%(map_url)s?%(maps_params)s"><img src="%(api_url)s?%(params)s"></a>"""
  return html % values

def user_url(username):
  """Get a user's url."""
  return "https://instagram.com/%s/" % username
