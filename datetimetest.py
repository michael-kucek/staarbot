# Code borrowed from https://gist.github.com/morion4000/3866374
from datetime import datetime, time

def dateDiffInSeconds(date1, date2):
    timedelta = date2 - date1
    return timedelta.days * 24 * 3600 + timedelta.seconds

def daysHoursMinutesSecondsFromSeconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (hours, minutes, seconds)

leaving_date = datetime.strptime('14:00:00', '%H:%M:%S')


def comm_school_day():
    now = datetime.now()
    if now >= leaving_date:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)) + " until school is out!"
    else:
        return "School was dismissed *%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(leaving_date, now)) + " ago!"
