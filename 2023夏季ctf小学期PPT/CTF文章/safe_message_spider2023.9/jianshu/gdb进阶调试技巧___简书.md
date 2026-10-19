gdb进阶调试技巧

[ DayDayUpppppp](https://www.jianshu.com/u/8530ab416e50)关注赞赏支持

# gdb进阶调试技巧

整理一下在linux下C/C++用gdb工具debug一些提高效率的操作。基本的gdb操作就不在这里赘述了。

  * 打印各种变量  
x 命令  
在gdb中可以使用x命令，来打印内存中的值。具体的格式是x/nfu addr。 含义为以f格式打印从addr开始的n个长度单元为u的内存值。

    1. n表示打印的n个u的长度
    2. f 表示打印格式，u，d表示10进制的无符号和有符号数; x表示16进制；t表示二进制
    3. u表示单元长度，b表示一个byte，w表示4个byte
    
        int main()
    {
      int val = 0xa;
      
      char buff[1024];
      memset(buff, 0, sizeof(1024));
    
      char name[]="hello world";
      strcpy(buff, name);
      
      int arr[10] = {0};
      arr[0] = 0xa;
      arr[1] = 10;
      arr[2] = 20;
    
      return 0;
    }
    
    (gdb) x/16db &arr
    0x7fffffffe010:   10  0   0   0   10  0   0   0
    0x7fffffffe018:   20  0   0   0   0   0   0   0
    
    (gdb) x/16sb &buff
    0x7fffffffe050:    "hello world"
    0x7fffffffe05c:    "\177"
    0x7fffffffe05f:    ""
    0x7fffffffe060:    "<纵?\177"
    0x7fffffffe067:    ""
    0x7fffffffe068:    "X\227\177"
    0x7fffffffe06f:    ""
    0x7fffffffe070:    "\020暂?\177"
    0x7fffffffe077:    ""
    0x7fffffffe078:    ""
    0x7fffffffe079:    ""
    0x7fffffffe07a:    ""
    0x7fffffffe07b:    ""
    0x7fffffffe07c:    "\001"
    0x7fffffffe07e:    ""
    0x7fffffffe07f:    ""
    

* * *

  * 日志打印到某个文件 
    
        set pagination off
    set logging file a.log
    set logging overwrite
    set logging on
    

* * *

  * -tui 图形界面选项  
gdb a.out -tui # gdb tui 启动  
gdb attach pid -tui # gdb tui attach

  

* * *

  * gdb定义函数  
在开发中有时会遇到需要看一个很大的数组，里面有没有被写坏的元素。如果数组中还有嵌套其他结构体，每个依次打印出来非常麻烦。 **这里可以使用gdbinit**
，定义一个函数，依次遍历数组，打印超过某个值的元素。比如：

    
        const int MAX_LEN = 1024;
    
    struct DEBUG_DETAIL_INFO{
      int id;
      int extra_info;
    };
    
    struct DEBUG_ARR{
      int num;
      DEBUG_DETAIL_INFO info_arr[MAX_LEN];
    };
    
    int main()
    {
      DEBUG_ARR arr;
      init_arr(100, arr);
      
      // todo
      return 0;
    }
    

gdb调用函数有两种方式：

  1. gdb启动时，会在当前目录下查找 .gdbinit 文件
  2. gdb在运行时，在命令行输入 source xx.gdb文件 来加载

gdb启动的时候， **会在当前目录或home目录自动加载gdbinit脚本** 。在脚本中定义gdb函数。(或者gdb attach上去。)

    
    
    define print_if_my_arr
      printf "argc %d, arg %d \n", $argc, $arg0
    
      set $num = arr.num
      printf "print_func num %d \n", $num
    
      set $idx = 0
      while $idx < $num
          if arr.info_arr[$idx].id >= $arg0
              printf "idx %d id %d \n", $idx, arr.info_arr[$idx].id
          end
          set $idx = $idx + 1
      end
    end
    
    document print_if_my_arr
      example : print_if_my_arr 10
      desc    : print DEBUG_ARR ele if val >= 10
    end
    

gdb实测一把

gdbinit文件同理也可以插入其他命令，比如各种让输出比较直观的命令等：

    
    
    set print pretty on
    set print object on
    

gdb定义的常用函数可以放到一个文件里面，需要的时候通过source命令加载。

    
    
    define mybt
        set logging file output_bt.log
        set logging on
        bt
        set logging off
    end
    

使用的时候

    
    
    gdb attach xxxx
    source xxx/path/xxx.gdb
    mybt
    

* * *

  * gdb 条件断点 
    
        # 文件名 + 行号的条件断点
    b xxx.cpp:20 if value == 100   #xx.cpp 行号20 如果value == 100 触发断点
    
    # 包含一些简单计算的断点
    (gdb) p 100
    $2 = 100
    (gdb) b test1.cpp:8 if i + $2 == 130
    

* * *

  * ignore 命令  
断点触发被忽略xx次  
ignore <break_list> count  

* * *

  * command命令  
command <break_list>  

触发断点后自动执行command里面定义的命令

command的命令另一个妙用

* * *

  * gdb return  
进入某个函数执行，不想执行里面的逻辑，直接gdb return 出去。里面的逻辑就不会执行了。

* * *

  * gdb gcore  
gcore命令可以从当前环境导出成为一个core文件，供日后分析。

  

* * *

  * handle SIGPIPE nostop  
为了gdb不被信号断开，可以屏蔽掉各种pipe信号。

* * *

  * gdb -ex 参数  
生产环境操作的时候可以使用

    
        gdb -ex "bt" -batch -p pid
    

跳出死循环

* * *

  * display 命令  

对于debug需要关注的变量名，可以使用display打印出来。每次gdb操作的时候，都会显示出来。示意图如下：

* * *

  * info命令 
    
        info sharedlibrary  #显示共享库
    (gdb) info sharedlibrary 
    From                To                  Syms Read   Shared Object Library
    0x00007ffff7dd5050  0x00007ffff7df4854  Yes (*)     /lib64/ld-linux-x86-64.so.2
    0x00007ffff7aceb60  0x00007ffff7b84bb2  Yes (*)     /lib64/libstdc++.so.6
    0x00007ffff76c9510  0x00007ffff77687ca  Yes (*)     /lib64/libm.so.6
    0x00007ffff74a7dc0  0x00007ffff74b8a25  Yes (*)     /lib64/libgcc_s.so.1
    0x00007ffff7104900  0x00007ffff724ef0f  Yes (*)     /lib64/libc.so.6
    

* * *

  * gdb调用函数 
    
        void func() {  xxx; }
    
    b func
    call func()  // gdb 直接调用这个函数
    

gdb调用class的成员函数

    
        // todo
    

* * *

  * strip命令 （这个和gdb关系不大）  
strip命令可以极大的降低可执行文件的体积，其实就是去掉符号表和调试信息等。当gdb的时候，拷贝strip下来的.debug文件到需要gdb的机器上，然后进行gdb
attach。这里gdb上来以后，会自动找到对应的.debug文件。

    
         cd xxxx_app_bin_path
     objcopy --only-keep-debug xxxx_app ./.debug/xxxx.debug
     strip --strip-debug --strip-unneeded xxxx_app
     objcopy --add-gnu-debuglink=./.debug/xxxx_app.debug xxxx_app
    

* * *

###### GDB的基本原理

gdb有两种跟踪进程的方法，第一种是gdb +
a.out的方式启动进程，第二种的方式是gdb去attach一个已经启动了的进程。这种方式都是利用ptrace系统调用去跟踪被调试的进程。

    
    
    ptrace共有四个参数：
    long ptrace(enum __ptrace_request request,pid_t pid,void *addr,void *data);
    
    // 两种gdb的区别在于参数不同
    PTRACE_TRACEME 和 PTRACE_ATTACH
    

`ptrace系统函数`是Linux内核提供的一个用于进程跟踪的系统调用，通过它，一个进程(gdb)可以读写另外一个进程(test)的指令空间、数据空间、堆栈和寄存器的值。而且gdb进程接管了test进程的所有信号，也就是说系统向test进程发送的所有信号，都被gdb进程接收到，这样一来，test进程的执行就被gdb控制了，从而达到调试的目的。

也就是说，如果没有gdb调试，操作系统与目标进程之间是直接交互的；如果使用gdb来调试程序，那么操作系统发送给目标进程的信号就会被gdb截获，gdb根据信号的属性来决定：在继续运行目标程序时是否把当前截获的信号转交给目标程序，如此一来，目标程序就在gdb发来的信号指挥下进行相应的动作。

第一种方式是通过gdb去fork一个子进程，子进程去执行被调试的进程。然后建立父子关系。如下图所示：

第二种方式是gdb去attach被调试的子进程。如果想对一个已经执行的进程B进行调试，那么就要在gdb这个父进程中调用ptrace(PTRACE_ATTACH,[其他参数])，此时，gdb进程会attach(绑定)到已经执行的进程B，gdb把进程B收养成为自己的子进程，而子进程B的行为等同于它进行了一次
PTRACE_TRACEME操作。此时gdb进程会发送SIGSTO信号给子进程B，子进程B接收到SIGSTOP信号后，就会暂停执行进入TASK_STOPED状态，表示自己准备好被调试了。

  

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [GDB 常见使用介绍](https://www.jianshu.com/p/e6af28e2566f)

官方文档 http://sourceware.org/gdb/current/onlinedocs/gdb/[ht...

[wayyyy](https://www.jianshu.com/u/46663e457260)阅读 11,390评论 0赞 3

  * [借助gdb调试glibc代码学习House of Orange](https://www.jianshu.com/p/57a5c9a492aa)

1．准备工作 学习了CTF比赛中的一种堆利用方法—house of orange，看了很多师傅们的博客和一些国外网...

[静析机言](https://www.jianshu.com/u/fd954951a7f2)阅读 355评论 0赞 0

  * [浅谈LLDB调试器](https://www.jianshu.com/p/6c069de83810)

［转］浅谈LLDB调试器文章来源于：http://www.cocoachina.com/ios/20150126/...

[loveobjc](https://www.jianshu.com/u/195c47531281)阅读 2,268评论 2赞 6

  * [用gdb & strace追踪 jdk OOM bug](https://www.jianshu.com/p/35055c1bbe46)

现象 java应用的web服务器突然挂掉，无任何jvm相关日志，重启后不久再次挂掉 再次重启，不久后机器挂掉【机器...

[军哥ye话](https://www.jianshu.com/u/564ef1976e12)阅读 4,562评论 0赞 5

  * [翻译： iOS调试（iOS Debugging Magic）](https://www.jianshu.com/p/8d06df24c378)

iOS包含许多“秘密”调试工具，包括环境变量、偏好、GCB的常规调用，等等。本技术说明描述了这些工具。如果你开发i...

[栗子烤肉](https://www.jianshu.com/u/b5e6b79c1109)阅读 2,787评论 1赞 7

 