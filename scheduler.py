import datetime
from datetime import date, timedelta
import random as rand
import math
import os
import sys

days = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}
inverse = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday'
}

dayiter = timedelta(1)


class RA:
    '''
     Class to represent a single RA.
     Params:
         name -> The RA's name
         unv_irregular -> the restricted specific dates
    '''

    def __init__(self, name='', building='', unv_irregular=set()):
        self.name = name
        self.unv_irregular = unv_irregular
        self.building = building

    def __str__(self):
        return 'Name: %s\nDays Restriction: %s\nDates Restriction %s' % (self.name, str(self.unv_regular), str(self.unv_irregular))


class InvalidDateRangeException(Exception):
    '''
     Exception that represents invalid date ranges. 
     Params:
         date1 -> the start date
         date2 -> the end date
    '''

    def __init__(self, date1, date2):
        self.date1 = date1
        self.date2 = date2

    def __str__(self):
        return 'Start date %s is later than end date %s' % (self.date1, self.date2)


class InvalidFileFormatException(Exception):
    '''
     Exception that represents invalid input file. 
     Params:
        fn -> the filename
    '''

    def __init__(self, fn):
        self.fn = fn

    def __str__(self):
        return '%s - file format is invalid.' % (self.fn)


def get_date_obj(s):
    '''
     Returns a date object based on an input string.
     Params:
        s -> a string of the form m/d/yyyy, mm/dd/yyyy, or mm/dd/yy
    '''
    parts = s.split('/')
    if len(parts[2]) == 2:
        parts[2] = '20' + parts[2]
    print(int(parts[2]), int(parts[0]), int(parts[1]))
    return date(int(parts[2]), int(parts[0]), int(parts[1]))


def create_gcal_even(name, date, tag=''):
    '''
     Returns a dict event based on the given data. 
     Params:
        name -> the name of the event 
        date -> a string representation of the date 
        tag -> an optional tag to prepend to the event title. 
     Returns:
        a dict event based on the Google Calendar API
    '''
    tag = tag + ': ' if tag != '' and tag != None else ''
    event = {
        'summary': tag + name,
        'start': {
            'date': date
        },
        'end': {
            'date': date
        }
    }
    return event


def create_date_range(begin_str, end_str, exclude=set()):
    '''
     Creates a list of dates from begin to end excluding the dates in the exclude list.
     Params:
         begin_str -> a string representing the beginning of the date range 
         end_str -> a string representing the end of the date range
         exclude -> a set of dates to exclude from the date range.
     Returns:
         ret -> a list object containing all dates in the desired range
         weekdays -> the number of weekdays in the range
         weekends -> the number of weekends in the range
    '''
    curr = get_date_obj(begin_str)
    end = get_date_obj(end_str)
    if end < curr:
        raise InvalidDateRangeException(curr, end)
    ret = list()
    weekdays, weekends = 0, 0
    while curr <= end:
        if curr not in exclude:
            ret.append(curr)
            if curr.weekday() < 5:
                weekdays += 1
            else:
                weekends += 1
        curr = curr + dayiter
    return (ret, weekdays, weekends)


def parse_file(infile):
    '''
     Parses a (prooperly formatted) input file and returns a list of RA objects.
     Params:
        infile -> a file object
     Returns:
        ras -> a list of RA objects based on the data in infile
    '''
    ras = []
    for line in infile:
        try:
            parts = line.split('| ')
            if len(parts) <= 1:
                continue
            name = parts[0].strip()
            building = parts[1].lower().strip()
            parts[2] = parts[2].replace(' ', '').strip()
            irregular = set([get_date_obj(i) for i in parts[2].split(',')]) if parts[2] != '' else set()
            ras.append(RA(name=name, building=building, unv_irregular=irregular))
        except Exception as e:
            print(e)
            raise InvalidFileFormatException()
    return ras


