# DDCTF 2018 writeup(二) 逆向篇

阅读量 **240610**

发布时间 : 2018-05-23 14:14:12

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0172de15c76d1e5e6d.jpg)

### 传送门： [_DDCTF_ 2018 writeup(一)
WEB篇](https://www.anquanke.com/post/id/144879)

## 一. 奈沙夜影与DDCTF

夜影是江苏科技大学大二的一名学生，也是本次比赛的第一名（Excellent！）~对于DDCTF2018他这样评价：

看到群里安姐说平台开放一年的消息，真的佩服！
Σ(ﾟДﾟ|||)━投入这种平台的公司貌似滴滴是头一家？能长期学习交流这样高质量的题目真的是幸事，感谢滴滴安全~(≧ω≦)/

re里的黑盒破解，初看起来觉得很复杂 然后一步一步逆下去抽丝剥茧最终完全理解整个程序的时候 非常巨大的成就感，这题很纯粹很硬核，我对它的印象最深~

总体而言，re系的题目都是考点很明确。以前懒得碰，这次在DD的指bi引po下去详细了解了一波ECC,比特币算法和b58等。

就从各种密码学和新颖的题型上学到了很多知识和技巧，这七天非常充实~ 基本就是醒了就做题，然后一边想着题怎么解一边睡着2333 很令人满足的比赛！

更多CTFer眼中的DDCTF请戳链接：

[https://www.zhihu.com/question/273538879](https://www.zhihu.com/question/273538879)

## 二. 逆向 writeup

### **0x01** **Baby MIPS**

IDA打开发现几个字符串结构都很清晰，提供16个变量，然后进行16次方程校验，但是运行会发现在中间就因为段错误而异常，尝试许久以后发现几个不太对劲的指令，突兀出现的t,
sp, 跳转等等的机器码都为EB02开头，猜测为花指令，于是使用IDC脚本去花。

注意MIPS为定长指令集，每个指令都为4字节，因此需要固定监测指令的头部，否则可能会误清除掉正常指令，例如方程参数的赋值

(╯‵□′)╯︵┻━┻

    
    
    #include <idc.idc>  
    static matchBytes(StartAddr, Match)   
    {   
    auto Len, i, PatSub, SrcSub;   
    Len = strlen(Match);  
    while (i < Len)   
    {   
       PatSub = substr(Match, i, i+1);   
       SrcSub = form("%02X", Byte(StartAddr));   
       SrcSub = substr(SrcSub, i % 2, (i % 2) + 1);   
       if (PatSub != "?" && PatSub != SrcSub)   
       {   
        return 0;   
       }   
       if (i % 2 == 1)   
       {   
        StartAddr++;   
       }   
       i++;   
    }  
    return 1;   
    }  
    static main()   
    {   
       auto StartVa, SavedStartVa, StopVa, Size, i, j;  
    StartVa = 0x400420;   
    StopVa = 0x403233;  
    Size = StopVa - StartVa;   
    SavedStartVa = StartVa;  
    for (i = 0; i < Size/4; i++)   
    {   
       if (matchBytes(StartVa, "EB02????"))   
       {   
        Message("Find%x:%02x%02x%02x%02xn", StartVa,Byte(StartVa),Byte(StartVa+1),Byte(StartVa+2),Byte(StartVa+3));  
        for (j = 0; j < 4; j++)   
        {   
         PatchByte(StartVa, 0x00);   
         MakeCode(StartVa);   
         StartVa++;   
        }   
       }   
        else  
        StartVa=StartVa+4;   
    }  
    AnalyzeArea(SavedStartVa, StopVa);   
    Message("Clear eb02 Opcode Ok ");   
    }   
    

去花后再次分析即可得到清晰的赋值和check过程

有三种求解方法

**简单粗暴反汇编**

写了一个伪执行汇编的py脚本来得到参数，最后清洗一下即可得到方程，通过z3限制BitVec即可跑出整数解

    
    
    f = open("code.txt", "r")  
    flower = ["slti", "sdc1"]  
    a0 = 0x76ff270  
    v0 = 0xd0000  
    v1 = 8  
    fp = [0 for i in range(0x500)]  
    table = [0x0, 0x42d1f0, 0x0, 0x42d1f0,  
    0xa, 0xa, 0x0, 0x9,  
    0x4250bc, 0x9, 0x426630, 0x42d1f0,  
    0x40a3ec, 0x37343431, 0x363434, 0x0,  
    0x0, 0x42d1f0, 0x0, 0x4250bc,  
    0x0, 0x0, 0x425060, 0x42d1f0,  
    0x403ad0, 0x0, 0x0, 0x1000,  
    0x425088, 0x76fff184, 0x412fcd, 0x1,  
    0x410570, 0x425190, 0x40ca48, 0x0,  
    0x0, 0x42d1f0, 0x0, 0x42d1f0,  
    0x425088, 0xffffffff, 0x4106c4, 0xffffffff,  
    0x76fff184, 0x412fcd, 0x1, 0x42d1f0,  
    0x0, 0x425088, 0x40ccac, 0x0,  
    0x0, 0x0, 0x0, 0x42d1f0,  
    0x0, 0x425190, 0x76ffeef8, 0x425190,  
    0x10, 0x425088, 0x40baac, 0x42d1f0,  
    0x412fcd, 0x1, 0x425088, 0x40baac,  
    0x76fff184, 0x412fce, 0x40b684, 0x0,  
    0x0, 0x0, 0x0, 0x42d1f0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x42d1f0, 0x0, 0x42d1f0,  
    0x0, 0x4250bc, 0x413081, 0x9,  
    0x403f24, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x42d1f0,  
    0x0, 0x413078, 0x0, 0x0,  
    0x0, 0x0, 0xd0000, 0xf1f4,  
    0xcf8, 0xf5f1, 0x7883, 0xe2c6,  
    0x67, 0xeccc, 0xc630, 0xba2e,  
    0x6e41, 0x641d, 0x716d, 0x4505,  
    0x76fff224, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0xfffffffe, 0x0,  
    0x76fff2ac, 0x412fcd, 0x1, 0x0,  
    0x6, 0x7fffffff, 0x1, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x0,  
    0xa, 0xa, 0x425088, 0x8,  
    0x7ffffff8, 0x100, 0x413f38, 0x1,  
    0x413f38, 0x0, 0x2, 0x76fff0f8,  
    0x0, 0x0, 0x7fffffff, 0x76fff220,  
    0x405050, 0x550001, 0x0, 0x425000,  
    0x0, 0x0, 0x0, 0x0,  
    0x0, 0x0, 0x0, 0x76fff220,  
    0x404d84, 0x42d1f0, 0x0, 0x500,  
    0x5, 0x42d1f0, 0xb3b, 0x76fff224,  
    0x115, 0x1a131100, 0x76fff220, 0x76fff270,  
    0x76fff2ac, 0xffbecf88, 0xa, 0x405880]  
    j = 0  
    functions = 0  
    for i in range(0xb4, 0x410, 4):  
        fp[i] = table[j]  
        j += 1  
    input = [int(str(i)*3, 16) for i in range(16)]  
    try:  
        while(True):  
            code = f.readline()  
            if(code == ""):  
                print("finish")  
                break  
            if(code[:3] == "loc"):  
                # print("n[s]:t" + code[:-1])  
                continue  
            if(code.find("nop")!=-1):  
                continue  
            code = code.split("$")  
            # print(code)  
            c = code[0].strip()  
            if(c=="sw"):  
                n1 = code[1].split(",")[0]  
                n2 = 0x410 - int("0x" + code[1].split("_")[1].split("(")[0], 16)  
                code = ("fp[" + hex(n2) + "] = " + n1)  
            elif(c=="li"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n2)  
            elif(c=="lw"):  
                n1 = code[1].split(",")[0]  
                if("".join(code).find("fp")!=-1):  
                    n2 = 0x410 - int("0x" + code[1].split("_")[1].split("(")[0], 16)  
                    code = (n1 + " = fp[" + hex(n2) + "]")  
                    # print("# " + hex(fp[n2]))  
                    #输出方程  
                    print("0x%x*"%fp[n2],end='')  
                else:  
                    # print("[c]:t" + "".join(code)[:-1], "v0=%x"%v0)  
                    n2 = ((v0) + int(code[1].split(",")[1].replace("(", "")))//4  
                    code = (n1 + " = input[" + str(n2) + "]")  
                    print("a[%d]"%n2)  
                    # print(code)  
                    # print(hex(v0))  
                    # break  
            elif(c=="sll"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n1 + "<<" + n2)  
            elif(c=="sra"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n1 + ">>" + n2)  
            elif(c=="xori"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n1 + "^" + n2)  
            elif(c=="addiu"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n1 + "+" + n2)  
                # print("+")  
            elif(c=="mul"):  
                n1 = code[1].split(",")[0]  
                n2 = code[2].split(",")[0].strip()  
                n3 = code[3].strip()  
                code = (n1 + " = " + n2 + "*" + n3)  
            elif(c=="addu"):  
                n1 = code[1].split(",")[0]  
                n2 = code[2].split(",")[0].strip()  
                code = (n1 + " = " + n1 + "+" + n2)  
                print("+")  
            elif(c=="subu"):  
                n1 = code[1].split(",")[0]  
                n2 = code[2].split(",")[0].strip()  
                code = (n1 + " = " + n1 + "-" + n2)  
                print("-")  
            elif(c=="beq"):  
                print("=0x%x"%(v0))  
                print("================================================one function=====================================")  
                functions +=1  
                continue  
            elif(c=="negu"):  
                n1 = code[1].split(",")[0]  
                n2 = code[2].split(",")[0].strip()  
                code = (n1 + " = " + "-" + n2)  
                print("-")  
            elif(c=="nop"):  
                continue  
            elif(c=="lui"):  
                n1 = code[1].split(",")[0]  
                n2 = code[1].split(",")[1].strip()  
                code = (n1 + " = " + n2 + "<<32")  
            elif(c=="move" or c=="and"):  
                continue  
            elif(c in flower):  
                # print("[f]:t" + "".join(code)[:-1])  
                continue  
            else:  
                print("[x]:tFind unknown code | " + "".join(code))  
                break  
            # print("[-]:t" + code)  
            exec(code)  
    except Exception as e:  
        print(repr(e))  
        print(code)  
    print(functions)  
    # print(fp)  
    

**优雅反编译**

在某zhao师傅的提醒下想起来jeb的MIPS版本可以对汇编进行简单的反编译：

虽然数组全部是通过指针+偏移的方式来调用，不过可以全部复制下来再用正则来整理数据，将*(par00+x)替换为par00[x/4]的形式（可不要像某zhao师傅一样将参数一个个抄下来哟（不然就会像他一样把参数不慎抄错几个然后纠结若干小时XDDDDDD

上述两种方法得到方程以后就可以通过z3, numpy, matlab一类的数学工具求解方程组了，下面给出z3py的示例代码

    
    
    from z3 import *  
    a = [BitVec("a%d"%i, 32) for i in range(16)]  
    s = Solver()  
    s.add(0xca6a*a[0] -0xd9ee*a[1] +0xc5a7*a[2] +0x19ee*a[3] +0xb223*a[4] +0x42e4*a[5] +0xc112*a[6] -0xcf45*a[7] +0x260d*a[8] +0xd78d*a[9] +0x99cb*a[10] -0x3e58*a[11] -0x97cb*a[12] +0xfba9*a[13] -0xdc28*a[14] +0x859b*a[15]  == 0xaa2ed7)  
    s.add(0xf47d*a[0] +0x12d3*a[1] -0x4102*a[2] +0xcedf*a[3] -0xafcf*a[4] -0xeb20*a[5] -0x2065*a[6] +0x36d2*a[7] -0x30fc*a[8] -0x7e5c*a[9] +0xeea8*a[10] +0xd8dd*a[11] -0xae2*a[12] +0xc053*a[13] +0x5158*a[14] -0x8d42*a[15]  == 0x69d32e)  
    s.add(0xffff52cf*a[0] -0x4fea*a[1] +0x2075*a[2] +0x9941*a[3] -0xbd78*a[4] +0x9e58*a[5] +0x40ad*a[6] -0x8637*a[7] -0x2e08*a[8] +0x4414*a[9] +0x2748*a[10] +0x1773*a[11] +0xe414*a[12] -0x7b19*a[13] +0x6b71*a[14] -0x3dcf*a[15]  == 0x3b89d9)  
    s.add(0xffffedd7*a[0] -0x1df0*a[1] +0x8115*a[2] +0x54bd*a[3] -0xf2ba*a[4] +0xdbd*a[5] +0x1dcf*a[6] +0x272*a[7] -0x2fcc*a[8] -0x93d8*a[9] -0x6f6c*a[10] -0x98ff*a[11] +0x2148*a[12] -0x6be2*a[13] +0x2e56*a[14] -0x7bdf*a[15]  == 0xff6a5aea)  
    s.add(0xffffa8c1*a[0] +0xdc78*a[1] -0x380f*a[2] +0x33c0*a[3] -0x7252*a[4] -0xe5a9*a[5] +0x7a53*a[6] -0x4082*a[7] -0x584a*a[8] +0xc8db*a[9] +0xd941*a[10] +0x6806*a[11] -0x8b97*a[12] +0x23d4*a[13] +0xac2a*a[14] +0x20ad*a[15]  == 0x953584)  
    s.add(0x5bb7*a[0] -0xfdb2*a[1] +0xaaa5*a[2] -0x50a2*a[3] -0xa318*a[4] +0xbcba*a[5] -0x5e5a*a[6] +0xf650*a[7] +0x4ab6*a[8] -0x7e3a*a[9] -0x660c*a[10] +0xaed9*a[11] -0xa60f*a[12] +0xf924*a[13] -0xff1d*a[14] +0xc888*a[15]  == 0xffd31341)  
    s.add(0x812d*a[0] -0x402c*a[1] +0xaa99*a[2] -0x33b*a[3] +0x311b*a[4] -0xc0d1*a[5] -0xfad*a[6] -0xc1bf*a[7] -0x1560*a[8] -0x445b*a[9] -0x9b78*a[10] +0x3b94*a[11] +0x2531*a[12] -0xfb03*a[13] +0x8*a[14] +0x8721*a[15]  == 0xff9a6b57)  
    s.add(0x15c5*a[0] +0xb128*a[1] -0x957d*a[2] +0xdf80*a[3] +0xee68*a[4] -0x3483*a[5] -0x4b39*a[6] -0x3807*a[7] -0x4f77*a[8] +0x652f*a[9] -0x686f*a[10] -0x7fc1*a[11] -0x5d2b*a[12] -0xb326*a[13] -0xacde*a[14] +0x1f11*a[15]  == 0xffd6b3d3)  
    s.add(0xaf37*a[0] +0x709*a[1] +0x4a95*a[2] -0xa445*a[3] -0x4c32*a[4] -0x6e5c*a[5] -0x45a6*a[6] +0xb989*a[7] +0xf5b7*a[8] +0x3980*a[9] -0x151d*a[10] +0xaf13*a[11] +0xa134*a[12] +0x67ff*a[13] +0xce*a[14] +0x79cf*a[15]  == 0xc6ea77)  
    s.add(0xffff262a*a[0] +0xdf05*a[1] -0x148e*a[2] -0x4758*a[3] -0xc6b2*a[4] -0x4f94*a[5] -0xf1f4*a[6] +0xcf8*a[7] +0xf5f1*a[8] -0x7883*a[9] -0xe2c6*a[10] -0x67*a[11] +0xeccc*a[12] -0xc630*a[13] -0xba2e*a[14] -0x6e41*a[15]  == 0xff1daae5)  
    s.add(0xffff9be3*a[0] -0x716d*a[1] +0x4505*a[2] -0xb99d*a[3] +0x1f00*a[4] +0x72bc*a[5] -0x7ff*a[6] +0x8945*a[7] -0xcc33*a[8] -0xab8f*a[9] +0xde9e*a[10] -0x6b69*a[11] -0x6380*a[12] +0x8cee*a[13] -0x7a60*a[14] +0xbd39*a[15]  == 0xff5be0b4)  
    s.add(0x245e*a[0] +0xf2c4*a[1] -0xeb20*a[2] -0x31d8*a[3] -0xe329*a[4] +0xa35a*a[5] +0xaacb*a[6] +0xe24d*a[7] +0xeb33*a[8] +0xcb45*a[9] -0xdf3a*a[10] +0x27a1*a[11] +0xb775*a[12] +0x713e*a[13] +0x5946*a[14] +0xac8e*a[15]  == 0x144313b)  
    s.add(0x157*a[0] -0x5f9c*a[1] -0xf1e6*a[2] +0x550*a[3] -0x441b*a[4] +0x9648*a[5] +0x8a8f*a[6] +0x7d23*a[7] -0xe1b2*a[8] -0x5a46*a[9] -0x5461*a[10] +0xee5f*a[11] -0x47e6*a[12] +0xa1bf*a[13] +0x6cf0*a[14] -0x746b*a[15]  == 0xffd18bd2)  
    s.add(0xf81b*a[0] -0x76cb*a[1] +0x543d*a[2] -0x4a85*a[3] +0x1468*a[4] +0xd95a*a[5] +0xfbb1*a[6] +0x6275*a[7] +0x30c4*a[8] -0x9595*a[9] -0xdbff*a[10] +0x1d1d*a[11] +0xb1cf*a[12] -0xa261*a[13] +0xf38e*a[14] +0x895c*a[15]  == 0xb5cb52)  
    s.add(0xffff6b97*a[0] +0xd61d*a[1] +0xe843*a[2] -0x8c64*a[3] +0xda06*a[4] +0xc5ad*a[5] +0xd02a*a[6] -0x2168*a[7] +0xa89*a[8] +0x2dd*a[9] -0x80cc*a[10] -0x9340*a[11] -0x3f07*a[12] +0x4f74*a[13] +0xb834*a[14] +0x1819*a[15]  == 0xa6014d)  
    s.add(0x48ed*a[0] +0x2141*a[1] +0x33ff*a[2] +0x85a9*a[3] -0x1c88*a[4] +0xa7e6*a[5] -0xde06*a[6] +0xbaf6*a[7] +0xc30f*a[8] -0xada6*a[9] -0xa114*a[10] -0x86e9*a[11] +0x70f9*a[12] +0x7580*a[13] -0x51f8*a[14] -0x492f*a[15]  == 0x2fde7c)  
    if(s.check()==sat):  
        c = b''  
        m = s.model()  
        for i in range(16):  
            print("a[%d]=%d"%(i, m[a[i]].as_long()))  
        for i in range(16):  
            print(chr(m[a[i]].as_long()&0xff), end='')  
    

**符号执行**

无名侠师傅提出了使用angr来全自动求解的方法，注意二进制文件也需要去过花。我这边不知道是因为capstone没有mips反编译的版本还是地址扒错了跑不出来，只好直接附上师傅的脚本。

注意其中find和avoid的值由于各人的bin文件不同，因此地址需要自行修正。

    
    
    from angr import *  
    import logging  
    import IPython  
    logging.getLogger('angr.manager').setLevel(logging.DEBUG)  
    p = Project('mips2')  
    state = p.factory.blank_state(addr=0x400420)  
    DATA_ADDR = 0xA0000  
    state.regs.a0 = DATA_ADDR  
    for i in range(16*4):  
     vec = state.solver.BVS("c{}".format(i),8,explicit_name=True)  
     cond = state.solver.And(vec>=32,vec<=126) # low byte  
     state.memory.store(DATA_ADDR+i,vec)  
     if i % 4 == 0:  
     pass  
    #state.add_constraints(cond)  
    sm = p.factory.simulation_manager(state)  
    res = sm.explore(find=0x403150,avoid=[0x403644,0x401940,0x0401ADC,0x401C74  
    ,0x401E10 ,0x401FA8,0x402144  
    ,0x4022DC,0x402478,0x402610,0x4027A8,0x402940,0x402AD8,0x402C74,0x402E10,0x  
    402FA8,0x403144])  
    # 这些地址不同⼈的bin会不⼀样。  
    found = res.found[0]  
    mem = found.memory.load(DATA_ADDR,16*4)  
    print found.solver.eval(mem)  
    

********

### ****0x0** **2 **黑盒破解******

这个题目比较硬核，输入的地方通过比较字符串来选择函数。首先通过构造函数找到整个数据结构的定义

偏移 | 值 | 类型 | 长度 | 备注 |  
---|---|---|---|---|---  
a1 | sth_p | q | 0x100 |  |  
a1+8 | char_table_0_p | q | 0x100 | 0x6030e0 |  
a1+16 | input | c | 100 |  |  
a1+272 | rand%50 |  |  |  |  
a1+280 | char_table_0_p-sth_p | q |  |  |  
a1+288+8 | char_table_2 | d | 8 | (a1+8)[72+l] 6030e0[l+255] |  
a1+408 | char_table_1 | b | 255 | 0x603700 |  
a1+672 | func_addr | q | 255 | (a1+8)[84+i] 603200+i(+=) |  
a1+672+8 | func_table | q | 8 | (a1+8)[84+6030e0[l+255]] |  
  
输入函数形式为：

    
    
    for i in range(len(input)):  
        *(a1+664) = input[i+1]  
        for j in range(8):  
            if(f[input[i]] == (a1 + 408)[(a1+8)[72+j]]):  
                call (a1+8)[84 + (a1+8)[j+72]] ( a1 )  
    

可以看到，实际上就是令Input[i]作为下标取数组f的值，然后遍历char_table_1中的8个值，如有相等的则取func_addr中对应的函数来调用。

一共8个函数，根据提示语可以定位到其中的一个函数，查看交叉引用则能找到另外8个函数的函数表：

逐个反编译发现：

函数名 | 执行条件 | 表达式 | 功能  
---|---|---|---  
func_0 | (a1+288)<(a1+292) | (a1+665) = char_table[a1+288] | m=c[index]  
func_1 | (a1+288)<(a1+292) | char_table[a1+288] = (a1+665) | c[index]=m  
func_2 | … | (a1+665) = (a1+665) + (a1+664) – 33 | m+=[next]-33  
func_3 | … | (a1+665) = (a1+665) – ((a1+664) – 33) + 1 | m-=[next]-33  
func_4 | … | (a1+288)++ | index++  
check_func | *(a1+664)==’s’ | s = char_table_0[(a1+288)], len=20,puts(s) |
check(s)  
func_6 | … | (a1+288)– | index–  
func_7 | … | 后一个参<=0x59 | char_table_0[a1+288] = input[*(a1+288) + *(a1+664) –
48] – 49  
  
其中用到的变量一共有4个：

    
    
    a1+292 = 255  
    a1+664 = [next]（即input[i+1])  
    a1+665 = m（临时变量）  
    a1+288 = index  
    

在check_func中会输出s，s是从char_table_0中以index为起点取的0x20个值。如果s满足三个方程则通过校验，返回成功。

而实际上那三个方程是不需要逆的—题目中明示了只要输出“Binggo”即可得到flag。因此目标显然是在char_table_0中获得Binggo的字符串，将其dump出来输出了一下发现并字符顺序并没有合适的，甚至上述5个字母都不齐。以及一个最关键的问题，check_func中取了0x20个值赋给s，这显然不符合”Binggo”的要求，因此第七个字符必须给上”使其截断才行。

分析其余7个函数，发现0和1可以交换char_table_0中的字符的位置，2、3和7则可以修改char_table_0中字符的值，4和6则是用来移动下标的，最后check_func加’s’来结束并输出。在构造输入之前，先要找到函数对应的输入值。

逆向一下发现char_table中还被更改了值，IDA动态调试断在函数调用处调用idc脚本,即可得到对应值：

    
    
    auto i, j, v14, p, q;  
    for(i=0;i<8;i++)  
    {  
        p = Byte(0x6030e0+255+i);  
        v14 = 0x400dc1;  
        //for ( j = 0; j <= p; ++j )  
        {  
          v14 = Dword(0x91d440+8+8*(p+0x54));  
        }  
        for(j=0;j<255;j++)  
        {  
            if(Byte(0x603900+j)==Byte(0x91d5d8+p))  
            {  
                q = j;  
                break;  
            }  
            //Message("Not Found : %x", Byte(0x603700+p));  
        }  
        Message("%xt%ct%xn",q , q, v14);  
    }
    
    
    24  $   400dc1  
    38  8   400e7a  
    43  C   400f3a  
    74  t   401064  *  
    30  0   4011c9  
    45  E   40133d  
    75  u   4012f3  *  
    23  #   4014b9  

得到这8个输入字符即可开始构造了。

由于函数功能很多样，因此构造方法很多，在此仅表述我的构造方法：

由于输入buffer有限，因此不适合向右移动指针太多来找寻合适的字符。所以我就原地变换—毕竟将一个字符变成另一个字符满打满算也只要4个输入，移动指针可就轻而易举几十上百了。

下列计划中push表示将char_table中的值取入m，A->B表示将A通过func_2和3变换成B，->1表示指针后移1位

    
    
    push P    # $  
    P->B    # t/  
    pop B    # 8  
    #111(用于填充make，其实1个就够，懒得算了233)  
    B->i    # CH  
    ->1        # 0  
    pop i    # 8  
    i->n    # C&  
    ->1        # 0  
    pop n    # 8  
    ->1        # 0  
    n->g    # t(  
    pop g    # 8  
    ->1        # 0  
    pop g    # 8  
    g->o    # C)  
    ->1        # 0  
    pop o    # 8  
    ->1        # 0  
    make x00    # #0  
    <-6        # uuuuuu  
    End        # Es  
      
    

其中的111是为了make
x00，在指针指向第七个字符时直接构造，提交给服务器即可获得flag。相对而言我觉得这题是所有（re和安卓）题目中质量最高和最（逆向过程中）有趣的~

### **0x03 被隐藏的真实**

这题本来单纯地以为是很简单的题，听欧佳俊师傅讲了一下出题思路才发现他的想法真的比答题人多得多……

main函数里调用了三次get_pwd()这个函数来check输入

get_pwd中接受输入，然后对count自增，调用了Bitcoin对象的一个函数来校验输入

如果熟悉C++逆向的话，一眼就能看出来这是在调用虚函数  

因为v2是对象的空间，在C++的对象构造中，开头4个字节指向的是虚函数表

_v2指向的是虚函数表，_ *v2就是虚函数表的第一个函数了

（图片引自C++对象模型详解释https://www.cnblogs.com/tgycoder/p/5426628.html）

做题的时候不是很熟悉C++的模型，以及虚函数反编译的不是很明显，直接动态调试做的。初始状态这个虚函数是init，其中调用了verify，第一次直接返回输入，对应输出列表的需求，要输入0xdeadbeef的小端序表示”efbeadde”。如果纯静态逆向，会继续往下看verify函数的第二、三次校验，但事实上第二次就没有调用init了。

我在做的时候因为不熟悉虚函数，所以动态调试直接跟进函数，发现进入了sub_4046D7这个函数，其中的核心函数b58e乍看起来很复杂，但其实通过其中的24（实际上是256）、%58，和题目内的信息描述很容易想到比特币地址转换方法–base58

直接进行解密获得bytes类型即可通关（注意最后4字节是sha256的验算字节，不可提交，否则会导致flag的sha256计算错误。因为第二关仅截取19个字符送入，但跟flag有关的sha256却会把所有input全部进行运算，导致最后提示Correct实际上的flag却不对）

话是这么说，直接套来的脚本解密出来其实没看懂，还是自己查资料从加密到解密走了一趟才get到应该是hex格式。第三小关本来以为是脑洞题了，其实是误打误撞做出来的，运气是真的好OTZ

这次虚函数又回到了verify，将Input进行两次sha256然后逆序与结果比较，当时的想法是结合提示语：

查了一下发现这条地址是中本聪在开始比特币时记录的第一个块–创世块，刚开始想到的是根据创世块向区块链后端爆破，某个区块的sha将会满足要求。不过查了一下好像也没什么适合计算的，总不能自己重复一遍挖矿过程吧233

卡了许久，代码中突然发现一个关键点

长度80是个很关键的提示！

于是去找了区块链结构解析，发现区块头的长度正好是80个字节

https://webbtc.com/block/000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f.hex

在这里得到了创世块的头部信息，提交即可获得flag

事实上在经过家俊师傅的讲解后，再回头逆才发现这里的memcmp被覆盖到了sub_404A36函数

这个函数中通过异或生成了一个串，然后将输入的字符串与做过两次sha256再逆序的输入进行memcmp。这个两次sha256再逆序的操作，在之前的查资料过程中发现就是比特币的哈希方法，把异或生成的串dump出来去搜索。

IDC>auto i;for(i=0;i<80;i++){Message(“%02x”,
Byte(0x6d0a00+i));}000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f4e61

发现是创世块的哈希值，由此倒推出原输入是创世块。

比赛的时候从一个长度猜到创世块头部，不得不感叹自己的运气真的是……

最后再分析一下虚函数的覆盖，和家俊师傅挖下的种种坑

首先注意到虚函数表中的第一个函数在初始情况下是Init

逐步跟踪，发现Bitcoin在构造函数中就有玄机

这里跳转到了0x6D0F88处，过去看看

这时是直接一个leave和retn返回了

但是后面有很多不可识别的脏数据，暂且先放着不管，继续往后走

get_pwd函数中就如之前分析的一样，没什么问题

问题在于析构函数里

乍一看好像没什么问题哦，delete释放空间嘛

注意这里的(this+3)指向的就是刚才跳转的0x6D0F88

再点进delete内一看

？！

跟正常调用free的delete完全不一样，左边function列表中也竟然出现了两个同名的函数

另外一个才是调用free的原delete，这个是冒牌的！

这里利用的是IDA的重命名机制–C++编译器为了区分重载函数，会对函数生成一些其他字符来修饰。delete函数被修饰以后的名称是”_ZdaPv”，但是冒牌delete函数的原名是”__ZdaPv”，IDA同样也会将其重命名为delete，导致被忽视。

这个delete中将参数指向的空间写为0x90，即NOP的机器码

因此可以将刚才的leave、retn和大量脏数据全部写成NOP，从而使下一次调用构造函数的时候可以执行一些其他代码，而这个机密的函数就是脏数据之后的代码，sub_6D1048

这里的a1是rbp，频繁调用的a1-8就是this指针

可以看到，每次调用都会覆盖一次虚函数

另外当第三次执行的时候会将memcmp重写

整个理透以后这个题目学到的应该是最多的，各种阴险技术，真的很有意思23333

可惜做的时候动态跟过去会忽视掉这里的大量重写，比较可惜

****

### **0x04 探寻逝去的Atlantis文明**

打开文件发现啥都没有

运行杀毒软件提示有代码混淆器

OD挂上各种报错，估计有反调

于是从头分析，首先是两个TlsCallback

TlsCallback_0中第一个函数sub_402B30动态获取了ZwSetInformationThread设置当前线程的信息

    
    
    v0 = GetModuleHandleA(&ModuleName);           // Ntdll  
      v1 = GetProcAddress(v0, &ProcName);           // ZwSetInformationThread  
      v2 = GetCurrentThread();  
      return ((int (__stdcall *)(HANDLE, signed int, _DWORD, _DWORD))v1)(v2, 17, 0, 0);//  ThreadHideFromDebugger  
    

百度一下可以轻松发现这个函数经常被用来反调试，第17个参数正好就是反调用的：

将其首字节改成0xc3，爆破掉即可

后一个函数sub_4028F0同样也是动态获取了4个函数的地址，将它们保存在了一个函数表中留待日后取用。其中一个是IsDebuggerPresent这样的反调函数，另外三个则是VirtualAlloc、VirtualFree和Exit这种有用的函数，因此不可简单Patch

再往后立即就调用了刚才的IsDebuggerPresent，判断到直接Exit

这里Patch或者下断过都行，小问题

TlsCallback_1里则是一个MessageBox，无关紧要

接着进入main主函数

那三个连续的函数不用在意，解密代码很复杂，无需关心

sub_43180里是对Debug断点的Hook

我们知道调试器下断的原理是将某个地址的机器码改为0xcc，使其触发异常，从而被调试器捕捉中断

这个Hook会将0xcc改为0xc3，直接ret，导致不仅调试器捕捉不到断点，而且会直接令程序崩溃

这个函数里除了Hook没有别的东西，直接Patch掉

sub_403010里才是重头戏，通过memcpy将解密后的代码送入开辟出的空间中，然后直接调用

几个函数通过F8步过函数可以大致猜测出功能

关键在change_input和check两个函数中

其实当把那几个反调试通过以后就问题就不大了

动态调试跟进去，发现change_input中将Inputbase64后通过GlobalAddAtom将其加入了全局原子

再往后跟的几个函数都格外的复杂，再加上代码是动态解密的，每次都需要自己MakeCode再F5才能浏览一遍猜测是否需要详细跟踪

事实上在AddAtom之后虽然还有几个函数调用了Input的指针，但它们都是释放空间用的。

这个AddAtom添加了一个全局可用的字符串，必然在某处调用了GlobalGetAtomName

因此不妨稍微忽视一下其他函数，再往后跟

果不其然在v19，即check中捕捉到了GlobalGetAtomName的调用

该函数中生成了一个table，然后将table进行一顿操作后与Input逐字节异或，最后与另一个值进行比较—非常简单粗暴常见的逆向套路了

可以通过dump将table得到，然后效仿操作与结果数组异或从而得到flag

但更简单的方法当然是注意到这两点：

  1. 异或的逆运算还是异或

  2. 将table进行一顿操作与input完全无关

因此将结果数组直接放入Input的地址中，等到比较的时候，该地址中就是我们需要input的值了

解base64轻松得到flag。

**本次 逆向篇的writeup到此结束啦~** **比赛平台地址：<http://ddctf.didichuxing.com>** ****

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **滴滴出行DSRC** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/145553](/post/id/145553)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [技术分析](/tag/技术分析)
  * [安全研究](/tag/安全研究)
  * [DDCTF](/tag/DDCTF)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t01658dc77240b945a8.jpg) 滴滴出行DSRC

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

