作者: [Hcamael@知道创宇404实验室](http://0x48.pw)  
发布时间：2017-08-29

本周的Pwnhub延迟到了周一，所以周一中午就看了下这题，是一道Python 的pyc逆向题，思路到挺简单的，但是很花精力

本题是一道pyc逆向题，用uncompyle6没法跑出来，所以猜测又是考python的opcode

之前做过相关研究，也写过一篇blog：<http://0x48.pw/2017/03/20/0x2f/>

主要是两个参考文档：

  1. [opcode.h](https://github.com/Python/cpython/blob/2.7/Include/opcode.h)
  2. [opcode 具体代表的操作](https://docs.python.org/2/library/dis.html)

    
    
    >>> import dis, marshal
    
    >>> f = open("./final.pyc")
    
    >>> f.read(8)
    '\x03\xf3\r\nT\x16xY'
    
    >>> code = marshal.load(f)
    
    >>> code.co_consts
    .....(输出太多了省略)
    >>> code.co_varnames
    ('DIVIDER',)
    
    >>> code.co_names
    ('a', 'b', 'int', 'str', 'i', 'q', 'raw_input', 'True', 'aa', 'xrange', 'OO00000O0O0OO0OOO', 'sys', 'OO000OOO0O000O00O', 'time', 'OO0OO00O0OO0OO00O', 'False', 'r', 'marshal', 'c', 'x', 'p', 'None', 'f', 'args', 'kwargs', 'u')

我们主要关心上面这三个集合，分别是`co_consts`, `co_varnames`, `co_names`

其中：

  * co_consts集合中包含的是该模块中定义的各种数据类型，具体的值，比如定义的对象，赋值的字符串/int型数据
  * co_varnames表示的是当前作用域的局部变量的变量名

接下来就是看具体的opcode：

    
    
    >>> dis.disassemble_string(code.co_code)
    Traceback (most recent call last):
    IndexError: string index out of range
    string index out of range

但是发现报错，跑不了，我的思路是一句一句看，从opcode.h头文件中可以看出opcode为1字节，再加上操作数的话就是3字节，所以一句指令的长度是1字节或者3字节，所以：

    
    
    >>> dis.disassemble_string(code.co_code[:3])
              0 JUMP_ABSOLUTE    3292
    
    >>> dis.disassemble_string(code.co_code[3292:3292+3])
              0 JUMP_FORWARD       24 (to 27)

我使用上面的方面进行简单的测试，发现有一大堆的`JUMP_ABSOLUTE`和`JUMP_FORWARD`指令，这时就知道这里有混淆了。

参考文档，我们可以知道`JUMP_ABSOLUTE`是跳到绝对地址，`JUMP_FORWARD`是下一个地址加上操作数，比如`0 JUMP_FORWARD
24 (to 27)`
，当前地址0，当前指令是3字节，下一个地址是3，加上24是27，所以执行完这句指令是跳到27，这里我只是举例，在本题中，地址0是从code.co_code[0]开始

该模块的最外层很麻烦，追了一会指令流就看不住了，然后就看定义的函数：

    
    
    >>> func_list = []                                                           
    >>> for x in code.co_consts:
    ...     if type(x) == type(code.co_consts[0]):
    ...         func_list.append(x)
    >>> for x in func_list:
    ...     print x.co_name                  # 函数名
    a
    q
    a
    a
    a
    aa
    a
    a
    aa
    r
    a
    a
    a
    p
    a
    a
    a
    f
    a
    <setcomp>
    <dictcomp>
    u
    
    >>> for x in func_list:
    ...     print x.co_consts
    (None, 2574606289, None)
    (None, 'hex', '', 2269302367, 3999397071, 3212575724, 4011125418, 2541851390, 3101964664, 4002314880, None)
    (3363589608, None)
    (None, 928441828, None)
    (None, 1, 2827689411, 3340835492, None)
    (0, 3149946851, 1915448404, None)
    (None, 1, 1761489969, None)
    (None, 3346499627, None)
    (0, 804230483, 1849535108, None)
    (None, 18, 1, 0, 811440571, 694805067, 1480591167, 2317567929, None)
    (None, '', 103332102, 3569318510, 2445961406, 2136442608, 3449813582, None)
    (None, 1254503156, None)
    (None, 1, 3745711837, None)
    (None, 13, 25, 254, 256, 184, 139, 1, 2, 3, 158, 161, 21, 10, 251, 142, 128, 115, 5, 99, 28, 130, 253, 17, 219, 88, 180, 14, 83, 119, 101, 7, 57, 178, 91, 245, 207, 0, 249, 166, 230, 85, 8, 213, 134, 240, 4, 199, 255, 202, 6, 30, 9, 173, 69, 227, 124, 15, 141, 205, 170, 11, 133, 218, 149, 12, 193, 67, 24, 16, 103, 151, 145, 4002470191, 2521589842, 1264028523, 1557840806, 2269633706, 951771769, 1948225321, 2840041954, 240350730, 2835968845, 1344465054, 1832969381, 414996033, 893304341, 1033856613, 2005820485, 1655033734, 383297387, 1110377909, 1331741225, 98787899, 3245587348, 3507579705, 2710942562, 408230478, 4193925412, 4258146773, 3555027567, 2696796853, 3228309104, 1702138493, 878416672, 1840033377, 2212037170, 1264539365, 155548767, 3125510233, 2468296542, 2105197060, 1611521139, 2978471848, 3090963965, 3551862263, 4190549182, 1060650455, 418207362, 2505390665, 148314961, 1392669086, 3687927788, 740579929, 2902468892, 3221147519, 1094609218, 2451398154, 2409455404, 3351906386, 2473439137, 3475738179, 1904786329, 3519084889, 979327822, 2909197751, 2846946149, 3980818176, 4127800602, 1291996042, 4037586272, 2675091267, 199113052, 710970151, 1897807508, 1373489195, 1776856572, 1804854838, 1781505473, 3306320587, 1760320652, 860749406, 161432034, 3258951656, 2792565458, 1916846289, 2023044049, 1935716574, 1285095588, 3035625565, 3586006421, 2368742222, 3131839710, 2298893290, 1460710676, 4009727955, 2535652387, 19895811, 2953554646, 1834358963, None)
    (None, 1, 156819970, None)
    (None, 1, 2362387540, None)
    (None, 807794131, None)
    (None, 1, <code object O0O00O0OOOOO000OO at 0x7fd9b10f6ab0, file "ck.py", line 200>, 2901513116, 1218601877, 625447945, None)
    (None, 2014553041, None)
    (1296050898, 2236454079, 1998426264, 3102970915, None)
    (2343257866, 676615509, 2173771105, 697135550, 1974986440, None)
    (None, '', 'Wrong key!', 'Good job! The flag is pwnhub{flag:your input(lower case)}', 3463300106, 3857901018, 3949890875, 174919631, 1639824250, 433978434, 3710075802, 161154336, 33478671, 2489981027, 1574135945, 3935706030, 1700692433, 832561131, None)

随便看了下各个函数的相关信息，发现u函数中有flag相关信息，然后开始逆u函数，首先收集下u函数的相关变量信息：

    
    
    >>> u = func_list[-1]
    
    >>> u.co_argcount
    1
    
    >>> u.co_varnames
    ('OOO000OOOOOO00OOO', 'OOOO000OO000OOOOO', 'DIVIDER')
    
    >>> u.co_names
    ('q', 'r', 'p')
    
    >>> u.co_consts
    (None, '', 'Wrong key!', 'Good job! The flag is pwnhub{flag:your input(lower case)}', 3463300106, 3857901018, 3949890875, 174919631, 1639824250, 433978434, 3710075802, 161154336, 33478671, 2489981027, 1574135945, 3935706030, 1700692433, 832561131, None)

写了个脚本，自动追踪指令并输出，但是跳过两个`JUMP`指令的输出，然后又发现了一个控制流平坦化混淆.......简单的举例下：

    
    
    175: 
              0 LOAD_CONST         10 (10)
    178: 
              0 STORE_FAST          2 (2)
    247: 
              0 LOAD_CONST          9 (9)
    44: 
              0 LOAD_FAST           2 (2)
    47: 
              0 COMPARE_OP          2 (==)
    50: 
              0 POP_JUMP_IF_TRUE    74
    53: 
              0 LOAD_CONST         15 (15)
    56: 
              0 LOAD_FAST           2 (2)
    59: 
              0 COMPARE_OP          2 (==)
    62: 
              0 POP_JUMP_IF_TRUE    77
    65: 
              0 LOAD_CONST          5 (5)
    68: 
              0 LOAD_FAST           2 (2)
    596: 
              0 COMPARE_OP          2 (==)
    599: 
              0 POP_JUMP_IF_TRUE   626
    602: 
              0 LOAD_CONST         11 (11)
    605: 
              0 LOAD_FAST           2 (2)
    608: 
              0 COMPARE_OP          2 (==)
    611: 
              0 POP_JUMP_IF_TRUE   629
    614: 
              0 LOAD_CONST         10 (10)
    617: 
              0 LOAD_FAST           2 (2)
    620: 
              0 COMPARE_OP          2 (==)
    88: 
              0 POP_JUMP_IF_TRUE   115

解释下各个指令的含义：

  * LOAD_CONST 10 (10) ==> push co_consts[10]
  * STORE_FAST 2 (2) ==> pop co_varnames[2]
  * LOAD_FAST 2 (2) ==> push co_varnames[2]
  * COMPARE_OP 2 (==) ==> pop x1; pop x2; if x1 == x2: push 1 else: push 0 (该指令的操作数2表示栈上的两个数进行比较)
  * POP_JUMP_IF_TRUE 74 ==> pop x1; if x1: jmp 74

翻译成伪代码就是：

    
    
    DIVIDER = co_consts[10]
    if DIVIDER == co_consts[9]:
        jmp 74
    if DIVIDER == co_consts[15]:
        jmp 77
    if DIVIDER == co_consts[5]:
        jmp 626
    if DIVIDER == co_consts[11]:
        jmp 629
    if DIVIDER == co_consts[10]:
        jmp 115

这个就是控制流平坦化混淆，中间有一堆垃圾代码，因为我怕时间来不及就没有写全自动换脚本，是半自动半手工做题，用脚本去掉JUMP混淆，把结果输出到文件中，然后用ctrl+f，去掉控制流平坦化混淆(之后会在我博客中放全自动脚本)

去掉混淆后的代码：

    
    
    283: 
              0 LOAD_GLOBAL         0 (0)     TOP1
    286: 
              0 LOAD_FAST           0 (0)     TOP
    289: 
              0 CALL_FUNCTION       1         CALL TOP1(TOP)
    
    q(OOO000OOOOOO00OOO)
    
    229: 
              0 STORE_FAST          1 (1)     
    
    OOOO000OO000OOOOO = q(OOO000OOOOOO00OOO)
    
    232: 
              0 LOAD_FAST           1 (1)
    235: 
              0 LOAD_CONST          1 (1)
    336: 
              0 COMPARE_OP          2 (==)
    222: 
              0 POP_JUMP_IF_FALSE   253
    
    if OOOO000OO000OOOOO != "":   JUMP 253
    
    657: 
              0 LOAD_CONST          2 (2)
    660: 
              0 PRINT_ITEM     
    661: 
              0 PRINT_NEWLINE  
    
    PRINT co_consts[2]
    
    276: 
              0 LOAD_CONST          0 (0)
              0 RETURN_VALUE  
    return 0 
    ###
    def u(OOO000OOOOOO00OOO):
      OOOO000OO000OOOOO = q(OOO000OOOOOO00OOO)
      if OOOO000OO000OOOOO == "":
        print 'Wrong key!'
        return 0
    ###

第一个分支我们可以翻译出上面的代码，然后把指令调到253，在继续跑脚本：

    
    
    682: 
              0 LOAD_GLOBAL         1 (1)
    685: 
              0 LOAD_FAST           1 (1)
    688: 
              0 CALL_FUNCTION       1
    691: 
              0 POP_JUMP_IF_FALSE   709
    
     if r(OOOO000OO000OOOOO) == False: JMP 709
    
    16: 
              0 LOAD_CONST          2 (2)
    19: 
              0 PRINT_ITEM     
    20: 
              0 PRINT_NEWLINE  
    PRINT co_consts[2]
    
    317: 
              0 LOAD_CONST          0 (0)
              0 RETURN_VALUE 
    return 0

继续跟踪到709：

    
    
    324: 
              0 LOAD_GLOBAL         2 (2)
    327: 
              0 LOAD_FAST           1 (1)
    330: 
              0 CALL_FUNCTION       1
    241: 
              0 POP_JUMP_IF_FALSE   262
    
    if p(OOOO000OO000OOOOO) == False: JMP 262
    
    701: 
              0 LOAD_CONST          2 (2)
    704: 
              0 PRINT_ITEM     
    705: 
              0 PRINT_NEWLINE  
    
    print co_consts[2]
    
    10: 
              0 LOAD_CONST          0 (0)
              0 RETURN_VALUE   
    return 0

根据到262:

    
    
    24: 
              0 LOAD_CONST          3 (3)
    27: 
              0 PRINT_ITEM     
    28: 
              0 PRINT_NEWLINE  
    311: 
              0 LOAD_CONST          0 (0)
              0 RETURN_VALUE  
    
    print co_consts[3]
    return 0

根据上面追踪翻译出来的代码，成功还原出u函数：

    
    
    def u(OOO000OOOOOO00OOO):
        OOOO000OO000OOOOO = q(OOO000OOOOOO00OOO)
        if OOOO000OO000OOOOO == "":
            print ERROR
            return 0
        if r(OOOO000OO000OOOOO):
            print ERROR
            return 0
        if p(OOOO000OO000OOOOO):
            print ERROR
            return 0
        print "Good job!"
        return 0

如果输出`Good job!`则表示得到flag

所以下面就是取逆向`q`, `r`, `p`三个函数，原理和上面逆向`u`函数一样：

    
    
    def q(O0OOO0O0O00O00OOO):
        return O0OOO0O0O00O00OOO.decode('hex')
    
    def r(O0O000OO00OO00OO0):
        if len(O0O000OO00OO00OO0) == 18:
            return 0
        return 1

`q`和`r`两个函数，一个是进行decode操作，一个是判断长度，所以判断flag是否正确就在`p`函数中，而`p`函数是手工最难逆的函数，我从下午6点，逆到了8点，/(ㄒoㄒ)/~~，我应该是采取了最笨的方法，前面提到了，我现在有个自动化的思路，之后会放到我blog中。

    
    
    def p(hhh):
      if ((ord(hhh[13])*25+254)%256) ^ 184 == 139:
        if ((ord(hhh[2])*3+158)%256) ^ 161 == 21:
          if ((ord(hhh[10])*251+142)%256) ^ 128 ==  115:
            if ((ord(hhh[5])*99+28)%256) ^ 130 ==  253:
              if ((ord(hhh[17])*219+88)%256) ^ 130 ==  180:
                if ((ord(hhh[14])*83+119)%256) ^ 161 ==  101:
                  if ((ord(hhh[7])*57+178)%256) ^ 184 ==  91:
                    if ((ord(hhh[1])*245+207)%256) ^ 184 ==  57:
                      if ((ord(hhh[0])*249+166)%256) ^ 230 ==  85:
                        if ((ord(hhh[8])*213+134)%256) ^ 161 ==  240:
                          if ((ord(hhh[4])*199+255)%256) ^ 128 ==  202:
                            if ((ord(hhh[6])*85+30)%256) ^ 230 ==  202:
                              if ((ord(hhh[9])*173+69)%256) ^ 227 ==  124:
                                if ((ord(hhh[15])*141+205)%256) ^ 227 ==  170:
                                  if ((ord(hhh[11])*133+218)%256) ^ 130 ==  149:
                                    if ((ord(hhh[12])*139+193)%256) ^ 230 ==  2:
                                      if ((ord(hhh[3])*67+202)%256) ^ 227 ==  24:
                                        if ((ord(hhh[16])*103+151)%256) ^ 128 ==  145:
                                          return 0
      return 1
    #  这代码弄出来的时候差点猝死

然后写个脚本爆破出flag(现在想想，应该可以用z3)：

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    
    flag = [""]*18
    
    bds = ['((x*25+254)%256) ^ 184 == 139', '((x*3+158)%256) ^ 161 == 21', '((x*251+142)%256) ^ 128 ==  115', '((x*99+28)%256) ^ 130 ==  253', '((x*219+88)%256) ^ 130 ==  180', '((x*83+119)%256) ^ 161 ==  101', '((x*57+178)%256) ^ 184 ==  91', '((x*245+207)%256) ^ 184 ==  57', '((x*249+166)%256) ^ 230 ==  85', '((x*213+134)%256) ^ 161 ==  240', '((x*199+255)%256) ^ 128 ==  202', '((x*85+30)%256) ^ 230 ==  202', '((x*173+69)%256) ^ 227 ==  124', '((x*141+205)%256) ^ 227 ==  170', '((x*133+218)%256) ^ 130 ==  149', '((x*139+193)%256) ^ 230 ==  2', '((x*67+202)%256) ^ 227 ==  24', '((x*103+151)%256) ^ 128 ==  145']
    bds_index = [13,2,10,5,17,14,7,1,0,8,4,6,9,15,11,12,3,16]
    
    for y in xrange(18):
        for x in xrange(256):
            if eval(bds[y]):
                flag[bds_index[y]] = x
                break
    
    payload= ""
    
    for x in flag:
        payload += chr(x)
    
    print payload.encode('hex')
    
    # b5aab27b5d01d6b91f021f59c97ddf6c76fa
    $ python final.pyc 
    Please input your key(hex string):b5aab27b5d01d6b91f021f59c97ddf6c76fa
    Good job! The flag is pwnhub{flag:your input(lower case)}

傻逼的半自动化脚本：

    
    
    #!/usr/bin/env python2.7
    # -*- coding=utf-8 -*-    
    import dis, marshal
    from pwn import u16
    
    one_para = ["\x01","\x02", "\x03", "\x21", "\x17", "\x0a", "\x0b", "\x0c", "\x0f", "\x13", "\x14", "\x15", "\x16", "\x18", "\x19", "\x1a", "\x1c", "\x1e", "\x1f", "\x47", "\x48"]
    
    f = open("final.pyc")
    f.read(8)
    code = marshal.load(f)
    
    code = code.co_consts[45]
    print code.co_name
    asm = code.co_code
    # asm = code.co_consts[45].co_code
    stack = []
    varn = {
        'DIVIDER': None,       # DEVIDER
        'OOO000OOOOOO00OOO': None,
        'OOOO000OO000OOOOO': None,
        'OOO0OOO00O00OOOO0': None,
        'O0OOO0O0O00O00OOO': None,
        'O0O000OO00OO00OO0': None,
    }
    flag = 0
    
    # n = 1632
    n = 0
    add = 0
    while True:
        if len(asm) <= n:
            print n
            break
    
        if asm[n] == 'q':  # JUMP_ABSOLUTE
            n = u16(asm[n+1:n+3])
            continue
        elif asm[n] == 'n':  # JUMP_FORWARD
            n += u16(asm[n+1:n+3]) + 3
            continue
        # elif asm[n] in one_para:
        #     dis.disassemble_string(asm[n])
        #     n+=1
        #     continue
        elif asm[n] == "\x53":   # RETURN
            dis.disassemble_string(asm[n])
            break
    
        try:
            print "%d: "%n
            dis.disassemble_string(asm[n:n+3])
            add = 3
        except IndexError:
            try:
                dis.disassemble_string(asm[n])
                add = 1
            except IndexError:
                print "%d: %d"%(n, ord(asm[n]))
                break
    
        if asm[n] == 'd': # LOAD_CONST
            key = u16(asm[n+1:n+3])
            value = code.co_consts[key]
            stack.append(value)
            n += 3
        elif asm[n] == '|': # LOAD_FAST
            key = u16(asm[n+1:n+3])
            value = varn[code.co_varnames[key]]
            stack.append(value)
            n += 3
        elif asm[n] == '}':   # STORE_FAST
            key = code.co_varnames[u16(asm[n+1:n+3])]
            varn[key] = stack.pop()
            n += 3
        elif asm[n] == 'k':   # COMPARE_OP
            x1 = stack.pop()
            x2 = stack.pop()
            if x1 == x2:
                flag = 1
            n += 3
        elif asm[n] == "s":   # POP_JUMP_IF_TRUE
            if flag:
                n = u16(asm[n+1:n+3])
                flag = 0
            else:
                n += 3
        # elif ord(asm[n]) == 114:  # POP_JUMP_IF_FALSE
        #     break 
        else:
            n += add

* * *

自动跑p函数，使用z3跑出flag自动化脚本：

    
    
    #!/usr/bin/env python2.7
    # -*- coding=utf-8 -*-    
    import dis, marshal
    from pwn import u16
    import z3
    
    flag_n = z3.BitVecs('x__0 x__1 x__2 x__3 x__4 x__5 x__6 x__7 x__8 x__9 x__10 x__11 x__12 x__13 x__14 x__15 x__16 x__17', 8)
    
    f = open("final.pyc")
    f.read(8)
    
    code = marshal.load(f)
    
    code = code.co_consts[34]
    print code.co_name
    asm = code.co_code
    # asm = code.co_consts[45].co_code
    stack = []
    varn = {
        'DIVIDER': None,       # DEVIDER
        'OOO000OOOOOO00OOO': None,
        'OOOO000OO000OOOOO': None,
        'OOO0OOO00O00OOOO0': flag_n,
        'O0OOO0O0O00O00OOO': None,
        'O0O000OO00OO00OO0': None,
    }
    flag = 0
    
    # n = 1632
    n = 0
    add = 0
    index = 0
    while True:
        if len(asm) <= n:
            print n
            break
    
        if asm[n] == 'q' or asm[n] == 'r':  # JUMP_ABSOLUTE    or  POP_JUMP_IF_FALSE
            n = u16(asm[n+1:n+3])
            continue
        elif asm[n] == 'n':  # JUMP_FORWARD
            n += u16(asm[n+1:n+3]) + 3
            continue
        # elif asm[n] in one_para:
        #     dis.disassemble_string(asm[n])
        #     n+=1
        #     continue
        elif asm[n] == "\x53":   # RETURN
            dis.disassemble_string(asm[n])
            break
    
        try:
            print "%d: "%n
            dis.disassemble_string(asm[n:n+3])
            add = 3
        except IndexError:
            try:
                dis.disassemble_string(asm[n])
                add = 1
            except IndexError:
                print "%d: %d"%(n, ord(asm[n]))
                break
    
        if asm[n] == 'd': # LOAD_CONST
            key = u16(asm[n+1:n+3])
            value = code.co_consts[key]
            stack.append(value)
            n += add
        elif asm[n] == '|': # LOAD_FAST
            key = u16(asm[n+1:n+3])
            value = varn[code.co_varnames[key]]
            stack.append(value)
            n += add
        elif asm[n] == '}':   # STORE_FAST
            key = code.co_varnames[u16(asm[n+1:n+3])]
            varn[key] = stack.pop()
            n += add
        elif asm[n] == 'k':   # COMPARE_OP
            op = u16(asm[n+1:n+3])
            if op == 3:
                x1 = stack.pop()
                x2 = stack.pop()
                flag_n[index] = (x2==x1)
            elif op == 2:
                x1 = stack.pop()
                x2 = stack.pop()
                if x1 == x2:
                    flag = 1
            n += add
        elif asm[n] == "s":   # POP_JUMP_IF_TRUE
            if flag:
                n = u16(asm[n+1:n+3])
                flag = 0
            else:
                n += add
        elif asm[n] == chr(25):   # BINARY_SUBSCR
            x1 = stack.pop()
            x2 = stack.pop()
            stack.append(x2[x1])
            #print stack
            index = x1
            n += add
        elif asm[n] == chr(20):   # BINARY_MULTIPLY
            x1 = stack.pop()
            x2 = stack.pop()
            stack.append(x2*x1)
            #print stack
            n += add
        elif asm[n] == chr(22):   # BINARY_MODULO
            x1 = stack.pop()
            x2 = stack.pop()
            stack.append(x2%x1)
            #print stack
            n += add
        elif asm[n] == chr(65):   # BINARY_XOR
            x1 = stack.pop()
            x2 = stack.pop()
            stack.append(x2^x1)
            #print stack
            n += add
        elif asm[n] == chr(23):   # BINARY_ADD
            x1 = stack.pop()
            x2 = stack.pop()
            stack.append(x2+x1)
            #print stack
            n += add
        else:
            n += add
    
    flag = []
    for x in flag_n:
        s = z3.Solver()
        s.add(x)
        s.check()
        res = s.model()
        flag.append(res[res[0]])
    
    flag_hex = ""
    for y in flag:
        flag_hex += chr(y.as_long())
    
    print flag_hex.encode('hex')

思路挺简单的，相当于自己实现一个解释器，实现一个stack，因为我代码中的opcode不全，所以只能针对本题，还有几种思路，比如魔改dis，目前的dis是线性的翻译opcode，可以按照我脚本的思路，当遇到JUMP类指令时，也跟随跳转，但是这个不能去除混淆，混淆还是需要自己写代码去，而我上面自动跑flag的脚本思路是来源于Triton，传入的参数是未知的，就设置为符号变量，当分支判断的时候进行响应的处理，进行动态分析，这样就不需要去混淆。

等我把Triton研究清楚了，说不定能用Triton调试pyc？

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/446/>

