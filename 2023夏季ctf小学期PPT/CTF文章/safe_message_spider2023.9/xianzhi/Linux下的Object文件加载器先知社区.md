## 前言

在Windows下已经有了很多针对Coff文件的加载器，如CoffLoader和CS的BOF功能，但是linux上面相关功能还是欠缺的，因此本本文章介绍一下相关技术，并提供了实现代码

项目地址（求个star）：<https://github.com/Sndav/coffee>

## 目标设定

    
    
    void println(char *buf);
    void debugln(char *buf);
    void hello_world();
    
    
    int test_func_call(unsigned char *buf){
        println(buf);
        return 0;
    }
    
    int main(){
        char *buf = "Hello World!";
        test_func_call(buf);
        debugln(buf);
        hello_world();
        return 1;
    }
    

期望可以加载上述文件所生成的`test.o`文件

## ELF文件中结构

我们可以用`objdump -d test.o -M intel`看一下这个load函数的汇编

    
    
    Disassembly of section .text:
    
    0000000000000000 <test_func_call>:
       0:   f3 0f 1e fa             endbr64
       4:   55                      push   rbp
       5:   48 89 e5                mov    rbp,rsp
       8:   48 83 ec 10             sub    rsp,0x10
       c:   48 89 7d f8             mov    QWORD PTR [rbp-0x8],rdi
      10:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
      14:   48 89 c7                mov    rdi,rax
      17:   e8 00 00 00 00          call   1c <test_func_call+0x1c>
      1c:   b8 00 00 00 00          mov    eax,0x0
      21:   c9                      leave
      22:   c3                      ret
    
    0000000000000023 <main>:
      23:   f3 0f 1e fa             endbr64
      27:   55                      push   rbp
      28:   48 89 e5                mov    rbp,rsp
      2b:   48 83 ec 10             sub    rsp,0x10
      2f:   48 8d 05 00 00 00 00    lea    rax,[rip+0x0]        # 36 <main+0x13>
      36:   48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
      3a:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
      3e:   48 89 c7                mov    rdi,rax
      41:   e8 [00 00 00 00]        call   46 <main+0x23> # 可以看到这里的操作数全是0
      46:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
      4a:   48 89 c7                mov    rdi,rax
      4d:   e8 [00 00 00 00]        call   52 <main+0x2f>
      52:   b8 00 00 00 00          mov    eax,0x0
      57:   e8 00 00 00 00          call   5c <main+0x39>
      5c:   b8 01 00 00 00          mov    eax,0x1
      61:   c9                      leave
      62:   c3                      ret
    

### .rela节

我们可以发现，上述反编译代码的call指令的操作数全部是0，为了能正确找到call的正确位置，所以链接器会修改这个偏移值。怎么修改呢，需要根据rela节中的数据进行修改。rela节的表项结构体如下

    
    
    typedef struct {
            Elf32_Addr      r_offset;
            Elf32_Word      r_info;
            Elf32_Sword     r_addend;
    } Elf32_Rela;
    

我们可以使用`readelf -r test.o`获取函数的重定向节，一般来说`.text`的rela节的名字是`.rela.text`

    
    
    Relocation section '.rela.text' at offset 0x268 contains 5 entries:
      Offset          Info           Type           Sym. Value    Sym. Name + Addend
    000000000018  000500000004 R_X86_64_PLT32    0000000000000000 println - 4
    000000000032  000300000002 R_X86_64_PC32     0000000000000000 .rodata - 4
    000000000042  000400000004 R_X86_64_PLT32    0000000000000000 test_func_call - 4
    00000000004e  000700000004 R_X86_64_PLT32    0000000000000000 debugln - 4
    000000000058  000800000004 R_X86_64_PLT32    0000000000000000 hello_world - 4
    
    Relocation section '.rela.eh_frame' at offset 0x2e0 contains 2 entries:
      Offset          Info           Type           Sym. Value    Sym. Name + Addend
    000000000020  000200000002 R_X86_64_PC32     0000000000000000 .text + 0
    000000000040  000200000002 R_X86_64_PC32     0000000000000000 .text + 23

我们可以看到其中的一行，这里面有6个值，但是结构体只有3个，这个原因我们下面会解释

    
    
    000000000018  000500000004 R_X86_64_PLT32    0000000000000000 println - 4

  * `r_offset: 000000000018`: 代表着这个重定向位置相对section首地址的偏移，这里就是用括号框起来的这个位置，

    
    
    17: e8 [00 00 00 00]        call   1c <test_func_call+0x1c>

  * `r_info: 000500000004`：对于32位ELF文件可进一步细分为 24 位 **符号表索引** 和 8 位 **类型字段** ，64位ELF文件可以32位的的 **符号表索引** 和32位的 **类型字段**
    * `sym = r_info >> 32 = 5`
    * `type = r_info & 0xFFFFFFFF = 4`
  * `R_X86_64_PLT32`: 这个不是一个字段，type就是来决定`R_X86_64_PLT32`的
    * 这个类型可以在Intel的官网中找到 <https://www.intel.com/content/dam/develop/external/us/en/documents/mpx-linux64-abi.pdf>
    * ![](./img/619029992578112752.png)
    * 我们可以看到4代表的就是`R_X86_64_PLT32`
  * `0000000000000000 println`：这两个是从符号表中关联过来的，后面会详细介绍
  * `r_addend: -4`：这是一个很重要的字段，在重定位中有着很重要的作用，在后续的重定位指针章节中会详细介绍

