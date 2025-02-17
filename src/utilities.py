import os
import numpy as np
from tqdm import tqdm


def test_td_model(agent, env, num_test_games=10000, true_count=2):
    """
    Test the TemporalDifference agent in the given environment.

    Args:
        agent (TemporalDifference): The trained agent to test.
        env (BlackjackGame): The environment to test the agent on.
        num_test_games (int): Number of test games to evaluate.
        true_count (int): True count to reset the environment to.

    Returns:
        dict: A dictionary containing the test results.
    """
    wins = 0
    losses = 0
    ties = 0
    blackjack_count = 0
    total_reward = 0

    for _ in tqdm(range(num_test_games), desc="Testing Games"):
        env.reset(true_count=true_count)
        game_reward, state, winner = env.new_game()  # Start a new game

        while not winner:
            # Get the best action based on the trained model
            action = agent.get_best_action(state)

            # Take the action in the environment
            reward, next_state, winner = env.step(action)

            # Accumulate reward for the current game
            game_reward += reward

            # Update the state
            state = next_state

        # Track total reward
        total_reward += game_reward

        # Record the outcome
        if winner == 'player':
            wins += 1
        elif winner == 'blackjack':
            wins += 1
            blackjack_count += 1
        elif winner == 'dealer':
            losses += 1
        else:  # Tie
            ties += 1

    # Compute performance metrics
    win_rate = wins / num_test_games
    loss_rate = losses / num_test_games
    tie_rate = ties / num_test_games
    average_reward = total_reward / num_test_games
    blackjack_rate = blackjack_count / num_test_games

    # Return results as a dictionary
    return {
        "win_rate": win_rate,
        "loss_rate": loss_rate,
        "tie_rate": tie_rate,
        "blackjack_rate": blackjack_rate,
        "total_reward": total_reward,
        "average_reward": average_reward
    }


def save_td_model(q_table, file_path):
    """
    Save the Q-table to a file.

    Args:
        q_table (np.ndarray): The Q-table to save.
        file_path (str): File path to save the Q-table.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Save the Q-table
    np.save(file_path, q_table)
    print(f"TD model is saved to {file_path}.")


def load_q_table(file_path):
    """
    Load the Q-table from a file.

    Args:
        file_path (str): File path to load the Q-table from.
    
    Returns:
        np.ndarray: The loaded Q-table.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Load and return the Q-table
    q_table = np.load(file_path)
    print(f"TD model is loaded from {file_path}.")
    return q_table


def test_ppo_model(agent, env, num_test_games=10000, true_count=2):
    """
    Test the PPO agent in the given environment.

    Args:
        agent (PPO): The trained agent to test.
        env (BlackjackGameGym): The environment to test the agent on.
        num_test_games (int): Number of test games to evaluate.
        true_count (int): True count to reset the environment to.

    Returns:
        dict: A dictionary containing the test results.
    """
    total_rewards = []
    win_count = 0
    loss_count = 0
    tie_count = 0

    for episode in range(num_test_games):
        env.initialize(true_count=true_count)  # Set initial true count
        obs, info = env.reset()  # Reset the environment

        done = False
        episode_reward = 0

        while not done:
            action, _ = agent.predict(obs, deterministic=True)  # Predict action
            obs, reward, done, truncated, info = env.step(action)  # Step the environment
            episode_reward += reward  # Accumulate reward

        total_rewards.append(episode_reward)

        # Track win/loss/tie counts
        if episode_reward > 0:
            win_count += 1
        elif episode_reward < 0:
            loss_count += 1
        else:
            tie_count += 1

    # Compute statistics
    average_reward = np.mean(total_rewards)
    win_rate = win_count / num_test_games
    loss_rate = loss_count / num_test_games
    tie_rate = tie_count / num_test_games

    # Print results
    print(f"Average Reward over {num_test_games} episodes: {average_reward:.2f}")
    print(f"Win Rate: {win_rate * 100:.2f}%")
    print(f"Loss Rate: {loss_rate * 100:.2f}%")
    print(f"Tie Rate: {tie_rate * 100:.2f}%")

    # Return results as a dictionary
    return {
        "average_reward": average_reward,
        "win_rate": win_rate,
        "loss_rate": loss_rate,
        "tie_rate": tie_rate
    }