import time

import simpy
import ffmpeg
from PIL import Image
import numpy as np
import random
from enum import Enum

EPS = 10 ** -6


class State(Enum):
    MOVING_IN_QUEUE = 1
    STANDING_IN_QUEUE = 3
    NOT_IN_FRAME_YET = 5
    GONE_FOREVER = 6


class Event(Enum):
    ENTER_QUEUE_MOVING_END = 4  # e4
    ENTER_QUEUE_MOVING_MIDDLE = 5  # e5
    EXIT_QUEUE_MOVING = 6  # e6
    START_MOVING_IN_QUEUE = 9  # e9
    STOP_MOVING_IN_QUEUE = 10  # e10
    EXIT_QUEUE_STANDING = 11  # e11
    ENTER_QUEUE_STANDING = 12  # e12

    CONTINUE_MOVING_IN_QUEUE = 15  # e03
    CONTINUE_STANDING_IN_QUEUE = 16  # e04


event_destination = {
    Event.ENTER_QUEUE_MOVING_END: State.MOVING_IN_QUEUE,
    Event.ENTER_QUEUE_MOVING_MIDDLE: State.MOVING_IN_QUEUE,
    Event.EXIT_QUEUE_MOVING: State.GONE_FOREVER,
    Event.START_MOVING_IN_QUEUE: State.MOVING_IN_QUEUE,
    Event.STOP_MOVING_IN_QUEUE: State.STANDING_IN_QUEUE,
    Event.EXIT_QUEUE_STANDING: State.GONE_FOREVER,
    Event.ENTER_QUEUE_STANDING: State.STANDING_IN_QUEUE,

    Event.CONTINUE_MOVING_IN_QUEUE: State.MOVING_IN_QUEUE,
    Event.CONTINUE_STANDING_IN_QUEUE: State.STANDING_IN_QUEUE
}

probability_distribution = {
    State.NOT_IN_FRAME_YET: {
    },
    State.MOVING_IN_QUEUE: {
        Event.CONTINUE_MOVING_IN_QUEUE: 0.99,
        Event.STOP_MOVING_IN_QUEUE: 0.01,
        Event.EXIT_QUEUE_MOVING: 0
    },
    State.STANDING_IN_QUEUE: {
        Event.CONTINUE_STANDING_IN_QUEUE: 0.95,
        Event.EXIT_QUEUE_STANDING: 0,
        Event.START_MOVING_IN_QUEUE: 0.05
    }
}


def get_transition(current_state: State):
    val = random.random()
    for (event, probability) in probability_distribution[current_state].items():
        val -= probability
        if val < EPS:
            return event_destination[event]


class ViewField:
    def __init__(self):
        self.height = 300
        self.width = 300
        self.passport_control_seg = (120, 180)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    @staticmethod
    def limit_value(a: int, limit: int):
        return limit if a > limit else -limit if a < -limit else a

    def limit_vector(self, limit_vector):
        self.x = Vector.limit_value(self.x, limit_vector.x)
        self.y = Vector.limit_value(self.y, limit_vector.y)


class Person:
    def __init__(self, name: str):
        self.state = State.NOT_IN_FRAME_YET
        self.name = name
        self.pt = Vector(0, 0)
        self.speed_vector = Vector(0, 0)
        self.max_speed = Vector(1, 1)
        self.field = ViewField()
        self.img_color = [random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)]

    def check_out_of_bounds(self):
        return self.pt.x < 0 or self.pt.x > self.field.width or self.pt.y < 0 or self.pt.y > self.field.height

    def check_gone_through_passport_control(self):
        return self.pt.y > self.field.height and self.field.passport_control_seg[0] < self.pt.x < \
               self.field.passport_control_seg[1]

    def move(self):
        self.speed_vector += Vector((random.random() - 0.4) / 2, (random.random()-0.5) / 20)
        self.speed_vector.limit_vector(self.max_speed)
        self.pt += self.speed_vector

    def run(self, env):
        if self.state == State.NOT_IN_FRAME_YET:
            self.pt = Vector(self.field.height / 3 - random.random() * 100, self.field.width / 2)
            self.state = State.STANDING_IN_QUEUE
        while self.state != State.GONE_FOREVER:
            print(self.speed_vector.x, self.speed_vector.y)
            if self.state == State.MOVING_IN_QUEUE:
                self.move()
            if self.check_out_of_bounds():
                if self.check_gone_through_passport_control():
                    pass
                new_state = State.GONE_FOREVER
            else:
                new_state = get_transition(self.state)
            if new_state != self.state:
                print(f'{env.now}: {self.name} moved to {new_state}')
            self.state = new_state
            yield env.timeout(1)


class Handler:
    def __init__(self):
        self.field = ViewField()
        self.frame_number = 0

    def run(self, env):
        flag_continue = True
        while flag_continue:
            flag_continue = False
            img = np.zeros((self.field.width + 1, self.field.height + 1, 3), dtype=np.uint8)
            for pers in people:
                if not pers.check_out_of_bounds():
                    flag_continue = True
                    img[int(pers.pt.x)][int(pers.pt.y)] = pers.img_color
            img = Image.fromarray(img, 'RGB')
            img.save(r'C:\Users\artem\imitational_modelling\images\img'+str(self.frame_number)+'.png')
            self.frame_number += 1
            yield env.timeout(1)


names = [str(i) for i in range(5)]

people = [Person(name) for name in names]
handler = Handler()
env = simpy.Environment()

for person in people:
    env.process(person.run(env))
env.process(handler.run(env))

env.run(until=100000)

(
    ffmpeg
    .input(r'C:\Users\artem\imitational_modelling\images\img*.png', pattern_type='glob', framerate=25)
    .output('movie.mp4')
    .run()
)
