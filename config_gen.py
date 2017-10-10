"""
Author: Alex Frias - Pacesetter Technology
Date: 8/16/17

Converter from csv to json file for use with implementation doc
"""


import csv
import json
import pprint
from collections import OrderedDict, defaultdict
import settings
import to_dict
import os
import sys
import tkinter
import tkinter as tk
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askopenfile


CWD = os.getcwd()


def init_std(_type):
    """
    Gets the correct config depending on the type of club
    :param str _type: Type of club
    """
    if _type == 'c':
        STANDARD = to_dict.standard_dict()
    else:
        STANDARD = to_dict.standard_dict('golf')
    return STANDARD


def validate(all_info, key='c'):
    """
    Take in the resulting list from the csv and make sure it is in correct format. Correct format entails:
        1. First entry is (*,Front,*,[*])
        2. Ends in END
        3. If golf -> Needs GOLF else -> no GOLF
        4. if code == submenu -> needs a submenu
        5. Make sure codes match?
    """
    # print(all_info)
    front = (all_info[0][1].lower() == 'front', 'Does not start with Front')
    end = (all_info[-1][0].lower() == 'end', 'Does not end with END')
    end_tuples = [x[1].lower() for x in all_info]
    golf = ('golf' in end_tuples if key == 'g' else 'golf' not in end_tuples, 'Either given type golf with no golf menu, or given type city with a golf menu')
    submenu = (all([x[3] != [''] for x in all_info if x[1] == 'submenu']), 'Submenu code with no corresponding submenu given')
    returns = [front, end, golf, submenu]
    return [x for x in returns if not x[0]]


def read_csv(filename, _type):
    """
    Read in the csv file and preprocess the data.
    """
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        # Read in the file to format (title, info, access, extra)
        # where extra implies everything else. Could be nothing or
        # could be 3 columns depending on the type
        all_info = [(title.strip().replace('\ufeff', ''), info.strip(), access.strip(), extra) for title, info, access, *extra in reader]
        bad_list = validate(all_info, _type)
        return all_info, [warning for _, warning in bad_list]


def list_to_dict(info_list):
    """
    Takes in the list with all of the info, and depending on the types turns
    it into a more informative dictionary we can more easily parse into json.
    """
    info_dict = OrderedDict()  # dict which will hold the standard info
    golf_dict = OrderedDict()  # may not use this, will have golf stuff

    # all of the current items to use
    curr_tl = []
    curr_title = None
    curr_access = None
    curr_dict = info_dict

    # flag for if we switched from info -> golf
    switched = False

    # loop over all of the tuples w/in the infor list
    for title, info, access, extra in info_list:
        if info == 'Front':  # Should be the first one, set our current values
            curr_title = title
            curr_access = access
            continue
        # header w/in the menu, at this point we know all of the previous entries within the header have been added, and we can safely add them the the dictionary. We then reset the curr variables and add those to the next header list and repeat
        elif info == 'Header':
            if not switched:
                if curr_access == '':  # no access level given
                    curr_dict[curr_title] = curr_tl
                else:
                    curr_dict[curr_title + '[v:' + curr_access.lower().replace(' ', '') + ']'] = curr_tl

            # reset curr variables
            curr_access = access
            curr_title = title
            curr_tl = []
            switched = False
            continue
        elif info == 'GOLF':
            # add to the curr header and switch to golf dict
            if curr_access == '':
                curr_dict[curr_title] = curr_tl
            else:
                curr_dict[curr_title + '[v:' + curr_access.lower().replace(' ', '') + ']'] = curr_tl

            # switch to the golf dict and set the flag accordingly
            curr_dict = golf_dict
            switched = True
            continue
        elif info == 'END':  # we done! Make sure we add the final header list
            curr_dict[curr_title] = curr_tl
            break
        if info == 'submenu':  # if it's a submenu, we need to add the extra
            curr_tl.append((title + '|', info, access, ','.join(extra)))
        else:  # otherwise just add the current stuff
            curr_tl.append((title + '|', info, access))
    return info_dict, golf_dict  # return both


def create_submenu(tup, code=None, access=False):
    """
    Takes in tuple of information on the submenu, a code (really only None and 'url' matter), and an access level. Creates and returns a submenu to be added into the dict.
    """
    # get the title and the submenu contents
    title, sub = tup[0], tup[-1]

    # create it in the right format
    subs = [title.strip('|')] + [x.strip(',') for x in sub.split('~')]
    new_subs = subs[:1]
    if access:
        new_subs[0] += '[v:{}]'.format(tup[-2].lower())

    # create each tab within the submenu
    for sub in subs[1:]:
        sub_title = sub.split('|')[0] + '||'
        if code == 'url':
            new_subs.append(sub_title + sub.split('|')[1] + '|' + settings.DEFAULTS[code] + sub.split('|')[2])
        else:
            new_subs.append(sub_title + '|'.join(sub.split('|')[1:]))
    return new_subs


