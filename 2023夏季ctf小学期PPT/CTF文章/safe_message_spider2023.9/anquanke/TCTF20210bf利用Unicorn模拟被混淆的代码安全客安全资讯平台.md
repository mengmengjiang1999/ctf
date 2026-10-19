# TCTF 2021 0bf - 利用Unicorn模拟被混淆的代码

阅读量 **229181**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-15 15:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01518ea2e829c8d00b.jpg)

## 简介

这次的TCTF 2021 Final有队友们的鼎力相助，拿了Rising
Star的冠军，十分刺激。其中收获比较大的是`0bf`这道题目，这是一个10轮的加密算法，代码有大量混淆，加密逻辑没法直观地看出来。赛后官方的writeup是去混淆再解，但在比赛时没有足够的时间来研究混淆的规律，只能硬着头皮分析。这道题目也是我第一次用Unicorn来模拟函数逻辑，收获还是很大。

## 程序逻辑

由于代码经过了混淆，函数严重膨胀，首先要修改IDA的配置文件，将函数大小的上限调高，IDA反编译插件的配置文件在`IDA安装目录\cfg\hexrays.cfg`，打开找到`MAX_FUNCSIZE`，改成一个大数，再重新分析程序的加密函数`sub_11C9`，等上十几分钟，反编译完成后把代码复制到一个文件中，重新格式化成每个赋值语句一行的形式，方便查看。我上传了一份[反编译后的代码](https://pastebin.com/pjH7iacC)，有需要可以下载。

这时从VSCode的代码缩略图中就可以看出，该加密函数有明显的重复部分，例如函数入口的两行：

    
    
      v2 = 12 * (*a1 & 0x4138B65C) + 8 * ~(*a1 & 0xBEC749A3) + (*a1 & 0xBEC749A3) + 1 - 6 * (*a1 ^ 0xBEC749A3) + 8 * ~*a1 + *a1 + 1 - 2 * (*a1 | 0xBEC749A3) - 4 * ~(*a1 | 0xBEC749A3) - 4 * ~(*a1 | 0x4138B65C) + 5 * (*a1 & 0xBEC749A3) + 1688020449;
      v3 = 2636545543LL * v1;
    

和第二轮开始的部分：

    
    
      v106 = 12 * (v103 & 0x70E38EE0) + 8 * ~(v103 & 0x8F1C711F) + (v103 & 0x8F1C711F) + 1 - 6 * (v103 ^ 0x8F1C711F) + 8 * ~v103 + v103 + 1 - 2 * (v103 | 0x8F1C711F) - 4 * ~(v103 | 0x8F1C711F) - 4 * ~(v103 | 0x70E38EE0) + 5 * (v103 & 0x8F1C711F) + 1583631427;
      v107 = 4225108746u * v105;
    

以及第三轮开始的部分：

    
    
      v209 = 12 * (v206 & 0xEEE7AAAE) + 8 * ~(v206 & 0x11185551) + (v206 & 0x11185551) + 1 - 6 * (v206 ^ 0x11185551) + 8 * ~v206 + v206 + 1 - 2 * (v206 | 0x11185551) - 4 * ~(v206 | 0x11185551) - 4 * ~(v206 | 0xEEE7AAAE) + 5 * (v206 & 0x11185551) + 1862844314;
      v210 = 3734538576u * v208;
    

仔细寻找类似的代码，可以将整个加密函数分成10轮，每轮之间传递两个32位的值。第一轮的输入是`a1`开始的8字节，第二轮输入是第一轮计算产生的`v103`和`v105`两个值，依次类推，第10轮完成后计算结果作为加密后的8字节。

第一轮代码大致结构如下：

    
    
      v1 = (unsigned int)a1[1];
      v2 = 12 * (*a1 & 0x4138B65C) + 8 * ~(*a1 & 0xBEC749A3) + ...;
      v3 = 2636545543LL * v1;
      if (2636545543LL * v1) {
        ...
        v10 = 6 * ~((HIDWORD(v9) - 1) | ~(_DWORD)v9 | 0x9D267E07) + 2 * (v9 & ((HIDWORD(v9) - 1) | 0x9D267E07)) - ...;
      } else {
        ...
        v10 = 4 * (~((v1 - 1) | 0x9D267E05) - 3 * ~((v1 - 1) | 0x62D981FA)) - ...;
      }
      v12 = 300216365LL * (21 * (v10 & ~v2 & 0xEE1B0FD2) + 10 * ~(v10 | ~v2 | 0xEE1B0FD2) + ...;
      if (v12) {
        v1222 = -4 * (-(__int64)HIDWORD(v12) ^ (unsigned int)v12);
        v1182 = 6 * (v12 | (HIDWORD(v12) - 1)) + 5 * (~(unsigned __int64)(unsigned int)v12 & (v12 | (HIDWORD(v12) - 1)) ^ -(__int64)HIDWORD(v12));
        ...
      } else {
        v20 = 2 * ~((21 * (v10 & ~v2 & 0xEE1B0FD2) + 10 * ~(v10 | ~v2 | 0xEE1B0FD2) + ....;
        v21 = v20 - (-(21 * (v10 & ~v2 & 0xEE1B0FD2) + 10 * ~(v10 | ~v2 | 0xEE1B0FD2) + ...;
        ...
      }
      ...
      v103 = 4 * (v2 & v93 & v101) - 21 * (v2 & v93 & ~(_DWORD)v101) + ...;
      v105 = 26 * (v10 & v101 & ~v97) + ((unsigned int)v101 & v10 | v97 ^ v101) + ...;
    

从上面的代码可以将一轮的加密过程总结如下：

1、将本轮输入`*a1`，`a1[1]`经过短暂的处理，变为两个新的32位数`v2 = s(*a1)`和`v10 =
t(a[1])`，再用这两个数计算第三个值`v12 = r(v2, v10)`。

2、此后的计算仅依赖于第三个值`v12`（注意计算出`v12`后，下面的代码对`v2`和`v10`的使用形式与`v12`完全相同，均为`21 * (v10
& ~v2 & 0xEE1B0FD2) + ...`，实际上这个表达式还是`v12`）。

3、将第二步的计算结果记为`f(v12)`，则两个输出32位值`v103`和`v105`分别为`g(v2, f(v12))`和`h(v10,
f(v12))`。

`r`，`s`，`t`，`f`，`g`，`h`的具体操作未知。

## 分析

在没法去除混淆的情况下，只能将各段代码分别看作不同的黑盒，通过改变黑盒的输入，观察黑盒的输出，来猜测黑盒中的逻辑。

IDA的反汇编代码中用到的`_DWORD`，`LOWORD`，`__CFADD__`等宏定义可以从`IDA安装目录\plugins\defs.h`中找到，以分析`v2
= s(*a1)`中的`s`函数为例，将IDA反汇编重新改为C代码：

    
    
    #include <assert.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
    
    #include "defs.h"
    
    void f(unsigned int* a1) {
      unsigned int v2 = 12 * (*a1 & 0x4138B65C) + 8 * ~(*a1 & 0xBEC749A3) +
                        (*a1 & 0xBEC749A3) + 1 - 6 * (*a1 ^ 0xBEC749A3) + 8 * ~*a1 +
                        *a1 + 1 - 2 * (*a1 | 0xBEC749A3) - 4 * ~(*a1 | 0xBEC749A3) -                        4 * ~(*a1 | 0x4138B65C) + 5 * (*a1 & 0xBEC749A3) +
                        1688020449;
      printf("%x %x\n", *a1, v2);
    }
    
    int main() {
      srand((unsigned)time(NULL));
      unsigned int a, x;
      for (a = 0; a < 256; a++) {
        x = a;
        f(&x);
      }
      for (a = 0; a < 256; a++) {
        x = rand();
        f(&x);
      }
      return 0;
    }
    

输入0-255的所有值，再输入一些随机的值，可以观察出`s`函数实际为`s(x) = x + 0x6e62d8bf`，通过类似的方法还可以确定`r(x,
y) = g(x, y) = h(x, y) = x ^ y`，`t(x) =
(x*0x9d267e07-((x*0x9d267e07)>>32))&0xFFFFFFFF`。剩余`f`过于复杂，没法直接观察出结果。单轮加密可以总结如下：

    
    
    输入：32位值a，b
    输出：32位值x，y
    v1=(a*C1-((a*C1)>>32))&0xFFFFFFFF
    v2=b+C2
    v3=v1^v2
    x=v1^f(v3)
    y=v2^f(v3)
    

## 解法

不去混淆的情况下，程序中唯一无法求逆的是`f`函数，但观察得知`f`函数的可以通过异或来消去。给定加密结果`x`，`y`，若取`v1'=x^y,
v2'=0`，则`v3'=x^y`，`x'=v1'^f(v3')=x^y^f(x^y)`，`y'=v2'^f(v3')=f(x^y)`，可以发现新的加密中的`y'`即原先的加密时`f`函数的输出，再将`y'`分别与`x`，`y`异或，可以求出原先加密时的`v1`和`v2`。

再取`a'=0, b'=1`，则`v1'=C1,
v2'=C2`，加上上一步解出的`v1`和`v2`，就可以推出最初的`a`和`b`。这样就可以在不对`f`函数求逆的情况下进行解密。

利用[Unicorn](https://www.unicorn-engine.org/)可以方便地对代码片段进行部分模拟。模拟执行的关键在于找到一个合适的起点和终点，将二者之间的代码视为一个黑盒，并且使该黑盒对外部信息的依赖尽可能地小，方便模拟。

加密函数`sub_11C9`的开头部分如下：

    
    
    .text:00000000000011C9                   ; __unwind {
    .text:00000000000011C9 F3 0F 1E FA                       endbr64
    .text:00000000000011CD 55                                push    rbp
    .text:00000000000011CE 48 89 E5                          mov     rbp, rsp
    .text:00000000000011D1 41 57                             push    r15
    .text:00000000000011D3 41 56                             push    r14
    .text:00000000000011D5 41 55                             push    r13
    .text:00000000000011D7 41 54                             push    r12
    .text:00000000000011D9 53                                push    rbx
    .text:00000000000011DA 48 89 7D C0                       mov     [rbp+var_40], rdi
    .text:00000000000011DE 48 8B 45 C0                       mov     rax, [rbp+var_40]
    .text:00000000000011E2 8B 00                             mov     eax, [rax]
    .text:00000000000011E4 41 89 C5                          mov     r13d, eax
    .text:00000000000011E7 48 8B 45 C0                       mov     rax, [rbp+var_40]
    .text:00000000000011EB 48 83 C0 04                       add     rax, 4
    .text:00000000000011EF 8B 00                             mov     eax, [rax]
    .text:00000000000011F1 41 89 C4                          mov     r12d, eax
    .text:00000000000011F4 B8 A3 49 C7 BE                    mov     eax, 0BEC749A3h
    .text:00000000000011F9 4C 31 E8                          xor     rax, r13
    .text:00000000000011FC 48 89 C2                          mov     rdx, rax
    .text:00000000000011FF 48 89 D0                          mov     rax, rdx
    .text:0000000000001202 48 C1 E2 02                       shl     rdx, 2
    .text:0000000000001206 48 29 D0                          sub     rax, rdx
    .text:0000000000001209 48 01 C0                          add     rax, rax
    .text:000000000000120C 48 89 C1                          mov     rcx, rax
    .text:000000000000120F 4C 89 E8                          mov     rax, r13
    

可以将`0x11F4`作为模拟的起点，此时`r12`和`r13`寄存器中分别存放了首轮的输入值。第一轮的结束位于`0xF7AD`，此时加密结果也存放在`r12`和`r13`寄存器中。我们同时还需要中途控制`v3`并检查`v1`和`v2`的值，因此还需要找到一个中间点，可以选在`0x241A`，此时`r12`和`r13`寄存器中分就是`v1`和`v2`。代码如下：

    
    
    void solve(uint64_t start,
               uint64_t middle,
               uint64_t end,
               uint64_t x,
               uint64_t y,
               uint64_t* ox,
               uint64_t* oy) {
      uint64_t z, w, s, t;
      uint32_t a, b;
      do_emulation(binary, start, middle, 1, 0, &s, &t);
      do_emulation(binary, middle, end, x ^ y, 0, &z, &w);
      printf("z=%lx w=%lx s=%lx t=%lx\n", z, w, s, t);
      b = (w ^ y) - t;
      uint64_t m, n;
      assert(exgcd(0x100000001, s, &m, &n) == 1);
      a = ((x ^ w) * n) % 0x100000001;
      if (n & (1UL << 63)) {
        a -= 1;
      }
      printf("n=%lx a=%x b=%x\n", n, a, b);
      *ox = a;
      *oy = b;
    }
    

其中`do_emulation`是用Unicorn模拟执行代码片段，第一次我们从起点开始，`a`和`b`分别取`1`和`0`，运行到中间点，根据上面的分析，此时`r12=C2,
r13=C1`，将结果保存为`s`和`t`。第一次我们从中间点开始，`v1`和`v2`分别取`x^y`和`0`，运行到终点，根据上面的分析，此时`r12=x^y^f(x^y),
r13=f(x^y)`，将结果保存为`z`和`w`。再通过`v1=w^x, v2=w^y`继续逆推出`v1`和`v2`。`b=v2-C2,
a=(v1*n)%0x100000001`，其中`n`是`C1`对`0x100000001`的乘法逆元。

## Unicorn的使用

接下来是`do_emulation`的实现：

    
    
    void do_emulation(FILE* fp,
                      uint64_t start,
                      uint64_t end,
                      uint64_t r12,
                      uint64_t r13,
                      uint64_t* x,
                      uint64_t* y) {
      uc_engine* uc;
      uint64_t size = end - start;
      uint64_t rsp = 0x280000, rbp = 0x2c0000;
    
      assert(uc_open(UC_ARCH_X86, UC_MODE_64, &uc) == UC_ERR_OK);
      assert(uc_mem_map(uc, 0x1000, 0x100000, UC_PROT_ALL) == UC_ERR_OK);
      assert(uc_mem_map(uc, 0x200000, 0x100000, UC_PROT_ALL) == UC_ERR_OK);
      assert(fseek(fp, start, SEEK_SET) == 0);
      assert(fread(buf, size, 1, fp) == 1);
      assert(uc_mem_write(uc, start, buf, size) == UC_ERR_OK);
      assert(uc_reg_write(uc, UC_X86_REG_RSP, &rsp) == UC_ERR_OK);
      assert(uc_reg_write(uc, UC_X86_REG_RBP, &rbp) == UC_ERR_OK);
      assert(uc_reg_write(uc, UC_X86_REG_R12, &r12) == UC_ERR_OK);
      assert(uc_reg_write(uc, UC_X86_REG_R13, &r13) == UC_ERR_OK);
      assert(uc_emu_start(uc, start, end, 0, 0) == UC_ERR_OK);
      assert(uc_reg_read(uc, UC_X86_REG_R12, x) == UC_ERR_OK);
      assert(uc_reg_read(uc, UC_X86_REG_R13, y) == UC_ERR_OK);
      uc_close(uc);
    }
    

题目是PIE程序，为了省去重定位过程，直接将.text段映射到`0x1000`地址处。再分配一个空的栈段，将rsp和rbp都指向栈段，r12和r13填入输入值，调用`uc_emu_start`开始运行即可。

将Unicorn下载下来并编译，一般不建议将自己编译的东西用`make
install`安装到系统目录，避免和已有的东西冲突。网上很多教程编译OpenSSL都敢直接安装到/usr/lib，很多依赖OpenSSL的系统程序都会因此载入错误版本的libssl而无法运行。

采用静态链接+局部包含路径的方式可以很方便地使用自编译的第三方库，同时不污染环境，适合编译仅运行一次的程序，链接到Unicorn时可以使用如下指令：

    
    
    gcc solve.c -I /xxx/download/unicorn/include/ /xxx/download/unicorn/libunicorn.a -lm -lpthread
    

-I选项指定头文件的搜索目录，同时把静态库libunicorn.a直接作为链接器输入，再链接到libm和libpthread即可编译出一个可独立运行的模拟程序。

完整代码参见[Pastebin](https://pastebin.com/DZtjMXiZ)

flag: `flag{0o0..MBA_0bF_1s_S0_1ntEresT1ng!!}`

## 总结

这道题目因为不懂去混淆还是费了很大的力气，最后还是靠加密函数中的异或结构巧妙地重用了已有的二进制代码，还是要提高自己的知识水平，学习去混淆。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Nagi** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/255241](/post/id/255241)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Reverse](/tag/Reverse)
  * [Unicorn](/tag/Unicorn)
  * [emulation](/tag/emulation)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) Nagi

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

