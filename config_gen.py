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
                curr_dict[curr_title + '[v:' + curr_access.lower() + ']'] = curr_tl
            curr_access = access
            curr_title = title
            curr_tl = []
            switched = False
            continue
        elif info == 'GOLF':
            curr_dict[curr_title + '[v:' + curr_access.lower() + ']'] = curr_tl
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


def create_submenu(tup, code=None):
    title, sub = tup[0], tup[2]
    subs = [title.strip('|')] + [x.strip(',') for x in sub.split('~')]
    new_subs = subs[:1]
    for sub in subs[1:]:
        sub_title = sub.split('|')[0] + '||'
        if code == 'url':
            new_subs.append(sub_title + '|' + sub.split('|')[1] + '|' + settings.DEFAULTS[code] + sub.split('|')[2])
        else:
            new_subs.append(sub_title + '|'.join(sub.split('|')[1:]))
    return new_subs


def front_menu(v):
    start = settings.COLORS['box'] + '|' + settings.COLORS['text'] + '|'
    def_list = [start + ''.join(elt) for elt in v]
    return {'default': def_list}


def to_json(info_dict, inner='primary', outer='PacesetterMainMenuDetails', key='c'):
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
                submenu = create_submenu(elt, elt[2].split('|')[1])
                to_add_sub = list([k])
                to_add_sub.append(submenu)
                is_submenu = True
            else:
                if not is_submenu and len(elt) > 2:
                    to_add = elt[0][:-1] + '[v:{}]||'.format(elt[2].lower()) + '|'.join(elt[1:-1])
                    new_v.append(to_add)
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


_type = input('Type of club? (c or g) ')
STANDARD = init_std(_type)
std_dict, golf_dict = list_to_dict(read_csv('test_menu.csv'))
# pprint.pprint(std_dict)
# pprint.pprint(golf_dict)
# pprint.pprint(STANDARD)
std_json = to_json(std_dict)
if _type == 'g':
    golf_json = to_json(golf_dict, 'COURSE_ID_member', 'PacesetterRoundMenuDetails', 'g')

with open('out.json', 'w+') as out:
    if _type == 'c':
        out.write(std_json)
    elif _type == 'g':
        out.write(golf_json)
