import sys
import math
import gc
gc.disable()

import os
import sys
classify_path = os.path.abspath('../classify')
sys.path.append(classify_path)
from name_classify import NameClassify
from utils import *

class FileLoader():
  def __init__(self):
    pass

  def load_n_match(self, p_in):
    match_count = {}
    for line in open(p_in):
      arr = line.strip().split(',')
      arr += [''] * (4 - len(arr))
      pid, aid, aname, aaff = arr[0], arr[1], arr[2], arr[3]

      key = aid + '\t' + pid
      match_count[key] = match_count.get(key, 0) + 1

    key_dict = {}
    for key in match_count:
      key_dict[key] = [ (1, match_count[key]) ]
    return key_dict 

  def load_match_score(self, p_match, p_aff):
    aid_aff = {}
    for line in open(p_aff):
      arr = line.strip().split(',')
      arr += [''] * (3 - len(arr))
      aid, aname, aaff = arr[0], arr[1], arr[2]
      aid_aff[aid] = [aname, aaff]

    match_score = {}
    for line in open(p_match):
      arr = line.strip().split(',')
      arr += [''] * (4 - len(arr))
      pid, aid, aname, aaff = arr[0], arr[1], arr[2], arr[3]
      if aid not in aid_aff: continue

      key = aid + '\t' + pid
      score = compare_pair([aname, aaff], aid_aff[aid]) 
      match_score[key] = min( score, match_score.get(key, 10) )

    match_dict = {}
    for key in match_score:
      match_dict[key] = [ (match_score[key], 1) ] 
    return match_dict

  def load_paper(self, p_in):
    pid_dict = {}
    for line in open(p_in):
      arr = line.strip().split(',')
      arr += [''] * (6 - len(arr))
      pid, pname, pword = arr[0], arr[1], arr[5]
      year, conf, jour = int(arr[2]), int(arr[3]), int(arr[4])

      pid_dict[pid] = []
      if year > 1500 and year < 2015:
        pid_dict[pid].append( (year-1500, 1) ) # 1->1000
      else:
        pid_dict[pid].append( (800, 1) ) # 1->1000

      if conf > 0 and conf < 6000:
        pid_dict[pid].append( (conf+1000, 1) ) # 1001->7000
      elif jour > 0 and jour < 23000:
        pid_dict[pid].append( (jour+7000, 1) ) # 7001->30000 
      else:
        pid_dict[pid].append( (30001, 1) ) 
      if conf > 0 and conf < 6000 and jour > 0 and jour < 23000:
        pid_dict[pid].append( (30002, 1) ) 

      '''
      if not pname:
        pid_dict[pid].append( (31001, 1) ) 
      else:
        len_title = len(pname.split(' '))
        len_title = min(10, len_title/3)
        pid_dict[pid].append( (31002+len_title, 1) ) 
      '''
      '''
      if not pword:
        pid_dict[pid].append( (32001, 1) ) 
      else:
        len_word = len(pword.split(' '))
        len_word = min(10, len_word)
        pid_dict[pid].append( (32002+len_word, 1) ) 
      '''

    return pid_dict

  def load_paper_info(self, p_in):
    word_dict = {}
    for line in open(p_in):
      arr = line.strip().split(',')
      arr += [''] * (6 - len(arr))
      pid, pname, pword = arr[0], arr[1], arr[5]
      if pname:
        arr_word = pname.split(' ')
        for word in arr_word:
          word_dict[word] = word_dict.get(word, 0) + 1
    sort_list = sorted(word_dict.items(), key=lambda d:d[1], reverse=True)
    sort_list = sort_list[30:30000]
    word_dict = {}
    for idx in range( len(sort_list) ):
      word, weight = sort_list[idx]
      if weight <= 30: continue
      word_dict[word] = idx 

    pid_dict = {}
    for line in open(p_in):
      arr = line.strip().split(',')
      arr += [''] * (6 - len(arr))
      pid, pname, pword = arr[0], arr[1], arr[5]
      year, conf, jour = int(arr[2]), int(arr[3]), int(arr[4])

      '''
      pid_dict[pid] = {}
      if pname:
        pid_dict[pid][1] = set() 
        arr_word = pname.split(' ')
        for word in arr_word:
          if word in word_dict:
            pid_dict[pid][1].add( word_dict[word] )
      if year > 1500 and year < 2015:
        pid_dict[pid][2] = set( [year] ) 
      if conf > 0 and conf < 6000:
        pid_dict[pid][3] = set( [conf] )
      elif jour > 0 and jour < 23000:
        pid_dict[pid][4] = set( [jour] )
      '''
      pid_dict[pid] = set()
      if pname:
        arr_word = pname.split(' ')
        for word in arr_word:
          if word in word_dict:
            pid_dict[pid].add( word_dict[word]+0 )
      if year > 1500 and year < 2015:
        pid_dict[pid].add( year-1500+30000 ) 
      if conf > 0 and conf < 6000:
        pid_dict[pid].add( conf+31000 )
      elif jour > 0 and jour < 23000:
        pid_dict[pid].add( jour+37000 )

    return pid_dict
      

  def load_author(self, p_in):
    nc = NameClassify()
    aid_dict = {}
    for line in open(p_in):
      arr = line.strip().split(',')
      arr += [''] * (3 - len(arr))
      aid, aname, aaff = arr[0], arr[1], arr[2]

      aid_dict[aid] = []
      if not aname:
        aid_dict[aid].append( (1, 1) )
      else:
        arr_name = aname.split(' ')
        len_name = len(arr_name)
        len_name = min(6, len_name)
        aid_dict[aid].append( (len_name+1, 1) )

        if len_name >= 2:
          first_name, last_name = arr_name[0], arr_name[-1] 
          if len(last_name) == 1:
            aid_dict[aid].append( (11, 1) )
          if len(first_name) == 1:
            aid_dict[aid].append( (12, 1) )
        if nc.is_cn(aname):
          aid_dict[aid].append( (15, 1) )
        else:
          aid_dict[aid].append( (16, 1) )
      if aaff:
        aid_dict[aid].append( (21, 1) )
      else:
        aid_dict[aid].append( (22, 1) )
    return aid_dict

