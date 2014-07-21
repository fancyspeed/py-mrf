import sys

def predict(p_pred):
  key_score = {}

  for line in open(p_pred):
    pred, aid, pid = line.strip().split('\t')

    pred = float( pred ) 
    if aid not in key_score:
      key_score[aid] = []
    key_score[aid].append( (pid, pred) )

  return key_score

def construct(p_out, key_score):
  f_out = open(p_out, 'w')
  for aid in key_score:
    sort_list = sorted(key_score[aid], key=lambda d:d[1], reverse=True)
    pid_list = [k for k, v in sort_list]
    new_line = '%s,%s\n' % (aid, ' '.join(pid_list))
    f_out.write(new_line)
  f_out.close()

if __name__ == '__main__':
  if len(sys.argv) >= 2:
    key_score = predict('./tmp/pig_mrf_pred')
    construct('./tmp/pig_mrf_result', key_score)
  else:
    key_score = predict('./tmp/cat_mrf_pred')
    construct('./tmp/cat_mrf_result', key_score)

