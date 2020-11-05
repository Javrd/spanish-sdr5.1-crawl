import json
import os
import traceback

from bs4.element import Tag
from unidecode import unidecode

from crawl_utils import (extract_abilities, extract_armor_class,
                         extract_challenge_rating, extract_description,
                         extract_hit_points, extract_initiative, extract_name,
                         extract_speed, extract_subtitle_info,
                         get_creature_paths, get_soup_with_cache)
from settings import set_logger

base = "http://srd.nosolorol.com/DD5/"
logger = set_logger(__name__)


def extract_from_url(path: str):
    creature = {}
    link = base + path
    try:
        soup = get_soup_with_cache(base, path)

        content: Tag = soup.select("#mainContent > div.row > div.col")[0]

        name = extract_name(content)
        logger.debug(f'{name}')

        name_id = unidecode(name).lower()
        name_id = name_id.replace(' ', '-').replace('(', '-').replace(')', '-')
        fid = f"sdr5-spanish.{name_id}"

        alignment, size, type_, tags = extract_subtitle_info(content)
        hit_points, hit_dice = extract_hit_points(content)

        source = f"SRD 5.1 Español:{link}"

        return {
            "index": fid,
            "name": name,
            "size": size,
            "type": type_,
            "tags": tags,
            "alignment": alignment,
            "description": extract_description(content),
            "armor_class": extract_armor_class(content),
            "hit_points": hit_points,
            "hit_dice": hit_dice,
            "speed": extract_speed(content),
            "initiative": extract_initiative(content),
            "abilities": extract_abilities(content),
            "saving-throws": "TODO",
            "skills": "TODO",
            "damage_vulnerabilities": "TODO",
            "damage_resistances": "TODO",
            "damage_immunities": "TODO",
            "condition_immunities": "TODO",
            "senses": "TODO",
            "languages": "TODO",
            "challenge_rating": extract_challenge_rating(content),
            "special_abilities": "TODO",
            "actions": "TODO",
            "legendary_actions": "TODO",
            "source": source,
        }

    except Exception as _:
        logger.error(f"Error: {link} couldn't been extracted")
        logger.error(f'{traceback.format_exc()}')


if __name__ == "__main__":
    dirpath = os.path.dirname(os.path.realpath(__file__))
    creature_index = get_soup_with_cache(base, 'bestiario_index.html')
    creature_paths = get_creature_paths(creature_index)

    result = []
    for path in creature_paths:
        result.append(extract_from_url(path))

    with open(f'{dirpath}/../output/monsters.json', 'w',
              encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
