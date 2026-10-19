##  前言

**上篇文章（[一份专供初学者食用的AES加密壳](http://www.freebuf.com/system/235167.html)）中我们分析了一个简单的AES壳的加壳与解壳的过程，在加壳的过程中，直接将源程序加密后，追加到壳的最后一个节当中，这种壳可被秒脱。所以这节在之前的基础上进阶，加大解壳的难度，进行IAT表的加密。**

这篇文章中介绍了IAT加壳与解壳的全过程，并用Ollydbg进行逆向分析，说明这个壳的鸡肋的之处，最后给出了核心源代码。

##  必备基础

必须很熟悉PE结构，特别是导入表的双桥结构。

IAT(Import Address Table)，导入地址表。

节就是区段，区段就是节，但节和节表不是同一个概念。

RVA 相对（基址ImageBase）虚拟地址。

VA 虚拟地址。

**实验环境** ：WIN10 、VS2017、DIE(Detect it Easy)、Ollydbg

**PS：** 这里还不需要了解混淆、花指令、反调试等技术，掌握了上面提到的基础，新手就可以放心阅读了。

##  IAT加解壳的主要步骤

###  **一、加壳步骤**

> 1、打开源程序
>
> 2、加载 Packer.dll
>
> 3、AES加密所有区段
>
> 4、清除目录表
>
> 5、添加新区段
>
> 6、修复重定位表
>
> 7、保存源程序的OEP
>
> 8、将 packer.dll 的 .text 段 拷贝到 .NewSec 段里
>
> 9、修改OEP为 Packer.dll函数入口点在.NewSec 段中的RVA
>
> 10、去掉随机基址
>
> 11、保存被加壳的程序

加壳完成。

示意图如下（从左到右是大致的加壳过程）：图片仅供参考。

![](https://image.3001.net/images/20200507/1588820646_5eb37aa65dba5.png!small)

###  **二、解壳步骤**

解壳的步骤都封装在Packer.dll中，我们来解剖一下它。

> 1、动态获取函数的API地址
>
> 2、AES解密所有区段
>
> 3、恢复目录表
>
> 4、修复IAT表
>
> 5、密码验证对话框弹出
>
> 6、加密IAT表
>
> 7、跳转到原始OEP

解壳完成。

示意图如下（从左到右是大致的解壳过程）：图片仅供参考。

![](https://image.3001.net/images/20200507/1588820660_5eb37ab48bf5e.png!small)

##  IAT加解壳之3问3知

###  一、加壳之3问3知

**1、为什么要加密所有区段 & 清楚目录项呢？**

那当然是为了防止别人分析PE文件，达到保护PE文件的目的。

**2、为什么要添加新节？添加新节后，为何要修复重定位表？**

如果PE文件不增加新节，也可以在其他空白区添加代码。但是这样会有两个不妙的情况：

> （1）空白区根本放不下你的代码，
>
> （2）即使空白区能放得下你的代码，可能空白区的节属性不能执行，修改属性，可能会导致程序执行出错。

明白了新增节的作用，也就知道为啥我们要把Packer.dll的 .text段拷贝到 .NewSec段了：

> （1） .NewSec段是我们自己添加的，大小自己定。
>
> （2）放在新节里，目的是让Packer.dll被执行起来，直接加载到主进程空间是不会运行的，需要获取主进程的控制权。在 .NewSec段
> 我们可以让节"RWE（可读、可写、可执行）"，这样才能让shellcode执行起来。

**3、为什么要去掉随机基址？**

观察这段嵌入汇编：

    
    
    //跳转到原始OEP
    __asm
    {
    mov eax, g_conf.srcOep; //跳转到源程序的OEP
    add eax,0x400000 //srcOep将RVA-->VA ，加上基址0x400000，所以选择的源程序需要选择0x400000，否则会水土不服
    jmp eax
    }

在Packer.dll的入口函数Start()中，我采用固定基址0x400000的方法来计算src
OEP的RV，也就是这段shellcode利用成功的前提要确定一个明确的跳转地址。无论是JMP ESP 等通用跳板指令还是Ret2Libc
使用的各指令，我们都要先确定这条指令的入口点。所谓惹不起躲得起，微软的ASLR（Address Space Layout
Randomization）技术就是通过加载程序的时候不再使用固定的基址加载，从而干扰shellcode 定位的一种保护机制。

——引自《0day漏洞.软件漏洞分析技术（第二版）》

###  二、解壳之3问3知

**1、为什么要动态获取函数的API地址？**

通常我们使用windwos
API都是直接获取IAT表中的函数地址，而这里的情况比较特殊：后面需要对IAT表进行加密，加了密后就不能从IAT表里获取函数地址。

附上一张IAT的表回顾一下：

![](https://image.3001.net/images/20200507/1588820744_5eb37b08502d8.png!small)

**那么有啥办法可以获取到函数地址呢？**

常用的办法：1、LoadLibrary()，然后 GetMoudleName() 2、动态加载

**我这里用的是第2种办法，为啥呢？**

> **对于方法1：** 加载进来后，调用的方法是 [0x12345678] 的形式，这是全局变量的调用方式，当需要重定位的时候，访问这个地址会出错。
>
> **对于方法2：** 动态的方式获取API的地址，兼容性好。获取的方式有3种：（1）利用PEB结构来查找 （2）利用堆栈暴力搜索
> （3）使用SEH的链表来查找。

这里利用PEB结构来查找API的方式，接下来是动态获取API的代码，代码中有详细的解释：

    
    
    _asm
    {
    pushad;
    ; //获取kernel32.dll的加载基址;
    ;// 1. 找到PEB的首地址;
    mov eax, fs:[0x30]; //fs偏移0x30处为peb的首地址, fs为段寄存器
    ;// 2. 得到PEB_LDR_DATA的值;
    mov eax, [eax + 0ch]; //在PEB偏移的0x0c处是指向PEB_LDR_DATA结构的指针
    mov eax, [eax + 0ch]; //eax = > PEB.Ldr的值;
    ; //3. 得到_PEB_LDR_DATA.InLoadOrderMoudleList.Flink的值, 实际得到的就是主模块节点的首地址;
    mov eax, [eax]; //eax = > _PEB_LDR_DATA.InLoadOrderMoudleList.Flink(NTDLL);
    ; //4. 再获取下一个;
    mov eax, [eax]; _LDR_DATA_TABLE_ENTRY.InLoadOrderMoudleList.Flink(kernel32), ;
    mov eax, [eax + 018h]; _LDR_DATA_TABLE_ENTRY.DllBase;
    mov hKernel32, eax;;
    ; //遍历导出表;
    ;// 1.依次获取：dos头、 nt头、 扩展头、 数据目录表;
    mov ebx, [eax + 03ch]; //偏移到NT头;
    add ebx, eax; // NT头的首地址;
    add ebx, 078h; //引出表偏移
    ; //2. 得到导出表的RVA;
    mov ebx, [ebx];
    add ebx, eax; //ebx = 导出表首地址(VA);
    ; //3. 遍历名称表找到GetProcAddress;
    ; //3.1 找到名称表的首地址;
    lea ecx, [ebx + 020h]; //ebx=函数名地址，AddressOfName
    mov ecx, [ecx]; // ecx =名称表的首地址(RVA);
    add ecx, eax; // ecx =名称表的首地址(VA);
    xor edx, edx; // 作为index来使用.
    ; //3.2 遍历名称表;
    _WHILE:;
    mov esi, [ecx + edx * 4]; //esi= 名称的RVA;
    lea esi, [esi + eax];// esi =名称首地址;
    cmp dword ptr[esi], 050746547h; 47657450 726F6341 64647265 7373; //dword:  'PteG' 、'rocA' 、'ddre' 、'ss' =>GetProcAddress，如果是GetProcAddress，表示在AddressOfName中找到了
    jne _LOOP;
    cmp dword ptr[esi + 4], 041636f72h;
    jne _LOOP;
    cmp dword ptr[esi + 8], 065726464h;
    jne _LOOP;
    cmp word  ptr[esi + 0ch], 07373h;
    jne _LOOP;
    ; //找到GetProcAddress后;
    mov edi, [ebx + 024h]; // edi = 函数序号(RVA);
    add edi, eax; 
    mov di, [edi + edx * 2]; //ecx=计算出序号值，序号表是2字节的元素, 因此是 * 2;
    and edi, 0FFFFh; //edi=GetProcAddress在地址表中的下标;
    ; //得到地址表首地址;
    mov edx, [ebx + 01ch]; //edx = 地址表的RVA;
    add edx, eax; //edx = 地址表的VA;
    mov edi, [edx + edi * 4]; //edi = GetProcAddress的RVA;
    add edi, eax; ; //edx =  GetProcAddress的VA;
    mov MyGetProcAddress, edi;
    jmp _ENDWHILE;
    _LOOP:;
    inc edx; // ++index;
    jmp _WHILE; //跳转
    _ENDWHILE:;
    popad; //平衡堆栈
     }

**2、为什么要选择加密IAT表？**

个人从攻防的角度来思考，原因有2：

> （1）对IAT表的函数地址加密后，API就不能一下子看得出来了（比如说Ollydbg就解析不出来dll名），增大逆向分析PE的难度。
>
> （2）AT表PE程序动态执行依赖的dll，加了密之后，恶意代码也就不能用我们的IAT表来使坏了，这也是对程序的一种保护。

**3、如何对IAT进行加解密？**

IAT加解密原理如下：

> （1）遍历导入表获取IAT表里的每个函数地址
>
> （2）取出IAT的函数地址，该函数地址异或 0x12345678，得到加密后的地址
>
> （3）申请一段内存，存放解密后的地址，然后调用该地址的代码。
>
> （4）把申请的内存地址放入IAT表对应表项中。

如此这般，IAT就被加密了。

**我们再来仔细推敲一下步骤（3），NB的你可能早就发现：解密后的地址放在内存中，不做任何保护，恢复IAT表依然无障碍！！！**

别着急，我们来看看这里的解密怎么处理？

> （1）写一段具有迷惑性的代码，干扰逆向分析者对解密后地址的定位，也就是传说中的 **混淆+花指令** 操作。
>
> （2） **动态解密** ：在目标程序运行起来之后，动态地对代码段进行解密。

先运行一段代码、解密一部分的代码，然后再运行解密后的代码，循环直到解密完成。这种方式给逆向带来的挑战是：盯着运行着的代码及附近代码，同时又能兼顾隔得很远的加密状态的代码。

本人新手还是太菜了，现在只能理解 **混淆+花指令** 操作，代码如下：

    
    
    _asm
    {
    push eax;
    mov eax, dwFunAddr; //未加密的函数地址
    xor eax, 0x12345678; //eax = dwFunAddr 异或 0x15151515
    mov dwEncryptFunAddr, eax; //dwEncryptFunAddr=eax
    pop eax;
    }
    // 3.构造一段花指令shellcode，用来解密函数地址
    BYTE OpCode[] = {
    0xE8, 0x01, 0x00, 0x00, //call
    0x00, 0xE9, 0x58, 0xEB, //jmp 
    0x01, 0xE8, 0xB8, 0x85, //MOV EAX,
    0xEE, 0xCB, 0x60, 0xEB, //JMP
    0x01, 0x15, 0x35, 0x12,//ADC EAX,
    0x34, 0x56, 0x78, 0xEB, //ADC EAX,
    0x01, 0xFF, 0x50, 0xEB, //JMP SHORT 1F
    0x02, 0xFF, 0x15, 0xC3  //CALL
      };
    //把函数地址放到解密的OpCode里
    OpCode[11] = dwEncryptFunAddr;    // 0x85  假如：dwEncryptFunAddr = 0x12345678
    OpCode[12] = dwEncryptFunAddr >> 0x08;// 0xEE  十六进制右移8位刚好截掉低位的2位  0x00123456
    OpCode[13] = dwEncryptFunAddr >> 0x10;// 0xCB  十六进制右移16位刚好截掉低位的4位 0x00001234
    OpCode[14] = dwEncryptFunAddr >> 0x18;// 0x60  十六进制右移16位刚好截掉低位的4位 0x00001234

##  Ollydbg逆向分析IAT加密壳

我们先用工具（DiE、importREC）来尝试一下侦壳、脱壳，然后再用Ollydbg分析一下。

未知壳信息

![](https://image.3001.net/images/20200507/1588820836_5eb37b648dab2.png!small)

![](https://image.3001.net/images/20200507/1588820846_5eb37b6e38d88.png!small)

导入表修复失败

![](https://image.3001.net/images/20200507/1588820858_5eb37b7a07716.png!small)

从壳的入口点F7跳进去，进入壳的Start()入口函数

![](https://image.3001.net/images/20200507/1588820879_5eb37b8f78d33.png!small)

真正的入口点，由于这个壳在入口处没加反调试、花指令保护，所以原始程序的OEP一眼就看得到

![](https://image.3001.net/images/20200507/1588820897_5eb37ba1d0bc2.png!small)![](https://image.3001.net/images/20200507/1588821020_5eb37c1c3bfd4.png!small)

F4 跳到密码验证弹框处

![](https://image.3001.net/images/20200507/1588821044_5eb37c34869cd.png!small)

输入密码123 验证，断下；再F7进入IAT加密

![](https://image.3001.net/images/20200507/1588821068_5eb37c4c73d1d.png!small)

![](https://image.3001.net/images/20200507/1588821088_5eb37c60b5a75.png!small)

F7跳到真正的AT函数地址加密的地方，看见一堆花指令

![](https://image.3001.net/images/20200507/1588821107_5eb37c73d0dc6.png!small)

解密密钥藏在花指令的这里

![](https://image.3001.net/images/20200507/1588821129_5eb37c8978714.png!small)

这是shellcode解密函数地址的地方

![](https://image.3001.net/images/20200507/1588821146_5eb37c9aab267.png!small)

观察加密前和加密后eax的值：

![](https://image.3001.net/images/20200507/1588821160_5eb37ca88b577.png!small)![](https://image.3001.net/images/20200507/1588821172_5eb37cb4d5ab6.png!small)

看完了分析，是不是觉得没加保护的壳很鸡肋呢？只要nop填充密码验证弹框和IAT加密，轻而易举就绕过了壳到达真正的程序入口。

在这个基础上，我们该如何去隐藏我们这个入口呢？带着这个问题，和我一样的新手小菜就可以进一步进阶，做出更安全的壳了。

最后我还想说，其实加壳与解壳拼的就是谁对PE更了解，所以掌握基础还是至关重要的。

##  核心代码

###  一、加壳

    
    
    #include <windows.h>
    #include <stdio.h>
    #include "PeFileOperator.h"
    #include <stdio.h>
    int main()
    {
    PeFileOperator myPE;//PE文件操作类对象
    char path[MAX_PATH] = "src.exe";
    //1、打开被加壳程序
    int nTargetSize = 0;
    char* pTargetBuff = myPE.GetFileData(path, &nTargetSize);
    //2、加载Packer.dll
    StubInfo packer = { 0 };
    myPE.LoadStub(&packer); ///这里对IAT表已经加了密，具体查看packer的 Start() 函数
    //3、加密所有区段
    myPE.Encrypt(pTargetBuff, packer);
    //4、清除目录表
    myPE.ClearDataDir(pTargetBuff, packer);
    //添加新节
    char cNewSectionName[] = {".NewSec"};//新节表名
    myPE.AddSection(pTargetBuff, nTargetSize, cNewSectionName,
    myPE.GetSection(packer.dllbase,".text")->Misc.VirtualSize);
    //修复重定位
    myPE.FixStubRelocation((DWORD)packer.dllbase,
    myPE.GetSection(packer.dllbase,".text")->VirtualAddress,
    myPE.GetOptionHeader(pTargetBuff)->ImageBase,
    myPE.GetSection(pTargetBuff, cNewSectionName)->VirtualAddress);
    //保存目标文件的OEP到packer的全局变量中
    //如果不知道为什么移步到这里看一下手动方式注入shellcode，修改OEP  https://www.cnblogs.com/Erma/p/12593860.html 
    packer.pStubConf->srcOep = myPE.GetOptionHeader(pTargetBuff)->AddressOfEntryPoint;
    //将packer.dll的代码段复制到新加的NewSec段中(注意：packer.dll也是个PE文件，主进程加载packer.dll时，作为一个模块附加在主程序的4GB地址空间)
    memcpy(myPE.GetSection(pTargetBuff, cNewSectionName)->PointerToRawData+pTargetBuff,
    myPE.GetSection(packer.dllbase,".text")->VirtualAddress+packer.dllbase,
    myPE.GetSection(packer.dllbase,".text")->Misc.VirtualSize);
    //修改OEP ( OEP = Start(RV)-dll加载基址)-段首RVA+新区段的段首RVA ) ,注意：packer.dll 加载进来是不会自己执行的，一定要获得控制权才可以
    //Start(RV)-dll加载基址)-段首RVA: Start()在.text内的偏移
    /////因为获取到的 start 函数的地址是在dll中的地址，现在这个区段被拷贝到了
        /////被加壳程序中，所以需要重新计算 start 的 RVA 并设置为 OEP
    myPE.GetOptionHeader(pTargetBuff)->AddressOfEntryPoint =
    packer.pfnStart-(DWORD)packer.dllbase
    -myPE.GetSection(packer.dllbase,".text")->VirtualAddress
    +myPE.GetSection(pTargetBuff, cNewSectionName)->VirtualAddress;
    //去掉随机基址：利于shellcode的定位 具体解释见《0day安全：软件漏洞分析技术（第二版）》
    myPE.GetOptionHeader(pTargetBuff)->DllCharacteristics &= (~0x40);
    //保存被加壳的程序
    myPE.SavePEFile(pTargetBuff,nTargetSize,"AES.Packed.exe");
    return 0;
    }

###  二、解壳

    
    
    //************************************************************
    // 函数名称: Start
    // 函数说明: dll的OEP
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    extern "C" __declspec(dllexport) __declspec(naked)
    void Start()
    {
    //获取函数的API地址
    GetApis();
    //解密所有区段
    Decrypt();
    //恢复数据目录表
    RecoverDataDir();
    //修复IAT
    FixImportTable();
    //密码验证对话框弹出
    AlertPasswdBox();
    //加密IAT
    EncryptIAT();
    //跳转到原始OEP
    __asm
    {
    mov eax, g_conf.srcOep; //跳转到源程序的OEP
    add eax,0x400000 //srcOep将RVA-->VA ，加上基址0x400000，所以选择的源程序需要选择0x400000，否则会水土不服
    jmp eax
    }
    }
    //************************************************************
    // 函数名称: Decrypt
    // 函数说明: 解密所有段
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    void  Decrypt()
    {
    //获取当前程序的基址
    DWORD dwBase = (DWORD)pfnGetMoudleHandleA(NULL);
    AES aes(g_conf.key);
    //循环解密所有区段
    DWORD old = 0;
    for (int i = 0; i < g_conf.index-1; i++)
    {
    //拿到所有区段的首地址和大小
    unsigned char* pSection = (unsigned char*)g_conf.data[i][0]+ dwBase;
    DWORD dwSectionSize = g_conf.data[i][1];
    //修改区段属性
    MyVirtualProtect(pSection, dwSectionSize, PAGE_EXECUTE_READWRITE, &old);
    //解密代码段
    aes.InvCipher(pSection, dwSectionSize);
    //把属性修改回去
    MyVirtualProtect(pSection, dwSectionSize, old, &old);
    }
    }
    //************************************************************
    // 函数名称: GetApis
    // 函数说明: 获取API函数地址
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    void GetApis()
    {
    HMODULE hKernel32;
    _asm
    {
    pushad;
    ; //获取kernel32.dll的加载基址;
    ;// 1. 找到PEB的首地址;
    mov eax, fs:[0x30]; //fs偏移0x30处为peb的首地址, fs为段寄存器
    ;// 2. 得到PEB_LDR_DATA的值;
    mov eax, [eax + 0ch]; //在PEB偏移的0x0c处是指向PEB_LDR_DATA结构的指针
    mov eax, [eax + 0ch]; //eax = > PEB.Ldr的值;
    ; //3. 得到_PEB_LDR_DATA.InLoadOrderMoudleList.Flink的值, 实际得到的就是主模块节点的首地址;
    mov eax, [eax]; //eax = > _PEB_LDR_DATA.InLoadOrderMoudleList.Flink(NTDLL);
    ; //4. 再获取下一个;
    mov eax, [eax]; _LDR_DATA_TABLE_ENTRY.InLoadOrderMoudleList.Flink(kernel32), ;
    mov eax, [eax + 018h]; _LDR_DATA_TABLE_ENTRY.DllBase;
    mov hKernel32, eax;;
    ; //遍历导出表;
    ;// 1.依次获取：dos头、 nt头、 扩展头、 数据目录表;
    mov ebx, [eax + 03ch]; //偏移到NT头;
    add ebx, eax; // NT头的首地址;
    add ebx, 078h; //引出表偏移
    ; //2. 得到导出表的RVA;
    mov ebx, [ebx];
    add ebx, eax; //ebx = 导出表首地址(VA);
    ; //3. 遍历名称表找到GetProcAddress;
    ; //3.1 找到名称表的首地址;
    lea ecx, [ebx + 020h]; //ebx=函数名地址，AddressOfName
    mov ecx, [ecx]; // ecx =名称表的首地址(RVA);
    add ecx, eax; // ecx =名称表的首地址(VA);
    xor edx, edx; // 作为index来使用.
    ; //3.2 遍历名称表;
    _WHILE:;
    mov esi, [ecx + edx * 4]; //esi= 名称的RVA;
    lea esi, [esi + eax];// esi =名称首地址;
    cmp dword ptr[esi], 050746547h; 47657450 726F6341 64647265 7373; //dword:  'PteG' 、'rocA' 、'ddre' 、'ss' =>GetProcAddress，如果是GetProcAddress，表示在AddressOfName中找到了
    jne _LOOP;
    cmp dword ptr[esi + 4], 041636f72h;
    jne _LOOP;
    cmp dword ptr[esi + 8], 065726464h;
    jne _LOOP;
    cmp word  ptr[esi + 0ch], 07373h;
    jne _LOOP;
    ; //找到GetProcAddress后;
    mov edi, [ebx + 024h]; // edi = 函数序号(RVA);
    add edi, eax; 
    mov di, [edi + edx * 2]; //ecx=计算出序号值，序号表是2字节的元素, 因此是 * 2;
    and edi, 0FFFFh; //edi=GetProcAddress在地址表中的下标;
    ; //得到地址表首地址;
    mov edx, [ebx + 01ch]; //edx = 地址表的RVA;
    add edx, eax; //edx = 地址表的VA;
    mov edi, [edx + edi * 4]; //edi = GetProcAddress的RVA;
    add edi, eax; ; //edx =  GetProcAddress的VA;
    mov MyGetProcAddress, edi;
    jmp _ENDWHILE;
    _LOOP:;
    inc edx; // ++index;
    jmp _WHILE; //跳转
    _ENDWHILE:;
    popad; //平衡堆栈
     }
    //给函数指针变量赋值
    //Kernel32
    MyLoadLibraryA = (FnLoadLibraryA)MyGetProcAddress(hKernel32, "LoadLibraryA");
    MyVirtualProtect = (FnVirtualProtect)MyGetProcAddress(hKernel32, "VirtualProtect");
    pfnGetMoudleHandleA = (fnGetMoudleHandleA)MyGetProcAddress(hKernel32, "GetModuleHandleA");
    pfnExitProcess = (fnExitProcess)MyGetProcAddress(hKernel32, "ExitProcess");
    pfnVirtualAlloc = (FnVirtualAlloc)MyGetProcAddress(hKernel32, "VirtualAlloc");
    pfnRtlMoveMemory = (FnRtlMoveMemory)MyGetProcAddress(hKernel32, "RtlMoveMemory");
    //Use***
    HMODULE hUse*** = (HMODULE)MyLoadLibraryA((char*)"use***.dll");
    pfnRegisterClassEx = (fnRegisterClassEx)MyGetProcAddress(hUse***, "RegisterClassExW");
    pfnCreateWindowEx = (fnCreateWindowEx)MyGetProcAddress(hUse***, "CreateWindowExW");
    pfnUpdateWindow = (fnUpdateWindow)MyGetProcAddress(hUse***, "UpdateWindow");
    pfnShowWindow=(fnShowWindow)MyGetProcAddress(hUse***, "ShowWindow");
    pfnGetMessage=(fnGetMessage)MyGetProcAddress(hUse***, "GetMessageW");
    pfnTranslateMessage=(fnTranslateMessage)MyGetProcAddress(hUse***, "TranslateMessage");
    pfnDispatchMessageW =(fnDispatchMessageW)MyGetProcAddress(hUse***, "DispatchMessageW");
    pfnGetWindowTextW =(fnGetWindowTextW)MyGetProcAddress(hUse***, "GetWindowTextW");
    pfnSendMessageW =(fnSendMessageW)MyGetProcAddress(hUse***, "SendMessageW");
    pfnDefWindowProcW =(fnDefWindowProcW)MyGetProcAddress(hUse***, "DefWindowProcW");
    pfnPostQuitMessage =(fnPostQuitMessage)MyGetProcAddress(hUse***, "PostQuitMessage");
    pfnFindWindowW =(fnFindWindowW)MyGetProcAddress(hUse***, "FindWindowW");
    pfnMessageBoxW =(fnMessageBoxW)MyGetProcAddress(hUse***, "MessageBoxW");
    pfnBeginPaint =(fnBeginPaint)MyGetProcAddress(hUse***, "BeginPaint");
    pfnEndPaint =(fnEndPaint)MyGetProcAddress(hUse***, "EndPaint");
    }
    //************************************************************
    // 函数名称: AlertPasswdBox
    // 函数说明: 弹框：要求密码验证
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    void AlertPasswdBox()
    {
    //注册窗口类
    g_hInstance = (HINSTANCE)pfnGetMoudleHandleA(NULL);
    WNDCLASSEX ws;
    ws.cbSize = sizeof(WNDCLASSEX);
    ws.hInstance = g_hInstance;
    ws.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    ws.hIcon = NULL;
    ws.hIconSm = NULL;
    ws.hCursor = NULL;
    ws.style = CS_VREDRAW | CS_HREDRAW;
    ws.lpszMenuName = NULL;
    ws.lpfnWndProc = (WNDPROC)WndPrco;//回调函数
    ws.lpszClassName = TEXT("NewSec");
    pfnRegisterClassEx(&ws);
    //创建窗口
    HWND hWnd = pfnCreateWindowEx(0,TEXT("NewSec"),TEXT("密码验证对话框"),
    WS_OVERLAPPED|WS_VISIBLE,
    100,100,400,200,NULL,NULL,g_hInstance,NULL);
    //更新窗口
    //pfnUpdateWindow(hWnd);
    pfnShowWindow(hWnd, SW_SHOW);
    //消息处理
    MSG msg = { 0 };
    while (pfnGetMessage(&msg,NULL,NULL,NULL))
    {
    pfnTranslateMessage(&msg);
    pfnDispatchMessageW(&msg);
    }
    }
    //设置属性可写
    void SetFileHeaderProtect(bool nWrite)
    {
    //获取当前程序的加载基址
    DWORD ImageBase = (DWORD)pfnGetMoudleHandleA(NULL);
    DWORD nOldProtect = 0;
    if (nWrite)
    MyVirtualProtect((LPVOID)ImageBase, 0x400, PAGE_EXECUTE_READWRITE, &nOldProtect);
    else
    MyVirtualProtect((LPVOID)ImageBase, 0x400, nOldProtect, &nOldProtect);
    }
    //************************************************************
    // 函数名称: FixImportTable
    // 函数说明: 修复IAT
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    void FixImportTable()
    {
    //设置文件属性为可写
    SetFileHeaderProtect(true);
    //获取当前程序的加载基址
    DWORD ImageBase = (DWORD)pfnGetMoudleHandleA(NULL);
    IMAGE_THUNK_DATA* pInt = NULL;
    IMAGE_THUNK_DATA* pIat = NULL;
    SIZE_T impAddress = 0;
    HMODULEhImpModule = 0;
    DWORD dwOldProtect = 0;
    IMAGE_IMPORT_BY_NAME* pImpName = 0;
    if (!GetOptionHeader((char*)ImageBase)->DataDirectory[1].VirtualAddress)return;
    //导入表=导入表偏移+加载基址
    IMAGE_IMPORT_DESCRIPTOR* pImp = (IMAGE_IMPORT_DESCRIPTOR*)(GetOptionHeader((char*)ImageBase)->DataDirectory[1].VirtualAddress + ImageBase);
    while (pImp->Name)
    {
    //IAT=偏移+基址
    pIat = (IMAGE_THUNK_DATA*)(pImp->FirstThunk + ImageBase);
    if (pImp->OriginalFirstThunk == 0) // 如果不存在INT则使用IAT
    {
    pInt = pIat;
    }
    else
    {
    pInt = (IMAGE_THUNK_DATA*)(pImp->OriginalFirstThunk + ImageBase);
    }
    // 加载dll
    hImpModule = (HMODULE)MyLoadLibraryA((char*)(pImp->Name + ImageBase));
    //导入函数地址
    while (pInt->u1.Function)
    {
    //判断导入的方式、序号还是名称
    if (!IMAGE_SNAP_BY_ORDINAL(pInt->u1.Ordinal))
    {
    pImpName = (IMAGE_IMPORT_BY_NAME*)(pInt->u1.Function + ImageBase);
    impAddress = (SIZE_T)MyGetProcAddress(hImpModule, (char*)pImpName->Name);
    }
    else
    {
    impAddress = (SIZE_T)MyGetProcAddress(hImpModule, (char*)(pInt->u1.Function & 0xFFFF));
    }
    MyVirtualProtect(&pIat->u1.Function, sizeof(pIat->u1.Function), PAGE_READWRITE, &dwOldProtect);
    pIat->u1.Function = impAddress;
    MyVirtualProtect(&pIat->u1.Function, sizeof(pIat->u1.Function), dwOldProtect, &dwOldProtect);
    ++pInt;
    ++pIat;
    }
    ++pImp;
    }
    SetFileHeaderProtect(false);
    }
    DWORD EncryptFun(DWORD dwFunAddr)
    {
    // 1.申请内存空间
    DWORD dwNewMem = (DWORD)pfnVirtualAlloc(NULL, 0x20, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    // 2.加密函数地址
    DWORD dwEncryptFunAddr = 0;
    _asm
    {
    push eax;
    mov eax, dwFunAddr; //未加密的函数地址
    xor eax, 0x12345678; //eax = dwFunAddr 异或 0x15151515
    mov dwEncryptFunAddr, eax; //dwEncryptFunAddr=eax
    pop eax;
    }
    // 3.构造一段花指令shellcode，用来解密函数地址
    BYTE OpCode[] = {
    0xE8, 0x01, 0x00, 0x00, //call 0x6
    0x00, 0xE9, 0x58, 0xEB, //jmp  0xE801EB62
    0x01, 0xE8, 0xB8, 0x85, //MOV EAX,60CBEE85
    0xEE, 0xCB, 0x60, 0xEB, //JMP SHORT 12
    0x01, 0x15, 0x35, 0x12,//ADC EAX,
    0x34, 0x56, 0x78, 0xEB, //ADC EAX,50FF01EB
    0x01, 0xFF, 0x50, 0xEB, //JMP SHORT 1F
    0x02, 0xFF, 0x15, 0xC3  //CALL DWORD PTR DS:[C3]
    };
    //把函数地址放到解密的OpCode里
    OpCode[11] = dwEncryptFunAddr;// 0x85  假如：dwEncryptFunAddr = 0x12345678
    OpCode[12] = dwEncryptFunAddr >> 0x08;// 0xEE  十六进制右移8位刚好截掉低位的2位  0x00123456
    OpCode[13] = dwEncryptFunAddr >> 0x10;// 0xCB  十六进制右移16位刚好截掉低位的4位 0x00000012
    OpCode[14] = dwEncryptFunAddr >> 0x18;// 0x60  十六进制右移16位刚好截掉低位的4位 0x00000000
    // 4.将数据拷贝到申请的内存
    pfnRtlMoveMemory((LPVOID)dwNewMem, OpCode, 0x20);
    // 5.返回新的函数地址
    return dwNewMem;
    }
    //************************************************************
    // 函数名称: EncryptIAT
    // 函数说明: 加密IAT
    // 参 数: void
    // 返 回 值: void
    //************************************************************
    void EncryptIAT()
    {
    //设置文件属性为可写
    SetFileHeaderProtect(true);
    //获取当前程序的加载基址
    DWORD ImageBase = (DWORD)pfnGetMoudleHandleA(NULL);
    IMAGE_THUNK_DATA* pInt = NULL;
    IMAGE_THUNK_DATA* pIat = NULL;
    SIZE_T impAddress = 0;
    HMODULEhImpModule = 0;
    DWORD dwOldProtect = 0;
    IMAGE_IMPORT_BY_NAME* pImpName = 0;
    if (!GetOptionHeader((char*)ImageBase)->DataDirectory[1].VirtualAddress)return;
    //导入表=导入表偏移+加载基址
    IMAGE_IMPORT_DESCRIPTOR* pImp = (IMAGE_IMPORT_DESCRIPTOR*)(GetOptionHeader((char*)ImageBase)->DataDirectory[1].VirtualAddress + ImageBase);
    while (pImp->Name)
    {
    //IAT=偏移加加载基址
    pIat = (IMAGE_THUNK_DATA*)(pImp->FirstThunk + ImageBase);
    if (pImp->OriginalFirstThunk == 0) // 如果不存在INT则使用IAT
    {
    pInt = pIat;
    }
    else
    {
    pInt = (IMAGE_THUNK_DATA*)(pImp->OriginalFirstThunk + ImageBase);
    }
    // 加载dll
    hImpModule = (HMODULE)MyLoadLibraryA((char*)(pImp->Name + ImageBase));
    //导入函数地址
    while (pInt->u1.Function)
    {
    //判断导入的方式、序号还是名称
    if (!IMAGE_SNAP_BY_ORDINAL(pInt->u1.Ordinal))
    {
    pImpName = (IMAGE_IMPORT_BY_NAME*)(pInt->u1.Function + ImageBase);
    impAddress = (SIZE_T)MyGetProcAddress(hImpModule, (char*)pImpName->Name);
    }
    else
    {
    impAddress = (SIZE_T)MyGetProcAddress(hImpModule, (char*)(pInt->u1.Function & 0xFFFF));
    }
    MyVirtualProtect(&pIat->u1.Function, sizeof(pIat->u1.Function), PAGE_READWRITE, &dwOldProtect);
    pIat->u1.Function = EncryptFun(impAddress);
    MyVirtualProtect(&pIat->u1., sizeof(pIat->u1.Function), dwOldProtect, &dwOldProtect);
    ++pInt;
    ++pIat;
    }
    ++pImp;
    }
    SetFileHeaderProtect(false);
    }
    //************************************************************
    // 函数名称: RecoverDataDir
    // 函数说明: 恢复数据目录表
    // 参 数: DWORD funcAddress 函数地址
    // 返 回 值: void
    //************************************************************
    void RecoverDataDir()
    {
    //获取当前程序的加载基址
    char* dwBase = (char*)pfnGetMoudleHandleA(NULL);
    //获取数据目录表的个数
    DWORD dwNumOfDataDir = g_conf.dwNumOfDataDir;
    DWORD dwOldAttr = 0;
    PIMAGE_DATA_DIRECTORY pDataDirectory = (GetOptionHeader(dwBase)->DataDirectory);
    //遍历数据目录表
    for (DWORD i = 0; i < dwNumOfDataDir; i++)
    {
    if (i == 2)
    {
    pDataDirectory++;
    continue;
    }
    //修改属性为可读可写
    MyVirtualProtect(pDataDirectory, 0x8, PAGE_EXECUTE_READWRITE, &dwOldAttr);
    //还原数据目录表项
    pDataDirectory->VirtualAddress = g_conf.dwDataDir[i][0];
    pDataDirectory->Size = g_conf.dwDataDir[i][1];
    //把属性修改回去
    MyVirtualProtect(pDataDirectory, 0x8, dwOldAttr, &dwOldAttr);
    pDataDirectory++;
    }
    }
    // 壳程序
    int packerDoNum = 1; //这个执行次数可以加大脱壳的难度，这里设为1，方便做实验
    void AllFunc()
    {
    // 递归执行packerDoNum次后执行壳程序
    if (!packerDoNum)
    {
    _asm
    {
    nop
    mov   ebp, esp
    push - 1
    push   0
    push   0
    mov   eax, fs:[0]
    push   eax
    mov   fs : [0], esp
    sub   esp, 0x68
    push   ebx
    push   esi
    push   edi
    pop   eax
    pop   eax
    pop   eax
    add   esp, 0x68
    pop   eax
    mov   fs : [0], eax
    pop   eax
    sub packerDoNum, 1
    pop   eax
    pop   eax
    pop   eax
    mov   ebp, eax
    push AllFunc
    }
    }
    }

##  参考资料

> 《0day安全.软件漏洞分析（第二版）》
>
> 《Windows黑客编程技术》
>
> [动态地址的获取方式](https://bbs.bccn.net/thread-465350-1-1.html)
>
> [C++写壳之高级篇](https://bbs.pediy.com/thread-251267.htm)
>
> [获取GetProcAddress函数地址遇到的的有关问题](http://www.myexception.cn/assembly-> language/553150.html)

***本文作者：m0h1e0，转载请注明来自FreeBuf.COM**

