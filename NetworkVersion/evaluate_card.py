from collections import Counter
from itertools import combinations
from NetworkVersion.utils import Chosen_Card_Info


# gets the most common element from a list
def Most_Common(lst):
    data = Counter(lst)
    return data.most_common(1)[0]


# gets card value from  a hand. converts A to 14,  is_seq function will convert the 14 to a 1 when necessary to evaluate A 2 3 4 5 straights
def convert_to_nums(h):
    nums = {'J': 11, 'Q': 12, 'K': 13, "A": 14}
    return [nums[x.rank] if x.rank in nums.keys() else int(x.rank) for x in h]


# is royal flush
# if a hand is a straight and a flush and the lowest value is a 10 then it is a royal flush
def is_royal(h):
    if is_seq(h)[0] and is_flush(h)[0]:
        nn = convert_to_nums(h)
        if min(nn) == 10:
            return True, is_seq(h)[1]
    else:
        return False, None


def is_straight_flush(h):
    if is_seq(h)[0] and is_flush(h)[0]:
        return True, is_seq(h)[1]
    return False, None


# converts hand to number valeus and then evaluates if they are sequential  AKA a straight
# if it is, return the max num of the seq
def is_seq(h):
    h = convert_to_nums(h)

    h = sorted(h, reverse=True)
    ref = True
    for x in range(len(h)-1):
        if not h[x]+1 == h[x+1]:
            ref = False
            break
    if ref:
        return True, h

    for x in range(len(h)):
        if h[x] == 14:
            h[x] = 1

    h = sorted(h, reverse=True)
    for x in range(0,len(h)-1):
        if not h[x]-1 == h[x+1]:
            return False, None
    return True, h


# call set() on the suite values of the hand and if it is 1 then they are all the same suit
def is_flush(h):
    suits = [x.suit for x in h]
    if len(set(suits)) == 1:
        return True, sorted(convert_to_nums(h), reverse=True)
    else:
        return False, None


# if the most common element occurs 4 times then it is a four of a kind
def is_fourofakind(h):
    h = convert_to_nums(h)
    i = Most_Common(h)
    if i[1] == 4:
        return True, [i[0]] + [x for x in h if x != i[0]]
    else:
        return False, None


# if the most common element occurs 3 times then it is a three of a kind
def is_threeofakind(h):
    h = convert_to_nums(h)
    i = Most_Common(h)
    if i[1] == 3:
        return True, [i[0]] + sorted([x for x in h if x != i[0]], reverse=True)
    else:
        return False, None


# if the first 2 most common elements have counts of 3 and 2, then it is a full house
def is_fullhouse(h):
    h = convert_to_nums(h)
    data = Counter(h)
    a, b = data.most_common(1)[0], data.most_common(2)[-1]
    if a[1] == 3 and b[1] == 2:
        return True, [a[0], b[0]]
    return False, None


# if the first 2 most common elements have counts of 2 and 2 then it is a two pair
def is_twopair(h):
    h = convert_to_nums(h)
    data = Counter(h)
    a, b = data.most_common(1)[0], data.most_common(2)[-1]
    if a[1] == 2 and b[1] == 2:
        return True, sorted([a[0], b[0]], reverse=True) + [x for x in h if x != a[0] and x != b[0]]
    return False, None


#if the first most common element is 2 then it is a pair
# DISCLAIMER: this will return true if the hand is a two pair, but this should not be a conflict because is_twopair is always evaluated and returned first
def is_pair(h):
    h = convert_to_nums(h)
    data = Counter(h)
    a = data.most_common(1)[0]

    if a[1] == 2:
        return True, [a[0]] + sorted([x for x in h if x != a[0]], reverse=True)
    else:
        return False, None


#get the high card
def get_high(h):
    h = convert_to_nums(h)
    return sorted(h, reverse=True)


# categorized a hand based on previous functions
def evaluate_hand(h):
    flag, comp = is_royal(h)
    if flag:
        return "ROYAL FLUSH", comp, 10

    flag, comp = is_straight_flush(h)
    if flag:
        return "STRAIGHT FLUSH", comp, 9

    flag, comp = is_fourofakind(h)
    if flag:
        return "FOUR OF A KIND", comp, 8

    flag, comp = is_fullhouse(h)
    if flag:
        return "FULL HOUSE", comp, 7

    flag, comp = is_flush(h)
    if flag:
        return "FLUSH", comp, 6

    flag, comp = is_seq(h)
    if flag:
        return "STRAIGHT", comp, 5

    flag, comp = is_threeofakind(h)
    if flag:
        return "THREE OF A KIND", comp, 4

    flag, comp = is_twopair(h)
    if flag:
        return "TWO PAIR", comp, 3

    flag, comp = is_pair(h)
    if flag:
        return "PAIR", comp, 2

    return "HIGH CARD", get_high(h), 1


# given a hand of 5 cards, this function evaluates two hands and also deals with ties and edge cases
def compare_hands(h1, h2):
    one, two = evaluate_hand(h1), evaluate_hand(h2)
    if one[2] > two[2]:
        return 'LEFT', one[0], h1, one[2]
    elif one[2] < two[2]:
        return 'RIGHT', two[0], h2, two[2]
    else:
        comp1, comp2 = one[1], two[1]
        for i in range(len(comp1)):
            if comp1[i] > comp2[i]:
                return 'LEFT', one[0], h1, one[2]
            elif comp1[i] < comp2[i]:
                return 'RIGHT', two[0], h2, two[2]
        return "TIE", one[0], h1, one[2]


# given 7 card, choose 5 of them to form the biggest card type
def choose_own_biggest_card(seven_cards):
    all_combinations = list(combinations(seven_cards, 5))
    best_card = list(all_combinations[0])
    best_card_type, _, best_card_value = evaluate_hand(best_card)
    for five_cards in all_combinations[1:]:
        five_cards = list(five_cards)
        result, best_card_type, best_card, best_card_value = compare_hands(best_card, five_cards)
    return Chosen_Card_Info(best_card_type, best_card, best_card_value)






