import sys
import math
import random

class MyIO():
  def __init__(self):
    self.n_site = 0
    self.n_edge = 0
    self.max_idx = 0

  def parse_line(self, line):
    flag = 0
    score, gid, pid, nid, feat_list = 0, 0, 0, 0, []

    arr = line.strip().split(' ')
    if not line or line[0] == '#': 
      flag = 0 #comment
    elif arr[0].startswith('gid'):
      flag = 1 #edge

      if len(arr) < 3: pass
      elif not arr[1].startswith('pid'): pass 
      elif not arr[2].startswith('nid'): pass 
      else:
        gid = arr[0].split(':')[1]
        pid = arr[1].split(':')[1]
        nid = arr[2].split(':')[1]
        feat_str_list = arr[3:]
        feat_pair_list = [feat_str.split(':') for feat_str in feat_str_list]
        feat_list = [(int(idx), float(weight)) for idx, weight in feat_pair_list]
    else:  
      flag = 2 #site

      if len(arr) < 3: pass 
      elif not arr[1].startswith('gid'): pass 
      elif not arr[2].startswith('pid'): pass 
      else:
        score = float(arr[0])
        gid = arr[1].split(':')[1]
        pid = arr[2].split(':')[1]
        feat_str_list = arr[3:]
        feat_pair_list = [feat_str.split(':') for feat_str in feat_str_list]
        feat_list = [(int(idx), float(weight)) for idx, weight in feat_pair_list]

    return flag, score, gid, pid, nid, feat_list


  def load_train(self, p_in):
    self.train_site_score = {}
    self.train_site_feat = {}
    self.train_edge_feat = {}
     
    for line in open(p_in):
      flag, score, gid, pid, nid, feat_list = self.parse_line(line)

      if flag == 2:
        self.n_site += 1
        if gid not in self.train_site_score:
          self.train_site_score[gid] = {}
          self.train_site_feat[gid] = {}
        self.train_site_score[gid][pid] = score
        self.train_site_feat[gid][pid] = []
        for idx, weight in feat_list:
          self.train_site_feat[gid][pid].append( (idx, weight) )
          if idx > self.max_idx: self.max_idx = idx
      elif flag == 1:
        self.n_edge += 1
        if gid not in self.train_edge_feat:
          self.train_edge_feat[gid] = {}
        if pid not in self.train_edge_feat[gid]:
          self.train_edge_feat[gid][pid] = {} 
        self.train_edge_feat[gid][pid][nid] = [] 
        for idx, weight in feat_list:
          self.train_edge_feat[gid][pid][nid].append( (idx, weight) )
          if idx > self.max_idx: self.max_idx = idx
    print '<train> site:%d, edge:%d, max index:%d' % (self.n_site, self.n_edge, self.max_idx)
    print '<train> group:%d, group_with_edge:%d' % (len(self.train_site_feat), len(self.train_edge_feat))

  def load_test(self, p_in):
    self.test_site_score = {}
    self.test_site_feat = {}
    self.test_edge_feat = {}

    test_n_site, test_n_edge, test_max_idx = 0, 0, 0
     
    for line in open(p_in):
      flag, score, gid, pid, nid, feat_list = self.parse_line(line)
      #score = 1
      #if random.randint(0,1) == 1: score = 1
      #else: score = -1

      if flag == 2:
        test_n_site += 1
        if gid not in self.test_site_score:
          self.test_site_score[gid] = {}
          self.test_site_feat[gid] = {}
        self.test_site_score[gid][pid] = score
        self.test_site_feat[gid][pid] = []
        for idx, weight in feat_list:
          if idx > test_max_idx: test_max_idx = idx
          if idx > self.max_idx: continue
          self.test_site_feat[gid][pid].append( (idx, weight) )
      elif flag == 1:
        test_n_edge += 1
        if gid not in self.test_edge_feat:
          self.test_edge_feat[gid] = {}
        if pid not in self.test_edge_feat[gid]:
          self.test_edge_feat[gid][pid] = {} 
        self.test_edge_feat[gid][pid][nid] = [] 
        for idx, weight in feat_list:
          if idx > test_max_idx: test_max_idx = idx
          if idx > self.max_idx: continue
          self.test_edge_feat[gid][pid][nid].append( (idx, weight) )

    print '<test>  site:%d, edge:%d, max index:%d' % (test_n_site, test_n_edge, test_max_idx)
    print '<test>  group:%d, group_with_edge:%d' % (len(self.test_site_feat), len(self.test_edge_feat))

def test():
  myio = MyIO()
  myio.load_train('./tmp/cat_mrf_train')
  myio.load_test('./tmp/cat_mrf_test')

if __name__ == '__main__':
  test()