def create_schedule(ras, outfile, start, end, break_start=None, break_end=None):
    '''
     Creates a duty schedule based on the data in ras a outputs to an outfile. 
     Params:
        ras -> a list of RA objects
        outfile -> a file object to be written to
        start -> the starting date
        end -> the ending date
        break_start -> the starting date for a major break (Thanksgiving / Spring)
        break_end -> the ending date for a major break (Thanksgiving / Spring)
    '''

    '''
    Algorithm:
    On a given day, generate a list of all RAs that are free. 
    Select all the RAs with the least number of duties.
    If there are more than one, randomly select one of them.

    For weekends, select two people, one from each building. 
    '''
    num_ras = len(ras)
    break_, _, _ = create_date_range(
        break_start, break_end) if break_start != None and break_end != None else set()
    duty_range, num_weekdays, num_weekends = create_date_range(
        start, end, break_)
    print (num_ras)

    tracker, schedule = dict(), dict()
    for ra in ras:
        tracker[ra.name] = [0, 0] # Track how many days of weekdays and weekends

    for curr in duty_range:
        day = curr.weekday()
        if day != 4 and day != 5:  # weekday
            ind = 0
        else:  # weekend
            ind = 1

        if ind == 0:
            # Generate a list of all available RAs
            available_ras = []
            for ra in ras:
                if curr not in ra.unv_irregular:
                    available_ras.append(ra)
            
            # Get the one with the least amount so far 
            selected_ras = []
            min_val = 100 # RAs should not have this many duties
            for ra in available_ras:
                if tracker[ra.name][ind] < min_val:
                    # Reset selected
                    selected_ras = []
                    min_val = tracker[ra.name][ind]
                    selected_ras.append(ra)
                elif tracker[ra.name][ind] == min_val:
                    selected_ras.append(ra)

            # Assign the date
            selected = None
            if len(selected_ras) == 0:
                print ('%s - Couldn\'t resolve' % str(curr))
                # Select at random for now
                chosen_by_god = rand.randint(0, num_ras)
                selected = ras[chosen_by_god]

            elif len(selected_ras) == 1:
                # Just get this person out
                selected = selected_ras[0]

            else:
                # Many RAs with the same number of empty dates. Chosen by god
                chosen_by_god = rand.randint(0, len(selected_ras))
                selected = selected_ras[chosen_by_god]
            schedule[curr] = selected.name
        
        else: # Generate for the weekends
            # For weekends, 1 Bradford and 1 Homewood
            bradford_available_ras = []
            homewood_available_ras = []
            for ra in ras:
                if curr not in ra.unv_irregular:
                    if ra.building == 'homewood':
                        homewood_available_ras.append(ra)
                    elif ra.building == 'bradford':
                        bradford_available_ras.append(ra)

            # Selected RA for each building
            selected_bradford_ras = []
            min_val = 100 # RAs should not have this many duties
            for ra in bradford_available_ras:
                if tracker[ra.name][ind] < min_val:
                    # Reset selected
                    selected_bradford_ras = []
                    min_val = tracker[ra.name][ind]
                    selected_bradford_ras.append(ra)
                elif tracker[ra.name][ind] == min_val:
                    selected_bradford_ras.append(ra)

            selected_homewood_ras = []
            min_val = 100 # RAs should not have this many duties
            for ra in homewood_available_ras:
                if tracker[ra.name][ind] < min_val:
                    # Reset selected
                    selected_homewood_ras = []
                    min_val = tracker[ra.name][ind]
                    selected_homewood_ras.append(ra)
                elif tracker[ra.name][ind] == min_val:
                    selected_homewood_ras.append(ra)

            # Assign people
            homewood_selected = None
            bradford_selected = None

            if len(selected_homewood_ras) == 0:
                print ('%s - Couldn\'t resolve for Homewood' % str(curr))
                print('We are fuckeddddddd')
                # Select at random for now
                chosen_by_god = rand.randint(0, num_ras)
                homewood_selected = ras[chosen_by_god]

            elif len(selected_homewood_ras) == 1:
                # Just get this person out
                homewood_selected = selected_homewood_ras[0]

            else:
                # Many RAs with the same number of empty dates. Chosen by god
                chosen_by_god = rand.randint(0, len(selected_homewood_ras))
                homewood_selected = selected_homewood_ras[chosen_by_god]
            
            if len(selected_bradford_ras) == 0:
                # Best solution is to ask a Homewood RA to cover for now
                print ('%s - Couldn\'t resolve for Bradford' % str(curr))
                if len(homewood_available_ras) == 1:
                    print('%s - Not enough RAs to cover 2 buildings' %str(curr))
                    bradford_selected = homewood_selected
                
                else:
                    chosen_by_god = rand.randint(0, len(homewood_available_ras))
                    bradford_selected = homewood_available_ras[chosen_by_god]

            elif len(selected_bradford_ras) == 1:
                bradford_selected = selected_bradford_ras[0]

            else:
                chosen_by_god = rand.randint(0, len(selected_bradford_ras))
                bradford_selected = selected_bradford_ras[chosen_by_god]
                
            schedule[curr] = homewood_selected.name + bradford_selected.name
                



        '''
        old code 
        '''

        nm = lst.pop(roll).name
        tracker[nm][ind] -= 1
    for curr in duty_range:
        outfile.write('%s : %s : %s\n' %
                      (inverse[curr.weekday()], str(curr), schedule[curr]))
    outfile.close()
    print ('Summary')
    for ra in ras:
        curr = tracker[ra.name]
        print ('%s : weekdays %d, weekends %d' % (ra.name, curr[0], curr[1]))


