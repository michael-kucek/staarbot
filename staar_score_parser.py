from PyPDF2 import PdfFileWriter, PdfFileReader
import sys # used for progress
import csv


def csv_reader(path):
    with open(path, 'r', encoding="utf8") as bigfile:
        readbigfile = csv.reader((line.replace('\0','') for line in bigfile), delimiter=",", quotechar='"')
        temparray = list(readbigfile)
        for row in temparray:
            if len(row) == 0:
                temparray.remove(row)
        return temparray

def dprint(dict):
    for thing in dict:
        print(thing, ":", dict[thing])

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress, text):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r" + text + ": [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def is_id(s):
    """Checks to see if s is a valid ID
    It must be either 9 digits or 'S' followed by 8 digits (always len == 9)
    """
    try:
        # truncate the first character (it may be S)
        int(s[1::])
        return True and len(s) == 9
    except ValueError:
        return False

# Returns a list of all valid pages of staar scores
# Each entry is an entire page that needs to be parsed
def readSTAARfile(filename):
    input = PdfFileReader(open(filename, 'rb'))
    print("scores.pdf has %d pages." % input.getNumPages())
    p = 0
    bigList = []
    index3list = []
    while p < input.getNumPages():
        # for old scores
        # currentPage = input.getPage(p).extractText()
        currentPage = input.getPage(p).extractText().split('\n')
        fixedPage = [x for x in currentPage if x != 'NOT TESTED-ABSENT' and x != 'NOT SCORED-PREVIOUSLY ACHIEVED LEVEL II: SATISFACTORY' and x != 'NOT SCORED']
        index3list.append(fixedPage[3])
        if fixedPage[3] == 'All Students':
            bigList.append(fixedPage)
        p += 1
        update_progress(p/input.getNumPages(), "Reading STAAR PDF")
    return bigList


def readSTAARscores(staarList):
    print("Cleaned up STAAR data has", len(staarList), 'pages')
    # create dictionary to store scores
    scoreDict = {}
    progress_index = 0
    progress_max = len(staarList)
    # for page in staarList:
    #     if page[2] not in scoreDict:
    #         scoreDict[page[2]] = [['peims', 'test', 'grade', 'scale', 'level II', 'level III']]
    tempScores = []
#   specific code to be generalized
#   replace the first [0] with p
    for page in range(len(staarList)):
        update_progress(progress_index/progress_max, "Parsing STAAR Scores")
        progress_index += 1
        tempPage = staarList[page]
        pageSubject = staarList[page][2]
        pageTest = staarList[page][0][-1]
        idIndexes = []
        finalIndex = 0
        for j in range(len(staarList[page])):
            if is_id(staarList[page][j]):
                idIndexes.append(j)
            elif staarList[page][j] == 'TOTAL STUDENTS LISTED: ':
                finalIndex = j + 3
        if finalIndex == 0:
            finalIndex = len(staarList[page])
        for index in range(len(idIndexes)):
            currentStudent = []
            # try/except block handles index out of range for finding where the student ends
            try:
                studentDiff = idIndexes[index + 1] - idIndexes[index]
            except IndexError:
                studentDiff = finalIndex - idIndexes[index]
            # need to add each piece of data to the current student up until the next id
            # minus 3 accounts for three name fields
            for looping in range(int(studentDiff) - 3):
                # what we need to check before adding
                currentData = staarList[page][idIndexes[index] + looping]
                if currentData != 'p':
                    currentStudent.append(currentData)
            # try block adds data back in if only 2 name fields were present
            try:
                lastData = int(staarList[page][idIndexes[index] + int(studentDiff) - 3])
                currentStudent.append(str(lastData))
            except ValueError:
                pass
            currentStudent.insert(2, pageSubject)
            currentStudent.insert(3, pageTest)
            tempScores.append(currentStudent)
    averageDict = {}
    for row in tempScores:
        if row[2] not in averageDict:
            averageDict[row[2]] = [len(row[7::]), 1, 0]
        else:
            averageDict[row[2]][0] += len(row[7::])
            averageDict[row[2]][1] += 1
            averageDict[row[2]][2] = float(averageDict[row[2]][0]/averageDict[row[2]][1])
    # for entry in averageDict:
    #     print(entry, averageDict[entry])
    # #  remove ELL Progress measure
    for studentScore in tempScores:
        lengthofrow = len(studentScore[7::])
        averageoftest = averageDict[studentScore[2]][2]
        if len(studentScore[7::]) > averageDict[studentScore[2]][2]:
            # print('going to pop', studentScore[len(studentScore)-int(averageDict[studentScore[2]][2])-1], 'from', studentScore)
            studentScore.pop(len(studentScore)-int(averageDict[studentScore[2]][2])-1)
    return tempScores

def clean_state_ids(infile):
    rawData = csv_reader(infile)
    cleanData = {}
    for row in rawData:
        cleanData[row[34]] = {'name': row[27], 'localid': row[26], 'eth': row[30]}
    return cleanData

def calc_fpa(row):
    if row[7] == "YES":
        return "Adv"
    elif row[6] == "YES":
        return "Pass"
    else:
        return "Fail"

def calc_raw(row):
    i = 9
    raw = 0
    while i < len(row):
        try:
            raw += int(row[i])
            i += 1
        except ValueError:
            break
    return str(raw)


def create_score_dict(score_list):
    dict_of_scores = {}
    for row in score_list:
        if row[1] != 'invalid':
            if row[1] not in dict_of_scores:
                # key is id, value is [test, scale, fpa, raw]
                dict_of_scores[row[1]] = [[row[2], row[3] + 'th'], [row[4] + (" " + row[5] if row[5] != "" else ""), row[6], calc_raw(row), calc_fpa(row)]]
            else:
                dict_of_scores[row[1]].append([row[4] + (" " + row[5] if row[5] != "" else ""), row[6], calc_raw(row), calc_fpa(row)])
    # dprint(dict_of_scores)
    return dict_of_scores

def merge_ids(staarList, idDict):
    progress_index = 0
    progress_max = len(staarList)
    for row in staarList:
        update_progress(progress_index/progress_max, "Parsing STAAR Scores")
        progress_index += 1
        try:
            row.insert(1, idDict[row[0]]['name'])
            row.insert(1, idDict[row[0]]['localid'])
        except KeyError:
            row.insert(1, 'invalid')
            row.insert(1, 'invalid')
    return create_score_dict(staarList)


def convertSTAARscores(infile1, infile2):
    # # temporary to speed up testing
    # cleanScores = readSTAARscores(temp_clean_scores)
    cleanScores = readSTAARscores(readSTAARfile(infile1))
    cleanIDs = clean_state_ids(infile2)
    finalData = merge_ids(cleanScores, cleanIDs)
    # finalData.insert(0, ['peims', 'local id', 'name', 'eth', 'grade', 'test', 'version', 'scale', 'level II', 'level III',
    #                       'category 1', 'category 2', 'category 3', 'category 4', 'category 5', 'category 6',
    #                       'category 7', 'category 8'])
    return finalData


# scores = convertSTAARscores('data/staar a and l.pdf', 'data/stateid.csv')