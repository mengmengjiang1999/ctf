***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：tocttou，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**我发现Freebuf上没有整数溢出漏洞的基础介绍，所以这篇文章通过分析我刚刚发现的UPX源代码中的整数溢出漏洞，介绍一下C/C++整数溢出漏洞的原理、触发和修复方法。这篇文章暂不涉及如何利用整数溢出达到远程代码执行，UPX的漏洞只是一个拒绝服务漏洞。**

## 0x01 整数溢出原理

C/C++中的整数溢出基本原理非常简单，比如unsigned char number = 200 + 200;。最终number的值是400 mod
256=144。这是因为C++对于无符号整数（unsigned char, unsigned
int等）溢出的处理是取模，导致的结果是两个整数相加，反而结果更小。C++中有符号整数溢出是未定义行为。下文中所有提到整数溢出，都指的是无符号整数溢出。整数溢出的利用一般都是用它来导致缓冲区溢出，进而利用缓冲区溢出技巧来代码执行、泄露内存或拒绝服务。

我认为对于文件解析一类的程序要特别注意整数溢出问题，因为有很多文件格式，它们的文件头中包含了长度、偏移信息。攻击者通过构造畸形文件可以直接控制这些信息，尝试触发整数溢出或其他缓冲区溢出漏洞。所以在写代码时我们需要关注的点有：第一，将整数运算的结果作为缓冲区长度分配内存；第二，将整数运算的结果作为偏移量读取内存。

对于第一点，比如这段代码：

    
    
    size_t len = len1 + 0x40;
    char *buffer = new char[len];
    buffer[0x10] = 'a';
    

如果len1是攻击者可控的值，那么这里就存在整数溢出问题。假设是32位程序，攻击者选取len1 =
0xFFFFFFC1，那么len1+40等于1，所以buffer的长度为1。第三行，作者错误地假设了下标0x10一定会在buffer分配的内存区间内，但实际上这里发生了越界写入。

对于第二点，看这段代码：

    
    
    char buffer[100];
    unsigned char offset = getOffset();  // offset攻击者可控
    if (40 + offset < sizeof(buffer)) {
        buffer[offset] = 0;
    }
    

这里作者错误地假设了如果40 + offset这个index没有越界，则offset这个index也没有越界。但是如果我们取offset=255。则40 +
offset = 39，那么我们就将buffer[255]这个越界地址写入了0。  

## 0x02 分析UPX整数溢出漏洞

