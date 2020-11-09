import os
import re
from typing import List, Tuple, Union

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from custom_types import Action


def find_index(flist, func):
    for idx, var in enumerate(flist):
        if func(var):
            return idx
    return -1


def get_soup_with_cache(base, path):

    cache_folder = f'{os.path.dirname(os.path.realpath(__file__))}/../cache/'
    if not os.path.isdir(cache_folder):
        os.mkdir(cache_folder)

    cache_name = cache_folder + path.replace('/', '-')
    if os.path.isfile(cache_name):
        with open(cache_name, 'r') as file:
            html = file.read()
    else:
        response = requests.get(base + path)
        response.encoding = 'utf-8'
        html = response.text

        with open(cache_name, 'w+') as file:
            file.write(html)

    return BeautifulSoup(html, 'html.parser')


def get_creature_paths(creature_index):
    option = creature_index.find('option', string='Animales por Nombre')
    animals = option.parent.find_all('option', value=True)
    option = creature_index.find('option', string='PNJs por Nombre')
    npcs = option.parent.find_all('option', value=True)
    option = creature_index.find('option', string='Monstruos por Nombre')
    monsters = option.parent.find_all('option', value=True)

    paths = animals + npcs + monsters

    return [(path['value']).replace('./', '') for path in paths]


def extract_text_from_parent_tag(content, search, tag='b'):
    return extract_text_from_tag(content, search, tag, True)


def extract_text_from_tag(content, search, tag='b', parent=False):
    tag = content.find(tag, string=re.compile(search + r':?\s?'))

    if tag:
        if parent:
            text = tag.parent.text
        else:
            text = tag.text
        return re.sub(search + r':?\s?', '', text).replace('\n', ' ').strip()

    return None


def extract_damage_text(input_text):
    result = []
    for text in input_text.split(';'):
        # Skip errates
        if any(char.isdigit() for char in text):
            continue
        match = re.search(r'( de ataques.+)|( de armas.+)', text)
        if match:
            text = re.sub(match.group(0), '', text)
            text_array = re.split(',|y', text)
            text_array = [text.strip() + match.group(0) for text in text_array]
        else:
            text_array = re.split(',|y', text)

        text_array = [text.strip().capitalize() for text in text_array]
        result += text_array
    return result


def get_actions(content: Tag,
                tag_name: str,
                help_=False) -> Union[List[Action], Tuple[str, List[Action]]]:
    help_text = None
    p_list = content.find_all('p')
    tag = content.find('b', string=re.compile(tag_name + r':?\s?'))
    if not tag:
        return []

    actions_index = find_index(p_list, lambda p: tag == p.b)
    action_list = p_list[actions_index + 1:]

    result = []
    for tag in action_list:
        if len(tag.contents) == 1 and result:
            break
        if tag.i and tag.i.b:
            name = re.sub(r'\.|:$', '', tag.i.text.replace('\n', ' ').strip())
            desc = tag.text.replace(tag.i.text, '').replace('\n', ' ').strip()
            result.append({'name': name, 'description': desc})
        elif tag.b:
            name = re.sub(r'\.|:$', '', tag.b.text.replace('\n', ' ').strip())
            desc = tag.text.replace(tag.b.text, '').replace('\n', ' ').strip()
            extra = {'name': name, 'description': desc}
            last = result[-1]
            if not 'extra' in last:
                last['extra'] = [extra]
            else:
                last['extra'].append(extra)
        else:
            if help_:
                help_text = tag.text.replace('\n', ' ').strip()
                help_ = False
            else:
                desc = '\n' + tag.text.replace('\n', ' ')
                result[-1]['description'] += desc.strip()

    if help_text:
        return result, help_text
    return result
