***本文原创作者：Abyss0，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x01前言

 **刷题遇到CBC字节翻转攻击，就去查了资料，然后自己做了份整理，只是看原理有点枯燥，就写了点样例代码，顺便练习一下Python。**

原理部分写的比较简单，所以就先附上参考的内容吧

> <http://resources.infosecinstitute.com/cbc-byte-flipping-> attack-101-approach/>  
>
>
> 《白帽子讲Web安全》

## 0x02CBC模式介绍

 **加密过程：**

![image.png](https://image.3001.net/images/20180228/15198072135832.png!small)  

**Plaintext：** 明文数据

 **IV：** 初始向量

 **Key：** 分组加密使用的密钥

 **Ciphertext：** 密文数据

明文都是先与混淆数据（第一组是与IV，之后都是与前一组的密文）进行异或，再执行分组加密的。

### 解密过程：

每组解密时，先进行分组加密算法的解密，然后与前一组的密文进行异或才是最初的明文。

对于第一组则是与IV进行异或。

## 0x03攻击介绍

### 对于解密时：

设明文为X，密文为Y，解密函数为k。

X[i] = k(Y[i]) Xor Y[i-1]

### 解密第一组时：

X[1]=k(Y[1]) Xor IV

对于X[i]的解密时，X[i] = k(Y[i]) Xor
Y[i-1]，k(Y[i])部分是无法控制的，假如修改Y[i]的值，是无法确定k(Y[i])的值，由于最后是异或操作，因此可以仅修改Y[i-1]的内容为Y'[i-1]来控制最后的明文的值，设解密后的内容为M[i]=k(Y[i])
Xor Y[i-1]。

将Y[i-1]的值设置为Y[i-1] Xor M[i]的值，新的Y[i-1]的值用Y'[i-1]表示。

那么X[i] = k(Y[i]) Xor Y'[i-1]=k(Y[i]) Xor Y[i-1] Xor M[i] = M[i] Xor M[i] = 0

这样就能将只修改Y[i-1]的内容来控制X[i]的值

而此时X[i-1]的值肯定就会出错了，设修改Y[i-1]的值，导致解密后X[i-1]的值为M[i-1]，那么将Y[i-2]的值改为Y[i-2]=Y[i-2]
Xor M[i-1] Xor 任意值，可以使得X[i-1]=任意值

这样循环往前，最后一组就是根据M[1]的值修改IV=IV Xor M[1] Xor 任意值，使得X[1]=任意值

## 0x04代码示例

代码：

    
    
    #coding:utf-8
    from Crypto.Cipher import AES
    from binascii import b2a_hex,a2b_hex
    
    def encrypt(iv,plaintext):
        if len(plaintext)%16 != 0:
            print "plaintext length is invalid"
            return
        if len(iv) != 16:
            print "IV length is invalid"
            return
        key="1234567890123456"
        aes_encrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_encrypt.encrypt(plaintext))
    
    def decrypt(iv,cipher):
        if len(iv) != 16:
            print "IV length is invalid"
            return
        key="1234567890123456"
        aes_decrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_decrypt.decrypt(a2b_hex(cipher)))
    
    def test():
        iv="ABCDEFGH12345678"
        plaintext="0123456789ABCDEFhellocbcflipping"
        cipher=encrypt(iv, plaintext)
        print cipher
        de_cipher = decrypt(iv, cipher)
        print de_cipher
        print a2b_hex(de_cipher)
    
    test()
    

定义了加密与解密方法，对于调用方法的人来说（比如test方法），可以定义IV，明文，密文，但是不知道key是多少

 **测试结果如下：**

