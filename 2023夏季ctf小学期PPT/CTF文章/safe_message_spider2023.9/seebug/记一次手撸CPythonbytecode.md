作者： [Hcamael@知道创宇404实验室](http://0x48.pw)  
发布时间：2017-03-20

上周末的0CTF出现了一个pyc的题目，但是Pyopcode损坏，于是手撸了一波

题目: <https://github.com/Hcamael/CTF_repo/tree/master/0CTF%202017/Re3%28py%29>

通过pyc还原出py网上的资料挺多了，py也有专门的库可以还原，但是0CTF这题却无法还原，目测是opcode损坏，同时根据题目描述，也知道是要修复pyc文件。

这里用到两个库，一个`dis`，可以把二进制反编译CPython bytecode。一个是`marshal`，可以把字符串转换成pyopcode对象

    
    
    >>> import dis, marshal
    >>> f = open("crypt.pyc")
    >>> f.read(4)
    '\x03\xf3\r\n'               # magic number
    >>> f.read(4)                # time
    'f4oX'
    >>> code = marshal.load(f)
    # 对我们有用的属性有:
    >>> code.co_argcount          # 参数的个数
    0
    >>> code.co_varnames          # 局部变量
    ()
    >>> code.co_consts            # 常量 
    (-1, None, <code object encrypt at 0x7f1987df65b0, file "/Users/hen/Lab/0CTF/py/crypt.py", line 2>, <code object decrypt at 0x7f1987e10430, file "/Users/hen/Lab/0CTF/py/crypt.py", line 10>)
    # 从这个常量中我们可以看出，该py文件中定义了两个函数，encrypt和decrypt
    >>> code.co_code                  
    '\x99\x00\x00\x99\x01\x00\x86\x00\x00\x91\x00\x00\x99\x02\x00\x88\x00\x00\x91\x01\x00\x99\x03\x00\x88\x00\x00\x91\x02\x00\x99\x01\x00S'
    # CPython bytecode的二进制, 可以通过dis反编译
    >>> dis.disassemble_string(code.co_code)
              0 <153>               0
              3 <153>               1
              6 MAKE_CLOSURE        0
              9 EXTENDED_ARG        0
             12 <153>               2
             15 LOAD_DEREF          0
             18 EXTENDED_ARG        1
             21 <153>               3
             24 LOAD_DEREF          0
             27 EXTENDED_ARG        2
             30 <153>               1
             33 RETURN_VALUE   
    # 发现bytecode损坏，根本无法阅读

二进制对应的bytecode可以参考:
<https://github.com/Python/cpython/blob/2.7/Include/opcode.h>

从上面的参考连接可以得知153没有对应的bytecode，所以猜测bytecode损坏

每个bytecode所代表的意义: <https://docs.Python.org/2/library/dis.html>

    
    
    >>> code.co_name              # 当前对象名 
    '<module>'
    >>> code.co_names             # 当前对象中使用的对象名
    ('rotor', 'encrypt', 'decrypt')          
    # 从上可以看出，encrypt和decrypt是我们定义的两个函数，那么rotor我们可以猜测是通过import rotor得来的

rotor的使用可以参考: <https://docs.Python.org/2.0/lib/module-rotor.html>

    
    
    # 我们可以通过以下方式查看两个函数中的信息
    >>> enc = code.co_consts[2]
    >>> dec = code.co_consts[3]
    >>> enc.co_argcount
    1
    >>> dec.co_argcount
    1
    # 两个函数中都有一个传入的参数
    >>> enc.co_varnames
    ('data', 'key_a', 'key_b', 'key_c', 'secret', 'rot')
    >>> dec.co_varnames
    ('data', 'key_a', 'key_b', 'key_c', 'secret', 'rot')
    # 两个函数中的局部变量, 我们可以猜测，data是传入的参数，需要加解密的数据
    >>> enc.co_consts
    (None, '!@#$%^&*', 'abcdefgh', '<>{}:"', 4, '|', 2, 'EOF')
    >>> dec.co_consts
    (None, '!@#$%^&*', 'abcdefgh', '<>{}:"', 4, '|', 2, 'EOF')
    # 两个函数中的常量，我们可以猜测key_a, key_b, key_c三个变量对应的值
    >>> enc.co_code
    "\x99\x01\x00h\x01\x00\x99\x02\x00h\x02\x00\x99\x03\x00h\x03\x00a\x01\x00\x99\x04\x00F\x99\x05\x00'a\x02\x00a\x01\x00'a\x03\x00'\x99\x06\x00F'\x99\x05\x00'a\x02\x00\x99\x06\x00F'\x99\x07\x00'h\x04\x00\x9b\x00\x00`\x01\x00a\x04\x00\x83\x01\x00h\x05\x00a\x05\x00`\x02\x00a\x00\x00\x83\x01\x00S"
    >>> dec.co_code
    "\x99\x01\x00h\x01\x00\x99\x02\x00h\x02\x00\x99\x03\x00h\x03\x00a\x01\x00\x99\x04\x00F\x99\x05\x00'a\x02\x00a\x01\x00'a\x03\x00'\x99\x06\x00F'\x99\x05\x00'a\x02\x00\x99\x06\x00F'\x99\x07\x00'h\x04\x00\x9b\x00\x00`\x01\x00a\x04\x00\x83\x01\x00h\x05\x00a\x05\x00`\x02\x00a\x00\x00\x83\x01\x00S"
    # 发现两个函数bytecode的二进制是一样的，操作是一样的？
    >>> enc.co_name
    'encrypt'
    >>> enc.co_names
    ('rotor', 'newrotor', 'encrypt')
    >>> dec.co_name
    'decrypt'
    >>> dec.co_names
    ('rotor', 'newrotor', 'decrypt')
    # 通过研究rotor的用法，猜测两个函数的区别可能是在于rotor.newrotor(key).encrypt(data)和rotor.newrotor(key).decrypt(data)

所以现在的问题就在于，`key`是怎么来的，然后就开始了手撸CPython bytecode

    
    
    >>> dis.disassemble_string(dec.co_code)
              0 <153>               1
              3 BUILD_SET           1
              6 <153>               2
              9 BUILD_SET           2
             12 <153>               3
             15 BUILD_SET           3
             18 STORE_GLOBAL        1 (1)
             21 <153>               4
             24 PRINT_EXPR     
             25 <153>               5
             28 <39>           
             29 STORE_GLOBAL        2 (2)
             32 STORE_GLOBAL        1 (1)
             35 <39>           
             36 STORE_GLOBAL        3 (3)
             39 <39>           
             40 <153>               6
             43 PRINT_EXPR     
             44 <39>           
             45 <153>               5
             48 <39>           
             49 STORE_GLOBAL        2 (2)
             52 <153>               6
             55 PRINT_EXPR     
             56 <39>           
             57 <153>               7
             60 <39>           
             61 BUILD_SET           4
             64 <155>               0
             67 DELETE_ATTR         1 (1)
             70 STORE_GLOBAL        4 (4)
             73 CALL_FUNCTION       1
             76 BUILD_SET           5
             79 STORE_GLOBAL        5 (5)
             82 DELETE_ATTR         2 (2)
             85 STORE_GLOBAL        0 (0)
             88 CALL_FUNCTION       1
             91 RETURN_VALUE   

右边的数字为操作数，括号里的是注释

因为题目啥信息也没给我们。。。所以修bytecode只能靠猜

我们先假设这里所有的153为同一个操作符，同理所有的39也为同一个

先看第一部分

    
    
              0 <153>               1
              3 BUILD_SET           1
              6 <153>               2
              9 BUILD_SET           2
             12 <153>               3
             15 BUILD_SET           3

这是最容易猜的地方，右边的操作数为123，在看常量和局部变量的tuple，可以猜测是:

    
    
    key_a = '!@#$%^&*'
    key_b = 'abcdefgh'
    key_c = '<>{}:"'

然后去上面给的参考文档里，查出对应的bytecode

    
    
              0 LOAD_CONST           1
              3 STORE_FAST           1
              6 LOAD_CONST           2
              9 STORE_FAST           2
             12 LOAD_CONST           3
             15 STORE_FAST           3

再去`opcode.h`中查其对应的值进行替换

    
    
    >>> dis.disassemble_string(dec.co_code.replace("\x99","\x64").replace("\x68","\x7d"))
              0 LOAD_CONST          1 (1)
              3 STORE_FAST          1 (1)
              6 LOAD_CONST          2 (2)
              9 STORE_FAST          2 (2)
             12 LOAD_CONST          3 (3)
             15 STORE_FAST          3 (3)
             18 STORE_GLOBAL        1 (1)
             21 LOAD_CONST          4 (4)
             24 PRINT_EXPR     
             25 LOAD_CONST          5 (5)
             28 <39>           
             29 STORE_GLOBAL        2 (2)
             32 STORE_GLOBAL        1 (1)
             35 <39>           
             36 STORE_GLOBAL        3 (3)
             39 <39>           
             40 LOAD_CONST          6 (6)
             43 PRINT_EXPR     
             44 <39>           
             45 LOAD_CONST          5 (5)
             48 <39>           
             49 STORE_GLOBAL        2 (2)
             52 LOAD_CONST          6 (6)
             55 PRINT_EXPR     
             56 <39>           
             57 LOAD_CONST          7 (7)
             60 <39>           
             61 STORE_FAST          4 (4)
             64 <155>               0
             67 DELETE_ATTR         1 (1)
             70 STORE_GLOBAL        4 (4)
             73 CALL_FUNCTION       1
             76 STORE_FAST          5 (5)
             79 STORE_GLOBAL        5 (5)
             82 DELETE_ATTR         2 (2)
             85 STORE_GLOBAL        0 (0)
             88 CALL_FUNCTION       1
             91 RETURN_VALUE 

继续，发现肛不动了。。。。然后从底下开始肛

    
    
             64 <155>               0
             67 DELETE_ATTR         1 (1)
             70 STORE_GLOBAL        4 (4)
             73 CALL_FUNCTION       1
             76 STORE_FAST          5 (5)
             79 STORE_GLOBAL        5 (5)
             82 DELETE_ATTR         2 (2)
             85 STORE_GLOBAL        0 (0)
             88 CALL_FUNCTION       1
             91 RETURN_VALUE

根据之前得到的结论，可以猜测这里的代码是:

    
    
        xxx = rotor.newrotor(secret)
        return xxx.decrypt(data)

所以猜测上面的操作数，0指的是局部变量`data`，1指的是全局变量`newrotor`, 2猜测可能是全局变量`decrypt`,
4指的是局部变量`secret`, 5指的是局部变量`rot`，<155>的0可能指的是全局变量`rotor`

然后查找bytecode，改成:

    
    
             64 LOAD_GLOBAL         0
             67 LOAD_ATTR           1 (1)
             70 LOAD_FAST           4 (4)
             73 CALL_FUNCTION       1
             76 STORE_FAST          5 (5)
             79 LOAD_FAST           5 (5)
             82 LOAD_ATTR           2 (2)
             85 LOAD_FAST           0 (0)
             88 CALL_FUNCTION       1
             91 RETURN_VALUE

发现，合情合理，使人姓胡.....

然后和上面一样，整体替换bytecode:

    
    
    >>> dis.disassemble_string(dec.co_code.replace("\x99","\x64").replace("\x68","\x7d").replace("\x61","\x7c").replace("\x60","\x6a").replace("\x9b","\x74"))
              0 LOAD_CONST          1 (1)
              3 STORE_FAST          1 (1)
              6 LOAD_CONST          2 (2)
              9 STORE_FAST          2 (2)
             12 LOAD_CONST          3 (3)
             15 STORE_FAST          3 (3)
             18 LOAD_FAST           1 (1)
             21 LOAD_CONST          4 (4)
             24 PRINT_EXPR     
             25 LOAD_CONST          5 (5)
             28 <39>           
             29 LOAD_FAST           2 (2)
             32 LOAD_FAST           1 (1)
             35 <39>           
             36 LOAD_FAST           3 (3)
             39 <39>           
             40 LOAD_CONST          6 (6)
             43 PRINT_EXPR     
             44 <39>           
             45 LOAD_CONST          5 (5)
             48 <39>           
             49 LOAD_FAST           2 (2)
             52 LOAD_CONST          6 (6)
             55 PRINT_EXPR     
             56 <39>           
             57 LOAD_CONST          7 (7)
             60 <39>           
             61 STORE_FAST          4 (4)
             64 LOAD_GLOBAL         0 (0)
             67 LOAD_ATTR           1 (1)
             70 LOAD_FAST           4 (4)
             73 CALL_FUNCTION       1
             76 STORE_FAST          5 (5)
             79 LOAD_FAST           5 (5)
             82 LOAD_ATTR           2 (2)
             85 LOAD_FAST           0 (0)
             88 CALL_FUNCTION       1
             91 RETURN_VALUE
    
    
             18 LOAD_FAST           1 (1)
             21 LOAD_CONST          4 (4)
             24 PRINT_EXPR     
             25 LOAD_CONST          5 (5)
             28 <39>           
             29 LOAD_FAST           2 (2)
             32 LOAD_FAST           1 (1)
             35 <39>           
             36 LOAD_FAST           3 (3)
             39 <39>           
             40 LOAD_CONST          6 (6)
             43 PRINT_EXPR     
             44 <39>           
             45 LOAD_CONST          5 (5)
             48 <39>           
             49 LOAD_FAST           2 (2)
             52 LOAD_CONST          6 (6)
             55 PRINT_EXPR     
             56 <39>           
             57 LOAD_CONST          7 (7)
             60 <39>           
             61 STORE_FAST          4 (4)

猜测这部分就是局部变量`secret`计算的方法，最后一句`STORE_FAST 4`，猜测就是把上面计算后的值储存到`secret`中

整体看看，发现主要就剩`<39>`和`PRINT_EXPR`不通顺了。。。然后他们都是没操作数的，所以排除了调用函数，调用属性之类的

之后联想到最开头对`key_a, key_b, key_c`的赋值，然后目前的bytecode中没有任何运算操作

再来看这部分

    
    
             18 LOAD_FAST           1 ("!@#$%^&*")
             21 LOAD_CONST          4 (4)
             24 PRINT_EXPR

所以猜测`PRINT_EXPR`, 是字符串和整型之间的操作运算

    
    
             29 LOAD_FAST           2 ("abcdefgh")
             32 LOAD_FAST           1 ("!@#$%^&*")
             35 <39>

这里猜测`<39>`是字符串和字符串之间的操作运算

到这里，我们来想想，整型和字符串之间的操作有啥？

    
    
    >>> "a"*3
    >>> "aaa"[1]
    >>> "aaa"[:1]
    >>> "aaa"[1:]

字符串和字符串之间呢？

    
    
    >>> "aaa" + "bbb"                 # 我只想到了这一个

从上面可以猜测出，`<39>`可能是字符串拼接的操作，然后`PRINT_EXPR`需要一个一个去试，现在我们可以还原出`decrypt`函数了:

    
    
    # import rotor
    def decrypt(data):
        key_a = "!@#$%^&*"
        key_b = "abcdefgh"
        key_c = '<>{}:"'
        secret=key_a*4 + "|" + (key_b+key_a+key_c)*2 + "|" + key_b*2 + "EOF"
        # secret=key_a[4] + "|" + (key_b+key_a+key_c)[2] + "|" + key_b[2] + "EOF"
        # secret=key_a[4:] + "|" + (key_b+key_a+key_c)[2:] + "|" + key_b[2:] + "EOF"
        # secret=key_a[:4] + "|" + (key_b+key_a+key_c)[:2] + "|" + key_b[:2] + "EOF"
        rot = rotor.newrotor(secret)
        return rot.decrypt(data)

简直难受.......

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/443/>