def front_menu(v):
    """
    Takes in the tupe of values and turns it into the front menu
    """
    start = settings.COLORS['box'] + '|' + settings.COLORS['text'] + '|'
    def_list = [elt[:-1] for elt in [start + '|'.join(elt) for elt in v]]
    return {'default': def_list}  # return in form of dict to add to json


def create_more_courses(course_id, STANDARD):
    """
    If there is more than on course, we need to add these courses to the config. We can add each according to a standard format, this is pretty straightforward with a little bit of string parsing.
    """
    # These are the standard config values
    pcc = {"FBReminderHole": 8, "FBReminderPosition": "tee"}
    prmd = ["Golf", "Weather||url|/web/CLIENT_ID/weather", "Notifications||notifications", "End Round||endround"]
    # The stnadard menu we want to add to each course
    menu = STANDARD['PacesetterRoundMenuDetails']['COURSE_ID_member']
    # loop over all of the courses and add them to the config
    for course in course_id[1:]:
        STANDARD['PacesetterCourseConfig'].update({course:pcc})
        STANDARD['PacesetterCourseIDs'].append(course)
        STANDARD['PacesetterRoundMenuDetails'].update({course:[prmd]})
        s_course = str(course) + '_member'
        STANDARD['PacesetterRoundMenuDetails'].update({s_course:menu})

    # The indent is only there to make printing look pretty
    return json.dumps(STANDARD, indent=4)


def to_json(info_dict, STANDARD, inner='primary', outer='PacesetterMainMenuDetails', key='c'):
    """
    HOOOOOO BOYYYYYYY. Welcome to some ~ugly~ code up in here. It could be much much cleaner, but real life has gotten in the way of my once beautiful code. This function takes in:
        A dictionary in the format from 'list_to_dict': info_dict
        The json dict to add it to: STANDARD
        What we want the inside dictionary to be called: inner
        What we want the outside dictionary to be called: outer
        A key denoting city or golf: key
    It then takes this and converts it into a nice clean json format.
    I'd really like to refactor this out, as there must be a cleaner way to do this. It's been hacked together to deal with all of the individual cases, but there must be a way for the cases to sort of auto-json themselves.
    """
    primary = defaultdict(list)  # the dict of lists we add everything to
    for k, v in info_dict.items():  # loop over all of the items in out dict
        is_menu = False  # flag to denote this was a front menu item
        if k.split('[')[0] == 'Menu':  # get and create the front menu
            menu = front_menu(v)
            STANDARD['PacesetterHomeDetails'] = menu
            is_menu = True  # flag it!
        new_v = []  # the new list we will be creating to append stuff to
        to_add_sub = None
        for tup in v:  # go through every entry in the header
            is_submenu = False  # flag to denote a submenu task
            elt = list(filter(None, tup))  # gets rid of empty elements
            # split into the code and any extra info (possibly)
            code, *alt = elt[1].split('|')[0].split('~')
            if code in settings.DEFAULTS:  # check if we have responses stored
                # if we have extra stuff to add to the elements
                if len(alt) > 0:
                    elt[1] = code + '|' + settings.DEFAULTS[code] + alt[0]
                # special case for url dealt with above, do others here
                if code != 'url':
                    elt[1] += settings.DEFAULTS[code]
            if code == 'submenu':  # special submenu case
                submenu = create_submenu(elt, elt[-1].split('|')[1], len(elt) == 4)
                # Fixes bug where only one submenu per header worked
                if not to_add_sub:
                    to_add_sub = list([k])
                to_add_sub.append(submenu)
                is_submenu = True  # Gotta flag it!
            else:  # the 'usual' case. Feels like there is no usual case
                # Oy this is a mouthful. Checking for individual access level
                if not is_submenu and len(elt) > 2 and code != 'url':
                    to_add = elt[0][:-1] + '[v:{}]||'.format(elt[2].lower()).replace(' ', '') + '|'.join(elt[1:-1])
                    new_v.append(to_add)
                # url case for individual access level. See what I mean about it being ugly?
                elif len(elt) > 2:
                    elt[0] = elt[0][:-1] + '[v:{}]|'.format(elt[-1].lower())
                    new_v.append('|'.join(elt[:-1]))
                # usual case of the usual case
                else:
                    new_v.append('|'.join(elt))
        # If its a menu we dont want to add it here, we did up there
        if not is_menu:
            if to_add_sub is not None:  # submenu case of adding
                to_add = new_v
                primary[inner].append((to_add_sub + to_add))
            else:  # usual case for adding to dict
                to_add = list([k]) + new_v
                primary[inner].append((to_add))
    if key == 'c':  # if its a city, we overwrite...
        STANDARD[outer] = primary
    elif key == 'g':  # ...if its golf, we update (append)
        STANDARD[outer].update(primary)
    return json.dumps(STANDARD, indent=4)  # return and make it pretty!

