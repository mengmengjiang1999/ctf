# 【技术分享】Lua程序逆向之Luac字节码与反汇编

阅读量 **436197**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-17 15:00:25

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

作者：[非虫](http://bobao.360.cn/member/contribute?uid=2669205776)

预估稿费：800RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**传送门**

****

****[**【技术分享】Lua程序逆向之Luac文件格式分析**](http://bobao.360.cn/learning/detail/4534.html)

**  
**

**简介**

****

在了解完了Luac字节码文件的整体结构后，让我们把目光聚焦，放到更具体的指令格式上。
**Luac字节码指令是整个Luac最精华、也是最具有学习意义的一部分，了解它的格式与OpCode相关的知识后，对于逆向分析Luac，会有事半功倍的效果，同时，也为自己开发一款虚拟机执行模板与引擎打下良好的理论基础。**

**指令格式分析**

Luac指令在Lua中使用Instruction来表示，是一个32位大小的数值。在 **Luac.bt**
中，我们将其定义了为Inst结构体，回顾一下它的定义与读取函数：

    
    
    typedef struct(int pc) {
        local int pc_ = pc;
        local uchar inst_sz = get_inst_sz();
        if (inst_sz == 4) {
            uint32 inst;
        } else {
            Warning("Error size_Instruction.");
        }
    } Inst <optimize=false>;

定义的每一条指令为uint32，这与ARM处理器等长的32位指令一样，但不同的是，Lua
5.2使用的指令只有40条，也就是说，要为其Luac编写反汇编引擎，比起ARM指令集，在工作量上要少出很多。

Luac指令完整由：OpCode、OpMode操作模式，以及不同模式下使用的不同的操作数组成。

官方5.2版本的Lua使用的指令有四种格式，使用OpMode表示，它的定义如下：

    
    
    enum OpMode {iABC, iABx, iAsBx, iAx};

其中，i表示6位的OpCode；A表示一个8位的数据；B表示一个9位的数据，C表示一个9位的无符号数据；后面跟的x表示数据组合，如Bx表示B与C组合成18位的无符号数据，Ax表示A与B和C共同组成26位的无符号数据。sBx前的s表示是有符号数，即sBx是一个18位的有符号数。

ABC这些字节大小与起始位置的定义如下：

    
    
    #define SIZE_C9
    #define SIZE_B9
    #define SIZE_Bx(SIZE_C + SIZE_B)
    #define SIZE_A8
    #define SIZE_Ax(SIZE_C + SIZE_B + SIZE_A)
    #define SIZE_OP6
    #define POS_OP0
    #define POS_A(POS_OP + SIZE_OP)
    #define POS_C(POS_A + SIZE_A)
    #define POS_B(POS_C + SIZE_C)
    #define POS_BxPOS_C
    #define POS_AxPOS_A

从定义中可以看来，从位0开始，ABC的排列为A->C->B。

以小端序为例，完整的指令格式定义如下表所示：

先来看最低6位的OpCode，在Lua中，它使用枚举表示，5.2版本的Lua支持40条指令，它们的定义如下所示：

    
    
    typedef enum {
    /*----------------------------------------------------------------------    nameargsdescription
    ------------------------------------------------------------------------*/
    OP_MOVE,/*A BR(A) := R(B)*/
    OP_LOADK,/*A BxR(A) := Kst(Bx)*/
    OP_LOADBOOL,/*A B CR(A) := (Bool)B; if (C) pc++*/
    OP_LOADNIL,/*A BR(A) := ... := R(B) := nil*/
    OP_GETUPVAL,/*A BR(A) := UpValue[B]*/
    OP_GETGLOBAL,/*A BxR(A) := Gbl[Kst(Bx)]*/
    OP_GETTABLE,/*A B CR(A) := R(B)[RK(C)]*/
    OP_SETGLOBAL,/*A BxGbl[Kst(Bx)] := R(A)*/
    OP_SETUPVAL,/*A BUpValue[B] := R(A)*/
    OP_SETTABLE,/*A B CR(A)[RK(B)] := RK(C)*/
    ......
    OP_CLOSE,/*A close all variables in the stack up to (>=) R(A)*/
    OP_CLOSURE,/*A BxR(A) := closure(KPROTO[Bx], R(A), ... ,R(A+n))*/
    OP_VARARG/*A BR(A), R(A+1), ..., R(A+B-1) = vararg*/
    } OpCode;

OpCode定义的注释中，详细说明了每一条指令的格式、使用的参数，以及它的含义。以第一条OP_MOVE指令为例，它接受两个参数R(A)与R(B)，的作用是完成一个赋值操作“
**R(A) := R(B)”** 。

从指令的格式可以看出，尽管OpCode定义的注释中描述了每条指令使用的哪种OpMode，但32位的指令格式中，并没有指出到底每个OpCode对应哪一种OpMode，Lua的解决方法是单独做了一张OpMode的表格luaP_opmodes，它的定义如下：

    
    
    LUAI_DDEF const lu_byte luaP_opmodes[NUM_OPCODES] = {
    /*       T  A    B       C     mode   opcode*/
      opmode(0, 1, OpArgR, OpArgN, iABC)/* OP_MOVE */
     ,opmode(0, 1, OpArgK, OpArgN, iABx)/* OP_LOADK */
     ,opmode(0, 1, OpArgN, OpArgN, iABx)/* OP_LOADKX */
     ,opmode(0, 1, OpArgU, OpArgU, iABC)/* OP_LOADBOOL */
     ,opmode(0, 1, OpArgU, OpArgN, iABC)/* OP_LOADNIL */
     ,opmode(0, 1, OpArgU, OpArgN, iABC)/* OP_GETUPVAL */
     ,opmode(0, 1, OpArgU, OpArgK, iABC)/* OP_GETTABUP */
     ,opmode(0, 1, OpArgR, OpArgK, iABC)/* OP_GETTABLE */
     ,opmode(0, 0, OpArgK, OpArgK, iABC)/* OP_SETTABUP */
     ,opmode(0, 0, OpArgU, OpArgN, iABC)/* OP_SETUPVAL */
     ,opmode(0, 0, OpArgK, OpArgK, iABC)/* OP_SETTABLE */
     ,opmode(0, 1, OpArgU, OpArgU, iABC)/* OP_NEWTABLE */
     ,opmode(0, 1, OpArgR, OpArgK, iABC)/* OP_SELF */
     ,opmode(0, 1, OpArgK, OpArgK, iABC)/* OP_ADD */
     ,opmode(0, 1, OpArgK, OpArgK, iABC)/* OP_SUB */
     ......
     ,opmode(0, 1, OpArgU, OpArgN, iABx)/* OP_CLOSURE */
     ,opmode(0, 1, OpArgU, OpArgN, iABC)/* OP_VARARG */
     ,opmode(0, 0, OpArgU, OpArgU, iAx)/* OP_EXTRAARG */
    };

构成完整的OpMode列表使用了opmode宏，它的定义如下：

    
    
    #define opmode(t,a,b,c,m) (((t)<<7) | ((a)<<6) | ((b)<<4) | ((c)<<2) | (m))

它将OpMode相关的数据采用一字节表示，并将其组成划分为以下几个部分：

m位，占最低2位，即前面OpMode中定义的四种模式，通过它，可以确定OpCode的参数部分。

c位，占2~3位，使用OpArgMask表示，说明C参数的类型。定义如下：

    
    
    enum OpArgMask {
        OpArgN,  /* 参数未被使用 */
        OpArgU,  /* 已使用参数 */
        OpArgR,  /* 参数是寄存器或跳转偏移 */
        OpArgK   /* 参数是常量或寄存器常量 */
    };

b位，占4~5位。使用OpArgMask表示，说明B参数的类型。

a位，占位6。表示是否是寄存器操作。

t位，占位7。表示是否是测试操作。跳转和测试指令该位为1。

将 **luaP_opmodes** 的值使用如下代码打印出来：

    
    
    printf("opcode ver 5.2:n");
    for (int i=0; i<sizeof(luaP_opmodes); i++) {
        printf("0x%x, ", luaP_opmodes[i]);
    }
    printf("n");

输出如下：

    
    
    opcode ver 5.2:
    0x60, 0x71, 0x41, 0x54, 0x50, 0x50, 0x5c, 0x6c, 0x3c, 0x10, 0x3c, 0x54, 0x6c, 0x7c, 0x7c, 0x7c, 0x7c, 0x7c, 0x7c, 0x60, 0x60, 0x60, 0x68, 0x22, 0xbc, 0xbc, 0xbc, 0x84, 0xe4, 0x54, 0x54, 0x10, 0x62, 0x62, 0x4, 0x62, 0x14, 0x51, 0x50, 0x17,

可以看到，有很多指令的OpMode是相同的，比如有多条指令对应的值都是0x7c，如果OpMode的顺序经过修改，要想通过OpMode直接还原所有的指令，是无法做到的，需要配合其他方式来还原，比如Lua虚拟机对指令的处理部分。

**反汇编引擎实现**

编写反汇编引擎需要做到以下几点：

正确的识别指令的OpCode。识别该条指令对应的OpCode，了解当前指令的作用。

处理指令的参数列表。解析不同指令使用到的参数信息，与OpCode在一起可以完成指令反汇编与指令的语义转换。

指令解析。反汇编引擎应该能够支持所有的指令。

指令语义转换。完成反汇编后，加入语义转换，更加方便了解指令的意图。

处理指令依赖关系。处理语义转换时，需要处理好指令之前的关系信息。

下面，我们一条条看如何实现。

**OpCode获取**

首先是通过指令获取对应的OpCode，即传入一个32位的指令值，返回一个OpCode的名称。Lua中有一个GET_OPCODE宏可以通过指令返回对应的OpCode，定义如下：

    
    
    #define GET_OPCODE(i)
    (cast(OpCode, ((i)>>POS_OP) & MASK1(SIZE_OP,0)))

这个宏在010 Editor模板语法中并不支持，因此，实现上，需要编写展开后的代码，并将其定义为函数。功能上就是取32位指令的最低6位，代码如下所示：

    
    
    uchar GET_OPCODE(uint32 inst) {
        return ((inst)>>POS_OP) & ((~((~(Instruction)0)<<(SIZE_OP)))<<(0));
    }

**参数获取**

取指令的参数，包括取指令的A、B、C、Bx、Ax、sBx等信息。前面已经介绍了它们在指令中的位偏移，因此，获取这些参数信息与获取OpCode一样，Lua中提供了GETARG_A、GETARG_B、GETARG_C、GETARG_Bx、GETARG_Ax、GETARG_sBx等宏来完成这些功能，定义如下：

    
    
    #define GETARG_A(i)getarg(i, POS_A, SIZE_A)
    #define GETARG_B(i)getarg(i, POS_B, SIZE_B)
    #define GETARG_C(i)getarg(i, POS_C, SIZE_C)
    #define GETARG_Bx(i)getarg(i, POS_Bx, SIZE_Bx)
    #define GETARG_Ax(i)getarg(i, POS_Ax, SIZE_Ax)
    #define GETARG_sBx(i)(GETARG_Bx(i)-MAXARG_sBx)

同样的，010 Editor模板语法不支持直接定义这些宏，需要编写展开后的代码，实现如下：

    
    
    int GETARG_A(uint32 inst) {
        return ((inst)>>POS_A) & ((~((~(Instruction)0)<<(SIZE_A)))<<(0));
    }
    int GETARG_B(uint32 inst) {
        return ((inst)>>POS_B) & ((~((~(Instruction)0)<<(SIZE_B)))<<(0));
    }
    int GETARG_C(uint32 inst) {
        return ((inst)>>POS_C) & ((~((~(Instruction)0)<<(SIZE_C)))<<(0));
    }
    int GETARG_Bx(uint32 inst) {
        return ((inst)>>POS_Bx) & ((~((~(Instruction)0)<<(SIZE_Bx)))<<(0));
    }
    int GETARG_Ax(uint32 inst) {
        return ((inst)>>POS_Ax) & ((~((~(Instruction)0)<<(SIZE_Ax)))<<(0));
    }
    int GETARG_sBx(uint32 inst) {
        return GETARG_Bx(inst)-MAXARG_sBx;
    }

**指令解析**

在指令解析的编写工作上，参考了luadec的反汇编引擎。它的实现主要位于luadec_disassemble()函数。这里要做的工作就是将它的所有代码与语法都进行一次010
Editor模板语法化。代码片断如下：

    
    
    // luadec_disassemble() from luadec disassemble.c
    string InstructionRead(Inst &inst) {
        local int i = inst.inst;
        OpCode o = (OpCode)GET_OPCODE(i);
        /*
        Printf("inst: 0x%xn", o);
        */
        local int a = GETARG_A(i);
        local int b = GETARG_B(i);
        local int c = GETARG_C(i);
        local int bc = GETARG_Bx(i);
        local int sbc = GETARG_sBx(i);
        local int dest;
        local string line;
        local string lend;
        local string tmpconstant1;
        local string tmpconstant2;
        local string tmp;
        local string tmp2;
        local uchar lua_version_num = get_lua_version();
        local int pc = inst.pc_;
    
        //Printf("Inst: %sn", EnumToString(o));
        switch (o) {
            case OP_MOVE:
    			/*	A B	R(A) := R(B)					*/
    			SPrintf(line,"R%d R%d",a,b);
    			SPrintf(lend,"R%d := R%d",a,b);
    			break;
            case OP_LOADK:  //FIXME OP_LOADK DecompileConstant
    			/*	A Bx	R(A) := Kst(Bx)					*/
    			SPrintf(line,"R%d K%d",a,bc);
                //Printf("OP_LOADK bc:%dn", bc);
    			tmpconstant1 = DecompileConstant(parentof(parentof(inst)),bc);
    			SPrintf(lend,"R%d := %s",a,tmpconstant1);
    			break;
            ......
            case OP_CLOSURE:
            {
    			/*	A Bx	R(A) := closure(KPROTO[Bx])		*/
    			SPrintf(line,"R%d %d",a,bc);
    			SPrintf(lend, "R%d := closure(Function #%d)", a, bc);
    			break;
            }
    		default:
    			break;
    
        }
    
        local string ss;
        SPrintf(ss, "[%d] %-9s %-13s; %sn", pc, get_opcode_str(o),line,lend);
    
        return ss;
    }

上面的代码中，通过GET_OPCODE获取OpCode后，分别对它进行判断与处理，参数信息在函数的最开始获取，方便指令中使用。pc表示当前执行的指令所在位置，方便代码中做语义转换与依赖处理。代码中这一行需要注意：

    
    
    DecompileConstant(parentof(parentof(inst))

因为处理指令时，需要读取指令所在Proto的常量信息，但010
Editor尴尬的模板语法不支持传递指针，也不支持引用类型作为函数的返回值，这导致无法直接读到到Proto的Constants信息。幸好新版本的010
Editor的模板语法加入了self与parentof关键字，用于获取当前结构体与父结构体的字段信息，因此，这里需要对Proto结构体进行修改，让Code结构体成为它的内联的子结构体，如下所示：

    
    
    typedef struct(string level) {
        local string level_ = level;
        //Printf("level:%sn", level_);
        //header
        ProtoHeader header;
        //code
        //Code code;
        struct Code {
            uint32 sizecode <format=hex>;
            local uchar inst_sz = get_inst_sz();
            local int pc = 1;
            if (inst_sz == 4) {
                local uint32 sz = sizecode;
                while (sz-- > 0) {
                    Inst inst(pc);
                    pc++;
                }
            } else {
                Warning("Error size_Instruction.");
            }
            
            typedef struct(int pc) {
                local int pc_ = pc;
                local uchar inst_sz = get_inst_sz();
                if (inst_sz == 4) {
                    uint32 inst;
                } else {
                    Warning("Error size_Instruction.");
                }
            } Inst <read=InstructionRead, optimize=false>;
        
        } code <optimize=false>;
        ......
        // upvalue names
        UpValueNames names;
    } Proto <read=ProtoRead>;

然后在代码中，通过parentof(parentof(inst)就能够返回一个Proto的引用类型，然后就可以愉快的读Proto中所有的字段数据了。

**指令语义转换**

所谓语义转换，就是将直接的指令格式表示成可以读懂的指令反汇编语句。如指令0x0000C1，反汇编后，它的指令表示为“LOADK R3
K0”，LOADK为OpCode的助记符，这里取助记符时，直接通过010
Editor模板函数EnumToString()，传入OpCode名，然后去掉前面的OP_就可以获得。使用get_opcode_str()实现该功能，代码如下：

    
    
    string get_opcode_str(OpCode o) {
        string str = EnumToString(o);
        str = SubStr(str, 3);
        
        return str;
    }

R3表示寄存器，K0表示常量1，即当前函数的Constants中索引为0的Constant。这一条指令经过语义转换后就变成了“R3 :=
xxx”，这个xxx是常量的值，需要通过DecompileConstant()获取它具体的值。

在进行语义转换时，将处理后的指令信息保存到line字符串中，将语义字符串转换到lend字符串中，处理完后输出时加在一起，中间放一个分号。如下所示是指令处理后的输出效果：

    
    
    struct Inst inst[1]
    [2] LOADK     R3 K0        ; R3 := 1

**指令依赖处理**

指令依赖是什么意思呢？即一条指令想要完整的了解它的语义，需要依赖它前面或后面的指令，就解析该指令时，需要用到指令前面或后面的数据。

拿OP_LE指令来说，它的注释部分如下：

    
    
    /*
    A B C
    if ((RK(B) <= RK(C)) ~= A) then pc++  
    */

条件满足时，跳转去执行，否则pc向下，在编写反汇编引擎时，使用的代码片断如下：

    
    
    case OP_LE:
        {
            /*A B Cif ((RK(B) <= RK(C)) ~= A) then pc++  */
            dest = GETARG_sBx(parentof(inst).inst[pc+1].inst) + pc + 2;
            SPrintf(line,"%d %c%d %c%d",a,CC(b),CV(b),CC(c),CV(c));
            tmpconstant1 = RK(parentof(parentof(inst)), b);
            tmpconstant2 = RK(parentof(parentof(inst)), c);
            SPrintf(lend,"if %s %s %s then goto [%d] else goto [%d]",tmpconstant1,(a?invopstr(o):opstr(o)),tmpconstant2,pc+2,dest);
            break;
        }

dest是要跳转的目标地址，GETARG_sBx()返回的是一个有符号的跳转偏移，因为指令是可以向前与向后进行跳转的，RK宏判断参数是寄存器还是常量，然后返回它的值，这里的实现如下：

    
    
    string RegOrConst(Proto &f, int r) {
    if (ISK(r)) {
    return DecompileConstant(f, INDEXK(r));
    } else {
    string tmp;
    SPrintf(tmp, "R%d", r);
    return tmp;
    }
    }
    //#define RK(r) (RegOrConst(f, r))
    string RK(Proto &f, int r) {
        return (RegOrConst(f, r));
    }

最终，OP_LE指令处理后输出如下：

    
    
    struct Inst inst[35] [36] LE 0 R5 R6  ; if R5 <= R6 then goto [38] else goto [40]

其他所有的指令的处理可以参看luadec_disassemble()的代码，这里不再展开。

最后，所有的代码编写完成后，效果如图所示：

luac.bt的完整实现可以在这里找到：<https://github.com/feicong/lua_re> 。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **非虫** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87262](/post/id/87262)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t01107231badf7fd1ea.jpg) 非虫

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

