#! /usr/bin/env python3

import pandas as pd
import numpy as np 
from copy import deepcopy
import collections

SUITS = ["HEARTS", "DIAMONDS", "SPADES", "CLUBS"]

class PokerSimulator:
    def __init__(self, STARTING_HANDS):
        self.starting_hands = STARTING_HANDS
        self.reserved_cards = self.get_reserved_cards()
        self.deck = self.create_deck()
        self.hands = self.deal_hands()
        self.board = []

        self.checkers = [
            self.check_royal_flush, 
            self.check_straight_flush, 
            self.check_four_of_a_kind, 
            self.check_full_house, 
            self.check_flush, 
            self.check_straight, 
            self.check_three_of_a_kind, 
            self.check_two_pair, 
            self.check_pair,
            self.check_high_card
        ]
        self.hand_names = [
            "Royal Flush",
            "Straight Flush", 
            "Four or a Kind",
            "Full House",
            "Flush",
            "Straight",
            "Three of a Kind",
            "Two Pair",
            "Pair",
            "High Card"
        ]
        self.best_hands = []

        self.hand_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        #self.get_reserved_cards()

    def get_reserved_cards(self):
        reserved_cards = []
        for i in self.starting_hands:
            assert type(i) == list or i.strip() == "?", "Invalid Input"
            if type(i) == list:
                assert len(i) == 2, "{} {}".format(i, len(i))
                reserved_cards += [i[0]] if type(i[0]) == list else []
                reserved_cards += [i[1]] if type(i[0]) == list else []
        return reserved_cards
        

    def create_deck(self):
        deck = [[(i%13) + 2, SUITS[i//13]] for i in range(52) if [(i%13) + 2, SUITS[i//13]] not in self.reserved_cards]
        np.random.shuffle(deck)
        return deck
        #self.deal_hands()

    def deal_hands(self):
        hands = self.starting_hands
        for i in range(len(hands)):
            if type(hands[i]) == str and hands[i].strip() == "?":
                hands[i] = [self.deck.pop(), self.deck.pop()]
            elif type(hands[i]) == list:
                hands[i][0] = self.deck.pop() if hands[i][0] == "?" else hands[i][0]
                hands[i][1] = self.deck.pop() if hands[i][1] == "?" else hands[i][1]
        return hands

    def flop(self):
        self.deck.pop()
        for i in range(3):
            self.board.append(self.deck.pop())

    def turn_river(self):
        self.deck.pop()
        self.board.append(self.deck.pop())

    def combine_board_and_hands(self):
        self.hands = [hand + sim.board for hand in self.hands]
    
    def check_royal_flush(self, cards):
        straight_flush = self.check_straight_flush(cards)
        return straight_flush if bool(straight_flush) and straight_flush[0][0] == 14 else None

    def check_straight_flush(self, cards):
        straight = self.check_straight(cards) 
        flush = self.check_flush(cards)
        if straight == None or flush == None:
            return None
        else:
            hand = sorted([z for z in cards if z[1] == flush[0][1]])
            return self.check_straight(hand)

            
    def check_four_of_a_kind(self, cards):
        hand = [z[0] for z in sorted(cards, reverse=True)]
        quads = [sorted(cards, reverse=True)[i] for i in range(len(hand)) if hand.count(hand[i]) == 4]
        next_best = [x for x in sorted(cards, reverse=True) if x not in quads]
        return sorted(quads, reverse=True) + [next_best[0]] if quads else None

    def check_full_house(self, cards):
        if self.check_three_of_a_kind(cards) != None:
            if self.check_pair(cards) != None:
                return self.check_three_of_a_kind(cards)[:3] + self.check_pair(cards)[:2]

    def check_flush(self, cards):
        hand = [z[1] for z in cards] #self.hands[player] + self.board]
        for i in SUITS:
            if hand.count(i) >= 5:
                return sorted([x for x in cards if x[1] == i], reverse=True)[:5]
        return None

    def check_straight(self, cards):
        hand = [z[0] for z in cards] 

        straight = []
        for i in reversed(range(15)):
            straight = straight + [cards[hand.index(i)]] if i in hand else []
            if len(straight) == 5:
                return sorted(straight, reverse=True)

        if 14 in hand:
            cards = [[1, d[1]] if d[0] == 14 else d for d in cards]
            return self.check_straight(cards)

        return None

    def check_three_of_a_kind(self, cards):
        hand = [z[0] for z in sorted(cards, reverse=True)]
        trios = [sorted(cards, reverse=True)[i] for i in range(len(hand)) if hand.count(hand[i]) == 3][:3]
        next_best = [x for x in sorted(cards, reverse=True) if x not in trios]
        return sorted(trios, reverse=True) + next_best[:2] if trios else None

    def check_two_pair(self, cards):
        hand = self.check_pair(cards)
        if hand:
            return hand if len(set([z[0] for z in hand])) == 3 else None
        return None

    def check_pair(self, cards):
        hand = [z[0] for z in sorted(cards, reverse=True)]
        pairs = [sorted(cards, reverse=True)[i] for i in range(len(hand)) if hand.count(hand[i]) == 2][:4]
        next_best = sorted([x for x in cards if x not in pairs], reverse=True)
        #sorted(pairs + next_best[:3], reverse=True))
        return sorted(pairs, reverse=True) + next_best[:5 - len(pairs)] if pairs else None

    def check_high_card(self, cards, n=5):
        return self.n_best_cards(cards, n)

    def n_best_cards(self, cards, n):
        assert len(cards) >= n, "Number of cards must be greater than n"
        return [x for x in sorted(cards, reverse=True)[:n]]

    def find_duplicates(self, hand):
        assert len(set(map(tuple, hand))) == 7, "FUCK"

    def highest_card(self, tying_players, s=0, f=5):
        high_cards = []
        for i in [self.best_hands[i][1][s:f] for i in tying_players]:
            high_cards.append([q[0] for q in i])
        
        in_ = None
        for i, f in enumerate(zip(*high_cards)):
            high = max(f)
            in_ = [1 if j == high else 0 for j in f] if in_ == None else [1 if f[z] == high and in_[z] == 1 else 0 for z in range(len(f))]
            if collections.Counter(in_)[1] == 1:
                return in_.index(1)
            #print(f, high, in_, counter[1])
        # counter = collections.Counter(in_)
        return [x for x in range(len(in_)) if in_[x] == 1] if collections.Counter(in_)[1] > 1 else in_.index(1)

    def determine_winner(self):
        # test = [[[10, 'HEARTS'], [10, 'CLUBS'], [8, 'HEARTS'], [8, 'CLUBS'], [11, 'DIAMONDS']], [[11, 'DIAMONDS'], [10, 'CLUBS'], [9, 'HEARTS'], [8, 'HEARTS'], [7, 'CLUBS']]]
        # self.best_hands[0][1] = test[0]
        # self.best_hands[1][1] = test[1]

        #print(sim.best_hands)
        outcomes = [z[0] for z in sim.best_hands]
        counter = collections.Counter(outcomes)
        best_hand = min(outcomes)
        #print(counter[best_hand])
        #print(sim.hands)
        #print(sim.best_hands)
        if counter[best_hand] == 1:
            return outcomes.index(best_hand)
        else:
            #Breaking Ties
            tying_players = [i for i in range(len(outcomes)) if outcomes[i] == best_hand]
            #If there are ever two or more royal flushes
            if best_hand == 0:
                return tying_players
            #Two or more straight flushes
            elif best_hand == 1:
                return self.highest_card(tying_players, 0, 5)
            #two or more four of a kinds
            elif best_hand == 2:
                return self.highest_card(tying_players, 0, 4)
            #two or more full houses
            elif best_hand == 3:
                finisher = self.highest_card(tying_players,0, 3)
                return finisher if type(finisher) == int else self.highest_card(tying_players, 3, 5)
            #twp or more flushes
            elif best_hand == 4:
                return self.highest_card(tying_players, 0, 5)
            #two or more straights
            elif best_hand == 5:
                return self.highest_card(tying_players, 0, 5)
            #two or more three of a kinds
            elif best_hand == 6:
                finisher = self.highest_card(tying_players, s=0, f=3)
                assert type(finisher) == list or type(finisher) == int, "Error"
                return finisher if type(finisher) == int else self.highest_card(tying_players, 3, 5)
            #two or more two pairs
            elif best_hand == 7:
                finisher = self.highest_card(tying_players, s=0, f=4)
                assert type(finisher) == list or type(finisher) == int, "Error"
                return finisher if type(finisher) == int else self.highest_card(tying_players, 4, 5)
            #two or more pairs
            elif best_hand == 8:
                finisher = self.highest_card(tying_players, s=0, f=2)
                assert type(finisher) == list or type(finisher) == int, "Error"
                return finisher if type(finisher) == int else self.highest_card(tying_players, 2, 5)
            elif best_hand == 9:
                return self.highest_card(tying_players, s=0, f=5)
                # high = max([d[1][0][0] for d in self.best_hands])
                # winners = [i for i in tying_players if sim.best_hands[i][1][0][0] == high]
                # if len(winners) == 1:
                #     return winners[0]
                # else:
                #     return self.highest_card(tying_players, s=2)
                    # high_cards = []
                    # for i in [self.best_hands[i][1][2:] for i in tying_players]:
                    #     high_cards.append([q[0] for q in i])
                    
                    # in_ = None
                    # for i, f in enumerate(zip(*high_cards)):
                    #     high = max(f)
                    #     in_ = [1 if j == high else 0 for j in f] if in_ == None else [1 if f[j] == high and in_[j] == 1 else 0 for j in range(len(f))]
                    # counter = collections.Counter(in_)
                    # return [x for x in in_ if x == 1] if counter[1] > 1 else in_.index(1)

STARTING_HANDS = [
    [
        [5, "HEARTS"], [5, "CLUBS"]
    ], 
    [
        "?", "?"
    ]
]

from time import time
STARTING_TIME = time()

NUMBER_OF_PLAYERS = len(STARTING_HANDS)

NUMBER_OF_GAMES = 50000

outcomes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
win_count = [0 for i in STARTING_HANDS]


for x in range(NUMBER_OF_GAMES):
    sim = PokerSimulator(deepcopy(STARTING_HANDS))
    sim.flop()
    sim.turn_river()
    sim.turn_river()
    sim.combine_board_and_hands()

    for z in range(len(sim.starting_hands)):
        hand = sim.hands[z]
        #sim.find_duplicates(hand)
        for i, func in enumerate(sim.checkers):
            outcome = func(hand)
            if outcome != None:
                outcomes[i] += 1
                sim.best_hands.append([i, outcome])
                break
    
    winner = sim.determine_winner()
    if type(winner) == int:
        win_count[winner] += 1

TOTAL_HANDS_DEALT = NUMBER_OF_PLAYERS * NUMBER_OF_GAMES

for i in zip(sim.hand_names, outcomes):
    print("{}: {:.5%}".format(i[0], (i[1] / TOTAL_HANDS_DEALT)))

WIN_PERCENTAGE = ["{:.5%}".format(x/NUMBER_OF_GAMES) for x in win_count]

HANDS = [STARTING_HANDS[i] if len(STARTING_HANDS) > i else None for i in range(8)]
log = '{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(NUMBER_OF_PLAYERS, NUMBER_OF_GAMES, win_count[0] / NUMBER_OF_GAMES, win_count[1] / NUMBER_OF_GAMES, *HANDS)
with open("results.txt", "a") as fh:
    fh.write(log + "\n")

print(time() - STARTING_TIME)

# print("\n")

