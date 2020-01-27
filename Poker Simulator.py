#! /usr/bin/env python3

import pandas as pd
import numpy as np 
from copy import deepcopy

SUITS = ["HEARTS", "DIAMONDS", "SPADES", "CLUBS"]

class PokerSimulator:
    def __init__(self, STARTING_HANDS):
        self.starting_hands = STARTING_HANDS
        self.reserved_cards = self.get_reserved_cards()
        self.deck = self.create_deck()
        self.hands = self.deal_hands()
        self.board = []
        
        # for i in range(len(STARTING_HANDS)):
        #     self.hands[i].append(self.deck.pop())
        # for i in range(len(STARTING_HANDS)):
        #     self.hands[i].append(self.deck.pop())


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
        self.win_count = [[] for i in range(len(self.starting_hands))]

        #self.get_reserved_cards()

    def get_reserved_cards(self):
        reserved_cards = []
        for i in self.starting_hands:
            assert type(i) == list or i.strip() == "?"
            if type(i) == list:
                assert len(i) == 2, "Invalid Input"
                reserved_cards += [i[0]] if type(i[0]) == list else []
                reserved_cards += [i[1]] if type(i[0]) == list else []
        return reserved_cards

    def create_deck(self):
        deck = [[(i%13) + 2, SUITS[i//13]] for i in range(52) if [(i%13) + 2, SUITS[i//13]] not in self.reserved_cards]
        np.random.shuffle(deck)
        return deck

    def deal_hands(self):
        hands = self.starting_hands
        for i in range(len(hands)):
            assert hands[i] == "?" or type(hands[i]) == list, "Invalid Input"
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

    def print_card(self, card, end='\n'):
        print(SUITS[card // 13][0] + str(card % 13), end=end)

    def print_hand(self, player):
        self.print_card(self.hands[player][0], end=', ')
        self.print_card(self.hands[player][1], end='\n')

    def print_board(self):
        for i in range(len(self.board)):
            self.print_card(self.board[i], end="\n" if i == len(self.board) - 1 else ", ")

    
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
        next_best = [x for x in sorted(cards, reverse=True) if x not in pairs]
        return sorted(pairs, reverse=True) + next_best[:(5 - len(pairs))] if pairs else None

    def check_high_card(self, cards):
        return self.n_best_cards(cards, 5)

    def n_best_cards(self, cards, n):
        assert len(cards) > n, "Number of cards must be greater than n"
        return [x for x in sorted(cards, reverse=True)[:n]]

    def find_duplicates(self, hand):
        #print(hand)
        assert len(set(map(tuple, hand))) == 7, "FUCK"

STARTING_HANDS = [
    [
        [7, "HEARTS"], [2, "SPADES"]
    ]
]

NUMBER_OF_GAMES = 25000

outcomes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
wins = [[] for i in range(len(STARTING_HANDS))]

for x in range(NUMBER_OF_GAMES):
    sim = PokerSimulator(deepcopy(STARTING_HANDS))
    sim.flop()
    sim.turn_river()
    sim.turn_river()
    for z in range(len(sim.starting_hands)):
        hand = sim.hands[z] + sim.board
        sim.find_duplicates(hand)
        #print(z, hand)
        for i, func in enumerate(sim.checkers):
            outcome = func(sim.hands[z] + sim.board)
            if outcome != None:
                outcomes[i] += 1
                sim.best_hands.append([i, outcome])
                break
    #print(sim.best_hands)

TOTAL_HANDS_DEALT = len(STARTING_HANDS) * NUMBER_OF_GAMES

for i in zip(sim.hand_names, outcomes):
    print("{}: {:.5%}".format(i[0], (i[1] / TOTAL_HANDS_DEALT)))

# print("\n")

