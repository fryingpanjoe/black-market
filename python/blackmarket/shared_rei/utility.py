from random import random


def weighted_choice(seq):
    """Returns a randomly chosen object based on its weight from the sequence
    `seq` which consists of (weight, obj) tuples."""
    total_weight = float(sum(weight for weight, _ in seq))
    r = random()
    p = 0.0
    for weight, obj in seq:
        p += weight / total_weight
        if r <= p:
            return obj
