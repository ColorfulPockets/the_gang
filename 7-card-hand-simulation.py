import random
from collections import Counter, defaultdict

NUM_SIMULATIONS = 1000000

RANKS = list(range(1, 14))  # 1 = Ace
SUITS = ["H", "D", "C", "S"]

DECK = [(r, s) for r in RANKS for s in SUITS]


def get_longest_consecutive(ranks):
    unique = set(ranks)

    # Ace high handling
    if 1 in unique:
        unique.add(14)

    sorted_ranks = sorted(unique)

    longest = 1
    current = 1

    for i in range(1, len(sorted_ranks)):
        if sorted_ranks[i] == sorted_ranks[i - 1] + 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    return longest


def get_longest_straight_flush(hand):
    suit_groups = defaultdict(list)
    for r, s in hand:
        suit_groups[s].append(r)

    longest = 0
    for ranks in suit_groups.values():
        if len(ranks) >= 3:
            longest = max(longest, get_longest_consecutive(ranks))

    return longest


def has_smaller_straight_house(ranks, rank_counts):
    pair_ranks = {rank for rank, count in rank_counts.items() if count >= 2}
    if not pair_ranks:
        return False

    unique = set(ranks)
    if 1 in unique:
        unique.add(14)

    sorted_ranks = sorted(unique)

    for i in range(len(sorted_ranks) - 2):
        first = sorted_ranks[i]
        second = sorted_ranks[i + 1]
        third = sorted_ranks[i + 2]

        if second == first + 1 and third == second + 1:
            straight_ranks = {1 if rank == 14 else rank for rank in (first, second, third)}
            if any(pair_rank not in straight_ranks for pair_rank in pair_ranks):
                return True

    return False


def has_smaller_straight_flush_house(hand, rank_counts):
    pair_ranks = {rank for rank, count in rank_counts.items() if count >= 2}
    if not pair_ranks:
        return False

    suit_groups = defaultdict(list)
    for rank, suit in hand:
        suit_groups[suit].append(rank)

    for ranks in suit_groups.values():
        unique = set(ranks)
        if len(unique) < 3:
            continue

        if 1 in unique:
            unique.add(14)

        sorted_ranks = sorted(unique)

        for i in range(len(sorted_ranks) - 2):
            first = sorted_ranks[i]
            second = sorted_ranks[i + 1]
            third = sorted_ranks[i + 2]

            if second == first + 1 and third == second + 1:
                straight_flush_ranks = {1 if rank == 14 else rank for rank in (first, second, third)}
                if any(pair_rank not in straight_flush_ranks for pair_rank in pair_ranks):
                    return True

    return False


def classify_hand(hand):
    results = set()

    ranks = [r for r, _ in hand]
    suits = [s for _, s in hand]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    pair_counts = sum(1 for c in rank_counts.values() if c >= 2)
    three_counts = sum(1 for c in rank_counts.values() if c >= 3)
    four_counts = sum(1 for c in rank_counts.values() if c >= 4)

    longest_straight = get_longest_consecutive(ranks)
    longest_flush = max(suit_counts.values())
    longest_sf = get_longest_straight_flush(hand)

    # Pairs
    if pair_counts >= 1:
        results.add("Pair")
    if pair_counts >= 2:
        results.add("Two Pair")
    if pair_counts >= 3:
        results.add("Three Pair")

    # Three of a kind
    if three_counts >= 1:
        results.add("Three of a Kind")
    if three_counts >= 2:
        results.add("Double Three of a Kind")

    # Four of a kind
    if four_counts >= 1:
        results.add("Four of a Kind")

    # Full house types
    if three_counts >= 1 and pair_counts >= 2:
        results.add("Full House")
    if four_counts >= 1 and pair_counts >= 2:
        results.add("Fuller House (4 of a kind + pair)")
    if four_counts >= 1 and three_counts >= 2:
        results.add("Fullest House (4 of a kind + 3 of a kind)")

    # Straights
    if longest_straight >= 3:
        results.add("Smaller Straight (3 cards)")
    if has_smaller_straight_house(ranks, rank_counts):
        results.add("Smaller Straight House")
    if longest_straight >= 4:
        results.add("Small Straight (4 cards)")
    if longest_straight >= 5:
        results.add("Straight (5 cards)")
    if longest_straight >= 6:
        results.add("Longer Straight (6 cards)")
    if longest_straight >= 7:
        results.add("Longest Straight (7 cards)")

    # Flushes
    if longest_flush >= 3:
        results.add("Smaller Flush (3 cards)")
    if longest_flush >= 4:
        results.add("Small Flush (4 cards)")
    if longest_flush >= 5:
        results.add("Flush (5 cards)")
    if longest_flush >= 6:
        results.add("Bigger Flush (6 cards)")
    if longest_flush >= 7:
        results.add("Biggest Flush (7 cards)")

    # Straight flush
    if longest_sf >= 3:
        results.add("Smaller Straight Flush (3 cards)")
    if has_smaller_straight_flush_house(hand, rank_counts):
        results.add("Smaller Straight Flush House")
    if longest_sf >= 4:
        results.add("Small Straight Flush (4 cards)")
    if longest_sf >= 5:
        results.add("Straight Flush (5 cards)")
    if longest_sf >= 6:
        results.add("Longer Straight Flush (6 cards)")
    if longest_sf >= 7:
        results.add("Longest Straight Flush (7 cards)")
    return results


results_counter = Counter()

for _ in range(NUM_SIMULATIONS):
    hand = random.sample(DECK, 7)
    categories = classify_hand(hand)
    for cat in categories:
        results_counter[cat] += 1

print(f"\nResults after {NUM_SIMULATIONS} simulations:\n")

sorted_results = sorted(
    results_counter.items(),
    key=lambda x: x[1],
    reverse=True
)

for hand_type, count in sorted_results:
    percent = (count / NUM_SIMULATIONS) * 100
    print(f"{hand_type}: {count} ({percent:.2f}%)")
