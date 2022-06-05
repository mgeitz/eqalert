#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: util/spell-to-json.py
   Copyright (C) 2022 Michael Geitz

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

   Parse and react to eqemu logs
"""

import json
import os

# Spell file to convert
raw_spell_file_location = "./spells_us.txt"

raw_spell_file = open(raw_spell_file_location, "r")
raw_spell_file_lines = raw_spell_file.readlines()


# Prep JSON Target
spell_json_file = "./spells_us.json"

## Empty Slate
spell_json = {"spells": {}}

with open(spell_json_file, "w") as f:
    json.dump(spell_json, f, sort_keys=True, indent=2)

json_data = open(spell_json_file, "r")
spell_data = json.load(json_data)
json_data.close()

# Write to JSON
for line in raw_spell_file_lines:
    modified_line = line.split("^")

    spell_id = modified_line[0]
    spell_name = modified_line[1]
    spell_player = modified_line[2]
    spell_teleport_zone = modified_line[3]
    spell_you_cast = modified_line[4]
    spell_other_casts = modified_line[5]
    spell_cast_on_you = modified_line[6]
    spell_cast_on_other = modified_line[7]
    spell_fades = modified_line[8]
    spell_range = modified_line[9]
    spell_aoerange = modified_line[10]
    spell_pushback = modified_line[11]
    spell_pushup = modified_line[12]
    spell_cast_time = modified_line[13]
    spell_recovery_time = modified_line[14]
    spell_recast_time = modified_line[15]
    spell_buffdurationformula = modified_line[16]
    spell_buff_duration = str(int(modified_line[17]) * 6)
    spell_aeduration = str(int(modified_line[18]) * 6)
    spell_mana = modified_line[19]
    spell_base = modified_line[20]
    spell_base2 = modified_line[21]
    spell_max = modified_line[22]
    spell_icon = modified_line[23]
    spell_memicon = modified_line[24]
    spell_components = modified_line[25]
    spell_component_counts = modified_line[26]
    spell_noexpendreagent = modified_line[27]
    spell_formula = modified_line[28]
    spell_lighttype = modified_line[29]
    spell_goodeffect = modified_line[30]
    spell_activated = modified_line[31]
    spell_resisttype = modified_line[32]
    spell_effectid = modified_line[33]
    spell_basediff = modified_line[34]
    spell_skill = modified_line[35]
    spell_zonetype = modified_line[36]
    spell_environmenttype = modified_line[37]
    spell_timeofday = modified_line[38]
    spell_classes = modified_line[39]
    spell_castinganim = modified_line[40]
    spell_targetanim = modified_line[41]
    spell_traveltype = modified_line[42]
    spell_spellaffectindex = modified_line[43]
    spell_spacing2 = modified_line[44]
    spell_resistdiff = modified_line[45]
    spell_spacing3 = modified_line[46]
    spell_recourselink = modified_line[47]
    spell_spacing4 = modified_line[48]
    spell_descnum = modified_line[49]
    spell_typedescnum = modified_line[50]
    spell_effectdescnum = modified_line[51]
    spell_spacing5 = modified_line[52]

    if not spell_name.startswith("test"):
        spell_data["spells"].update(
            {
                spell_name: {
                    "time": {
                        #                        "cast": spell_cast_time,
                        #                        "recovery": spell_recovery_time,
                        #                        "recast": spell_recast_time,
                        #                        "duration_formula": spell_buffdurationformula,
                        "duration": spell_buff_duration,
                        "ae": spell_aeduration,
                    },
                    "text": {
                        "you_cast": spell_you_cast,
                        "other_casts": spell_other_casts,
                        "cast_on_you": spell_cast_on_you,
                        "cast_on_other": spell_cast_on_other,
                        "fades": spell_fades,
                    },
                    #                    "other": {
                    #                        "teleport_zone": spell_teleport_zone,
                    #                        "range": spell_range,
                    #                        "aoe_range": spell_aoerange,
                    #                        "push_back": spell_pushback,
                    #                        "push_up": spell_pushup,
                    #                        "mana": spell_mana,
                    #                        "base": spell_base,
                    #                        "base_2": spell_base2,
                    #                        "max": spell_max,
                    #                        "icon": spell_icon,
                    #                        "mem_icon": spell_memicon,
                    #                        "components": spell_components,
                    #                        "no_expend_reagent": spell_noexpendreagent,
                    #                        "formula": spell_formula,
                    #                        "light_type": spell_lighttype,
                    #                        "good_effect": spell_goodeffect,
                    #                        "activated": spell_activated,
                    #                        "resist_type": spell_resisttype,
                    #                        "effect_id": spell_effectid,
                    #                        "base_diff": spell_basediff,
                    #                        "skill": spell_skill,
                    #                        "zone_type": spell_zonetype,
                    #                        "environment_type": spell_environmenttype,
                    #                        "time_of_day": spell_timeofday,
                    #                        "classes": spell_classes,
                    #                        "casting_animation": spell_castinganim,
                    #                        "target_animation": spell_targetanim,
                    #                        "travel_type": spell_traveltype,
                    #                        "spell_affect_index": spell_spellaffectindex,
                    #                        "spacing_2": spell_spacing2,
                    #                        "resist_diff": spell_resistdiff,
                    #                        "spacing_3": spell_spacing3,
                    #                        "recourse_link": spell_recourselink,
                    #                        "spacing_4": spell_spacing4,
                    #                        "desc_num": spell_descnum,
                    #                        "type_desc_num": spell_typedescnum,
                    #                        "effect_desc_num": spell_effectdescnum,
                    #                        "spacing_5": spell_spacing5
                    #                    }
                }
            }
        )

json_data = open(spell_json_file, "w")
json.dump(spell_data, json_data, sort_keys=True, indent=2)
json_data.close()
