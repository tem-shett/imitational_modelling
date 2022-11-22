import simpy
import random
from enum import Enum

EPS = 10 ** -6


class State(Enum):
    MOVING_IN_QUEUE = 1
    MOVING_NOT_IN_QUEUE = 2
    STANDING_IN_QUEUE = 3
    STANDING_NOT_IN_QUEUE = 4
    NOT_IN_FRAME_YET = 5
    GONE_FOREVER = 6


class Event(Enum):
    ENTER_FRAME = 1  # e1
    EXIT_FRAME = 2  # e2
    EXIT_THROUGH_PASSPORT_CONTROL = 3  # e3
    ENTER_QUEUE_MOVING_END = 4  # e4
    ENTER_QUEUE_MOVING_MIDDLE = 5  # e5
    EXIT_QUEUE_MOVING = 6  # e6
    START_MOVING_NOT_IN_QUEUE = 7  # e7
    STOP_MOVING_NOT_IN_QUEUE = 8  # e8
    START_MOVING_IN_QUEUE = 9  # e9
    STOP_MOVING_IN_QUEUE = 10  # e10
    EXIT_QUEUE_STANDING = 11  # e11
    ENTER_QUEUE_STANDING = 12  # e12

    CONTINUE_MOVING_NOT_IN_QUEUE = 13  # e01
    CONTINUE_STANDING_NOT_IN_QUEUE = 14  # e02
    CONTINUE_MOVING_IN_QUEUE = 15  # e03
    CONTINUE_STANDING_IN_QUEUE = 16  # e04


event_destination = {
    Event.ENTER_FRAME: State.MOVING_NOT_IN_QUEUE,
    Event.EXIT_FRAME: State.GONE_FOREVER,
    Event.EXIT_THROUGH_PASSPORT_CONTROL: State.GONE_FOREVER,
    Event.ENTER_QUEUE_MOVING_END: State.MOVING_IN_QUEUE,
    Event.ENTER_QUEUE_MOVING_MIDDLE: State.MOVING_IN_QUEUE,
    Event.EXIT_QUEUE_MOVING: State.MOVING_NOT_IN_QUEUE,
    Event.START_MOVING_NOT_IN_QUEUE: State.MOVING_NOT_IN_QUEUE,
    Event.STOP_MOVING_NOT_IN_QUEUE: State.STANDING_NOT_IN_QUEUE,
    Event.START_MOVING_IN_QUEUE: State.MOVING_IN_QUEUE,
    Event.STOP_MOVING_IN_QUEUE: State.STANDING_IN_QUEUE,
    Event.EXIT_QUEUE_STANDING: State.STANDING_NOT_IN_QUEUE,
    Event.ENTER_QUEUE_STANDING: State.STANDING_IN_QUEUE,

    Event.CONTINUE_MOVING_NOT_IN_QUEUE: State.MOVING_NOT_IN_QUEUE,
    Event.CONTINUE_STANDING_NOT_IN_QUEUE: State.STANDING_NOT_IN_QUEUE,
    Event.CONTINUE_MOVING_IN_QUEUE: State.MOVING_IN_QUEUE,
    Event.CONTINUE_STANDING_IN_QUEUE: State.STANDING_IN_QUEUE
}

probability_distribution = {
    State.NOT_IN_FRAME_YET: {
        Event.ENTER_FRAME: 1
    },
    State.MOVING_NOT_IN_QUEUE: {
        Event.CONTINUE_MOVING_NOT_IN_QUEUE: 0.94,
        Event.STOP_MOVING_NOT_IN_QUEUE: 0.01,
        Event.EXIT_FRAME: 0.01,
        Event.ENTER_QUEUE_MOVING_END: 0.02,
        Event.ENTER_QUEUE_MOVING_MIDDLE: 0.02
    },
    State.STANDING_NOT_IN_QUEUE: {
        Event.CONTINUE_STANDING_NOT_IN_QUEUE: 0.95,
        Event.START_MOVING_NOT_IN_QUEUE: 0.045,
        Event.ENTER_QUEUE_STANDING: 0.005,
    },
    State.MOVING_IN_QUEUE: {
        Event.CONTINUE_MOVING_IN_QUEUE: 0.65,
        Event.STOP_MOVING_IN_QUEUE: 0.32,
        Event.EXIT_THROUGH_PASSPORT_CONTROL: 0.02,
        Event.EXIT_QUEUE_MOVING: 0.01,
    },
    State.STANDING_IN_QUEUE: {
        Event.CONTINUE_STANDING_IN_QUEUE: 0.9,
        Event.EXIT_QUEUE_STANDING: 0.02,
        Event.START_MOVING_IN_QUEUE: 0.08
    }
}


def get_transition(current_state: State):
    val = random.random()
    for (event, probability) in probability_distribution[current_state].items():
        val -= probability
        if val < EPS:
            return event_destination[event]


class Person:
    def __init__(self, name: str):
        self.state = State.NOT_IN_FRAME_YET
        self.name = name

    def run(self, env):
        while self.state != State.GONE_FOREVER:
            new_state = get_transition(self.state)
            if new_state != self.state:
                print(f'{env.now}: {self.name} moved to {new_state}')
            self.state = new_state
            yield env.timeout(1)


names = [str(i) for i in range(1, 10)]

people = [Person(name) for name in names]
env = simpy.Environment()

for person in people:
    env.process(person.run(env))

env.run(until=100000)
