from z3 import *
import json
from pprint import pprint
import sys
from itertools import combinations
import time

start_global = time.clock()

#if len(sys.argv) < 2:
#	print('use as program.py input_file_name.json')
#	sys.exit(1)

# with open('newinp.json') as f:
with open(sys.argv[1]) as f:
	data = json.load(f)

# pprint(data)

print('--------------------------------------------------------------------------------')
print('pre-processing, reading and parsing input file')
print('--------------------------------------------------------------------------------')

# coarses list
print('reading and storing input data', end=' ')
type_rooms = {}
room_types = {}

for room_type in data['Room Types']:
	type_rooms[room_type] = []

for room, room_type in data['Classrooms']:
	room_types[room] = room_type
	type_rooms[room_type].append(room)

course_names = []
course_rooms = {}

course_prof_names = {}
course_prof_p = {}
prof_course_names = {}

course_time_req = {}
course_time_freq = {}

room_type_courses = {}
batch_course = {}

course_info = {}

courses_id = {}
n_courses = len(data['Courses'])
skip = []
counter = 0
for i in range(n_courses):
	# union find tree
	courses_id[i] = 0	# dummy, will be overwritten with prev course id or new one
	for j in range(i):
		if data['Courses'][i][:-1] == data['Courses'][j][:-1]:
			courses_id[i] = courses_id[j]			
			break
	else:
		# if no similar course, give it a uniqui id
		counter += 1
		courses_id[i] = counter

# reverse the tree
similar_courses = {}

for i, j in courses_id.items():
	if j not in similar_courses:
		similar_courses[j] = []
	similar_courses[j].append(i)

for courses_indices in similar_courses.values():
	courses = []
	for course_index in courses_indices:
		# combine batch numbers of dist_course and add
		courses.append(data['Courses'][course_index])

	batches = [i[-1] for i in courses]
	course = courses[0]
	name = str(course[0]) + '_' + '+'.join([str(i) for i in batches])	# name = cs201_2_3

	course_info[name] = course
	course_info[name][-1] = batches

	course_names.append(name)
	course_rooms[name] = type_rooms[course[1]]
	course_time_req[name] = [ int(float(i)*60) for i in course[2]]
	course_time_freq[name] = {}
	course_prof_p[name] = {}

	for batch in course_info[name][-1]:
		if batch not in batch_course:
			batch_course[batch] = []
		batch_course[batch].append(name)

	for j in course_time_req[name]:
		if j not in course_time_freq[name]:
			course_time_freq[name][j] = 1
		else:
			course_time_freq[name][j] += 1

	if course[1] not in room_type_courses:
		room_type_courses[course[1]] = [name]
	else:
		room_type_courses[course[1]].append(name)

	for prof in course[3]:

		if prof not in prof_course_names:
			prof_course_names[prof] = []
		prof_course_names[prof].append(name)

		if name not in course_prof_names:
			course_prof_names[name] = []
		course_prof_names[name].append(prof)

print(': done')

# determine what size of lectures are needed
# will only be 1 if only 1 hr lectures
# 1, 1.5, 3 if 3 hr lectures

print('calculating valid time intervals', end=' ')
lec_times = {}
for course in data['Courses']:
	for lec_time in course[2]:
		if lec_time not in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
			print( "only ", [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4], ' hrs lecture timings allowed' )
			sys.exit(1)
		elif lec_time not in lec_times:
			lec_times[lec_time] = 1
		else:
			lec_times[lec_time] += 1

intervals  = [int(float(i)*60) for i in lec_times.keys()]	# in minutes

time_unit = 30	# 30 minutes

time_slot_names = {}			
time_slot_names_without_days = {}

# make time slots of different types and assign numbers
for start_time, end_time in data['Institute time']:
	# split time in intervals
	start_time = int(round((start_time - int(start_time))*100, 0)) + int(start_time)*60 
	end_time = int(round((end_time - int(end_time))*100, 0)) + int(end_time)*60 
	for interval in intervals:
		if interval not in time_slot_names_without_days:
			time_slot_names_without_days[interval] = []
		cursor = start_time
		while cursor+interval <= end_time:
			name = str(int(cursor))+'_'+str(int(cursor+interval))		# week, start_time, end_time
			time_slot_names_without_days[interval].append(name)
			cursor += time_unit

# five days
for i in range(5):			# monday to friday
	for interval, time_slots in time_slot_names_without_days.items():
		if interval not in time_slot_names:
			time_slot_names[interval] = []
		for time_slot in time_slots:
			time_slot_names[interval].append(str(i)+'_'+time_slot)

print(': done')

