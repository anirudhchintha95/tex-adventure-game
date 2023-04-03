# CS 515-A - Project 1 - Adventure Game

Submitted By

- Name: Anirudh Chintha
- Email: achintha@stevens.edu
- Github URL: https://github.com/anirudhchintha95/text-adventure-game

## Description

This is a basic text based adventure game with some very interesting extensions.

## Time Spent

48 hours

## Basic Verbs

### 1. `look`

- No. of required args - 0
- This verb is shows current rooms' details.
- Usage Eg:

```
What would you like to do? look
> A white room

You are in a simple room with white walls.

Items: button

Exits: north east

```

### 2. `go (direction)`

- No. of required args - 1
- This verb is used to navigate from one location to another.
- After it goes to next location, it looks into that location.
- If the argument is not provided, it will throw error.
- If the argument provided is not in current locations' exits, it will throw error.
- Usage Eg:

```
What would you like to do? go north
You go north.

> A blue room

This room is simple, too, but with blue walls.

Exits: east south

```

```
What would you like to do? go WEST
There's no way to go west.
```

```
What would you like to do? GO NORTHEAST
There's no way to go northeast.
```

### 3. `get (item)`

- No. of required args - 1
- This verb is used to get items in the current location.
- If the argument is not provided, it will throw error.
- If the argument provided is not in items list in current location, it will throw error.
- Usage Eg:

```
What would you like to do? get rose
There's no rose anywhere.
```

```
What would you like to do? get BUTTON
You pick up the button.
```

```
What would you like to do? GET DECK OF cards
You pick up the deck of cards.
```

### 4. `inventory`

- No. of required args - 0
- This verb will list the items that you have on you after you `get` them rooms.
- If there are no personal inventory, it will say so.
- Otherwise, it will list the inventory available on you(More about this on extensions).
- Usage Eg:

```
What would you like to do? inventory
You're not carrying anything.
```

```
What would you like to do? inventory
Inventory:
  rose
  deck of cards
```

### 5. `quit`

- No. of required args - 0
- This verb will quit the game completely.
- ctrl+d should not quit the game, but should mention to use the quit word.
- ctrl+c should also quit the game throwing the normal keyboard interrupt error.
- Usage Eg:

```
What would you like to do? ^D
Use 'quit' to exit.
What would you like to do? quit
Goodbye!
```

```
What would you like to do? ^CTraceback (most recent call last):
  ...
KeyboardInterrupt
```

## Map layout and hints

8 -- 7 -- 6 -- 9
|
3 -- 4 -- 5
  /  |  
2 -- 1 -- 0

- Crafting room available at room 0 and 4.
- Make sure you kill enemies before doing anything
- Make sure you check if you have `ingredients` or if the room has `items` for a recipe to craft. Every recipe as the game progresses provides powerful stuff compared to the one before.

## Extensions

### Combat with win/lose conditions

- If there are enemies in the room, they will attack at the start of every turn until you kill them.
- You can attack enemies as well.
- Each weapon will have a damage attribue and a chance attribute. Damage tells the amount of hp it will take off of the enemy, while the chance tells us the probability of the hit landing on the enemy.
- Enemy will also have these attributes(and more?). So strategize and be careful.
- Once you reach the end, you will face a final boss and defeating him will win you the run.
- If at any point of time, your hp goes below or equal to 0, the game ends.
- You can use the following verbs to attack individual enemies

  - 1. `punch (enemy)`

    - This is the first combat move available.
    - This verb will attack 9 out of 10 times

    ```
    {
        "name": "punch",
        "type": "weapon",
        "desc": "Deals 1 damage",
        "damage": 1,
        "chance": 0.9
    }
    ```

    ```
    What would you like to do? punch goblin
    You attack the goblin with the punch
    ```

  - 2. `attack (enemy)`
    - This will take one argument seperated by `:`.
    - The first part is supposed to be the enemy while the second part should be the weapon.
    ```
    What would you like to do? attack zombie1:spear
    You attack the zombie1 with the spear
    ```
  - 3. `use (spell)`
    - There are heal spells and attack spells.
    - You can use heal spells to heal yourself and attack spells to attack the enemy or modify your attack power.
    - Rage and Poison works 3 times on enemies.
    ```
    What would you like to do? use fireball
    You cast a fireball!
    The enemy has 20 hp left.
    ```
  - 4. `hp`
    - Shows your current hp.

### Crafting and managing inventory

- Craft requires you to have recipes that are dropped by killing enemies.
- There is max cap for invemtory. So juggling your inventory is a important thing.
- Also, there are certain places where you can craft. So juggling items becomes even more important now.
- You can craft new items and manage your inventory using the following verbs.
  - 1. `craft (recipe_name)`
    - This crafts the recipe and adds the result to the current room's items.
    - You can later pick em up using get command.
    - Recipes are dropped by enemies after you defeat them. So keep an eye out and save everything(These wont take your inventory space.)ß
    - There are crafting recipes available for spells and weapons as well. Make sure that you look around for enemies before crafting.
    - If you dont have the required ingredients in your bag, it will throw an error
    ```
    You pick up the spear_recipe.
    What would you like to do? craft spear_recipe
    You craft the spear
    ```
    ```
    You pick up the spear_recipe.
    What would you like to do? craft spear
    You craft the spear
    ```
  - 2. `drop (item_name)`
    - This works opposite to get.
    - This drops item in your current inventory onto the current locations items.
    ```
    What would you like to do? drop BUTTON
    You dropped the button.
    ```
  - 3. `inventory`
    - Inventory also shows your recipes, items, weapons and spells if any.
  - 4. `ingredients (recipe_name)`
    - As the command suggests, it shows the ingredients required for a certain recipe

### Unlocking doors and chests.

- There are doors that can be unlocked and chests that can be opened in the game.
- This can be done by the following commands.
  - 1. `unlock (direction)`
    - if the direction is locked, we can use this keyword to unlock it.
    - This requires a specific key that will come from enemy drops. So keep an eye out and save everything(These wont take your inventory space.)
    - Once unlocked, you can go through it any number of times.
    ```
    What would you like to do? unlock north
    You unlock the east with the key: key-7-6
    ```
  - 2. `open_chest`
    - There are chests available in a few locations.
    - Use this command to open them and get the loot. You might as wll find something `god`ly.

## Code testing.

- Initially tested using running the code everytime.
- At the later stages, when the map was becoming bigger with extensions, that seemed counter-intuitive to just run it everytime manually.
- Hence I wrote a simple shell script that executes the entire map.
- Upon running this script, the chance of winning looks to be around 50%(26 wins and 24 losses).
- `For professor and TAs:` You can follow a similar path of written in shell script. It does not include picking up items from chests. That might swing the chances in your favor.

## Bugs and challenges.

### Bugs

- Currently, after a few runs, I could not find any bugs.

### Challenges

- One of the major challenges was to develop a balance map with the core functionality and the extensions intact. This was acheieved using the following conditions
  - checking if there are any enemies right now to maintain the maximum capacity
  - checking if there are extension keys available before doing anything in the vanilla verbs.
  - Maintaining the assets details in the map.
- Also handling different use cases for combat and spells were challenging. Handled this by making sure that the damage caused to enemies came from a single source rather than repeating code everytime.
