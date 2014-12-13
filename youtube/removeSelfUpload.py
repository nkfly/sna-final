from os.path import isfile

with open('info/users.txt') as f_in:
    user_list = map(lambda x: x.strip(), f_in)

for uid in user_list:
    print '\r',uid,
    ignore_list = []
    if isfile('video_id/' + uid + '.uploads'):
        with open('video_id/' + uid + '.uploads') as f_in:
            ignore_list.extend(map(lambda x: x.strip(), f_in))
    keep_list = []
    if isfile('video_id/' + uid + '.favorites'):
        with open('video_id/' + uid + '.favorites') as f_in:
            keep_list.extend(map(lambda x: x.strip(), f_in))
    to_add_list = []
    if isfile('video_id/' + uid + '.likes'):
        with open('video_id/' + uid + '.likes') as f_in:
            to_add_list.extend(map(lambda x: x.strip(), f_in))
    to_add_list = [x for x in to_add_list if x not in keep_list]
    keep_list.extend(to_add_list)
    keep_list = [x for x in keep_list if x not in ignore_list]
    if len(keep_list) == 0: continue
    with open('video_id_no_upload/' + uid, 'w') as f_out:
        for vid in keep_list:
            f_out.write(vid + '\n')
