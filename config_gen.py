import csv
import json
import pprint
from collections import OrderedDict, defaultdict
import settings
import to_dict


def init_std():
    _type = input('Type of club? (c or g) ')
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
    curr_tl = []
    curr_title = None
    curr_access = None
    for title, info, access, extra in info_list:
        if info == 'Front':
            curr_title = title
            curr_access = access
            continue
        elif info == 'Header':
            print(title, access, curr_tl)
            info_dict[curr_title + '[v:' + curr_access.lower() + ']'] = curr_tl
            curr_access = access
            curr_title = title
            curr_tl = []
            continue
        elif info == 'END':
            info_dict[curr_title] = curr_tl
            break
        if info == 'submenu':
            curr_tl.append((title + '|', info, access, ','.join(extra)))
        else:
            curr_tl.append((title + '|', info, access))
    pprint.pprint(info_dict)
    return info_dict


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


def to_json(info_dict):
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
                new_v.append('|'.join(elt))
        if not is_menu:
            if to_add_sub is not None:
                to_add = new_v
                primary['primary'].append((to_add_sub + to_add))
            else:
                to_add = list([k]) + new_v
                primary['primary'].append((to_add))
    # pprint.pprint(info_dict)
    STANDARD['PacesetterMainMenuDetails'] = primary
    # print(json.dumps(STANDARD, indent=4))
    return json.dumps(STANDARD, indent=4)


STANDARD = init_std()
_dict = list_to_dict(read_csv('test_menu.csv'))
# pprint.pprint(STANDARD)
_json = to_json(_dict)
with open('out.json', 'w+') as out:
    out.write(_json)
