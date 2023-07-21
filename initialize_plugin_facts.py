import yaml
import glob
import os
from pathlib import Path


def get_fact_descriptions():
    ability_files = glob.glob("./plugins/**/data/abilities/**/*.yml")
    facts_per_plugin = {}
    for ability_path in ability_files:
        with open(ability_path, "r") as file:
            plugin_name = Path(ability_path).parents[3].name
            if plugin_name not in facts_per_plugin:
                facts_per_plugin[plugin_name] = set()
            r_ability = yaml.safe_load(file)[0]
            commands = []
            if "executors" in r_ability:
                commands.append(r_ability["executors"][0]["command"])
            else:
                for platform in r_ability["platforms"]:
                    try:
                        for thingy in r_ability["platforms"][platform]:
                            commands.append(r_ability["platforms"][platform][thingy]["command"])
                            commands.append(r_ability["platforms"][platform][thingy]["alt_command"])

                    except KeyError:
                        pass
                if not commands:
                    continue
        plugin_facts = get_facts_from_commands(commands, plugin_name)
        facts_per_plugin[plugin_name] = facts_per_plugin[plugin_name] | plugin_facts[plugin_name]
    return facts_per_plugin


def get_facts_from_commands(commands, plugin_name):
    plugin_facts = {plugin_name: set()}
    for command in commands:
        split_command = command.split()
        for cmd in split_command:
            if "#{" in cmd:
                fact_start_idx = cmd.index("#{")
                fact_end_idx = cmd.index("}")
                unprocessed_fact_name = cmd[fact_start_idx + 2: fact_end_idx]
                plugin_facts[plugin_name].add(unprocessed_fact_name)
    return (plugin_facts)


def write_descriptions(facts_per_plugin):
    for plug in facts_per_plugin:
        descriptions = {x: {"default": None, "description": ""} for x in facts_per_plugin[plug]}
        descriptions_path = f"./plugins/{plug}/fact_description.yml"
        to_write = {}
        if os.path.exists(descriptions_path):
            with open(descriptions_path, "r") as f:
                existing_data = yaml.safe_load(f)
                if existing_data:
                    to_write = existing_data
                    for k in descriptions:
                        if k not in existing_data:
                            to_write.update({k: descriptions[k]})
        else:
            to_write = descriptions

        if to_write:
            with open(descriptions_path, "w") as fw:
                yaml.dump(to_write, fw)


if __name__ == "__main__":
    descriptions = get_fact_descriptions()
    write_descriptions(descriptions)