class Constructer():
  def __init__(self):
    pass

  def load_train(self, p_in):
    self.site_score = {}
    self.site_feat = {}
    self.edge_feat = {}

    for line in open(p_in):
      score, gid, pid = line.strip().split('\t')
      key = gid + '\t' + pid
      self.site_score[key] = score

  def add_site_feature(self, key_dict, from_idx): 
    for key in key_dict:
      if key in self.site_score:
        if key not in self.site_feat: self.site_feat[key] = []
        for idx, weight in key_dict[key]:
          self.site_feat[key].append( (from_idx+idx, weight) )

  def add_pid_feature(self, pid_dict, from_idx):
    for key in self.site_score:
      gid, pid = key.split('\t')
      if pid in pid_dict:
        if key not in self.site_feat: self.site_feat[key] = []
        for idx, weight in pid_dict[pid]:
          self.site_feat[key].append( (from_idx+idx, weight) )
    

  def add_gid_feature(self, gid_dict, from_idx):
    for key in self.site_score:
      gid, pid = key.split('\t')
      if gid in gid_dict:
        if key not in self.site_feat: self.site_feat[key] = []
        for idx, weight in gid_dict[gid]:
          self.site_feat[key].append( (from_idx+idx, weight) )

  def add_stat_feature(self, from_idx):
    gid_dict = {}
    for key in self.site_score:
      gid, pid = key.split('\t')
      gid_dict[gid] = gid_dict.get(gid, 0) + 1
    for key in self.site_score:
      gid, pid = key.split('\t')
      idx, weight = min(100, gid_dict[gid]/3), 1
      self.site_feat[key].append( (from_idx+idx, weight) )

  def add_edge_feature(self, pid_dict, from_idx):
    gid_dict = {}
    for key in self.site_score:
      gid, pid = key.split('\t')
      if pid not in pid_dict: continue

      if gid not in gid_dict:
        gid_dict[gid] = set( [pid] )
      else:
        gid_dict[gid].add(pid)

      for pid2 in gid_dict[gid]:
        if pid2 == pid: continue

        key = gid + '\t' + pid + '\t' + pid2
        key2 = gid + '\t' + pid2 + '\t' + pid

        comm_set = pid_dict[pid].intersection(pid_dict[pid2])
        for idx in comm_set:
          if key not in self.edge_feat:
            self.edge_feat[key] = []
            self.edge_feat[key2] = []
          self.edge_feat[key].append( (from_idx+idx, 1) )
          self.edge_feat[key2].append( (from_idx+idx, 1) )

        '''
        for idx, feat_set in pid_dict[pid].items():
          if idx in pid_dict[pid2]:
            feat_set2 =  pid_dict[pid2][idx]
            comm_set = feat_set2.intersection(feat_set)
            len_set = len(comm_set)
            if not len_set: continue

            if key not in self.edge_feat:
              self.edge_feat[key] = []
              self.edge_feat[key2] = []
            self.edge_feat[key].append( (from_idx+idx, len_set) )
            self.edge_feat[key2].append( (from_idx+idx, len_set) )
        '''

  def add_edge_feature2(self, pid_dict, from_idx):
    all_edge_feat = {}

    gid_dict = {}
    for key in self.site_score:
      gid, pid = key.split('\t')
      if pid not in pid_dict: continue

      if gid not in gid_dict:
        gid_dict[gid] = set( [pid] )
      else:
        gid_dict[gid].add(pid)

      for pid2 in gid_dict[gid]:
        if pid2 == pid: continue

        key = gid + '\t' + pid + '\t' + pid2
        key2 = gid + '\t' + pid2 + '\t' + pid
        for idx, feat_set in pid_dict[pid].items():
          if idx in pid_dict[pid2]:
            feat_set2 =  pid_dict[pid2][idx]
            comm_set = feat_set2.intersection(feat_set)
            len_set = len(comm_set)
            if not len_set: continue

            if key not in all_edge_feat:
              all_edge_feat[key] = []
              all_edge_feat[key2] = []
            all_edge_feat[key].append( (from_idx+idx, len_set) )
            all_edge_feat[key2].append( (from_idx+idx, len_set) )

    neigh_dict = {}
    for key in all_edge_feat: 
      gid, pid, pid2 = key.split('\t')
      pair = gid + '\t' + pid
      score = 0
      for idx, weight in all_edge_feat[key]:
        score += 1 + weight / 100.0
      if pair not in neigh_dict:
        neigh_dict[pair] = []
      neigh_dict[pair].append( (pid2, score) ) 

    for pair in neigh_dict:
      sort_list = sorted(neigh_dict[pair], key = lambda d:d[1], reverse=True)[:5]
      for pid2, score in sort_list:
        key = pair + '\t' + pid2
        self.edge_feat[key] = all_edge_feat[key]
    
  def store(self, p_out):
    f_out = open(p_out, 'w')

    # site: score gid:1 pid:1 idx:weight ...
    # edge: gid:1 pid:1 nid:1 idx:weight ...

    for key in self.site_score: 
      gid, pid = key.split('\t')

      feat_str_list = [] 
      if key in self.site_feat:
        feat_str_list = ['%s:%s' % (idx, weight) for idx, weight in self.site_feat[key]]
      line = '%s gid:%s pid:%s %s\n' % (self.site_score[key], gid, pid, ' '.join(feat_str_list))
      f_out.write(line)

    for key in self.edge_feat:
      gid, pid, nid = key.split('\t')

      feat_str_list = ['%s:%s' % (idx, weight) for idx, weight in self.edge_feat[key]]
      line = 'gid:%s pid:%s nid:%s %s\n' % (gid, pid, nid, ' '.join(feat_str_list))
      f_out.write(line)

    f_out.close()


if __name__ == '__main__':
  loader = FileLoader()
  cons = Constructer()

  match_dict = loader.load_n_match('./data/pig_match')

  if len(sys.argv) >= 2:
    cons.load_train('./data/pig_train.txt')
  else:
    cons.load_train('./data/cat_train.txt')
  cons.add_site_feature(match_dict, 1)
  if len(sys.argv) >= 2:
    cons.store('./tmp/pig_mrf_train')
  else:
    cons.store('./tmp/cat_mrf_train')

  if len(sys.argv) >= 2:
    cons.load_train('./data/pig_test.txt')
  else:
    cons.load_train('./data/cat_test.txt')
  cons.add_site_feature(match_dict, 1)
  if len(sys.argv) >= 2:
    cons.store('./tmp/pig_mrf_test')
  else:
    cons.store('./tmp/cat_mrf_test')

