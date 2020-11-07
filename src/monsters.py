import re
from typing import Dict, List, Tuple, Union

from bs4.element import Tag

from utils import (extract_damage_text, extract_text_from_parent_tag,
                   extract_text_from_tag, find_index)


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
    match = re.search(r'\((.+?)\)', size_type_info)
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
    ac_tag = content.find("b", string=re.compile(r"Clase de Armadura:?\s?"))
    ac_index = find_index(p_list, lambda p: p.b == ac_tag)
    return "\n".join([p.text.replace('\n', ' ') for p in p_list[1:ac_index]])


def extract_armor_class(content: Tag) -> List[Dict[str, Union[int, str]]]:
    result = []
    ac_text = extract_text_from_parent_tag(content, "Clase de Armadura")
    acs = ac_text.split(",")

    if len(acs) > 1 and not acs[1][1].strip().isdigit():
        acs = [', '.join(acs)]

    for armor_class in acs:
        armor_class = armor_class.strip()
        type_ = ''
        condition = ''
        ac_array = armor_class.split(' ')

        if len(ac_array) > 1 and ac_array[1][1].isdigit():
            second_ac = " ".join(ac_array[1:])
            armor_class = armor_class.replace(second_ac, '').strip()
            second_ac = second_ac.replace("(", "").replace(")", "")
            acs.append(second_ac)

        match = re.search(r'\((.+?)\)', armor_class)
        if match:
            type_ = match.group(1).strip()
            armor_class = armor_class.replace(match.group(0), '')

        armor_class, *condition_array = armor_class.split(' ')
        condition = " ".join(condition_array).strip()
        result.append({
            "armor_class": int(armor_class),
            "type": type_,
            "condition": condition
        })
    return result


def extract_hit_points(content: Tag) -> Tuple[int, str]:
    search = "Puntos de golpe"
    hp_text = extract_text_from_parent_tag(content, search)
    if not hp_text:
        hp_text = extract_text_from_tag(content, search, tag='p')
    match = re.search(r'\((.+?)\)', hp_text)
    dice = match.group(1).strip()
    hit_points = hp_text.replace(match.group(0), '').strip()
    return int(hit_points), dice


def extract_speed(content: Tag) -> str:
    speed_text = extract_text_from_parent_tag(content, "Velocidad")
    match = re.search(r'\((.+?)\)', speed_text)
    special_array = []

    if match:
        special_condition = re.search(r'en forma .+', match.group(1))
        if special_condition:
            speed_text = speed_text.replace(match.group(0), '').strip()
            special_speed = match.group(1).replace(special_condition.group(0),
                                                   '').strip()
            special_array = [
                f'{speed} {special_condition.group(0)}'
                for speed in special_speed.split(", ")
            ]

    speed_array = [
        speed.strip() for speed in speed_text.replace('.', ',').split(", ")
    ]
    speed_array += special_array

    result = {}
    for speed in speed_array:
        speed_splitted = speed.split(" ")
        if not speed_splitted[0][0].isdecimal():
            speed_splitted.append(speed_splitted.pop(0).lower())

        if len(speed_splitted) < 3:
            speed_splitted.append('caminando')

        result[" ".join(speed_splitted[2:])] = int(speed_splitted[0])

    return result


def extract_initiative(content: Tag) -> str:
    row = content.table.find_all('tr')[1].find_all('td')[1]
    mod = re.search(r'(.+)\((.+?)\)', row.text).group(2)
    mod = mod.replace('−', '-').replace('–', '-')
    return int(mod)


def extract_abilities(content: Tag) -> Dict[str, int]:
    rows = content.table.find_all('tr')[1].find_all('td')
    abilities = []
    for row in rows:
        row_text = row.text.replace('\n', ' ')
        ability = re.search(r'(.+)\((.+?)\)', row_text).group(1).strip()
        abilities.append(int(ability))

    result = {
        "strength": abilities[0],
        "dexterity": abilities[1],
        "constitution": abilities[2],
        "intelligence": abilities[3],
        "wisdom": abilities[4],
        "charisma": abilities[5],
    }
    return result


def extract_saving_throws(content: Tag) -> Dict[str, int]:
    throws_text = extract_text_from_parent_tag(content, "Tiradas de salvación")
    result = {}
    if throws_text:
        throws_array = throws_text.split(",")
        for saving_throw in throws_array:
            match = re.search(r"(\w{3})\s(.+)", saving_throw)
            if match:
                result[match.group(1)] = int(match.group(2))
    return result


def extract_skills(content: Tag) -> Dict[str, int]:
    skills_text = extract_text_from_parent_tag(content, "Habilidades")
    result = {}
    if skills_text:
        skills_array = skills_text.split(",")
        for skill in skills_array:
            special = re.search(r'\((.+?)\)', skill)
            if special:
                skill = skill.replace(special.group(0), '')

            match = re.search(r"(\w+[\s?\w*]+)\s(.+)", skill)
            if match:
                result[match.group(1)] = int(match.group(2))
                if special:
                    conditional = f'{match.group(1)} {special.group(1)[3:]}'
                    result[conditional] = int(special.group(1)[0:2])
    return result


def extract_vulnerabilities(content):
    text = extract_text_from_parent_tag(content, "Vulnerabilidades al daño")
    if text:
        return extract_damage_text(text)
    return None


def extract_resistances(content):
    text = extract_text_from_parent_tag(content, "Resistencias al daño")
    if text:
        return extract_damage_text(text)
    return None


def extract_immunities(content):
    text = extract_text_from_parent_tag(content, "Inmunidades al daño")
    if text:
        return extract_damage_text(text)
    return None


def extract_condition_immunities(content):
    return "TODO"


def extract_senses(content):
    return "TODO"


def extract_languages(content):
    return "TODO"


def extract_challenge_rating(content: Tag) -> str:
    return extract_text_from_parent_tag(content, "Desafío")


def extract_special_abilities(content):
    return "TODO"


def extract_actions(content):
    return "TODO"


def extract_legendary_actions(content):
    return "TODO"
