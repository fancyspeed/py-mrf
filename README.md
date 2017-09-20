Simple MRF implementation.

## Data Format

### site:

* score gid:1 pid:2 feat:value feat:value ...

### edge:

* gid:1 pid:2 nid:3 feat:value feat:value ...

* gid means group, pid means point, nid means neighbour.


I transform MRF as a Logistic Regression Problem, by adding points' neighbours' feature weights to itself.

