import time
import sys
import json
import random


class Parser:
    class __Parser:

        NO_COMPRENDE = [
            'No comprende. Uno mas?',
            "Sorry, didn't get it. Use smaller words, please.",
            'What was that?',
            "I don't understand.",
        ]

        def __init__(self, dictionary):
            self.dictionary = dictionary
            self._words = {}
            self._actions = []

            for action in dictionary:
                self._actions.append(action)
                for word in dictionary[action][-1]:
                    self._words[word] = len(self._actions) - 1

        def __str__(self):
            return repr(self) + self.dictionary

        def interpret(self, words):
            input_words = words.split(' ')
            for word in input_words:
                idx = -1
                for (i, action) in enumerate(self._actions):
                    if word == action:
                        idx = i
                        break
                if idx >= 0:
                    return self._actions[idx]
            return None

    instance = None

    def __init__(self, dictionary):
        if not Parser.instance:
            Parser.instance = Parser.__Parser(dictionary)
        else:
            Parser.instance.dictionary = dictionary

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def interpret(self, word):
        return self.instance.interpret(word)


class Player:
    def __init__(self, name=''):
        """player stats
        hp?
        location?
        items?
        """
        self.hp = 100
        self.name = name

    def is_alive(self):
        print('is_alive')
        self.hp > 0


class BlockType:
    """A type of node that can be placed on the map
    """

    DEFAULT_DESCRIPTION = "An unremarkable place"

    def __init__(self, description, is_passable):
        self.description = description or self.DEFAULT_DESCRIPTION
        self.is_passable = is_passable or False


class Block:
    """A node on the map.
    """

    def __init__(self, surface):
        self.surface_type = surface
        self.description = self.description()
        self.is_passable = self.is_passable()

    def __str__(self):
        self.surface_type.key

    def description(self):
        return self.surface_type.description

    def is_passable(self):
        return self.surface_type.is_passable


class GridGraph:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.nodes = {}

        self._block_types = {}

    def is_boundary(self, location):
        print('is_boundary')
        return len(self.neighbors(location)) < 4

    def neighbors(self, location):
        print('neighbors')
        neighbors = [
            self.nodes.get(location[0] - 1, location[1]),
            self.nodes.get(location[0] + 1, location[1]),
            self.nodes.get(location[0], location[1] - 1),
            self.nodes.get(location[0], location[1] + 1),
        ]
        return filter(lambda n: n, neighbors)

    def insert_node(self, location, symbol):
        if location[0] > self.width:
            self.width = location[0]
        if location[1] > self.height:
            self.height = location[1]

        surface_type = self._block_types.get(symbol)

        if not surface_type:
            return

        self.nodes[location] = Block(surface_type)

    def add_block_config(self, block_config):
        """
        Add metadata to map for block descriptions and actions

        Expects:
            key
            symbol
            passable
            description
        """
        self._block_types[block_config['symbol']] = BlockType(
                block_config.get('description'),
                block_config.get('passable'),
            )


class Game:
    def __init__(self, initial_state):
        """Set up some useful state.
        """
        self.current_coords = (0, 0)
        self.map = GridGraph()
        self.player = Player()
        self.parser = None

        for aspect in initial_state:
            self._read(aspect, initial_state[aspect])

    def _read(self, state_aspect, data):
        """Translate state aspect e.g. game map into game
        """
        if state_aspect == 'player':
            self.player = Player(data)
        elif state_aspect == 'map':
            with open(data) as map_file:
                for y, line in enumerate(map_file):
                    for x, char in enumerate(line):
                        self.map.insert_node((x, y), char)
        elif state_aspect == 'config':
            with open(data) as config_file:
                config_data = json.load(config_file)
                for config_aspect in config_data:
                    self._read(config_aspect, config_data[config_aspect])
        elif state_aspect == 'block_types':
            for block_type in data:
                self.map.add_block_config(block_type)
        elif state_aspect == 'responses':
            self.responses = data
        elif state_aspect == 'content':
            self.content = data
        elif state_aspect == 'dictionary':
            self.parser = Parser(data)

    # def _draw(self):
    #     unmap = {v: k for k, v in self.MAP_KEY.items()}
    #     line_buffer = ''
    #     for y in range(0, self.map.height + 1):
    #         for x in range(0, self.map.width + 1):
    #             node = self.map.nodes.get((x, y))
    #             line_buffer += unmap[node.surface] if node else '#'
    #         line_buffer = ''

    def _introduction(self):
        self._narrate(self.content.get("introduction"))
        self.player.name = input("What's your name again?\n > ")
        print("OK, %s." % self.player.name)

    def _move(self, direction):
        directions = {
            'N': (0, 1),
            'E': (1, 0),
            'S': (0, -1),
            'W': (-1, 0),
        }

        desired_coords = (
            self.current_coords[0] + directions[direction][0],
            self.current_coords[1] + directions[direction][1]
        )

        desired_block = self.map.nodes.get(desired_coords)

        if desired_block.is_passable:
            self.current_coords = desired_coords
            return desired_block
        else:
            return None

    def _describe(self):
        surroundings = self.map.nodes.get(self.current_coords)
        self._narrate('Your surroundings: %s ' % surroundings.description)

    def _narrate(self, content):
        print()
        print('* ' * 20)
        for char in content:
            if char == '\n':
                print(char)
                # time.sleep(1)
            else:
                print(char, end='')
                sys.stdout.flush()
                # time.sleep(0.02)
        print()

    def _ask(self, prompt=None):
        NO_COMPRENDE = [
            'No comprende. Uno mas?',
            "Sorry, didn't get it. Use smaller words, please.",
            'What was that?',
            "I don't understand.",
        ]
        if prompt:
            print(prompt)

        response = input('\n > ')
        action = self.parser.interpret(response)
        params = response.split(' ')[-1]

        if not action:
            return self._ask(NO_COMPRENDE[random.randrange(len(NO_COMPRENDE))])
        return (action, params)

    def _respond(self, action, **kwargs):
        """Apply result here, increment/decrement whatever
        """
        if action == 'move':
            direction = kwargs['params'].get('direction')
            if self._move(direction):
                self._narrate("You moved %s." % direction)
            else:
                self._narrate("You cannot move %s." % direction)
            return None

        self._narrate("You chose to %s. That's a bold move." % action)

    def play(self):
        """Do loop for a) prompting based on state b) translating action c) mutating state based on action d) presenting result
        """
        if not self.player.name:
            self._introduction()

        while self.player.is_alive:
            self._describe()
            action, params = self._ask()
            self._respond(action, params=params)


game = Game({
    'config': 'config.json',
    'map': 'map.txt'
})
game.play()
