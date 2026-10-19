# 2021ByteCTF-language binding-WriteUp

阅读量 **219590**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-17 16:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

出处: 2021 ByteCTF  
原题链接: 链接：<https://pan.baidu.com/s/1-IZPcIzGRx1NvMzLBCtHAg>  
提取码：1111  
时间: October 16, 2021  
考点: Golang, Lua  
难度: 困难

## 推测考点

  * 上来直接往 IDA 里面一拖
  * 根据特征，确定这是 Golang。但是出题人对所有的函数名称都做了混淆，全部函数恢复的符号都是错误的…非常不好办 **（考点一：无符号 Go 逆向）**
  * 观察汇编时函数的调用约定，发现这又和传统的 Golang 不一样（采用了大量寄存器来传递参数）。于是打开 Google，搜索后发现这是 Go1.17 新引入的调用约定。 _因此后续所有 Go 相关的，辅助我们判断的程序都应该使用 Go1.17+ 进行编译_
  * 在 IDA 中全局搜索&浏览字符串，发现有 luago 的字样。网上搜索发现这是拿 Go 写的 Lua 解释器 **（考点二：Lua 逆向）**  

  * 因为这并不是一个完整的开源项目，所以只能自己手动筛选，尽量选一个实现上较为完整的。这里选用了这个版本 [zhengted/luago: golang实现Lua (github.com)](https://github.com/zhengted/luago)

## 具体分析

###  解决无符号的问题

  * Go + 没法恢复符号，我真的是吐了。不过既然前面已经推测出了 Go 使用的版本以及它调用的库（luago），可以尝试使用 BinDiff 恢复一下符号
  * 下载并编译 luago，拖到 IDA 里面分析一遍然后保存 IDB 文件，然后在题目的窗口中调用 Bindiff 插件进行比对
  * 。。。不知道出题人咋处理的，所有 luago 库相关的函数几乎都没有识别出来（可信度低的就无视就好了，否则容易误导自己），只是把 Go 的 runtime 大部分都识别出来了
  * 重新分析程序的行为。发现程序运行的时候有如下提示字符串打印  

  * 根据交叉引用定位到了 `main` 函数  

  * 此时已经可以通过结合动态调试对关键逻辑进行分析了。考点一基本完成

###  通过动调梳理程序逻辑

  * 设置调试器参数如下  

  * 此处的寄存器中有通过参数传递的文件名  

  * 不断步过&步进，调到此处发现了亦或的逻辑  

  * 尝试对题目附件的文件进行亦或 0x55 解密，得到 `repaired.lua`，里面含有大量明文字符串  

  * 打开前面下载好的 luago 库，在此处发现了对于 Lua header 的定义  

  * 与 `repaired.lua` 进行对比，发现头部除了前面 5 个字节不一致，后面都是一样的，所以手动对 `repaired.lua` 的头部进行修复

    
    
    with open("new_lang_script.out", "rb")as f:
      f.seek(5)
      data = f.read()
    with open("repaired.lua", "wb")as f:
      f.write(b'\x1bLua\x53'+bytes([i ^ 0x55 for i in data]))
    

  * 此时已经基本理清了程序的逻辑 
    1. 读取 argv 指定的 bytecode 文件
    2. 亦或 0x55 解密
    3. 解释执行

###  Lua 逆向

  * 然后试图调用 luago 运行程序，直接 fatalpanic。。。

    
    
    func main() {
        runCode()
    
    }
    func runCode() {
        ls := state.New()
        ls.OpenLibs()               // 开启标准库
        ls.LoadFile("repaired.lua") // 加载文件
        ls.Call(0, -1)
    }
    

  * 果然没有那么简单。于是开始阅读 luago 的源码，发现虚拟机的 `for loop` 在此处实现。在此处下断点，动调几遍你就会发现，每次执行的 Bytecode 完全驴唇不对马嘴，这时候猜测出题人魔改了 Lua Bytecode 的顺序  

  * 发现这里是从 `Opcodes` 数组中获取的具体要执行的 `action` ，于是进而查看 `Opcodes` 数组的定义  

  * 猜测在题目附件中应该也存在这样的数组。于是继续动调，定位到了原程序中的 `Execute` 函数及 `Opcode` 数组  

  * 这时候发现出题人是真狠。。。把所有 `Opcodes` 对应的字符串描述都给换成 `NONNAME` 了  

  * 所以这里就是想办法获取出题人魔改后 `Opcode` 的顺序

###  获取 Opcode 的顺序

  * 首先定义一下 Opcode 数组元素的结构体并导入到 IDA 里面

    
    
    typedef void (*func_t)(void*, void*);
    typedef struct
    {
      char testFlag, setAflag, argBMode, argCMode, opMode;
      char* string;
      uint64_t pad;
      func_t func_ptr;
    } opcode_t;
    
    enum arg_mask_t {
      OpArgN,  // argument is not used
      OpArgU,  // argument is used
      OpArgR,  // argument is a register or a jump offset
      OpArgK
    };
    

  * 然后使用 `IDAPython` 定义一下结构体，提高可读性

    
    
    def define_opcode_array():
      start_ea = 0x1005540
      end_ea = 0x1005B20
      count = 0
      for ea in range(start_ea, end_ea, 0x20):
        idc.create_struct(ea, 0x20, "opcode_t")
        count += 1
      print(count)
    

  * 首先注意到 Opcode 的参数类型不尽相同  

  * 根据参数类型对 Opcode 进行一个分类，得到了如下的 `dict`

    
    
    known_sig = {
    (0, 1, 2, 0, 0): ['MOVE', 'UNM', 'BNOT', 'NOT', 'LEN'], 
    (0, 1, 3, 0, 1): ['LOADK'], 
    (0, 1, 0, 0, 1): ['LOADKX'], 
    (0, 1, 1, 1, 0): ['LOADBOOL', 'NEWTABLE', 'CALL', 'TAILCALL'],
    (0, 1, 1, 0, 0): ['LOADNIL', 'GETUPVAL', 'VARARG'],
    (0, 1, 1, 3, 0): ['GETTABUP'],
    (0, 1, 2, 3, 0): ['GETTABLE', 'SELF'],
    (0, 0, 3, 3, 0): ['SETTABUP', 'SETTABLE'], 
    (0, 0, 1, 0, 0): ['SETUPVAL', 'RETURN'], 
    (0, 1, 3, 3, 0): ['ADD', 'SUB', 'MUL', 'MOD', 'POW', 'DIV', 'IDIV', 'BAND', 'BOR', 'BXOR', 'SHL', 'SHR'], 
    (0, 1, 2, 2, 0): ['CONCAT'], 
    (0, 0, 2, 0, 2): ['JMP'], 
    (1, 0, 3, 3, 0): ['EQ', 'LT', 'LE'], 
    (1, 0, 0, 1, 0): ['TEST'], 
    (1, 1, 2, 1, 0): ['TESTSET'], 
    (0, 1, 2, 0, 2): ['FORLOOP', 'FORPREP', 'TFORLOOP'], 
    (0, 0, 0, 1, 0): ['TFORCALL'], 
    (0, 0, 1, 1, 0): ['SETLIST'], 
    (0, 1, 1, 0, 1): ['CLOSURE'], 
    (0, 0, 1, 1, 3): ['EXTRAARG']
    }
    

  * 此时可以唯一的识别出部分函数，剩下的那些不确定的也缩小了搜索的范围
  * 然后使用 IDAPython 根据此步的归类对函数进行重命名

    
    
    known_sig = {(0, 1, 2, 0, 0): ['MOVE', 'UNM', 'BNOT', 'NOT', 'LEN'], (0, 1, 3, 0, 1): ['LOADK'], (0, 1, 0, 0, 1): ['LOADKX'], (0, 1, 1, 1, 0): ['LOADBOOL', 'NEWTABLE', 'CALL', 'TAILCALL'], (0, 1, 1, 0, 0): ['LOADNIL', 'GETUPVAL', 'VARARG'], (0, 1, 1, 3, 0): ['GETTABUP'], (0, 1, 2, 3, 0): ['GETTABLE', 'SELF'], (0, 0, 3, 3, 0): ['SETTABUP', 'SETTABLE'], (0, 0, 1, 0, 0): ['SETUPVAL', 'RETURN'], (0, 1, 3, 3, 0): [
        'ADD', 'SUB', 'MUL', 'MOD', 'POW', 'DIV', 'IDIV', 'BAND', 'BOR', 'BXOR', 'SHL', 'SHR'], (0, 1, 2, 2, 0): ['CONCAT'], (0, 0, 2, 0, 2): ['JMP'], (1, 0, 3, 3, 0): ['EQ', 'LT', 'LE'], (1, 0, 0, 1, 0): ['TEST'], (1, 1, 2, 1, 0): ['TESTSET'], (0, 1, 2, 0, 2): ['FORLOOP', 'FORPREP', 'TFORLOOP'], (0, 0, 0, 1, 0): ['TFORCALL'], (0, 0, 1, 1, 0): ['SETLIST'], (0, 1, 1, 0, 1): ['CLOSURE'], (0, 0, 1, 1, 3): ['EXTRAARG']}
    manual_sig = {}
    def rename_action():
      for mv in manual_sig.values():
        for k, v in known_sig.items():
          if mv in v:
            known_sig[k].remove(mv)
      start_ea = 0xFF5540
      end_ea = start_ea+47*0x20
      for ea in range(start_ea, end_ea, 0x20):
        func_ptr_addr = idc.get_qword(ea+0x18)
        func_addr = idc.get_qword(func_ptr_addr)
        idc.set_name(func_ptr_addr, "", ida_name.SN_NOCHECK)
        idc.set_name(func_addr, "", ida_name.SN_NOCHECK)
      for ea in range(start_ea, end_ea, 0x20):
        index = (ea-start_ea)//0x20
        tmp = idc.get_bytes(ea, 5)
        this_sig = tuple([i for i in tmp])
        func_ptr_addr = idc.get_qword(ea+0x18)
        func_addr = idc.get_qword(func_ptr_addr)
    
        if index in manual_sig.keys():
          f_name = manual_sig[index]
        elif len(known_sig[this_sig]) == 1:
          f_name = known_sig[this_sig][0]
        else:
          possible_funcs = '_'.join(known_sig[this_sig])
          f_name = "F_%d_%s" % (index, possible_funcs)
        # all_sig[f_name] = this_sig
    
        p_name = "_p_"+f_name
        idc.set_name(func_ptr_addr, p_name, ida_name.SN_NOCHECK)
        idc.set_name(func_addr, f_name, ida_name.SN_NOCHECK)
    

  * 重命名完之后  

  * 然后就是非常枯燥的比对过程。。。在这一步你需要通过手动对比源程序和下载并自己编译的 `luago.exe` ，手动识别其它函数，然后把 Opcode 的信息以 index:name 的形式加入 `manual_sig` 字典里
  * 最终可以唯一地标记所有 Opcode action 函数  

  * 题目中 Opcode 的顺序如下

    
    
    OP_UNM,OP_SETLIST,OP_TESTSET,OP_CLOSURE,OP_LOADKX,OP_TFORLOOP,OP_NEWTABLE,OP_SHR,OP_SETTABLE,OP_ADD,OP_TAILCALL,OP_SETUPVAL,OP_EXTRAARG,OP_GETTABUP,OP_LEN,OP_SUB,OP_LOADBOOL,OP_TFORCALL,OP_LOADNIL,OP_FORPREP,OP_SHL,OP_TEST,OP_BXOR,OP_LT,OP_CALL,OP_NOT,OP_BOR,OP_MUL,OP_SETTABUP,OP_EQ,OP_MOVE,OP_JMP,OP_IDIV,OP_GETTABLE,OP_CONCAT,OP_VARARG,OP_POW,OP_MOD,OP_DIV,OP_BNOT,OP_SELF,OP_LE,OP_RETURN,OP_FORLOOP,OP_GETUPVAL,OP_LOADK,OP_BAND
    

###  魔改 Lua5.3 & Luadec

  * 然后就需要对原版的 Lua5.3 和 Luadec 进行修改，来得到反汇编后的 Lua 代码
  * 修改 `lopcode.c`

    
    
    /*
    ** $Id: lopcodes.c,v 1.55 2015/01/05 13:48:33 roberto Exp $
    ** Opcodes for Lua virtual machine
    ** See Copyright Notice in lua.h
    */
    
    #define lopcodes_c
    #define LUA_CORE
    
    #include "lopcodes.h"
    
    #include <stddef.h>
    
    #include "lprefix.h"
    
    /* ORDER OP */
    
    LUAI_DDEF const char *const luaP_opnames[NUM_OPCODES + 1] = {
        "UNM",
        "SETLIST",
        "TESTSET",
        "CLOSURE",
        "LOADKX",
        "TFORLOOP",
        "NEWTABLE",
        "SHR",
        "SETTABLE",
        "ADD",
        "TAILCALL",
        "SETUPVAL",
        "EXTRAARG",
        "GETTABUP",
        "LEN",
        "SUB",
        "LOADBOOL",
        "TFORCALL",
        "LOADNIL",
        "FORPREP",
        "SHL",
        "TEST",
        "BXOR",
        "LT",
        "CALL",
        "NOT",
        "BOR",
        "MUL",
        "SETTABUP",
        "EQ",
        "MOVE",
        "JMP",
        "IDIV",
        "GETTABLE",
        "CONCAT",
        "VARARG",
        "POW",
        "MOD",
        "DIV",
        "BNOT",
        "SELF",
        "LE",
        "RETURN",
        "FORLOOP",
        "GETUPVAL",
        "LOADK",
        "BAND",
        NULL};
    
    #define opmode(t, a, b, c, m) (((t) << 7) | ((a) << 6) | ((b) << 4) | ((c) << 2) | (m))
    
    LUAI_DDEF const lu_byte luaP_opmodes[NUM_OPCODES] = {
        opmode(0, 1, 2, 0, 0)  // UNM
        ,
        opmode(0, 0, 1, 1, 0)  // SETLIST
        ,
        opmode(1, 1, 2, 1, 0)  // TESTSET
        ,
        opmode(0, 1, 1, 0, 1)  // CLOSURE
        ,
        opmode(0, 1, 0, 0, 1)  // LOADKX
        ,
        opmode(0, 1, 2, 0, 2)  // TFORLOOP
        ,
        opmode(0, 1, 1, 1, 0)  // NEWTABLE
        ,
        opmode(0, 1, 3, 3, 0)  // SHR
        ,
        opmode(0, 0, 3, 3, 0)  // SETTABLE
        ,
        opmode(0, 1, 3, 3, 0)  // ADD
        ,
        opmode(0, 1, 1, 1, 0)  // TAILCALL
        ,
        opmode(0, 0, 1, 0, 0)  // SETUPVAL
        ,
        opmode(0, 0, 1, 1, 3)  // EXTRAARG
        ,
        opmode(0, 1, 1, 3, 0)  // GETTABUP
        ,
        opmode(0, 1, 2, 0, 0)  // LEN
        ,
        opmode(0, 1, 3, 3, 0)  // SUB
        ,
        opmode(0, 1, 1, 1, 0)  // LOADBOOL
        ,
        opmode(0, 0, 0, 1, 0)  // TFORCALL
        ,
        opmode(0, 1, 1, 0, 0)  // LOADNIL
        ,
        opmode(0, 1, 2, 0, 2)  // FORPREP
        ,
        opmode(0, 1, 3, 3, 0)  // SHL
        ,
        opmode(1, 0, 0, 1, 0)  // TEST
        ,
        opmode(0, 1, 3, 3, 0)  // BXOR
        ,
        opmode(1, 0, 3, 3, 0)  // LT
        ,
        opmode(0, 1, 1, 1, 0)  // CALL
        ,
        opmode(0, 1, 2, 0, 0)  // NOT
        ,
        opmode(0, 1, 3, 3, 0)  // BOR
        ,
        opmode(0, 1, 3, 3, 0)  // MUL
        ,
        opmode(0, 0, 3, 3, 0)  // SETTABUP
        ,
        opmode(1, 0, 3, 3, 0)  // EQ
        ,
        opmode(0, 1, 2, 0, 0)  // MOVE
        ,
        opmode(0, 0, 2, 0, 2)  // JMP
        ,
        opmode(0, 1, 3, 3, 0)  // IDIV
        ,
        opmode(0, 1, 2, 3, 0)  // GETTABLE
        ,
        opmode(0, 1, 2, 2, 0)  // CONCAT
        ,
        opmode(0, 1, 1, 0, 0)  // VARARG
        ,
        opmode(0, 1, 3, 3, 0)  // POW
        ,
        opmode(0, 1, 3, 3, 0)  // MOD
        ,
        opmode(0, 1, 3, 3, 0)  // DIV
        ,
        opmode(0, 1, 2, 0, 0)  // BNOT
        ,
        opmode(0, 1, 2, 3, 0)  // SELF
        ,
        opmode(1, 0, 3, 3, 0)  // LE
        ,
        opmode(0, 0, 1, 0, 0)  // RETURN
        ,
        opmode(0, 1, 2, 0, 2)  // FORLOOP
        ,
        opmode(0, 1, 1, 0, 0)  // GETUPVAL
        ,
        opmode(0, 1, 3, 0, 1)  // LOADK
        ,
        opmode(0, 1, 3, 3, 0)  // BAND
    
    };
    

  * 修改 `lopcode.h`

    
    
    /*
    ** $Id: lopcodes.h,v 1.148 2014/10/25 11:50:46 roberto Exp $
    ** Opcodes for Lua virtual machine
    ** See Copyright Notice in lua.h
    */
    
    #ifndef lopcodes_h
    #define lopcodes_h
    
    #include "llimits.h"
    
    /*===========================================================================
      We assume that instructions are unsigned numbers.
      All instructions have an opcode in the first 6 bits.
      Instructions can have the following fields:
        'A' : 8 bits
        'B' : 9 bits
        'C' : 9 bits
        'Ax' : 26 bits ('A', 'B', and 'C' together)
        'Bx' : 18 bits ('B' and 'C' together)
        'sBx' : signed Bx
    
      A signed argument is represented in excess K; that is, the number
      value is the unsigned value minus K. K is exactly the maximum value
      for that argument (so that -max is represented by 0, and +max is
      represented by 2*max), which is half the maximum for the corresponding
      unsigned argument.
    ===========================================================================*/
    
    enum OpMode { iABC,
                  iABx,
                  iAsBx,
                  iAx }; /* basic instruction format */
    
    /*
    ** size and position of opcode arguments.
    */
    #define SIZE_C 9
    #define SIZE_B 9
    #define SIZE_Bx (SIZE_C + SIZE_B)
    #define SIZE_A 8
    #define SIZE_Ax (SIZE_C + SIZE_B + SIZE_A)
    
    #define SIZE_OP 6
    
    #define POS_OP 0
    #define POS_A (POS_OP + SIZE_OP)
    #define POS_C (POS_A + SIZE_A)
    #define POS_B (POS_C + SIZE_C)
    #define POS_Bx POS_C
    #define POS_Ax POS_A
    
    /*
    ** limits for opcode arguments.
    ** we use (signed) int to manipulate most arguments,
    ** so they must fit in LUAI_BITSINT-1 bits (-1 for sign)
    */
    #if SIZE_Bx < LUAI_BITSINT - 1
    #define MAXARG_Bx ((1 << SIZE_Bx) - 1)
    #define MAXARG_sBx (MAXARG_Bx >> 1) /* 'sBx' is signed */
    #else
    #define MAXARG_Bx MAX_INT
    #define MAXARG_sBx MAX_INT
    #endif
    
    #if SIZE_Ax < LUAI_BITSINT - 1
    #define MAXARG_Ax ((1 << SIZE_Ax) - 1)
    #else
    #define MAXARG_Ax MAX_INT
    #endif
    
    #define MAXARG_A ((1 << SIZE_A) - 1)
    #define MAXARG_B ((1 << SIZE_B) - 1)
    #define MAXARG_C ((1 << SIZE_C) - 1)
    
    /* creates a mask with 'n' 1 bits at position 'p' */
    #define MASK1(n, p) ((~((~(Instruction)0) << (n))) << (p))
    
    /* creates a mask with 'n' 0 bits at position 'p' */
    #define MASK0(n, p) (~MASK1(n, p))
    
    /*
    ** the following macros help to manipulate instructions
    */
    
    #define GET_OPCODE(i) (cast(OpCode, ((i) >> POS_OP) & MASK1(SIZE_OP, 0)))
    #define SET_OPCODE(i, o) ((i) = (((i)&MASK0(SIZE_OP, POS_OP)) | \
                                     ((cast(Instruction, o) << POS_OP) & MASK1(SIZE_OP, POS_OP))))
    
    #define getarg(i, pos, size) (cast(int, ((i) >> pos) & MASK1(size, 0)))
    #define setarg(i, v, pos, size) ((i) = (((i)&MASK0(size, pos)) | \
                                            ((cast(Instruction, v) << pos) & MASK1(size, pos))))
    
    #define GETARG_A(i) getarg(i, POS_A, SIZE_A)
    #define SETARG_A(i, v) setarg(i, v, POS_A, SIZE_A)
    
    #define GETARG_B(i) getarg(i, POS_B, SIZE_B)
    #define SETARG_B(i, v) setarg(i, v, POS_B, SIZE_B)
    
    #define GETARG_C(i) getarg(i, POS_C, SIZE_C)
    #define SETARG_C(i, v) setarg(i, v, POS_C, SIZE_C)
    
    #define GETARG_Bx(i) getarg(i, POS_Bx, SIZE_Bx)
    #define SETARG_Bx(i, v) setarg(i, v, POS_Bx, SIZE_Bx)
    
    #define GETARG_Ax(i) getarg(i, POS_Ax, SIZE_Ax)
    #define SETARG_Ax(i, v) setarg(i, v, POS_Ax, SIZE_Ax)
    
    #define GETARG_sBx(i) (GETARG_Bx(i) - MAXARG_sBx)
    #define SETARG_sBx(i, b) SETARG_Bx((i), cast(unsigned int, (b) + MAXARG_sBx))
    
    #define CREATE_ABC(o, a, b, c) ((cast(Instruction, o) << POS_OP) | (cast(Instruction, a) << POS_A) | (cast(Instruction, b) << POS_B) | (cast(Instruction, c) << POS_C))
    
    #define CREATE_ABx(o, a, bc) ((cast(Instruction, o) << POS_OP) | (cast(Instruction, a) << POS_A) | (cast(Instruction, bc) << POS_Bx))
    
    #define CREATE_Ax(o, a) ((cast(Instruction, o) << POS_OP) | (cast(Instruction, a) << POS_Ax))
    
    /*
    ** Macros to operate RK indices
    */
    
    /* this bit 1 means constant (0 means register) */
    #define BITRK (1 << (SIZE_B - 1))
    
    /* test whether value is a constant */
    #define ISK(x) ((x)&BITRK)
    
    /* gets the index of the constant */
    #define INDEXK(r) ((int)(r) & ~BITRK)
    
    #define MAXINDEXRK (BITRK - 1)
    
    /* code a constant index as a RK value */
    #define RKASK(x) ((x) | BITRK)
    
    /*
    ** invalid register that fits in 8 bits
    */
    #define NO_REG MAXARG_A
    
    /*
    ** R(x) - register
    ** Kst(x) - constant (in constant table)
    ** RK(x) == if ISK(x) then Kst(INDEXK(x)) else R(x)
    */
    
    /*
    ** grep "ORDER OP" if you change these enums
    */
    
    typedef enum {
      OP_UNM,
      OP_SETLIST,
      OP_TESTSET,
      OP_CLOSURE,
      OP_LOADKX,
      OP_TFORLOOP,
      OP_NEWTABLE,
      OP_SHR,
      OP_SETTABLE,
      OP_ADD,
      OP_TAILCALL,
      OP_SETUPVAL,
      OP_EXTRAARG,
      OP_GETTABUP,
      OP_LEN,
      OP_SUB,
      OP_LOADBOOL,
      OP_TFORCALL,
      OP_LOADNIL,
      OP_FORPREP,
      OP_SHL,
      OP_TEST,
      OP_BXOR,
      OP_LT,
      OP_CALL,
      OP_NOT,
      OP_BOR,
      OP_MUL,
      OP_SETTABUP,
      OP_EQ,
      OP_MOVE,
      OP_JMP,
      OP_IDIV,
      OP_GETTABLE,
      OP_CONCAT,
      OP_VARARG,
      OP_POW,
      OP_MOD,
      OP_DIV,
      OP_BNOT,
      OP_SELF,
      OP_LE,
      OP_RETURN,
      OP_FORLOOP,
      OP_GETUPVAL,
      OP_LOADK,
      OP_BAND
    } OpCode;
    
    #define NUM_OPCODES (cast(int, OP_BAND) + 1)
    
    /*===========================================================================
      Notes:
      (*) In OP_CALL, if (B == 0) then B = top. If (C == 0), then 'top' is
      set to last_result+1, so next open instruction (OP_CALL, OP_RETURN,
      OP_SETLIST) may use 'top'.
    
      (*) In OP_VARARG, if (B == 0) then use actual number of varargs and
      set top (like in OP_CALL with C == 0).
    
      (*) In OP_RETURN, if (B == 0) then return up to 'top'.
    
      (*) In OP_SETLIST, if (B == 0) then B = 'top'; if (C == 0) then next
      'instruction' is EXTRAARG(real C).
    
      (*) In OP_LOADKX, the next 'instruction' is always EXTRAARG.
    
      (*) For comparisons, A specifies what condition the test should accept
      (true or false).
    
      (*) All 'skips' (pc++) assume that next instruction is a jump.
    
    ===========================================================================*/
    
    /*
    ** masks for instruction properties. The format is:
    ** bits 0-1: op mode
    ** bits 2-3: C arg mode
    ** bits 4-5: B arg mode
    ** bit 6: instruction set register A
    ** bit 7: operator is a test (next instruction must be a jump)
    */
    
    enum OpArgMask {
      OpArgN, /* argument is not used */
      OpArgU, /* argument is used */
      OpArgR, /* argument is a register or a jump offset */
      OpArgK  /* argument is a constant or register/constant */
    };
    
    LUAI_DDEC const lu_byte luaP_opmodes[NUM_OPCODES];
    
    #define getOpMode(m) (cast(enum OpMode, luaP_opmodes[m] & 3))
    #define getBMode(m) (cast(enum OpArgMask, (luaP_opmodes[m] >> 4) & 3))
    #define getCMode(m) (cast(enum OpArgMask, (luaP_opmodes[m] >> 2) & 3))
    #define testAMode(m) (luaP_opmodes[m] & (1 << 6))
    #define testTMode(m) (luaP_opmodes[m] & (1 << 7))
    
    LUAI_DDEC const char *const luaP_opnames[NUM_OPCODES + 1]; /* opcode names */
    
    /* number of list items to accumulate before a SETLIST instruction */
    #define LFIELDS_PER_FLUSH 50
    
    #endif
    

  * 然后编译 lua5.3
  * 之后编译 `luadec` ，编译过程中报错，意味着改动后的 Opcode 与原来的并不兼容  

  * 通过动调等手段定位什么指令导致了 `Segmentation fault` ，发现很有可能是因为 `#` 导致的：`#` 是 Lua 的语法糖，约等于 `len(arg)` ，于是把 `luadec/bin/bin2c.lua` 进行微调  

  * 此时可以顺利编译 `luadec` 了，同时也可以对魔改的 Lua Bytecode 进行反编译了
  * 运行  

  * 得到 `recovered.lua`

    
    
    -- Decompiled using luadec 2.2 rev: 895d923 for Lua 5.3 from https://github.com/viruscamp/luadec
    -- Command line: ../repaired.lua 
    
    -- params : ...
    -- function num : 0 , upvalues : _ENV
    print("input flag:")
    flag = (io.read)()
    if #flag ~= 29 then
      print("flag is wrong")
      return 
    end
    lst = {100, 120, 133}
    dict = {[9] = 101, [10] = 122}
    ad = function(a, b)
      -- function num : 0_0
      return a + b
    end
    
    mul = function(a, b)
      -- function num : 0_1
      return a * b
    end
    
    check2 = function(f)
      -- function num : 0_2 , upvalues : _ENV
      if (string.byte)(f, 18) + 11 ~= 106 then
        return false
      elseif (string.byte)(f, 19) ~= lst[1] + 21 then
        return false
      elseif (string.byte)(f, 20) ~= dict[9] + 8 then
        return false
      elseif (string.byte)(f, 21) ~= ad(100, 22) then
        return false
      elseif (string.byte)(f, 22) ~= 55 then
        return false
      elseif (string.byte)(f, 23) ~= mul(51, 2) then
        return false
      elseif (string.byte)(f, 24) - 1 ~= 108 then
        return false
      elseif (string.byte)(f, 25) ~= 48 then
        return false
      elseif (string.byte)(f, 26) ~= 100 then
        return false
      elseif (string.byte)(f, 27) ~= 102 then
        return false
      elseif (string.byte)(f, 28) ~= 120 then
        return false
      end
      do return true end
      -- DECOMPILER ERROR: 22 unprocessed JMP targets
    end
    
    check3 = function(f)
      -- function num : 0_3 , upvalues : _ENV
      if (string.byte)(f, 1) ~= 66 then
        return false
      elseif (string.byte)(f, 2) ~= 121 then
        return false
      elseif (string.byte)(f, 3) ~= 116 then
        return false
      elseif (string.byte)(f, 4) ~= 101 then
        return false
      elseif (string.byte)(f, 5) ~= 67 then
        return false
      elseif (string.byte)(f, 6) ~= 84 then
        return false
      elseif (string.byte)(f, 7) ~= 70 then
        return false
      elseif (string.byte)(f, 8) ~= 123 then
        return false
      elseif (string.byte)(f, 29) ~= 125 then
        return false
      end
      do return true end
      -- DECOMPILER ERROR: 18 unprocessed JMP targets
    end
    
    local flag1 = _(flag)
    local flag2 = check2(flag)
    local flag3 = check3(flag)
    if not not flag1 or flag2 or flag3 then
      print("flag is right")
    elseif true then
      print("flag is wrong")
    end
    -- DECOMPILER ERROR: 6 unprocessed JMP targets
    

  * 大部分逻辑都很简单，基本就是明文比较。但有一点：脚本调用了 `_` 这个闭包函数，而这个函数并不是在 Lua 脚本中定义的

