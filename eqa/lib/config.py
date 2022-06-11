#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/config.py
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
"""

import json
import os
import sys
import pkg_resources
import re

import eqa.lib.settings as eqa_settings
import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct


def init(base_path):
    """Create any missing config files"""
    try:
        generated = build_config(base_path)

        if generated:
            print("One or more new versioned configuration files have been generated.")
            print("Older files have been archived under config/archive/\n")
            print("Please validate your config/settings.json and relaunch eqalert.")
            exit(1)

    except Exception as e:
        eqa_settings.log(
            "config init: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def read_config(base_path):
    """All the config"""
    try:

        line_alerts = {}

        # Characters
        config_path_char = base_path + "config/characters.json"
        json_data = open(config_path_char, "r", encoding="utf-8")
        config_file_characters = json.load(json_data)
        json_data.close()
        config_characters = eqa_struct.config_file(
            "characters", config_path_char, config_file_characters
        )

        # Settings
        config_path_settings = base_path + "config/settings.json"
        json_data = open(config_path_settings, "r", encoding="utf-8")
        config_file_settings = json.load(json_data)
        json_data.close()
        config_settings = eqa_struct.config_file(
            "settings", config_path_settings, config_file_settings
        )

        # Zones
        config_path_zones = base_path + "config/zones.json"
        json_data = open(config_path_zones, "r", encoding="utf-8")
        config_file_zones = json.load(json_data)
        json_data.close()
        config_zones = eqa_struct.config_file(
            "zones", config_path_zones, config_file_zones
        )

        ## Combat
        config_path_line_combat = base_path + "config/line-alerts/combat.json"
        json_data = open(config_path_line_combat, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts.update(config_file_line_alerts)

        ## Spell General
        config_path_line_spell_general = (
            base_path + "config/line-alerts/spell-general.json"
        )
        json_data = open(config_path_line_spell_general, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Spell Specific
        config_path_line_spell_specific = (
            base_path + "config/line-alerts/spell-specific.json"
        )
        json_data = open(config_path_line_spell_specific, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Pets
        config_path_line_pets = base_path + "config/line-alerts/pets.json"
        json_data = open(config_path_line_pets, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Recieved NPC
        config_path_line_chat_recieved_npc = (
            base_path + "config/line-alerts/chat-recieved-npc.json"
        )
        json_data = open(config_path_line_chat_recieved_npc, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Recieved
        config_path_line_chat_recieved = (
            base_path + "config/line-alerts/chat-recieved.json"
        )
        json_data = open(config_path_line_chat_recieved, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Sent
        config_path_line_chat_sent = base_path + "config/line-alerts/chat-sent.json"
        json_data = open(config_path_line_chat_sent, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Command Output
        config_path_line_command_output = (
            base_path + "config/line-alerts/command-output.json"
        )
        json_data = open(config_path_line_command_output, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## System Messages
        config_path_line_system_messages = (
            base_path + "config/line-alerts/system-messages.json"
        )
        json_data = open(config_path_line_system_messages, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Group System Messages
        config_path_line_group_system_messages = (
            base_path + "config/line-alerts/group-system-messages.json"
        )
        json_data = open(config_path_line_group_system_messages, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Loot Trade Messages
        config_path_line_loot_trade = base_path + "config/line-alerts/loot-trade.json"
        json_data = open(config_path_line_loot_trade, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Emotes
        config_path_line_emotes = base_path + "config/line-alerts/emotes.json"
        json_data = open(config_path_line_emotes, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Who
        config_path_line_who = base_path + "config/line-alerts/who.json"
        json_data = open(config_path_line_who, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Other
        config_path_line_other = base_path + "config/line-alerts/other.json"
        json_data = open(config_path_line_other, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        config_line_alerts = eqa_struct.config_file("line-alerts", None, line_alerts)

        configs = eqa_struct.configs(
            config_characters, config_settings, config_zones, config_line_alerts
        )

        return configs

    except Exception as e:
        print(
            "config read: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "config read: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_logs(configs):
    """Add characters and servers of eqemu_ prefixed files in the log path"""

    try:
        log_files = [
            f
            for f in os.listdir(
                configs.settings.config["settings"]["paths"]["everquest_logs"]
            )
            if os.path.isfile(
                os.path.join(
                    configs.settings.config["settings"]["paths"]["everquest_logs"], f
                )
            )
        ]

        for logs in log_files:
            if "eqlog_" in logs:
                emu, middle, end = logs.split("_")
                server_name = end.split(".")[0]
                char_name = middle
                char_server = char_name + "_" + server_name
                if char_server not in configs.characters.config["char_logs"].keys():
                    add_char_log(char_name, server_name, configs)
                if len(configs.settings.config["last_state"].keys()) == 0:
                    bootstrap_state(configs, char_name, server_name)

    except Exception as e:
        print(
            "set config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "set config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_char_log(char, server, configs):
    """Adds a new character to the config"""
    try:
        char_server = char + "_" + server
        char_log = "eqlog_" + char.title() + "_" + server + ".txt"

        configs.characters.config["char_logs"].update(
            {
                char_server: {
                    "character": char,
                    "server": server,
                    "file_name": char_log,
                    "disabled": "false",
                    "char_state": {
                        "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                        "direction": "unavailable",
                        "zone": "unavailable",
                        "encumbered": "false",
                        "bind": "unavailable",
                        "level": "unavailable",
                        "class": "unavailable",
                        "guild": "unavailable",
                    },
                }
            }
        )
        json_data = open(configs.characters.path, "w", encoding="utf-8")
        json.dump(configs.characters.config, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        print(
            "add char: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "add char: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def bootstrap_state(configs, char, server):
    """Generate and save state to config"""

    try:
        data = configs.settings.config
        data["last_state"].update(
            {
                "server": server,
                "character": char,
                "afk": "false",
                "group": "false",
                "leader": "false",
                "raid": "false",
            }
        )
        json_data = open(configs.settings.path, "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "bootstrap state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_config_chars(configs):
    """Return each unique character log"""
    try:
        chars = []
        for char_server in configs.characters.config["char_logs"].keys():
            if (
                configs.characters.config["char_logs"][char_server]["disabled"]
                == "false"
            ):
                chars.append(char_server)

        return chars

    except Exception as e:
        eqa_settings.log(
            "get config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_spell_timers(data_path, eq_spells_file_path):
    """Parse spells_us.txt to data/spell-timers.json"""
    try:
        # Valid Spells
        valid_spells = [
            "aanyas_animation",
            "aanyas_quickening",
            "abolish_disease",
            "abolish_enchantment",
            "abolish_posion",
            "abscond",
            "abundant_drink",
            "abundant_food",
            "accuracy",
            "acid_jet",
            "acumen",
            "adorning_grace",
            "adroitness",
            "aegis",
            "aegis_of_bathezid",
            "aegis_of_ro",
            "aegolism",
            "affliction",
            "agility",
            "agilmentes_aria_of_eagles",
            "alacrity",
            "alenias_disenchanting_melody",
            "alliance",
            "allure",
            "allure_of_death",
            "allure_of_the_wild",
            "alluring_aura",
            "alluring_whispers",
            "aloe_sweat",
            "alter_plane_hate",
            "alter_plane_sky",
            "anarchy",
            "ancient_breath",
            "angstilchs_appalling_screech",
            "angstilchs_assonance",
            "animate_dead",
            "annul_magic",
            "ant_legs",
            "anthem_de_arms",
            "antidote",
            "arch_lich",
            "arch_shielding",
            "armor_of_faith",
            "armor_of_protection",
            "asphyxiate",
            "assiduous_vision",
            "asystole",
            "atols_spectral_shackles",
            "atone",
            "augment",
            "augment_death",
            "augmentation",
            "augmentation_of_death",
            "aura_of_antibody",
            "aura_of_battle",
            "aura_of_black_petals",
            "aura_of_blue_petals",
            "aura_of_cold",
            "aura_of_green_petals",
            "aura_of_heat",
            "aura_of_marr",
            "aura_of_purity",
            "aura_of_red_petals",
            "aura_of_white_petals",
            "avalanche",
            "avatar",
            "avatar_power",
            "bandoleer_of_luclin",
            "bane_of_nife",
            "banish_summoned",
            "banish_undead",
            "banishment",
            "banishment_of_shadows",
            "banshee_aura",
            "barbcoat",
            "barrier_of_combustion",
            "barrier_of_force",
            "battery_vision",
            "bedlam",
            "befriend_animal",
            "beguile",
            "beguile_animals",
            "beguile_plants",
            "beguile_undead",
            "bellowing_winds",
            "benevolence",
            "berserker_madness_i",
            "berserker_madness_ii",
            "berserker_madness_iii",
            "berserker_madness_iv",
            "berserker_spirit",
            "berserker_strength",
            "bind_affinity",
            "bind_sight",
            "bladecoat",
            "blanket_of_forgetfulness",
            "blast_of_cold",
            "blast_of_poison",
            "blaze",
            "blessing_of_nature",
            "blessing_of_the_blackstar",
            "blessing_of_the_grove",
            "blessing_of_the_theurgist",
            "blinding_fear",
            "blinding_luminance",
            "blinding_poison_i",
            "blind_poison_ii",
            "blinding_poison_iii",
            "blinding_step",
            "blizzard",
            "blizzard_blast",
            "blood_claw",
            "bobbing_corpse",
            "boil_blood",
            "boiling_blood",
            "bolt_of_flame",
            "bolt_of_karana",
            "boltrans_agacerie",
            "boltrans_animation",
            "bond_of_death",
            "bonds_of_force",
            "bonds_of_tunare",
            "bone_melt",
            "bone_shatter",
            "bone_walk",
            "boneshear",
            "boon_of_immolation",
            "boon_of_the_clear_mind",
            "boon_of_the_garou",
            "bramblecoat",
            "bravery",
            "breath_of_karana",
            "breath_of_ro",
            "breath_of_the_dead",
            "breath_of_the_sea",
            "breeze",
            "brilliance",
            "bristlebanes_bundle",
            "bittle_haste_i",
            "brittle_haste_ii",
            "brittle_haste_iii",
            "brittle_haste_iv",
            "bruscos_boastful_bellow",
            "bruscos_bombastic_bellow",
            "bulwark_of_faith",
            "burn",
            "burning_vengeance",
            "burningtouch",
            "burnout",
            "burnout_ii",
            "burnout_iii",
            "burnout_iv",
            "burrowing_scarab",
            "burst_of_fire",
            "burst_of_flame",
            "burst_of_flametest",
            "burst_of_strength",
            "cackling_bones",
            "cadeau_of_flame",
            "cajole_undead",
            "calefaction",
            "calimony",
            "call_of_bones",
            "call_of_earth",
            "call_of_flame",
            "call_of_karana",
            "call_of_sky",
            "call_of_sky_strike",
            "call_of_the_hero",
            "call_of_the_predator",
            "call_of_the_zero",
            "calm",
            "calm_animal",
            "camouflage",
            "can_owhoop_ass",
            "cancel_magic",
            "cannibalize",
            "cannibalize_ii",
            "cannibalize_iii",
            "cannibalize_iv",
            "cantata_of_replenishment",
            "cantata_of_soothin",
            "captain_nalots_quickening",
            "careless_lightning",
            "cascade_of_hail",
            "cascading_darkness",
            "cassindras_chant_of_clarity",
            "cassindras_chorus_of_clarity",
            "cassindras_elegy",
            "cassindras_insipid_ditty",
            "cast_force",
            "cast_sight",
            "cavorting_bones",
            "cazic_gate",
            "cazic_portal",
            "cazic_touch",
            "celerity",
            "celestial_cleansing",
            "celestial_elixer",
            "celestial_healing",
            "celestial_tranquility",
            "center",
            "cessation_of_cor",
            "ceticious_cloud",
            "chant_of_battle",
            "chaos_breath",
            "chaos_flux",
            "chaotic_feedback",
            "char",
            "charisma",
            "charm",
            "charm_animals",
            "chase_the_moon",
            "chill_bones",
            "chill_of_unlife",
            "chill_sight",
            "chilling_embrace",
            "chloroblast",
            "chloroplast",
            "choke",
            "chords_of_dissonance",
            "cindas_charismatic_carillon",
            "cinder_bolt",
            "cinder_jolt",
            "circle_of_butcher",
            "circle_of_cobalt_scar",
            "circle_of_commons",
            "circle_of_feerrott",
            "circle_of_force",
            "circle_of_great_divide",
            "circle_of_iceclad",
            "circle_of_karana",
            "circle_of_lavastorm",
            "circle_of_misty",
            "circle_of_ro",
            "circle_of_steamfont",
            "circle_of_summer",
            "circle_of_surefall_glades",
            "circle_of_the_combines",
            "circle_of_toxxulia",
            "circle_of_wakening_lands",
            "circle_of_winter",
            "clarify_mana",
            "clarity",
            "clarity_ii",
            "cleanse",
            "clinging_darkness",
            "clockwork_poison",
            "cloud",
            "cloud_of_disempowerment",
            "cloud_of_fear",
            "cloud_of_silence",
            "cobalt_scar_gate",
            "cobalt_scar_portal",
            "cog_boost",
            "cohesion",
            "coldlight",
            "collaboration",
            "color_flux",
            "color_shift",
            "color_skew",
            "color_slant",
            "column_of_fire",
            "column_of_frost",
            "column_of_lightning",
            "combine_gate",
            "combine_portal",
            "combust",
            "common_gate",
            "common_portal",
            "companion_spirit",
            "complete_heal",
            "complete_healing",
            "composition_of_ervaj",
            "concussion",
            "conflagration",
            "conglaciation_of_bone",
            "conjuration_air",
            "conjuration_earth",
            "conjuration_fire",
            "conjuration_water",
            "conjure_corpse",
            "contact_poision_i",
            "contact_poision_ii",
            "contact_poision_iii",
            "contact_poision_iv",
            "convergence",
            "convoke_shadow",
            "cornucopia",
            "corporeal_empathy",
            "counteract_disease",
            "counteract_poison",
            "courage",
            "covetous_subversion",
            "creeping_crud",
            "creeping_vision",
            "cripple",
            "crissions_pixie_strike",
            "crystallize_mana",
            "cure_blindness",
            "cure_disease",
            "cure_poison",
            "curse_of_the_garou",
            "curse_of_the_simple_mind",
            "curse_of_the_spirits",
            "dagger_of_symbols",
            "damage_shield",
            "dance_of_the_blade",
            "dance_of_the_fireflies",
            "daring",
            "dark_empathy",
            "dark_pact",
            "dawncall",
            "dazzle",
            "dead_man_floating",
            "dead_men_floating",
            "deadeye",
            "deadly_lifetap",
            "deadly_poison",
            "deadly_velium_poison",
            "death_pact",
            "death_peace",
            "deflux",
            "defoliate",
            "defoliation",
            "deftness",
            "deliriously_nimble",
            "dementia",
            "dementing_visions",
            "demi_lich",
            "denons_bereavement",
            "denons_desperate_dirge",
            "denons_disruptive_discord",
            "denons_dissension",
            "desperate_hope",
            "devouring_darkness",
            "dexterity",
            "dexterous_aura",
            "diamondskin",
            "dictate",
            "dimensional_hole",
            "dimensional_pocket",
            "discordant_mind",
            "disease",
            "disease_cloud",
            "diseased_cloud",
            "disempower",
            "disintegrate",
            "dismiss_summoned",
            "dismiss_undead",
            "distill_mana",
            "distraction",
            "divine_aura",
            "divine_barrier",
            "divine_favor",
            "divine_glory",
            "divine_intervention",
            "divine_light",
            "divine_might",
            "divine_might_effect",
            "divine_purpose",
            "divine_strength",
            "divine_wrath",
            "dizzy_i",
            "dizzy_ii",
            "dizzy_iii",
            "dizzy_iv",
            "dizzying_winds",
            "doljons_rage",
            "dominate_undead",
            "dooming_darkness",
            "draconic_rage",
            "dragon_charm",
            "dragon_roar",
            "drain_soul",
            "drain_spirit",
            "draught_of_fire",
            "draught_of_ice",
            "draught_of_jiva",
            "draught_of_night",
            "drifting_death",
            "drones_of_doom",
            "drowsy",
            "drybonefireburst",
            "dulsehound",
            "dyns_dizzying_draught",
            "dyzils_deafening_decoy",
            "earthcall",
            "earthelementalattack",
            "earthquake",
            "ebbing_strength",
            "echinacea_infusion",
            "effect_flamesong",
            "efreeti_fire",
            "egress",
            "electric_blast",
            "elemental_armor",
            "elemental_maelstrom",
            "elemental_rhythms",
            "elemental_shield",
            "elemental_air",
            "elemental_earth",
            "elemental_fire",
            "elemental_water",
            "elementaling_air",
            "elementaling_earth",
            "elementaling_fire",
            "elementaling_water",
            "elementalkin_air",
            "elementalkin_earth",
            "elementalkin_fire",
            "elementalkin_water",
            "embrace_of_the_kelpmaiden",
            "emmisary_of_thule",
            "enchant_adamantite",
            "enchant_brellium",
            "enchant_clay",
            "enchant_electrum",
            "enchant_gold",
            "enchant_mithril",
            "enchant_platinum",
            "enchant_silver",
            "enchant_steel",
            "enchant_velium",
            "endure_cold",
            "endure_disease",
            "endure_fire",
            "endure_fire",
            "endure_magic",
            "endure_poison",
            "enduring_breath",
            "energy_sap",
            "energy_storm",
            "enfeeblement",
            "enforced_reverence",
            "engorging_roots",
            "engulfing_darkness",
            "engulfing_roots",
            "enlightenment",
            "enslave_death",
            "ensnare",
            "ensnaring_roots",
            "enstill",
            "enthrall",
            "enticement_of_flame",
            "entomb_in_ice",
            "entrance",
            "entrapping_roots",
            "enveloping_roots",
            "envenomed_bolt",
            "envenomed_breath",
            "envenomed_heal",
            "essence_drain",
            "essence_tap",
            "evacuate",
            "evacuate_fay",
            "evacuate_nek",
            "evacuate_north",
            "evacuate_ro",
            "evacuate_west",
            "everfount",
            "everlasting_breath",
            "exile_summoned",
            "exile_undead",
            "expedience",
            "expel_summoned",
            "expel_undead",
            "expulse_summoned",
            "expulse_undead",
            "extended_regeneration",
            "extinguish_fatigue",
            "eye_of_confusion",
            "eye_of_tallon",
            "eye_of_zomm",
            "eyes_of_the_cat",
            "fade",
            "fangols_breath",
            "fascination",
            "fatigue_drain",
            "fay_gate",
            "fay_portal",
            "fear",
            "feast_of_blood",
            "feckless_might",
            "feeble_mind_i",
            "feeble_mind_ii",
            "feeble_mind_iii",
            "feeble_mind_iv",
            "feeble_poison",
            "feedback",
            "feet_like_cat",
            "feign_death",
            "fellspine",
            "feral_spirit",
            "fetter",
            "field_of_bone_port",
            "fiery_death",
            "fiery_might",
            "fingers_of_fire",
            "fire",
            "fire_bolt",
            "fire_flux",
            "fire_spiral_of_alkabor",
            "firefist",
            "firestorm",
            "firestrike",
            "fist_of_air",
            "fist_of_fire",
            "fist_of_karana",
            "fist_of_mastery",
            "fist_of_sentience",
            "fist_of_water",
            "fixation_of_ro",
            "flame_arc",
            "flame_bolt",
            "flame_flux",
            "flame_jet",
            "flame_lick",
            "flame_of_light",
            "flame_of_the_efreeti",
            "flame_shock",
            "flame_song_of_ro",
            "flames_of_ro",
            "flaming_sword_of_xuzl",
            "flare",
            "flash_of_light",
            "fleeting_fury",
            "flesh_rot_i",
            "flesh_rot_ii",
            "flesh_rot_iii",
            "flowing_thought_i",
            "flowing_thought_ii",
            "flowing_thought_iii",
            "flowing_thought_iv",
            "flurry",
            "focus_of_spirit",
            "force",
            "force_shock",
            "force_spiral_of_alkabor",
            "force_strike",
            "forlorn_deeds",
            "form_of_the_great_bear",
            "form_of_the_great_wolf",
            "form_of_the_howler",
            "form_of_the_hunter",
            "fortitude",
            "freezing_breath",
            "frenzied_spirit",
            "frenzied_strength",
            "frenzy",
            "froglok_poison",
            "frost",
            "frost_bolt",
            "frost_breath",
            "frost_port",
            "frost_rift",
            "frost_shards",
            "frost_shock",
            "frost_spiral_of_alkabor",
            "frost_storm",
            "frost_strike",
            "frostbite",
            "frostreavers_blessing",
            "frosty_death",
            "fufils_curtailing_chant",
            "fungal_regrowth",
            "fungus_spores",
            "furious_strength",
            "furor",
            "fury",
            "fury_of_air",
            "gale_of_poison",
            "gangrenous_touch_of_zumuul",
            "garzicors_vengeance",
            "gasping_embrace",
            "gate",
            "gather_shadows",
            "gaze",
            "gelatroot",
            "ghoul_root",
            "gift_of_aerr",
            "gift_of_brilliance",
            "gift_of_insight",
            "gift_of_magic",
            "gift_of_pure_thought",
            "gift_of_xev",
            "girdle_of_karana",
            "glamour",
            "glamour_of_kintaz",
            "glamour_of_tunare",
            "glimpse",
            "grasping_roots",
            "graveyard_dust",
            "gravity_flux",
            "grease_injection",
            "great_divide_gate",
            "great_divide_portal",
            "greater_conjuration_air",
            "greater_conjuration_earth",
            "greater_conjuration_fire",
            "greater_conjuration_water",
            "greater_healing",
            "greater_shielding",
            "greater_summoning_air",
            "greater_summoning_earth",
            "greater_summoning_fire",
            "greater_summoning_water",
            "greater_vocaration_air",
            "greater_vocaration_earth",
            "greater_vocaration_fire",
            "greater_vocaration_water",
            "greater_wolf_form",
            "greenmist",
            "grim_aura",
            "group_resist_magic",
            "guard",
            "guardian",
            "guardian_rhythms",
            "guardian_spirit",
            "halo_of_light",
            "hammer_of_requital",
            "hammer_of_striking",
            "hammer_of_wrath",
            "harmony",
            "harmshield",
            "harpy_voice",
            "harvest",
            "harvest_leaves",
            "haste",
            "haunting_corpse",
            "haze",
            "healing",
            "health",
            "heart_flutter",
            "heat_blood",
            "heat_sight",
            "heroic_bond",
            "heroism",
            "holy_armor",
            "holy_might",
            "holy_shock",
            "hsagras_wrath",
            "hug",
            "hungry_earth",
            "hymn_of_restoration",
            "ice",
            "ice_breath",
            "ice_comet",
            "ice_rend",
            "ice_shock",
            "ice_spear_of_solist",
            "ice_strike",
            "iceclad_gate",
            "iceclad_portal",
            "icestrike",
            "identity",
            "ignite",
            "ignite_blood",
            "ignite_bones",
            "ikatiars_revenge",
            "illusion_air_elemental",
            "illusion_barbarian",
            "illusion_dry_bone",
            "illusion_dwarf",
            "illusion_earth_elemental",
            "illusion_erudite",
            "illusion_fire_elemental",
            "illusion_gnome",
            "illusion_halfelf",
            "illusion_halfling",
            "illusion_high_elf",
            "illusion_human",
            "illusion_iksar",
            "illusion_ogre",
            "illusion_skeleton",
            "illusion_spirit_wolf",
            "illusion_tree",
            "illusion_troll",
            "illusion_water_elemental",
            "illusion_werewolf",
            "illusion_wood_elf",
            "imbue_amber",
            "imbue_black_pearl",
            "imbue_black_sapphire",
            "imbue_diamond",
            "imbue_emerald",
            "imbue_fire_opal",
            "imbue_ivory",
            "imbue_jade",
            "imbue_opal",
            "imbue_peridot",
            "imbue_plains_pebble",
            "imbue_rose_quartz",
            "imbue_ruby",
            "imbue_sapphire",
            "imbue_topaz",
            "immobilize",
            "immolate",
            "immolating_breath",
            "impart_strength",
            "improved_invis_to_undead",
            "improved_invisibility",
            "improved_superior_camouflage",
            "incapacitate",
            "incinerate_bones",
            "infectious_cloud",
            "inferno_of_alkabor",
            "inferno_shield",
            "inferno_shock",
            "infusion",
            "injection_poison_i",
            "injection_poison_ii",
            "injection_poison_iii",
            "injection_poison_iv",
            "injection_poison_v",
            "inner_fire",
            "insidious_decay",
            "insidious_fever",
            "insidious_malady",
            "insight",
            "insipid_weakness",
            "inspire_fear",
            "intensify_death",
            "invert_gravity",
            "invigor",
            "invigorate",
            "invisibility",
            "invisibility_cloak",
            "invisibility_to_undead",
            "invisibility_versus_animal",
            "invisibility_versus_animals",
            "invisibility_versus_undead",
            "invoke_death",
            "invoke_fear",
            "invoke_lightning",
            "invoke_shadow",
            "jaxans_jig_ovigor",
            "jolt",
            "jonthans_inspiration",
            "jonthans_provocation",
            "jonthans_whistling_warsong",
            "journeymansboots",
            "judgement_of_ice",
            "julis_animation",
            "jylls_static_pulse",
            "jylls_wave_of_heat",
            "jylls_zephyr_of_ice",
            "kazumis_note_of_preservation",
            "kelins_lucid_lullaby",
            "kelins_lugubrious_lament",
            "kilans_animation",
            "kilvas_skin_of_flame",
            "kintazs_animation",
            "knights_blessing",
            "knockback",
            "kurrats_magician_epic_guide",
            "kylies_venom",
            "languid_pace",
            "largarns_lamentation",
            "largos_absonant_binding",
            "largos_melodic_binding",
            "lava_bolt",
            "lava_breath",
            "lava_storm",
            "leach",
            "leatherskin",
            "leering_corpse",
            "legacy_of_spike",
            "legacy_of_thorn",
            "lesser_conjuration_air",
            "lesser_conjuration_earth",
            "lesser_conjuration_fire",
            "lesser_conjuration_water",
            "lesser_shielding",
            "lesser_summoning_air",
            "lesser_summoning_earth",
            "lesser_summoning_fire",
            "lesser_summoning_water",
            "levant",
            "levitate",
            "levitation",
            "lich",
            "life_leech",
            "lifedraw",
            "lifespike",
            "lifetap",
            "light_healing",
            "lightning_blast",
            "lightning_bolt",
            "lightning_breath",
            "lightning_shock",
            "lightning_storm",
            "lightning_strike",
            "liquid_silver_i",
            "liquid_silver_ii",
            "liquid_silver_iii",
            "listless_power",
            "locate_corpse",
            "lower_element",
            "lower_resists_i",
            "lower_resists_ii",
            "lower_resists_iii",
            "lower_resists_iv",
            "lull",
            "lull_animal",
            "lure_of_flame",
            "lure_of_frost",
            "lure_of_ice",
            "lure_of_lightning",
            "lyssas_cataloging_libretto",
            "lyssas_locating_lyric",
            "lyssas_solidarity_of_vision",
            "lyssas_veracious_concord",
            "magi_curse",
            "magnify",
            "major_shielding",
            "mala",
            "malaise",
            "malaisement",
            "malevolent_grasp",
            "malo",
            "malosi",
            "malosini",
            "mana_conversion",
            "mana_convert",
            "mana_flare",
            "mana_shroud",
            "mana_sieve",
            "mana_sink",
            "manasink",
            "manaskin",
            "manastorm",
            "maniacal_strength",
            "manifest_elements",
            "manticore_poison",
            "mark_of_karn",
            "markars_clash",
            "markars_discord",
            "markars_relocation",
            "mask_of_the_hunter",
            "mcvaxius_berserker_crescendo",
            "mcvaxius_rousing_rondo",
            "melanies_mellifluous_motion",
            "melodious_beffuddlement",
            "melody_of_ervaj",
            "memory_blur",
            "memory_flux",
            "mend_bones",
            "mesmerization",
            "mesmerize",
            "mesmerizing_breath",
            "mind_cloud",
            "mind_wipe",
            "minion_of_hate",
            "minion_of_shadows",
            "minor_conjuration_air",
            "minor_conjuration_earth",
            "minor_conjuration_fire",
            "minor_conjuration_water",
            "minor_healing",
            "minor_illusion",
            "minor_shielding",
            "minor_summoning_air",
            "minor_summoning_earth",
            "minor_summoning_fire",
            "minor_summoning_water",
            "mircyls_animation",
            "mist",
            "mistwalker",
            "modulating_rod",
            "modulation",
            "monster_summoning_i",
            "monster_summoning_ii",
            "monster_summoning_iii",
            "mortal_deftness",
            "muscle_lock_i",
            "muscle_lock_ii",
            "muscle_lock_iii",
            "muscle_lock_iv",
            "muzzle_of_mardu",
            "mystic_precision",
            "naltrons_mark",
            "nature_walkers_behest",
            "natures_holy_wrath",
            "natures_melody",
            "natures_touch",
            "natures_wrath",
            "natureskin",
            "nek_gate",
            "nek_portal",
            "neutralize_magic",
            "nillipus_march_of_the_wee",
            "nimble",
            "nivs_harmonic",
            "nivs_melody_of_preservation",
            "north_gate",
            "null_aura",
            "nullify_magic",
            "numb_the_dead",
            "numbing_cold",
            "okeils_flickering_flame",
            "okeils_radiation",
            "obscure",
            "obsidian_shatter",
            "occlusion_of_sound",
            "one_hundred_blows",
            "open_black_box",
            "overthere",
            "overwhelming_splendor",
            "pacify",
            "pack_chloroplast",
            "pack_regeneration",
            "pack_spirit",
            "pact_of_shadow",
            "panic",
            "panic_animal",
            "panic_the_dead",
            "paralyzing_earth",
            "paralyzing_poison_i",
            "paralyzing_poison_ii",
            "paralyzing_poison_iii",
            "pendrils_animation",
            "phantom_armor",
            "phantom_chain",
            "phantom_leather",
            "phantom_plate",
            "phobocancel",
            "pillage_enchantment",
            "pillar_of_fire",
            "pillare_of_flame",
            "pillar_of_frost",
            "pillar_of_lightning",
            "plague",
            "plagueratdisease",
            "plainsight",
            "pogonip",
            "poison",
            "poison_animal_i",
            "poison_animal_ii",
            "poison_animal_iii",
            "poison_bolt",
            "poison_breath",
            "poison_storm",
            "poison_summoned_i",
            "poison_summoned_ii",
            "poison_summoned_iii",
            "poisonous_chill",
            "porlos_fury",
            "pouch_of_quellious",
            "power",
            "power_of_the_forests",
            "pox_of_bertoxxulous",
            "primal_avatar",
            "primal_essence",
            "prime_healers_blessing",
            "produce_wrench",
            "project_lightning",
            "protect",
            "protection_of_the_glades",
            "psalm_of_cooling",
            "psalm_of_mystic_shielding",
            "psalm_of_purity",
            "psalm_of_vitality",
            "psalm_of_warmth",
            "purge",
            "purify_mana",
            "purifying_rhythms",
            "putrefy_flesh",
            "putrid_breath",
            "pyrocruor",
            "quickness",
            "quiver_of_marr",
            "quivering_veil_of_xarn",
            "rabies",
            "radiant_visage",
            "rage",
            "rage_of_tallon",
            "rage_of_the_sky",
            "rage_of_vallon",
            "rage_of_zek",
            "rage_of_zomm",
            "rage_of_strength",
            "rage_of_blades",
            "rage_of_fire",
            "rage_of_lava",
            "rage_of_molten_lava",
            "rage_of_spikes",
            "rage_of_swords",
            "rampage",
            "rapacious_subversion",
            "rapture",
            "recant_magic",
            "reckless_health",
            "reckless_strength",
            "reckoning",
            "reclaim_energy",
            "regeneration",
            "regrowth",
            "regrowth_of_the_grove",
            "rejuvenation",
            "remedy",
            "rend",
            "renew_bones",
            "renew_elements",
            "renew_summoning",
            "reoccurring_amnesia",
            "repulse_animal",
            "resist_cold",
            "resist_disease",
            "resist_fire",
            "resist_magic",
            "resist_poison",
            "resistance_to_magic",
            "resistant_skin",
            "resolution",
            "rest_the_dead",
            "restless_bones",
            "restore_sight",
            "resurrection",
            "resurrection_effects",
            "resuscitate",
            "retribution",
            "retribution_of_alkabor",
            "revive",
            "reviviscence",
            "ring_of_butcher",
            "ring_of_cobolt_scar",
            "ring_of_commons",
            "ring_of_faydark",
            "ring_of_feerrott",
            "ring_of_great_divide",
            "ring_of_iceclad",
            "ring_of_karana",
            "ring_of_lavastorm",
            "ring_of_misty",
            "ring_of_ro",
            "ring_of_steamfont",
            "ring_of_surefall_glade",
            "ring_of_the_combines",
            "ring_of_toxxulia",
            "ring_of_wakening_lands",
            "riotous_health",
            "rising_dexterity",
            "ro_gate",
            "ro_portal",
            "ros_fiery_sundering",
            "rodricks_gift",
            "root",
            "rotting_flesh",
            "rubicite_aura",
            "rune_i",
            "rune_ii",
            "rune_iii",
            "rune_iv",
            "rune_v",
            "sacrifice",
            "sagars_animation",
            "sanity_wrap",
            "sathirs_mesmerization",
            "savage_spirit",
            "scale_of_wolf",
            "scale_skin",
            "scarab_storm",
            "scareling_step",
            "scars_of_sigil",
            "scent_of_darkness",
            "scent_of_dusk",
            "scent_of_shadow",
            "scent_of_terris",
            "scintillation",
            "scorching_skin",
            "scoriae",
            "scourge",
            "scream_of_chaos",
            "screaming_mace",
            "screaming_terror",
            "sear",
            "sebilite_pox",
            "sedulous_subversion",
            "see_invisible",
            "seeking_flame_of_seukor",
            "seething_fury",
            "selos_accelerando",
            "selos_assonant_strane",
            "selos_chords_of_cessation",
            "selos_consonant_chain",
            "selos_song_of_travel",
            "sense_animals",
            "sense_summoned",
            "sense_the_dead",
            "sentinel",
            "serpent_sight",
            "servant_of_bones",
            "shade",
            "shadow",
            "shadow_compact",
            "shadow_sight",
            "shadow_step",
            "shadow_vortex",
            "shadowbond",
            "shalees_animation",
            "shallow_breath",
            "shards_of_sorrow",
            "share_wolf_form",
            "shauris_sonorous_clouding",
            "shield_of_barbs",
            "shield_of_blades",
            "shield_of_brambles",
            "shield_of_fire",
            "shield_of_flame",
            "shield_of_lava",
            "shield_of_song",
            "shield_of_spikes",
            "shield_of_eighth",
            "shield_of_the_magi",
            "shield_of_thistles",
            "shield_of_words",
            "shielding",
            "shieldskin",
            "shifting_shield",
            "shifting_sight",
            "shiftless_deeds",
            "shock_of_blades",
            "shock_of_fire",
            "shock_of_flame",
            "shock_of_frost",
            "shock_of_ice",
            "shock_of_lightning",
            "shock_of_poison",
            "shock_of_spikes",
            "shock_of_steel",
            "shock_of_swords",
            "shock_of_the_tainted",
            "shock_spiral_of_alkabor",
            "shrieking_howl",
            "shrink",
            "shroud_of_death",
            "shroud_of_hate",
            "shroud_of_pain",
            "shroud_of_the_spirits",
            "shroud_of_undeath",
            "sicken",
            "sight",
            "sight_graft",
            "silver_breath",
            "silver_skin",
            "siphon",
            "siphon_life",
            "siphon_strength",
            "siphon_strength_recourse",
            "sirocco",
            "sisnas_animation",
            "skin_like_diamond",
            "skin_like_nature",
            "skin_like_rock",
            "skin_like_steel",
            "skin_like_wood",
            "skin_of_the_shadow",
            "skunkspray",
            "slime_mist",
            "smite",
            "smolder",
            "snakeelefireburst",
            "snare",
            "solons_bewitching_bravura",
            "solons_bravura",
            "solons_charismatic_concord",
            "solons_song_of_the_sirens",
            "song_of_dawn",
            "song_of_highsun",
            "song_of_midnight",
            "song_of_the_deep_seas",
            "song_of_twilight",
            "song_composition_of_ervaj",
            "song_melody_of_ervaj",
            "song_occlusion_of_sound",
            "sonic_scream",
            "soothe",
            "soul_bond",
            "soul_consumption",
            "soul_devour",
            "soul_leech",
            "soul_well",
            "sound_of_force",
            "spear_of_warding",
            "specter_lifetap",
            "speed_of_the_shissar",
            "sphere_of_light",
            "spikecoat",
            "spin_the_bottle",
            "spirit_armor",
            "spirit_of_bear",
            "spirit_of_cat",
            "spirit_of_cheetah",
            "spirit_of_monkey",
            "spirit_of_oak",
            "spirit_of_ox",
            "spirit_of_scale",
            "spirit_of_snake",
            "spirit_of_the_howler",
            "spirit_of_wolf",
            "spirit_pouch",
            "spirit_quickening",
            "spirit_sight",
            "spirit_strength",
            "spirit_strike",
            "spirit_tap",
            "splurt",
            "spook_the_dead",
            "stability",
            "staff_of_runes",
            "staff_of_symbols",
            "staff_of_tracing",
            "staff_of_warding",
            "stalking_probe",
            "stalwart_regeneration",
            "stamina",
            "starfire",
            "starshine",
            "static",
            "static_strike",
            "steal_strength",
            "steam_overload",
            "steelskin",
            "stinging_swarm",
            "stone_breath",
            "stone_spider_stun",
            "storm_strength",
            "stream_of_acid",
            "strength",
            "strength_of_earth",
            "strength_of_nature",
            "strength_of_stone",
            "strength_of_the_kunzar",
            "strengthen",
            "strengthen_death",
            "strike",
            "strike_of_the_chosen",
            "strike_of_thunder",
            "strip_enchantment",
            "strong_disease",
            "strong_poison",
            "stun",
            "stun_breath",
            "stun_command",
            "stunning_blow",
            "succor",
            "succor_butcher",
            "succor_east",
            "succor_lavastorm",
            "succor_north",
            "succor_ro",
            "suffocate",
            "suffocating_sphere",
            "summon_arrows",
            "summon_bandages",
            "summon_coldstone",
            "summon_companion",
            "summon_corpse",
            "summon_dagger",
            "summon_dead",
            "summon_drink",
            "summon_fang",
            "summon_food",
            "summon_golin",
            "summon_heatstone",
            "summon_holy_ale_of_brell",
            "summon_lava_diamond",
            "summon_orb",
            "summon_ring_of_flight",
            "summon_shard_of_the_core",
            "summon_throwing_dagger",
            "summon_throwing_hammer",
            "summon_waterstone",
            "summon_wisp",
            "summoning_air",
            "summoning_earth",
            "summoning_fire",
            "summoning_water",
            "sunbeam",
            "sunskin",
            "sunstrike",
            "superior_camouflage",
            "superior_healing",
            "supernova",
            "surge_of_enfeeblement",
            "swamp_port",
            "swarm_of_retribution",
            "swarming_pain",
            "swift_like_the_wind",
            "swift_spirit",
            "sword_of_runes",
            "sword_of_marzin",
            "sword_of_naltron",
            "sword_of_pinzarn",
            "sword_of_ryltan",
            "sword_of_transal",
            "sympathetic_aura",
            "symphonic_harmony",
            "system_shock_i",
            "system_shock_ii",
            "system_shock_iii",
            "system_shock_iv",
            "system_shock_v",
            "syvelians_antimagic_aria",
            "tagars_insects",
            "tainted_breath",
            "talisman_of_altuna",
            "talisman_of_jasinth",
            "talisman_of_kragg",
            "talisman_of_shadoo",
            "talisman_of_the_brute",
            "talisman_of_the_cat",
            "talisman_of_the_raptor",
            "talisman_of_the_rhino",
            "talisman_of_the_serpent",
            "talisman_of_tnarg",
            "taper_enchantment",
            "tarews_aquatic_ayre",
            "tashan",
            "tashani",
            "tashania",
            "tashanian",
            "tears_of_druzzil",
            "tears_of_solusek",
            "telescope",
            "tepid_deeds",
            "terrorize_animal",
            "the_dains_justice",
            "the_unspoken_word",
            "theft_of_thought",
            "thicken_mana",
            "thistlecoat",
            "thorncoat",
            "thorny_shield",
            "thrall_of_bones",
            "thunder_blast",
            "thunder_strike",
            "thunderbold",
            "thunderclap",
            "thurgadin_gate",
            "tigirs_insects",
            "tishans_clash",
            "tishans_relocation",
            "tishans_discord",
            "torgors_insects",
            "torbas_acid_blast",
            "torment",
            "torment_of_argli",
            "torment_of_shadows",
            "torpor",
            "torrent_of_poison",
            "touch_of_night",
            "tox_gate",
            "tox_portal",
            "track_corpse",
            "trakanon_tail",
            "trakanons_touch",
            "translocate",
            "translocate_cazic",
            "translocate_cobolt_scar",
            "translocate_combine",
            "translocate_common",
            "translocate_fay",
            "translocate_great_divide",
            "translocate_group",
            "translocate_iceclad",
            "translocate_nek",
            "translocate_north",
            "translocate_ro",
            "translocate_tox",
            "translocate_wakening_lands",
            "translocate_west",
            "travelerboots",
            "treeform",
            "tremor",
            "trepidation",
            "trucudation",
            "true_north",
            "tsunami",
            "tumultuous_strength",
            "tunares_request",
            "turgurs_insects",
            "turning_of_the_unnatural",
            "tuyens_chant_of_flame",
            "tuyens_chant_of_frost",
            "uleens_animation",
            "ultravision",
            "umbra",
            "unfailing_reverence",
            "unswerving_hammer",
            "upheaval",
            "valiant_companion",
            "valor",
            "vampire_charm",
            "vampire_curse",
            "vampire_embrace",
            "valium_shards",
            "velocity",
            "vengeance_of_alkabor",
            "vengeance_of_the_glades",
            "venom_of_the_snake",
            "verlekarnorms_disaster",
            "versus_of_victory",
            "vexing_mordinia",
            "vigilant_spirit",
            "vigor",
            "villas_chorus_of_celerity",
            "villas_versus_of_celerity",
            "vision",
            "visions_of_grandeur",
            "vocarate_air",
            "vocarate_earth",
            "vocarate_fire",
            "vocarate_water",
            "voice_graft",
            "voice_of_the_berserker",
            "voltaic_draught",
            "wake_of_karana",
            "wake_of_tranquility",
            "wakening_lands_gate",
            "wakening_lands_portal",
            "walking_sleep",
            "wandering_mind",
            "ward_summoned",
            "ward_undead",
            "wave_of_cold",
            "wave_of_enfeeblement",
            "wave_of_fear",
            "wave_of_fire",
            "wave_of_flame",
            "wave_of_healing",
            "wave_of_heat",
            "waves_of_the_deep_sea",
            "weak_poison",
            "weaken",
            "weakning_poison_i",
            "weakning_poison_ii",
            "weakning_poison_iii",
            "weakning_poison_iv",
            "weakness",
            "west_gate",
            "west_portal",
            "whirl_till_you_hurl",
            "whirlwind",
            "wildfire",
            "wind_of_the_north",
            "wind_of_the_south",
            "wind_of_tishani",
            "wind_of_tishanian",
            "winds_of_gelid",
            "winged_death",
            "winters_roar",
            "wolf_form",
            "wonderous_rapidity",
            "word_divine",
            "word_of_healing",
            "word_of_health",
            "word_of_pain",
            "word_of_redemption",
            "word_of_restoration",
            "word_of_shadow",
            "word_of_souls",
            "word_of_spirit",
            "word_of_vigor",
            "wrath",
            "wrath_of_alkabor",
            "wrath_of_nature",
            "wrath_of_elements",
            "yaulp",
            "yaulp_ii",
            "yaulp_iii",
            "yaulp_iv",
            "yegoreffs_animation",
            "ykesha",
            "yonder",
            "zumaiks_animation",
        ]

        version = str(pkg_resources.get_distribution("eqalert").version)
        spell_timers_file_name = "spell-timers.json"
        spell_timer_file = data_path + spell_timers_file_name

        # Read spells_us.txt
        eq_spells_file = open(eq_spells_file_path, "r")
        eq_spells_file_lines = eq_spells_file.readlines()
        eq_spells_file.close()

        # Check spell-timers.json version
        if os.path.isfile(spell_timer_file):
            json_data = open(spell_timer_file, "r", encoding="utf-8")
            spell_timers_version_check = json.load(json_data)
            if not spell_timers_version_check["version"] == version:
                print(
                    "Generating new spell-timers.json. This may take up to 45 seconds . . ."
                )
                # Bootstrap new spell-timers.json
                spell_timer_json = {"spells": {}, "version": version}

                # Read spells_us.txt line
                for line in eq_spells_file_lines:
                    modified_line = line.split("^")

                    ## Relevant values
                    spell_name = modified_line[1]
                    spell_buff_duration = str(int(modified_line[17]) * 6)
                    spell_aeduration = str(int(modified_line[18]) * 6)

                    ## Clean spell name
                    line_type_spell_name = re.sub(
                        r"[^a-z\s]", "", spell_name.lower()
                    ).replace(" ", "_")

                    if int(spell_buff_duration) > 0 and int(spell_aeduration) > 0:
                        spell_timer = str(spell_buff_duration)
                    elif int(spell_buff_duration) > 0 and int(spell_aeduration) == 0:
                        spell_timer = str(spell_buff_duration)
                    elif int(spell_buff_duration) == 0 and int(spell_aeduration) > 0:
                        spell_timer = str(spell_aeduration)
                    elif int(spell_buff_duration) == 0 and int(spell_aeduration) == 0:
                        spell_timer = "0"

                    if line_type_spell_name in valid_spells:
                        prefixed_line_type_spell_name = "spell_" + line_type_spell_name
                        spell_timer_json["spells"].update(
                            {prefixed_line_type_spell_name: spell_timer}
                        )

                    json_data = open(spell_timer_file, "w")
                    json.dump(spell_timer_json, json_data, sort_keys=True, indent=2)
                    json_data.close()
        else:
            print(
                "Generating new spell-timers.json. This may take up to 45 seconds . . ."
            )
            # Bootstrap new spell-timers.json
            spell_timer_json = {"spells": {}, "version": version}

            # Read spells_us.txt line
            for line in eq_spells_file_lines:
                modified_line = line.split("^")

                ## Relevant values
                spell_name = modified_line[1]
                spell_buff_duration = str(int(modified_line[17]) * 6)
                spell_aeduration = str(int(modified_line[18]) * 6)

                ## Clean spell name
                line_type_spell_name = re.sub(
                    r"[^a-z\s]", "", spell_name.lower()
                ).replace(" ", "_")

                if int(spell_buff_duration) > 0 and int(spell_aeduration) > 0:
                    spell_timer = str(spell_buff_duration)
                elif int(spell_buff_duration) > 0 and int(spell_aeduration) == 0:
                    spell_timer = str(spell_buff_duration)
                elif int(spell_buff_duration) == 0 and int(spell_aeduration) > 0:
                    spell_timer = str(spell_aeduration)
                elif int(spell_buff_duration) == 0 and int(spell_aeduration) == 0:
                    spell_timer = "0"

                if line_type_spell_name in valid_spells:
                    prefixed_line_type_spell_name = "spell_" + line_type_spell_name
                    spell_timer_json["spells"].update(
                        {prefixed_line_type_spell_name: spell_timer}
                    )

                json_data = open(spell_timer_file, "w")
                json.dump(spell_timer_json, json_data, sort_keys=True, indent=2)
                json_data.close()

    except Exception as e:
        eqa_settings.log(
            "update spell timers: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def set_last_state(state, configs):
    """Save state to config"""

    try:
        configs.settings.config["last_state"].update(
            {
                "server": str(state.server),
                "character": str(state.char),
                "afk": str(state.afk),
                "group": str(state.group),
                "leader": str(state.leader),
                "raid": str(state.raid),
            }
        )
        configs.settings.config["settings"]["encounter_parsing"].update(
            {"auto_save": str(state.save_parse), "enabled": str(state.encounter_parse)}
        )
        configs.settings.config["settings"]["raid_mode"].update(
            {
                "auto_set": str(state.auto_raid),
            }
        )
        configs.settings.config["settings"]["timers"].update(
            {
                "auto_mob_timer": str(state.auto_mob_timer),
            }
        )
        configs.settings.config["settings"]["debug_mode"].update(
            {"enabled": str(state.debug)}
        )
        configs.settings.config["settings"]["mute"].update({"enabled": str(state.mute)})
        configs.characters.config["char_logs"][state.char + "_" + state.server].update(
            {
                "char": str(state.char),
                "disabled": "false",
                "file_name": "eqlog_"
                + str(state.char)
                + "_"
                + str(state.server)
                + ".txt",
                "server": str(state.server),
                "char_state": {
                    "direction": str(state.direction),
                    "location": {
                        "x": str(state.loc[1]),
                        "y": str(state.loc[0]),
                        "z": str(state.loc[2]),
                    },
                    "zone": str(state.zone),
                    "encumbered": str(state.encumbered),
                    "bind": str(state.bind),
                    "level": str(state.char_level),
                    "class": str(state.char_class),
                    "guild": str(state.char_guild),
                },
            }
        )
        json_data = open(configs.settings.path, "w", encoding="utf-8")
        json.dump(
            configs.settings.config,
            json_data,
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
        json_data.close()
        json_data = open(configs.characters.path, "w", encoding="utf-8")
        json.dump(
            configs.characters.config,
            json_data,
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "set last state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_last_state(configs, char_name, char_server):
    """Load state from config"""

    try:
        # Populate State
        server = configs.settings.config["last_state"]["server"]
        char = configs.settings.config["last_state"]["character"]
        zone = configs.characters.config["char_logs"][char_name + "_" + char_server][
            "char_state"
        ]["zone"]
        location = [
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["y"]
            ),
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["x"]
            ),
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["z"]
            ),
        ]
        direction = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["direction"]
        encumbered = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["encumbered"]
        bind = configs.characters.config["char_logs"][char_name + "_" + char_server][
            "char_state"
        ]["bind"]
        char_level = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["level"]
        char_class = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["class"]
        char_guild = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["guild"]
        afk = configs.settings.config["last_state"]["afk"]
        group = configs.settings.config["last_state"]["group"]
        leader = configs.settings.config["last_state"]["leader"]
        raid = configs.settings.config["last_state"]["raid"]

        encounter_parse = configs.settings.config["settings"]["encounter_parsing"][
            "enabled"
        ]
        debug = configs.settings.config["settings"]["debug_mode"]["enabled"]
        mute = configs.settings.config["settings"]["mute"]["enabled"]
        save_parse = configs.settings.config["settings"]["encounter_parsing"][
            "auto_save"
        ]
        auto_raid = configs.settings.config["settings"]["raid_mode"]["auto_set"]
        auto_mob_timer = configs.settings.config["settings"]["timers"]["auto_mob_timer"]
        mute = configs.settings.config["settings"]["mute"]["enabled"]

        # Get chars
        chars = get_config_chars(configs)

        # Populate and return a new state
        state = eqa_state.EQA_State(
            char,
            chars,
            zone,
            location,
            direction,
            afk,
            server,
            raid,
            debug,
            mute,
            group,
            leader,
            encumbered,
            bind,
            char_level,
            char_class,
            char_guild,
            encounter_parse,
            save_parse,
            auto_raid,
            auto_mob_timer,
        )

        return state

    except Exception as e:
        eqa_settings.log(
            "get last state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_type(line_type, base_path):
    """Adds default setting values for new line_type"""

    try:
        json_data = open(
            base_path + "config/line-alerts/other.json", "w", encoding="utf-8"
        )
        data = json.load(json_data)
        data["line"].update(
            {line_type: {"sound": "false", "reaction": "false", "alert": {}}}
        )
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "add type: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_zone(zone, base_path):
    """Adds default setting values for new zones"""

    try:
        json_data = open(base_path + "config/zones.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["zones"].update({str(zone): {"raid_mode": "false", "timer": "0"}})
        json_data = open(base_path + "config/zones.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "add zone: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def build_config(base_path):
    """Build a default config"""

    new_char_config = """
{
  "char_logs": {}
}
"""

    new_settings_config = """
{
  "last_state": {},
  "settings": {
    "debug_mode": {
      "enabled": "false"
    },
    "encounter_parsing": {
      "auto_save": "false",
      "enabled": "true"
    },
    "mute": {
      "enabled": "false"
    },
    "paths": {
      "eqalert_log": "%slog/",
      "data": "%sdata/",
      "encounter": "%sencounters/",
      "everquest_logs": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "everquest_files": "%s/.wine/drive_c/Program Files/Sony/EverQuest/",
      "sound": "%ssound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
    "raid_mode": {
      "auto_set": "true"
    },
    "timers": {
      "auto_mob_timer": "false"
    }
  },
  "version": "%s"
}
"""

    new_zones_config = """
{
  "zones": {
    "An Arena (PVP) Area": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Befallen": {
      "raid_mode": "false",
      "timer": "1140"
    },
    "Blackburrow": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Butcherblock Mountains": {
      "raid_mode": "false",
      "timer": "600"
    },
    "Castle Mistmoore": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Chardok": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "City of Thurgadin": {
      "raid_mode": "false",
      "timer": "420"
    },
    "Cobalt Scar": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "Crushbone": {
      "raid_mode": "false",
      "timer": "540"
    },
    "Crystal Caverns": {
      "raid_mode": "false",
      "timer": "885"
    },
    "Dagnor's Cauldron": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Dalnir": {
      "raid_mode": "false",
      "timer": "720"
    },
    "Dragon Necropolis": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Dreadlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "East Commonlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "East Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Eastern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Eastern Wastelands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Erudin": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Erudin Palace": {
      "raid_mode": "false",
      "timer": "1500"
    },
    "Estate of Unrest": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Everfrost": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Field of Bone": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Firiona Vie": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Frontier Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Gorge of King Xorbb": {
      "raid_mode": "false",
      "timer": "360"
    },
    "Great Divide": {
      "raid_mode": "false",
      "timer": "640"
    },
    "Greater Faydark": {
      "raid_mode": "false",
      "timer": "425"
    },
    "Guk": {
      "raid_mode": "false",
      "timer": "990"
    },
    "High Keep": {
      "raid_mode": "false",
      "timer": "600"
    },
    "Highpass Hold": {
      "raid_mode": "false",
      "timer": "300"
    },
    "Howling Stones": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Iceclad Ocean": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Icewell Keep": {
      "raid_mode": "true",
      "timer": "1260"
    },
    "Infected Paw": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Innothule Swamp": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Kael Drakkel": {
      "raid_mode": "true",
      "timer": "1680"
    },
    "Kaesora": {
      "raid_mode": "false",
      "timer": "1080"
    },
    "Karnor's Castle": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Kedge Keep": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Kithicor Woods": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Kurn's Tower": {
      "raid_mode": "false",
      "timer": "1100"
    },
    "Lake Rathetear": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lake of Ill Omen": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lavastorm Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lesser Faydark": {
      "raid_mode": "false",
      "timer": "390"
    },
    "Lost Temple of Cazic-Thule": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Mines of Nurga": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Misty Thicket": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Nagafen's Lair": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Najena": {
      "raid_mode": "false",
      "timer": "1110"
    },
    "North Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Northern Desert of Ro": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Northern Felwithe": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Northern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Oasis of Marr": {
      "raid_mode": "false",
      "timer": "990"
    },
    "Ocean of Tears": {
      "raid_mode": "false",
      "timer": "360"
    },
    "Old Sebilis": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Paineel": {
      "raid_mode": "false",
      "timer": "630"
    },
    "Permafrost Caverns": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Plane of Air": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Fear": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Growth": {
      "raid_mode": "true",
      "timer": "43200"
    },
    "Plane of Hate": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Mischief": {
      "raid_mode": "false",
      "timer": "4210"
    },
    "Qeynos Hills": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Rathe Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Rivervale": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Ruins of Old Guk": {
      "raid_mode": "false",
      "timer": "1680"
    },
    "Sirens Grotto": {
      "raid_mode": "false",
      "timer": "1680"
    },
    "Skyfire Mountains": {
      "raid_mode": "false",
      "timer": "780"
    },
    "Skyshrine": {
      "raid_mode": "true",
      "timer": "1800"
    },
    "Sleepers Tomb": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "South Kaladim": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Southern Desert of Ro": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Southern Felwithe": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Southern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Steamfont Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Surefall Glade": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Temple of Droga": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Temple of Solusek Ro": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Temple of Veeshan": {
      "raid_mode": "true",
      "timer": "4398"
    },
    "The Arena": {
      "raid_mode": "false",
      "timer": "0"
    },
    "The Burning Wood": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The City of Mist": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "The Emerald Jungle": {
      "raid_mode": "false",
      "timer": "0"
    },
    "The Feerrott": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Hole": {
      "raid_mode": "false",
      "timer": "1290"
    },
    "The Nektulos Forest": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Overthere": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Wakening Lands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Tower of Frozen Shadow": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "Timorous Deep": {
      "raid_mode": "false",
      "timer": "720"
    },
    "Toxxulia Forest": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Trakanon's Teeth": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Veeshan's Peak": {
      "raid_mode": "true",
      "timer": "0"
    },
    "Velketor's Labyrinth": {
      "raid_mode": "false",
      "timer": "1972"
    },
    "Warrens": {
      "raid_mode": "false",
      "timer": "400"
    },
    "West Commonlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "West Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Western Plains of Karana": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Western Wastes": {
      "raid_mode": "true",
      "timer": "0"
    }
  },
  "version": "%s"
}
"""

    new_line_combat_config = """
{
  "line": {
    "combat_other_melee": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_block": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crip_blow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crit": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crit_kick": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_dodge": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_invulnerable": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_parry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_reposte": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_rune_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_receive_melee": {
      "alert": {},
      "reaction": "afk",
      "sound": "danger will robinson"
    },
    "experience_group": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "experience_lost": {
      "alert": {},
      "reaction": "all",
      "sound": "oh no!"
    },
    "experience_solo": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "experience_solo_resurrection": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "mob_enrage_off": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "mob_enrage_on": {
      "alert": {},
      "reaction": "group",
      "sound": "enrage"
    },
    "mob_out_of_range": {
      "alert": {},
      "reaction": "group",
      "sound": "range"
    },
    "mob_rampage_on": {
      "alert": {},
      "reaction": "group",
      "sound": "rampage"
    },
    "mob_slain_other": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "true"
    },
    "mob_slain_you": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_spell_general_config = """
{
  "line": {
    "songs_interrupted_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_item_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_oom": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cooldown_active": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_fizzle_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_fizzle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_forget": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_interrupt_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_interrupt_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_begin": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_not_hold": {
      "alert": {},
      "reaction": "raid",
      "sound": "did not hold"
    },
    "spells_protected": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_recover_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_recover_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_resist_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist"
    },
    "spells_sitting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_worn_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_spell_specific_config = """
{
  "line": {
    "spell_bind_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cured_other": {
      "alert": {},
      "reaction": "all",
      "sound": "cured"
    },
    "spell_gate_collapse": {
      "alert": {},
      "reaction": "all",
      "sound": "gate collapse"
    },
    "spell_heal_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invis_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis is dropping"
    },
    "spell_invis_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invis_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "levitate is dropping"
    },
    "spell_levitate_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_regen_on_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_regen_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_slow_on": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "slowed"
    },
    "spell_sow_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sow_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summoned_you": {
      "alert": {},
      "reaction": "group",
      "sound": "you have been summoned"
    }
  },
  "version": "%s"
}
"""

    new_line_pets_config = """
{
  "line": {
    "pet_attack": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_back": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_dead": {
      "alert": {},
      "reaction": "solo",
      "sound": "pet dead"
    },
    "pet_follow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_guard": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_illegal_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_sit_stand": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_spawn": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_taunt_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_recieved_npc_config = """
{
  "line": {
    "say_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_recieved_config = """
{
  "line": {
    "auction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "auction_wtb": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "auction_wts": {
      "alert": {
        "shiny brass idol": "true"
      },
      "reaction": "alert",
      "sound": "look at auction"
    },
    "group": {
      "alert": {
        "drop": "raid",
        "help": "raid",
        "inc": "true",
        "invis": "raid",
        "invite": "raid",
        "oom": "true"
      },
      "reaction": "alert",
      "sound": "look at group"
    },
    "guild": {
      "alert": {
        "assist": "raid",
        "crippled": "raid",
        "dispelled": "raid",
        "feared": "raid",
        "fixated": "raid",
        "fixation": "raid",
        "harmony": "raid",
        "help": "true",
        "incoming": "raid",
        "logs": "raid",
        "malo": "raid",
        "malosini": "raid",
        "occlusion": "raid",
        "off-tanking": "raid",
        "pop": "raid",
        "rampage": "raid",
        "rune": "raid",
        "sieve": "raid",
        "slow": "raid",
        "snare": "raid",
        "stand": "raid",
        "sunder": "raid",
        "tash": "raid"
      },
      "reaction": "alert",
      "sound": "look at guild"
    },
    "ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "say": {
      "alert": {
        "help": "true",
        "spot": "raid"
      },
      "reaction": "alert",
      "sound": "look at say"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_sent_config = """
{
  "line": {
    "auction_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ooc_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "say_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_command_output_config = """
{
  "line": {
    "command_block": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_block_casting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_invalid": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "direction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "direction_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "drink_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "location": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_game": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_guild": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "player_linkdead": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "random": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "server_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "skill_up": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "summon_corpse": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "time_earth": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "time_game": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_afk_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_afk_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_camping": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_camping_abandoned": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lfg_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lfg_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_system_messages_config = """
{
  "line": {
    "autofollow_advice": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_error": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "consider_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ding_down": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "ding_up": {
      "alert": {},
      "reaction": "all",
      "sound": "congratulations"
    },
    "earthquake": {
      "alert": {},
      "reaction": "solo",
      "sound": "earthquake!"
    },
    "encumbered_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "encumbered_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "engage": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "faction_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_welcome": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_offline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking_player_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking_player_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "weather_start_rain": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "weather_start_snow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "wrong_key": {
      "alert": {},
      "reaction": "all",
      "sound": "wrong key or place"
    },
    "you_auto_attack_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_auto_attack_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_cannot_reach": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_char_bound": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_hungry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_new_zone": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "you_outdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outdrinklowfood": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfood": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfooddrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfoodlowdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_stun_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_stun_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_thirsty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "zone_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "zoning": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_group_system_messages_config = """
{
  "line": {
    "group_created": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_disbanded": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_instruction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "group_join_notify": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_joined": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_joined_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_leader_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_leader_you": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "group_leave_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_removed": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_loot_trade_config = """
{
  "line": {
    "looted_item_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_item_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_money_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_money_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_item": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_money": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_npc_payment": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_emotes_config = """
{
  "line": {
    "emote_agree_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_amaze_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_apologize_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bird_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bite_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bleed_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_blink_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_blush_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_boggle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bonk_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bonk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bored_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bounce_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bow_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bow_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_brb_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_burp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bye_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cackle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_calm_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cheer_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cheer_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_chuckle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_clap_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_comfort_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_congratulate_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cough_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cringe_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cry_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_curious_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_dance_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_dance_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_drool_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_duck_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_eye_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_fidget_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_flex_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_frown_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_gasp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_giggle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_glare_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_grin_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_groan_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_grovel_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_happy_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_hug_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_hungry_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_introduce_you": {
      "alert": {},
      "reaction": "all",
      "sound": "why, hello there"
    },
    "emote_jk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kiss_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kneel_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_laugh_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_lost_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_massage_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_moan_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_mourn_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_nod_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_nudge_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_panic_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_pat_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_peer_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_plead_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_point_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_poke_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_ponder_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_purr_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_puzzle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_raise_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_ready_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_roar_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_rofl_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_salute_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shiver_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shrug_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_sigh_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smack_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smile_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smile_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smirk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_snarl_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_snicker_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_stare_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_tap_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_tease_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thank_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thank_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thirsty_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_veto_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_wave_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_wave_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_whine_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_whistle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_yawn_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_who_config = """
{
  "line": {
    "who_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_line_friends": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_player": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top_friends": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top_lfg": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total_empty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total_local_empty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_other_config = """
{
  "line": {
    "all": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "undetermined": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    try:
        home = os.path.expanduser("~")
        version = str(pkg_resources.get_distribution("eqalert").version)
        generated = False

        # Check for old config.yml
        legacy_config_json_path = base_path + "config.json"
        if os.path.isfile(legacy_config_json_path):
            json_data = open(legacy_config_json_path, "r", encoding="utf-8")
            legacy_config_json = json.load(json_data)
            json_data.close()
            old_version = str(legacy_config_json["settings"]["version"]).replace(
                ".", "-"
            )
            if not os.path.exists(base_path + "config/archive/"):
                os.makedirs(base_path + "config/archive/")
            if not os.path.exists(base_path + "config/archive/" + old_version + "/"):
                os.makedirs(base_path + "config/archive/" + old_version + "/")
            archive_config = (
                base_path + "config/archive/" + old_version + "/config.json"
            )
            os.rename(legacy_config_json_path, archive_config)

        # Generate Default Files if Needed
        ## Characters File
        characters_json_path = base_path + "config/characters.json"
        if not os.path.isfile(characters_json_path):
            f = open(characters_json_path, "w", encoding="utf-8")
            f.write(new_char_config)
            f.close()
            generated = True

        ## Settings
        settings_json_path = base_path + "config/settings.json"
        if not os.path.isfile(settings_json_path):
            f = open(settings_json_path, "w", encoding="utf-8")
            f.write(
                new_settings_config
                % (base_path, base_path, base_path, home, home, base_path, version)
            )
            f.close()
            generated = True
        elif os.path.isfile(settings_json_path):
            json_data = open(settings_json_path, "r", encoding="utf-8")
            settings_json = json.load(json_data)
            json_data.close()
            # Archive old settings.json and re-generate one
            if not settings_json["version"] == version:
                old_version = str(settings_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                archive_config = (
                    base_path + "config/archive/" + old_version + "/settings.json"
                )
                os.rename(settings_json_path, archive_config)
                f = open(settings_json_path, "w", encoding="utf-8")
                f.write(
                    new_settings_config
                    % (base_path, base_path, base_path, home, home, base_path, version)
                )
                f.close()
                generated = True

        ## Zones
        zones_json_path = base_path + "config/zones.json"
        if not os.path.isfile(zones_json_path):
            f = open(zones_json_path, "w", encoding="utf-8")
            f.write(new_zones_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(zones_json_path):
            json_data = open(zones_json_path, "r", encoding="utf-8")
            zones_json = json.load(json_data)
            json_data.close()
            # Archive old zones.json and re-generate one
            if not zones_json["version"] == version:
                old_version = str(zones_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                archive_config = (
                    base_path + "config/archive/" + old_version + "/zones.json"
                )
                os.rename(zones_json_path, archive_config)
                f = open(zones_json_path, "w", encoding="utf-8")
                f.write(new_zones_config % (version))
                f.close()
                generated = True

        ## Line Alerts
        ### Combat
        line_combat_json_path = base_path + "config/line-alerts/combat.json"
        if not os.path.isfile(line_combat_json_path):
            f = open(line_combat_json_path, "w", encoding="utf-8")
            f.write(new_line_combat_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_combat_json_path):
            json_data = open(line_combat_json_path, "r", encoding="utf-8")
            line_combat_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/combat.json and re-generate one
            if not line_combat_json["version"] == version:
                old_version = str(line_combat_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/combat.json"
                )
                os.rename(line_combat_json_path, archive_config)
                f = open(line_combat_json_path, "w", encoding="utf-8")
                f.write(new_line_combat_config % (version))
                f.close()
                generated = True

        ### Spell General
        line_spell_general_json_path = (
            base_path + "config/line-alerts/spell-general.json"
        )
        if not os.path.isfile(line_spell_general_json_path):
            f = open(
                line_spell_general_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_spell_general_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_spell_general_json_path):
            json_data = open(line_spell_general_json_path, "r", encoding="utf-8")
            line_spell_general_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/spell-general.json and re-generate one
            if not line_spell_general_json["version"] == version:
                old_version = str(line_spell_general_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/spell-general.json"
                )
                os.rename(line_spell_general_json_path, archive_config)
                f = open(
                    line_spell_general_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_spell_general_config % (version))
                f.close()
                generated = True

        ### Spell Specific
        line_spell_specific_json_path = (
            base_path + "config/line-alerts/spell-specific.json"
        )
        if not os.path.isfile(line_spell_specific_json_path):
            f = open(
                line_spell_specific_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_spell_specific_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_spell_specific_json_path):
            json_data = open(line_spell_specific_json_path, "r", encoding="utf-8")
            line_spell_specific_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/spell-specific.json and re-generate one
            if not line_spell_specific_json["version"] == version:
                old_version = str(line_spell_specific_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/spell-specific.json"
                )
                os.rename(line_spell_specific_json_path, archive_config)
                f = open(
                    line_spell_specific_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_spell_specific_config % (version))
                f.close()
                generated = True

        ### Pets
        line_pets_json_path = base_path + "config/line-alerts/pets.json"
        if not os.path.isfile(line_pets_json_path):
            f = open(line_pets_json_path, "w", encoding="utf-8")
            f.write(new_line_pets_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_pets_json_path):
            json_data = open(line_pets_json_path, "r", encoding="utf-8")
            line_pets_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/pets.json and re-generate one
            if not line_pets_json["version"] == version:
                old_version = str(line_pets_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/pets.json"
                )
                os.rename(line_pets_json_path, archive_config)
                f = open(line_pets_json_path, "w", encoding="utf-8")
                f.write(new_line_pets_config % (version))
                f.close()
                generated = True

        ### Chat Recieved NPC
        line_chat_recieved_npc_json_path = (
            base_path + "config/line-alerts/chat-recieved-npc.json"
        )
        if not os.path.isfile(line_chat_recieved_npc_json_path):
            f = open(
                line_chat_recieved_npc_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_chat_recieved_npc_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_recieved_npc_json_path):
            json_data = open(line_chat_recieved_npc_json_path, "r", encoding="utf-8")
            line_chat_recieved_npc_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-recieved-npc.json and re-generate one
            if not line_chat_recieved_npc_json["version"] == version:
                old_version = str(line_chat_recieved_npc_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-recieved-npc.json"
                )
                os.rename(line_chat_recieved_npc_json_path, archive_config)
                f = open(
                    line_chat_recieved_npc_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_recieved_npc_config % (version))
                f.close()
                generated = True

        ### Chat Recieved
        line_chat_recieved_json_path = (
            base_path + "config/line-alerts/chat-recieved.json"
        )
        if not os.path.isfile(line_chat_recieved_json_path):
            f = open(
                line_chat_recieved_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_chat_recieved_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_recieved_json_path):
            json_data = open(line_chat_recieved_json_path, "r", encoding="utf-8")
            line_chat_recieved_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-recieved.json and re-generate one
            if not line_chat_recieved_json["version"] == version:
                old_version = str(line_chat_recieved_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-recieved.json"
                )
                os.rename(line_chat_recieved_json_path, archive_config)
                f = open(
                    line_chat_recieved_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_recieved_config % (version))
                f.close()
                generated = True

        ### Chat Sent
        line_chat_sent_json_path = base_path + "config/line-alerts/chat-sent.json"
        if not os.path.isfile(line_chat_sent_json_path):
            f = open(line_chat_sent_json_path, "w", encoding="utf-8")
            f.write(new_line_chat_sent_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_sent_json_path):
            json_data = open(line_chat_sent_json_path, "r", encoding="utf-8")
            line_chat_sent_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-sent.json and re-generate one
            if not line_chat_sent_json["version"] == version:
                old_version = str(line_chat_sent_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-sent.json"
                )
                os.rename(line_chat_sent_json_path, archive_config)
                f = open(
                    line_chat_sent_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_sent_config % (version))
                f.close()
                generated = True

        ### Command Output
        line_command_output_json_path = (
            base_path + "config/line-alerts/command-output.json"
        )
        if not os.path.isfile(line_command_output_json_path):
            f = open(
                line_command_output_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_command_output_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_command_output_json_path):
            json_data = open(line_command_output_json_path, "r", encoding="utf-8")
            line_command_output_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/command-output.json and re-generate one
            if not line_command_output_json["version"] == version:
                old_version = str(line_chat_sent_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/command-output.json"
                )
                os.rename(line_command_output_json_path, archive_config)
                f = open(
                    line_command_output_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_command_output_config % (version))
                f.close()
                generated = True

        ### System Messages
        line_system_messages_json_path = (
            base_path + "config/line-alerts/system-messages.json"
        )
        if not os.path.isfile(line_system_messages_json_path):
            f = open(
                line_system_messages_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_system_messages_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_system_messages_json_path):
            json_data = open(line_system_messages_json_path, "r", encoding="utf-8")
            line_system_messages_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/system-messages.json and re-generate one
            if not line_system_messages_json["version"] == version:
                old_version = str(line_system_messages_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/system-messages.json"
                )
                os.rename(line_system_messages_json_path, archive_config)
                f = open(
                    line_system_messages_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_system_messages_config % (version))
                f.close()
                generated = True

        ### Group System Messages
        line_group_system_messages_json_path = (
            base_path + "config/line-alerts/group-system-messages.json"
        )
        if not os.path.isfile(line_group_system_messages_json_path):
            f = open(
                line_group_system_messages_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_group_system_messages_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_group_system_messages_json_path):
            json_data = open(
                line_group_system_messages_json_path, "r", encoding="utf-8"
            )
            line_group_system_messages_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/group-system-messages.json and re-generate one
            if not line_group_system_messages_json["version"] == version:
                old_version = str(line_group_system_messages_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/group-system-messages.json"
                )
                os.rename(line_group_system_messages_json_path, archive_config)
                f = open(
                    line_group_system_messages_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_group_system_messages_config % (version))
                f.close()
                generated = True

        ### Loot Trade Messages
        line_loot_trade_json_path = base_path + "config/line-alerts/loot-trade.json"
        if not os.path.isfile(line_loot_trade_json_path):
            f = open(line_loot_trade_json_path, "w", encoding="utf-8")
            f.write(new_line_loot_trade_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_loot_trade_json_path):
            json_data = open(line_loot_trade_json_path, "r", encoding="utf-8")
            line_loot_trade_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/loot-trade.json and re-generate one
            if not line_loot_trade_json["version"] == version:
                old_version = str(line_loot_trade_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/loot-trade.json"
                )
                os.rename(line_loot_trade_json_path, archive_config)
                f = open(
                    line_loot_trade_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_loot_trade_config % (version))
                f.close()
                generated = True

        ### Emotes
        line_emotes_json_path = base_path + "config/line-alerts/emotes.json"
        if not os.path.isfile(line_emotes_json_path):
            f = open(line_emotes_json_path, "w", encoding="utf-8")
            f.write(new_line_emotes_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_emotes_json_path):
            json_data = open(line_emotes_json_path, "r", encoding="utf-8")
            line_emotes_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/emotes.json and re-generate one
            if not line_emotes_json["version"] == version:
                old_version = str(line_emotes_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/emotes.json"
                )
                os.rename(line_emotes_json_path, archive_config)
                f = open(line_emotes_json_path, "w", encoding="utf-8")
                f.write(new_line_emotes_config % (version))
                f.close()
                generated = True

        ### Who
        line_who_json_path = base_path + "config/line-alerts/who.json"
        if not os.path.isfile(line_who_json_path):
            f = open(line_who_json_path, "w", encoding="utf-8")
            f.write(new_line_who_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_who_json_path):
            json_data = open(line_who_json_path, "r", encoding="utf-8")
            line_who_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/who.json and re-generate one
            if not line_who_json["version"] == version:
                old_version = str(line_who_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/who.json"
                )
                os.rename(line_who_json_path, archive_config)
                f = open(line_who_json_path, "w", encoding="utf-8")
                f.write(new_line_who_config % (version))
                f.close()
                generated = True

        ### Other
        line_other_json_path = base_path + "config/line-alerts/other.json"
        if not os.path.isfile(line_other_json_path):
            f = open(line_other_json_path, "w", encoding="utf-8")
            f.write(new_line_other_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_other_json_path):
            json_data = open(line_other_json_path, "r", encoding="utf-8")
            line_other_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/other.json and re-generate one
            if not line_other_json["version"] == version:
                old_version = str(line_other_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/other.json"
                )
                os.rename(line_other_json_path, archive_config)
                f = open(line_other_json_path, "w", encoding="utf-8")
                f.write(new_line_other_config % (version))
                f.close()
                generated = True

        return generated

    except Exception as e:
        print(
            "build config: Error on line"
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