def run_from_tkinter(_type, shortcode, client_id, longname, course_id, filename):
    # We need to know if its a golf or city club to load the right config
    # ****IMPORTANT: Should only be a golf club if there is a GOLF section in the app. Otherwise it does not need to golf config****
    _type = _type.strip()
    shortcode = shortcode.strip()
    client_id = client_id.strip()
    longname = longname.strip()
    course_id = course_id.split(',') if _type == 'g' else None

    # load the 'standard' config depending on club type
    STANDARD = init_std(_type)

    # get the file
    filename = filename.strip()
    errors = []
    if not os.path.exists(filename):
        errors.append('File does not exist. Please check path')
        return None, errors

    file_dir = '/'.join(filename.split('/')[:-1]) # directory where csv file is
    out_file = os.path.join(file_dir, 'out.json')

    # read in the file, load it from a list into a dict for easier parsing
    all_info, csv_errors = read_csv(filename, _type)
    # check for errors
    if csv_errors:
        errors.extend(csv_errors)
        return None, errors
    std_dict, golf_dict = list_to_dict(all_info)

    # do the standard updates to config
    std_json = to_json(std_dict, STANDARD)

    # if its a golf club, we'll have generated extra in-round we need to add
    if _type == 'g':
        golf_json = to_json(golf_dict, STANDARD, 'COURSE_ID_member', 'PacesetterRoundMenuDetails', 'g')

    # convert from list to string if its just one course
    if course_id and len(course_id) == 1:
        course_id = course_id[0]
    elif course_id:  # We need to create the config for the extra courses
        golf_json = create_more_courses(course_id, STANDARD)
        course_id = course_id[0]  # Need just the first one for placeholders

    # open the out file, write our B-E-A-U-tiful config to it
    with open(out_file, 'w+') as out:
        if _type == 'c':  # if its a city type -> write standard json
            updated_json = std_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id)  # replace placeholders
            out.write(updated_json)
        elif _type == 'g':  # if its a golf type -> write golf json
            updated_json = golf_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id).replace('COURSE_ID', course_id)  # replace placeholders
            out.write(updated_json)

    return out_file, errors  # One config, please!

def main():
    # We need to know if its a golf or city club to load the right config
    # ****IMPORTANT: Should only be a golf club if there is a GOLF section in the app. Otherwise it does not need to golf config****
    _type = input('Type of club? (c or g): ').strip()
    while _type not in {'c', 'g'}:  # Make sure its the right code
        _type = input("That's not 'c' or 'g'. Type of club? (c or g) ").strip()

    # Codes we have as placeholders to add in
    shortcode = input('Shortcode: ').strip()
    client_id = input('Client ID: ').strip()
    longname = input('Name of Club: ').strip()
    course_id = input('Course ID (Comma separated): ').split(',') if _type == 'g' else None

    # load the 'standard' config depending on club type
    STANDARD = init_std(_type)

    # get the file
    filename = input('Full path to file from {}: '.format(CWD))

    file_dir = '/'.join(filename.split('/')[:-1]) # directory where csv file is
    out_file = os.path.join(file_dir, 'out.json')

    # read in the file, load it from a list into a dict for easier parsing
    std_dict, golf_dict = list_to_dict(read_csv(filename, _type))

    # do the standard updates to config
    std_json = to_json(std_dict, STANDARD)

    # if its a golf club, we'll have generated extra in-round we need to add
    if _type == 'g':
        golf_json = to_json(golf_dict, STANDARD, 'COURSE_ID_member', 'PacesetterRoundMenuDetails', 'g')

    # convert from list to string if its just one course
    if course_id and len(course_id) == 1:
        course_id = course_id[0]
    elif course_id:  # We need to create the config for the extra courses
        golf_json = create_more_courses(course_id, STANDARD)
        course_id = course_id[0]  # Still need just the first one 4 placeholders

    # open the out file, write our B-E-A-U-tiful config to it
    with open(out_file, 'w+') as out:
        if _type == 'c':  # if its a city type -> write standard json
            updated_json = std_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id)  # replace placeholders
            out.write(updated_json)
        elif _type == 'g':  # if its a golf type -> write golf json
            updated_json = golf_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id).replace('COURSE_ID', course_id)  # replace placeholders
            out.write(updated_json)

    return 'Output file is: {}'.format(out_file)  # One config, please!


