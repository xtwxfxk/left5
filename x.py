# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

from torch.autograd import Function

from lutils.stock import lstock
from lutils.stock.lstock_data import LStockData

ls = LStockData()


id = '002108'
ls.search_to_h5(id, '/home/left5/datas/%s.h5' % id)



# import numpy as np
# from scipy.stats import rv_discrete
# import seaborn as sns
# import matplotlib.pyplot as plt
#
# # class weibull_gen(rv_discrete):
# #
# #     # def _pmf(self, k, mu):
# #     #     return exp(-mu) * mu**k / factorial(k)
# #
# #     def _cdf(self, x, lam, k):
# #         _x = np.copy(x)
# #         _x[_x < 0] = 0
# #
# #         return 1 - np.exp(-np.power((_x / lam), k - 1))
# #
# # lam = 1.
# # k = 1.5
# # x = 2.5 * np.random.random(1000)
# # w = weibull_gen(name='weibull', values=(x, lam, k))
# # a = w.rvs(size=100)
# #
# # sns.distplot(a)
# # plt.show()
#
# # from scipy.stats import rv_continuous
# # class gaussian_gen(rv_continuous):
# #     "Gaussian distribution"
# #     def _pdf(self, x):
# #         return np.exp(-x**2 / 2.) / np.sqrt(2.0 * np.pi)
# # gaussian = gaussian_gen(name='gaussian')
# #
# # a = gaussian.rvs(size=10000)
# #
# # sns.distplot(a)
# # plt.show()
#
#
# from scipy.stats import rv_continuous
# class weibull_gen(rv_continuous):
#     "Gaussian distribution"
#
#     lam = 1.
#     k = 1.5
#
#     def _pdf(self, x):
#         return self.k / self.lam * np.power(x / self.lam, self.k - 1) * np.exp(-np.power(x / self.lam, self.k))
# weibull = weibull_gen(name='gaussian')
#
# # a = weibull.rvs(size=1000)
# x = np.random.random(1000) * 2.5
# a = weibull.pdf(x)
#
# sns.distplot(a)
# plt.show()
#