def overlaps(t1, t2):
	if t1 == t2:
		return True
	time1 = t1.split('_')
	time2 = t2.split('_')
	if time1[0] != time2[0]:
		# different days
		return False
	time1 = [int(i) for i in time1]
	time2 = [int(i) for i in time2]
	if time1[1] > time2[1] and time1[1] >= time2[2] and time1[1] >= time2[2] and time1[2] > time2[2] :
		return False
	elif time1[2] <= time2[1] and time1[2] < time2[2] and time1[1] < time2[1] and time1[2] <= time2[1] :
		return False
	else:
		return True

def time_slot_type(time1):
	time1 = time1.split('_')
	time1 = [int(i) for i in time1]
	return time1[2] - time1[1]

# print('making overlap lookup dictionaries and lists ', end = " ")

# overlapping_times_all = {}
# for slot_type1, time_slots1 in time_slot_names_without_days.items():
# 	for time_slot1 in time_slots1:
# 		for i in range(5):
# 			overlapping_times_all[str(i)+'_'+time_slot1] = {}
# 		for slot_type2, time_slots2 in time_slot_names_without_days.items():
# 			for i in range(5):
# 				overlapping_times_all[str(i)+'_'+time_slot1][slot_type2] = []
# 			for time_slot2 in time_slots2:
# 				if overlaps('0_'+time_slot1, '0_'+time_slot2):
# 					for i in range(5):
# 						overlapping_times_all[str(i)+'_'+time_slot1][slot_type2].append(str(i)+'_'+time_slot2)

# print(': done')

# print('making unique overlap intervals', end = " ")
# unique_overlapping_intervals = []

# for start_time, end_time in data['Institute time']:
# 	# split time in intervals
# 	start_time = int(round((start_time - int(start_time))*100, 0)) + int(start_time)*60 
# 	end_time = int(round((end_time - int(end_time))*100, 0)) + int(end_time)*60

# 	cursor = start_time
# 	while cursor + time_unit < end_time:
# 		# print(cursor, interval)
# 		cursor += time_unit
# 		temp = []
# 		for time_slot in [j for i in time_slot_names_without_days.values() for j in i]:
# 			if overlaps('0_'+time_slot, '0_'+str(cursor)+'_'+str(cursor+time_unit)):
# 				temp.append(time_slot)
# 		# print(temp)
# 		if len(temp) > 1:
# 			unique_overlapping_intervals.append(temp)

# print(': done')

# make course-batch, classroom, timeslot propositions and store in list
ct_names = {}
ct_p = {}
cit_p = {}
crt_p = {}
c_sc_type = {}

print('making propositions', end = " ")

for course_name in course_names:

	ct_names[course_name] = {}
	ct_p[course_name] = {}

	for slot_type, time_slots in time_slot_names.items():
		if slot_type in course_time_req[course_name]:
			for time_slot in time_slots:
				name = course_name+'_'+time_slot
				ct_names[course_name][time_slot] = name
				ct_p[course_name][time_slot] = Bool(name)

	cit_p[course_name] = {}
	c_sc_type[course_name] = {}
	count = 0
	for slot_type, freq in course_time_freq[course_name].items():
		# 60: 1, 90: 2
		# course time requirements
		# a prop for each lecture
		for i in range(freq):
			count += 1
			c_sc_type[course_name][count] = slot_type
			cit_p[course_name][count] = {}
			for time_slot in time_slot_names[slot_type]:
				cit_p[course_name][count][time_slot] = Bool( course_name+'_'+str(count)+'_'+time_slot )

	crt_p[course_name] = {}
	for room in course_rooms[course_name]:
		crt_p[course_name][room] = {}
		for slot_type, time_slots in time_slot_names.items():
			if slot_type in course_time_req[course_name]:
				for time_slot in time_slots:
					name = course_name+'_'+room+'_'+time_slot
					crt_p[course_name][room][time_slot] = Bool(name)

print(': done')

stop_preprocessing = time.clock()
print('\nTotal time taken in preprocessing: ', round(stop_preprocessing - start_global, 2),'s\n')


# ---------------------------------------------------------------------------------------
# CONStRAINTS
# ---------------------------------------------------------------------------------------

start_making_constraints = time.clock()
print('--------------------------------------------------------------------------------')
print('making constraints')
print('--------------------------------------------------------------------------------')

