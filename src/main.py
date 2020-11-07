import json
import os
import traceback

from bs4.element import Tag
from unidecode import unidecode

import crawl_utils as cu
from settings import set_logger

BASE = "http://srd.nosolorol.com/DD5/"
logger = set_logger(__name__)


def extract_from_url(path: str):
    link = BASE + path
    try:
        soup = cu.get_soup_with_cache(BASE, path)

        content: Tag = soup.select("#mainContent > div.row > div.col")[0]

        name = cu.extract_name(content)
        logger.debug(f'{name}')

        name_id = unidecode(name).lower()
        name_id = name_id.replace(' ', '-').replace('(', '-').replace(')', '-')
        fid = f"srd5-spanish.{name_id}"

        alignment, size, type_, tags = cu.extract_subtitle_info(content)
        hit_points, hit_dice = cu.extract_hit_points(content)

        source = f"SRD 5.1 Español:{link}"

        return {
            "index": fid,
            "name": name,
            "size": size,
            "type": type_,
            "tags": tags,
            "alignment": alignment,
            "description": cu.extract_description(content),
            "armor_class": cu.extract_armor_class(content),
            "hit_points": hit_points,
            "hit_dice": hit_dice,
            "speed": cu.extract_speed(content),
            "initiative": cu.extract_initiative(content),
            "abilities": cu.extract_abilities(content),
            "saving-throws": cu.extract_saving_throws(content),
            "skills": cu.extract_skills(content),
            "damage_vulnerabilities": cu.extract_vulnerabilities(content),
            "damage_resistances": cu.extract_resistances(content),
            "damage_immunities": cu.extract_immunities(content),
            "condition_immunities": cu.extract_condition_immunities(content),
            "senses": cu.extract_senses(content),
            "languages": cu.extract_languages(content),
            "challenge_rating": cu.extract_challenge_rating(content),
            "special_abilities": cu.extract_special_abilities(content),
            "actions": cu.extract_actions(content),
            "legendary_actions": cu.extract_legendary_actions(content),
            "source": source,
        }

    except Exception as _:
        logger.error(f"Error: {link} couldn't been cu.extracted")
        logger.error(f'{traceback.format_exc()}')


if __name__ == "__main__":
    dirpath = os.path.dirname(os.path.realpath(__file__))
    output_folder = f'{dirpath}/../output'
    creature_index = cu.get_soup_with_cache(BASE, 'bestiario_index.html')
    creature_paths = cu.get_creature_paths(creature_index)

    result = []
    for creature_path in creature_paths:
        result.append(extract_from_url(creature_path))

    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    with open(f'{output_folder}/monsters.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