![Image
\[1\].png](https://image.3001.net/images/20180228/15198084772453.png!small)

现在使用cbc字节翻转攻击使得最后的字符g变为大写

g是第二组的第16个字节，最后异或的是第一组密文的第16个字节，也就是cipher[15]，因此需要将该字节修改为cipher[15] Xor
ord('g') Xor ord('G')

修改test方法，增加一些内容

    
    
    def test():
        iv="ABCDEFGH12345678"
        plaintext="0123456789ABCDEFhellocbcflipping"
        cipher=encrypt(iv, plaintext)
        print "cipher:"+cipher
        de_cipher = decrypt(iv, cipher)
        print "de_cipher:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 start-----------------------------------        bin_cipher = bytearray(a2b_hex(cipher))
        bin_cipher[15] = bin_cipher[15] ^ ord('g') ^ ord('G')
        de_cipher = decrypt(iv,b2a_hex(bin_cipher))
        print "de_cipher2:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 end-------------------------------------    

代码结果：

![Image
\[2\].png](https://image.3001.net/images/20180228/15198092566010.png!small)  

虽然字体变小了，但是可以看到第二组明文解密之后的，最后一个字母变为大写了，但是因为修改了第一组的密文，所以第一组解密时变成乱码了

此时可以修改IV的值来控制第一组密文解密后的结果，但是需要de_cipher2的内容，如果是将前十六个字节都修改为"X"，那么需要将IV与de_cipher2相应下标的值进行异或再与ord('X')进行异或，最后的结果就是新的IV的值

再次修改test方法，增加一些内容

    
    
    def test():
        iv="ABCDEFGH12345678"
        plaintext="0123456789ABCDEFhellocbcflipping"
        cipher=encrypt(iv, plaintext)
        print "cipher:"+cipher
        de_cipher = decrypt(iv, cipher)
        print "de_cipher:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 start-----------------------------------        bin_cipher = bytearray(a2b_hex(cipher))
        bin_cipher[15] = bin_cipher[15] ^ ord('g') ^ ord('G')
        de_cipher = decrypt(iv,b2a_hex(bin_cipher))
        print "de_cipher2:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 end-------------------------------------    #-------------------adding 2 start-----------------------------------        bin_decipher = bytearray(a2b_hex(de_cipher))
        bin_iv = bytearray(iv)
        for i in range(0,len(iv)):
            bin_iv[i] = bin_iv[i] ^ bin_decipher[i] ^ ord('X')
        de_cipher = decrypt(str(bin_iv),b2a_hex(bin_cipher))
        print "de_cipher3:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 2 end-------------------------------------
代码结果：

![Image
\[3\].png](https://image.3001.net/images/20180228/15198094173017.png!small)  

可以看到在不知道key的情况下，通过修改密文和IV（还有个条件是获得每次解密后的结果
），可以控制输出的明文为自己想要的内容，而且只能从最后一组开始修改，并且每改完一组，都需要重新获取一次解密后的数据，要根据解密后的数据来修改前一组密文的值。  

## 0x05 Padding Oracle Attack

该部分是参考《白帽子讲Web安全》11.5节内容，根据padding规则，CBC字节翻转攻击和解密结果是否合规的不同状态来进行明文的猜解。

### 1.padding

先提一下padding，实际加密数据时，由于明文长度不会一直正好是分组的倍数，因此就需要添加附加的数据来使得加密的数据的长度是分组长度的倍数。

使用以下策略添加（按照AES算法）：

如果需要添加一个字节，就添加0x01

如果需要添加两个字节，就添加0x02 0x02

三个字节就是：0x03 0x03 0x03，依次类推。

如果正好是分组长度倍数，如16个字节，也需要再添加16个0x10进行padding

以下是pad方法

    
    
    def pad(plaintext):
        block_size=16
        num = block_size - len(plaintext)%block_size
        padding = hex(num)[2:] if num>0x0f else '0'+hex(num)[2:]
        return a2b_hex(b2a_hex(plaintext)+padding*num)
    

使用该pad函数，编写加密解密方法，解密时需要获取最后一个字节的内容，根据其值判断最后几个字节是否值相等，由于本次实验使用aes加密算法，所以多了个if语句判断num的值是否在1~16范围内，这个If语句可以删除。另外decrypt方法返回两个结果，status和解密后的数据，模仿HTTP，如果200说明padding正确，解密应该是正确的，如果是500说明解密失败

    
    
    from Crypto.Cipher import AES
    from Crypto import Random
    from binascii import b2a_hex,a2b_hex
    
    def pad(plaintext):
        block_size=16
        num = block_size - len(plaintext)%block_size
        padding = hex(num)[2:] if num>0x0f else '0'+hex(num)[2:]
        return a2b_hex(b2a_hex(plaintext)+padding*num)
    
    def encrypt(key,iv,plaintext):
        key_len = len(key)
        if not (key_len == 16 or key_len == 24 or key_len == 32):
            print "key length is invalid"
            return ""
        pad_plaintext = pad(plaintext)
        aes_encrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_encrypt.encrypt(pad_plaintext))
    
    def decrypt(key,iv,cipher):
        key_len = len(key)
        if not (key_len == 16 or key_len == 24 or key_len == 32):
            print "key length is invalid"
            return 500,""
        if len(iv) != 16:
            print "IV length is invalid"
            return 500,""
        aes_decrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        pad_plaintext = aes_decrypt.decrypt(a2b_hex(cipher))
        length = len (pad_plaintext)
        num = ord(pad_plaintext[length-1])
        if num < 1 or num > 16:
            return 500,""
        for i in range(1,num):
            if ord(pad_plaintext[length-1-i]) != num:
                return 500,""
        plaintext = pad_plaintext[:length-num]
        return 200,b2a_hex(plaintext)
    

### 2.攻击原理

现在说一下具体攻击，CBC字节翻转攻击内容不提了，直接举栗说明，假设有密文cipher，长度为32字节（如果密文长度只有16字节，那么就将IV加在密文前面，变成32字节），分成两组prev=cipher[0:16],current=cipher[16:32]。

再设一个tmp_prev为16个0x00组成，先用tmp_prev+current去解密，解密后的结果末尾一般是不会满足padding规则的（别和我说如果，遇到了算你倒霉，但概率应该几乎为0吧），设current经过分组加密算法解密后的值为de_current，current解密后对应的明文为plaintext。

然后修改tmp_prev[15]的内容，从0x00遍历到0xff，有且仅有一个值使得tmp_prev+current的解密时满足padding规则的，此时解密后的最后一个字节内容应该是0x01

针对0x01来看下以下的表达式：

> tmp_prev[15] Xor de_current[15] = 0x01 (1)
>
> prev[15] Xor de_current[15] = plaintext[15] (2)

(1),(2)两个表达式左右两边再进行异或，等式还是成立的，因此得到下面的等式：

> tmp_prev[15] Xor prev[15] = plaintext[15] Xor 0x01

所以

> plaintext[15] = tmp_prev[15] Xor prev[15] Xor 0x01

这样就能获得明文的最后一个字节了。

接着依然是要让tmp_prev+current满足padding，不过最后两个字节为0x02，由于已经知道最后一个字节的内容了，因此很容易设置tmp_prev[15]的内容使得最后一个字节解密为0x02，然后同理使tmp_prev[14]从0x00遍历到0xff，有且仅有一个使得解密后padding正确。

tmp_prev[15]设置为prev[15] Xor plaintext[15] Xor 0x02

而plaintext[14]= tmp_prev[14] Xor prev[14] Xor 0x02

依次类推，就能获得current组对应的明文，如果需要prev组的明文，就需要prev组和prev前一组的密文重复上述操作，对于第一组密文，则是IV+第一组密文重复上述操作。

### 3.代码模拟

定义一个blackbox方法，接受两种调用方法，一种是blackbox()，返回结果是随机生成的IV以及加密后的密文（明文是随机生成的33个字符，我也不知道内容），另一种是blackbox(iv,cipher)，进行解密，根据padding判断解密是否正确，只有两种返回值200（正确），500（不正确）
PS:由于测试用，没去写的多严谨，如果你一定要这样调用blackbox(iv)，我就想问你皮这一下开心么？

    
    
    import random
    import string
    
    def blackbox(iv=None,cipher=None):
        key="1234567890123456"
        if iv is None:
            iv = Random.new().read(AES.block_size)
            plaintext=''.join(random.choice(string.ascii_letters) for _ in range(33))
            cipher = encrypt(key, iv, plaintext)
            return b2a_hex(iv),cipher
        else:
            status,plaintext = decrypt(key, iv, cipher)
            return status
    

现在是根据2.攻击原理写的代码，因为需要去调用blackbox，所以每次都是需要iv的值的，该方法每次传入两组密文，解密current组对应的明文的值返回。

    
    
    def padding_attack(iv,prev,current):
        tmp_prev = bytearray(16)
        byte_plain = bytearray(16)
        for i in range (0,16):
            if i != 0:
                for j in range (0,i):
                    tmp_prev[15-j] = prev[15-j] ^ byte_plain[15-j] ^ (i+1)
            for test in range (0,256):
                tmp_prev[15-i] = test
                status = blackbox(iv, b2a_hex(str(tmp_prev+current)))
                if status == 200:
                    byte_plain[15-i] = tmp_prev[15-i] ^ (i+1) ^ prev[15-i]
                else:
                    continue
        return byte_plain
    

再写一个遍历密文和IV的方法，依次调用上面的攻击方法，获取全部的明文，并删除padding部分，返回

    
    
    def attack(iv,cipher):
        byte_cipher = bytearray(a2b_hex(cipher))
        byte_iv = bytearray(iv)
        cipher_length = len(byte_cipher)
        num_group = cipher_length / 16
        for i in range(0,num_group):
            if i == 0:
                byte_plain = padding_attack(iv,byte_iv, byte_cipher[i*16:i*16+16])
            else:
                byte_plain = byte_plain + padding_attack(iv,byte_cipher[(i-1)*16:i*16], byte_cipher[i*16:i*16+16])
        return byte_plain[:cipher_length-byte_plain[cipher_length-1]]
    

最后写一个测试方法验证攻击是否成功

    
    
    def test():
        iv,cipher = blackbox()
        print iv
        print cipher
        iv = a2b_hex(iv)
        plaintext = attack(iv, cipher)
        print plaintext
    #-------------------verification--------------------------        key = "1234567890123456"
        cipher_test = encrypt(key, iv, plaintext)
        print cipher == cipher_test

运行结果：

![image.png](https://image.3001.net/images/20180228/15198103113697.png!small)  

也可以在blackbox方法中将随机生成的明文打印出来，进行对比

![image.png](https://image.3001.net/images/20180228/1519810329716.png!small)  

## 0x06附录

附上两个测试的源码

    
    
    #coding:utf-8
    from Crypto.Cipher import AES
    from binascii import b2a_hex,a2b_hex
    
    def encrypt(iv,plaintext):
        if len(plaintext)%16 != 0:
            print "plaintext length is invalid"
            return
        if len(iv) != 16:
            print "IV length is invalid"
            return
        key="1234567890123456"
        aes_encrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_encrypt.encrypt(plaintext))
    
    def decrypt(iv,cipher):
        if len(iv) != 16:
            print "IV length is invalid"
            return
        key="1234567890123456"
        aes_decrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_decrypt.decrypt(a2b_hex(cipher)))
    
    def test():
        iv="ABCDEFGH12345678"
        plaintext="0123456789ABCDEFhellocbcflipping"
        cipher=encrypt(iv, plaintext)
        print "cipher:"+cipher
        de_cipher = decrypt(iv, cipher)
        print "de_cipher:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 start-----------------------------------        bin_cipher = bytearray(a2b_hex(cipher))
        bin_cipher[15] = bin_cipher[15] ^ ord('g') ^ ord('G')
        de_cipher = decrypt(iv,b2a_hex(bin_cipher))
        print "de_cipher2:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 1 end-------------------------------------    #-------------------adding 2 start-----------------------------------        bin_decipher = bytearray(a2b_hex(de_cipher))
        bin_iv = bytearray(iv)
        for i in range(0,len(iv)):
            bin_iv[i] = bin_iv[i] ^ bin_decipher[i] ^ ord('X')
        de_cipher = decrypt(str(bin_iv),b2a_hex(bin_cipher))
        print "de_cipher3:"+de_cipher
        print a2b_hex(de_cipher)
    #-------------------adding 2 end-------------------------------------    
    test()
    
    
    
    #coding:utf-8
    from Crypto.Cipher import AES
    from Crypto import Random
    from binascii import b2a_hex,a2b_hex
    import random
    import string
    
    def pad(plaintext):
        block_size=16
        num = block_size - len(plaintext)%block_size
        padding = hex(num)[2:] if num>0x0f else '0'+hex(num)[2:]
        return a2b_hex(b2a_hex(plaintext)+padding*num)
    
    def encrypt(key,iv,plaintext):
        key_len = len(key)
        if not (key_len == 16 or key_len == 24 or key_len == 32):
            print "key length is invalid"
            return ""
        pad_plaintext = pad(plaintext)
        aes_encrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        return b2a_hex(aes_encrypt.encrypt(pad_plaintext))
    
    def decrypt(key,iv,cipher):
        key_len = len(key)
        if not (key_len == 16 or key_len == 24 or key_len == 32):
            print "key length is invalid"
            return 500,""
        if len(iv) != 16:
            print "IV length is invalid"
            return 500,""
        aes_decrypt = AES.new(key,AES.MODE_CBC,IV=iv)
        pad_plaintext = aes_decrypt.decrypt(a2b_hex(cipher))
        length = len (pad_plaintext)
        num = ord(pad_plaintext[length-1])
        if num < 1 or num > 16:
            return 500,""
        for i in range(1,num):
            if ord(pad_plaintext[length-1-i]) != num:
                return 500,""
    
        plaintext = pad_plaintext[:length-num]
        return 200,b2a_hex(plaintext)
    
    def blackbox(iv=None,cipher=None):
        key="1234567890123456"
        if iv is None:
            iv = Random.new().read(AES.block_size)
            plaintext=''.join(random.choice(string.ascii_letters) for _ in range(33))
            print "random plaintext:"+plaintext
            cipher = encrypt(key, iv, plaintext)
            return b2a_hex(iv),cipher
        else:
            status,plaintext = decrypt(key, iv, cipher)
            return status
    
    def padding_attack(iv,prev,current):
        tmp_prev = bytearray(16)
        byte_plain = bytearray(16)
        for i in range (0,16):
            if i != 0:
                for j in range (0,i):
                    tmp_prev[15-j] = prev[15-j] ^ byte_plain[15-j] ^ (i+1)
            for test in range (0,256):
                tmp_prev[15-i] = test
                status = blackbox(iv, b2a_hex(str(tmp_prev+current)))
                if status == 200:
                    byte_plain[15-i] = tmp_prev[15-i] ^ (i+1) ^ prev[15-i]
                else:
                    continue
        return byte_plain
    
    def attack(iv,cipher):
        byte_cipher = bytearray(a2b_hex(cipher))
        byte_iv = bytearray(iv)
        cipher_length = len(byte_cipher)
        num_group = cipher_length / 16
        for i in range(0,num_group):
            if i == 0:
                byte_plain = padding_attack(iv,byte_iv, byte_cipher[i*16:i*16+16])
            else:
                byte_plain = byte_plain + padding_attack(iv,byte_cipher[(i-1)*16:i*16], byte_cipher[i*16:i*16+16])
        return byte_plain[:cipher_length-byte_plain[cipher_length-1]]
    
    def test():
        iv,cipher = blackbox()
        iv = a2b_hex(iv)
        plaintext = attack(iv, cipher)
        print plaintext
    
    test()  
    

 ***本文原创作者：Abyss0，本文属FreeBuf原创奖励计划，未经许可禁止转载**

