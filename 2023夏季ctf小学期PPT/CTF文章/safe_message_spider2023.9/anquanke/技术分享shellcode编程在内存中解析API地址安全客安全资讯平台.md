# 【技术分享】shellcode编程：在内存中解析API地址

阅读量 **183519**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-01-23 11:04:41

 **x**

##### 译文声明

本文是翻译文章，文章来源：modexp.wordpress.com

原文地址：<https://modexp.wordpress.com/2017/01/15/shellcode-resolving-api-addresses/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**0x00 前言**

针对Windows的所有的与位置无关代码（PIC）的核心功能的基础就是实时解析API函数的地址。它是一个非常重要的任务。在这里我介绍两种流行的方法，使用导入地址表（IAT）和导出地址表（EAT）是目前为止最稳定的方法。

自从2007年Windows Vista发布以来，地址空间布局随机化（ASLR）在可执行文件和动态链接库中启用，这些开启ASLR的库用来缓解漏洞利用。

但是在ASLR出现之前，20年前的病毒开发者同样遇到一个相似的问题，kernel32.dll基址的无意的“随机化”。

第一个Windows
95的病毒叫做[Bizatch](http://virus.wikidot.com/bizatch)，由Quantum/VLAD在一个Windows
95的beta版本上编写。

Mr. Sandman, Jacky Qwerty 和
GriYo讨论过kernel32的问题、[Win32下面PE感染](http://vxheaven.org/29a/29a-2/29a-2.3_1)的GetModuleHandle解决方案，和当时不清楚的进程环境块（PEB）在后来由Ratter在[“在NT下从PEB获取重要数据”](http://vxheaven.org/29a/29a-6/29a-6.224)中讨论。

Jacky
Qwerty公布了一种[类GetProcAddress](http://vxheaven.org/29a/29a-2/29a-2.3_5)的功能，成为病毒中解析API的标准方法。

在这之后，作者开始通过CRC32的校验和来解析API，可以隐藏代码中的API字符串，同时减少空间。

在1999年LethalMind展示了一种他自己的校验和[解析API地址](https://vxheaven.org/29a/29a-4/29a-4.227)的方法。在2002年[LSD组织](http://lsd-pl.net/)提出了在Win32汇编（shellcode）中获取API的算法，之后被很多Win32 shellcode效仿。

上述是关于API获取的方案的一个简短的历史。到了今天，在漏洞利用时已经出现了很多高级技术，但是他们和保护机制强相关，在这不做讨论。

下面展示的左右结构能在微软SDK中WinNT.h头文件中找到。

你还能在[pecoff.docx](http://wordpress.redirectingat.com/?id=725X1342&site=modexp.wordpress.com&xs=1&isjs=1&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fdownload%2Fdetails.aspx%3Fid%3D19509&xguid=cb98a2b4a36da2c7175731d5e7783944&xuuid=a18e8de5088faafbb29427360d580a7b&xsessid=9)中找到PE/PE+文件格式的详细描述。

**0x01 Image DOS Header**

在每个PE文件开始都能找到一个MS-DOS可执行文件或者一个“存根”（即MZ）使得可验证为有效的MS-DOS可执行文件。

在这里我们需要e_lfnew字段，加上当前模块基址能得到NT_IMAGE_HEADERS的指针。

**  
**

**0x02 Image NT Headers**

因为在内存中映射的PE映像的基址是随机的，只有重要结构的相对虚拟地址（RVA）保存在PE文件中。  

为了将RVA转化为虚拟地址（VA），可以使用以下宏。

通过基址加上e_lfanew，然后获得指向IMAGE_NT_HEADERS的指针。

下面两个结构在头文件WinNT.h中定义了，但是编译时根据架构只是用一个。

**0x03 Image Optional Header**  

在可选头的末尾是一个IMAGE_DATA_DIRECTORY结构的数组。

    
    
    // Directory Entries
    #define IMAGE_DIRECTORY_ENTRY_EXPORT 0   // Export Directory
    #define IMAGE_DIRECTORY_ENTRY_IMPORT 1   // Import Directory
    //
    // Optional header format.
    //
    typedef struct _IMAGE_OPTIONAL_HEADER {
      //
      // Standard fields.
      //
      WORD    Magic;
      BYTE    MajorLinkerVersion;
      BYTE    MinorLinkerVersion;
      DWORD   SizeOfCode;
      DWORD   SizeOfInitializedData;
      DWORD   SizeOfUninitializedData;
      DWORD   AddressOfEntryPoint;
      DWORD   BaseOfCode;
      DWORD   BaseOfData;
      //
      // NT additional fields.
      //
      DWORD   ImageBase;
      DWORD   SectionAlignment;
      DWORD   FileAlignment;
      WORD    MajorOperatingSystemVersion;
      WORD    MinorOperatingSystemVersion;
      WORD    MajorImageVersion;
      WORD    MinorImageVersion;
      WORD    MajorSubsystemVersion;
      WORD    MinorSubsystemVersion;
      DWORD   Win32VersionValue;
      DWORD   SizeOfImage;
      DWORD   SizeOfHeaders;
      DWORD   CheckSum;
      WORD    Subsystem;
      WORD    DllCharacteristics;
      DWORD   SizeOfStackReserve;
      DWORD   SizeOfStackCommit;
      DWORD   SizeOfHeapReserve;
      DWORD   SizeOfHeapCommit;
      DWORD   LoaderFlags;
      DWORD   NumberOfRvaAndSizes;
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
    } IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;

**0x04 Image Data Directory**

每个目录拥有一个相对虚拟地址和大小。为了访问导出和导入目录，可简单的通过RVA2VA的宏得到虚拟地址。

VirtualAddress：

数据结构的相对虚拟地址。例如，如果这个结构是导入目录，这个字段填充IMAGE_IMPORT_DESCRIPTOR数组的相对虚拟地址。

Size：

包含指向的数据结构的大小。

**  
**

**0x05 Image Export Directory**  

因为导出目录是目录表的第一项，我们将解释这种获取API的方法。

我们只对5个字段有兴趣：

**Name**

DLL名字字符串的相对虚拟地址

**NumberOfNames**

通过名字导出的API的个数

**AddressOfFunctions**

指向所有函数的VA数组的相对虚拟机地址。每个VA加上模块基址，能得到一个导出函数的地址。

**AddressOfNames**

指向所有函数名的VA数组的相对虚拟机地址。每个VA加上模块基址，能得到表示API的非0结尾的字符串的地址。

**AddressOfNameOrdinals**

序号数组的相对虚拟地址。每个序号表示一个AddressOfFunctions数组的索引。

下面的函数使用DLL和API名字的CRC-32C哈希值，从导出表中获取API的地址。  

参数base明显是DLL的基址，参数hash是2个CRC-32C的哈希值。crc32c(DLL字符串)+crc32c(API字符串)。

    
    
    LPVOID search_exp(LPVOID base, DWORD hash)
    {
      PIMAGE_DOS_HEADER       dos;
      PIMAGE_NT_HEADERS       nt;
      DWORD                   cnt, rva, dll_h;
      PIMAGE_DATA_DIRECTORY   dir;
      PIMAGE_EXPORT_DIRECTORY exp;
      PDWORD                  adr;
      PDWORD                  sym;
      PWORD                   ord;
      PCHAR                   api, dll;
      LPVOID                  api_adr=NULL;
      dos = (PIMAGE_DOS_HEADER)base;
      nt  = RVA2VA(PIMAGE_NT_HEADERS, base, dos->e_lfanew);
      dir = (PIMAGE_DATA_DIRECTORY)nt->OptionalHeader.DataDirectory;
      rva = dir[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
      // if no export table, return NULL
      if (rva==0) return NULL;
      
      exp = (PIMAGE_EXPORT_DIRECTORY) RVA2VA(ULONG_PTR, base, rva);
      cnt = exp->NumberOfNames;
      // if no api, return NULL
      if (cnt==0) return NULL;
      
      adr = RVA2VA(PDWORD,base, exp->AddressOfFunctions);
      sym = RVA2VA(PDWORD,base, exp->AddressOfNames);
      ord = RVA2VA(PWORD, base, exp->AddressOfNameOrdinals);
      dll = RVA2VA(PCHAR, base, exp->Name);
      
      // calculate hash of DLL string
      dll_h = crc32c(dll);
      
      do {
        // calculate hash of api string
        api = RVA2VA(PCHAR, base, sym[cnt-1]);
        // add to DLL hash and compare
        if (crc32c(api) + dll_h == hash) {
          // return address of function
          api_adr = RVA2VA(LPVOID, base, adr[ord[cnt-1]]);
          return api_adr;
        }
      } while (--cnt && api_adr==0);
      return api_adr;
    }

一个重要的事情是这个函数不能解析通过序号导出的API，前向引用有时也是个问题。  

下面是实现相同功能的汇编代码。

    
    
    ; in:  ebx = base of module to search
    ;      ecx = hash to find
    ;
    ; out: eax = api address resolved in EAT
    ;
    search_expx:
        pushad
        ; eax = IMAGE_DOS_HEADER.e_lfanew
        mov    eax, [ebx+3ch]
        ; first directory is export
        ; ecx = IMAGE_DATA_DIRECTORY.VirtualAddress
        mov    ecx, [ebx+eax+78h]
        jecxz  exp_l2
        ; eax = crc32c(IMAGE_EXPORT_DIRECTORY.Name)
        mov    eax, [ebx+ecx+0ch]
        add    eax, ebx
        call   crc32c
        mov    [esp+_edx], eax
        ; esi = IMAGE_EXPORT_DIRECTORY.NumberOfNames
        lea    esi, [ebx+ecx+18h]
        push   4
        pop    ecx         ; load 4 RVA
    exp_l0:
        lodsd              ; load RVA
        add    eax, ebx    ; eax = RVA2VA(ebx, eax)
        push   eax         ; save VA
        loop   exp_l0
        pop    edi          ; edi = AddressOfNameOrdinals
        pop    edx          ; edx = AddressOfNames
        pop    esi          ; esi = AddressOfFunctions
        pop    ecx          ; ecx = NumberOfNames
       sub    ecx, ebx     ; ecx = VA2RVA(NumberOfNames, base)
        jz     exp_l2       ; exit if no api
    exp_l3:
        mov    eax, [edx+4*ecx-4] ; get VA of API string
        add    eax, ebx           ; eax = RVA2VA(eax, ebx)
        call   crc32c             ; generate crc32 of api string
        add    eax, [esp+_edx]    ; add crc32 of DLL string
        cmp    eax, [esp+_ecx]    ; found match?
        loopne exp_l3             ; --ecx && eax != hash
        jne    exp_l2             ; exit if not found
        xchg   eax, ebx
        xchg   eax, ecx
        movzx  eax, word [edi+2*eax] ; eax = AddressOfOrdinals[eax]
        add    ecx, [esi+4*eax] ; ecx = base + AddressOfFunctions[eax]
    exp_l2:
        mov    [esp+_eax], ecx
        popad
        ret

这就是从导出目录获取API的方法。通过导入表更加巧妙。

**  
**

**0x06 Image Import Descriptor**  

2009年微软发布的[EMET](http://wordpress.redirectingat.com/?id=725X1342&site=modexp.wordpress.com&xs=1&isjs=1&url=https%3A%2F%2Fwww.microsoft.com%2Fen-ie%2Fdownload%2Fdetails.aspx%3Fid%3D50766&xguid=af1c229770783c0d21eeb9ff0b7752a7&xuuid=26a5c8a10a811eabfe96ba08cc519a8f&xsessid=2)阻止了一些从导出目录获取API的shellcode。

EMET从5.2版本开始，包含了导出表访问过滤（EAF）和EAF+功能，都会阻止尝试从模块读取导出和导入目录。

通常，一个shellcode使用IAT解析其他函数前会先获取[GetModuleHandle](http://wordpress.redirectingat.com/?id=725X1342&site=modexp.wordpress.com&xs=1&isjs=1&url=https%3A%2F%2Fmsdn.microsoft.com%2Fen-us%2Flibrary%2Fwindows%2Fdesktop%2Fms683199\(v%3Dvs.85\).aspx&xguid=af1c229770783c0d21eeb9ff0b7752a7&xuuid=26a5c8a10a811eabfe96ba0)和[GeProcAddress](http://wordpress.redirectingat.com/?id=725X1342&site=modexp.wordpress.com&xs=1&isjs=1&url=https%3A%2F%2Fmsdn.microsoft.com%2Fen-us%2Flibrary%2Fwindows%2Fdesktop%2Fms683212\(v%3Dvs.85\).aspx&xguid=af1c229770783c0d21eeb9ff0b7752a7&xuuid=26a5c8a10a811eabfe96ba0)的地址。

如果PE文件从其他模块导入API，这个导入目录将包含导入描述符的数组，每个代表一个模块。

来看下面3个字段：

**OriginalFirstThunk**

包含导入函数名的偏移。

**Name**

非0结尾字符串表示的导入API的源模块名。

**FirstThunk**

包含真实函数地址的偏移。

  

**0x07 Image Thunk Data**  

每个描述符包含了指向Image Thunk Data结构数组的指针。每个入口表示了导入的API的信息。

在代码中，我跳过了那些使用序号导入的入口。

来自OriginalFirstThunk的AddressOfData字段是指向IMPORT_BY_NAME结构的RVA。

FirstThunk的Function字段指向我们要搜索的API的真实地址。

**  
**

**0x08 Image By Name**  

因为我们不处理从序号导入的情况，所以我们不关心hint字段，只需要非0结尾字符串表示的API名。

**Hint**

包含索引到DLL函数导出表的位置。这个字段被PE加载器使用，因此它能够在DLL导出表中快速的查找函数。这个值不是必须的，有些链接器将这个字段设置为0。

**Name**

包含导入函数的名字。是一个ASCIIZ字符串。注意Name字段的大小是可变的。提供的结构方便使您可以使用描述性名称引用数据结构。

下面的代码使用DLL和API名字的CRC-32C哈希值，从导出表中获取API的地址。

    
    
    LPVOID search_imp(LPVOID base, DWORD hash)
    {
      DWORD                    dll_h, i, rva;
      PIMAGE_IMPORT_DESCRIPTOR imp;
      PIMAGE_THUNK_DATA        oft, ft;
      PIMAGE_IMPORT_BY_NAME    ibn;
      PIMAGE_DOS_HEADER        dos;
      PIMAGE_NT_HEADERS        nt;
      PIMAGE_DATA_DIRECTORY    dir;
      PCHAR                    dll;
      LPVOID                   api_adr=NULL;
      
      dos = (PIMAGE_DOS_HEADER)base;
      nt  = RVA2VA(PIMAGE_NT_HEADERS, base, dos->e_lfanew);
      dir = (PIMAGE_DATA_DIRECTORY)nt->OptionalHeader.DataDirectory;
      rva = dir[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
      
      // if no import table, return
      if (rva==0) return NULL;
      imp  = (PIMAGE_IMPORT_DESCRIPTOR) RVA2VA(ULONG_PTR, base, rva);
      
      for (i=0; api_adr==NULL; i++) 
      {
        if (imp[i].Name == 0) return NULL;
        
        dll   = RVA2VA(PCHAR, base, imp[i].Name);
        dll_h = crc32c(dll); 
        
        rva   = imp[i].OriginalFirstThunk;
        oft   = (PIMAGE_THUNK_DATA)RVA2VA(ULONG_PTR, base, rva);
        
        rva   = imp[i].FirstThunk;
        ft    = (PIMAGE_THUNK_DATA)RVA2VA(ULONG_PTR, base, rva);
            
        for (;; oft++, ft++) 
        {
          if (oft->u1.Ordinal == 0) break;
          // skip import by ordinal
          if (IMAGE_SNAP_BY_ORDINAL(oft->u1.Ordinal)) continue;
          
          rva = oft->u1.AddressOfData;
          ibn = (PIMAGE_IMPORT_BY_NAME)RVA2VA(ULONG_PTR, base, rva);
          
          if ((crc32c(ibn->Name) + dll_h) == hash) {
            api_adr = (LPVOID)ft->u1.Function;
            break;
          }
        }
      }
      return api_adr;
    }

相同功能的汇编代码如下，但是有了些优化。  

    
    
    in: ebx = base of module to search
    ;     ecx = hash to find
    ;
    ; out: eax = api address resolved in IAT
    ;
    search_impx:
        xor    eax, eax    ; api_adr = NULL
        pushad
        ; eax = IMAGE_DOS_HEADER.e_lfanew
        mov    eax, [ebx+3ch]
        add    eax, 8     ; add 8 for import directory
        ; eax = IMAGE_DATA_DIRECTORY.VirtualAddress
        mov    eax, [ebx+eax+78h]
        test   eax, eax
        jz     imp_l2
        lea    ebp, [eax+ebx]
    imp_l0:
        mov    esi, ebp      ; esi = current descriptor
        lodsd                ; OriginalFirstThunk +00h
        xchg   eax, edx      ; temporarily store in edx
        lodsd                ; TimeDateStamp      +04h
        lodsd                ; ForwarderChain     +08h
        lodsd                ; Name_              +0Ch
        test   eax, eax
        jz     imp_l2        ; if (Name_ == 0) goto imp_l2;
        add    eax, ebx
        call   crc32c
        mov    [esp+_edx], eax
        lodsd                 ; FirstThunk
        mov    ebp, esi       ; ebp = next descriptor
        lea    esi, [edx+ebx] ; esi = OriginalFirstThunk + base
        lea    edi, [eax+ebx] ; edi = FirstThunk + base
    imp_l1:
        lodsd                 ; eax = oft->u1.Function, oft++;
        scasd                 ; ft++;
        test   eax, eax       ; if (oft->u1.Function == 0)
        jz     imp_l0         ; goto imp_l0
        cdq
        inc    edx         ; will be zero if eax >= 0x80000000
        jz     imp_l1      ; oft->u1.Ordinal & IMAGE_ORDINAL_FLAG
        lea    eax, [eax+ebx+2] ; oft->Name_
        call   crc32c           ; get crc of API string
        add    eax, [esp+_edx] ; eax = api_h + dll_h
        cmp    [esp+_ecx], eax ; found match?
        jne    imp_l1
        mov    eax, [edi-4]    ; ft->u1.Function
    imp_l2:
        mov    [esp+_eax], eax
        popad
        ret

**0x09 Process Environment Block**  

也许这个部分应该放在所有的内容之前？

另一个“进步”是在2002年由Ratter /
29A公布的[在NT下从PEB获得重要数据](http://vxheaven.org/29a/29a-6/29a-6.224)的方法。有一个更简单的方法从PEB中获取kernel32.dll的模块基址。

在这里我使用来自[Matt Graeber’s
PIC_Bindshell](https://github.com/mattifestation/PIC_Bindshell)的结构。

    
    
    LPVOID getapi (DWORD dwHash)
    {
      PPEB                     peb;
      PMY_PEB_LDR_DATA         ldr;
      PMY_LDR_DATA_TABLE_ENTRY dte;
      LPVOID                   api_adr=NULL;
      
    #if defined(_WIN64)
      peb = (PPEB) __readgsqword(0x60);
    #else
      peb = (PPEB) __readfsdword(0x30);
    #endif
      ldr = (PMY_PEB_LDR_DATA)peb->Ldr;
      
      // for each DLL loaded
      for (dte=(PMY_LDR_DATA_TABLE_ENTRY)ldr->InLoadOrderModuleList.Flink;
           dte->DllBase != NULL && api_adr == NULL; 
           dte=(PMY_LDR_DATA_TABLE_ENTRY)dte->InLoadOrderLinks.Flink)
      {
        api_adr=search_imp(dte->DllBase, dwHash);
      }
      return api_adr;
    }

下面是相同算法的汇编，做了一些优化。

    
    
    ; LPVOID getapix(DWORD hash);
    getapix:
    _getapix:
        pushad
        mov    ecx, [esp+32+4] ; ecx = hash
        push   30h
        pop    eax
        mov    eax, [fs:eax] ; eax = (PPEB) __readfsdword(0x30);
        mov    eax, [eax+12] ; eax = (PMY_PEB_LDR_DATA)peb->Ldr
        mov    edi, [eax+12] ; edi = ldr->InLoadOrderModuleList.Flink
        jmp    gapi_l1
    gapi_l0:
        call   search_expx
        test   eax, eax
        jnz    gapi_l2
        mov    edi, [edi]    ; edi = dte->InMemoryOrderLinks.Flink
    gapi_l1:
        mov    ebx, [edi+24] ; ebx = dte->DllBase
        test   ebx, ebx
        jnz    gapi_l0
    gapi_l2:
        mov    [esp+_eax], eax
        popad
        ret

**  
**

**0xA hash算法**  

上述所有的例子，我都是用CRC-32C。C代表使用的Castagnoli多项式。用这个的原因是测试的80000个API都不会有冲突。一些其他的hash算法也提供了足够好的结果，但是使用CRC-32C的优势是INTEL处理器发布的SSE4.2的支持。

然而与0x20做或操作不是CRC-32C特有的。在这里仅仅是在哈希前将字符串转为小写。有时kernel32.dll也会出现大写的情况。

    
    
    uint32_t crc32c(const char *s)
    {
      int i;
      uint32_t crc=0;
      
      do {
        crc ^= (uint8_t)(*s++ | 0x20);
        
        for (i=0; i<8; i++) {
          crc = (crc >> 1) ^ (0x82F63B78 * (crc & 1));
        }
      } while (*(s - 1) != 0);
      return crc;
    }

这是使用内置指令的代码。

    
    
    ;
        xor    eax, eax
        cdq
    crc_l0:
        lodsb
        or     al, 0x20
        crc32  edx, al
        cmp    al, 0x20
        jns    crc_l0

下面是CPU不支持SSE4.2的代码。

    
    
    ; in: eax = s
    ; out: crc-32c(s)
    ;
    crc32c:    
        pushad
        xchg   eax, esi          ; esi = s
        xor    eax, eax          ; eax = 0
        cdq                      ; edx = 0
    crc_l0:
        lodsb                    ; al = *s++ | 0x20
        or     al, 0x20
        xor    dl, al            ; crc ^= c
        push   8
        pop    ecx    
    crc_l1:
        shr    edx, 1            ; crc >>= 1
        jnc    crc_l2
        xor    edx, 0x82F63B78
    crc_l2:
        loop   crc_l1
        sub    al, 0x20          ; until al==0
        jnz    crc_l0    
        mov    [esp+_eax], edx
        popad
        ret

当然，CRC-32C不是绝对没冲突的。有时需要考虑使用加密哈希算法。最简单的是有Daniel
Bernstein的[CubeHash](http://cubehash.cr.yp.to/)。

也可以使用一个小块或流密码加密字符串和截断密文为32或64位。解决冲突是值得探索的。

  

**0xB 总结**  

解析导入和导出表不是困难的任务。所有的文档和代码将被提供，就没了不使用PIC技术的解析API的方法。使用硬编码API地址或者通过序号查找是个灾难。

[Getapi.c](https://github.com/odzhan/shellcode/blob/master/win/getapi.c)包含了通过CRC-32C定位API的C代码。[X86.asm](https://github.com/odzhan/shellcode/blob/master/win/x86.asm)和[x64.asm](https://github.com/odzhan/shellcode/blob/master/win/x64.asm)包含了通过CRC-32C定位API的汇编代码。

本文翻译自modexp.wordpress.com
[原文链接](https://modexp.wordpress.com/2017/01/15/shellcode-resolving-api-addresses/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85386](/post/id/85386)

安全客 - 有思想的安全新媒体

本文转载自:
[modexp.wordpress.com](https://modexp.wordpress.com/2017/01/15/shellcode-resolving-api-addresses/)

如若转载,请注明出处： <https://modexp.wordpress.com/2017/01/15/shellcode-resolving-api-addresses/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

