import sys
import json
import random


def will_action_happen(chance):
    random_float = random.randint(1, 10) * 0.1
    return random_float <= float(chance)


def unlock_chest(chest):
    return random.choices(chest['items'], chest['chances'], k=chest.get("number_of_items_unlocked", 1))


commands_args_map = {
    0: [
        "quit",
        "look",
        "inventory",
        "items",
        "get_all",
        "open_chest",
        "hp",
    ],
    1: [
        "get",
        "drop",
        "go",
        "punch",
        "attack",
        "craft",
        "unlock",
        "ingredients",
        "use",
    ],
}


class MapParsor(object):
    def __init__(self, map_name):
        self.map_name = map_name
        self.map = None

    def parse(self):
        try:
            self.map = json.load(open(self.map_name, 'r'))
        except:
            print("Error: Map file is not valid JSON")

    def is_valid(self):
        return self.map is not None


class Player(object):
    def __init__(self, hasEnemies):
        self.items = []
        self.weapons = ([{
            "name": "punch",
            "type": "weapon",
            "desc": "Deals 1 damage",
            "damage": 1,
            "chance": 0.9
        }] if hasEnemies else [])
        self.recipies = []
        self.spells = []
        self.keys = []
        self.hp = 100
        self.total_capacity = 10 if hasEnemies else float('inf')

    def total_items(self):
        return len(self.items) + len(self.spells) + len(self.weapons)

    def exceeded_max_capacity(self):
        return self.total_items() >= self.total_capacity

    def take_hit(self, hp_lost):
        self.hp -= hp_lost

    def heal(self, hp_gained):
        self.hp = min(100, self.hp + hp_gained)

    def pick_item(self, item):
        self.items.append(item)

    def pick_recipe(self, recipe):
        self.recipies.append(recipe)

    def pick_spell(self, spell):
        self.spells.append(spell)

    def pick_weapon(self, weapon):
        self.weapons.append(weapon)

    def pick_key(self, key):
        self.keys.append(key)

    def get_recipe(self, recipe_name):
        for recipe in self.recipies:
            if recipe['name'] == recipe_name:
                return recipe

    def get_weapon(self, weapon_name):
        for weapon in self.weapons:
            if weapon['name'] == weapon_name:
                return weapon

    def get_key(self, key_name):
        for key in self.keys:
            if key['name'] == key_name:
                return key

    def can_pick_item(self):
        return not self.exceeded_max_capacity()

    def can_pick_complex_item(self, complex_item):
        return not self.exceeded_max_capacity() or complex_item['type'] in ['recipe', 'key']

    def my_complex_items(self):
        return self.weapons + self.recipies + self.spells

    def pick_complex_item(self, complex_item):
        if complex_item and complex_item['type'] in ['item', 'recipe', 'spell', 'weapon', 'key']:
            if complex_item['type'] == 'item':
                self.pick_item(complex_item['name'])
            elif complex_item['type'] == 'recipe':
                self.pick_recipe(complex_item)
            elif complex_item['type'] == 'spell':
                self.pick_spell(complex_item)
            elif complex_item['type'] == 'weapon':
                self.pick_weapon(complex_item)
            else:
                self.pick_key(complex_item)
            return True
        else:
            return False

    def remove_complex_item(self, complex_item):
        if complex_item and complex_item['type'] in ['item', 'recipe', 'spell', 'weapon', 'key']:
            if complex_item['type'] == 'item':
                self.remove_item(complex_item['name'])
            elif complex_item['type'] == 'recipe':
                self.remove_recipe(complex_item)
            elif complex_item['type'] == 'spell':
                self.remove_spell(complex_item)
            elif complex_item['type'] == 'weapon':
                self.remove_weapon(complex_item)
            else:
                self.remove_key(complex_item)
            return True
        else:
            return False

    def delete_spell(self, spell_name):
        for spell in self.spells:
            if spell['name'] == spell_name:
                self.spells.remove(spell)
                return spell
        return None

    def remove_item(self, item):
        self.items.remove(item)

    def remove_recipe(self, recipe):
        self.recipies.remove(recipe)

    def remove_spell(self, spell):
        self.spells.remove(spell)

    def remove_weapon(self, weapon):
        self.weapons.remove(weapon)

    def remove_key(self, key):
        self.keys.remove(key)


class GameEngineError(Exception):
    pass


class LocationMapError(GameEngineError):
    pass


class InvalidCommand(GameEngineError):
    pass


class CommandArgumentError(GameEngineError):
    pass


