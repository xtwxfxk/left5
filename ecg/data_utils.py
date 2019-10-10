
import os
import numpy as np

data_root = '~/data/xd'

train_x_dir = os.path.join(data_root, 'hf_round1_train/train')
train_y_file = os.path.join(data_root, 'hf_round1_label.txt')

arrythmia_file = os.path.join(data_root, 'hf_round1_arrythmia.txt')

test_x_dir = os.path.join(data_root, 'hf_round1_testA/testA')
test_y_file = os.path.join(data_root, 'hf_round1_subA.txt')


def name2index():
    return {name: i for i, name in enumerate([line.strip() for line in open(arrythmia_file, encoding='utf-8') if line.strip()])}

def index2name():
    return {i: name for i, name in enumerate([line.strip() for line in open(arrythmia_file, encoding='utf-8') if line.strip()])}


def train_data():
    
