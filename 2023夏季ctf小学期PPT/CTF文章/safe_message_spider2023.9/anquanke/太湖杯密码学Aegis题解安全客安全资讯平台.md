# 太湖杯密码学 Aegis 题解

阅读量 **285487**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-19 15:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t015c87745ee4cd9a52.jpg)

## Aegis

整个出题的题目参考了googlectf 2020
Oracle的题目。由于考虑到比赛时长的问题（其实是作者比较菜），基本上是将其中的一个考点拿了出来修改成了当前的题目。针对那个题目比较完整的解法可以参考[这里](https://github.com/nguyenduyhieukma/CTF-Writeups/blob/master/Google%20CTF%20Quals/2020/oracle/oracle-solution.ipynb)
这个地方也有这个算法的比较详细的解释。

###  算法简介

AEGIS 算法是一种AEAD（authenticated encryption with associated data 关联数据的认证加密）
加密。这种算法除了能够提供对指定明文的加密，还能够提供对未加密的关联数据的完整性保证。说通俗一点就是，除了能够对我们发送的需要加密的信息进行加密，同时还提供了对我们明文信息的长度和时间这些未加密的数据进行验证的手法。当我们将密文解开的时候，会包含一个之前提供的明文信息的验证途径，例如能够得到长度的一个验证数据，我们此时就能够用这个数据验证我们之前未加密的长度的完整性。  
在题目中，我们能看到两种不同的值:pt和aad

    
    
    ct, tag = cipher.encrypt(iv, aad, pt)
    

此处的pt表示的就是我们通常意义下的明文，而这里的aad，实际上就是`authenticated associated
data`，认证关联数据。这个数据会参与到整个加密过程中，用于生成状态。  
ct表示的是加密后的密文，tag则是在加密完成后的状态算法中生成的校验标签，可以用来校验aad的值是否发生变化。

关于aad的验证算法可以初步看一下加密过程。

    
    
      def encrypt(self, iv, ad, msg):
        S = self.initialize(iv)
        S = self.update_aad(S, ad)
        S, ct = self.raw_encrypt(S, msg)
        tag = self.finalize(S, len(ad) * 8, len(msg) * 8)
        return ct, tag
    
      def decrypt(self, iv, ad, ct, tag):
        S = self.initialize(iv)
        S = self.update_aad(S, ad)
        S, pt = self.raw_decrypt(S, ct)
        tag2 = self.finalize(S, len(ad) * 8, len(ct) * 8)
        if tag2 != tag:
          raise Exception('Invalid tag')
        return pt
    

由于在加密或者解密过程中，aad值参与了最初加密状态的生成，所以aad值在不变的前提下，加解密中状态（State）变化是一致的，最后阶段算出来的 tag2
理论上会和我们传入的tag一致，就是利用这一点来保证aad的完整性。

###  Aegis128的算法

想要明白当前的算法的漏洞，需要先看明白当前加密算法原理。整个加密中会维护一个 **状态**
的概念，然后我们需要加密的内容会类似一些向量来影响整个状态，从而对明文完成加密。那么首先，为了更加方便的描述加密过程，我们需要预先定义一些变量:

    
    
    S[i]: 第i步更新的状态
    S[i][j]: 第i步状态中，第j块128bit分组
    ^: 状态之间异或运算
    &: 状态的与运算
    const0: 128bit的一个魔数（0x000101020305080d1522375990e97962）
    const1: 128bit的一个魔数（0xdb3d18556dc22ff12011314273b528dd）
    

Aegis有三种不同的加密方式，我们这里使用的是128版本

####  状态更新 StatusUpdate

Aegis加密算法中，一个重要的概操作就是状态更新StateUpdate。当这个过程发生的时候，其更新算法如下:

    
    
    m: 一个128bit的信息
    S[i+1] = StatueUpdate(S[i], m)
    S[i+1][0] = S[i][0]^AESRound(S[i][4])^m
    S[i+1][1] = S[i][1]^AESRound(S[i][0])
    S[i+1][2] = S[i][2]^AESRound(S[i][1])
    S[i+1][3] = S[i][3]^AESRound(S[i][2])
    S[i+1][4] = S[i][4]^AESRound(S[i][3])
    

这个更新过程的流程大致可以写作如下:

![](https://p4.ssl.qhimg.com/t01d50ecb370d157793.png)

####  初始化过程

整个算法的更新，首先使用密钥K128与初始化向量IV128进行一些运算，最终产生整个算法的初始状态。此时的K128为我们加密算法的密钥，IV128为一个可变的向量。整个生成的过程可以写作:

    
    
    def initialize(self, iv):
        k_iv = _xor(self.key, iv)
        S = [k_iv,
             self.const_1,
             self.const_0,
             _xor(self.key, self.const_0),
             _xor(self.key, self.const_1)]
        for _ in range(5):
          S = self.state_update(S, self.key)
          S = self.state_update(S, k_iv)
        return S
    

根据代码，我们可以写作:

    
    
    S[-5][0] = k128^iv128
    S[-5][1] = const_1
    S[-5][2] = const_0
    S[-5][3] = k128^const_0
    S[-5][4] = k128^const_1
    
    for i in range(5)
        S[-5+i+1] = StatueUpdate(S[-4+i], k128)
        S[-5+i+1] = StatueUpdate(S[-4+i+1], k128^iv128)
    

这里写作-4，主要是为了可以同步，保证我们在起始状态下为`S[0]`。

###  Aegis 中的AES

我们来仔细看一下Aegis中的AES算法。首先来看到官方给出的aes:

    
    
    def aes_enc(s: block, round_key: block) -> block:
      """Performs the AESENC operation with tables."""
      t0 = (te0[s[0]] ^ te1[s[5]] ^ te2[s[10]] ^ te3[s[15]])
      t1 = (te0[s[4]] ^ te1[s[9]] ^ te2[s[14]] ^ te3[s[3]])
      t2 = (te0[s[8]] ^ te1[s[13]] ^ te2[s[2]] ^ te3[s[7]])
      t3 = (te0[s[12]] ^ te1[s[1]] ^ te2[s[6]] ^ te3[s[11]])
      s = _block_from_ints([t0, t1, t2, t3])
      return _xor(s, round_key)
    

`te0[s[0]],te1[s[1]]`这些就相当于是s盒，按照`s0,s5,s10,s15`这种顺序取值相当于是行位移(shift)，取值进行异或就相当于是列混淆(mix_column)。整个过程我们大致写下来就是:

    
    
    AES(m) = mix_column(shift(Sbox(m)))
    

实际上就是AES加密算法中，除去 **密钥交换** 这一步之后的剩余步骤。并且我们知道，整个Aegis加密中，AES参与的方式为:

    
    
    if j != 0
    S[i+1][j] = AES(S[i][(j+4)%5])
    else
    S[i+1][j] = AES(S[i][(j+4)%5]) ^ mi
    

于是我们可以简写成如下的运算:

    
    
    if j != 0
    C = AES(M)
    else
    C = AES(M)^m
    

那假设此时，我们的M发生了一些变化，我们这里将变化的差值写作`dM`，此时有

    
    
    M1 = M^dM
    

对M1的加密就可以写成:

    
    
    if j != 0
    C1 = AES(M1) = AES(M^dM)
    else
    C1 = AES(M1)^m = AES(M^dM)^m
    

C1、C均为我们可以得到的具体值，如果我们能够通过控制加密的内容，使得dM可控（之后会展示） **我们就有机会能够推导出M的值** 。具体的做法如下:

    
    
    1. 将C1^C，此时消除了m的影响，存在公式
    C1^C = AES(M^dM)^AES(M)
    2. AES = mix_column(shift(Sbox(m)))
    然而首先我们知道，mix_column本身也是异或运算得到的结果，也就是说满足
    mix_column(x)^mix_column(x^dx) = mix_column(dx)
    而shift只是位移操作，所以也可满足
    shift(x)^shift(x^dx) = shift(dx)
    所以实际上可以写作
    C1^C = AES(M^dM)^AES(M) = Sbox(M^dM)^Sbox(M)
    

然而实际上，Sbox运算是可以被爆破的。假设我们能知道dM，那我们只需要爆破16个字节，最终就能推导出M的值

###  Aegis的加密过程

由于Aegis128加密中的最小单位为128bit，也就是16字节，所以加密之前会将当前的明文填充至16的倍数。之后，每16个字节的加密手法如下:

    
    
    for i in range(0, len16(msg), 16):
        Ci = (S2 & S3) ^ S1 ^ S4 ^ mi
        Si+1 = StatusUpdate(Si, mi)
    

注意一个细节，这边为了防止S0的参与导致加密算法被利用，所以在加密过程中故意抛弃了S0。  
加密结束之后，更新当前状态块。这里参考一个图可能会更加清晰:

![](https://p3.ssl.qhimg.com/t0142e426183e15748b.png)

`p[i][0]`为我们按照16字节分组的第i组明文输入，`k[0][0]`表示第0组的明文加密得到的密文。这里注意，我们的明文的
**第0组实际上参与了第一组密文的生成，并且还影响了第1组的状态**
。图上的红框表示的就是，当我们的输入`p[0][0]`发生变化的时候，实际上会影响的状态。从图上可知，当输入`p[0][0]`变化的时候，实际上会影响的是:`s[1][0],
s[2][0], s[2][1], k[2][0]（这个地方应该写作k[2]，可能是图片作者写错了）`

参考源码：

    
    
    def raw_encrypt(S, msg):
        ct_blocks = []
        for i in range(0, len(msg), 16):
          blk = msg[i:i+16]
          mask = Aegis128.output_mask(S)
          if len(blk) < 16:
            mask = mask[:len(blk)]
            p = blk + bytes(16 - len(blk))
          else:
            p = blk
          ct_blocks.append(_xor(mask, blk))
          S = Aegis128.state_update(S, p)
        return S, b''.join(ct_blocks)
    
    def encrypt(self, iv, ad, msg):
        S = self.initialize(iv)
        S = self.update_aad(S, ad)
        S, ct = self.raw_encrypt(S, msg)
        tag = self.finalize(S, len(ad) * 8, len(msg) * 8)
        return ct, tag
    

###  Ageis的漏洞点

加密流程中，IV和key都不会更新，并且加密7次。最终目的是让我们求出当使用了空的aad进行了StateUpdate状态后得到的初始状态，也就是状态`S[1]`。  
这一类IV、key不发生变化的题目，其实传达的一个含义就是 **加密算法本身是不变的，即是说对于加密算法`C =
F(m)`，这个F是不变量，而此时的m和C都是已知的，就有机会构造合适的m，从而泄露F中的一些信息**

####  第一步泄露

这里重新展示一下之前用来描述加密的那张图，这里我们着重关注的是变化值:

可以看到，当`p[0][0]`变化的时候，`s[1][0], s[2][0], s[2][1], k[2]`均会收到影响。这里我们复习一下这几个值的关系:

    
    
    （1）k[2] = (S[2][2] & S[2][3]) ^ S[2][1] ^ S[2][4] ^ p[2][0]
    （2）k[1] = (S[1][2] & S[1][3]) ^ S[1][1] ^ S[1][4] ^ p[1][0]
    （3）S[2][0] = AESRound(S[1][4])^S[1][0]^p[1][0]
    （4）S[1][0] = AESRound(S[0][4])^S[0][0]^p[0][0]
    

  * 由于（2）我们可以知道，`S[1][0]`并不参与到整个加密过程中，所以不会对加密本身有影响，因此`k[1]`的值不发生变化
  * 此时生成的密文`kd[2]`虽然发生了变化，但是其变化 **仅仅是因为`S[2][1]`发生了变化**，因为在StateUpdate中，只有`S[2][1]`会受到输入的影响，其他的状态并不收到当前的输入状态影响:

这里我们将变化后的p写作`dp`，并且满足`dtp = dp^p`，发生了相应变化的变量都加上`d`的前缀，于是此时有：

    
    
    kd[2] ^ k[2] = S[2][1] ^ Sd[2][1] = AESRound(S[1][0])^AESRound(Sd[1][0])
    

此时我们的`kd[2] ^ k[2]`是已知量。而我们此时知道

    
    
    （5）AESRound(S[1][0])^AESRound(Sd[1][0]) = Sbox(S[1][0])^Sbox(Sd[1][0])
    （6）S[1][0] = AES(S[0][4]) ^ S[0][0] ^ p[0][0]
    

由于（6）中，`S[0][0], S[0][4]`在IV和key不变的情况下，即使我们更改p也不会发生变化，所以实际上可以推出

    
    
    （7）Sd[1][0]^S[1][0] = p[0][0]^dp[0][0] = dtp[0][0]
    ====> Sd[1][0] = S[1][0] ^ dtp[0][0]
    

于是我们可以将（5）推到成

    
    
    （8）Sbox(S[1][0])^Sbox(Sd[1][0]) = Sbox(S[1][0])^Sbox(S[1][0]^dpt[0][0]) = kd[2]^k[2]
    

在（8）这个算式中，`dpt，kd，k`三个值我们都知道，于是我们只需要爆破`S[1][0]`中的16字节即可。  
不过经过测试，直接爆破是存在多解的情况，所以我们可以 **增加一个变化，也就是dpt2，两次的结果综合考虑**
。经过测试，这种方式能够得到唯一的`S[1][0]`

    
    
    def resolve(dk_1, ds_1, dk_2, ds_2):
        # here we check the 
        tmpk = aes.bytes2matrix(dk_1)
        aes.inv_mix_columns(tmpk)
        aes.inv_shift_rows(tmpk)
        d_k1 = aes.matrix2bytes(tmpk)
    
        tmpk = aes.bytes2matrix(dk_2)
        aes.inv_mix_columns(tmpk)
        aes.inv_shift_rows(tmpk)
        d_k2 = aes.matrix2bytes(tmpk)
        # result should be unique
        res = bytearray(16)
        # try to bruce it
        for i in range(16):
            x1 = set()
            for c in range(256):
                if aes.s_box[c] ^ aes.s_box[c^ds_1[i]] == d_k1[i] and aes.s_box[c] ^ aes.s_box[c^ds_2[i]] == d_k2[i]:
                    x1.add(c)
            res[i] = x1.pop()
        assert(len(res) == 16)
        return bytes(res)
    

####  进一步泄露

由于我们有7次通信机会，目前可以如下安排

  * 第一次：我们一口气通信获得`k[0],k[1],k[2],k[3],k[4]`，此时我们可以将`p`设置为全0，这样的话能够帮助我们之后更加方便的进行计算
  * 第二、三次： 得到`S[1][0]`
  * 第四、五次： 得到`S[2][0]`
  * 第六、七次： 得到`S[3][0]`

我们可以如法炮制，通过修改`p[1][0],p[2][0]`，得到`S[2][0],S[3][0]`。此时我们有公式:

    
    
    （3）S[2][0] = AESRound(S[1][4])^S[1][0]^p[1][0] ==> 直接逆运算，可得S[1][4]
    （9）S[3][0] = AESRound(S[2][4])^S[2][0]^p[2][0] ==> 利用之前的技巧，可得S[2][4]
    （10）S[2][4] = AESRound(S[1][3])^S[1][4] ==> 直接逆运算，可得S[1][3]
    

此时我们就有了`S[1][0], S[1][3], S[1][4]`，并且题目中泄露了`S[1][2]`，所以我们最终利用

    
    
    （11）C[1] = (S[2][0] & S[3][0]) ^ S[1][0] ^ S[4][0] ^ pt[0]
    

就能得到最后的`S[1][1]`，此时整个题泄露完成。

    
    
    import aes
    import os
    import aegis
    from aegis import _xor,_and
    from pwn import *
    import base64
    
    
    
    def R(x):
        tmp = aes.bytes2matrix(x)
        aes.sub_bytes(tmp)
        aes.shift_rows(tmp)
        aes.mix_columns(tmp)
        return aes.matrix2bytes(tmp)
    
    
    def invR(x3):
        tmp = aes.bytes2matrix(x3)
        aes.inv_mix_columns(tmp)
        aes.inv_shift_rows(tmp)
        aes.inv_sub_bytes(tmp)
        return aes.matrix2bytes(tmp)
    
    def resolve(dk_1, ds_1, dk_2, ds_2):
        # here we check the 
        tmpk = aes.bytes2matrix(dk_1)
        aes.inv_mix_columns(tmpk)
        aes.inv_shift_rows(tmpk)
        d_k1 = aes.matrix2bytes(tmpk)
    
        tmpk = aes.bytes2matrix(dk_2)
        aes.inv_mix_columns(tmpk)
        aes.inv_shift_rows(tmpk)
        d_k2 = aes.matrix2bytes(tmpk)
        # result should be unique
        res = bytearray(16)
        # try to bruce it
        for i in range(16):
            x1 = set()
            for c in range(256):
                if aes.s_box[c] ^ aes.s_box[c^ds_1[i]] == d_k1[i] and aes.s_box[c] ^ aes.s_box[c^ds_2[i]] == d_k2[i]:
                    x1.add(c)
            res[i] = x1.pop()
        assert(len(res) == 16)
        return bytes(res)
    
    def encrypt(ph, aad, pt):
        ph.sendline(base64.standard_b64encode(pt))
        ph.sendline(base64.standard_b64encode(aad))
        ct = ph.recvline(keepends=False)
        ct = base64.standard_b64decode(ct.decode('utf-8'))
        tag = ph.recvline(keepends=False)
        tag = base64.standard_b64decode(tag.decode('utf-8'))
        return ct, tag
    
    
    def decrypt(ph, aad, pt, index, ct):
        left_index = (index+1)*16
        right_index = (index+2)*16
        enc, tag = encrypt(ph, aad, pt[2*index-1])
        # print("enc[{}:{}]".format(left_index/32,right_index/32))
        # print("pt[{}:{}]".format(2*index-1, 2*index))
        ct1_2 = enc[left_index:right_index]
        # encrypt 3
        enc, tag = encrypt(ph, aad, pt[2*index])
        # print(pt[2*index])
        ct1_3 = enc[left_index:right_index]
        # decrypt s10
        # print(ct)
        # print(ct1_2)
        # print(ct)
        # print(ct1_2)
        dk1 = _xor(ct,ct1_2)
        dk2 = _xor(ct,ct1_3)
        # split S1/S5
        # pt split ,too
        s = resolve(dk1, pt[2*index-1][16*(index-1):16*(index)], 
                    dk2, pt[2*index][16*(index-1):16*(index)])
        return s
    
    def localTest():
        ph = remote("127.0.0.1",'10090')
        pt = []
        padding = b'\x00'*16
        p0 = b'\x00'*16
        p1 = b'\x00'*16
        p2 = b'\x00'*16
        pt.append(p0+p1+p2+padding*2)
        # for i in range(1,7):
        # pt.append(bytes([i%2+1]*16)+padding)
        # for s10
        pt.append(bytes([1]*16)+padding+padding)
        pt.append(bytes([2]*16)+padding+padding)
        # for s20
        pt.append(padding+bytes([1]*16)+padding+padding)
        pt.append(padding+bytes([2]*16)+padding+padding)
        # for s30
        pt.append(padding+padding+bytes([1]*16)+padding*2)
        pt.append(padding+padding+bytes([2]*16)+padding*2)
        iv = ph.recvline(keepends=False)
        aad = b''
    
        # encrypt 1
        enc, tag = encrypt(ph, aad, pt[0])
        print(enc)
        ct = []
        for i in range(5):
            ct.append(enc[i*16:(i+1)*16])
    
        s10 = decrypt(ph, aad, pt, 1, ct[2])
        # decrypt 2 
        s20 = decrypt(ph, aad, pt, 2, ct[3])
        # decrypt 3
        s30 = decrypt(ph, aad, pt, 3, ct[4])
        # s20 = s10 xor R(s14) ==> s14 = invR(s20 xor s10)
        s14 = invR(_xor(s20, s10))
        # s30 = s20 xor R(s24) ==> s24 = invR(s20 xor s30)
        # s24 = s14 xor R(s13) ==> s13 = invR(s14 xor s24)
        s24 = invR(_xor(s20, s30))
        s13 = invR(_xor(s24, s14))
        ph.recvuntil("Oops, something leak:")
        s12 = ph.recvline(keepends=False)
        print(s12)
        s12 = base64.standard_b64decode(s12.decode('utf-8'))
        # if pt = 00 then enc1 = (s12&s13) xor s14 xor s11
        # -> s11 = enc1 xor s14 xor (s12&s13)
        enc1 = enc[16:16*2]
        s11 = _xor(s14, _xor(enc1, _and(s12, s13)))
        # s15 = _xor(s12, _xor(enc12, _and(s16, s17)))
        s1 = s10+s11+s12+s13+s14
        ph.sendline(base64.standard_b64encode(s1))
        ph.interactive()
    
    if __name__ == "__main__":
        localTest()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **l1nk3d** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222629](/post/id/222629)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [crypto](/tag/crypto)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t011f01b6fb65071cb1.png) l1nk3d

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

