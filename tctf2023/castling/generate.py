import string

# this is the set of caracters to use for generating collisions
chars = (string.ascii_lowercase+string.ascii_uppercase+string.digits)

def djbx33a(s):
    '''calculate djbx33a hash from string'''
    h = 5381
    for c in s:
        h += (h <<5) + ord(c)
        h &= 0xFFFFFFFF
    return h

def dohash(msg):
    from task import thisishash
    h = thisishash()
    res = h.hash(msg)
    return res

def find_collisions(length=2):
    '''Find the biggest set of strings of length chars that give the same hash
    '''
    hashes = {}
    best_hash, max_collitions = 0,0
    idxs = [0]*length
    while 1:
        name = ''.join(map(lambda x: chars[x],idxs))
        h = bytes(name,'utf-8')
        h = dohash(h)
        if h in hashes:
            hashes[h].append(name)
            if len(hashes[h]) > max_collitions:
                best_hash,max_collitions = h,len(hashes[h])
                print("best_hash: ",best_hash,max_collitions,hashes[h])
        else:
            hashes[h] = [name]

        i = 0
        while i < length:
            idxs[i] = (idxs[i]+1)%len(chars)
            if idxs[i] != 0:
                break
            i+=1

        if i == length:
            # we've looped over all strings
            return hashes[best_hash]

def make_combinations(dataset, limit):
    '''Combine the string in dataset until we have a given number of them,
    all the strings in the returned set are made of the same number of
    substrings
    '''
    values = ['']
    while 1:
        res = []
        for d in values:
            for i in dataset:
                res.append(d+i)
                if len(res) == limit:
                    return res
        values = res

def main():
    # find collision strings of length 3
    length = 3
    values = find_collisions(length)
    print(values)
    print("found %d collisions of length %d"%(len(values),length))

    # combine them
    keys = make_combinations(values, 20000)
    
    print("keys, ",keys)

    post = {}
    for k in keys: post[k] = ''

    with open('postdata.py', 'w') as f:
        f.write('post = '+str(post))
        print("generated",len(keys),"hash collisions")

if __name__ == '__main__':
    # main()
    msg0="bbbbaa"
    h = bytes(msg0,'latin-1')
    print(h.hex())
    h = dohash(h)
    print(h)
    msg1="bbbcaa"
    h = bytes(msg1,'latin-1')
    print(h.hex())
    h = dohash(h)
    print(h)
    if msg0!=msg1 and dohash(bytes(msg0,'utf-8')) == dohash(bytes(msg1,'utf-8')):
        print("2333")
        
    # print(msg0.encode('latin-1').hex())
    # print(msg1.encode('latin-1').hex())