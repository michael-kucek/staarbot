import csv

app_key = 'jbja9j7g02a863n'
app_secret = 'd81ga83ihm6jlgd'
db_token = 'uid8tVDyeVkAAAAAAAAEHCQtaIJajOFtc62AXXKyFH6UlXmapYAXYT1YfLQy7Vua'


# client.file

def read_csv(path):
    with open(path, 'r', encoding="utf8") as bigfile:
        readbigfile = csv.reader((line.replace('\0','') for line in bigfile), delimiter=",", quotechar='"')
        temparray = list(readbigfile)
        for row in temparray:
            if len(row) == 0:
                temparray.remove(row)
        return temparray

raw_gs = read_csv('data/failurereport.csv')
raw_hss = read_csv('data/summer hss.csv')

def grade_dict(grades):
    gd = {}

    for row in grades[1::]:
        gd[int(row[0]), int(row[5][-1])] = str(row[7])
    return gd

gdict = grade_dict(raw_gs)


def teacher_schedule_dict_creator(hss):
    name_dict = {}
    for row in hss:
        current_teacher = row[16].split(',')[0].split(' ')[0].lower()
        current_room = row[17].split(' (')[0]
        current_class = row[15].split('-')[0]
        try:
            current_period = int(row[13][2])
            if current_period > 3:
                continue
        except IndexError:
            continue
        if current_teacher not in name_dict:
            name_dict[current_teacher] = [current_teacher.title(), current_room, [['', 0],['', 0],['', 0]]]
            name_dict[current_teacher][2][current_period - 1][0] = current_class
            name_dict[current_teacher][2][current_period - 1][1] += 1
        else:
            name_dict[current_teacher][2][current_period - 1][0] = current_class
            name_dict[current_teacher][2][current_period - 1][1] += 1
    return name_dict

def student_sched_dict_creator(hss, gd):
    stud_dict = {}
    stud_list = []
    for row in hss:
        id = int(row[6].replace('(','|').replace(')','|').split('|',)[1]) # gets id number as int
        name = row[6].split('(')[0] # gets last, first [mi]
        grade = row[5].split(' ')[1]
        if len(grade) == 1: grade = ' ' + grade
        if (str(id) + ' ' + grade + ' ' + name) not in stud_list:
            stud_list.append(str(id) + ' ' + grade + ' ' + name)
        try:
            current_period = int(row[13][2])
            if current_period > 3:
                continue
        except IndexError:
            continue
        current_teacher = row[16].split(',')[0].split(' ')[0]
        current_room = row[17].split(' (')[0]
        current_class = row[15].split('-')[0]
        try: current_grade = gd[id, current_period]
        except KeyError: current_grade = "NA"
        if id not in stud_dict:
            stud_dict[id] = [id, name, [['', '', '', ''], ['', '', '', ''], ['', '', '', '']]]
        stud_dict[id][2][current_period - 1][0] = current_room
        stud_dict[id][2][current_period - 1][1] = current_teacher
        stud_dict[id][2][current_period - 1][2] = current_class.title().replace(" ","")
        stud_dict[id][2][current_period - 1][3] = current_grade
    return stud_dict, stud_list

def student_search(stud_list, q):
    matches = [x for x in stud_list if q.title() in x.title()]
    return matches

teacher_dict = teacher_schedule_dict_creator(raw_hss)
# for thing in teacher_dict:
#     print(teacher_dict[thing])
student_dict, student_list = student_sched_dict_creator(raw_hss, gdict)

# for thing in student_dict:
#     print(student_dict[thing])

def get_dicts():
    return teacher_dict, student_dict, student_list