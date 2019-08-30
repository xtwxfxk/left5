import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F



class ActorCritic(torch.nn.Module):
    def __init__(self, channels, memsize, action_num):
        super(ActorCritic, self).__init__()
        self.conv1 = nn.Conv2d(channels, 32, 3, stride=2, padding=1) # b c 40 40
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 32, 3, stride=2, padding=1) # b 32 20 20
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, 3, stride=2, padding=1) # b 32 10 10
        self.bn3 = nn.BatchNorm2d(32)
        self.conv4 = nn.Conv2d(32, 32, 3, stride=2, padding=1) # b 32 5 5
        self.bn4 = nn.BatchNorm2d(32)

        self.gru = nn.GRUCell(32 * 5 * 5, memsize)

        self.critic_linear = nn.Linear(memsize, 1)
        self.actor_linear = nn.Linear(memsize, action_num)


    def forward(self, inputs):
        x, hx = inputs
        x = F.elu(self.bn1(self.conv1(x)))
        x = F.elu(self.bn2(self.conv2(x)))
        x = F.elu(self.bn3(self.conv3(x)))
        x = F.elu(self.bn4(self.conv4(x)))

        hx = self.gru(x.view(-1, 32 * 5 * 5), hx)

        return self.critic_linear(hx), self.actor_linear(hx), hx