### .symtab节

    
    
    typedef struct {
            Elf64_Word      st_name;
            unsigned char   st_info;
            unsigned char   st_other;
            Elf64_Half      st_shndx;
            Elf64_Addr      st_value;
            Elf64_Xword     st_size;
    } Elf64_Sym;
    

我们可以通过`readelf -s test.o`读取符号节

    
    
    Symbol table '.symtab' contains 9 entries:
       Num:    Value          Size Type    Bind   Vis      Ndx Name
         0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
         1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS test.c
         2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1 .text
         3: 0000000000000000     0 SECTION LOCAL  DEFAULT    5 .rodata
         4: 0000000000000000    35 FUNC    GLOBAL DEFAULT    1 test_func_call
         5: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND println
         6: 0000000000000023    64 FUNC    GLOBAL DEFAULT    1 main
         7: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND debugln
         8: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND hello_world
    

  * st_name: 这里的起始是一个索引，对应strtab中的字符串。
    * 可以通过在strtab中读取这个值
  * st_shndx: 代表着该符号所在的节的序号，还有几个特殊的值
    * SHN_UNDEF表示这个符号并未在当前文件定义，这个文件没有这个符号的位置
    * SHN_ABS表示这个符号是一个绝对地址，不需要重定位
    * SHN_COMMON表示这个符号是用来定义对齐字节的。
  * st_value: 代表着该符号，相对于符号所在节起始地址的偏移
    * 若改符号st_shndx=SHN_COMMON，那么st_value代表着对齐字节数
  * 其他字段暂时用不到

## 重定位偏移

我们可以看到上面关于重定位类型的图，这里的S，A，L，P，G，GOT分别代表

  * A 代表用于计算可重定位字段值的被加数。
  * B 代表在执行期间加载到内存中的共享对象的基地址。一般来说，共享对象的基虚拟地址为0，但执行地址会有所不同。
  * G 代表重定位项符号在全局偏移表（GOT）中的偏移量，在执行期间该符号将位于此处。
  * GOT 代表全局偏移表的地址。 
  * L 代表符号的过程链接表（PLT）条目的位置（段偏移或地址）。 
  * P 代表正在重定位的存储单元的位置（段偏移或地址）（使用 r_offset 计算）。
  * S 代表重定位项中索引所在符号的值。
  * Z 代表重定位项中索引所在符号的大小。

到这里，就需要研究一下这些重定向模式了，但是值得一提的是，在这个加载器中很多类型都是相同的，比如说`R_X86_64_PLT32`和`R_X86_64_PC32`，因为我们根本没有PLT表

为了重定位，我们需要将重定位的类型分成两种情况，

  * 程序内重定向：指的是一个`.o`程序当中某个函数对另一个函数的调用，对程序内字符串的引用等，比如说在这个例子中`main`函数中对`test_func_call`的调用
  * 程序外重定向：指的是程序调用外部函数，需要重定向程序外的函数的真实地址，比如说在这个例子中`main`中对`hello_world`,`debugln`的调用

### 程序内重定向

程序内重定向的逻辑其实和标准的链接步骤相同，按照基本的规则进行链接即可。我们这里来看一下本例当中`main`函数对`test_func_call`的调用。

在重定位表中，这个对应如下表项

    
    
    000000000042  000400000004 R_X86_64_PLT32    0000000000000000 test_func_call - 4

这里我们可以看到我们修改的偏移是42字节，类型是`R_X86_64_PLT32`，代表着修改的长度是32位，4字节，`addend =
-4`。对应的汇编如下

    
    
    0000000000000023 <main>:
      23:   f3 0f 1e fa             endbr64
      27:   55                      push   rbp
      28:   48 89 e5                mov    rbp,rsp
      2b:   48 83 ec 10             sub    rsp,0x10
      2f:   48 8d 05 00 00 00 00    lea    rax,[rip+0x0]        # 36 <main+0x13>
      36:   48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
      3a:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
      3e:   48 89 c7                mov    rdi,rax
     >41:   e8 [00 00 00 00]        call   46 <main+0x23>
      46:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
      4a:   48 89 c7                mov    rdi,rax
      4d:   e8 00 00 00 00          call   52 <main+0x2f>
      52:   b8 00 00 00 00          mov    eax,0x0
      57:   e8 00 00 00 00          call   5c <main+0x39>
      5c:   b8 01 00 00 00          mov    eax,0x1
      61:   c9                      leave
      62:   c3                      ret
    

根据手册这个类型的计算规则是`L + A - P`,但是由于我们这里没有PLT表，但是根据基本原理我们这里要这么计算

    
    
    sym_real_address + r_addend - patch_real_address

  * sym_real_address: 符号的真实内存地址
  * patch_real_address: 在内存中修改的需要修改的起始地址
  * r_addend这是需要加上的，用来解决偏移问题的

同理，其他的模式也可以通过具体分析去写出来

### 程序外重定向

程序外重定向就更加简单了，根本不需要考虑重定向类型。由于`call`指令的操作数记录的是相对`rip`的偏移，而真实的`rip`相对修改的地址有4/8个字节的偏差（根据操作数长度判定）。所以直接计算这个偏移即可

    
    
    sym_real_address  - patch_real_address - 4/8

## 总结

到此为止我们介绍完了相关技术，具体代码已经上传至github，因为是rust语言编写可能读起来难度比较大，但是谁让rust好写呢（x，项目地址：<https://github.com/Sndav/coffee>

