**作者：evilpan  
原文链接：<https://evilpan.com/2020/09/06/macho-inside-out/>**

之前写了一篇[深入浅出ELF](https://evilpan.com/2020/08/09/elf-inside-out/)，作为姊妹篇这次就来聊聊MacOS的可执行文件格式MachO。

# Mach-O 101

在[之前的文章](https://evilpan.com/2020/08/09/elf-inside-out/)中我们说过，可执行文件的使命有两个，一是方便开发者在编译、链接时提供可扩展的封装结构；二是在执行时能给操作系统(内核)提供内存映射信息。MachO也不例外。

MachO本身没有什么特别的含义，就是`Mach
object`的简写，而[Mach](https://en.wikipedia.org/wiki/Mach_kernel)是早期的一个微内核。和ELF一样，MachO也极具拓展性，从全局视角来看，MachO文件可以分为三个部分，分别是:

  1. Mach Header: 文件头信息
  2. 可变长度的LOAD_COMMAND信息
  3. 上述LOAD_COMMAND中所用到的具体信息(segments)

这里的segment可以理解为一段连续的内存空间，拥有对应的读/写/执行权限，并且在内存中总是页对齐的。每个segment由一个或者多个section组成，section表示特定含义数据或者代码的集合(不需要页对齐)。在macOS中，通常约定segment的名称为双下划线加全大写字母(如`__TEXT`)，section的名称为双下划线加小写字母(如`__text`)。

下面对这三个部分进行分别介绍。

> 注: MachO文件结构的表示通常分为32位和64位两种，本文以64位为例，毕竟这是历史的进程。

## Header

文件头信息参考[mach-o/loader.h](https://github.com/apple/darwin-xnu/blob/master/EXTERNAL_HEADERS/mach-o/loader.h)中的定义如下:

    
    
    /* * The 64-bit mach header appears at the very beginning of object files for * 64-bit architectures. */ struct mach_header_64 { uint32_t   magic;      /* mach magic number identifier */ cpu_type_t   cputype;    /* cpu specifier */ cpu_subtype_t   cpusubtype; /* machine specifier */ uint32_t    filetype;   /* type of file */ uint32_t ncmds;      /* number of load commands */ uint32_t  sizeofcmds; /* the size of all the load commands */ uint32_t    flags;      /* flags */ uint32_t    reserved;   /* reserved */ }; /* Constant for the magic field of the mach_header_64 (64-bit architectures) */ #define MH_MAGIC_64 0xfeedfacf /* the 64-bit mach magic number */ #define MH_CIGAM_64 0xcffaedfe /* NXSwapInt(MH_MAGIC_64) */ 

`filetype`表示类型，常见的有:

  * MH_OBJECT: 可重定向的目标文件
  * MH_EXECUTE: 可执行文件
  * MH_DYLIB: 动态绑定的共享库文件
  * …

`flags`为不同的文件标签的组合，每个标签占一个位，可以用位或来进行组合，常见的标签有:

  * MH_NOUNDEFS: 该文件没有未定义的引用
  * MH_DYLDLINK: 该文件将要作为动态链接器的输入，不能再被静态链接器修改
  * MH_TWOLEVEL: 该文件使用两级名字空间绑定
  * MH_PIE: 可执行文件会被加载到随机地址，只对`MH_EXECUTE`有效
  * …

另外一个值得关注的就是`ncmds`和`sizeofcmds`，分别指定了 LOAD_COMMAND 的个数以及总大小，从这里也大概能猜到，每个
command 的大小是可变的。

## Command

`LOAD_COMMAND`是体现MachO文件拓展性的地方，每个 command 的头两个word分别表示类型和大小，如下:

    
    
    struct load_command { uint32_t cmd;     /* type of load command */ uint32_t cmdsize;    /* total size of command in bytes */ }; 

不同的`cmd`类型都会有其对应的结构体来描述其内容，`cmdsize`表示的是整个cmd的大小，即包括头部和内容。也就是说在处理的时候当前cmd的位置加上cmdsize就是下一个cmd的位置。注意每个command的大小(即cmdsize)需要word对齐，对于32位CPU来说是4字节，64位则是8字节；同时对齐末尾的填充部分必须是0。

`loader.h`中绝大部分的篇幅就是用来定义各种不同command类型的结构体了，这里挑选一些比较常见的来进行介绍。

### LC_SEGMENT

`LC_SEGMENT`/`LC_SEGMENT64`可以说是最重要的一个command。表示当前文件的一部分将会映射到目标进程(task)的地址空间中，包括程序运行所需要的所有代码和数据。假设当前MachO文件的起始地址为begin，则映射的内容为:

  * 原始地址(文件地址): _begin + fileoff_ ，大小为 _filesize_
  * 目的地址(进程虚址): _vmaddr_ ，大小为 _vmsize_

其中`vmsize >= filesize`，如果有多出来的部分需要填充为零。segment_command的结构体表示如下:

    
    
    struct segment_command_64 { /* for 64-bit architectures */ uint32_t cmd;        /* LC_SEGMENT_64 */ uint32_t    cmdsize;    /* includes sizeof section_64 structs */ char       segname[16];    /* segment name */ uint64_t vmaddr;     /* memory address of this segment */ uint64_t   vmsize;     /* memory size of this segment */ uint64_t  fileoff;    /* file offset of this segment */ uint64_t  filesize;   /* amount to map from the file */ vm_prot_t maxprot;    /* maximum VM protection */ vm_prot_t   initprot;   /* initial VM protection */ uint32_t    nsects;     /* number of sections in segment */ uint32_t    flags;      /* flags */ }; 

maxprot/initprot表示对应segment虚拟地址空间的RWX权限。如果segment包含一个或者多个section，那么在该segment结构体之后就紧跟着对应各个section头，总大小也包括在cmdsize之中，其结构如下:

    
    
    struct section_64 { /* for 64-bit architectures */ char     sectname[16];   /* name of this section */ char     segname[16];    /* segment this section goes in */ uint64_t addr;       /* memory address of this section */ uint64_t   size;       /* size in bytes of this section */ uint32_t    offset;     /* file offset of this section */ uint32_t  align;      /* section alignment (power of 2) */ uint32_t   reloff;     /* file offset of relocation entries */ uint32_t    nreloc;     /* number of relocation entries */ uint32_t flags;      /* flags (section type and attributes)*/ uint32_t   reserved1;  /* reserved (for offset or index) */ uint32_t   reserved2;  /* reserved (for count or sizeof) */ uint32_t   reserved3;  /* reserved */ }; 

每个section头对应一个section，位置在 **相对文件起始地址** 的 _offset_ 处，大小为 _size_ 字节，对应的虚拟地址为
_addr_ 。这里的 _align_
对齐指的是在虚拟地址空间中的对齐，实际上在文件中是连续存放的，因为有size指定大小。reloff和nreloc与符号的重定向有关，在下面的加载过程一节中再进行介绍。

从这里可以看出，section的内容和segment是不连续存放的，只是section header在对应segment之后。而segment的
_vmsize_
实际上会大于segment+section_header的大小(即cmdsize)，猜测多出来的空间是内核加载MachO时将对应section内容填充进去，后面将会对这一猜测进行验证。

#### TEXT

`__TEXT`段包含`__text`、`__stubs`、`__stub_helper`、`__cstring`等section，一般用来存放不可修改的数据，比如代码和const字符串，可以用`otool`查看对应的section内容:

    
    
    $ otool -V main -s __TEXT __stubs main: Contents of (__TEXT,__stubs) section 0000000100000f6a   jmpq    *0xa8(%rip) ## literal pool symbol address: _printf 0000000100000f70    jmpq    *0xaa(%rip) ## literal pool symbol address: _set_foo 

在实际的MachO可执行文件中观察发现TEXT的fileoff为0，也就是说TEXT段映射的时候会将当前文件头部分也映射到进程空间中。

    
    
    (lldbinit) image dump sections main Sections for '/Users/evilpan/temp/macho-test/main' (x86_64):  SectID     Type             Load Address                             Perm File Off.  File Size  Flags      Section Name  ---------- ---------------- ---------------------------------------  ---- ---------- ---------- ---------- ----------------------------  0x00000100 container        [0x0000000000000000-0x0000000100000000)* ---  0x00000000 0x00000000 0x00000000 main.__PAGEZERO  0x00000200 container        [0x0000000100000000-0x0000000100001000)  r-x  0x00000000 0x00001000 0x00000000 main.__TEXT  0x00000001 code             [0x0000000100000ee0-0x0000000100000f6a)  r-x  0x00000ee0 0x0000008a 0x80000400 main.__TEXT.__text  0x00000002 code             [0x0000000100000f6a-0x0000000100000f76)  r-x  0x00000f6a 0x0000000c 0x80000408 main.__TEXT.__stubs  0x00000003 code             [0x0000000100000f78-0x0000000100000f9c)  r-x  0x00000f78 0x00000024 0x80000400 main.__TEXT.__stub_helper  0x00000004 data-cstr        [0x0000000100000f9c-0x0000000100000fb0)  r-x  0x00000f9c 0x00000014 0x00000002 main.__TEXT.__cstring  0x00000005 compact-unwind   [0x0000000100000fb0-0x0000000100000ff8)  r-x  0x00000fb0 0x00000048 0x00000000 main.__TEXT.__unwind_info  0x00000300 container        [0x0000000100001000-0x0000000100002000)  rw-  0x00001000 0x00001000 0x00000000 main.__DATA  0x00000006 data-ptrs        [0x0000000100001000-0x0000000100001008)  rw-  0x00001000 0x00000008 0x00000006 main.__DATA.__nl_symbol_ptr  0x00000007 data-ptrs        [0x0000000100001008-0x0000000100001018)  rw-  0x00001008 0x00000010 0x00000006 main.__DATA.__got  0x00000008 data-ptrs        [0x0000000100001018-0x0000000100001028)  rw-  0x00001018 0x00000010 0x00000007 main.__DATA.__la_symbol_ptr  0x00000009 zero-fill        [0x0000000100001028-0x000000010000102c)  rw-  0x00000000 0x00000000 0x00000001 main.__DATA.__common  0x00000400 container        [0x0000000100002000-0x0000000100007000)  r--  0x00002000 0x00004a90 0x00000000 main.__LINKEDIT 

上面例子中`__TEXT`段的的vm_size和file_size都是`0x1000`，这个大小在文件中正好是第一个`__DATA`section的起始地址:

![](https://images.seebug.org/content/images/2020/10/b946dc7c-6e3f-4dd0-96ef-f0d939701b31.png-w331s)

`__PAGEZERO`是一个特殊的段，主要目的是将低地址占用，防止用户空间访问。个人理解这是对空指针引用类型漏洞的一种缓解措施，Linux内核中也有[mmap_min_addr](https://wiki.debian.org/mmap_min_addr)来限制用户可以mmap映射的最低地址。

#### DATA

`__DATA`段则包含`__got`、`__nl_symbol_ptr`、`__la_symbol_ptr`等section，一般包括可读写的内容。

#### LINKEDIT

另外一个重要的段为`__LINKEDIT`，其中包含需要被动态链接器使用的信息，包括符号表、字符串表、重定位项表、签名等。该段和`PAGEZERO`一样的是末尾没有额外的section信息，所以cmdsize都等于72(`sizeof(struct
segment_command_64)`)。其内容即`begin + fileoff`指向的地方保存linkedit
command的内容，这个内容的格式根据具体cmd的不同而不同。LINKEDIT可以理解为元数据，值得一提的是，经过观察，`fileoff
+filesize`即为MachO文件末尾，也就是等于文件的大小。

那么LINKEDIT块中的内容是什么格式呢？其实大部分有其专门的格式，比如对`Dynamic Loader
Info`来说是字节码，对于符号表来说是符号表结构体，对于函数地址项来说是`uleb128`编码的地址值，……因此LINKEDIT可谓包罗万象，需要具体问题具体分析，下面介绍的几个command就是其中几个例子。

### LC_CODE_SIGNATURE

Signature Command指定当前文件的签名信息，没有单独的结构体，而是使用下面这个结构来表示:

    
    
    struct linkedit_data_command {    uint32_t  cmd;        /* LC_CODE_SIGNATURE, LC_SEGMENT_SPLIT_INFO,                                   LC_FUNCTION_STARTS, LC_DATA_IN_CODE,                LC_DYLIB_CODE_SIGN_DRS or               LC_LINKER_OPTIMIZATION_HINT. */    uint32_t  cmdsize;    /* sizeof(struct linkedit_data_command) */    uint32_t  dataoff;    /* file offset of data in __LINKEDIT segment */    uint32_t datasize;   /* file size of data in __LINKEDIT segment  */ }; 

cmd/cmdsize和前面LC_SEGMENT的含义类似，只不过cmdsize是个常数，等于当前结构体的大小。 _dataoff_
表示前面信息在LINKEDIT数据中的偏移，注意这里不是相对文件头的偏移； _datasize_ 则表示签名信息的大小。

苹果的签名数据格式并不是常规类型，对其详细介绍超过了本文的范围，对于具体的签名实现有兴趣的可以参考Jonathan大神的`*OS
Internal`或者[Code Signing – Hashed
Out](http://www.newosxbook.com/articles/CodeSigning.pdf)。使用jtool工具可以打印出详细的签名信息，如下所示:

    
    
    $ jtool2 --sig -v main An embedded signature of 1953 bytes, with 3 blobs: Blob 0: Type: 0 @36: Code Directory (213 bytes)   Version:     20100  Flags:       none   CodeLimit:   0x22c0     Identifier:  main (@0x30)   CDHash:      f3d8c9a75487ecc6f3adbddca11ad987a171e8974e6df15e857d2ac962e4b886 (computed)    # of hashes: 3 code (4K pages) + 2 special  Hashes @117 size: 32 Type: SHA-256 Blob 1: Type: 2 @249: Requirement Set (80 bytes) with 1 requirement: Unknown opcode 14 - has Apple changed the op codes?Please notify J!     0: Designated Requirement (@20, 48 bytes): Ident(main) AND Blob 2: Type: 10000 @329: Blob Wrapper (1624 bytes) (0x10000 is CMS (RFC3852) signature)     Timestamp: 00:12:38 2020/09/06 

当然官方的`codesign -d`也可以。

### LC_DYLD_INFO_ONLY

这个Command的信息主要是提供给动态链接器`dyld`的，其结构如下:

    
    
    struct dyld_info_command {   uint32_t   cmd;        /* LC_DYLD_INFO or LC_DYLD_INFO_ONLY */   uint32_t   cmdsize;       /* sizeof(struct dyld_info_command) */   uint32_t   rebase_off; /* file offset to rebase info  */   uint32_t   rebase_size; /* size of rebase info   */   uint32_t   bind_off;  /* file offset to binding info   */   uint32_t   bind_size; /* size of binding info  */  uint32_t   weak_bind_off;  /* file offset to weak binding info   */   uint32_t   weak_bind_size;  /* size of weak binding info  */   uint32_t   lazy_bind_off; /* file offset to lazy binding info */   uint32_t   lazy_bind_size;  /* size of lazy binding infs */   uint32_t   export_off;   /* file offset to lazy binding info */   uint32_t   export_size;    /* size of lazy binding infs */ } 

虽然看起来很复杂，但实际上它的目的就是为了给dyld提供能够加载目标MachO所需要的必要信息:
因为可能加载到随机地址，所以需要rebase信息；如果进程依赖其他镜像的符号，则绑定需要bind信息；对于C++程序而言可能需要weak
bind实现代码/数据复用；对于一些外部符号不需要立即绑定的可以延时加载，这就需要lazy bind信息；对于导出符号也需要对应的export信息。

为了描述这些rebase/bind信息，dyld定义了一套伪指令，用来描述具体的操作(opcode)及其操作数据。以延时绑定为例，操作符看起来是这样:

![](https://images.seebug.org/content/images/2020/10/e13f3c91-992c-4851-8dd8-8be98fb5170e.png-w331s)

其表达的实际含义用中文来描述就是:

  1. `_printf`符号(来自`libSystem.B.dylib`)延时绑定到`0x1018`偏移地址；
  2. `_set_foo`符号(来自`libfoo.dylib`)延时绑定到`0x1020`偏移地址；

其中0x1018/0x1020地址在`__DATA`段，更准确来说是在`__la_symbol_ptr`这个section中，可以自行编译验证。

### LC_XXX_DYLIB

`LC_LOAD_{,WEAK_}DYLIB`用来告诉内核(实际上是dyld)当前可执行文件需要使用哪些动态库，而其结构如下:

    
    
    struct dylib {    union lc_str  name;           /* library's path name */    uint32_t timestamp;            /* library's build time stamp */    uint32_t current_version;       /* library's current version number */    uint32_t compatibility_version;   /* library's compatibility vers number*/ }; struct dylib_command { uint32_t cmd;        /* LC_ID_DYLIB, LC_LOAD_{,WEAK_}DYLIB, LC_REEXPORT_DYLIB */ uint32_t    cmdsize;    /* includes pathname string */ struct dylib dylib;      /* the library identification */ }; 

动态库(filetype为`MH_DYLIB`)中会包含 `LC_ID_DYLIB` command
来说明自己是个什么库，包括名称、版本、时间戳等信息。需要注意的是`lc_str`并不是字符串本身，而是字符串的偏移值，字符串信息在command的内容之后，该偏移指的是距离
**command起始位置** 的偏移。

> `LC_REEXPORT_DYLIB`表示加载并重新导出dylib

### 其他

除了上面的介绍，还有许多其他类型的 command
，比如`LC_FUNCTION_STARTS`表示函数入口地址，`LC_MAIN`表示主函数地址，`LC_ENCRYPTION_INFO`表示加密的segment段等等，可以在遇到的时候用查看`loader.h`的定义，这里就不再赘述了。

# 加载过程

MachO的加载和ELF的加载过程没有太大区别，还是`系统调用->内核处理->返回执行`的一般流程，对于静态链接程序返回执行是直接返回到程序入口地址，而动态链接程序则需要在程序开始执行之前进行重定向，因此这里也按照这个顺序介绍。

## 内核空间

内核空间的主要任务是创建新taks并初始化内存页和对应的权限，我们主要关注MachO文件的处理部分，即`parse_machfile`函数，文件为[bsd/kern/mach_loader.c][src]，其主要功能为检查header以及cmdsize等长度符合预期，然后通过4次循环来处理不同的信息，如下:

    
    
        /*  *  Scan through the commands, processing each one as necessary.  *  We parse in three passes through the headers:  *  0: determine if TEXT and DATA boundary can be page-aligned  *  1: thread state, uuid, code signature  *  2: segments  *  3: dyld, encryption, check entry point  */ 

这里重点关注pass2，关键代码如下:

其中很多command比如`LC_LOAD_DYLIB`、`LC_DYLD_INFO_ONLY`等不在内核态中进行处理，直接进入default分支忽略。

### load_segment

这个函数主要负责加载segment到内存中，实现有几个值得一提的点:

  * total_section_size = lcp->cmdsize - sizeof(struct segment_command_64)；这是文件后面section的大小
  * LC_SEGMENT_32会转换为LC_SEGMENT_64，使用widen_segment_command
  * 映射的内存地址是`slide + scp->vmaddr`，slide为随机化的地址偏移(如果有的话)，映射的内存大小是`scp->vmsize`
  * 文件中对应内容起始位置是`scp->fileoff`，大小为`scp->filesize`
  * file_offset = pager_offset + scp->fileoff，是该segment在内核空间中的地址，需要页对齐
  * 对于0地址页的映射，由于用户空间不能访问，因此直接增加了vm能访问的最低地址值(vm_map_raise_min_offset)，仅允许对`PAGEZERO`段执行0地址的映射命令

对于映射的地址和大小，都需要是4k页对齐的，并且最终使用`map_segment`进行映射:

    
    
    file_start = vm_map_trunc_page(file_offset, effective_page_mask); file_end = vm_map_round_page(file_offset + file_size, effective_page_mask); vm_start = vm_map_trunc_page(vm_offset, effective_page_mask); vm_end = vm_map_round_page(vm_offset + vm_size, effective_page_mask); ret = map_segment(map, vm_start, vm_end, control, file_start, file_end,                  initprot, maxprot, result); 

根据对代码的分析，内核中并不关心具体section的内容，即不解析单个section头的具体字段，而是以segment为单位进行映射。一般而言映射的是具体内容的值，比如`__DATA`段就映射了数据段。前面也说过`__TEXT`段比较特别，它是从文件开头开始映射的，一直到代码段的末尾(数据段的开头)。

### load_code_signature

MachO和ELF的一个最大不同点，或者说XNU和Linux的不同点是前者原生支持了对可执行文件的签名认证，文件的签名信息保存在LINKEDIT数据段，在前面我们已经介绍过了`LC_CODE_SIGNATURE`的内容。

### load_dylinker

`load_main`函数主要用来处理`LC_MAIN`命令，这里面包括了可执行文件的入口地址以及栈大小信息。但是在内核中并不需要关心main函数信息，而只需要关心入口信息(entry_point)。因此在load_main中只对栈和线程进行初始化，并且修改对应的result信息:

    
    
        result->user_stack = addr; result->user_stack -= slide;     result->needs_dynlinker = TRUE; result->using_lcmain = TRUE;    ret = thread_state_initialize( thread ); 

此时`result->entry_point`还是0(MACH_VM_MIN_ADDRESS)。

>
> 另外一个能决定入口地址的command是`LC_UNIXTHREAD`，类似于UNIX中直接将`start`符号导出，该符号应该是在`crt1.o`里的，但苹果并不默认提供。也就是说如果想要静态编译，需要自己下载源文件自己去编译，或者自己链接并导出这个符号。苹果不支持静态编译的原因是出于兼容性的考虑。

在load_main结束后，需要加载动态链接器:

    
    
            /* Make sure if we need dyld, we got it */  if (result->needs_dynlinker && !dlp) {      ret = LOAD_FAILURE;     }       if ((ret == LOAD_SUCCESS) && (dlp != 0)) {      /*       * load the dylinker, and slide it by the independent DYLD ASLR          * offset regardless of the PIE-ness of the main binary.         */         ret = load_dylinker(dlp, dlarchbits, map, thread, depth,                    dyld_aslr_offset, result, imgp);    } 

动态链接器就是`dyld`，在`LC_LOAD_DYLINKER`命令中指定，通常是`/usr/lib/dyld`。load_dylinker内部也同样调用了`parse_machfile`函数，因此大部分操作是类似的。注意到这里其实涉及到了递归调用，因此需要在该函数中加depth参数表示递归层数。

dyld文件中有`LC_UNIXTHREAD`命令，因此其`result->entry_point`将被设置，在原先的parse_mach返回到load_machfile后，则初始化新的内核task并将执行流交还给用户空间，对于大部分程序而言，就是跳转到dyld的起始地址执行。

## 用户空间

从内核回到用户空间，便跳转到目标的入口地址开始执行。对于静态链接链接程序，实际上执行的是dyld中的指令，该程序的源码可以参考[opensource-apple/dyld](https://github.com/opensource-apple/dyld)。

dyld的起始地址固定为`0x1000`，这个地址对应的符号是`__dyld_start`，文件定义在`src/dyldStartup.s`。这部分代码和`crt0.o`中的代码是一样的，主要是用来初始化C
Runtime，唯一的不同点是有个额外的参数用来指定MachO文件头的地址。

初始化完成后调用`call
__ZN13dyldbootstrap5startEPK12macho_headeriPPKclS2_Pm`，demangle之后为下面的函数:

    
    
    // //  This is code to bootstrap dyld.  This work in normally done for a program by dyld and crt. //  In dyld we have to do this manually. // uintptr_t start(const struct macho_header* appsMachHeader, int argc, const char* argv[],              intptr_t slide, const struct macho_header* dyldsMachHeader,             uintptr_t* startGlue) {     // if kernel had to slide dyld, we need to fix up load sensitive locations // we have to do this before using any global variables if ( slide != 0 ) {  rebaseDyld(dyldsMachHeader, slide); }   // allow dyld to use mach messaging mach_init();    // kernel sets up env pointer to be just past end of agv array const char** envp = &argv[argc+1];  // kernel sets up apple pointer to be just past end of envp array const char** apple = envp; while(*apple != NULL) { ++apple; } ++apple;     // set up random value for stack canary __guard_setup(apple); #if DYLD_INITIALIZER_SUPPORT // run all C++ initializers inside dyld runDyldInitializers(dyldsMachHeader, slide, argc, argv, envp, apple); #endif     // now that we are done bootstrapping dyld, call dyld's main uintptr_t appsSlide = slideOfMainExecutable(appsMachHeader); return dyld::_main(appsMachHeader, appsSlide, argc, argv, envp, apple, startGlue); } 

所以dyld真正的入口地址是`dyld::_main`，该函数的功能主要有:

  1. 初始化上下文(setContext)
  2. 将可执行文件的路径转为绝对路径
  3. 处理环境变量
  4. 判断是否需要加载共享缓存库，如果需要加载则直接映射到内存中(mapSharedCache)
  5. 加载注入的动态库(sEnv.DYLD_INSERT_LIBRARIES)
  6. 链接主程序(dyld::link)，实际上用的是虚函数`ImageLoader::link`
  7. initializeMainExecutable: 运行初始化函数(`__mod_init_funcs`)
  8. 执行最终的目标程序(LC_MAIN/LC_UNIXTHREAD)

最终目标程序正常执行，就像自己直接启动一样。下面挑几个比较关键的点进行深入分析。

### linking

链接是dyld的主要功能，执行实际动态链接功能的是link函数，除了链接待执行的目标程序，还链接所有插入的其他动态库:

    
    
            // link main executable     gLinkContext.linkingMainExecutable = true;  link(sMainExecutable, sEnv.DYLD_BIND_AT_LAUNCH, true, ImageLoader::RPathChain(NULL, NULL));     // link any inserted libraries  // do this after linking main executable so that any dylibs pulled in by inserted   // dylibs (e.g. libSystem) will not be in front of dylibs the program uses  if ( sInsertedDylibCount > 0 ) {        for(unsigned int i=0; i < sInsertedDylibCount; ++i) {           ImageLoader* image = sAllImages[i+1];           link(image, sEnv.DYLD_BIND_AT_LAUNCH, true, ImageLoader::RPathChain(NULL, NULL));           image->setNeverUnloadRecursive();       }       // only INSERTED libraries can interpose        // register interposing info after all inserted libraries are bound so chaining works       for(unsigned int i=0; i < sInsertedDylibCount; ++i) {           ImageLoader* image = sAllImages[i+1];           image->registerInterposing();       }   } 

而`dyld:link`使用的是具体ImageLoader的link多态实现:

    
    
    void link(ImageLoader* image, bool forceLazysBound, bool neverUnload, const ImageLoader::RPathChain& loaderRPaths) { // add to list of known images.  This did not happen at creation time for bundles if ( image->isBundle() && !image->isLinked() )   addImage(image);    // we detect root images as those not linked in yet  if ( !image->isLinked() )  addRootImage(image);  // process images try {   image->link(gLinkContext, forceLazysBound, false, neverUnload, loaderRPaths); } catch (const char* msg) {   garbageCollectImages();     throw; } } 

sMainExecutable的实现在开源代码中并没有给出，不过参考基类的默认实现如下:

    
    
    void ImageLoader::link(const LinkContext& context, bool forceLazysBound, bool preflightOnly, bool neverUnload, const RPathChain& loaderRPaths) { //dyld::log("ImageLoader::link(%s) refCount=%d, neverUnload=%d\n", this->getPath(), fDlopenReferenceCount, fNeverUnload);  // clear error strings (*context.setErrorStrings)(dyld_error_kind_none, NULL, NULL, NULL);  uint64_t t0 = mach_absolute_time(); this->recursiveLoadLibraries(context, preflightOnly, loaderRPaths); context.notifyBatch(dyld_image_state_dependents_mapped);  // we only do the loading step for preflights if ( preflightOnly )    return;      uint64_t t1 = mach_absolute_time(); context.clearAllDepths(); this->recursiveUpdateDepth(context.imageCount());    uint64_t t2 = mach_absolute_time();     this->recursiveRebase(context); context.notifyBatch(dyld_image_state_rebased);  uint64_t t3 = mach_absolute_time();     this->recursiveBind(context, forceLazysBound, neverUnload);     uint64_t t4 = mach_absolute_time(); if ( !context.linkingMainExecutable )   this->weakBind(context); uint64_t t5 = mach_absolute_time();        context.notifyBatch(dyld_image_state_bound); uint64_t t6 = mach_absolute_time();        std::vector<DOFInfo> dofs; this->recursiveGetDOFSections(context, dofs); context.registerDOFs(dofs); uint64_t t7 = mach_absolute_time();        // interpose any dynamically loaded images if ( !context.linkingMainExecutable && (fgInterposingTuples.size() != 0) ) {     this->recursiveApplyInterposing(context); }  // clear error strings  // ... } 

主要做的就是这几步:

  1. recursiveLoadLibraries
  2. recursiveUpdateDepth
  3. recursiveRebase
  4. recursiveBind
  5. weakBind
  6. recursiveGetDOFSections

根据名字不难看出其作用，其中大部分函数名称带recursive，这是因为动态库本身也可能会依赖其他的动态库，因此需要递归进行处理(当然循环依赖会有对应的处理)。其中`recursiveUpdateDepth`不太直观，其实作用只是为了对镜像进行排序，被依赖的库会出现在依赖者之前。

### dyld_cache

在上面第4步中说到要加载共享缓存库，这是个什么东西呢？这一步的目的其实是为了加速动态库的加载过程。对于我们自己编译的macOS命令行程序可能还好，但是对于图形界面应用来说，每个应用启动时需要加载的动态库可能有上百个，而其中很大一部分是系统库，比如UIKit、Foundation等。因此苹果就事先把这些常用的库打包成缓存，程序启动时候直接映射到内存中，而无需逐个执行繁琐的处理和解析。

映射共享缓存库的函数为`mapSharedCache`，首先检查共享缓存库是否已经映射过:

    
    
    static int __attribute__((noinline)) _shared_region_check_np(uint64_t* start_address) { if ( gLinkContext.sharedRegionMode == ImageLoader::kUseSharedRegion )   return syscall(294, start_address); return -1; } 

294号系统调用定义在内核中(bsd/kern/syscalls.master):

    
    
    294 AUE_NULL    ALL { int shared_region_check_np(uint64_t *start_address) NO_SYSCALL_STUB; } 295    AUE_NULL    ALL { int shared_region_map_np(int fd, uint32_t count, const struct shared_file_mapping_np *mappings) NO_SYSCALL_STUB; } 

内核中的实现也比较简单，忽略错误检查，关键的代码如下:

    
    
    int shared_region_check_np( __unused struct proc            *p, struct shared_region_check_np_args  *uap, __unused int              *retvalp) {  // ...  shared_region = vm_shared_region_get(current_task()); if (shared_region != NULL) {         /* retrieve address of its first mapping... */  kr = vm_shared_region_start_address(shared_region,                      &start_address);            /* ... and give it to the caller */     error = copyout(&start_address,                 (user_addr_t) uap->start_address,               sizeof (start_address));    // ...  vm_shared_region_deallocate(shared_region);  } } 

其内部实现姑且不管，继续回到用户空间，所返回的地址可以强制转换为`dyld_cache_header`格式:

    
    
    struct dyld_cache_header { char     magic[16];              // e.g. "dyld_v0    i386" uint32_t  mappingOffset;          // file offset to first dyld_cache_mapping_info uint32_t    mappingCount;           // number of dyld_cache_mapping_info entries uint32_t   imagesOffset;           // file offset to first dyld_cache_image_info uint32_t  imagesCount;            // number of dyld_cache_image_info entries uint64_t dyldBaseAddress;        // base address of dyld when cache was built uint64_t   codeSignatureOffset;    // file offset of code signature blob uint64_t  codeSignatureSize;      // size of code signature blob (zero means to end of file) uint64_t slideInfoOffset;        // file offset of kernel slid info uint64_t slideInfoSize;          // size of kernel slid info uint64_t    localSymbolsOffset;     // file offset of where local symbols are stored uint64_t   localSymbolsSize;       // size of local symbols information uint8_t        uuid[16];               // unique value for each shared cache file uint64_t cacheType;              // 1 for development, 0 for optimized }; 

检查共享缓存空间存在则直接复制其UUID到进程的`sharedCacheUUID`中，然后直接使用该缓存。

如果不存在，就需要进行创建，创建的过程如下:

  1. 如果是x86环境，需要判断当前是否为安全启动模式，则会删除之前余留的cache文件，路径为`/var/db/dyld/dyld_shared_cache_$arch`
  2. 打开sharedCache文件，对于IPhone路径为`/System/Library/Caches/com.apple.dyld/dyld_shared_cache_$arch`
  3. 读取文件的前8192字节转换为`struct dyld_cache_header`，并做一些合法性检查
  4. 处理cache文件，主要是将mapping信息提取出来，保存为一个数组`mappings[]`
  5. 调用`_shared_region_map_and_slide_np`映射每个mapping

mapping信息如下:

    
    
    struct dyld_cache_mapping_info { uint64_t   address; uint64_t   size; uint64_t  fileOffset; uint32_t    maxProt; uint32_t   initProt; }; 

和之前提到的segment信息类似，没有feilsize，因为不存在padding。

`_shared_region_map_and_slide_np`函数分别处理每个mapping，并最终使用`mmap`来完成cache到内存的映射操作。

> 每个mapping info对应一个`struct
> shared_file_mapping_np`，但是这个结构体的定义在开源代码中没找到，并且在苹果文档中也进行了隐藏，见:
> <https://developer.apple.com/documentation/kernel/shared_file_mapping_np>

# 后记

本文通过对MachO文件的文件格式研究，介绍了MacOS和iOS中可执行文件的加载过程，从内核中的处理一直到动态连接器dyld的代码分析。可以看出MachO与ELF相比实现方式各有千秋，但是在内核中原生增加了对代码的签名和加密，其实ELF也很容易实现类似的功能，但开放系统需要更多考虑兼容性的问题，不像苹果可以大刀阔斧的随便改。

对于MachO的深入理解其实也有助于日常的相关研究，比如Apple
Store的加密实现以及代码签名的大致原理，还有针对dyld_cache的处理等，其中每一项都值得去深入挖掘。而且本文也没有介绍到全部的MachO特性，比如Objective-C相关的段，具体的实战部分后面有时间会再去整理一下。

# 参考资料

  * [Overview of the Mach-O Executable Format](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/CodeFootprint/Articles/MachOOverview.html)
  * [Mach Object Files](http://www.cilinder.be/docs/next/NeXTStep/3.3/nd/DevTools/14_MachO/MachO.htmld/index.html)
  * [apple/darwin-xnu](https://github.com/apple/darwin-xnu)
  * [opensource-apple/dyld](https://github.com/opensource-apple/dyld)
  * RTFSC

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1363/>

