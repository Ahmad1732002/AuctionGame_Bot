import random
import newStrategy
import random_strategy
from copy import deepcopy

# rules
needed_to_win = 3
init_budget = 100
item_types = ["Picasso", "Van_Gogh", "Rembrandt", "Da_Vinci"]

bots = [
    ("strat1", newStrategy.compute_bid_state),
    ("strat2", random_strategy.compute_bid_state),
    ("strat3", random_strategy.compute_bid_state),
    ("strat4", random_strategy.compute_bid_state),
    ("strat5", random_strategy.compute_bid_state),
    ("strat6", random_strategy.compute_bid_state),
    ("strat7", random_strategy.compute_bid_state),
   
]


def init_player_info(player_name):
    return {
        "name": player_name,
        "budget": init_budget,
        "item_count": {it: 0 for it in item_types},
    }


def get_info_for(player_name, base_info):
    info = deepcopy(base_info)
    players = info.pop("players")
    info["self"] = players[player_name]
    info["others"] = [p for name, p in players.items() if name != player_name]
    return info


winners = []
for i in range(100):
    num_bidders = len(bots)
    base_info = {
        "item_types": item_types,
        "items": random.choices(
            item_types, k=num_bidders * needed_to_win * len(item_types) + 1
        ),
        "history": [],
        "cur_round": 0,
        "history": [],
        "players": {name: init_player_info(name) for name, strat in bots},
    }



    state = {name: None for name, strat in bots}
    auction_winner = None
    for cur_round, item in enumerate(base_info["items"]):
        base_info["cur_round"] = cur_round

        if auction_winner is not None:
            break

        bids = []
        for name, strat in bots:
            player_info = get_info_for(name, base_info)
            bid, state[name] = strat(deepcopy(player_info), state[name])

            # round
            bid = max(0, min(player_info["self"]["budget"], int(bid)))
            bids.append((bid, random.random(), name))

        bid, _, round_winner = max(bids)
        print(item, bid, round_winner, sep="  \t")
        base_info['history'].append({"bid": bid, "item": item, "player": round_winner})
        base_info["players"][round_winner]["budget"] -= bid
        base_info["players"][round_winner]["item_count"][item] += 1
        if base_info["players"][round_winner]["item_count"][item] == needed_to_win:
            auction_winner = round_winner

    print('winner:', auction_winner)
    print()
    winners.append(auction_winner)
from collections import Counter
print(Counter(winners))