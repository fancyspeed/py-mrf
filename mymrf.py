#coding: utf-8
import sys
import random
import time
import gc
from myio import *

class MyMRF():
  def __init__(self):
    self.myio = MyIO()
    self.u0 = 1 
    self.max_iter = 100 
    self.step_len = 0.01 
    self.gama = 0.1 
    self.delta = 0.001
    self.test_iter = 20
    self.test_delta = 0.01

  def set_parameters(self, u0, max_iter, step_len, gama, delta):
    self.u0 = u0
    self.max_iter = max_iter
    self.step_len = step_len
    self.gama = gama
    self.delta = delta
    print 'u0:%s, max iter:%s, step len:%s, gama:%s, delta:%s' % (u0, max_iter, step_len, gama, delta)

  def set_test_parameters(self, test_iter, test_delta):
    self.test_iter = test_iter
    self.test_delta = test_delta
    print 'test_iter:%s, test_delta:%s' % (test_iter, test_delta)

  def set_model_path(self, p_out):
    self.model_path = p_out

  def init_train(self, p_train):
    self.myio.load_train(p_train)

    self.theta = {}
    for i in range(0, self.myio.max_idx + 1):
      self.theta[i] = 0.00001 + random.random() * self.u0

    self.y_train = {}
    for gid in self.myio.train_site_score:
      for pid in self.myio.train_site_score[gid]:
        key = gid + '\t' + pid
        self.y_train[key] = self.myio.train_site_score[gid][pid]
    self.x_train = {} 
    for gid in self.myio.train_site_score:
      for pid in self.myio.train_site_score[gid]:
        key = gid + '\t' + pid
        self.x_train[key] = {}
        self.x_train[key][0] = 1
        for idx, weight in self.myio.train_site_feat[gid][pid]:
          self.x_train[key][idx] = weight
      if gid in self.myio.train_edge_feat:
        for pid in self.myio.train_edge_feat[gid]:
          key = gid + '\t' + pid
          for nid in self.myio.train_edge_feat[gid][pid]:
            for idx, weight in self.myio.train_edge_feat[gid][pid][nid]:
              if idx not in self.x_train[key]:
                self.x_train[key][idx] =  self.myio.train_site_score[gid][nid] * weight
              else:
                self.x_train[key][idx] += self.myio.train_site_score[gid][nid] * weight

  def init_test_y(self):
    self.y_test = {}
    for gid in self.myio.test_site_score:
      for pid in self.myio.test_site_score[gid]:
        key = gid + '\t' + pid
        self.y_test[key] = self.myio.test_site_score[gid][pid]

  def init_test_x(self):
    self.x_test = {} 
    for gid in self.myio.test_site_score:
      for pid in self.myio.test_site_score[gid]:
        key = gid + '\t' + pid
        self.x_test[key] = {}
        self.x_test[key][0] = 1
        for idx, weight in self.myio.test_site_feat[gid][pid]:
          self.x_test[key][idx] = weight
      if gid in self.myio.test_edge_feat:
        for pid in self.myio.test_edge_feat[gid]:
          key = gid + '\t' + pid
          for nid in self.myio.test_edge_feat[gid][pid]:
            for idx, weight in self.myio.test_edge_feat[gid][pid][nid]:
              if idx not in self.x_test[key]:
                self.x_test[key][idx] =  self.y_test[key] * weight
              else:
                self.x_test[key][idx] += self.y_test[key] * weight

  def predict(self, x):
    score1 = 0
    for idx in x:
      score1 += x[idx] * self.theta[idx]
    score2 = math.exp(2 * score1)
    score = (1 - score2) / (1 + score2)
    return score

  def predict_all(self):
    for key in self.x_test:
      self.y_test[key] = self.predict(self.x_test[key])

  def gradient(self, x, y):
    score1 = 0
    score3 = 0
    for idx in x:
      score1 += x[idx] * self.theta[idx]
      score3 += self.theta[idx] * self.theta[idx]
    score2 = math.exp(2 * score1)
    grad1 = (y-1) + 2 * score2 / (1 + score2) 

    loss = (y-1) * score1 + math.log(1 + score2) + self.gama * score3
    grad = {} 
    for idx in x:
      grad[idx] = grad1 * x[idx] + 2 * self.gama * self.theta[idx]
    return loss, grad 
    
  def update(self, grad):
    for idx in grad:
      self.theta[idx] -= self.step_len * grad[idx]

  def train(self, key_list):
    tot_error, n_line = 0, 0.0001 
    for key in key_list:
      loss, grad = self.gradient(self.x_train[key], self.y_train[key]) 
      self.update(grad)
      tot_error += loss
      n_line += 1
    return tot_error / n_line 

  def valid(self, key_list):
    tot_error, n_line = 0, 0.0001 
    for key in key_list:
      loss, grad = self.gradient(self.x_train[key], self.y_train[key]) 
      tot_error += loss
      n_line += 1
    return tot_error / n_line 

  def save_model(self):
    f_out = open(self.model_path, 'w')
    for idx, value in self.theta.items():
      f_out.write('%s %s\n' % (idx, value))
    f_out.close()

  def load_model(self):
    for line in open(self.model_path):
      idx, value = line.strip().split(' ')
      idx, value = int(idx), float(value)
      self.theta[idx] = value

  def set_label(self):
    label_dict = {}
    for key in self.y_test:
        if self.y_test[key] >= 0:
          label_dict[key] = 1
        else:
          label_dict[key] = -1
    return label_dict

  def get_diff_ratio(self, label_dict, prev_label_dict):
    n_tot, n_diff, n_positive = 0, 0, 0
    for key in label_dict:
      #if label_dict[key] != prev_label_dict[key]:
      #  n_diff += 1.0
      n_diff += math.fabs(label_dict[key] - prev_label_dict[key])
      if label_dict[key] >= 0:
        n_positive += 1.0
      n_tot += 1
    return n_diff/n_tot, n_positive/n_tot 

  def test(self, p_test, p_out):
    self.myio.load_test(p_test)
    self.load_model()
    self.init_test_y()

    #label_dict = self.set_label()
    label_dict = self.y_test.copy()
    prev_label_dict = label_dict
    print 'testing started', time.time()

    for iter in range(self.test_iter):
      self.init_test_x()
      self.predict_all()

      #label_dict = self.set_label()
      label_dict = self.y_test.copy()
      diff_ratio, pos_ratio = self.get_diff_ratio(label_dict, prev_label_dict)
      print 'iter:%6d, diff ratio:%.6f, pos ratio:%.6f' % (iter, diff_ratio, pos_ratio)
      if diff_ratio < self.test_delta: 
        break
      prev_label_dict = label_dict

    f_out = open(p_out, 'w')
    for key in self.y_test:
      gid, pid = key.split('\t')
      f_out.write('%s\t%s\t%s\n' % (self.y_test[key], gid, pid))
    f_out.close()


  def gradient_descent(self):
    train_rmse = 99999999
    valid_rmse = 99999999
    best_train_rmse = 99999999
    best_valid_rmse = 99999999

    key_train = self.x_train.keys()

    print 'gradient descent started', time.time()
    for iter in range(self.max_iter):
      random.shuffle(key_train)
      train_rmse = self.train(key_train)
      valid_rmse = self.valid(key_train)
      print 'iter:%6d, step len:%.6f, train:%.6f, validation:%.6f' % (iter, self.step_len, train_rmse, valid_rmse)
      self.step_len *= 0.995

      if (valid_rmse > best_valid_rmse) and (train_rmse + self.delta > best_train_rmse):
        break
      if valid_rmse < best_valid_rmse:
        best_valid_rmse = valid_rmse
        self.save_model()
      if train_rmse < best_train_rmse:
        best_train_rmse = train_rmse
    print 'gradient descent finished', time.time()


if __name__ == '__main__':
  mrf = MyMRF()
  mrf.set_parameters(u0=0.01, max_iter=50, step_len=0.0001, gama=0.00001, delta=0.0001)
  mrf.set_test_parameters(test_iter=1, test_delta=0.00001)

  if len(sys.argv) >= 2: 
    gc.disable()
    mrf.set_model_path('./tmp/pig_mrf_model')
    mrf.init_train('./tmp/pig_mrf_train')
    gc.enable()
    mrf.gradient_descent()
    gc.disable()
    mrf.test('./tmp/pig_mrf_test', './tmp/pig_mrf_pred')
  else:
    gc.disable()
    mrf.set_model_path('./tmp/cat_mrf_model')
    mrf.init_train('./tmp/cat_mrf_train')
    gc.enable()
    mrf.gradient_descent()
    gc.disable()
    mrf.test('./tmp/cat_mrf_test', './tmp/cat_mrf_pred')

