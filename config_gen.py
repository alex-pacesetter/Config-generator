import csv
import json
import pprint
from collections import OrderedDict, defaultdict
import settings
import to_dict


def init_std(_type):
    if _type == 'c':
        STANDARD = to_dict.standard_dict()
    else:
        STANDARD = to_dict.standard_dict('golf')
    return STANDARD


def read_csv(filename):
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        all_info = [(title.strip().replace('\ufeff', ''), info.strip(), access.strip(), extra) for title, info, access, *extra in reader]
        return all_info


def list_to_dict(info_list):
    info_dict = OrderedDict()
    golf_dict = OrderedDict()
    curr_tl = []
    curr_title = None
    curr_access = None
    curr_dict = info_dict
    switched = False
    for title, info, access, extra in info_list:
        if info == 'Front':
            curr_title = title
            curr_access = access
            continue
        elif info == 'Header':
            if not switched:
                if curr_access == '':
                    curr_dict[curr_title] = curr_tl
                else:
                    curr_dict[curr_title + '[v:' + curr_access.lower().replace(' ', '') + ']'] = curr_tl
            curr_access = access
            curr_title = title
            curr_tl = []
            switched = False
            continue
        elif info == 'GOLF':
            if curr_access == '':
                curr_dict[curr_title] = curr_tl
            else:
                curr_dict[curr_title + '[v:' + curr_access.lower().replace(' ', '') + ']'] = curr_tl
            curr_dict = golf_dict
            switched = True
            continue
        elif info == 'END':
            curr_dict[curr_title] = curr_tl
            break
        if info == 'submenu':
            curr_tl.append((title + '|', info, access, ','.join(extra)))
        else:
            curr_tl.append((title + '|', info, access))
    return info_dict, golf_dict


def create_submenu(tup, code=None, access=False):
    title, sub = tup[0], tup[-1]
    subs = [title.strip('|')] + [x.strip(',') for x in sub.split('~')]
    new_subs = subs[:1]
    if access:
        new_subs[0] += '[v:{}]'.format(tup[-2].lower())
    for sub in subs[1:]:
        sub_title = sub.split('|')[0] + '||'
        if code == 'url':
            new_subs.append(sub_title + sub.split('|')[1] + '|' + settings.DEFAULTS[code] + sub.split('|')[2])
        else:
            new_subs.append(sub_title + '|'.join(sub.split('|')[1:]))
    return new_subs


def front_menu(v):
    start = settings.COLORS['box'] + '|' + settings.COLORS['text'] + '|'
    def_list = [elt[:-1] for elt in [start + '|'.join(elt) for elt in v]]
    return {'default': def_list}


def create_more_courses(course_id, STANDARD):
    pcc = {"FBReminderHole": 8, "FBReminderPosition": "tee"}
    prmd = ["Golf", "Weather||url|/web/CLIENT_ID/weather", "Notifications||notifications", "End Round||endround"]
    menu = STANDARD['PacesetterRoundMenuDetails']['COURSE_ID_member']
    for course in course_id[1:]:
        STANDARD['PacesetterCourseConfig'].update({course:pcc})
        STANDARD['PacesetterCourseIDs'].append(course)
        STANDARD['PacesetterRoundMenuDetails'].update({course:[prmd]})
        s_course = str(course) + '_member'
        STANDARD['PacesetterRoundMenuDetails'].update({s_course:menu})
    return json.dumps(STANDARD, indent=4)


def to_json(info_dict, STANDARD, inner='primary', outer='PacesetterMainMenuDetails', key='c'):
    primary = defaultdict(list)
    for k, v in info_dict.items():
        is_menu = False
        if k.split('[')[0] == 'Menu':
            menu = front_menu(v)
            STANDARD['PacesetterHomeDetails'] = menu
            is_menu = True
        new_v = []
        to_add_sub = None
        for tup in v:
            is_submenu = False
            elt = list(filter(None, tup))
            code, *alt = elt[1].split('|')[0].split('~')
            if code in settings.DEFAULTS:
                if len(alt) > 0:
                    elt[1] = code + '|' + settings.DEFAULTS[code] + alt[0]
                if code != 'url':
                    elt[1] += settings.DEFAULTS[code]
            if code == 'submenu':
                submenu = create_submenu(elt, elt[-1].split('|')[1], len(elt) == 4)
                # Fixes bug where only one submenu per header worked
                if not to_add_sub:
                    to_add_sub = list([k])
                to_add_sub.append(submenu)
                is_submenu = True
            else:
                if not is_submenu and len(elt) > 2 and code != 'url':
                    to_add = elt[0][:-1] + '[v:{}]||'.format(elt[2].lower()).replace(' ', '') + '|'.join(elt[1:-1])
                    new_v.append(to_add)
                elif len(elt) > 2:
                    elt[0] = elt[0][:-1] + '[v:{}]|'.format(elt[-1].lower())
                    new_v.append('|'.join(elt[:-1]))
                else:
                    new_v.append('|'.join(elt))
        if not is_menu:
            if to_add_sub is not None:
                to_add = new_v
                primary[inner].append((to_add_sub + to_add))
            else:
                to_add = list([k]) + new_v
                primary[inner].append((to_add))
    if key == 'c':
        STANDARD[outer] = primary
    elif key == 'g':
        STANDARD[outer].update(primary)
    return json.dumps(STANDARD, indent=4)

def main():
    _type = input('Type of club? (c or g) ').strip()
    while _type not in {'c','g'}:
        _type = input("That's not 'c' or 'g'. Type of club? (c or g) ").strip()
    shortcode = input('Shortcode: ').strip()
    client_id = input('Client ID: ').strip()
    longname = input('Name of Club: ').strip()
    course_id = input('Course ID (Comma separated): ').split(',') if _type == 'g' else None
    STANDARD = init_std(_type)
    std_dict, golf_dict = list_to_dict(read_csv('real_menu_test.csv'))
    std_json = to_json(std_dict, STANDARD)
    if _type == 'g':
        golf_json = to_json(golf_dict, STANDARD, 'COURSE_ID_member', 'PacesetterRoundMenuDetails', 'g')

    if course_id and len(course_id) == 1:
        course_id = course_id[0]
    elif course_id:
        golf_json = create_more_courses(course_id, STANDARD)
        course_id = course_id[0]

    with open('out.json', 'w+') as out:
        if _type == 'c':
            updated_json = std_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id)
            out.write(updated_json)
        elif _type == 'g':
            updated_json = golf_json.replace('SHORTCODE', shortcode).replace('LONGNAME', longname).replace('CLIENT_ID', client_id).replace('COURSE_ID', course_id)
            out.write(updated_json)


if __name__ == '__main__':
    main()
