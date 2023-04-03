# Project 1 - Adventure Game

Submitted By
- Name: Anirudh Chintha
- Email: achintha@stevens.edu
- Github URL: 

## Description
This is a basic text based adventure game with some very interesting extensions.

## Basic Verbs

### 1. look
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

### 2. go (direction)
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

### 3. get (item)
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

### 4. inventory
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

### 5. quit
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


## Extensions
