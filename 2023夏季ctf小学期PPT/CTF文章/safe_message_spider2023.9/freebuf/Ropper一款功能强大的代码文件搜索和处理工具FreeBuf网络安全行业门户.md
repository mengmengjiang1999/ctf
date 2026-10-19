![](https://image.3001.net/images/20230713/1689246054_64afd9661f8b5c5e382e6.png!small)

## 关于Ropper

Ropper是一款功能强大的代码文件搜索和处理工具，该工具能够帮助广大研究人员以不同的文件格式显示有关文件的信息，并查找用于构建不同体系结构（x86/x86_64、ARM/ARM64、MIPS、PowerPC、SPARC64）的rop链的Gadget。

值得一提的是，Ropper基于著名的[ _Capstone_](http://www.capstone-engine.org/)框架实现了其反汇编功能。

## 工具安装

由于该工具基于Python开发，因此我们首先要在本地设备上安装并配置好Python环境以及pip工具。

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sashs/Ropper.git

使用PyPi安装[ _Capstone_](http://www.capstone-engine.org/)：

    
    
    $ sudo pip install capstone

使用PyPi安装[ _filebytes_](https://github.com/sashs/filebytes)：

    
    
    $ sudo pip install filebytes

使用PyPi安装[ _Keystone_](http://www.keystone-engine.org/)：

    
    
    $ sudo pip install keystone-engine

接下来，运行工具安装脚本并执行Ropper即可：

    
    
    $ python setup.py install
    
    $ ropper

除此之外，我们也可以直接使用pip来安装Ropper：

    
    
    $ pip install ropper

当然了，如果你不想安装的话，也可以直接执行Ropper脚本文件：

    
    
    $ ./Ropper.py

## 当前可能的限制

    
    
    reg == reg     -  分配寄存器给寄存器
    
    reg == number  -  分配数字给寄存器
    
    reg == [reg]   -  分配内存给寄存器
    
    reg += number/reg/[reg]
    
    reg -= number/reg/[reg]
    
    reg *= number/reg/[reg]
    
    reg /= number/reg/[reg]

### 限制样例

    
    
    eax==1 !ebx    - set eax to 1 and look for gadgets which does not clobber ebx

![](https://image.3001.net/images/20230713/1689246103_64afd997479d6820afd96.png!small)

## 工具使用

    
    
    usage: Ropper.py [-h] [-v] [--console] [-f <file>] [-r] [-a <arch>]
    
                     [--section <section>] [--string [<string>]] [--hex]
    
                     [--asm <asm> [H|S|R] [<asm> [H|S|R] ...]] [--disasm <opcode>]
    
                     [--disassemble-address <address:length>] [-i] [-e]
    
                     [--imagebase] [-c] [-s] [-S] [--imports] [--symbols]
    
                     [--set <option>] [--unset <option>] [-I <imagebase>] [-p]
    
                     [-j <reg>] [--stack-pivot] [--inst-count <n bytes>]
    
                     [--search <regex>] [--quality <quality>] [--opcode <opcode>]
    
                     [--instructions <instructions>] [--type <type>] [--detailed]
    
                     [--all] [--cfg-only] [--chain <generator>] [-b <badbytes>]
    
                     [--nocolor] [--clear-cache]
    
     
    
    You can use ropper to display information about binary files in different file formats
    
        and you can search for gadgets to build rop chains for different architectures
    
     
    
    supported filetypes:
    
      ELF
    
      PE
    
      Mach-O
    
      Raw
    
     
    
    supported architectures:
    
      x86 [x86]
    
      x86_64 [x86_64]
    
      MIPS [MIPS, MIPS64]
    
      ARM/Thumb [ARM, ARMTHUMB]
    
      ARM64 [ARM64]
    
      PowerPC [PPC, PPC64]
    
      SPARC [SPARC64]
    
     
    
    available rop chain generators:
    
      execve (execve[=<cmd>], default /bin/sh) [Linux x86, x86_64]
    
      mprotect  (mprotect=<address>:<size>) [Linux x86, x86_64]
    
      virtualprotect (virtualprotect=<address iat vp>:<size>) [Windows x86]
    
     
    
    optional arguments:
    
      -h, --help             show this help message and exit
    
      -v, --version         Print version
    
      --console             Starts interactive commandline
    
      -f <file>, --file <file>
    
                            The file to load
    
      -r, --raw             Loads the file as raw file
    
      -a <arch>, --arch <arch>
    
                            The architecture of the loaded file
    
      --section <section>   The data of the this section should be printed
    
      --string [<string>]   Looks for the string <string> in all data sections
    
      --hex                 Prints the selected sections in a hex format
    
      --asm <asm> [H|S|R] [<asm> [H|S|R] ...]
    
                            A string to assemble and a format of the output
    
                            (H=HEX, S=STRING, R=RAW, default: H)
    
      --disasm <opcode>     Opcode to disassemble (e.g. ffe4, 89c8c3, ...)
    
      --disassemble-address <address:length>
    
                            Disassembles instruction at address <address>
    
                            (0x12345678:L3). The count of instructions to
    
                            disassemble can be specified (0x....:L...)
    
      -i, --info            Shows file header [ELF/PE/Mach-O]
    
      -e                    Shows EntryPoint
    
      --imagebase           Shows ImageBase [ELF/PE/Mach-O]
    
      -c, --dllcharacteristics
    
                            Shows DllCharacteristics [PE]
    
      -s, --sections        Shows file sections [ELF/PE/Mach-O]
    
      -S, --segments        Shows file segments [ELF/Mach-O]
    
      --imports             Shows imports [ELF/PE]
    
      --symbols             Shows symbols [ELF]
    
      --set <option>        Sets options. Available options: aslr nx
    
      --unset <option>      Unsets options. Available options: aslr nx
    
      -I <imagebase>        Uses this imagebase for gadgets
    
      -p, --ppr             Searches for 'pop reg; pop reg; ret' instructions
    
                            [only x86/x86_64]
    
      -j <reg>, --jmp <reg>
    
                            Searches for 'jmp reg' instructions (-j reg[,reg...])
    
                            [only x86/x86_64]
    
      --stack-pivot         Prints all stack pivot gadgets
    
      --inst-count <n bytes>
    
                            Specifies the max count of instructions in a gadget
    
                            (default: 6)
    
      --search <regex>      Searches for gadgets
    
      --quality <quality>   The quality for gadgets which are found by search (1 =
    
                            best)
    
      --opcode <opcode>     Searches for opcodes (e.g. ffe4 or ffe? or ff??)
    
      --instructions <instructions>
    
                            Searches for instructions (e.g. "jmp esp", "pop eax;
    
                            ret")
    
      --type <type>         Sets the type of gadgets [rop, jop, sys, all]
    
                            (default: all)
    
      --detailed            Prints gadgets more detailed
    
      --all                 Does not remove duplicate gadgets
    
      --cfg-only            Filters out gadgets which fail the Microsoft CFG
    
                            check. Only for PE files which are compiled with CFG
    
                            check enabled (check DllCharachteristics) [PE]
    
      --chain <generator>   Generates a ropchain [generator parameter=value[
    
                            parameter=value]]
    
      -b <badbytes>, --badbytes <badbytes>
    
                            Set bytes which should not contains in gadgets
    
      --nocolor             Disables colored output
    
      --clear-cache         Clears the cache

## 工具使用样例

### 常用方法

    
    
    ./Ropper.py
    
      ./Ropper.py --file /bin/ls --console

### 信息收集

    
    
    ./Ropper.py --file /bin/ls --info
    
      ./Ropper.py --file /bin/ls --imports
    
      ./Ropper.py --file /bin/ls --sections
    
      ./Ropper.py --file /bin/ls --segments
    
      ./Ropper.py --file /bin/ls --set nx
    
      ./Ropper.py --file /bin/ls --unset nx
    
      ./Ropper.py --file /bin/ls --inst-count 5
    
      ./Ropper.py --file /bin/ls --search "sub eax" --badbytes 000a0d
    
      ./Ropper.py --file /bin/ls --search "sub eax" --detail
    
      ./Ropper.py --file /bin/ls --filter "sub eax"
    
      ./Ropper.py --file /bin/ls --inst-count 5 --filter "sub eax"
    
      ./Ropper.py --file /bin/ls --opcode ffe4
    
      ./Ropper.py --file /bin/ls --opcode ffe?
    
      ./Ropper.py --file /bin/ls --opcode ??e4
    
      ./Ropper.py --file /bin/ls --detailed
    
      ./Ropper.py --file /bin/ls --ppr --nocolor
    
      ./Ropper.py --file /bin/ls --jmp esp,eax
    
      ./Ropper.py --file /bin/ls --type jop
    
      ./Ropper.py --file /bin/ls --chain execve
    
      ./Ropper.py --file /bin/ls --chain "execve cmd=/bin/sh" --badbytes 000a0d
    
      ./Ropper.py --file /bin/ls --chain "mprotect address=0xbfdff000 size=0x21000"
    
      ./Ropper.py --file /bin/ls /lib/libc.so.6 --console

### 汇编/反汇编

    
    
    ./Ropper.py --asm "jmp esp"
    
      ./Ropper.py --asm "mov eax, ecx; ret"
    
      ./Ropper.py --disasm ffe4

### 数据搜索

    
    
    ./Ropper.py --file /bin/ls --search "mov e?x"
    
      0x000067f1: mov edx, dword ptr [ebp + 0x14]; mov dword ptr [esp], edx; call eax
    
      0x00006d03: mov eax, esi; pop ebx; pop esi; pop edi; pop ebp; ret ;
    
      0x00006d6f: mov ebx, esi; mov esi, dword ptr [esp + 0x18]; add esp, 0x1c; ret ;
    
      0x000076f8: mov eax, dword ptr [eax]; mov byte ptr [eax + edx], 0; add esp, 0x18; pop ebx; ret ;
    
     
    
      ./Ropper.py --file /bin/ls --search "mov [%], edx"
    
      0x000067ed: mov dword ptr [esp + 4], edx; mov edx, dword ptr [ebp + 0x14]; mov dword ptr [esp], edx; call eax;
    
      0x00006f4e: mov dword ptr [ecx + 0x14], edx; add esp, 0x2c; pop ebx; pop esi; pop edi; pop ebp; ret ;
    
      0x000084b8: mov dword ptr [eax], edx; ret ;
    
      0x00008d9b: mov dword ptr [eax], edx; add esp, 0x18; pop ebx; ret ;
    
     
    
      ./Ropper.py --file /bin/ls --search "mov [%], edx" --quality 1
    
      0x000084b8: mov dword ptr [eax], edx; ret ;; ret ;

## 在脚本中使用Ropper

    
    
    #!/usr/bin/env python
    
    from ropper import RopperService
    
     
    
    # not all options need to be given
    
    options = {'color' : False,     # if gadgets are printed, use colored output: default: False
    
                'badbytes': '00',   # bad bytes which should not be in addresses or ropchains; default: ''
    
                'all' : False,      # Show all gadgets, this means to not remove double gadgets; default: False
    
                'inst_count' : 6,   # Number of instructions in a gadget; default: 6
    
                'type' : 'all',     # rop, jop, sys, all; default: all
    
                'detailed' : False} # if gadgets are printed, use detailed output; default: False
    
     
    
    rs = RopperService(options)
    
     
    
    ##### change options ######
    
    rs.options.color = True
    
    rs.options.badbytes = '00'
    
    rs.options.badbytes = ''
    
    rs.options.all = True
    
     
    
     
    
    ##### open binaries ######
    
    # it is possible to open multiple files
    
    rs.addFile('test-binaries/ls-x86')
    
    rs.addFile('ls', bytes=open('test-binaries/ls-x86','rb').read()) # other possiblity
    
    rs.addFile('ls_raw', bytes=open('test-binaries/ls-x86','rb').read(), raw=True, arch='x86')
    
     
    
    ##### close binaries ######
    
    rs.removeFile('ls')
    
    rs.removeFile('ls_raw')
    
     
    
     
    
    # Set architecture of a binary, so it is possible to look for gadgets for a different architecture
    
    # It is useful for ARM if you want to look for ARM gadgets or Thumb gadgets
    
    # Or if you opened a raw file
    
    ls = 'test-binaries/ls-x86'
    
    rs.setArchitectureFor(name=ls, arch='x86')
    
    rs.setArchitectureFor(name=ls, arch='x86_64')
    
    rs.setArchitectureFor(name=ls, arch='ARM')
    
    rs.setArchitectureFor(name=ls, arch='ARMTHUMB')
    
    rs.setArchitectureFor(name=ls, arch='ARM64')
    
    rs.setArchitectureFor(name=ls, arch='MIPS')
    
    rs.setArchitectureFor(name=ls, arch='MIPS64')
    
    rs.setArchitectureFor(name=ls, arch='PPC')
    
    rs.setArchitectureFor(name=ls, arch='PPC64')
    
    rs.setArchitectureFor(name=ls, arch='SPARC64')
    
    rs.setArchitectureFor(name=ls, arch='x86')
    
     
    
     
    
    ##### load gadgets ######
    
     
    
    # load gadgets for all opened files
    
    rs.loadGadgetsFor()
    
     
    
    # load gadgets for only one opened file
    
    ls = 'test-binaries/ls-x86'
    
    rs.loadGadgetsFor(name=ls)
    
     
    
    # change gadget type
    
    rs.options.type = 'jop'
    
    rs.loadGadgetsFor()
    
     
    
    rs.options.type = 'rop'
    
    rs.loadGadgetsFor()
    
     
    
    # change instruction count
    
    rs.options.inst_count = 10
    
    rs.loadGadgetsFor()
    
     
    
    ##### print gadgets #######
    
    rs.printGadgetsFor() # print all gadgets
    
    rs.printGadgetsFor(name=ls)
    
     
    
    ##### Get gadgets ######
    
    gadgets = rs.getFileFor(name=ls).gadgets
    
     
    
     
    
    ##### search pop pop ret ######
    
    pprs = rs.searchPopPopRet(name=ls) # looks for ppr only in 'test-binaries/ls-x86'
    
    pprs = rs.searchPopPopRet()        # looks for ppr in all opened files
    
    for file, ppr in pprs.items():
    
        for p in ppr:
    
            print p
    
     
    
    ##### load jmp reg ######
    
    jmp_regs = rs.searchJmpReg(name=ls, regs=['esp', 'eax']) # looks for jmp reg only in 'test-binaries/ls-x86'
    
    jmp_regs = rs.searchJmpReg(regs=['esp', 'eax'])
    
    jmp_regs = rs.searchJmpReg()                             # looks for jmp esp in all opened files
    
    for file, jmp_reg in jmp_regs.items():
    
        for j in jmp_reg:
    
            print j
    
     
    
     
    
    ##### search opcode ######
    
    ls = 'test-binaries/ls-x86'
    
    gadgets_dict = rs.searchOpcode(opcode='ffe4', name=ls)
    
    gadgets_dict = rs.searchOpcode(opcode='ffe?')
    
    gadgets_dict = rs.searchOpcode(opcode='??e4')
    
     
    
    for file, gadgets in gadgets_dict.items():
    
        for g in gadgets:
    
            print g
    
     
    
    ##### search instructions ######
    
    ls = 'test-binaries/ls-x86'
    
    for file, gadget in rs.search(search='mov e?x', name=ls):
    
        print file, gadget
    
     
    
    for file, gadget in rs.search(search='mov [e?x%]'):
    
        print file, gadget    
    
     
    
    result_dict = rs.searchdict(search='mov eax')
    
    for file, gadgets in result_dict.items():
    
        print file
    
        for gadget in gadgets:
    
            print gadget
    
     
    
    ##### assemble instructions ######
    
    hex_string = rs.asm('jmp esp')
    
    print '"jmp esp" assembled to hex string =', hex_string
    
    raw_bytes = rs.asm('jmp esp', format='raw')
    
    print '"jmp esp" assembled to raw bytes =', raw_bytes
    
    string = rs.asm('jmp esp', format='string')
    
    print '"jmp esp" assembled to string =',string
    
    arm_bytes = rs.asm('bx sp', arch='ARM')
    
    print '"bx sp" assembled to hex string =', arm_bytes
    
     
    
    ##### disassemble bytes #######
    
    arm_instructions = rs.disasm(arm_bytes, arch='ARM')
    
    print arm_bytes, 'disassembled to "%s"' % arm_instructions
    
     
    
    # Change the imagebase, this also change the imagebase for all loaded gadgets of this binary
    
    rs.setImageBaseFor(name=ls, imagebase=0x0)
    
     
    
    # reset image base
    
    rs.setImageBaseFor(name=ls, imagebase=None)
    
     
    
    gadgets = rs.getFileFor(name=ls).gadgets
    
     
    
    # gadget address
    
    print hex(gadgets[0].address)
    
     
    
    # get instruction bytes of gadget
    
    print bytes(gadgets[0].bytes).encode('hex')
    
     
    
    # remove all gadgets containing bad bytes in address
    
    rs.options.badbytes = '000a0d'  # gadgets are filtered automatically

## 工具运行截图

![](https://image.3001.net/images/20230713/1689246176_64afd9e03edc08d82ffd0.jpeg!small)

![](https://image.3001.net/images/20230713/1689246182_64afd9e6a48ac59c5eb18.jpeg!small)

![](https://image.3001.net/images/20230713/1689246189_64afd9ed8d84cf41648ad.jpeg!small)

![](https://image.3001.net/images/20230713/1689246195_64afd9f3d6e5463565ce1.jpeg!small)

![](https://image.3001.net/images/20230713/1689246203_64afd9fba32b6c34b53f5.jpeg!small)

![](https://image.3001.net/images/20230713/1689246209_64afda01a195b0c1b8850.jpeg!small)

![](https://image.3001.net/images/20230713/1689246215_64afda07a54bccc9c493a.jpeg!small)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/sashs/Ropper/blob/master/COPYING)开源许可证协议。

## 项目地址

 **Ropper** ：【[ _GitHub传送门_](https://github.com/sashs/ropper)】

## 参考资料

> [ _http://www.capstone-engine.org/_](http://www.capstone-engine.org/)
>
> [ _http://scoding.de/ropper_](http://scoding.de/ropper)

