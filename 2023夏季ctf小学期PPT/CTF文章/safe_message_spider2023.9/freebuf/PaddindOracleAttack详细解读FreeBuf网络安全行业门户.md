# Paddind Oracle Attack详细解读

## 适用条件

  * 加密方式为AES.CBC模式
  * 已知加密后的cipher
  * 已知加密时初始的iv

## 攻击原理

如果明文过长，需要一个块一个块的进行解密，只是iv发生了变换，其中的过程一模一样

对于每一块的明文，从后向前一位一位的解密

先看CBC经典图

![0x00.png](https://image.3001.net/images/20201129/1606628767_5fc3359f65cf5e99f7ba9.png!small)

在加密时

![1606626434_5fc32c82632e225c55535.png!small?1606626434007](https://image.3001.net/images/20201129/1606626434_5fc32c82632e225c55535.png!small?1606626434007)

在解密时![1606626442_5fc32c8a181adf7feb28c.png!small?1606626441693](https://image.3001.net/images/20201129/1606626442_5fc32c8a181adf7feb28c.png!small?1606626441693)

## 攻击实现

存在一个服务器，会返回密文解密后的正确与否（padding），随后返回解密的状态，我们就可以通过该种方式取得加密后且与iv异或之前的中间态`I`，那么我们发现`I=C⊕P`，而`C`已知，我们就可以通过异或来得到原来的明文`P`，所以接下来的主要矛盾即是求得这个中间态`I`。

我们选择构建iv=`\x00`*16，将这个iv发送给服务器后会进行padding测试，假设`P`的最后一位为`X`，那么当且仅当padding后的结果为`0x01`时（`P⊕i⊕0x01`），服务器才会判定正确，那么我们即可对该位iv进行爆破测试，当服务器返回正确时，我们很大几率上是得到了正确的`I`了，所以我们从最低位开始枚举，当该位正确时，接着向前一位开始枚举，知道全部位被取得时，也就是`I`已知的时候了，最后利用`I⊕IV`即可得到该块的明文`P`了。

随后将`IV`改为上一个块的密文，重复上述操作即可。

## 例题

### 1\. 0xGame Padding Oracle

这里放一道标准实例题，相关分析如上，这里演示下具体操作。

![14.png](https://image.3001.net/images/20201129/1606628772_5fc335a46c5db0dcf79ee.png!small)

胡乱分析.jpg

  

这里因为懒，所以手动改代码后多跑了几遍，因为这玩意爆破一次时间长得离谱，debug噩梦

    
    
    from string import digits, ascii_letters
    
    
    from pwn import *
    
    
    from hashlib import sha256
    
    
    from Crypto.Util.number import *
    
    
    import os
    
    
    ​
    
    
    table = digits+ascii_letters
    
    
    r = remote("49.235.239.97", "10003")
    
    
    ​
    
    
    def proof_of_work():
    
    
    rev = r.recvuntil("sha256(XXXX+")
    
    
    suffix = r.recv(16).decode()
    
    
    r.recvuntil(" == ")
    
    
    res = r.recv(64).decode()
    
    
    def f(x):
    
    
    hashresult = hashlib.sha256((x+suffix).encode()).hexdigest()
    
    
    if hashresult == res:
    
    
    return 1
    
    
    else:
    
    
    return 0
    
    
    prefix = util.iters.mbruteforce(f,table,4,'upto')
    
    
    r.sendline(str(prefix))
    
    
    ​
    
    
    def read_data():
    
    
    r.recvuntil("iv : ")
    
    
    iv = r.recvuntil('\n')[:-1].decode()
    
    
    iv = bytearray.fromhex(iv)
    
    
    r.recvuntil("crypttext : ")
    
    
    qwq = r.recvuntil('\n')[:-1].decode()
    
    
    cbc = bytearray.fromhex(qwq)
    
    
    return iv,cbc,qwq
    
    
    ​
    
    
    proof_of_work()
    
    
    print('Successfully pass the pow!')
    
    
    iv,cbc,qwq=read_data()
    
    
    mid = []
    
    
    print('Successfully read the data!')
    
    
    #print('iv =',iv)
    
    
    #print('cbc =',cbc)
    
    
    #print(cbc.hex()[64:])
    
    
    ​
    
    
    r.recvuntil('> ')
    
    
    ​
    
    
    iv = bytearray.fromhex(qwq)[16:32]
    
    
    print(iv)
    
    
    new_iv = bytearray(b'\x00'*16)
    
    
    count = 1
    
    
    for i in range(16):
    
    
    for j in range(256):
    
    
    new_iv[15-i] = j
    
    
    r.sendline('1')
    
    
    r.recvuntil('(in hex): ')
    
    
    r.sendline(str(new_iv.hex()))
    
    
    r.recvuntil('(in hex): ')
    
    
    r.sendline(str(cbc.hex()[64:96]))
    
    
    back = r.recvline(keepends = False)
    
    
    r.recvuntil('> ')
    
    
    if(b'success' in back):
    
    
    print(back,j)
    
    
    ans = j ^ count
    
    
    break
    
    
    count += 1
    
    
    mid.append(ans)
    
    
    for m in range(15-i,16):
    
    
    new_iv[m] = count ^ mid[15-m]
    
    
    find = ''
    
    
    for i in range(16):
    
    
    find += hex(iv[i] ^ mid[15 - i])[2:].rjust(2,'0')
    
    
    flag = bytearray.fromhex(find)
    
    
    print(flag)
    
    
    r.interactive()

  