### 定位 `_` 闭包函数

  * 先看一下 Luago 中是怎么定义闭包函数的。原来是通过一个 `map`  

  * 在 Golang 中，`map` 是在函数中动态初始化的，全局搜索其中的部分字符串，找到了初始化的函数  

  * 但是怎么找也找不到 `"_"` 这个字符串，这其实反映了 IDA 在搜索字符串的时候一些局限性：没法找到特定长度的字符串
  * 所以这里采用一个骚办法：导出 ASM，然后用 VSCode 在文本文件中搜索  

  * 然后通过交叉引用定位到了跟它绑定的闭包函数  

  * 别被它的伪代码骗了。实际上，这是一个亦或加密并比对  

  * 至此，所有的程序逻辑梳理完成，基本全部都是非常简单的亦或加密，所以得到 `flag` 并不困难了

    
    
    def ad(a, b): return a+b
    def mul(a, b): return a*b
    
    dict = {9:  101, 10: 122}
    lst = (100, 120, 133)
    flag = [ord(' ')]*30
    flag[1] = 66
    flag[2] = 121
    flag[3] = 116
    flag[4] = 101
    flag[5] = 67
    flag[6] = 84
    flag[7] = 70
    flag[8] = 123
    flag[29] = 125
    flag[18] = 106-11
    flag[19] = lst[0]+21
    flag[20] = dict[9]+8
    flag[21] = ad(100, 22)
    flag[22] = 55
    flag[23] = mul(51, 2)
    flag[24] = 108+1
    flag[25] = 48
    flag[26] = 100
    flag[27] = 102
    flag[28] = 120
    front = b'9negozc9aj'
    for i, e in enumerate(front):
      print(chr((i+8) ^ e),end='')
    print()
    print(bytearray(flag).decode())
    # ByteCTF{1golcwm6q_ymz7fm0dfx}
    

## 总结与心得

  * 这道题综合性极强，工作量非常之大。当时花了一天时间看这道题，最后只拿了个四血（给 Nu1L 带哥们跪了，做得太快了）赛后好好整理 wp 也愣是写了一两个小时
  * 这道题涉及的知识点确实很多：Go 逆向（还是不带符号的）、魔改的 Lua 逆向（坑死了）
  * 不过，我感觉这题更多是在考察选手的 **正向开发思路** 。这体现在 
    1. 很多步骤都是需要选手“猜”来定位关键逻辑的，如定位 Opcode 结构体，以及最后能不能想到是通过 `Openlib` 注册了 `_` 回调
    2. 做题过程中需要写很多辅助脚本（IDAPython），同时需要快速魔改 Lua 和 Luadec 并定位其中的问题
  * 所以，想要做好逆向，一定要积累一些项目开发经验。这样你才能站在出题人（开发者）的角度，去思考在哪里布置考点
  * And _： ~~字节的逆向出题人真不当人啊~~_ ​

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **r4ve1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257453](/post/id/257453)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [RE](/tag/RE)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t0110990e54b33e853c.jpg) r4ve1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

