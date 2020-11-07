import os
import re

import requests
from bs4 import BeautifulSoup


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
        if (any(char.isdigit() for char in text)):
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