# course time requirements constraint
print('making subcourse_atleast_once_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, sub_c_time_prop in cit_p.items():
	for sub_course, time_prop in sub_c_time_prop.items():
		temp.append(Or(list(time_prop.values())))

subcourse_atleast_once_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# ith subcourse atmost once
print('making subcourse_atmost_once_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, sub_c_time_prop in cit_p.items():
	for sub_course, time_prop in sub_c_time_prop.items():
		for time1, prop1 in time_prop.items():
			temp2 = []
			for time2, prop2 in time_prop.items():
				if time2 != time1:
					temp2.append(Not(prop2))
			temp.append(Implies(prop1, And(temp2)))
subcourse_atmost_once_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# cit to ct map
print('making cit_ct_map_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, subc_time_prop in cit_p.items():
	for sub_course, time_prop in subc_time_prop.items():
		for time1, prop1 in time_prop.items():
			temp.append(Implies(prop1, ct_p[course_name][time1]))

cit_ct_map_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# ct to cit map
print('making ct_cit_map_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, time_prop in ct_p.items():
	for time1, prop in time_prop.items():
		temp2 = []
		for subcourse, time_prop2 in cit_p[course_name].items():
			if time1 not in time_prop2:
				# different slot type
				continue
			temp2.append(time_prop2[time1])
		temp.append(Implies(prop, Or(temp2)))

ct_cit_map_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# crt ct map constraint
print('making crt_ct_map_constraint_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, room_time_prop in crt_p.items():
	for room, time_prop in room_time_prop.items():
		for time1, prop in time_prop.items():
			temp.append(Implies(prop, ct_p[course_name][time1]))

crt_ct_map_constraint_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# ct crt map constraint
print('making ct_crt_map_constraint', end = ' ')
start = time.clock()
temp = []

for course_name, time_prop in ct_p.items():
	for time1, prop1 in time_prop.items():
		temp2 = []
		for room, time_prop2 in crt_p[course_name].items():
			temp2.append((time_prop2[time1]))
		temp.append(Implies(prop1, Or(temp2)))

ct_crt_map_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# no room double booked
print('making room_double_book_constraint', end = ' ')
start = time.clock()
temp = []

for course1, room_time_prop1 in crt_p.items():
	for room1, time_prop1 in room_time_prop1.items():
		for time1, prop1 in time_prop1.items():
			temp2 = []
			for course2, room_time_prop2 in crt_p.items():
				# if the second course needs the same room
				if room1 in room_time_prop2.keys():
					# course_time_freq
					# {'cs201_2': {90: 2}, 'cs228_3': {60: 3}, 'cs25_3': {60: 3}}
					# overlapping_times = []
					# for slot_type in course_time_freq[course2].keys():
					# 	overlapping_times.extend(overlapping_times_all[time1][slot_type])
					# for overlapping_time in overlapping_times:
					for time2, prop2 in room_time_prop2[room1].items():
						if overlaps(time1, time2):

							if not (course1 == course2 and time2 == time1):
								temp2.append(Not(room_time_prop2[room1][time2]))

			temp.append(Implies(prop1, And(temp2)))

room_double_book_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# no lecture in two diff rooms at overlapping times
print('making lecture_double_book_constraint', end = ' ')
start = time.clock()
temp = []

for course1, room_time_prop1 in crt_p.items():
	for room1, time_prop1 in room_time_prop1.items():
		for time1, prop1 in time_prop1.items():
			temp2 = []
			# for room2, time_prop2 in room_time_prop1.items():
			for room2 in course_rooms[course1]:
				if room2 != room1:
					for time2, prop2 in time_prop1.items():
						if overlaps(time1, time2):					
							temp2.append(Not(room_time_prop1[room2][time2]))
			temp.append(Implies(prop1, And(temp2)))

lecture_double_book_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# prof time overlaps
print('making prof_double_booking_constraint', end = ' ')
start = time.clock()
temp = []
for prof, course_list in prof_course_names.items():
	if len(course_list) > 1:
		courses = combinations(course_list, 2)	# course^2
		for course1, course2 in courses:
			for time1, prop1  in ct_p[course1].items():	
				for time2, prop2  in ct_p[course2].items():
					# if time1 != time2:		# ?????
					if overlaps(time1, time2):
						temp.append(Implies(prop1, Not(prop2)))

prof_double_booking_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# batch time overlaps
print('making batch_double_booking_constraint', end = ' ')
start = time.clock()
temp = []
for batch, course_list in batch_course.items():
	if len(course_list) > 1:
		courses = combinations(course_list, 2)	# course^2
		for course1, course2 in courses:
			for time1, prop1  in ct_p[course1].items():	
				for time2, prop2  in ct_p[course2].items():
					if overlaps(time1, time2):
						temp.append(Implies(prop1, Not(prop2)))
						# temp.append(Or(Implies(prop1, Not(prop2)),	Implies(prop2, Not(prop1))))
batch_double_book_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

# subcourses dont overlap
print('making subcourses_dont_overlap_constraint', end = ' ')
start = time.clock()
temp = []
for course_name, subc_time_prop1 in cit_p.items():
	for sub_course, time_prop1 in subc_time_prop1.items():
		for time1, prop1 in time_prop1.items():
			temp2 = []
			for sub_course2, time_prop2 in subc_time_prop1.items():
				if sub_course2 != sub_course:
					for time2, prop2 in time_prop2.items():
						if overlaps(time1, time2):
							temp2.append(Not(prop2))
			temp.append(Implies(prop1, And(temp2)))

subcourses_dont_overlap_constraint = And(temp)
end = time.clock()
print(': done', round(end - start, 2),'s')

end_making_constraints = time.clock()
print('\nTotal time taken in making constraints: ', round(end_making_constraints - start_making_constraints, 2),'s\n')


# ---------------------------------------------------------------------------------------
# start solving
# ---------------------------------------------------------------------------------------
print('--------------------------------------------------------------------------------')
print('Trying to solve the constraints')
print('--------------------------------------------------------------------------------')

start_solving = time.clock()

s = Solver()

# set_option('verbose',10)
print('adding all the constraints to the solver', end=' ')

s.add(prof_double_booking_constraint)		#01
s.add(subcourse_atleast_once_constraint)	#02
s.add(subcourse_atmost_once_constraint)		#03
s.add(cit_ct_map_constraint)				#04
s.add(ct_cit_map_constraint)				#05
s.add(crt_ct_map_constraint_constraint)		#06
s.add(ct_crt_map_constraint)				#07
s.add(room_double_book_constraint)			#08
s.add(lecture_double_book_constraint)		#09
s.add(batch_double_book_constraint)			#10
s.add(subcourses_dont_overlap_constraint)	#11

print('done')

print('checking if a solution exists')
if s.check() == sat:
	print ("A possible timetable found")
	solved = True
else:
	print ("Not possible")
	solved = False

end_solving = time.clock()
print('\nTotal time taken in solving the constraints: ', round(end_solving - start_solving, 2),'s\n')

time_table_room = {}
time_table_batch = {}
for i in range(5):
	# 5 days
	time_table_room[i] = {}
	time_table_batch[i] = {}
	for room in room_types.keys():
		time_table_room[i][room] = []
	for batch in batch_course.keys():
		time_table_batch[i][str(batch)] = []

def time2string(time1):
	time1 = int(time1)
	hr_ = (time1)//60
	min_ = (time1)%60
	time1 = str(hr_)+':'+str(min_)
	if hr_//10 == 0:
		time1 = '0' + time1
	if min_ == 0:
		time1 += '0'
	return time1

cfreq = {}

# nth_lecture = []
# course_time_ans = []
if solved == True:
	m = s.model()
	# print('name', 'batch', 'room', 'day', 'start', 'end', sep='\t')
	for i in m:
		if m[i]:
			lecture = str(i)
			lecture = lecture.split('_')
			if len(lecture) >= 6:
				# crt or cit constraint
				[course_name, batches, room_or_subcourse, day, start_time, end_time ] = lecture
				day = int(day)
				if room_or_subcourse in room_types:
					# room
					start_time = time2string(start_time)
					end_time = time2string(end_time)
					time_table_room[day][room_or_subcourse].append((start_time, end_time, course_name, batches))
					time_table_batch[day][batches].append((start_time, end_time, course_name, room_or_subcourse))
					if course_name not in cfreq:
						cfreq[course_name] = 0
					cfreq[course_name] += 1
					# print('\t'.join([course_name, batches, room_or_suncourse, day, start_time, end_time ]))
				else: 
					# nth_lecture.append(lecture)
					pass
			else:
				# course_time_ans.append(lecture)
				pass

for i in range(5):
	# 5 days
	for room in room_types.keys():
		time_table_room[i][room].sort(key=lambda x: x[1])
	for batch in batch_course.keys():
		time_table_batch[i][str(batch)].sort(key=lambda x: x[1])

day_name = {
	0: "MONDAY",
	1: "TUESDAY",
	2: "WEDNESDAY",
	3: "THURSDAY",
	4: "FRIDAY",
}

print('-------------------------- TIME TABLE ---------------------------------')
print('Day\nRoom\tStart\tEnd\tName\tBatch')
print('-----------------------------------------------------------------------')
for day, room_time in time_table_room.items():
	print(day_name[day])
	for room, lectures in room_time.items():
		if len(lectures) > 0:
			print(room,':')
			s = [[str(e) for e in row] for row in lectures]
			lens = [max(map(len, col)) for col in zip(*s)]
			fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
			table = [fmt.format(*row) for row in s]
			print('\t','\n\t '.join(table))
	print('-------------------------------------------------------------------')

end_global = time.clock()
print('________________________________________________________________________________')
print('Total time taken: ', round(end_global - start_global, 2),'s')
print('________________________________________________________________________________')