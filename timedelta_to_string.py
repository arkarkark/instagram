#!/usr/bin/python
import datetime

# from http://stackoverflow.com/a/19074707

def HowLongAgo(date):
  """Describe how long ago this date was."""
  return TimedeltaToString(datetime.datetime.now() - date)

def TimedeltaToString(timedelta):
  """Convert a timedelta obect to a human readable string."""
  s = int(timedelta.total_seconds())
  years = s // 31104000
  if years > 1:
    return '%d years' % years
  s = s - (years * 31104000)
  months = s // 2592000
  if years == 1:
    r = 'one year'
    if months > 0:
      r += ' and %d months' % months
    return r
  if months > 1:
    return '%d months' % months
  s = s - (months * 2592000)
  days = s // 86400
  if months == 1:
    r = 'one month'
    if days > 0:
      r += ' and %d days' % days
    return r
  if days > 1:
    return '%d days' % days
  s = s - (days * 86400)
  hours = s // 3600
  if days == 1:
    r = 'one day'
    if hours > 0:
      r += ' and %d hours' % hours
    return r
  s = s - (hours * 3600)
  minutes = s // 60
  seconds = s - (minutes * 60)
  if hours >= 6:
    return '%d hours' % hours
  if hours >= 1:
    r = '%d hours' % hours
    if hours == 1:
      r = 'one hour'
    if minutes > 0:
      r += ' and %d minutes' % minutes
    return r
  if minutes == 1:
    r = 'one minute'
    if seconds > 0:
      r += ' and %d seconds' % seconds
    return r
  if minutes == 0:
    return '%d seconds' % seconds
  if seconds == 0:
    return '%d minutes' % minutes
  return '%d minutes and %d seconds' % (minutes, seconds)

if __name__ == "__main__":
  for i in range(10):
    print pow(8, i), timedelta_to_string(datetime.timedelta(seconds=pow(8, i)))
