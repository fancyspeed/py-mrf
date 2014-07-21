import random

def trans_train(p_in, p_out):
  f_in = open(p_in)
  test_line = f_in.readline()
  if test_line[0] in ('A', 'a'):
    flag = True
  else:
    flag = False
  f_in.close()

  f_in = open(p_in)
  if flag:
    f_in.readline()
  line_list = []
  for line in f_in:
    uid, acc, rej = line.strip().split(',')
    acc_list = acc.strip().split(' ')
    rej_list = rej.strip().split(' ')

    #'''
    acc_set = set(acc_list)
    rej_set = set(rej_list)
    comm_set = acc_set.intersection(rej_set)
    acc_list = list( acc_set - comm_set )
    rej_list = list( rej_set - comm_set )
    #'''

    for v in acc_list:
      new_line = '1\t%s\t%s\n' % (uid, v)
      line_list.append(new_line)
    for v in rej_list:
      new_line = '-1\t%s\t%s\n' % (uid, v)
      line_list.append(new_line)
  f_in.close()

  random.shuffle(line_list)
  f_out = open(p_out, 'w')
  for new_line in line_list:
    f_out.write(new_line)
  f_out.close()

def trans_test(p_in, p_out):
  f_in = open(p_in)
  test_line = f_in.readline()
  if test_line[0] in ('A', 'a'):
    flag = True
  else:
    flag = False
  f_in.close()

  f_in = open(p_in)
  if flag:
    f_in.readline()
  f_out = open(p_out, 'w')
  for line in f_in:
    uid, pid = line.strip().split(',')
    p_list = pid.strip().split(' ')
    random.shuffle(p_list)
    for v in p_list:
      new_line = '0\t%s\t%s\n' % (uid, v)
      f_out.write(new_line)
  f_out.close()
  f_in.close()

if __name__ == '__main__':
  trans_train('./data/cat_train', './data/cat_train.txt')
  trans_train('./data/cat_truth', './data/cat_truth.txt')
  trans_test('./data/cat_test', './data/cat_test.txt')
  trans_train('./data/pig_train', './data/pig_train.txt')
  trans_test('./data/pig_test', './data/pig_test.txt')

