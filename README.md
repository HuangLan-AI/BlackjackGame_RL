# Blackjack with Card Counting and Reinforcement Learning

## Overview

This repository contains a Python implementation of a Blackjack game with card counting using the Hi-Lo system. The game follows the standard Blackjack rules, with the player making a decision to either "hit" or "stand." The game also incorporates a simple reinforcement learning (RL) agent that decides the best action based on the current game state, which includes both the player's and dealer's hands as well as the true count. The agent adjusts its betting strategy according to the state.
![Blackjack](images/blackjack_bg.png)

The project contains:
1. **Blackjack Game Environment**: Simulates the game according to the defined rules.
2. **Reinforcement Learning Agent**: A basic RL agent trained to optimize its decisions based on the game state and true count.
3. **Card Counting**: Uses the Hi-Lo system to track the running and true counts to influence the player's betting and actions.
4. **Simulation and Evaluation**: The agent is evaluated through simulations to verify its performance.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Game Rules](#game-rules)
4. [Reinforcement Learning](#reinforcement-learning)
5. [Card Counting](#card-counting)
6. [Visualizations](#visualizations)
7. [Evaluation](#evaluation)
8. [License](#license)

## Installation

### Requirements
- Python 3.7 or higher
- `numpy`, `matplotlib`, and other dependencies listed in the `requirements.txt`

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blackjack-game.git
   cd blackjack-game

2. Install the required dependencie:
    ```bash
    pip install -r requirements.txt

## Usage
### Running the Game
To start the Blackjack game and train the reinforcement learning agent, run the following command:
```bash
python blackjack_game.py
```

This will initialize the game and the agent, and the agent will start playing the game, making decisions based on the true count.

### Visualizing Agent Behavior
To visualize how the agent behaves under different true count conditions, use the following command:
```bash
python visualize.p
```

## Game Rules
The game is based on traditional Blackjack rules, with some adjustments for card counting and betting:
- **Card Values**: Number cards count as their face value, Jack, Queen, and King count as 10, and Aces can be counted as 1 or 11.
- **Blackjack**: A player total of 21 with the first two cards is a Blackjack. The player wins unless the dealer also has a Blackjack, in which case a tie occurs.
- **Dealer Behavior**: The dealer must draw cards if their hand value is a soft 17 (includes an Ace) or hard 16 or lower.
- **Hi-Lo Counting System**: Cards are counted as:
    - +1 for low cards (2, 3, 4, 5, 6)
    - 0 for neutral cards (7, 8, 9)
    - -1 for high cards (10, Jack, Queen, King, Ace)
- Bets: A large bet (20x minimum) is made when the true count is +2 or higher, and a small bet (1x minimum) is made otherwise.

## Reinforcement Learning
The reinforcement learning agent is trained to make decisions (either "hit" or "stand") based on the current game state. The agent's decisions are influenced by:
- The total value of the player's hand.
- The total value of the dealer's hand.
- The true count, which indicates the remaining deck's favorability.
- Wether have usable Aces.
The agent is trained using Q-learning or another RL algorithm to maximize the expected return based on its actions.

### Training the Agent
The agent updates its Q-values after each action (hit or stand), using the rewards from the environment (win, loss, tie, or Blackjack). The agent adjusts its strategy based on the true count, making larger bets when the count is favorable and playing more conservatively when the count is unfavorable.

## Card Counting
Card counting is implemented using the Hi-Lo system:
- Low cards (2-6) increase the running count by +1.
- Neutral cards (7-9) have no effect on the running count.
- High cards (10, Jack, Queen, King, Ace) decrease the running count by -1.
The running count is then divided by the number of remaining decks to calculate the true count. This value influences the agent’s betting and decision-making.

## Visualisation
The agent's behavior under different true count conditions is visualized to demonstrate how it adapts to favorable and unfavorable deck compositions.

## Evaluation
The agent's performance is evaluated through 10,000 simulations of 600 games each. The agent’s performance is analyzed under different true counts:
- **True Count +2**: The agent is expected to have a statistical advantage over the house.
- **True Count -2**: The agent is expected to be more conservative, with the house having a slight advantage.
The agent’s expected return is calculated and compared with theoretical expectations to determine if the agent is consistently performing as expected.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


