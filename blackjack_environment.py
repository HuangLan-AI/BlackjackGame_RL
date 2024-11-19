import random
import numpy as np
from copy import deepcopy
from tqdm import tqdm


class Cards:
    def __init__(self, num_of_decks):
        self.cards_remain = []
        self.cards_dealt = []
        self.num_of_decks = num_of_decks
        self.running_count = 0
        self.true_count = 0

        self.reset()
    

    def reset(self, true_count=0):
        """
        Reset the deck. If `true_count` is specified, simulate a specific state; 
        otherwise, initialize full shuffled decks.

        Args:
        - true_count (int): The desired true count for the simulated game state.

        Raises:
        - ValueError: If the recalculated true count does not match the given true_count.
        """
        # If true count is not specified, create decks and shuffle them
        if true_count == 0:
            self.cards_remain = self.initialize_cards()
            self.cards_dealt = []
            self.running_count = 0
            self.true_count = 0
        else:
            self.running_count, self.cards_remain, self.cards_dealt = self.simulate_true_count(true_count=true_count)
            # Recalculate the true count
            self.update_true_count()
            # Assert that self.true_count matches the provided true_count
            if self.true_count != true_count:
                raise ValueError(
                    f"Mismatch in true_count: expected {true_count}, but got {self.true_count}"
                )
    

    def initialize_cards(self):
        """
        Create and shuffle the cards for the given number of decks.
        """
        # Create 1 deck of cards
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = cards * 4
        # Create decks of cards based on num_of_decks
        decks = deck * self.num_of_decks
        # Shuffle them
        random.shuffle(decks)
        return decks
    

    def simulate_true_count(self, true_count):
        """
        Simulate the cards dealt and remaining cards to achieve a specific true count.

        Args:
        - true_count (int): The desired true count for the simulation.

        Returns:
        - running_count (int): The current Hi-Lo running count.
        - cards_remain (list): The list of cards left in the deck(s).
        - cards_dealt (list): The list of cards already dealt.
        """
        # Initialize low cards, neutral cards and high cards
        low_cards = ['2', '3', '4', '5', '6'] * 4 * self.num_of_decks
        neutral_cards = ['7', '8', '9'] * 4 * self.num_of_decks
        high_cards = ['10', 'J', 'Q', 'K', 'A'] * 4 * self.num_of_decks
        random.shuffle(low_cards)
        random.shuffle(neutral_cards)
        random.shuffle(high_cards)

        # Randomly choose number of decks remain between 2 to 5 inclusive
        deck_remain = random.randint(2, 5)
        # calculate number of cards requried to deal and running count
        num_cards_dealt = (self.num_of_decks - deck_remain) * 52    
        running_count = true_count * deck_remain  

        cards_dealt = []
        # If true count is non-negative, number of low cards required = running count
        if true_count >= 0:
            cards_dealt += self.deal_cards(low_cards, running_count)
        # Else, number of high cards required = absolute value of running count
        else:
            cards_dealt += self.deal_cards(high_cards, abs(running_count))

        # Deal remaining cards to match num_cards_dealt
        remaining_to_deal = num_cards_dealt - abs(running_count)
        while remaining_to_deal > 0:
            # If all nuetral cards are dealt, then take 1 card from each of low and high cards to make sure the count doesn't change
            if len(neutral_cards) == 0:
                cards_dealt += self.deal_cards(low_cards, 1)
                cards_dealt += self.deal_cards(high_cards, 1)
                remaining_to_deal -= 2
            # Else if all low or high cards are dealt, then take 1 card from nuetral card so that count doesn't change
            elif min(len(low_cards), len(high_cards)) == 0:
                cards_dealt += self.deal_cards(neutral_cards, 1)
                remaining_to_deal -= 1
            # Else, choose randomly from the two methods
            else:
                if random.random() <= 0.5:
                    cards_dealt += self.deal_cards(neutral_cards, 1)
                    remaining_to_deal -= 1
                else:
                    cards_dealt += self.deal_cards(low_cards, 1)
                    cards_dealt += self.deal_cards(high_cards, 1)
                    remaining_to_deal -= 2

        # Get cards remaining
        cards_remain = low_cards + neutral_cards + high_cards
        random.shuffle(cards_remain)
        
        return running_count, cards_remain, cards_dealt
    

    def deal_cards(self, card_pool, num_of_cards):
        """
        Helper function to deal a specified number of cards from a card pool.

        Args:
        - card_pool (list): The list of available cards to deal from.
        - num_of_cards (int): The number of cards to deal.

        Returns:
        - List of dealt cards.
        """
        dealt_cards = []
        for _ in range(num_of_cards):
            if card_pool:
                dealt_cards.append(card_pool.pop())
        return dealt_cards


    def update_running_count(self, card):
        """
        Update the running count based on the card drawn.
        """
        if card in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif card in ['10', 'J', 'Q', 'K', 'A']:
            self.running_count -= 1

    
    def update_true_count(self):
        """
        Update the true count based on the running count and remaining cards.
        """
        # True count = intermediate count / the number of remaining decks
        decks_remain = round(len(self.cards_remain) / 52, 1)
        self.true_count = round(self.running_count / decks_remain, 1)
    

    def draw_card(self):
        """
        Draw a card from the remaining cards and update the counts.
        """   
        # Draw a card from the end of list
        card = self.cards_remain.pop() 
        # Update running count and true count
        self.update_running_count(card)
        self.update_true_count()
        return card
      



class BlackjackGame:
    def __init__(self, CardsEnv):
        self.total_decks = 6
        self.cards_env = CardsEnv(num_of_decks=self.total_decks)
        self.dealer_hand = []
        self.player_hand = []

        # State: player hand value, dealer hand value, true count, available Aces in player hand
        self.state = [0, 0, 0, False]
        # Action: 0 for stand and 1 for hit
        self.actions = [0, 1]

        self.reset()


    def reset(self, true_count=0):
        """
        Reset the game state. If a specific true count is provided, reset the deck and state
        based on that true count; otherwise, reset to a default state with shuffled decks.

        Args:
        - true_count (int): Desired true count for the reset (default is 0).
        """
        self.cards_env.reset(true_count=true_count)
        self.dealer_hand = []
        self.player_hand = []
        self.bet = 0
        self.winner = None

        # Reset state based on true count
        if true_count == 0:
            # Default state: empty hands, true count=0, no available Ace
            self.state = [0, 0, 0, False]
        else:
            # State with specified true count
            self.state = [0, 0, self.cards_env.true_count, False]



