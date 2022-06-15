import random
from copy import deepcopy

# how to convert from glob vars to prev/next_state

# our glob vars here
a = 1
b = 1
c = 1
d = 1
e = 1

# first put them together
init_state = a, b, c, d, e

# for concurrent runs, dont use global state
def compute_bid_state(info, prev_state=None):
    if prev_state is None:
        prev_state = deepcopy(init_state)
        
    # retrieve our glob vars
    a, b, c, d, e = prev_state

    # do smth
    a += 1
    b += 2

    bid = random.random() * info['self']['budget']
    

    # put them back in next_state
    next_state = a, b, c, d, e
    return bid, next_state