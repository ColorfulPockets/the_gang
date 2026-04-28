import random
from collections import Counter

NUM_SIMULATIONS = 10000

# Card ranks (Ace treated as 1 initially)
RANKS = list(range(1, 14))  # 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
SUITS = ["H", "D", "C", "S"]

# Build deck as (rank, suit)
DECK = [(rank, suit) for rank in RANKS for suit in SUITS]


def has_n_of_a_kind(rank_counts, n):
	for count in rank_counts.values():
		if count >= n:
			return True
	return False


def count_pairs(rank_counts):
	return sum(1 for count in rank_counts.values() if count >= 2)


def has_straight(ranks, length):
	"""
	ranks: iterable of distinct ranks
	length: required straight length (3 or 4)
	Ace can be low (1) or high (14)
	No wrap-around (K-A-2 not allowed)
	"""
	unique_ranks = set(ranks)

	# If Ace present, add 14 as possible high Ace
	if 1 in unique_ranks:
		unique_ranks.add(14)

	sorted_ranks = sorted(unique_ranks)

	consecutive = 1
	for i in range(1, len(sorted_ranks)):
		if sorted_ranks[i] == sorted_ranks[i - 1] + 1:
			consecutive += 1
			if consecutive >= length:
				return True
		else:
			consecutive = 1

	return False


results = {
	"Pair": 0,
	"Two Pair": 0,
	"Tiny Straight": 0,
	"Small Straight": 0,
	"Three of a Kind": 0
}

for _ in range(NUM_SIMULATIONS):
	hand = random.sample(DECK, 7)
	ranks = [card[0] for card in hand]
	rank_counts = Counter(ranks)

	# Pair
	if count_pairs(rank_counts) >= 1:
		results["Pair"] += 1

	# Two Pair
	if count_pairs(rank_counts) >= 2:
		results["Two Pair"] += 1

	# Three of a Kind
	if has_n_of_a_kind(rank_counts, 3):
		results["Three of a Kind"] += 1

	# Tiny Straight (3 in a row)
	if has_straight(ranks, 3):
		results["Tiny Straight"] += 1

	# Small Straight (4 in a row)
	if has_straight(ranks, 4):
		results["Small Straight"] += 1


print(f"Results after {NUM_SIMULATIONS} simulations:\n")
for hand_type, count in results.items():
	percentage = (count / NUM_SIMULATIONS) * 100
	print(f"{hand_type}: {count} ({percentage:.2f}%)")
