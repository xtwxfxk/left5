# -*- coding: utf-8 -*-
'''
@time: 2019/9/8 19:47

@ author: javis
'''
import pywt, os, copy
import torch
import numpy as np
import pandas as pd
import neurokit as nk
from config import config
from torch.utils.data import Dataset
from torchvision import transforms
from scipy import signal

import traceback


def resample(sig, target_point_num=None):
    '''
    对原始信号进行重采样
    :param sig: 原始信号
    :param target_point_num:目标型号点数
    :return: 重采样的信号
    '''
    sig = signal.resample(sig, target_point_num) if target_point_num else sig
    return sig

def scaling(X, sigma=0.1):
    scalingFactor = np.random.normal(loc=1.0, scale=sigma, size=(1, X.shape[1]))
    myNoise = np.matmul(np.ones((X.shape[0], 1)), scalingFactor)
    return X * myNoise

def verflip(sig):
    '''
    信号竖直翻转
    :param sig:
    :return:
    '''
    return sig[::-1, :]

def shift(sig, interval=20):
    '''
    上下平移
    :param sig:
    :return:
    '''
    for col in range(sig.shape[1]):
        offset = np.random.choice(range(-interval, interval))
        sig[:, col] += offset
    return sig


def wavelet(sig, threshold =.04):
    '''
    小波去噪
    :param sig:
    :return:
    '''
    # db = 'db%s' % np.random.randint(1, 10)
    db = 'db5'
    
    w = pywt.Wavelet(db)
    
    for col in range(sig.shape[1]):
        _data = sig[:, col]
        maxlev = pywt.dwt_max_level(_data.shape[0], w.dec_len)
        coeffs = pywt.wavedec(_data, db, level=maxlev)
        for i in range(1, len(coeffs)):
            coeffs[i] = pywt.threshold(coeffs[i] + .0001, threshold*max(coeffs[i]))

        sig[:, col] = pywt.waverec(coeffs, db)
        
    return sig

def switch(sig):
    '''
    随机调转
    :param sig:
    :return:
    '''
    for col in range(sig.shape[1]):
        _data = sig[:, col]
        s = np.random.randint(0, _data.shape[0])
        sig[:, col] = np.concatenate((_data[s:], _data[:s]))
        
    return sig

def neuro_ecg(sig, sampling_rate=500):
    _data = None
    for col in range(sig.shape[1])[:1]:
        bio = nk.bio_process(ecg=sig[:, col], sampling_rate=sampling_rate, ecg_hrv_features=None)
        _data = bio['df'] if _data is None else np.hstack((_data, bio['df'].values))

    return np.hstack((sig, _data))

def transform(sig, sex, age, train=False):
    # 前置不可或缺的步骤
    sig = resample(sig, config.target_point_num)
    # # 数据增强
    # if train:
    #     if np.random.randn() > 0.3: sig = wavelet(sig)
    #     if np.random.randn() > 0.3: sig = scaling(sig)

    #     if np.random.randn() > 0.5: sig = verflip(sig)
        # if np.random.randn() > 0.5: sig = shift(sig)
    

    # sig = neuro_ecg(sig)

    # 后置不可或缺的步骤
    sig = np.column_stack((sig, sex, age))
    sig = sig.transpose()

    # print(sig.shape)

    # sig = torch.tensor(sig.copy(), dtype=torch.float)
    # qn = torch.norm(sig, dim=1)
    # sig = sig.div(qn.unsqueeze(1).expand_as(sig))
    # sig[torch.isnan(sig)] = 0
    
    sig = torch.tensor(sig, dtype=torch.float)
    return sig


class ECGDataset(Dataset):
    """
    A generic data loader where the samples are arranged in this way:
    dd = {'train': train, 'val': val, "idx2name": idx2name, 'file2idx': file2idx}
    """

    def __init__(self, data_path, train=True):
        super(ECGDataset, self).__init__()
        dd = torch.load(config.train_data)
        self.train = train
        self.data = dd['train'] if train else dd['val']
        self.idx2name = dd['idx2name']
        self.file2idx = dd['file2idx']
        self.wc = 1. / np.log(dd['wc'])

        # print(self.data)
        print(len(self.data))

    def __getitem__(self, index):
        fid = self.data[index]
        # file_path = os.path.join(config.train_dir, fid)
        # df = pd.read_csv(file_path, sep=' ') # .values

        file_path = os.path.join(config.train_dir, fid)
        # print(file_path)
        # with open(file_path, 'rb') as f:
        #     df = pd.read_parquet(f, engine='auto') # .values
        #     for i in range(3):
        #         try:
        #             df = pd.read_parquet(f, engine='auto') # .values
        #         except:
        #             open('/home/left/code/xx.txt', 'w').write(traceback.format_exc())
                    
        #         break

        df = pd.read_feather(file_path)

        # df.head()
        # df['III'] = df['I'] - df['II']
        # df['aVR'] = -(df['I'] + df['II']) / 2
        # df['aVL'] = df['I'] - df['II'] / 2
        # df['aVF'] = df['II'] - df['I'] / 2
        df = df.values
        
        sex = np.ones(df.shape[0]) * self.file2idx[fid][-1]
        age = np.ones(df.shape[0]) * self.file2idx[fid][-2]

        x = transform(df, sex, age, self.train)

        # print(x.shape)
        # print(x.data.numpy())
        # x = np.vstack((x.data.numpy(), sex, age))
        # torch.tensor(sig.copy(), dtype=torch.float)

        target = np.zeros(config.num_classes)
        target[self.file2idx[fid][:-2]] = 1
        target = torch.tensor(target, dtype=torch.float32)
        return x, target

    def __len__(self):
        return len(self.data)


if __name__ == '__main__':
    d = ECGDataset(config.train_data)
    print(d[0])
