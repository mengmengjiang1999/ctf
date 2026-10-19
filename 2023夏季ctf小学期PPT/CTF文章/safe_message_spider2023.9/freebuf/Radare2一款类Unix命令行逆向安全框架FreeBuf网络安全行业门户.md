工具介绍  

**Radare2基于Radare开发，并支持第三方二进制文件以提供更多的实用功能。Radare作为一款取证工具，提供了可编辑的命令行十六进制编辑器，可直接打开磁盘文件，但后来又添加了分析模块、反编译模块、调试程序和远程gdb服务器。Radere2亦是如此，但Radare2的灵活性更高。**

![a.jpg](https://image.3001.net/images/20190213/1550068279_5c642a371e64f.jpg!small)

### 架构支持

i386,x86-64, ARM, MIPS, PowerPC, SPARC, RISC-V, SH, m68k, AVR, XAP, System Z,
XCore,CR16, HPPA, ARC, Blackfin, Z80, H8/300, V810, V850, CRIS, XAP, PIC,
LM32, 8051,6502, i4004, i8080, Propeller, Tricore, Chip8 LH5801, T8200,
GameBoy, SNES,MSP430, Xtensa, NIOS II, Dalvik, WebAssembly, MSIL, EBC, TMS320
(c54x, c55x,c55+, c66), Hexagon, Brainfuck, Malbolge, DCPU16。

### 文件格式

ELF,Mach-O, Fatmach-O, PE, PE+, MZ, COFF, OMF, TE, XBE, BIOS/UEFI, Dyldcache,
DEX,ART, CGC, Java类, Android启动镜像, Plan9可执行文件, ZIMG, MBN/SBL bootloader, ELF
coredump, MDMP (Windows minidump),WASM (WebAssembly代码), Commodore VICE 模拟器,
Game Boy (高级), Nintendo DS ROMs, Nintendo3DS FIRMs, 以及各种文件系统。

### 操作系统

Windows（XP及以上版本）, GNU/Linux, OS X, [Net|Free|Open]BSD, Android, iOS, OSX,
QNX,Solaris, Haiku, FirefoxOS。

### 支持绑定

Vala/Genie,Python (2, 3), NodeJS, Lua, Go, Perl, Guile, PHP, Newlisp, Ruby,
Java, OCaml...

### 依赖组件

Radare2可以在不依赖任何特殊组件的情况下完成构建，你可以使用libewf来加载EnCase磁盘镜像，如需构建绑定的额外代码库，你需要最新版本的valabind、g++和swig2。

## 工具安装

安装Radare2最简单的方法就是直接使用下列命令下载并安装：

    
    
    $sys/install.sh

如果你想从主目录安装Radare2，并且没有root权限和sudo的话，你可以运行：

    
    
    $sys/user.sh

### 使用meson + ninja构建

如果你没有meson和ninja，你可以使用安装包管理器或r2pm进行安装：

    
    
    $r2pm -i meson

如果你已经安装好了，你可以直接运行下列代码编译radare2：

    
    
    $python ./sys/meson.py --prefix=/usr --shared –install

## 工具更新

运行下列命令可直接更新Radare2：

    
    
    $sys/install.sh

如果你把Radare2安装在主目录，你可以直接运行：

    
    
    $sys/user.sh

## 包管理器

Radare2拥有自己的包管理器：r2pm，所有的包代码都可以在[GitHub](https://github.com/radare/radare2-pm)上找到。首次使用时，你需要初始化包：

    
    
    $r2pm init

在安装任何代码包前请刷新包数据库：

    
    
    $r2pm update

使用下列命令安装代码包：

    
    
    $r2pm install [package name]

## 代码绑定

所有绑定的编程语言全部在r2-bindings目录下，你需要安装swig和valabind来构建绑定的Python和Lua等语言。比如说，你可以使用下列命令安装Python绑定：

    
    
    $r2pm install lang-python2 #lang-python3 for python3 bindings
    
    $r2pm install r2api-python
    
    $r2pm install r2pipe-py

## Web服务器

Radare2自带了内嵌的Web服务器，服务器提供了纯html/js接口可发送ajax请求。

    
    
    $ r2-c=H /bin/ls

在Windows平台上使用Web服务器，你需要一个cmd实例以及管理员权限。使用下列命令开启Web服务器：

    
    
    >radare2.exe -c=H rax2.exe

## 参考文档

【[Radare2文档](https://radare.gitbooks.io/radare2book/content/)】

### 项目地址

Radare2：【[GitHub传送门](https://github.com/radare/radare2)】

 ***参考来源：[radare2](https://www.kitploit.com/2018/12/radare2-unix-like-reverse-engineering.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

