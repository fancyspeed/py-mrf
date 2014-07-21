from utils import *
import math
import gc
gc.disable()

import os
import sys
classify_path = os.path.abspath('../classify')
sys.path.append(classify_path)
from name_classify import NameClassify

def get_pword_map(p_paper):
  word_dict = {}
  for line in open(p_paper):
    arr = line.strip().split(',')
    arr += [''] * (6 - len(arr))
    pid, pname, pword = arr[0], arr[1], arr[5]
    if pword:
      arr_word = pword.split(' ')
      for word in arr_word:
        word_dict[word] = word_dict.get(word, 0) + 1
  sort_list = sorted(word_dict.items(), key=lambda d:d[1], reverse=True)

  word_dict = {}
  for idx in range( len(sort_list) ):
    if idx >= 29000: break 
    if idx <= 10: continue 
    word, score = sort_list[idx]
    if score <= 10: continue 
    
    word_dict[word] = idx
  return word_dict 

def get_paper_info(p_paper):
  pid_info = {}
  for line in open(p_paper):
    arr = line.strip().split(',')
    arr += [''] * (6 - len(arr))
    pid, pname, pword = arr[0], arr[1], arr[5]
    year, conf, jour = int(arr[2]), int(arr[3]), int(arr[4])
    pid_info[pid] = [year, conf, jour]
  return pid_info


def load_papers(p_paper, word_dict):
  pid_dict = {}
  for line in open(p_paper):
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
      pid_dict[pid].append( (30001, 1) ) # 7001->30000 
    if conf > 0 and conf < 6000 and jour > 0 and jour < 23000:
      pid_dict[pid].append( (30002, 1) ) # 7001->30000 

    if pword:
      arr_word = pword.split(' ')
      for word in arr_word: 
        if word in word_dict:
          pid_dict[pid].append( (word_dict[word]+31000, 1) )

  return pid_dict

def load_authors(p_author):
  nc = NameClassify()
  aid_dict = {}

  for line in open(p_author):
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

def load_match(p_match, pid_info):
  match_count = {}
  aid_year, aid_conf, aid_jour = {}, {}, {}
  pid_author, aid_paper = {}, {}

  for line in open(p_match):
    arr = line.strip().split(',')
    arr += [''] * (4 - len(arr))
    pid, aid, aname, aaff = arr[0], arr[1], arr[2], arr[3]

    key = pid + '\t' + aid
    match_count[key] = match_count.get(key, 0) + 1

    if pid in pid_info: 
      year = pid_info[pid][0]
      if year > 1500 and year < 2015:
        key2 = aid + '\t' + str(year) 
        aid_year[key2] = aid_year.get(key2, 0) + 1
      conf = pid_info[pid][1]
      if conf > 0 and conf < 10000:
        key2 = aid + '\t' + str(conf) 
        aid_conf[key2] = aid_conf.get(key2, 0) + 1
      jour = pid_info[pid][2]
      if jour > 0 and jour < 30000:
        key2 = aid + '\t' + str(jour) 
        aid_jour[key2] = aid_jour.get(key2, 0) + 1

    if pid not in pid_author:
      pid_author[pid] = set()
    pid_author[pid].add(aid)
    if aid not in aid_paper:
      aid_paper[aid] = set()
    aid_paper[aid].add(pid)

  match_dict = {}
  for key in match_count:
    if key not in match_dict:
      match_dict[key] = []
    count = min(9, match_count[key])
    match_dict[key].append( (count+1, 1) )
    match_dict[key].append( (11, count) )

  return match_dict, aid_year, aid_conf, aid_jour, pid_author, aid_paper


def construct(p_train, p_out, pid_dict, aid_dict, match_dict, pid_info, aid_year, aid_conf, aid_jour, pid_author, aid_paper):
  f_out = open(p_out, 'w')
  for line in open(p_train):
    score, aid, pid = line.strip().split('\t')

    feat_list = [] #(feat_id, feat_weight)

    # paper features
    if pid in pid_dict:
      for k, v in pid_dict[pid]:
        feat_list.append( (k, v) ) 

    # author features
    if aid in aid_dict:
      for k, v in aid_dict[aid]:
        feat_list.append( (k+70000, v) ) 

    # (paper, author) features
    key = pid + '\t' + aid
    if key in match_dict:
      for k, v in match_dict[key]:
        feat_list.append( (k+80000, v) ) 

    '''
    if pid in pid_info: 
      year = pid_info[pid][0]
      if year > 1500 and year < 2015:
        key2 = aid + '\t' + str(year) 
        if key2 in aid_year:
          feat_list.append( (aid_year[key2]+90000, 1) ) 
      conf = pid_info[pid][1]
      if conf > 0 and conf < 10000:
        key2 = aid + '\t' + str(conf) 
        if key2 in aid_conf:
          feat_list.append( (aid_conf[key2]+91000, 1) ) 
      jour = pid_info[pid][2]
      if jour > 0 and jour < 30000:
        key2 = aid + '\t' + str(jour) 
        if key2 in aid_jour:
          feat_list.append( (aid_jour[key2]+92000, 1) ) 
    '''

    '''
    n_comm_pid = 0
    if pid in pid_author and aid in aid_paper:
      a_set = pid_author[pid]
      for pid2 in aid_paper[aid]:
        if pid2 in pid_author:
          a_set2 = pid_author[pid2]
          c_set = a_set.intersection(a_set2)
          if len(c_set) > 1:
            n_comm_pid += 1
    if n_comm_pid > 0:
      n_comm_pid = min(8, n_comm_pid/10)
      feat_list.append( (n_comm_pid+93000, 1) ) 
    '''


    feat_list2 = ['%s:%s' % (k, v) for k, v in feat_list]
    new_line = '%s %s\n' % (score, ' '.join(feat_list2))
    f_out.write(new_line)
  f_out.close()


if __name__ == '__main__':
  word_dict = {} #get_pword_map('cat_paper')
  pid_info = {} #get_paper_info('cat_paper')
  pid_dict = load_papers('cat_paper', word_dict)
  aid_dict = load_authors('cat_author')
  match_dict, aid_year, aid_conf, aid_jour, pid_author, aid_paper = load_match('cat_match', pid_info)

  construct('cat_train.txt', 'cat_fm_train', pid_dict, aid_dict, match_dict, pid_info, aid_year, aid_conf, aid_jour, pid_author, aid_paper)
  construct('cat_test.txt', 'cat_fm_test', pid_dict, aid_dict, match_dict, pid_info, aid_year, aid_conf, aid_jour, pid_author, aid_paper)

