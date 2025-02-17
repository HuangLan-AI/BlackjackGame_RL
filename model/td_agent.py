import random
import math
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns


class TemporalDifference:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1, lambd=0.9):
        self.env = env
        self.alpha = alpha
        self.max_alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.max_epsilon = epsilon
        self.lambd = lambd

        # Set up Q-table and eligibility trace
        self.Q = np.zeros((10, 17, 13, 2, 2))  # dealer first card, player hand value, true count index, usable Aces, action 
        self.E = np.zeros((10, 17, 13, 2, 2))


    def map_state(self, state):
        """
        Map a state to the corresponding indices for Q-table and eligibility trace.
        """
        dealer_card, player_total, true_count, usable_ace = state

        # Map dealer card (2–11) to 0–9
        dealer_index = dealer_card - 2
        # Map player hand (4–20) to 0–16
        player_index = player_total - 4
        
        # Bin true count 
        true_count_index = self.map_true_count(true_count)

        # Convert boolean to 0 or 1
        usable_ace_index = int(usable_ace)

        return dealer_index, player_index, true_count_index, usable_ace_index


    def map_true_count(self, true_count):
        if true_count < -5:
            true_count_index = 0
        elif true_count > 5:
            true_count_index = 12
        else:
            # Map true count (-5 to 5) to 1–11
            true_count_index = true_count + 6
        return true_count_index
    

    def epsilon_greedy_policy(self, state):
        """
        Epsilon-greedy policy for action selection.
        """
        dealer_index, player_index, true_count_index, usable_ace_index = self.map_state(state)
        if random.random() < self.epsilon:
            # Random action
            return random.choice(self.env.actions)
        else:
            return np.argmax(self.Q[dealer_index, player_index, true_count_index, usable_ace_index, :])
    

    def decay(self, episode, max_episodes):
        """
        Linear decay for learning rate and epsilon.
        """
        self.alpha = max(0, self.max_alpha * (1 - episode / max_episodes))
        self.epsilon = max(0, self.max_epsilon * (1 - episode / max_episodes))


    def train(self, num_episodes, on_policy=True, true_count=0):
        """
        Train the agent using Temporal Difference learning with eligibility traces.
        """
        # Reset environment by default
        self.env.reset()
            
        for episode in tqdm(range(num_episodes)):
            # Apply decay to learning rate and epsilon
            self.decay(episode, num_episodes)

            # Reset and start a new game
            self.E.fill(0)
            # If true count is specified, reset env using true count before each game
            if true_count:
                self.env.reset(true_count=true_count)
            reward, state, winner = self.env.new_game()

            # Skip games that end immediately
            while winner:
                self.env.reset(true_count=true_count)
                reward, state, winner = self.env.new_game()

            while not winner:
                # Map state
                dealer_index, player_index, true_count_index, usable_ace_index = self.map_state(state)
                
                # Select action using epsilon-greedy policy
                action = self.epsilon_greedy_policy(state)
                reward, next_state, winner = self.env.step(action)

                # Compute target
                if winner:
                    target = reward
                else:
                    next_action = self.epsilon_greedy_policy(next_state)
                    next_dealer_index, next_player_index, next_true_count_index, next_usable_ace_index = self.map_state(next_state)

                    if on_policy:
                        target = reward + self.gamma * self.Q[
                            next_dealer_index, next_player_index, next_true_count_index, next_usable_ace_index, next_action
                        ]
                    else:
                        target = reward + self.gamma * np.max(
                            self.Q[next_dealer_index, next_player_index, next_true_count_index, next_usable_ace_index, :]
                        )

                # Compute TD error
                delta = target - self.Q[dealer_index, player_index, true_count_index, usable_ace_index, action]

                # Update eligibility trace
                self.E[dealer_index, player_index, true_count_index, usable_ace_index, action] += 1

                # Update Q-values and decay traces
                self.Q += self.alpha * delta * self.E
                self.E *= self.gamma * self.lambd

                # Update state for the next iteration
                state = next_state


    def get_best_action(self, state):
        """
        Returns the best action for a given state based on the trained Q-values.
        """
        dealer_index, player_index, true_count_index, usable_ace_index = self.map_state(state)
        q_values = self.Q[dealer_index, player_index, true_count_index, usable_ace_index, :]

        # Check if the state-action pair has been trained
        if np.all(q_values == 0):
            # Default action is hit if no Q-values are leanrned
            return 1
        else:
            # Return the action with the highest Q-value
            return np.argmax(q_values)
        

    def plot_q_table(self, true_count, usable_aces):
        """
        Plot Q-table heatmaps for the specified true_count and usable_aces (raw values).
        Two heatmaps are displayed: one for action=0 and another for action=1.
    
        Args:
            true_count (int): true count value.
            usable_aces (bool): usable aces value (True/False).
        """
        # Map raw true_count and usable_aces to indices
        true_count_index = self.map_true_count(true_count)
        usable_ace_index = int(usable_aces)
    
        # Determine player hand range and initialize heatmaps
        if usable_aces:
            # Player hand values 12–20
            player_range = range(12, 21)
        else:
            # Player hand values 4–20
            player_range = range(4, 21)

        action_0_data = np.zeros((len(player_range), 10))
        action_1_data = np.zeros((len(player_range), 10))

        # Populate heatmaps
        for dealer_index in range(10):
            for i, player_value in enumerate(player_range):
                # Adjust for Q-table index
                player_index = player_value - 4
                action_0_data[i, dealer_index] = self.Q[dealer_index, player_index, true_count_index, usable_ace_index, 0]
                action_1_data[i, dealer_index] = self.Q[dealer_index, player_index, true_count_index, usable_ace_index, 1]

        # Reverse Q-table
        action_0_data = np.flipud(action_0_data)
        action_1_data = np.flipud(action_1_data)

        # Determine shared color scale
        vmin = math.floor(min(action_0_data.min(), action_1_data.min()))
        vmax = math.ceil(max(action_0_data.max(), action_1_data.max()))

        # Create heatmaps with Seaborn
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        dealer_labels = [str(i) for i in range(2, 12)]
        player_labels = [str(i) for i in reversed(player_range)]
    
        # Action = 0 Heatmap
        sns.heatmap(action_0_data, annot=True, fmt=".2f", cmap="coolwarm", ax=axes[0],
                    xticklabels=dealer_labels, yticklabels=player_labels, vmin=vmin, vmax=vmax)
        axes[0].set_title(f"Q-Table Heatmap: Action = Stand\n(True Count = {true_count}, Usable Aces = {usable_aces})")
        axes[0].set_xlabel("Dealer Card")
        axes[0].set_ylabel("Player Hand Total Value")
    
        # Action = 1 Heatmap
        sns.heatmap(action_1_data, annot=True, fmt=".2f", cmap="coolwarm", ax=axes[1],
                    xticklabels=dealer_labels, yticklabels=player_labels, vmin=vmin, vmax=vmax)
        axes[1].set_title(f"Q-Table Heatmap: Action = Hit\n(True Count = {true_count}, Usable Aces = {usable_aces})")
        axes[1].set_xlabel("Dealer Card")
        axes[1].set_ylabel("Player Hand Total Value")
    
        # Adjust layout and display
        plt.tight_layout()
        plt.show()


    def plot_policy(self, true_count):
        """
        Plot policy heatmaps for the specified true_count.
        Two heatmaps are displayed: one for usable_aces = False and another for usable_aces = True.
        The plot shows whether to hit (1) or stand (0) based on the Q-values.
    
        Args:
            true_count (int): True count value.
        """
        # Initialize placeholders for policies
        policy_false = []
        policy_true = []
    
        # For usable_aces = False: player hand total is 4–20
        player_range_false = range(4, 21)
        for dealer_index in range(10):
            column_false = []
            for player_total in player_range_false:
                state_false = [dealer_index + 2, player_total, true_count, False]
                action = self.get_best_action(state_false)
                column_false.append(action)
            policy_false.append(column_false)

        # For usable_aces = True: player hand total is 12–20
        player_range_true = range(12, 21)
        for dealer_index in range(10):  # Dealer card: 2–11
            column_true = []
            for player_total in player_range_true:
                state_true = [dealer_index + 2, player_total, true_count, True]
                action = self.get_best_action(state_true)
                column_true.append(action)
            policy_true.append(column_true)
    
        # Convert lists to numpy arrays and flip for proper heatmap orientation
        policy_false = np.flipud(np.array(policy_false).T)
        policy_true = np.flipud(np.array(policy_true).T)

        # Create heatmaps with Seaborn
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        dealer_labels = [str(i) for i in range(2, 12)]
        player_labels_false = [str(i) for i in reversed(player_range_false)]
        player_labels_true = [str(i) for i in reversed(player_range_true)]
    
        # Usable Aces = False Heatmap
        sns.heatmap(policy_false, cmap="coolwarm", cbar=False, annot=False, ax=axes[0],
                    xticklabels=dealer_labels, yticklabels=player_labels_false)
        axes[0].set_title(f"Plot of Policy: True Count = {true_count}\n(Usable Aces = False)")
        axes[0].set_xlabel("Dealer Card")
        axes[0].set_ylabel("Player Hand Total Value")
    
        # Replace annotations with "H" and "S"
        for i in range(policy_false.shape[0]):
            for j in range(policy_false.shape[1]):
                text = "H" if policy_false[i, j] == 1 else "S"
                axes[0].text(j + 0.5, i + 0.5, text, color="black",
                             ha="center", va="center", fontsize=10)
    
        # Usable Aces = True Heatmap
        sns.heatmap(policy_true, cmap="coolwarm", cbar=False, annot=False, ax=axes[1],
                    xticklabels=dealer_labels, yticklabels=player_labels_true)
        axes[1].set_title(f"Plot of Policy: True Count = {true_count}\n(Usable Aces = True)")
        axes[1].set_xlabel("Dealer Card")
        axes[1].set_ylabel("Player Hand Total Value")
    
        # Replace annotations with "H" and "S"
        for i in range(policy_true.shape[0]):
            for j in range(policy_true.shape[1]):
                text = "H" if policy_true[i, j] == 1 else "S"
                axes[1].text(j + 0.5, i + 0.5, text, color="black",
                             ha="center", va="center", fontsize=10)
    
        # Adjust layout and display
        plt.tight_layout()
        plt.show()