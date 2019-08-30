import time
import torch
import torch.nn.functional as F
import torch.optim as optim
import cv2
from envs import create_env
from model import ActorCritic
import numpy as np
from PIL import Image

# prepro = lambda img: cv2.resize(img, (80,80), interpolation=cv2.INTER_AREA).astype(np.float32).transpose(2, 0, 1)/255.
prepro = lambda img: cv2.resize(img, (80,80)).astype(np.float32)/255.

def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(),
                                   shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad.cpu()

def train(rank, args, shared_model, optimizer=None):
    torch.manual_seed(args.seed + rank)

    env = create_env()

    model = ActorCritic(1, args.memsize, len(env.action_space)).to(args.device)

    if optimizer is None:
        optimizer = optim.Adam(shared_model.parameters(), lr=args.lr)

    model.train()

    ii = 0
    state = env.reset()
    done = True

    episode_length = 0
    while True:
        # Sync with the shared model
        model.load_state_dict(shared_model.state_dict())
        if done:
            hx = torch.zeros(1, args.memsize).to(args.device)
        else:
            hx = hx.detach()

        values = []
        log_probs = []
        rewards = []
        entropies = []

        for step in range(args.num_steps):
            episode_length += 1
            # iii = prepro(state)
            # img = Image.fromarray(iii * 255)
            # img.save('/home/left/code/python/left5/flappybird-a3c/xx/%08d.png' % ii)


            value, logit, hx = model((torch.tensor(prepro(state)).to(args.device).view(1,1,80,80), hx))

            prob = F.softmax(logit, dim=-1)
            log_prob = F.log_softmax(logit, dim=-1)
            entropy = -(log_prob * prob).sum(1, keepdim=True)
            entropies.append(entropy)

            action = prob.multinomial(num_samples=1).detach()
            log_prob = log_prob.gather(1, action)

            # print(action.cpu().numpy().item())
            state, reward, done = env.step(action.cpu().numpy().item())
            # img = Image.fromarray(state)
            # img.save('/home/left/code/python/left5/flappybird-a3c/xx/%08d.png' % ii)
            # ii += 1

            # print('%s %s' % (action.cpu().numpy().item(), reward))
            done = done or episode_length >= args.max_episode_length
            # reward = max(min(reward, 10), -10)

            if done:
                episode_length = 0
                state = env.reset()

            values.append(value)
            log_probs.append(log_prob)
            rewards.append(reward)

            # print(reward)

            # if done:
            #     break

        if not done:
            value, _, _ = model((torch.tensor(prepro(state)).to(args.device).view(1,1,80,80), hx))
            R = value.detach().cpu()
        else:
            R = torch.zeros(1, 1)

        values.append(R)
        policy_loss = 0
        value_loss = 0
        gae = torch.zeros(1, 1)
        for i in reversed(range(len(rewards))):
            R = args.gamma * R + rewards[i]
            advantage = R.cpu() - values[i].cpu()
            value_loss = value_loss + 0.5 * advantage.pow(2)

            # Generalized Advantage Estimation
            delta_t = rewards[i] + args.gamma * values[i + 1].cpu() - values[i].cpu()
            gae = gae * args.gamma * args.gae_lambda + delta_t.cpu()

            policy_loss = policy_loss - log_probs[i].cpu() * gae.detach() - args.entropy_coef * entropies[i].cpu()

        optimizer.zero_grad()

        loss = policy_loss + args.value_loss_coef * value_loss.cpu()
        loss.backward()

        # torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

        ensure_shared_grads(model, shared_model)
        optimizer.step()
