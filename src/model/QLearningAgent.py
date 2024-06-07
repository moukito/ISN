import os
import pickle
import numpy as np


class QLearningAgent:
    def __init__(
        self,
        actions,
        learning_rate=0.01,
        discount_factor=0.9,
        exploration_rate=0.1,
        q_load=None,
        q_state=None,
    ):
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        if q_state is None:
            self.q_state = "qstate.pkl"
            if os.path.isfile(self.q_state):
                self.states = self.load_state(self.q_state)
            else:
                self.states = list()
        else:
            self.states = self.load_state(q_state)
            self.q_state = q_state

        if q_load is None:
            self.q_load = "qtable.npy"
            if os.path.isfile(self.q_load):
                self.q_table = self.load_table(self.q_load)
            else:
                self.q_table = np.zeros((0, len(actions)))
        else:
            self.q_table = self.load_table(q_load)
            self.q_load = q_load

    def save_table(self, path):
        np.save(path, self.q_table)

    @staticmethod
    def load_table(path):
        return np.load(path)

    def save_state(self, path):
        with open(path, "wb") as file:
            pickle.dump(self.states, file)

    @staticmethod
    def load_state(path):
        with open(path, "rb") as file:
            return pickle.load(file)

    def choose_action(self, state):
        if state not in self.states:
            self.add_state(state)
        if np.random.uniform(0, 1) < self.exploration_rate:
            action = np.random.randint(0, len(self.actions))  # Explore action space
        else:
            action = np.argmax(
                self.q_table[self.states.index(state), :]
            )  # Exploit learned values
        return action

    def update_q_table(self, state, action, reward, next_state):
        id_state = self.states.index(state)
        if next_state not in self.states:
            self.add_state(next_state)
        id_next_state = self.states.index(next_state)

        old_value = self.q_table[id_state, action]
        next_max = np.max(self.q_table[id_next_state])

        new_value = self.learning_rate * (
            reward + self.discount_factor * next_max - old_value
        )

        self.q_table[id_state, action] += new_value

    def add_state(self, state):
        self.states.append(state)
        self.q_table = np.vstack([self.q_table, np.zeros((1, len(self.actions)))])
