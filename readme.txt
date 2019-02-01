run using:
python make_timetable.py input_file_name.json

OUTPUT ON THE TEST INPUT FILE GIVEN:

>>> python .\make_timetable.py .\trial_input.json
--------------------------------------------------------------------------------
pre-processing, reading and parsing input file
--------------------------------------------------------------------------------
reading and storing input data : done
calculating valid time intervals : done
making propositions : done

Total time taken in preprocessing:  0.18 s

--------------------------------------------------------------------------------
making constraints
--------------------------------------------------------------------------------
making subcourse_atleast_once_constraint : done 0.09 s
making subcourse_atmost_once_constraint : done 10.12 s
making cit_ct_map_constraint : done 0.21 s
making ct_cit_map_constraint : done 0.2 s
making crt_ct_map_constraint_constraint : done 0.19 s
making ct_crt_map_constraint : done 0.19 s
making room_double_book_constraint : done 3.47 s
making lecture_double_book_constraint : done 1.03 s
making prof_double_booking_constraint : done 0.14 s
making batch_double_booking_constraint : done 1.25 s
making subcourses_dont_overlap_constraint : done 1.28 s

Total time taken in making constraints:  18.18 s

--------------------------------------------------------------------------------
Trying to solve the constraints
--------------------------------------------------------------------------------
adding all the constraints to the solver done
checking if a solution exists
A possible timetable found

Total time taken in solving the constraints:  1.0 s

-------------------------- TIME TABLE ---------------------------------
Day
Room    Start   End     Name    Batch
-----------------------------------------------------------------------
MONDAY
T1 :
         14:00  15:00   CH105   1
LH1 :
         11:00  12:30   EE101   2
computer lab :
         08:30  10:30   CS101   1
         15:00  17:00   CS101   1
T2 :
         10:00  11:00   CS305   3
         15:00  16:00   CS228   3
LH2 :
         14:00  15:00   CS207   2
         15:00  16:30   EE101   2
ground :
         10:30  12:30   NO101   1
-------------------------------------------------------------------
TUESDAY
T1 :
         09:00  10:00   CS305   3
         11:30  12:30   CS305   3
LH1 :
         10:00  11:30   CS215   2
computer lab :
         15:00  17:00   CS251   2
Chemistry lab :
         15:00  17:00   CH117   1
T3 :
         10:30  11:30   CS344   3
         14:00  15:00   CH105   1
LH2 :
         10:30  11:30   ENG101  1
         16:00  17:00   HS301   3
-------------------------------------------------------------------
WEDNESDAY
T1 :
         16:00  17:00   CS228   3
Chemistry lab :
         10:30  12:30   CH117   1
T2 :
         14:00  15:00   CH107   1
T3 :
         10:30  11:30   CS344   3
LH2 :
         08:30  09:30   PH107   1
         14:30  15:30   CS207   2
ground :
         15:00  17:00   NO101   1
-------------------------------------------------------------------
THURSDAY
T1 :
         09:00  10:00   CH107   1
         10:30  11:30   CS228   3
         14:00  15:00   CH107   1
LH1 :
         10:30  12:00   CS215   2
         15:00  16:00   PH107   1
computer lab :
         10:00  12:00   CS101   1
         14:30  16:30   CS341   3
T2 :
         09:00  10:00   CS344   3
-------------------------------------------------------------------
FRIDAY
T1 :
         08:30  09:30   HS101   2
         16:00  17:00   CH105   1
LH1 :
         11:30  12:30   ENG101  1
         15:00  16:00   CS207   2
computer lab :
         14:30  16:30   CS386   3
T2 :
         10:30  11:30   HS101   2
LH2 :
         08:30  09:30   HS301   3
         15:00  16:00   PH107   1
-------------------------------------------------------------------
________________________________________________________________________________
Total time taken:  20.08 s
________________________________________________________________________________