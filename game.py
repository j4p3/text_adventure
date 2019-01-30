import time
import sys
import json


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
        self.hp > 0


class Block:
    TYPES = {
        'WALL': 0,
        'FLOOR': 1,
        'DOOR': 2
    }

    DEFAULT_DESCRIPTION = 'You are in a converted hotel above a laundromat. You are likely to be eaten by a grue.'

    def __init__(self, surface='WALL', description=DEFAULT_DESCRIPTION):
        self.surface = surface
        self.description = description

    def __str__(self):
        self.description


class GridGraph:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.nodes = {}

    def is_boundary(self, location):
        return len(self.neighbors(location)) < 4

    def neighbors(self, location):
        neighbors = [
            self.nodes.get(location[0] - 1, location[1]),
            self.nodes.get(location[0] + 1, location[1]),
            self.nodes.get(location[0], location[1] - 1),
            self.nodes.get(location[0], location[1] + 1),
        ]
        return filter(lambda n: n, neighbors)

    def insert_node(self, location, **kwargs):
        if location[0] > self.width:
            self.width = location[0]
        if location[1] > self.height:
            self.height = location[1]
        self.nodes[location] = Block(kwargs.get('surface'), kwargs.get('description'))


class Game:
    MAP_KEY = {
        '#': 'WALL',
        '_': 'FLOOR',
        '|': 'DOOR',
        'X': 'EXIT',
    }

    def __init__(self, initial_state):
        """Set up some useful state.
        """
        self.current_coords = (0, 0)
        self.map = GridGraph()
        self.player = Player()

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
                        self.map.insert_node(
                            (x, y),
                            surface=self.MAP_KEY.get(char, 'WALL'),
                        )
        elif state_aspect == 'config':
            with open(data) as config_file:
                config_data = json.load(config_file)
                for config_aspect in config_data:
                    print('commencing read for %s' % config_aspect)
                    self._read(config_aspect, config_data[config_aspect])
        elif state_aspect == 'block_types':
            pass
        elif state_aspect == 'responses':
            self.responses = data
        elif state_aspect == 'content':
            print('initializing content')
            # why is config_data the entire data blob rather than the config section?
            print(data)
            self.content = data

    def _draw(self):
        unmap = {v: k for k, v in self.MAP_KEY.items()}
        line_buffer = ''
        for y in range(0, self.map.height + 1):
            for x in range(0, self.map.width + 1):
                node = self.map.nodes.get((x, y))
                line_buffer += unmap[node.surface] if node else '#'
            print(line_buffer)
            line_buffer = ''

    def _introduction(self):
        self._narrate(self.content.get("introduction"))
        self.player.name = self._ask("What's your name again?")
        print("OK, %s." % self.player.name)

    def _parse(self, input):
        """Match player input to something
        """
        USELESS_WORDS = ['a', 'the', 'i']
        return input

    def _describe(self):
        print(self.current_coords)
        surroundings = self.map.nodes.get(self.current_coords)
        self._narrate(surroundings.description)

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
        print('* ' * 20)
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

        action = self._parse(input('\n > '))

        if not action:
            return self._ask(NO_COMPRENDE[random.randrange(len(NO_COMPRENDE))])
        return action

    def _respond(self, action):
        """Apply result here, increment/decrement whatever
        """
        self._narrate("You chose to %s. That's a bold move." % action)

    def play(self):
        """Do loop for a) prompting based on state b) translating action c) mutating state based on action d) presenting result
        """
        if not self.player.name:
            self._introduction()

        while self.player.is_alive:
            self._describe()
            action = self._ask()
            self._respond()


game = Game({
    'map': 'map.txt',
    'config': 'config.json'
})
game.play()