class MaxCapacityError(GameEngineError):
    pass


class StopGameEngine(GameEngineError):
    pass


class GameEngine(object):
    def __init__(self, location_map):
        self.location_map = location_map
        self.current_location = None
        self.player = Player(
            any(
                [
                    len(location.get('enemies', {})) != 0
                    for location in location_map
                ]
            )
        )
        self.current_spell = None

    def play(self):
        """
        Play the game
        """

        self.validate_map()
        self.current_location = self.location_map[0]
        self.look()
        while True:
            try:
                command = input("What would you like to do? ")
                if command != "quit":
                    self.enemy_attack_at_start_of_turn()
                func_name, args = self.parse_command(command)
                getattr(self, func_name)(*args)
            except EOFError:
                print("Use 'quit' to exit.")
            except StopGameEngine as e:
                print(e)
                break
            except InvalidCommand as e:
                print(e)
                print("Please check readme.txt for a list of valid commands.")
            except (CommandArgumentError, MaxCapacityError) as e:
                print(e)

    def parse_command(self, command):
        """
        Parse the command and return the function name and arguments
        """

        unpacked_command = command.lower().split(" ", 1)
        func_name = unpacked_command[0]
        secondPart = None

        if not any(func_name in commands for commands in commands_args_map.values()):
            raise InvalidCommand("Unknown command: " + func_name)

        if len(unpacked_command) > 1:
            secondPart = unpacked_command[1].strip()

        if func_name in commands_args_map[1]:
            return (func_name, [secondPart])

        return (func_name, [])

    def validate_map(self):
        """
        Validate the map
        """

        try:
            if not isinstance(self.location_map, list):
                raise LocationMapError("Map is not a list.")
            if len(self.location_map) == 0:
                raise LocationMapError("Map is empty.")
        except LocationMapError as e:
            print(e)
            sys.exit(1)

    def look(self):
        """
        Describe the current location
        """

        if not self.current_location:
            return

        print(
            "> " +
            self.current_location["name"] +
            (
                ("(ID: " + str(self.current_location["id"]) + ")")
                if self.current_location.get("id")
                else ""
            )
        )
        print()
        print(self.current_location["desc"])
        print()
        if self.current_location.get("items", []) or self.current_location.get("complex_items", []):
            self.items()
            print()
        print("Exits: " + " ".join(self.current_location["exits"].keys()))
        print()
        if self.current_location.get('chest'):
            print("$" * 50)
            print()
            print(
                f"There is a {self.current_location.get('chest')['name']} in this room."
            )
            print()
            print("$" * 50)
            print()
        if self.current_location.get("enemies"):
            print("*" * 50)
            print()
            print("Current HP: " + str(self.player.hp))
            print()
            if self.current_location.get("enemy_attack_desc"):
                print(self.current_location["enemy_attack_desc"])
                print()
            print(
                "There are the following enemies trying to attack you: " +
                ", ".join(self.current_location_enemy_names())
            )
            print()
            print("*" * 50)
            print()

    def quit(self):
        """
        Quit the game
        """

        raise StopGameEngine("Goodbye!")

    def go(self, direction):
        """
        Go in a particular direction.
        """

        if not direction:
            raise CommandArgumentError("Sorry, you need to 'go' somewhere.")

        direction = direction.lower()

        if direction in self.current_location["exits"]:
            next_location = self.location_map[self.current_location["exits"][direction]]
            if next_location.get("locked"):
                print("The door is locked.")
                return
            self.current_location = next_location
            print(f"You go {direction}.")
            print()
            self.look()
        else:
            print(f"There's no way to go {direction}.")

    def get(self, item_name):
        """
        Get an item
        """

        if not item_name:
            raise CommandArgumentError("Sorry, you need to 'get' something.")

        item_name = item_name.lower()

        if item_name in self.current_location.get('items', []):
            if not self.player.can_pick_item():
                raise MaxCapacityError("You can't carry any more items.")
            self.player.pick_item(item_name)
            self.current_location["items"].remove(item_name)
            print(f"You pick up the {item_name}.")
            return

        complex_item = next(
            (i for i in self.current_location.get(
                'complex_items', []) if i['name'] == item_name),
            None
        )
        if not complex_item:
            print(f"There's no {item_name} anywhere.")
            return

        if not self.player.can_pick_complex_item(complex_item):
            raise MaxCapacityError("You can't carry any more items.")

        if self.player.pick_complex_item(complex_item):
            self.current_location["complex_items"].remove(complex_item)
            print(f"You pick up the {item_name}.")
        else:
            print(f"There's no {item_name} anywhere.")
            return

    def get_all(self):
        """
        Get all items
        """

        exceeded_max_capacity = False
        picked_items = []
        picked_complex_items = []

        for item_name in self.current_location.get('items', []):
            if self.player.exceeded_max_capacity():
                exceeded_max_capacity = True
                break
            self.player.pick_item(item_name)
            picked_items.append(item_name)
            print(f"You pick up the {item_name}.")

        if len(picked_items) > 0:
            for item_name in picked_items:
                self.current_location["items"].remove(item_name)

        for complex_item in self.current_location.get('complex_items', []):
            if not self.player.can_pick_complex_item(complex_item):
                exceeded_max_capacity = True
            elif self.player.pick_complex_item(complex_item):
                picked_complex_items.append(complex_item)
                print(f"You pick up the {complex_item['name']}.")

        if len(picked_complex_items) > 0:
            for complex_item in picked_complex_items:
                self.current_location["complex_items"].remove(complex_item)

        if exceeded_max_capacity:
            raise MaxCapacityError("You can't carry any more items.")

    def drop(self, item_name):
        """
        Drop an item
        """

        if not item_name:
            raise CommandArgumentError("Sorry, you need to 'drop' something.")

        if item_name in self.player.items:
            self.player.remove_item(item_name)
            self.current_location["items"].append(item_name)
            print(f"You drop the {item_name}.")
            return

        complex_item = next(
            (i for i in self.player.my_complex_items()
             if i['name'] == item_name), None
        )

        if not complex_item:
            print(f"You don't have {item_name}.")
            return

        if self.player.remove_complex_item(complex_item):
            self.current_location['complex_items'] = self.current_location.get(
                'complex_items', []
            )
            self.current_location["complex_items"].append(complex_item)
            print(f"You drop the {item_name}.")
        else:
            print("Weird item. Can't drop it.")
            return

    def inventory(self):
        """
        Show the player's inventory
        """

        if len(self.player.items) + len(self.player.recipies) + len(self.player.weapons) + len(self.player.spells) == 0:
            print("You're not carrying anything.")
            return

        print("Inventory:")
        print(
            ("  " + "\n  ".join(self.player.items))
            if self.player.items
            else "NA"
        )
        if len(self.player.recipies) > 0:
            print("Recipes:")
            print("  " + "\n  ".join((i['name']
                  for i in self.player.recipies)))

        if len(self.player.weapons) > 0:
            print("Weapons:")
            print("  " + "\n  ".join((i['name']
                  for i in self.player.weapons)))

        if len(self.player.spells) > 0:
            print("Spells:")
            print("  " + "\n  ".join((i['name']
                  for i in self.player.spells)))

    def hp(self):
        print(f"Current HP: {self.player.hp}")

    def items(self):
        """
        Show the current location items
        """

        print(
            "Items: " + (
                ", ".join(self.current_location.get("items"))
                if len(self.current_location.get("items", [])) > 0
                else "NA"
            )
        )
        if len(self.current_location.get('complex_items', [])) > 0:
            print("Complex Items:")
            print(
                ", ".join(
                    (
                        i['name'] + " (" + i['type'] + ")"
                        for i in self.current_location.get('complex_items', [])
                    )
                )
            )

    def ingredients(self, recipe_name):
        """
        Show the ingredients for a recipe
        """

        if not recipe_name:
            raise CommandArgumentError(
                "Sorry, you need to 'ingredients' something.")

        recipe = self.player.get_recipe(recipe_name)
        if not recipe:
            recipe = self.player.get_recipe(f"{recipe_name}_recipe")

        if recipe:
            print("Ingredients:")
            print(", ".join(recipe['ingredients']))
        else:
            print("You don't have that recipe.")

    def craft(self, recipe_name):
        """
        Craft an item
        """

        if not self.current_location.get('craftable', False):
            print("You can't craft here.")
            return

        if not recipe_name:
            raise CommandArgumentError("Sorry, you need to 'craft' something.")

        recipe = self.player.get_recipe(recipe_name)

        if not recipe:
            recipe = self.player.get_recipe(f"{recipe_name}_recipe")

        if recipe:
            if all(item_name in self.player.items for item_name in recipe['ingredients']):
                for item_name in recipe['ingredients']:
                    self.player.items.remove(item_name)
                print("You craft the " + recipe['result']['name'])
                self.current_location["complex_items"] = self.current_location.get(
                    "complex_items", []
                )
                self.current_location["complex_items"].append(recipe['result'])
                print("You can pick up the " +
                      recipe['result']['name'] + " now.")
            else:
                print("You don't have the ingredients to craft that.")
            return
        else:
            print("Recipe unavailble or you don't know how to craft that yet.")
            return

    def unlock(self, exit):
        """
        Unlock an exit
        """

        if not exit:
            raise CommandArgumentError(
                "Sorry, you need to 'unlock' something."
            )

        if exit not in self.current_location.get("exits", []):
            print("Exit does not exist")
            return

        if exit not in self.current_location.get("locked_exits", []):
            print("Exit is not locked")
            return

        exit_location = self.location_map[self.current_location["exits"][exit]]

        if exit_location.get("locked"):
            required_key = self.player.get_key(exit_location["required_key"])
            if required_key is not None and required_key.get('from') == self.current_location.get("id") and required_key.get("to") == exit_location.get("id"):
                print("You unlock the " + exit,
                      "with the key: " + required_key["name"])
                exit_location["locked"] = False
            else:
                print("You don't have the key to unlock the " + exit)
        else:
            print("The " + exit + " is already unlocked")

    def open_chest(self):
        """
        Open a chest
        """

        if not self.current_location.get("chest"):
            print("There's no chest here.")
            return

        if not self.current_location["chest"]["items"]:
            print("Wa Wa. The chest is empty.")
            return

        print(
            f"You open the {self.current_location['chest']['name']}. All the items fall out.")
        self.current_location["chest"]["locked"] = False
        self.current_location['complex_items'] = self.current_location.get(
            'complex_items', []
        )
        unlocked_items = list(unlock_chest(self.current_location["chest"]))
        print(f"you unlock the chest and find {unlocked_items[0]['name']}")
        self.current_location["complex_items"].extend(
            unlocked_items
        )
        self.current_location["chest"]["items"] = []

    def punch(self, enemy):
        """
        Punch an enemy
        """

        if not enemy:
            raise CommandArgumentError("Sorry, you need to 'punch' something.")

        self.attack(f"{enemy}:punch")

    def current_location_enemy_names(self):
        return list(self.current_location["enemies"].keys())

    def attack(self, enemy_and_weapon_name):
        """
        Attack an enemy
        """

        enemy_and_weapon_name = enemy_and_weapon_name.split(":", 1)
        weapon_name = None
        enemy = None

        if len(enemy_and_weapon_name) == 0:
            raise CommandArgumentError(
                "Sorry, you need to 'attack' someone with something."
            )
        elif len(enemy_and_weapon_name) == 1:
            raise CommandArgumentError(
                f"Sorry, you need to 'attack' {enemy_and_weapon_name[0]} with something."
            )
        else:
            enemy = enemy_and_weapon_name[0]
            weapon_name = enemy_and_weapon_name[1]

        weapon = self.player.get_weapon(weapon_name)

        if not weapon:
            print("You don't have that weapon.")
            return

        if not self.current_location.get("enemies"):
            print("There's nothing to attack here.")
            return

        if enemy in self.current_location["enemies"]:
            print("You attack the " + enemy + " with the " + weapon_name)
            if will_action_happen(self.current_location["enemies"][enemy].get("evasion_chance", 0)):
                print(f"The {enemy} evaded your attack!")
                return

            if not will_action_happen(weapon['chance']):
                print(f"You missed hitting the {enemy}!")
                return

            multiplier = 1
            if self.current_spell and self.current_spell.get("name") == "rage":
                print("Rage mode ongoing!")
                if self.current_spell["turns"] > 0:
                    self.current_spell["turns"] -= 1
                    multiplier = 1 + \
                        (self.current_spell["damage_multiplier"] / 100)
                if self.current_spell["turns"] == 0:
                    print("Your rage mode will be deactivated after this attack")
                    self.current_spell = None

            killed_enemy = self.damage_enemy(
                enemy, weapon['damage'] * multiplier
            )
            if killed_enemy:
                del self.current_location["enemies"][enemy]
        else:
            print(f"There is no {enemy} to attack here.")

    def use(self, spell_name):
        if not spell_name:
            raise CommandArgumentError("Sorry, you need to 'use' something.")

        spell = self.player.delete_spell(spell_name)

        if not spell:
            print("You don't have that spell on you. Craft it or dont 'use' it.")
            return

        enemies_available = len(self.current_location.get('enemies', [])) > 0

        if spell['name'] == 'peace':
            print(
                f"You cast a {spell_name} spell! A wave of white foam starts to consume the entire world"
            )
            raise StopGameEngine(
                "Thud! You get up with a loud noise of your phone hitting the floor. You check that your bed is wet with sweat. You had a nightmare. You have a sip of water, say your prayers and go back to sleep. You sleep now with peace knowing that you are safe and conquered everything."
            )

        if 'heal' in spell_name:
            print(
                f"You cast a {spell_name} spell! You heal {spell['heal_amount']} hp."
            )
            self.player.heal(spell['heal_amount'])
            print(f"You now have {self.player.hp} hp.")
            return

        shouldCast = True

        if not enemies_available:
            print("You are casting a spell for no reason. There are no enemies here.")

            shouldCastResponse = input(
                "Do you want to cast it anyway? (y/n): ")

            if not shouldCastResponse or shouldCastResponse.lower() in ['n', 'no', 'false', 'f', '0', 'nope']:
                shouldCast = False

        if not shouldCast:
            print("You decided not to cast the spell.")
            self.player.pick_spell(spell)
            return

        if spell['name'] == 'rage':
            print(
                f"Rage mode activated. Your damage is increased by {spell['damage_multiplier']} percentage for the next {spell['turns']} turns!"
            )
            self.current_spell = dict(spell)

        if spell['name'] == 'fireball':
            print("You cast a fireball!")
            self.attack_enemies_with_spell_damage(
                spell['damage']
            )

        if spell['name'] == 'poison':
            print(
                f"You cast a poison cloud! Enemies take {spell['damage']} damage per turn for the next {spell['turns']} turns including current turn."
            )
            self.current_spell = dict(spell)
            if len(self.current_location.get('enemies', [])) > 0:
                self.attack_enemies_with_spell_damage(
                    spell['damage']
                )
                self.current_spell['turns'] = spell['turns'] - 1

    def enemy_attack_at_start_of_turn(self):
        """
        Attack the player if there are enemies in the current location at the start of the turn
        """

        if not self.current_location:
            return

        if len(self.current_location.get('enemies', {})) == 0:
            return

        print()
        print("*" * 50)
        print()

        if self.current_spell is not None and self.current_spell.get('name') == "poison":
            if self.current_spell["turns"] > 0:
                print("Enemies are affected by posion damage!")
                self.attack_enemies_with_spell_damage(
                    self.current_spell['damage']
                )
                self.current_spell["turns"] -= 1
            if self.current_spell["turns"] == 0:
                print("Your poison spell wore out!")
                self.current_spell = None

            if len(self.current_location.get('enemies', [])) == 0:
                print("You snake-d your way to victory in this room!")

        hp_lost = 0
        for (name, i) in self.current_location['enemies'].items():
            if will_action_happen(i.get('chance', 1)):
                hp_lost += i['attack']
                print(f"{name} attacked you!")
            else:
                print(f"{name} missed!")
        self.player.take_hit(hp_lost)
        if hp_lost > 0:
            print(f"You lost {hp_lost} hp.")
        else:
            print("Lucky you! You didn't lose any hp.")
        if self.player.hp <= 0:
            raise StopGameEngine("You died!")
        print("Your current hp is:", self.player.hp)
        print()
        print("*" * 50)
        print()

    def attack_enemies_with_spell_damage(self, damage):
        killed_enemies = [
            self.damage_enemy(enemy, damage)
            for enemy in self.current_location['enemies']
        ]
        for enemy in killed_enemies:
            if enemy:
                del self.current_location['enemies'][enemy]

    def damage_enemy(self, enemy, damage):
        self.current_location['enemies'][enemy]['hp'] -= damage
        if self.current_location['enemies'][enemy]['hp'] <= 0:
            print(f"You killed the {enemy}!")
            drop = self.current_location['enemies'][enemy].get('drop')
            if drop:
                print(f"You found one {drop['type']}: `{drop['name']}`!")
                print("You can pickup the item with the 'get' command.")
                self.current_location['complex_items'] = self.current_location.get(
                    'complex_items', []
                )

                self.current_location['complex_items'].append(drop)

            return enemy
        else:
            print(
                f"The {enemy} has {self.current_location['enemies'][enemy]['hp']} hp left."
            )
            return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a map file.")
        sys.exit(1)
    map_parsor = MapParsor(sys.argv[1])
    map_parsor.parse()

    if map_parsor.is_valid():
        location_map = map_parsor.map
        GameEngine(location_map).play()
