import csv


def calc_fpa(row, index):
    if row[index + 5] == "YES":
        return "Adv"
    elif row[index + 4] == "YES":
        return "Pass"
    else:
        return "Fail"
# E1 = 60
# name, date, scale, raw, fpa
def getScores(kid, index):
    if index == 60: test = "English 1"
    if index == 90: test = "English 2"
    if index == 120: test = "Algebra 1"
    if index == 130: test = "Biology"
    if index == 140: test = "US History"
    if kid[index] != "":
        return test + " | " + kid[index] + " | " + kid[index + 2] + " | " + kid[index + 3] + " | " + calc_fpa(kid, index)
    else:
        return "Student has not taken the " + test + " STAAR test."

def read_a4e(path):
    with open(path, 'r', encoding="utf8") as bigfile:
        readbigfile = csv.reader((line.replace('\0','') for line in bigfile), delimiter=",", quotechar='"')
        temparray = list(readbigfile)
        for row in temparray:
            try:
                if len(row) == 0:
                    temparray.remove(row)
            except UnicodeDecodeError:
                continue
    data_dict = {}
    for kid in temparray:
        data_dict[kid[0]] = [kid[0] + " | " + kid[1] + ', ' + kid[2] + " | " + kid[3], # 0 ID, Last First, Grade
                             getScores(kid, 60),        # 1 [English 1, date, scale, raw, fpa]
                             getScores(kid, 90),        # 2 [English 2, date, scale, raw, fpa]
                             getScores(kid, 120),       # 3 [Algebra 1, date, scale, raw, fpa]
                             getScores(kid, 130),       # 4 [Biology, date, scale, raw, fpa]
                             getScores(kid, 140)]       # 5 [US History, date, scale, raw, fpa]
    return data_dict

data = read_a4e('data/staar data noheader.csv')