这个漏洞是我最近找出来的[UPX开源项目](https://github.com/upx/upx/)的漏洞。因为最近研究UPX，随手在[CVE数据库](https://cve.mitre.org/cve/search_cve_list.html)里搜索了一下有没有UPX的漏洞，结果还真有，[CVE-2017-15056](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-15056)。漏洞报告在
<https://github.com/upx/upx/issues/128>
。这是一个畸形文件导致内存越界读取漏洞，我看了一下[修复的commit](https://github.com/upx/upx/commit/ef336dbcc6dc8344482f8cf6c909ae96c3286317)。从commit来看，修复并不完美，而且正好可以拿来讲整数溢出。

我们重点看commit中PackLinuxElf32::PackLinuxElf32help1函数中添加在250-256行的校验：  

![oldcommit.png](https://image.3001.net/images/20180316/15211604596575.png!small)

file_size是用户输入的ELF文件的大小，e_phoff, e_phnum, e_shoff,
e_shnum都是ELF文件头部的字段。这些值我们可以通过构造畸形ELF文件来控制。显然这里作者在避免缓冲区越界读取问题，检测e_shoff +
e_shnum *
sizeof(Elf32_Shdr)这个偏移量是否依然在ELF文件大小之内。如果不在，就抛出异常，因为我们的缓冲区只有file_size这么大。作者想到了检查整数溢出，但是他的方法是把e_phoff和e_shoff从unsigned
int转换成unsigned long。值得注意的是unsigned
long的大小是：MSVC下永远是32位整数，gcc和clang下32位ELF就是32位整数，64位ELF就是64位整数。所以如果我们用32位UPX的话，(unsigned
long)e_shoff + e_shnum *
sizeof(Elf32_Shdr)是可以溢出的，只要e_shoff足够大，让它们的和大于或等于2^32，它的值就可以小于file_size。

往下：

![Line265to287.png](https://image.3001.net/images/20180316/15211604596795.png!small)

268至272行针对e_type不是ET_DYN (shared object
file)情形，268行的len就是之前258行校验的值，按上文说的len是溢出之后的值，它小于file_size，但是e_phoff很大。所以到272行phdri=e_phoff
+
file_image又发生整数溢出，phdri会小于file_image。所以如果接下来phdri被用于读取Elf32_Phdr结构体的值，那么读到的实际上是缓冲区file_image以外的值。但是随后发现phdri使用之前会检查e_phoff是否为0x40。所以这个缓冲区越界读取是触发不了的。

接下来274行以下针对e_type是ET_DYN情形，类似地，因为我们取e_shoff为一个接近2^32的值，如0xFFFFE000，这样shdri=
(Elf32_Shdr *)(e_shoff +
file_image);指向的就是file_image内存之前的位置。然后进入elf_find_section_type(Elf32_Shdr::SHT_DYNSYM)函数：

![findsectiontype.png](https://image.3001.net/images/20180317/15212275472037.png!small)

for循环内shdri指针被用来读取shdri->sh_type的值。这时因为shdri不是一个有效的地址，这里就会触发崩溃。

所以我的PoC就直接把CVE-2017-15056的PoC拿来，把e_type改成3
(ET_DYN)、e_shoff改成0xFFFFE000、e_shnum改成0x00FF。这样e_shoff + e_shnum *
sizeof(Elf32_Shdr)的值是0x07D8，小于file_size。shdri等于file_image -0x2000。用32位UPX压缩PoC，就能看到崩溃：

![crash.png](https://image.3001.net/images/20180316/15211604594469.png!small)

当然这个整数溢出漏洞只能到拒绝服务为止了，应该是没法远程利用的（比如把内存写到输出文件里）。我也对UPX、ELF文件了解不多，所以就没深入研究其他位置有没有溢出问题。

## 0x03 修复

我提交了一个[Pull
request](https://github.com/upx/upx/pull/190)修复这个UPX漏洞，但是他们没用我的PR，他们自己写了一个[commit](https://github.com/upx/upx/commit/90a1322929259b3049f11564d25cc1bc99ee54fa)。对于加法避免整数溢出的方法两种：加法运算的和如果小于任何一个加数，则有溢出：

    
    
    unsigned int add(unsigned int a, unsigned int b, bool& isOverflow)
    {
        unsigned int result = a + b;
        isOverflow = (result < a);
        return result;
    }
    

另一种是转换成64位无符号整数：

    
    
    unsigned int add(unsigned int a, unsigned int b, bool& isOverflow)
    {
        unsigned long long result64 = (unsigned long long)a + (unsigned long long)b;
        unsigned int result = static_cast<unsigned int>(result64);
        isOverflow = (result64 != result);
        return result;
    }
    

乘法：转换成64位或者：

    
    
    unsigned int mul(unsigned int a, unsigned int b, bool& isOverflow)
    {
        unsigned int result = a * b;
        isOverflow = (a != 0) && (result / a != b);
        return result;
    }
    

## 0x04 参考

> <https://github.com/upx/upx/issues/128>
>
> <https://github.com/upx/upx/commit/ef336dbcc6dc8344482f8cf6c909ae96c3286317>
>
> <https://github.com/upx/upx/pull/190>
>
> <https://github.com/upx/upx/commit/90a1322929259b3049f11564d25cc1bc99ee54fa>

***本文原创作者：tocttou，本文属FreeBuf原创奖励计划，未经许可禁止转载**

