import random

def MAP(p_result, p_truth):
  acc_dict = {}
  for line in open(p_truth): 
    aid, accept, reject = line.strip().split(',') 
    arr = accept.strip().split(' ')
    if not arr[0]:
      rr = []
    acc_set = set(arr)
    acc_dict[aid] = acc_set

  map_dict = {} 
  for line in open(p_result):
    aid, submit = line.strip().split(',')
    if aid not in acc_dict: continue
    if aid in map_dict: continue

    sub_list = submit.strip().split(' ')
    #random.shuffle(sub_list)
    n_right = 0
    marked = set()
    for i in range( len(sub_list) ):
      if sub_list[i] not in marked and sub_list[i] in acc_dict[aid]:
        n_right += 1
        map_dict[aid] = map_dict.get(aid, 0) + n_right / (i + 1.0) 
        marked.add(sub_list[i])

    if len(acc_dict[aid]) == 0:
      map_dict[aid] = 1 
    else:
      map_dict[aid] = map_dict[aid] / len(acc_dict[aid]) 
  
  tot_map = 0
  for aid, score in map_dict.items():
    tot_map += score
  return tot_map / len(map_dict)
      
if __name__ == '__main__':
  import sys
  if len(sys.argv) < 3:
    print '<usage> p_result p_truth'
    exit(-1)
  map_score = MAP(sys.argv[1], sys.argv[2])
  print 'map:', map_score

