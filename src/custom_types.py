from typing import Dict, List, Union

Spell = Dict[str, str]
Action = Dict[str, str]
SpecialAbility = Dict[str, Union[str, List[Spell]]]
LegendaryActions = Dict[str, Union[str, List[Action]]]
