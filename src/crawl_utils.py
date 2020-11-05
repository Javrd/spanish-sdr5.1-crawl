import os
import re
from typing import Dict, List, Tuple, Union

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from utils import find_index


def get_soup_with_cache(base, path):

    cache_folder = f'{os.path.dirname(os.path.realpath(__file__))}/../cache/'
    if not os.path.isdir(cache_folder):
        os.mkdir(cache_folder)

    cache_name = cache_folder + path.replace('/', '-')
    if os.path.isfile(cache_name):
        with open(cache_name, 'r') as f:
            html = f.read()
    else:
        response = requests.get(base + path)
        response.encoding = 'utf-8'
        html = response.text

        with open(cache_name, 'w+') as f:
            f.write(html)

    return BeautifulSoup(html, "html.parser")


def get_creature_paths(creature_index):
    option = creature_index.find("option", string="Animales por Nombre")
    animals = option.parent.find_all("option", value=True)
    option = creature_index.find("option", string="PNJs por Nombre")
    npcs = option.parent.find_all("option", value=True)
    option = creature_index.find("option", string="Monstruos por Nombre")
    monsters = option.parent.find_all("option", value=True)

    paths = animals + npcs + monsters

    return [(path["value"]).replace("./", "") for path in paths]


def extract_name(content: Tag) -> str:
    if content.find('h3'):
        name = content.h3
    elif content.find('h4'):
        name = content.h4
    else:
        name = content.h5
    return name.text.replace('\n', '').strip()


def extract_subtitle_info(content: Tag) -> Tuple[str, str, str, List[str]]:
    subtitle_text: str = content.p.text
    subtitle = subtitle_text.replace('\n', '').split(",")
    alignment = subtitle.pop().strip()
    size_type_info = ",".join(subtitle).strip()
    size_type_list = size_type_info.split(" ")
    tags = []
    match = re.search('\((.+?)\)', size_type_info)
    if match:
        details = match.group(1)
        tags += details.split(',')

        size_type_info = size_type_info.replace(match.group(0), '').strip()
        size_type_list = size_type_info.split(" ")
        size = size_type_list.pop().strip()
        type_ = " ".join(size_type_list).strip()
    elif size_type_list[0] == "Enjambre":
        type_ = f"{size_type_list[3][0].upper()}{size_type_list[3][1:-1]}"
        type_ = type_.strip()
        size = size_type_list[1].strip()
        tags.append(size_type_list[0].strip())
    else:
        size = size_type_list.pop()
        type_ = " ".join(size_type_list)

    return alignment, size, type_, tags


def extract_description(content: Tag) -> str:
    p_list = content.find_all('p')
    ac_tag = content.find("b", string=re.compile("Clase de Armadura:?\s?"))
    ac_index = find_index(p_list, lambda p: p.b == ac_tag)
    return "\n".join([p.text.replace('\n', ' ') for p in p_list[1:ac_index]])


def extract_armor_class(content: Tag) -> List[Dict[str, Union[int, str]]]:
    result = []
    ac_tag = content.find("b", string=re.compile("Clase de Armadura:?\s?"))
    ac_text = ac_tag.parent.text
    ac_text = " ".join(ac_text.replace('\n', ' ').split(' ')[3:])
    acs = ac_text.split(",")

    if len(acs) > 1 and not acs[1][1].strip().isdigit():
        acs = [', '.join(acs)]

    for ac in acs:
        ac = ac.strip()
        type_ = ''
        condition = ''
        ac_array = ac.split(' ')

        if len(ac_array) > 1 and ac_array[1][1].isdigit():
            second_ac = " ".join(ac_array[1:])
            ac = ac.replace(second_ac, '').strip()
            second_ac = second_ac.replace("(", "").replace(")", "")
            acs.append(second_ac)

        match = re.search('\((.+?)\)', ac)
        if match:
            type_ = match.group(1).strip()
            ac = ac.replace(match.group(0), '')

        ac, *condition_array = ac.split(' ')
        condition = " ".join(condition_array).strip()
        result.append({
            "armor_class": int(ac),
            "type": type_,
            "condition": condition
        })
    return result


def extract_hit_points(content: Tag) -> Tuple[int, str]:
    hp_tag = content.find("b", string=re.compile("Puntos de golpe:?\s?"))
    if hp_tag:
        hp_tag = hp_tag.parent
    else:
        hp_tag = content.find("p", string=re.compile("Puntos de golpe:?\s?"))
    hp_text = " ".join(hp_tag.text.replace('\n', ' ').split(' ')[3:])
    match = re.search('\((.+?)\)', hp_text)
    dice = match.group(1).strip()
    hp = hp_text.replace(match.group(0), '').strip()
    return int(hp), dice


def extract_speed(content: Tag) -> str:
    speed_tag = content.find("b", string=re.compile("Velocidad:?\s?"))
    speed = " ".join(speed_tag.parent.text.replace('\n', ' ').split(' ')[1:])
    speed_array = [speed.strip() for speed in speed.split(", ")]
    return speed_array


def extract_initiative(content: Tag) -> str:
    rows = content.table.find_all('tr')[1].find_all('td')[1]
    return int(rows.text.replace('\n', '').split('(')[1][1:-1])


def extract_abilities(content: Tag) -> Dict[str, int]:
    return {
        "strength": "TODO",
        "dexterity": "TODO",
        "constitution": "TODO",
        "intelligence": "TODO",
        "wisdom": "TODO",
        "charisma": "TODO",
    }


def extract_challenge_rating(content: Tag) -> str:
    challenge_tag = content.find("b", string=re.compile("Desafío:?\s?"))
    challenge_text = challenge_tag.parent.text
    return challenge_text.replace('\n', '').split(':')[1].strip().split(" ")[0]
