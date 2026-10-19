# 2020湖湘杯Reverse Writeup及复盘

阅读量 **269716**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-05 12:00:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0185e774e0b7feb8a5.jpg)

## 前言

>
> 这次和happy_misc里的师傅一起报了湖湘杯，打了一天，总体感觉还算可以，虽然没进线下，但还是很感觉到自己一年中的提升和现在的不足的。re差一点儿ak，也就算是半个ak吧，嘻嘻。比赛嘛，一如既往的卷，就嗯卷。

## 0x00 easyre

![](https://p5.ssl.qhimg.com/t0128fb2f1cfc781849.png)

这题放入IDA可以看到，在main中其实是没有关于flag的check部分的。有的只是对flag的长度的一个check，仅仅只是要求了flag的长度为0x18。之后就会ret，会到上一级函数。这里我没有选择去用IDA深究，而是用OD去动态调试看一下。

![](https://p4.ssl.qhimg.com/t018d58e659d50d3699.png)

向下跟进可以看到在main返回之后，会有一个加密的过程。先将第一个字符与0xe0存到栈中。之后就是第一个字符左移3位，第二个字符右移5位，之后取或运算。之后异或循环变量也就是字符数组下标。大致伪代码就是`(((input[i])|(input[i+1]))&0xff)^i`。最后将存入栈中的变量和最后一位做运算。

再次ret可以看到check部分，找到加密flag之后的数据。

![](https://p1.ssl.qhimg.com/t01b67c8308da496e44.png)

位运算本身不可逆，而我算法也不大行，所以直接正面爆破。我们可以把每一位的表达式看做一种条件，而对于移位和或运算，必然会有多解，满足所有条件，才能确定唯一的flag。在我多次的尝试之后发现，每一位的取值其实可能性也很有限，而在前后两个条件的限制下，其实就会固定，所以可以进行分段爆破。（不存在艺术，简单粗暴才能抢血）大致给一下部分代码截图，就不给完全了，每个人的爆破代码都不一样的。

![](https://p2.ssl.qhimg.com/t012163fd1721f0c987.png)

## 0x01 ReMe

这题主要考察python的反编译，具体从exe->pyc->py这个过程可以百度，这里不多说。反编译后的代码如下

    
    
    # uncompyle6 version 3.7.4
    # Python bytecode 3.7 (3394)
    # Decompiled from: Python 2.7.15+ (default, Aug 31 2018, 11:56:52) 
    # [GCC 8.2.0]
    # Warning: this version of Python has problems handling the Python 3 "byte" type in constants properly.
    # Embedded file name: ReMe.py
    # Compiled at: 1995-09-28 00:18:56
    # Size of source mod 2**32: 272 bytes
    import sys, hashlib
    check = [
     'e5438e78ec1de10a2693f9cffb930d23',
     '08e8e8855af8ea652df54845d21b9d67',
     'a905095f0d801abd5865d649a646b397',
     'bac8510b0902185146c838cdf8ead8e0',
     'f26f009a6dc171e0ca7a4a770fecd326',
     'cffd0b9d37e7187483dc8dd19f4a8fa8',
     '4cb467175ab6763a9867b9ed694a2780',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'cffd0b9d37e7187483dc8dd19f4a8fa8',
     'fd311e9877c3db59027597352999e91f',
     '49733de19d912d4ad559736b1ae418a7',
     '7fb523b42413495cc4e610456d1f1c84',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'acb465dc618e6754de2193bf0410aafe',
     'bc52c927138231e29e0b05419e741902',
     '515b7eceeb8f22b53575afec4123e878',
     '451660d67c64da6de6fadc66079e1d8a',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'fe86104ce1853cb140b7ec0412d93837',
     'acb465dc618e6754de2193bf0410aafe',
     'c2bab7ea31577b955e2c2cac680fb2f4',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'f077b3a47c09b44d7077877a5aff3699',
     '620741f57e7fafe43216d6aa51666f1d',
     '9e3b206e50925792c3234036de6a25ab',
     '49733de19d912d4ad559736b1ae418a7',
     '874992ac91866ce1430687aa9f7121fc']
    def func(num):
        result = []
        while num != 1:
            num = num * 3 + 1 if num % 2 else num // 2
            result.append(num)
        return result
    if __name__ == '__main__':
        print('Your input is not the FLAG!')
        inp = input()
        if len(inp) != 27:
            print('length error!')
            sys.exit(-1)
        for i, ch in enumerate(inp):
            ret_list = func(ord(ch))
            s = ''
            for idx in range(len(ret_list)):
                s += str(ret_list[idx])
                s += str(ret_list[(len(ret_list) - idx - 1)])
            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            if md5.hexdigest() != check[i]:
                sys.exit(i)
        md5 = hashlib.md5()
        md5.update(inp.encode('utf-8'))
        print('You win!')
        print('flag{' + md5.hexdigest() + '}')
    # okay decompiling 2.pyc
    

稍微改一改源码，就会自己出flag（有手就行）

    
    
    # uncompyle6 version 3.7.4
    # Python bytecode 3.7 (3394)
    # Decompiled from: Python 2.7.15+ (default, Aug 31 2018, 11:56:52) 
    # [GCC 8.2.0]
    # Warning: this version of Python has problems handling the Python 3 "byte" type in constants properly.
    # Embedded file name: ReMe.py
    # Compiled at: 1995-09-28 00:18:56
    # Size of source mod 2**32: 272 bytes
    import sys, hashlib
    check = [
     'e5438e78ec1de10a2693f9cffb930d23',
     '08e8e8855af8ea652df54845d21b9d67',
     'a905095f0d801abd5865d649a646b397',
     'bac8510b0902185146c838cdf8ead8e0',
     'f26f009a6dc171e0ca7a4a770fecd326',
     'cffd0b9d37e7187483dc8dd19f4a8fa8',
     '4cb467175ab6763a9867b9ed694a2780',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'cffd0b9d37e7187483dc8dd19f4a8fa8',
     'fd311e9877c3db59027597352999e91f',
     '49733de19d912d4ad559736b1ae418a7',
     '7fb523b42413495cc4e610456d1f1c84',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'acb465dc618e6754de2193bf0410aafe',
     'bc52c927138231e29e0b05419e741902',
     '515b7eceeb8f22b53575afec4123e878',
     '451660d67c64da6de6fadc66079e1d8a',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'fe86104ce1853cb140b7ec0412d93837',
     'acb465dc618e6754de2193bf0410aafe',
     'c2bab7ea31577b955e2c2cac680fb2f4',
     '8e50684ac9ef90dfdc6b2e75f2e23741',
     'f077b3a47c09b44d7077877a5aff3699',
     '620741f57e7fafe43216d6aa51666f1d',
     '9e3b206e50925792c3234036de6a25ab',
     '49733de19d912d4ad559736b1ae418a7',
     '874992ac91866ce1430687aa9f7121fc']
    def func(num):
        result = []
        while num != 1:
            num = num * 3 + 1 if num % 2 else num // 2
            result.append(num)
        return result
    if __name__ == '__main__':
        flag = ''
        '''
        print('Your input is not the FLAG!')
        inp = input()
        if len(inp) != 27:
            print('length error!')
            sys.exit(-1)
    
        for i, ch in enumerate(inp):
        '''
        for i in range(len(check)):
            for ch in range(32,128):
                ret_list = func(ch)
                s = ''
                for idx in range(len(ret_list)):
                    s += str(ret_list[idx])
                    s += str(ret_list[(len(ret_list) - idx - 1)])
                md5 = hashlib.md5()
                md5.update(s.encode('utf-8'))
                if md5.hexdigest() == check[i]:
                    flag += chr(ch)
        print(flag)
        '''
        md5 = hashlib.md5()
        md5.update(inp.encode('utf-8'))
        print('You win!')
        print('flag{' + md5.hexdigest() + '}')
        '''
    # okay decompiling 2.pyc
    

## 0x02 easy_c++

签到题，最基本的逆向。

![](https://p5.ssl.qhimg.com/t0111fdc51770149359.png)

这里可以看到最关键的三个地方，就是很常见的，密文，加密算法，比较，而算法又是最基础的xor。直接上脚本就行

    
    
    >>> a = '7d21e<e3<:3;9;ji t r#w\"$*{*+*$|,'
    >>> flag = ''
    >>> for i in range(len(a)):
    ...     flag += chr(ord(a[i])^i)
    ...
    >>> flag
    '7e02a9c4439056df0e2a7b432b0069b3'
    

## 0x03 easyZ

这题其实才是最有意思的一题。至于为什么要放最后，是因为我比赛过程中没有做出来，这里留做记录，有师傅指点之后就行修改。s390是一个很不常见的架构，之前在CTF中出现过没有超过三次，我知道的有分别是2018年的一个国外的比赛和2019的bytectf。有幸参加了其中一场，那场的s390是可以qemu模拟并且调试的。而今天的不能，不知道是自己环境的问题还是题目的问题（基本上确定是自己环境的问题，但是自己环境和之前的没变，可能是还差一些什么）。而IDA7.4以下是不支持反编译s390的。知道比较好用的，也只有objdump。

附件给出了各个区段和汇编代码，我们需要找到关键位置。而常见的寻找关键位置就是查找字符串，一般字符串是在data段。在rodata段，找到了关键的信息。对照指令手册，审代码就行。<http://www.tachyonsoft.com/inst390m.htm>

![](https://p5.ssl.qhimg.com/t01407bd837295dd530.png)

这部分可以看到一些有用的信息。please这句话的偏移是0x1071064，如果想要调用，汇编代码中一定有这个字符串的地址，直接查找。

![](https://p2.ssl.qhimg.com/t01ff57663b0914bd23.png)

可以找到关键的地方，而通过字符串，也可以确定一些库函数。

    
    
     1000b38:    eb bf f0 58 00 24     stmg    %r11,%r15,88(%r15)      #main
     1000b3e:    e3 f0 ff 20 ff 71     lay    %r15,-224(%r15)
     1000b44:    b9 04 00 bf           lgr    %r11,%r15
     1000b48:    b2 4f 00 10           ear    %r1,%a0
     1000b4c:    eb 11 00 20 00 0d     sllg    %r1,%r1,32
     1000b52:    b2 4f 00 11           ear    %r1,%a1
     1000b56:    d2 07 b0 d8 10 28     mvc    216(8,%r11),40(%r1)
     1000b5c:    c0 20 00 03 82 84     larl    %r2,0x1071064           ;Please input
     1000b62:    c0 e5 00 00 40 43     brasl    %r14,0x1008be8          ;printf
     1000b68:    ec 1b 00 a6 00 d9     aghik    %r1,%r11,166
     1000b6e:    b9 04 00 31           lgr    %r3,%r1
     1000b72:    c0 20 00 03 82 87     larl    %r2,0x1071080           ;%s
     1000b78:    c0 e5 00 00 3a 5c     brasl    %r14,0x1008030          ;scanf
     1000b7e:    ec 1b 00 a6 00 d9     aghik    %r1,%r11,166
     1000b84:    b9 04 00 21           lgr    %r2,%r1                     ;load r1,r2
     1000b88:    c0 e5 ff ff fe c4     brasl    %r14,0x1000910          ;call func1  规定格式，0-9a-f
     1000b8e:    b9 04 00 12           lgr    %r1,%r2
     1000b92:    12 11                 ltr    %r1,%r1
     1000b94:    a7 84 00 17           je    0x1000bc2
     1000b98:    ec 1b 00 a6 00 d9     aghik    %r1,%r11,166
     1000b9e:    b9 04 00 21           lgr    %r2,%r1
     1000ba2:    c0 e5 ff ff ff 33     brasl    %r14,0x1000a08          ;call func2
     1000ba8:    b9 04 00 12           lgr    %r1,%r2
     1000bac:    12 11                 ltr    %r1,%r1
     1000bae:    a7 84 00 0a           je    0x1000bc2
     1000bb2:    c0 20 00 03 82 69     larl    %r2,0x1071084           ;You win!
     1000bb8:    c0 e5 00 00 40 18     brasl    %r14,0x1008be8          ;printf
     1000bbe:    a7 f4 00 08           j    0x1000bce
     1000bc2:    c0 20 00 03 82 66     larl    %r2,0x107108e           ;You lose!
     1000bc8:    c0 e5 00 00 40 10     brasl    %r14,0x1008be8          ;printf
     1000bce:    a7 18 00 00           lhi    %r1,0
     1000bd2:    b9 14 00 11           lgfr    %r1,%r1
     1000bd6:    b9 04 00 21           lgr    %r2,%r1
     1000bda:    b2 4f 00 10           ear    %r1,%a0
     1000bde:    eb 11 00 20 00 0d     sllg    %r1,%r1,32
     1000be4:    b2 4f 00 11           ear    %r1,%a1
     1000be8:    d5 07 b0 d8 10 28     clc    216(8,%r11),40(%r1)
     1000bee:    a7 84 00 05           je    0x1000bf8
     1000bf2:    c0 e5 00 00 e5 2b     brasl    %r14,0x101d648
     1000bf8:    e3 40 b1 50 00 04     lg    %r4,336(%r11)
     1000bfe:    eb bf b1 38 00 04     lmg    %r11,%r15,312(%r11)
     1000c04:    07 f4                 br    %r4
    

审一下main可以看到，主要有两个函数，0x1000910和0x1000a08，接下来可以一个一个看。

    
    
    # func1
     1000910:    eb bf f0 58 00 24     stmg    %r11,%r15,88(%r15)
     1000916:    e3 f0 ff 50 ff 71     lay    %r15,-176(%r15)
     100091c:    b9 04 00 bf           lgr    %r11,%r15
     1000920:    e3 20 b0 a0 00 24     stg    %r2,160(%r11)
     1000926:    e3 20 b0 a0 00 04     lg    %r2,160(%r11)
     100092c:    c0 e5 ff ff ff 02     brasl    %r14,0x1000730      ;strlen
     1000932:    b9 04 00 12           lgr    %r1,%r2
     1000936:    a7 1f 00 20           cghi    %r1,32  ;Compare Halfword
     100093a:    a7 84 00 06           je    0x1000946   ;bin(32) = 100000b
     100093e:    a7 18 00 00           lhi    %r1,0
     1000942:    a7 f4 00 56           j    0x10009ee   ;不能走这个
     1000946:    e5 4c b0 ac 00 00     mvhi    172(%r11),0 ;
     100094c:    a7 f4 00 49           j    0x10009de
     1000950:    e3 10 b0 ac 00 14     lgf    %r1,172(%r11)
     1000956:    e3 10 b0 a0 00 08     ag    %r1,160(%r11)
     100095c:    43 10 10 00           ic    %r1,0(%r1)
     1000960:    b9 94 00 11           llcr    %r1,%r1
     1000964:    c2 1f 00 00 00 2f     clfi    %r1,47  ;0
     100096a:    a7 c4 00 11           jle    0x100098c
     100096e:    e3 10 b0 ac 00 14     lgf    %r1,172(%r11)
     1000974:    e3 10 b0 a0 00 08     ag    %r1,160(%r11)
     100097a:    43 10 10 00           ic    %r1,0(%r1)
     100097e:    b9 94 00 11           llcr    %r1,%r1
     1000982:    c2 1f 00 00 00 39     clfi    %r1,57  ;9
     1000988:    a7 c4 00 24           jle    0x10009d0
     100098c:    e3 10 b0 ac 00 14     lgf    %r1,172(%r11)
     1000992:    e3 10 b0 a0 00 08     ag    %r1,160(%r11)
     1000998:    43 10 10 00           ic    %r1,0(%r1)
     100099c:    b9 94 00 11           llcr    %r1,%r1
     10009a0:    c2 1f 00 00 00 60     clfi    %r1,96  ;a
     10009a6:    a7 c4 00 11           jle    0x10009c8
     10009aa:    e3 10 b0 ac 00 14     lgf    %r1,172(%r11)
     10009b0:    e3 10 b0 a0 00 08     ag    %r1,160(%r11)
     10009b6:    43 10 10 00           ic    %r1,0(%r1)
     10009ba:    b9 94 00 11           llcr    %r1,%r1
     10009be:    c2 1f 00 00 00 66     clfi    %r1,102 f
     10009c4:    a7 c4 00 09           jle    0x10009d6
     10009c8:    a7 18 00 00           lhi    %r1,0
     10009cc:    a7 f4 00 11           j    0x10009ee
     10009d0:    18 00                 lr    %r0,%r0
     10009d2:    a7 f4 00 03           j    0x10009d8
     10009d6:    18 00                 lr    %r0,%r0
     10009d8:    eb 01 b0 ac 00 6a     asi    172(%r11),1
     10009de:    58 10 b0 ac           l    %r1,172(%r11)
     10009e2:    a7 1e 00 1f           chi    %r1,31      ;Compare Halfword Immediate 
     10009e6:    a7 c4 ff b5           jle    0x1000950
     10009ea:    a7 18 00 01           lhi    %r1,1
     10009ee:    b9 14 00 11           lgfr    %r1,%r1
     10009f2:    b9 04 00 21           lgr    %r2,%r1
     10009f6:    e3 40 b1 20 00 04     lg    %r4,288(%r11)
     10009fc:    eb bf b1 08 00 04     lmg    %r11,%r15,264(%r11)
     1000a02:    07 f4                 br    %r4
     1000a04:    07 07                 nopr    %r7
     1000a06:    07 07                 nopr    %r7
    

第一个函数细审一下会发现，是一个大循环，由上下文可以知道0x1000730为strlen。这个函数的主要作用是限制flag的格式，首先限制了flag的长度为32，之后就是要求flag的格式为0-9a-f。

    
    
    #func2
     1000a08:    b3 c1 00 2b           ldgr    %f2,%r11
     1000a0c:    b3 c1 00 0f           ldgr    %f0,%r15
     1000a10:    e3 f0 ff 48 ff 71     lay    %r15,-184(%r15)
     1000a16:    b9 04 00 bf           lgr    %r11,%r15
     1000a1a:    e3 20 b0 a0 00 24     stg    %r2,160(%r11)
     1000a20:    e5 4c b0 a8 00 00     mvhi    168(%r11),0
     1000a26:    a7 f4 00 4b           j    0x1000abc
     1000a2a:    e3 10 b0 a8 00 14     lgf    %r1,168(%r11)   ;jmp
     1000a30:    e3 10 b0 a0 00 08     ag    %r1,160(%r11)
     1000a36:    43 10 10 00           ic    %r1,0(%r1)
     1000a3a:    b9 94 00 11           llcr    %r1,%r1
     1000a3e:    50 10 b0 b4           st    %r1,180(%r11)
     1000a42:    58 30 b0 b4           l    %r3,180(%r11)
     1000a46:    71 30 b0 b4           ms    %r3,180(%r11)   ;r3*r3
     1000a4a:    c0 10 00 04 d3 ef     larl    %r1,0x109b228
     1000a50:    e3 20 b0 a8 00 14     lgf    %r2,168(%r11)
     1000a56:    eb 22 00 02 00 0d     sllg    %r2,%r2,2
     1000a5c:    58 12 10 00           l    %r1,0(%r2,%r1)
     1000a60:    b2 52 00 31           msr    %r3,%r1         ;0xb2b0*r3*r3
     1000a64:    c0 10 00 04 d3 e2     larl    %r1,0x109b228   ;address
     1000a6a:    e3 20 b0 a8 00 14     lgf    %r2,168(%r11)
     1000a70:    a7 2b 00 20           aghi    %r2,32
     1000a74:    eb 22 00 02 00 0d     sllg    %r2,%r2,2   ;r2 = r2 <<2
     1000a7a:    58 12 10 00           l    %r1,0(%r2,%r1)
     1000a7e:    71 10 b0 b4           ms    %r1,180(%r11)   ;r3*(109b228+4)
     1000a82:    1a 31                 ar    %r3,%r1
     1000a84:    c0 10 00 04 d3 d2     larl    %r1,0x109b228
     1000a8a:    e3 20 b0 a8 00 14     lgf    %r2,168(%r11)
     1000a90:    a7 2b 00 40           aghi    %r2,64
     1000a94:    eb 22 00 02 00 0d     sllg    %r2,%r2,2
     1000a9a:    58 12 10 00           l    %r1,0(%r2,%r1)
     1000a9e:    1a 31                 ar    %r3,%r1
     1000aa0:    c4 18 00 04 d3 68     lgrl    %r1,0x109b170
     1000aa6:    e3 20 b0 a8 00 14     lgf    %r2,168(%r11)
     1000aac:    eb 22 00 02 00 0d     sllg    %r2,%r2,2
     1000ab2:    50 32 10 00           st    %r3,0(%r2,%r1)
     1000ab6:    eb 01 b0 a8 00 6a     asi    168(%r11),1
     1000abc:    58 10 b0 a8           l    %r1,168(%r11)
     1000ac0:    a7 1e 00 1f           chi    %r1,31
     1000ac4:    a7 c4 ff b3           jle    0x1000a2a
     1000ac8:    e5 4c b0 ac 00 01     mvhi    172(%r11),1
     1000ace:    e5 4c b0 b0 00 00     mvhi    176(%r11),0
     1000ad4:    a7 f4 00 21           j    0x1000b16
     1000ad8:    c4 18 00 04 d3 4c     lgrl    %r1,0x109b170
     1000ade:    e3 20 b0 b0 00 14     lgf    %r2,176(%r11)
     1000ae4:    eb 22 00 02 00 0d     sllg    %r2,%r2,2
     1000aea:    58 32 10 00           l    %r3,0(%r2,%r1)
     1000aee:    c0 10 00 04 d3 5d     larl    %r1,0x109b1a8      ;check
     1000af4:    e3 20 b0 b0 00 14     lgf    %r2,176(%r11)
     1000afa:    eb 22 00 02 00 0d     sllg    %r2,%r2,2
     1000b00:    58 12 10 00           l    %r1,0(%r2,%r1)
     1000b04:    19 31                 cr    %r3,%r1         ;cmp   
     1000b06:    a7 84 00 05           je    0x1000b10
     1000b0a:    e5 4c b0 ac 00 00     mvhi    172(%r11),0
     1000b10:    eb 01 b0 b0 00 6a     asi    176(%r11),1
     1000b16:    58 10 b0 b0           l    %r1,176(%r11)
     1000b1a:    a7 1e 00 1f           chi    %r1,31
     1000b1e:    a7 c4 ff dd           jle    0x1000ad8
     1000b22:    58 10 b0 ac           l    %r1,172(%r11)
     1000b26:    b9 14 00 11           lgfr    %r1,%r1
     1000b2a:    b9 04 00 21           lgr    %r2,%r1
     1000b2e:    b3 cd 00 b2           lgdr    %r11,%f2
     1000b32:    b3 cd 00 f0           lgdr    %r15,%f0
     1000b36:    07 fe                 br    %r14
    

第二个函数，是两个循环。ar相当于add，ms相当于mul，ic相当于movzx。这样看就可以发现，
~~其实一开始会取0x109b228的第一个值，乘input[0]的平方，加取0x109b228的第二个值，乘input[0]，加0x109b228的第三个值。~~
这里错了划掉，应该是`0x109b228`的96个值分成每32一组，一共三组。而并不是我之前认为的三个一组，一共32组。与`0x109b1a8`中的值做比较。exp简单，直接解方程或者爆破就好了。

    
    
    value1 = [0x0000b2b0, 0x00006e72, 0x00006061, 0x0000565d,0x0000942d, 0x0000ac79, 0x0000391c, 0x0000643d,0x0000ec3f, 0x0000bd10, 0x0000c43e, 0x00007a65,0x0000184b, 0x0000ef5b, 0x00005a06, 0x0000a8c0,0x0000f64b, 0x0000c774, 0x000002ff, 0x00008e57,0x0000aed9, 0x0000d8a9, 0x0000230c, 0x000074e8,0x0000c2a6, 0x000088b3, 0x0000af2a, 0x00009ea7,0x0000ce8a, 0x00005924, 0x0000d276, 0x000056d4]
    value2 = [0x000077d7, 0x0000990e, 0x0000b585, 0x00004bcd,0x00005277, 0x00001afc, 0x00008c8a, 0x0000cdb5,0x00006e26, 0x00004c22, 0x0000673f, 0x0000daff,0x00000fac, 0x000086c7, 0x0000e048, 0x0000c483,0x000085d3, 0x00002204, 0x0000c2ee, 0x0000e07f,0x00000caf, 0x0000bf76, 0x000063fe, 0x0000bffb,0x00004b09, 0x0000e5b3, 0x00008bda, 0x000096df,0x0000866d, 0x00001719, 0x00006bcf, 0x0000adcc]
    value3 = [0x00000f2b, 0x000051ce, 0x00001549, 0x000020c1,0x00003a8d, 0x000005f5, 0x00005403, 0x00001125,0x00009161, 0x0000e2a5, 0x00005196, 0x0000d8d2,0x0000d644, 0x0000ee86, 0x00003896, 0x00002e71,0x0000a6f1, 0x0000dfcf, 0x00003ece, 0x00007d49,0x0000c24d, 0x0000237e, 0x00009352, 0x00007a97,0x00007bfa, 0x0000cbaa, 0x000010dc, 0x00003bd9,0x00007d7b, 0x00003b88, 0x0000b0d0, 0x0000e8bc]
    result = [0x08a73233, 0x116db0f6, 0x0e654937, 0x03c374a7,0x16bc8ed9, 0x0846b755, 0x08949f47, 0x04a13c27,0x0976cf0a, 0x07461189, 0x1e1a5c12, 0x11e64d96,0x03cf09b3, 0x093cb610, 0x0d41ea64, 0x07648050,0x092039bf, 0x08e7f1f7, 0x004d871f, 0x1680f823,0x06f3c3eb, 0x2205134d, 0x015c6a7c, 0x11c67ed0,0x0817b32e, 0x06bd9b92, 0x08806b0c, 0x06aaa515,0x205b9f76, 0x0de963e9, 0x2194e8e2, 0x047593bc]
    table = '0123456789abcdef'
    flag = ''
    for i in range(len(value1)):
        for x in table:
            tmp = ord(x)
            if tmp*tmp*value1[i]+tmp*value2[i]+value3[i] == result[i]:
                flag += x
    print flag
    

## 总结

这次湖湘杯，re的整体题目算是偏简单吧。最好玩的是s390这个，没做出来也是自己的失误吧，不仔细审汇编代码导致的，题目的话还是不难的。已经很长时间没有这样纯审过汇编代码了，感觉以后还是需要更加提升汇编方面的能力吧，F5不是什么时候都能用的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Prowes5** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/221283](/post/id/221283)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Reverse](/tag/Reverse)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t0189f115b91bf10a2a.png) Prowes5

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

