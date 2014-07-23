aid_set = set()
pid_set = set()
for line in open('./data/pig_train'):
  arr = line.strip().split(',')
  aid = arr[0]
  aid_set.add(aid)
  pids = (arr[1] + ' ' + arr[2]).split(' ')
  for pid in pids:
    pid_set.add(pid)
for line in open('./data/pig_test'):
  arr = line.strip().split(',')
  aid = arr[0]
  aid_set.add(aid)
  pids = (arr[1]).split(' ')
  for pid in pids:
    pid_set.add(pid)


fo = open('./data/pig_author', 'w')
for line in open('../../postdata/author2.txt'):
  aid = line.strip().split(',')[0]
  if aid in aid_set:
    fo.write(line)
fo.close()

fo = open('./data/pig_match', 'w')
for line in open('../../postdata/match2.txt'):
  pid = line.strip().split(',')[0]
  if pid in pid_set:
    fo.write(line)
fo.close()
  
conf_set, jour_set = set(), set()
fo = open('./data/pig_paper', 'w')
for line in open('../../postdata/paper2.txt'):
  arr = line.strip().split(',')
  pid = arr[0]
  if pid in pid_set:
    fo.write(line)
  conf, jour = arr[2], arr[3]
  if conf: conf_set.add(conf)
  if jour: jour_set.add(jour)
fo.close()
  
fo = open('./data/pig_conference', 'w')
for line in open('../../postdata/conference2.txt'):
  cid = line.strip().split(',')[0]
  if cid in conf_set:
    fo.write(line)
fo.close()

fo = open('./data/pig_journal', 'w')
for line in open('../../postdata/journal2.txt'):
  cid = line.strip().split(',')[0]
  if cid in jour_set:
    fo.write(line)
fo.close()

