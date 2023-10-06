import os

todo = ['match', 'adds']
for i in todo:
    fs = os.listdir(i)

    j = (os.listdir(os.path.join('data/train/', i)))
    j = max(int(f.split('.')[0].split(' ')[0]) for f in j) + 1
    for f in fs:
        os.rename(os.path.join(i, f), os.path.join('data/train', i, str(j) + '.png'))
        j += 1
        