def parse_sched_file(sched_file):
    '''
     Parses a schedule file of the format created when autogenerating a schedule.
     Params:
        sched_file -> a file handle for the file containing the schedule
     Returns:
        a dictionary representation of the schedule
    '''
    sched = dict()
    lines = sched_file.readlines()
    i = 1
    try:
        for line in lines:
            parts = line.split(' : ')  # day of week : date : name
            sched[parts[1]] = parts[2]
            i += 1
        return sched
    except Exception as e:
        raise InvalidFileFormatException(sched_file.name)
        print ('File format error on line %d' % (i))

def run_create(infile, outfile, start_date, end_date, break_start, break_end):
    '''
     Creates a schedule based on data in infile and outptus to outfile. 
     Params:
        infile -> an input file handle 
        outfile -> an output file handle 
        start_date -> the start date for the schedule 
        end_date -> the end date for the schedule
    '''
    ras = parse_file(infile)
    create_schedule(ras, outfile, start=start_date, end=end_date,
                    break_start=break_start, break_end=break_end)
    print ('Finished schedule has been output to %s.\n \
           Please look over schedule before commiting to Google Calendar.\n \
           Run \'$ python scheduler.py -i %s -c\' to commit to Google Calendar.' % (outfile.name, outfile.name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ResLife duty scheduler',
                                     parents=[tools.argparser],
                                     prog='scheduler.py')
    parser.add_argument('-i', '--infile', type=argparse.FileType('r'),
                        required=True,
                        help='Enter filename of preference file. Example: \
                        mccoy.txt')
    parser.add_argument('-o', '--outfile', nargs='?',
                        type=argparse.FileType('w'),
                        default='schedule_out.txt', help='Enter name of \
                        preferred output file. Default is schedule_out.txt')
    parser.add_argument('-s', '--start-date', default='2/16/2018',
                        help='Enter starting date in MM/DD/YYYY format.')
    parser.add_argument('-e', '--end-date', default='5/17/2018',
                        help='Enter ending date in MM/DD/YYYY format.')
    parser.add_argument('-bs', '--break-start-date', default='3/17/2018',
                        help='Enter the starting date of a major break \
                        (Thanksgiving / Easter) in MM/DD/YYYY format.')
    parser.add_argument('-be', '--break-end-date', default='3/24/2018',
                        help='Enter the ending date of a major break \
                        (Thanksgiving / Easter) in MM/DD/YYYY format.')

    flags = parser.parse_args()
    run_create(flags.infile, flags.outfile, flags.start_date,
                   flags.end_date, flags.break_start_date,
                   flags.break_end_date)
