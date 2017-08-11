import csv
import json
import pprint
from collections import OrderedDict, defaultdict
import settings

def read_csv(filename):
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        all_info = [(title.strip().replace('\ufeff', ''), info.strip(), access.strip(), extra) for title, info, access, *extra in reader]
        return all_info

def list_to_dict(info_list):
    info_dict = OrderedDict()
    curr_tl = []
    curr_title = None
    for title, info, access, extra in info_list:
        if info == 'Front':
            curr_title = title
            continue
        elif info == 'Header':
            info_dict[curr_title + '[v:' + access.lower() + ']'] = curr_tl
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
    return info_dict


def create_submenu(tup):
    title, sub = tup[0], tup[2]
    subs = [title.strip('|')] + [x.strip(',') for x in sub.split('~')]
    new_subs = subs[:1]
    for sub in subs[1:]:
        sub_title = sub.split('|')[0] + '||'
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
            settings.STANDARD['PacesetterHomeDetails'] = menu
            is_menu = True
        new_v = []
        for tup in v:
            elt = list(filter(None, tup))
            code, *alt = elt[1].split('|')[0].split('~')
            if code in settings.DEFAULTS:
                if len(alt) > 0:
                    elt[1] = code + '|' + settings.DEFAULTS[code] + alt[0]
                if code != 'url':
                    elt[1] += settings.DEFAULTS[code]
            elif code == 'submenu':
                submenu = create_submenu(elt)
                to_add = list([k])
                to_add.append(submenu)
                primary['primary'].append(to_add)
                is_menu = True
            new_v.append('|'.join(elt))
        if not is_menu:
            to_add = list([k]) + new_v
            primary['primary'].append((to_add))
    # pprint.pprint(info_dict)
    settings.STANDARD['PacesetterMainMenuDetails'] = primary
    # print(json.dumps(settings.STANDARD, indent=4))
    return json.dumps(settings.STANDARD, indent=4)

_dict = list_to_dict(read_csv('test_menu.csv'))
# pprint.pprint(settings.STANDARD)
_json = to_json(_dict)
with open('out.json', 'w+') as out:
    out.write(_json)