if __name__ == '__main__':  # You already know what's going on

    class Application(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.pack()
            self.create_widgets()

        def create_widgets(self):
            self.tlabel = tk.StringVar()
            self.tlabel.set('Type of Club:')
            self.type_label = tk.Label(self, textvariable=self.tlabel)
            self.type_label.pack(side='left')
            self.t_value = tk.IntVar()
            self.type_g = tk.Radiobutton(self, text='Golf', variable=self.t_value, value=True)
            self.type_c = tk.Radiobutton(self, text='City', variable=self.t_value, value=False)
            self.type_g.pack(side='left')
            self.type_c.pack(side='left')
            self.type_label.grid(row=0, column=0)
            self.type_g.grid(row=0, column=1)
            self.type_c.grid(row=0, column=2)

            self.slabel = tk.StringVar()
            self.slabel.set('Shortcode:')
            self.short_label = tk.Label(self, textvariable=self.slabel)
            self.short_label.pack(side='left')
            self.shortcode = tk.Entry(self)
            self.shortcode.pack(side='left')
            self.short_label.grid(row=1, column=0)
            self.shortcode.grid(row=1, column=1)

            self.cidlabel = tk.StringVar()
            self.cidlabel.set('Client ID:')
            self.cid_label = tk.Label(self, textvariable=self.cidlabel)
            self.cid_label.pack(side='left')
            self.cid = tk.Entry(self)
            self.cid.pack(side='left')
            self.cid_label.grid(row=2, column=0)
            self.cid.grid(row=2, column=1)


            self.nclabel = tk.StringVar()
            self.nclabel.set('Name of Club:')
            self.nc_label = tk.Label(self, textvariable=self.nclabel)
            self.nc_label.pack(side='left')
            self.nc = tk.Entry(self)
            self.nc.pack(side='left')
            self.nc_label.grid(row=3, column=0)
            self.nc.grid(row=3, column=1)

            self.courseslabel = tk.StringVar()
            self.courseslabel.set('Course ID (Comma separated):')
            self.courses_label = tk.Label(self, textvariable=self.courseslabel)
            self.courses_label.pack(side='left')
            self.courses = tk.Entry(self, textvariable=tk.StringVar(None))
            self.courses.pack(side='left')
            self.courses_label.grid(row=4, column=0)
            self.courses.grid(row=4, column=1)


            self.pathlabel = tk.StringVar()
            self.pathlabel.set('Please choose file:')
            self.path_label = tk.Label(self, textvariable=self.pathlabel)
            self.path_label.pack(side='left')
            self.path_label.grid(row=5, column=0)
            self.path_button =tk.Button(self, text='Choose File', command=self.openfile)
            self.path_button.pack(side='left')
            self.path_button.grid(row=5, column=1)

            self.submit = tk.Button(self, text="Submit", command=self.run)
            self.submit.pack(side="bottom")
            self.submit.grid(row=6, column=1)

            self.quit = tk.Button(self, text='Quit', command=root.quit)
            self.quit.pack(side="bottom")
            self.quit.grid(row=6, column=2)

        def openfile(self):
            self.path = askopenfile()
            self.opened_file = tk.StringVar()
            self.opened_file.set('Opened File: {}'.format(self.path.name))
            self.file_label = tk.Label(self, textvariable=self.opened_file)
            self.file_label.pack(side='left')
            self.file_label.grid(row=5, column=2)

        def validate(self, _type):
            return True if _type in {'c', 'g'} else False

        def run(self):
            _type = 'g' if self.t_value else 'c'
            shortcode = self.shortcode.get()
            client_id = self.cid.get()
            longname = self.nc.get()
            course_id = self.courses.get()
            filename = self.path.name
            out, errors = run_from_tkinter(_type, shortcode, client_id, longname, course_id, filename)
            if len(errors) > 0:
                showerror('ERROR', '\n'.join([x for x in errors]))
            else:
                showinfo('Window', 'File located at: {}'.format(out))


    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
