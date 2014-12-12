from os import listdir, remove
import os.path

i = 0
for fname in listdir('video_info'):
    vid = fname[:11]
    if os.path.isfile('video_info/'+vid): continue
    print '\r',i,vid,
    with open('video_info/'+vid, 'w') as f_out:
        with open('video_info/'+vid+'.title') as f_in:
            for line in f_in:
                f_out.write('<title>\t'+line+'\n')
        with open('video_info/'+vid+'.meta') as f_in:
            for line in f_in:
                f_out.write(line)
        with open('video_info/'+vid+'.desc') as f_in:
            lines = map(lambda x: x.strip(), f_in.readlines())
            f_out.write('<description>\t'+' '.join(lines)+'\n')
    remove('video_info/'+vid+'.title')
    remove('video_info/'+vid+'.meta')
    remove('video_info/'+vid+'.desc')
    i += 1
