import simpy
import random

CHANGE_CHANCE = [20, 70]
STATE_NAME = ['moving', 'standing']


def person(env, num):
    cur_state = 0
    while True:
        if random.randint(0, 100) < CHANGE_CHANCE[cur_state]:
            cur_state = 1 - cur_state
            print(f'{num} changed state to {STATE_NAME[cur_state]} in {env.now}')
        yield env.timeout(1)


env = simpy.Environment()
for i in range(5):
    env.process(person(env, i))
env.run(until=15)
