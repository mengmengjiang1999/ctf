本文是笔者近期整理编写[IOT 固件安全 All in One](https://wokough.gitbook.io/iot-firmware-aio/)【1】时对二进制静态辅助工具的分析整理，文档 **V0.1** 版本已在 **GitBook** 完成，后期不定时更新。

## 一、预备知识

### 1.1 污点分析

 **污点分析**
是一种跟踪并分析污点信息在程序中流动的技术。在漏洞分析中，使用污点分析技术将所感兴趣的数据（通常来自程序的外部输入）标记为污点数据，然后通过跟踪和污点数据相关的信息的流向，可以知道它们是否会影响某些关键的程序操作，进而挖掘程序漏洞。即将程序是否存在某种漏洞的问题转化为污点信息是否会被
Sink 点上的操作所使用的问题。

使用污点分析检测程序漏洞的工作原理如下图所示：

![](https://image.3001.net/images/20220715/1657858563_62d0ea03c569ac7b1df78.png!small)

### 1.2 符号执行

 **符号执行** 起初应用于基于源代码的安全检测中，它通过符号表达式来模拟程序的执行，将程序的输出表示成包含这些符号的逻辑或数学表达式，从而进行语义分析。

程序中变量的取值可以被表示为符号值和常量组成的计算表达式，而一些程序漏洞可以表现为某些相关变量的取值不满足相应的约束，这时通过判断表示变量取值的表达式是否可以满足相应的约束，就可以判断程序是否存在相应的漏洞。

使用符号执行检测程序漏洞的原理如下图所示：

![https://image.3001.net/images/20220714/1657800725_62d00815c9de9787587ca.png!small](https://image.3001.net/images/20220714/1657800725_62d00815c9de9787587ca.png!small)

### 1.3 环境准备

本文选用某厂商路由器的`upnpd`二进制文作为实例，笔者在很久以前的一篇[文章](../vuls/228293.html)中对`upnpd(CVE-2020-9373)`挖掘利用作过分析，之后不同型号相继爆出类似问题。

  * 固件结构

在上述文章中笔者对结构作过分析，这里不赘述，结构如下图：

![](https://image.3001.net/images/20220715/1657858592_62d0ea206c5cfa3aea330.png!small)解包之分接单，直接通过`binwalk`提取，CPU架构为`ARMv5`，文件系统是`Squashfs`。

    
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    58            0x3A            TRX firmware header, little endian, image size: 32653312 bytes, CRC32: 0x5CEAB739, flags: 0x0, version: 1, header size: 28 bytes, loader offset: 0x1C, linux kernel offset: 0x21AB50, rootfs offset: 0x0
    86            0x56            LZMA compressed data, properties: 0x5D, dictionary size: 65536 bytes, uncompressed size: 5470272 bytes
    2206602       0x21AB8A        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 30443160 bytes, 1650 inodes, blocksize: 131072 bytes, created: 2018-12-13 04:36:38
    

  * 漏洞简介

漏洞成因是`upnpd`服务中解析 SSDP 协议数据包的代码存在缺陷，导致未经授权的远程攻击者可以发送特制的数据包使得栈溢出，进一步实现`RCE`。

漏洞原理很简单， `strcpy()`拷贝导致的缓冲区溢出，在 `sub_1D020()`中使用 `recvfrom()`从接受最大长度 `0x1fff`的
UDP 报文数据。

![](https://image.3001.net/images/20220715/1657858622_62d0ea3e5bbeb06e247e9.png!small)在
`sub_25E04()`中调用 `strcpy()`将以上数据拷贝到大小为 `0x634 - 0x58 = 0x5dc`的
buffer。![](https://image.3001.net/images/20220715/1657858647_62d0ea576ce51faaa96b8.png!small)

下文工具测试结果中就要重点关注`sub_25E04`调用`strcpy()`是否出现。

### 1.4 工具简介

>  **[BinAbsInspector](https://github.com/KeenSecurityLab/BinAbsInspector)**

BinAbsInspector是Keenlab开发的用于自动化逆向工程和扫描二进制文件漏洞的静态分析器，其基于 Ghidra 的 Pcode
而不是汇编，目前支持 x86、x64、armv7 和 aarch64
上的二进制文件。![](https://image.3001.net/images/20220715/1657858670_62d0ea6ea214dc853eea4.png!small)

到目前为止 BinAbsInspector 支持以下漏洞检测：

  * [CWE78](https://cwe.mitre.org/data/definitions/78.html)(OS Command Injection)

  * [CWE119](https://cwe.mitre.org/data/definitions/119.html)(Buffer Overflow (generic case))

  * [CWE125](https://cwe.mitre.org/data/definitions/125.html)(Buffer Overflow (Out-of-bounds Read))

  * [CWE134](https://cwe.mitre.org/data/definitions/134.html)(Use of Externally-Controlled Format string)

  * [CWE190](https://cwe.mitre.org/data/definitions/190.html)(Integer overflow or wraparound)

  * [CWE367](https://cwe.mitre.org/data/definitions/367.html)(Time-of-check Time-of-use (TOCTOU))

  * [CWE415](https://cwe.mitre.org/data/definitions/415.html)(Double free)

  * [CWE416](https://cwe.mitre.org/data/definitions/416.html)(Use After Free)

  * [CWE426](https://cwe.mitre.org/data/definitions/426.html)(Untrusted Search Path)

  * [CWE467](https://cwe.mitre.org/data/definitions/467.html)(Use of sizeof() on a pointer type)

  * [CWE476](https://cwe.mitre.org/data/definitions/476.htmll)(NULL Pointer Dereference)

  * [CWE676](https://cwe.mitre.org/data/definitions/676.html)(Use of Potentially Dangerous Function)

  * [CWE787](https://cwe.mitre.org/data/definitions/787.html)(Buffer Overflow (Out-of-bounds Write))

>  **[SaTC](https://github.com/NSSL-SJTU/SaTC)**

SaTC是上海交大研究人员提出的IoT漏洞自动化挖掘方法，相应的学术论文已在 USENIX Security 2021【2】发表。

与BinAbsInspector通用性不同，SaTC则是专注IOT漏洞挖掘。现有嵌入式系统中的许多漏洞都位于web服务中，寻找这些漏洞的关键是如何定位后端程序中用于处理与用户输入数据相关的代码，而Web前端文件（html、js、xml等）中存在的一些关键字符串通常与后端二进制文件之间共享，也就是说承载用户输入数据的某个参数名称在前端文件与后端文件中都会存在。基于此，SaTC将解压后的固件目录作为输入，然后全程自动完成提取关键字符串、定位后端程序中关键字符串的引用位置、以引用点为起始位置进行污点分析，最终输出了所有可能存在漏洞的指令位置，同时还给出了从输入点到漏洞指令位置的函数调用链条。![](https://image.3001.net/images/20220715/1657858690_62d0ea8245f2923f05cb2.png!small)

>  **[Rhabdomancer](https://github.com/0xdea/ghidra-> scripts/blob/main/Rhabdomancer.java)**

Rhabdomancer是一个简单的Ghidra脚本，它将对 **可能不安全的API函数的所有调用**
定位在二进制文件中。研究人员可以从这些候选点回溯，以找到二进制文件脆弱性。![](https://image.3001.net/images/20220715/1657858708_62d0ea94be60393504e1c.png!small)

  *  **Haruspex + semgrep**

  * [Haruspex](https://github.com/0xdea/ghidra-scripts/blob/main/Haruspex.java)是另一个 Ghidra 脚本，它能够以适合导入到 IDE（如 [VS Code](https://code.visualstudio.com/)）或静态分析工具（如 [Semgrep](https://semgrep.dev/)）解析的格式提取 Ghidra 反编译器生成 **的所有伪** 代码。

  * [Semgrep](https://github.com/0xdea/semgrep-rules)是经过专门设计的，可帮助审计员 **识别潜在的错误，并在 C/C++ 代码中找到** 热点，以便将注意力集中在这些代码上。![](https://image.3001.net/images/20220715/1657858728_62d0eaa89ce95401fafa1.png!small)

 **Haruspex + semgrep** 给了二进制漏洞分析另一种“旁门左道”的分析思路，即先利用 **Haruspex** 反编译成伪代码，再通过
**semgrep** 对伪代码作审计，即转黑为白的测试方法。

## 二、静态分析

不需要氪金买设备，不需要解决各种头疼的模拟错误，下面开始愉快地静态分析。

### 2.1 BinAbsInspector

  * 安装

将`[ghidra_10.1.2_PUBLIC_20220420_BinAbsInspector.zip](<https://github.com/KeenSecurityLab/BinAbsInspector/releases/download/v0.1/ghidra_10.1.2_PUBLIC_20220420_BinAbsInspector.zip>)`拷贝至`ghidra_10.1.2_PUBLIC_20220125\\ghidra_10.1.2_PUBLIC\\Extensions\\Ghidra`目录下，

点击file->install
extension，选择执行插件安装，这里注意版本要对应上：![](https://image.3001.net/images/20220715/1657858749_62d0eabd7093056cf276f.png!small)

此外还需安装`[z3 lib](<https://github.com/Z3Prover/z3/releases>)`，如果`z3
lib`没有装成功，可以先不勾选`z3`。![](https://image.3001.net/images/20220715/1657858768_62d0ead069db003439dfa.png!small)

  * 测试

用Ghidra打开upnpd二进制文件，选择windows→Script
Manager→BinAbsInspector，等待分析结束即可：![](https://image.3001.net/images/20220715/1657858787_62d0eae3c441e79e6d60b.png!small)

当然 **CWE** 规则可以自行选择，这里默认全选，所以检测出的结果比较多……

  * 分析

可以看到把所有认为的危险函数列出并下了断点，在已知upnpd的漏洞处当然也有标识：![](https://image.3001.net/images/20220715/1657858805_62d0eaf59206a25e9c5d3.png!small)

但其缺点在于没有作过滤(应该可以通过二次开发解决)，所以需要手动回溯的信息过多，实际使用中必然要结合其他方式分析。再比如对`strcpy(local_2c[0],s_HTTP/1.1_200_OK_CONTENT-LENGTH:_00081c70)`此类固定值也未作判断，也标识为潜在漏洞点：![](https://image.3001.net/images/20220715/1657858822_62d0eb06b86f9cb998bf4.png!small)

### 2.2 SaTC

  * 安装

SaTC安装参见 **[Github](https://github.com/NSSL-SJTU/SaTC)** ，当然也可直接下载使用Docker：

    
    
    # 从docker hun拉去image
    docker pull smile0304/satc:V1.0
    
    # 进入Dokcer环境, 自行添加目录映射
    docker run -it smile0304/satc:V1.0
    

值得注意的是在使用中可能 **报错** ，下述解决方案可供参考：

`(1) Docker: Error response from daemon: cgroups: cgroup mountpoint does not
exist: unknown`

    
    
    # 解决方法
    $ sudo mkdir /sys/fs/cgroup/systemd
    $ sudo mount -t cgroup -o none,name=systemd cgroup /sys/fs/cgroup/systemd
    

`(2) No handlers could be found for logger "root" …… for consistency with C it
should have a storage class specifier (usually 'extern') "(usually 'extern')"
% (decl.name,))`

    
    
    # 解决方法
    # 使用 -b 加参数时无需路径，只需elf名：
    $ python satc.py -d /targetfs/ -o ../lighttpd_result/ --ghidra_script=ref2sink_bof --ghidra_script=ref2sink_cmdi --taint_check -b lighttpd
    

`(3) IOError: [Errno 2] No such file or directory:
u'/home/satc/SaTC/SaTC_data/res/keyword_extract_result/simple/.data/downloadFlile.cgi.result’`

这是因为固件多个bin共享关键字，调用顺序应该为 ：前段关键字 -> lighttpd->
xxx.cgi，也就是数据是要先经过lighttpd的，使用share2sink从lighttpd中提取使用nvram或env设置的关键字，然后再追踪流向cgi的关键字。

    
    
    # 首先使用ref2share提取关键字
    $ python satc.py -d /home/satc/dlink_878 -o /home/satc/res --ghidra_script=ref2share -b prog.cgi
    # 在进行进一步测试
    $ python satc.py -d /home/satc/dlink_878 -o /home/satc/res --ghidra_script=share2sink --ref2share_result=/home/satc/res/ghidra_extract_result/prog.cgi/prog.cgi_ref2share.result -b rc --taint_check
    

更多细节可参见[ **官方issue**](https://github.com/NSSL-SJTU/SaTC/issues)。

  * 测试

SaTC针对性更强，但缺陷也教明显，如果研究的二进制文件没有与前端共享字符串就很难检测出异常。在upnpd检测中，通过以下命令检测`bof`漏洞：

    
    
    $ python satc.py -d /home/satc/squashfs -o /home/satc/res --ghidra_script=refsink2_bof -b upnpd --taint_check

![](https://image.3001.net/images/20220715/1657858850_62d0eb22708592915a340.png!small)SaTC运行时间较长，通过关键字层层过滤，最后结果可查询`info.txt`：![](https://image.3001.net/images/20220715/1657858872_62d0eb38726ae20bbd3f3.png!small)

可以看到SaTC结果中给出了回溯信息：![](https://image.3001.net/images/20220715/1657858888_62d0eb48b91cceef0d15c.png!small)

### 2.3 Rhabdomancer

  * 安装

无需安装，只有一个[ **java**](https://github.com/0xdea/ghidra-scripts/blob/main/Rhabdomancer.java)文件，点击window→Script Manager→Manager Script
Directories，将.java所在文件夹路径添加即可：![](https://image.3001.net/images/20220715/1657858906_62d0eb5a6e55c85ce1703.png!small)

  * 测试

通过加载插件可以很快得到结果：![](https://image.3001.net/images/20220715/1657858925_62d0eb6d09e39a6023d1d.png!small)

Rhabdomancer插件功能比较单一，会将设置好的关键字过滤打印，好处是代码结构很好理解，方便二次开发，下文也会作进一步分析。![](https://image.3001.net/images/20220715/1657858941_62d0eb7de43a83dac959b.png!small)

### 2.4 **Haruspex + semgrep**

  * Haruspex同样也是Ghidra插件，安装同上：![](https://image.3001.net/images/20220715/1657858958_62d0eb8e856a90a4674fa.png!small)

其功能是将二进制文件转化成伪代码，这里在生成的伪代码文件夹中可以找到upnpd漏洞函数，表现为一个以函数地址命名的C文件：![](https://image.3001.net/images/20220715/1657858973_62d0eb9d7b8b30479b908.png!small)

 **semgrep**
是一款开源的源代码审计工具，适用于**C/C++**等多语言，以插件形式加载。![](https://image.3001.net/images/20220715/1657858991_62d0ebafcb92d58117c96.png!small)

    
    
    # 安装
    pip install semgrep
    # 加载插件
    semgrep --config=auto
    

![](https://image.3001.net/images/20220715/1657859008_62d0ebc07de7d42d2e37a.png!small)

此工具属于源码审计范畴，同类工具也比较多，这里就不作赘述，对该工具感兴趣的可参考【3】，效果如下：![](https://image.3001.net/images/20220715/1657859040_62d0ebe034104a44e9374.png!small)

## 三、工具分析

### 3.1 源码分析

  * BinAbsInspector

BinAbsInspector的关键文件包括`InterSolver.java`、`BinAbsInspector.java`和`CWEXXX.java`，其执行流如下图所示：![](https://image.3001.net/images/20220715/1657859056_62d0ebf0f2ac16ff6ed3c.png!small)

  * AbsVal

抽象值（AbsVal）不同于具体值。抽象值由两部分组成：一个是该抽象值所在的区域组件，另一个是通过区域基数加上区域内的偏移量计算的值组件。

  * AbsEnv

抽象环境（AbsEnv）是存储每个程序点的程序状态的核心数据结构。AbsEnv 是从 ALoc 作为键到 KSet 作为值的映射。

  * AbsVal

KSet是一个特殊的集合，可以容纳具有大小限制K的抽象值 (AbsVal)。

`InterSolver.java`将Ghidra P-Code 转化成
KSet，并生成Context和AbsEnv；`BinAbsInspector.java`先获取`GlobalState.config`配置，然后`call
analyze()`进入分析引擎`InterSolver`进行分析
，其输入是`main/e_entry`地址(从`GlobalState.config`读取，可自定义)，接着进入到`CheckerManager.runCheckers`。`CheckerManager.runCheckers`根据`GlobalState.config`配置的`CWE`选项进一步分析。

有关BinAbsInspector 原理与调试的更多细节可参考 **BinAbsInspector研究笔记【4】**

  * SaTC

SaTC关注前后端关键字共享，并将其作为污点选取的依据。![](https://image.3001.net/images/20220715/1657859070_62d0ebfe2f167ebbf4179.png!small)

SaTC使用`python`开发，结构也十分清晰，`stac.py`中通过前端分析函数`front_analysise(args)`生成`bin_list`列表，在根据参数进一步污点分析：![](https://image.3001.net/images/20220715/1657859082_62d0ec0abed00c90215fa.png!small)

值得注意的还有`ref2share.py`，定义了提取关键字，适用于先提取后检测的情况：

    
    
    sinks = ['nvram_safe_set', 'nvram_bufset', 'setenv']
    digest = ['strcpy', 'sprintf', 'memcpy', 'strcat']
    
    heuristicIgnoreFunctions = ['strcpy', 'strncpy', 'strcat', 'memcpy']
    
    needCheckConstantStr = {
        'system': 0,
        'fwrite': 0,
        '___system': 0,
        'bstar_system': 0,
        'popen': 0,
        'execve': 0,
        'strcpy': 1,
        'strcat': 1,
        'strncpy': 1,
        'memcpy': 1,
        'twsystem': 0
    }
    

SaTC输出目录含义如下:

  * keyword_extract_result/detail/Clustering_result_v2.result

前端关键字在bin中的匹配情况。为`Input Entry Recognition`模块的输入；

  * ghidra_extract_result/{bin}/*

ghidra脚本的分析结果。为`Input Sensitive Taint Analysise`模块的输入；

  * result-{bin}-{ghidra_script}-{random}.txt

污点分析结果。

其他结果含义如下：

    
    
    |-- ghidra_extract_result # ghidra寻找函数调用路径的分析结果, 启用`--ghidra_script`选项会输出该目录
    |   |-- httpd # 每个被分析的bin都会生成一个同名文件夹
    |       |-- httpd # 被分析的bin
    |       |-- httpd_ref2sink_bof.result # 定位bof类型的sink函数路径
    |       |-- httpd_ref2sink_cmdi.result # 定位cmdi类型的sink函数路径
    |-- keyword_extract_result  # 关键字提取结果
    |   |-- detail  # 前端关键字提取结果(详细分析结果)
    |   |   |-- API_detail.result # 提取的API详细结果
    |   |   |-- API_remove_detail.result # 被过滤掉的API信息
    |   |   |-- api_split.result  # 模糊匹配的API结果
    |   |   |-- Clustering_result_v2.result # 详细分析结果(不关心其他过程关心此文件即可)
    |   |   |-- File_detail.result  # 记录了从单独文件中提取的关键字
    |   |   |-- from_bin_add_para.result # 在二进制匹配过程中新增的关键字
    |   |   |-- from_bin_add_para.result_v2 # 同上,V2版本
    |   |   |-- Not_Analysise_JS_File.result # 未被分析的JS文件
    |   |   |-- Prar_detail.result # 提取的Prar详细结果
    |   |   |-- Prar_remove_detail.result # 被过滤掉的Prar结果
    |   |-- info.txt  # 记录前端关键字提取时间等信息
    |   |-- simple  # 前端关键字提取结果, 比较简单
    |       |-- API_simple.result # 在全部二进制中出现的全部API名称
    |       |-- Prar_simple.result  # 在全部二进制中出现等的全部Prar
    |-- result-httpd-ref2sink_cmdi-ctW8.txt # 污点分析结果,启用`--taint-check` 和 `--ghidra_script`选项才会生成该文件
    

  * Rhabdomancer

 **[Rhabdomancer](https://github.com/0xdea/ghidra-scripts/blob/main/Rhabdomancer.java)**
结构十分简单，通过`tier0`，`tier1`，`tier2`定义三类Bad函数：

    
    
    bad.put("[BAD 0]", tier0);
    	bad.put("[BAD 1]", tier1);
    	bad.put("[BAD 2]", tier2);
    

  * `tier0`：

    
    
    // these functions are generally considered insecure
    // see also <https://github.com/x509cert/banned/blob/master/banned.h>
    List<String> tier0 = new ArrayList<>(List.of(
    			// strcpy family
    			"strcpy", "_strcpy", "strcpyA", "strcpyW", "wcscpy", "_wcscpy", "_tcscpy", "mbscpy", "_mbscpy", 
    			"StrCpy", "StrCpyA", "StrCpyW", 
    			"lstrcpy", "lstrcpyA", "lstrcpyW", "_tccpy", "_mbccpy", "_ftcscpy",
    			....
    

  * `tier1`：

    
    
    // these functions are interesting and should be checked for insecure use cases
    		List<String> tier1 = new ArrayList<>(List.of(
    			// strncpy needs explicit null-termination: buf[sizeof(buf) – 1] = '\\0'
    			"strncpy", "_strncpy", "wcsncpy", "_tcsncpy", "_mbsncpy", "_mbsnbcpy", 
    			"StrCpyN", "StrCpyNA", "StrCpyNW", "StrNCpy", "strcpynA", "StrNCpyA", "StrNCpyW", 
    			"lstrcpyn", "lstrcpynA", "lstrcpynW", "_csncpy", "wcscpyn",
    			"stpncpy", "wcpncpy",......
    

  * `tier2`：

    
    
    // code paths involving these functions should be carefully checked
    		List<String> tier2 = new ArrayList<>(List.of(
    			// check for insecure use of environment vars
    			"getenv",
    			// check for insecure use of arguments
    			"getopt", "getopt_long",
    			// check for insecure use of memory allocation functions
    			// check if size arg can contain negative numbers or zero, return value must be checked
    			"malloc", "xmalloc",
    			"calloc", // potential implicit overflow due to integer wrapping
    			"realloc", "xrealloc", "reallocf", // doesn't initialize memory to zero; realloc(0) is equivalent to free
    			"valloc", "pvalloc", "memalign", "aligned_alloc", ......
    

通过`getFunctions`和`listCalls`函数实现迭代查找：

    
    
    // enumerate candidate points at each tier
    		Iterator<Map.Entry<String, List<String>>> i = bad.entrySet().iterator();
    		while (i.hasNext()) {
    			funcs.clear();
    			Map.Entry<String, List<String>> entry = i.next();
    			printf("\\n%s\\n\\n", entry.getKey());
    			entry.getValue().forEach(s -> getFunctions(s, funcs));
    			funcs.forEach(f -> listCalls(f, entry.getKey() + " " + f.getName()));
    		}
    

### 3.2 进一步工作

  * 上述二进制辅助工具各有优势，一定程度上提高了分析效率，但在实际研究中有时也需要 **二次开发** 加强针对性，对于污点的选择、判断和回溯准确性和效率仍是需要重点研究优化的方向。

  * 可以将二进制辅助工具与固件分析平台结合进一步提高自动化(懒)，如FACT，实际上FACT已包含cwe_checker作为插件，只是功能较为单一，感兴趣的可参考笔者之前的一篇文章[ **FACT二次开发指** 北](../sectool/323613.html)【5】。

## 四、参考资料

【1】 **[IOT 固件安全 All in One](https://wokough.gitbook.io/iot-firmware-aio/)**

【2】[ **Sharing More and Checking Less: Leveraging Common Input Keywords to
Detect Bugs in Embedded
Systems**](https://www.usenix.org/system/files/sec21fall-chen-libo.pdf)

【3】 **[Automating binary vulnerability discovery with Ghidra and
Semgrep](https://security.humanativaspa.it/automating-binary-vulnerability-discovery-with-ghidra-and-semgrep/)**

【4】
**[BinAbsInspector研究笔记](https://www.wolai.com/nocbtm/aSHsPHF3QG8RueRMT7xiKQ)**

【5】[ **FACT二次开发指北**](../sectool/323613.html)

【6】
**[开源二进制文件静态漏洞分析工具BinAbsInspector安装使用](https://chowdera.com/2022/174/202206231017262244.html)**

【7】 **[CTF All In One](https://firmianay.gitbooks.io/ctf-all-in-one/content/)**

