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

# Summer school periods
per1b = datetime.strptime('08:00:00', '%H:%M:%S')
per1e = datetime.strptime('09:45:00', '%H:%M:%S')
per2e = datetime.strptime('11:35:00', '%H:%M:%S')
lunche = datetime.strptime('12:10:00', '%H:%M:%S')
per3e = datetime.strptime('14:00:00', '%H:%M:%S')
school_end = datetime.strptime('14:00:00', '%H:%M:%S')


def comm_school_day():
    now = datetime.now()
    if now >= school_end:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, school_end)) + " until school is out!"
    else:
        return "School was dismissed *%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(school_end, now)) + " ago!"

def comm_period():
    now = datetime.now()
    if now <= per1b and now >= per1e:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, per1e)) + " until the end of 1st period."
    elif now >= per2e:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, per2e)) + " until the end of 2nd period."
    elif now >= lunche:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, per1e)) + " until the end of 1st period."
    elif now >= per3e:
        return "*%d hours, %d minutes, %d seconds*" % \
           daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, per3e)) + " until the end of 3rd period."