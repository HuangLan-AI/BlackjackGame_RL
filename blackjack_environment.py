import random
import numpy as np
from copy import deepcopy
from tqdm import tqdm


class Cards:
    def __init__(self, num_of_decks=6):
        self.cards_remain = []
        self.cards_dealt = []
        self.num_of_decks = num_of_decks
        self.min_num_of_cards = 52 * self.num_of_decks * 0.25
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
            self.initialize_cards()
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
        
        self.cards_remain = decks
        self.cards_dealt = []
        self.running_count = 0
        self.true_count = 0
    

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
        self.true_count = round(self.running_count / decks_remain)
    

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

        # State: dealer hand value, player hand value, true count, usable Aces in player hand
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


    def get_hand_value(self, hand):
        """
        Calculate the value of a hand.

        Args:
        - hand (list): List of cards in a hand.

        Returns:
        - value (int): hand value.
        - usable_aces (bool): True if have at least one Ace valued at 1.
        """
        value = 0
        aces_value = []

        for card in hand:
            if card in ['J', 'Q', 'K']:
                value += 10
            elif card == 'A':
                # Try to value the Ace at 11
                value += 11
                aces_value.append(11)
            else:
                # For the rest of cards from 2 to 10
                value += int(card)

        # Adjust for multiple Aces if the value exceeds 21
        while value > 21 and 11 in aces_value:
            # Convert one Ace from 11 to 1
            value -= 10
            aces_value[aces_value.index(11)] = 1
        
        return value, aces_value
    

    def deal_initial_hands(self):
        """
        Deal 3 cards to player and dealer at the begining of each game.
        """
        # Deal two faced-up cards to player and one faced-up card to dealer alternatively
        self.player_hand.append(self.cards_env.draw_card())
        self.dealer_hand.append(self.cards_env.draw_card())
        self.player_hand.append(self.cards_env.draw_card())

        # Update state
        dealer_hand_value, _ = self.get_hand_value(self.dealer_hand)
        player_hand_value, aces_value = self.get_hand_value(self.player_hand)
        usable_aces = 1 in aces_value
        self.state[0] = dealer_hand_value
        self.state[1] = player_hand_value
        self.state[2] = self.cards_env.true_count
        self.state[3] = usable_aces


    def dealer_play(self):
        """
        Dealer's turn to play according to the rules.
        """
        hand_value, aces_value = self.get_hand_value(self.dealer_hand)
        # Check soft 17
        soft = 11 in aces_value
        soft_17 = (hand_value == 17) and soft
        
        # Dealer draws if soft 17 or below
        while hand_value < 17 or soft_17:
            self.dealer_hand.append(self.cards_env.draw_card())
            hand_value, aces_value = self.get_hand_value(self.dealer_hand)
            soft = 11 in aces_value
            soft_17 = (hand_value == 17) and soft

        return hand_value
    

    def player_hit(self):
        """
        Player chooses to hit.
        """
        self.player_hand.append(self.cards_env.draw_card())
        player_hand_value, aces_value = self.get_hand_value(self.player_hand)
        usable_aces = 1 in aces_value

        return player_hand_value, usable_aces


    def check_blackjack(self):
        """
        Check if player has blackjack and update self.winner.
        """
        # Check if player hand value is 21
        player_bj = self.get_hand_value(self.player_hand) == 21

        if player_bj:
            if self.dealer_hand[0] in ['10', 'J', 'Q', 'K', 'A']:
                # If dealer has a chance to get blackjack, draw a card
                self.dealer_hand.append(self.cards_env.draw_card())
                dealer_hand_value, _ = self.get_hand_value(self.dealer_hand)
                # Player wins unless dealer also has a blackjack, in which case a tie occurs
                self.winner = 'tie' if dealer_hand_value == 21 else 'blackjack'
            else:
                # If dealer doesn't have a chance to get blackjack, player wins
                self.winner = 'blackjack'
        else:
            # If player doesn't have a blackjack, game continues
            self.winner = None
    

    def check_winner(self):
        """
        Check the result of the game.
        """
        if len(self.player_hand) == 2:
            # Check blackjack after initial cards dealt
            self.check_blackjack()
            return self.winner
        else:
            # Get hand values
            dealer_hand_value, _ = self.get_hand_value(self.dealer_hand)
            player_hand_value, _ = self.get_hand_value(self.player_hand)
            
            # Check bust of player
            if player_hand_value > 21:
                self.winner = 'dealer'
                return self.winner

            # Check bust of dealer
            if dealer_hand_value > 21:
                self.winner = 'player'
                return self.winner

            # Compare two hand values if no one busts
            if player_hand_value > dealer_hand_value:
                self.winner = 'player'
            elif player_hand_value < dealer_hand_value:
                self.winner = 'dealer'
            else:
                # If both dealer and player have the same value, check if dealer has blackjack
                if dealer_hand_value == 21 and len(self.dealer_hand) == 2:
                    self.winner = 'dealer'
                else:
                    self.winner = 'tie'
            return self.winner
    

    def place_bet(self):
        """
        Place a bet based on the true count
        """
        if self.true_count >= 2:
            # Large bet
            self.bet = 20
        else:
            # Small bet
            self.bet = 1
    

    def clearing(self):
        """
        Calculate the rewared based on winner.
        """
        if self.winner == 'dealer':
            reward = -1 * self.bet
        elif self.winner == 'player':
            reward = self.bet
        elif self.winner == 'blackjack':
            reward = 1.5 * self.bet
        else:
            reward = 0
        return reward
    

    def new_game(self):
        """
        Start a new game on the same table.
        The Hi-Lo counting system continues from the last game unless shuffle cards.
        Return reward, current state and winner.
        """
        # Shuffle cards if 75% of cards have been dealt
        if len(self.cards) <= self.min_num_of_cards:
            self.cards_env.initialize_cards()
        
        # Reset hands, state
        self.dealer_hand = []
        self.player_hand = []
        self.winner = None
        self.state = [0, 0, self.cards_env.true_count, False]

        # Place bet
        self.place_bet()

        # Deal initial cards
        self.deal_initial_hands()
        
        # Check blackjack
        self.check_winner()
        reward = self.clearing()
            
        return reward, self.state, self.winner
    

    def step(self, state, action):
        """
        Player takes an action, hit or stand.
        Return reward, next state and winner
        """
        next_state = state.copy()
        
        if action == 1:
            # If player choose hit
            player_hand_value, usable_aces = self.player_hit()
            next_state[1] = player_hand_value
            next_state[2] = self.cards_env.true_count
            next_state[3] = usable_aces

            if player_hand_value > 21:
                # If player busts, dealer wins
                self.winner = 'dealer'
                reward = self.clearing()
            elif player_hand_value == 21:
                # If player get 21, dealer plays
                dealer_hand_value = self.dealer_play()
                next_state[0] = dealer_hand_value
                next_state[2] = self.cards_env.true_count_bin
                self.check_winner()
                reward = self.clearing()
            else:
                # If player hand is less than 21, continue
                self.winner = None
                reward = 0

        elif action == 0:
            # If player choose stand
            dealer_hand_value = self.dealer_play()
            next_state[0] = dealer_hand_value
            next_state[2] = self.cards_env.true_count
            self.check_winner()
            reward = self.clearing()

        else:
            # Invalid action
            assert False, "Invalid action"

        self.state = next_state
        
        return reward, next_state, self.winner

