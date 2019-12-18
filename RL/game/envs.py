import cv2
import gym
import numpy as np

from ple.games.flappybird import FlappyBird
from ple.games.monsterkong import MonsterKong
from ple import PLE


def create_env():
    return FlappyBirdEnv()

class FlappyBirdEnv(object):

    def __init__(self):
        self.game = FlappyBird()
        self.p = PLE(self.game, fps=30, display_screen=True)

        # self.actions = self.p.getActionSet()
        # self._action_space = list(range(self.actions[0]))
        # self._action_space.append(self.actions[-1])
        self.action_space = self.p.getActionSet()

    def reset(self):
        self.p.init()
        self.p.act(None)
        # return self.p.getScreenRGB()
        return self.p.getScreenGrayscale()

    def step(self, action):
        reward = self.p.act(self.action_space[action])
        # reward = self.p.act(119)
        # print(self.action_space[action], reward)
        # return self.p.getScreenRGB(), reward, self.p.game_over()
        return self.p.getScreenGrayscale(), reward, self.p.game_over()

    @property
    def action_space(self):
        return self._action_space

    @action_space.setter
    def action_space(self, action_space):
        self._action_space = action_space



class MonsterKongEnv(object):

    def __init__(self):
        self.game = MonsterKong()
        self.p = PLE(self.game, fps=30, display_screen=True)

        # self.actions = self.p.getActionSet()
        # self._action_space = list(range(self.actions[0]))
        # self._action_space.append(self.actions[-1])
        self.action_space = self.p.getActionSet()

    def reset(self):
        self.p.init()
        self.p.act(None)
        # return self.p.getScreenRGB()
        return self.p.getScreenGrayscale()

    def step(self, action):
        reward = self.p.act(self.action_space[action])
        # reward = self.p.act(119)
        # print(self.action_space[action], reward)
        # return self.p.getScreenRGB(), reward, self.p.game_over()
        return self.p.getScreenGrayscale(), reward, self.p.game_over()

    @property
    def action_space(self):
        return self._action_space

    @action_space.setter
    def action_space(self, action_space):
        self._action_space = action_space