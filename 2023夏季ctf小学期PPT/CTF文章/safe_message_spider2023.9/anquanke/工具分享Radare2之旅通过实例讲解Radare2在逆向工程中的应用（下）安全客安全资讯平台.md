# 【工具分享】Radare 2之旅：通过实例讲解Radare 2在逆向工程中的应用（下）

阅读量 **245034**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-28 11:13:58

 **x**

##### 译文声明

本文是翻译文章，文章来源：megabeets.net

原文地址：<https://www.megabeets.net/a-journey-into-radare-2-part-1/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

  

译者：[ **Kp_sover**](http://bobao.360.cn/member/contribute?uid=2899451914)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**传送门**

[**【工具分享】Radare 2之旅——通过crackme实例讲解Radare
2在逆向工程中的应用（上）**](http://bobao.360.cn/learning/detail/4400.html)

**  
**

**前言**

好了，接着上一篇继续介绍 Radare 2 其他的功能。

  

**定位（Seeking）**

之前介绍过，r2分析完一个程序后会停留在入口点，现在是时候去其他地方看看了，刚刚看到我们所感兴趣的字符串都是在 'main'
这个函数里被调用的，因此我们用'seek' 命令跳转过去，在 r2 里，它的指令是 's' ,当然你仍然可以用在它后面添加 '?'
的方式来查看它所有可能的用法，根据你的需要选择吧：

    
    
    [0x08048370]> s?
    |Usage: s  # Seek commands
    | s                 Print current address
    | s addr            Seek to address
    | s-                Undo seek
    | s- n              Seek n bytes backward
    | s–                Seek blocksize bytes backward
    | s+                Redo seek
    | s+ n              Seek n bytes forward
    | s++               Seek blocksize bytes forward
    | s[j*=]            List undo seek history (JSON, =list, *r2)
    | s/ DATA           Search for next occurrence of ‘DATA’
    | s/x 9091          Search for next occurrence of x90x91
    | s.hexoff          Seek honoring a base from core->offset
    | sa [[+-]a] [asz]  Seek asz (or bsize) aligned to addr
    | sb                Seek aligned to bb start
    | sC[?] string      Seek to comment matching given string
    | sf                Seek to next function (f->addr+f->size)
    | sf function       Seek to address of specified function
    | sg/sG             Seek begin (sg) or end (sG) of section or file
    | sl[?] [+-]line    Seek to line
    | sn/sp             Seek next/prev scr.nkey
    | so [N]            Seek to N next opcode(s)
    | sr pc             Seek to register

seek 命令通常是接受一个地址或者数学表达式作为参数，这个表达式可以是操作指令、标志位、或者内存操作相关，现在我们想查找 main 函数，因此我们使用
's main' 指令就可以了，不过在这之前我们可以先看看 r2 到底为我们分析出了哪些函数，因此我们用 'afl'
指令，这个指令代表着分析函数列表（Analyze Functions List）.

    
    
    [0x08048370]> afl
    0x080482ec    3 35           sym._init
    0x08048320    1 6            sym.imp.strcmp
    0x08048330    1 6            sym.imp.strcpy
    0x08048340    1 6            sym.imp.puts
    0x08048350    1 6            sym.imp.__libc_start_main
    0x08048360    1 6            sub.__gmon_start___252_360
    0x08048370    1 33           entry0
    0x080483a0    1 4            sym.__x86.get_pc_thunk.bx
    0x080483b0    4 43           sym.deregister_tm_clones
    0x080483e0    4 53           sym.register_tm_clones
    0x08048420    3 30           sym.__do_global_dtors_aux
    0x08048440    4 43   -> 40   sym.frame_dummy
    0x0804846b   19 282          sym.rot13
    0x08048585    1 112          sym.beet
    0x080485f5    5 127          main
    0x08048680    4 93           sym.__libc_csu_init
    0x080486e0    1 2            sym.__libc_csu_fini
    0x080486e4    1 20           sym._fini

漂亮，在这里我们看到了之前看到过的导入函数，同时还有入口点，导入库，主函数和两个引起我们兴趣的函数：'sym.beet' 和 'sym.rot13'.

  

**反汇编（Disassembling）**

**主函数**

是时候去看看反汇编代码了，首先我们用 's main' 指令定位到main函数入口处，然后用 'pdf'（输出反汇编代码）

注意：就像我之前说过的，这系列文章的主要目的是去让大家了解并学习 r2
的，而不是去教大家如何阅读或者理解反汇编代码，所以在这里我不会刻意的去逐条解释每句代码的意思！事实上这些汇编代码只要有基础的汇编知识我相信都是很容易看懂的.

    
    
    [0x08048370]> s main
    [0x080485f5]> pdf
              ;– main:
    / (fcn) main 127
    |   main ();
    |           ; var int local_8h @ ebp-0x8
    |           ; var int local_4h @ esp+0x4
    |              ; DATA XREF from 0x08048387 (entry0)
    |           0x080485f5      8d4c2404       lea ecx, [esp + local_4h]   ; 0x4
    |           0x080485f9      83e4f0         and esp, 0xfffffff0
    |           0x080485fc      ff71fc         push dword [ecx – 4]
    |           0x080485ff      55             push ebp
    |           0x08048600      89e5           mov ebp, esp
    |           0x08048602      53             push ebx
    |           0x08048603      51             push ecx
    |           0x08048604      89cb           mov ebx, ecx
    |           0x08048606      83ec0c         sub esp, 0xc
    |           0x08048609      6800870408     push str._n__.::_Megabeets_::. ; str._n__.::_Megabeets_::.
    |           0x0804860e      e82dfdffff     call sym.imp.puts          ; int puts(const char *s)
    |           0x08048613      83c410         add esp, 0x10
    |           0x08048616      83ec0c         sub esp, 0xc
    |           0x08048619      6815870408     push str.Think_you_can_make_it_ ; “Think you can make it?” @ 0x8048715
    |           0x0804861e      e81dfdffff     call sym.imp.puts          ; int puts(const char *s)
    |           0x08048623      83c410         add esp, 0x10
    |           0x08048626      833b01         cmp dword [ebx], 1          ; [0x1:4]=0x1464c45
    |       ,=< 0x08048629      7e2a           jle 0x8048655
    |       |   0x0804862b      8b4304         mov eax, dword [ebx + 4]    ; [0x4:4]=0x10101
    |       |   0x0804862e      83c004         add eax, 4
    |       |   0x08048631      8b00           mov eax, dword [eax]
    |       |   0x08048633      83ec0c         sub esp, 0xc
    |       |   0x08048636      50             push eax
    |       |   0x08048637      e849ffffff     call sym.beet
    |       |   0x0804863c      83c410         add esp, 0x10
    |       |   0x0804863f      85c0           test eax, eax
    |      ,==< 0x08048641      7412           je 0x8048655
    |      ||   0x08048643      83ec0c         sub esp, 0xc
    |      ||   0x08048646      682c870408     push str.Success__n ; “Success!.” @ 0x804872c
    |      ||   0x0804864b      e8f0fcffff     call sym.imp.puts          ; int puts(const char *s)
    |      ||   0x08048650      83c410         add esp, 0x10
    |     ,===< 0x08048653      eb10           jmp 0x8048665
    |     |||      ; JMP XREF from 0x08048629 (main)
    |     |||      ; JMP XREF from 0x08048641 (main)
    |     |-> 0x08048655      83ec0c         sub esp, 0xc
    |     |     0x08048658      6836870408     push str.Nop__Wrong_argument._n ; “Nop, Wrong argument..” @ 0x8048736
    |     |     0x0804865d      e8defcffff     call sym.imp.puts          ; int puts(const char *s)
    |     |     0x08048662      83c410         add esp, 0x10
    |     |        ; JMP XREF from 0x08048653 (main)
    |     `—> 0x08048665      b800000000     mov eax, 0
    |           0x0804866a      8d65f8         lea esp, [ebp – local_8h]
    |           0x0804866d      59             pop ecx
    |           0x0804866e      5b             pop ebx
    |           0x0804866f      5d             pop ebp
    |           0x08048670      8d61fc         lea esp, [ecx – 4]
               0x08048673      c3             ret

这些汇编代码大致的意思可以通过下面这个c 代码来解释：

    
    
    if (argc > 1 && beet(argv[1]) == true) 
    # i.e - if any argument passed to the program AND the result of beet, given the passed argument, is true
    # argc is the number of arguments passed to the program
    # argc will be at least 1 becuase the first argument is the program name
    # argv is the aray of parameters passed to the program
    {
        print "success"
    }
    else
    { 
         print "fail"
    } 
    exit

  

**视图模式 & 图形模式（Visual Mode & Graph Mode）**

radare2 具有非常强和高效率的组件用来提供十分友好的视图模式，这也将 r2 的强大带入到了一个新的高度.按 V 键将开启视图模式，按 p/P
可以在不同的模式之间切换，在屏幕的顶部就是你输入的命令，这里使用 p 命令先切换回之前的反编译模式.

视图模式下基本的命令：

**移动**

你可以使用 k 和 j 来 上下移动，按回车键将在 call 和 jmp
的时候跳转到目的地址，同时上图里你能看到有一些方括号里面有数字，你可以直接在键盘上按相应的数字就会跳转到对应的函数和地址处 ！

**帮助**

在使用 r2 的任何阶段，你都可以按 ?来调出帮助画面，这能帮助你更好的使用 r2 .

**交叉引用**

x / X 可以列出当前函数的引用状况，之后再输入相应的数字就可以跳转到指定的引用处了.

  

**radare2 命令解释器**

使用 :command 命令来执行你想要的 r2 命令.

**注释**

通过 ;[-] 来添加相应的注释

**标记**

m<key> 可以用来标记特定的偏移地址，之后输入对应的key就可以跳转到你设置的地方.

**退出**

按 q 返回到 r2 的 shell操作界面.

**可视图形模式**  

在反汇编中经常会用到的就是 图形视图， r2也提供了这个功能，你可以在 shell 里输入 VV来进入图形模式, h / j / k / l 分别表示 左
/ 下 / 上 / 右 ,输入 g来跳转到你想去的函数地址.  

使用 '?' 可以列出所有可用的命令，提醒下 R 命令挺不错.

  

**反汇编 'beet' 函数**

现在回到 beet 函数上，我们之前看到，二进制程序是通过获取 beet函数的返回结果来判断是否正确，因此我们需要输入 beet
的返回结果，这里有下面几种方式:

0x1、在 r2 的shell 界面搜索 beet 函数并打印出它的反汇编代码：因为 sym.beet 是beet 函数的标志,因此使用 f
sym.<tab> 来定位出 sym.beet 函数，最后使用 pdf 来输出它的具体内容.

0x2、直接输出 beet 的代码：通过 pdf @ sym.beet 命令，'@' 表示临时查找.

0x3、在可视视图界面直接跳转到 beet 函数：记得上面说过的方框中的数字吗？这里直接按 3 就可以了  

0x4、在图形界面下输入 gd 命令，d 就是每一个跳转或者调用代码旁边的 字母.  

这就是 r2 图形模式大致的样子：

我们看到输入的参数被拷贝到了一个缓存空间里，这个空间的地址是 ‘ebp – local_88h’ 。 'local_88h' 就是十进制的
136，我们可以输入 :之后再输入 ? 0x88 来执行 r2 内置的命令.

    
    
    :> ? 0x88
    136 0x88 0210 136 0000:0088 136 “x88” 10001000 136.0 136.000000f 136.000000

由于4个字节会被用来保存 ebp 的地址，4个字节被用来保存返回地址，所以这个缓冲区得大小是 128个字节.它们加起来刚好是 136.  

我们输入的参数被拷贝到缓冲区后被用来和 sym.rot13的返回结果作对比， Rot-13
是一个著名的替换密码算法，在ctf和crackme中被广泛使用，这个函数接受了9个十六进制值作为参数，看起来r2好像没有识别出来到底是什么字符，这里我们需要用
'ahi s' 来做些处理.

    
    
    :> ahi s @@=0x080485a3 0x080485ad 0x080485b7

ahi s 是用来设置字符串特定的偏移地址（使用 ahi?
获取更多用法），@@是一个迭代器，可以用来接受后面输入的多个参数,执行完这条命令后，图形视图会自动刷新，如果没有，可以手动输入 r 来刷新。

漂亮，我们已经看到了之前无法识别的字符串'Megabeets'(根据字节序反向压栈顺序得到).  

这个二进制文件将我们传入的参数来和经过 rot13 处理后的 'Megabeets' 作比较，幸运的是我们不用去辛苦的分析 rot13 的具体算法，因为
r2 的 rahash2 组件可以代替我们做这些事情.  

rahash2 包含很多种算法来求证一个文件或者字符串的校验值,具体的用法请使用 'man rahash2 '.

    
    
    :> !rahash2 -E rot -S s:13 -s ‘Megabeetsn’
    Zrtnorrgf

rahash2 通过内置的算法 处理 'Megabeets' 后得到 'Zrtnorrgf' 这个字符串，我们可以在 r2 的shell 视图中输入 !
命令来执行 系统命令，假设 'Zrtnorrgf' 就是用来和我们输入的字符串作比较，那我们重新在调试模式下打开二进制文件，使用 'ood' 命令将
'Zrtnorrgf'作为参数（更多用法使用 ood? ） ，现在看看我们得到了什么：

    
    
    [0xf7749be9]> ood?
    | ood [args]    reopen in debugger mode (with args)
    [0xf7749be9]> ood Zrtnorrgf
    Wait event received by different pid 7415
    Wait event received by different pid 7444
    Process with PID 7575 started…
    File dbg:///home/remnux/Desktop/tutorials/megabeets_0x1 Zrtnorrgf reopened in read-write mode
    = attach 7575 7575
    Assuming filepath /home/remnux/Desktop/tutorials/megabeets_0x1
    [0xf7749be9]> dc
    Selecting and continuing: 7575.:: Megabeets ::.
    Think you can make it?
    Success!PTRACE_EVENT_EXIT pid=7575, status=0x0

Woohoo! 消息提示我们成功破解了这个 crackme，回顾这个过程，大致就是这个二进制文件会将我们输入的参数来和 经过 rot13 算法加密后得到的
“Zrtnorrgf” 字符串作对比.  

你可以在这里获取到这个二进制的源码 [here](https://github.com/ITAYC0HEN/A-journey-into-Radare2/blob/master/Part%201%20-%20Simple%20crackme/megabeets_0x1.c).

**结语**

有关 radare2 教程系列的第一篇文章，到现在就算结束了，我们其实只是最浅显的了解了 r2 的用法和最基础的功能，在下一篇文章中，我们将学到有关 r2
的脚本处理、恶意软件分析、以及溢出相关.我很担心这对于大多数人来说是十分困难的知识，我觉得你们应该先正确的认识 r2
的强大，然后反问自己为什么还要保留以前的那些工具的使用习惯？是否有必要做出些改变，这样也许会让你更加坚定的去学习和使用 r2
，相信我，如果你是一个逆向工程师、ctf 选手、甚至仅仅是安全爱好者，我都建议你将 r2 添加进你的新的工具箱，它会给你带来惊喜！

本文翻译自megabeets.net [原文链接](https://www.megabeets.net/a-journey-into-radare-2-part-1/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Kp_sover** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86943](/post/id/86943)

安全客 - 有思想的安全新媒体

本文转载自: [megabeets.net](https://www.megabeets.net/a-journey-into-radare-2-part-1/)

如若转载,请注明出处： <https://www.megabeets.net/a-journey-into-radare-2-part-1/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) Kp_sover

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

