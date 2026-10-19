# **TLS - Thread-Local Storage**

> 线程私有变量（`Thread Local Storage`）之于线程相当于静态变量之于进程

当程序运行时，函数的局部变量是在线程的栈上进行分配，虽然线程共享进程的虚拟地址空间，但因为每个线程有自己的线程栈，所以栈中的数据是互相隔离的，互不侵扰；

在一个进程中，所有线程是共享同一个地址空间的。所以，如果一个变量是全局的或者是静态的，那么所有线程访问的是同一份，如果某一个线程对其进行了修改，也就会影响到其他所有的线程。不过我们可能并不希望这样，所以更多的推荐用基于堆栈的自动变量或函数参数来访问数据，因为基于堆栈的变量总是和特定的线程相联系的

不过如果某些时候，我们就是需要依赖全局变量或者静态变量： **比如说对一个`global variable`进行累加的情况，为了避免`race
condition`的传统做法是使用`mutex`，但也可以使用`TLS`先在每个线程本地累加，然后再讲每个线程的累加结果同步到一个真正的`global
variable`之上**

然而有一种多线程下的编程方式，可以使得全局变量或静态变量只对单个线程可见，而对其它线程不可见，这就是`Thread Local
Storage`，又叫`线程本地存储`或`线程局部存储``TLS`的作用是能将数据和执行的特定的线程联系起来

`Thread local storage(TLS)`是线程独占的空间

线程本地存储(`TLS`)，对于线程来讲是一种对本地化使用静态或全局内存的计算机编程方法

##  **__thread**

可以使用`__thread`关键字告诉编译器某一个变量应当被放入线程局部存储的空间（`TLS`）中

`__thread`创建了本地存储的线程间全局变量，只要其他线程用它他会直接在自己的线程栈上创建该对象并保留其原有的值,不会干扰其他线程中的该值，可以在线程中将该值覆盖为其他值，但仅对当前进程有效

也就是说，`TLS`只能被当前线程访问和修改，使得其不能像一般的变量一样被简单的存储到`ELF`文件的某个段，而且`TLS`变量也与一般的变量不同

    
    
    #include <pthread.h>
    #include <stdio.h>
    
    __thread int a = 123;// 0x7b
    __thread unsigned long long b = 234;// 0xea
    __thread int c;
    
    // test 线程
    void test(void *func)
    {
        printf("in thread test: a = %d, b = %llu, c = %p\\n", a, b, &c);
        printf("in thread test: &a = %p, b = %p\\n", &a, &b);
    }
    
    // 主线程
    int main()
    {
        a = 345;// 0x159
        b = 456;// 0x1c8
        c = 567;// 0x237
        printf("in main thread: a = %d, b = %llu, c = %p\\n", a, b, &c);
        printf("in main thread: &a = %p, b = %p\\n", &a, &b);
        pthread_t pid;
        pthread_create(&pid, NULL, test, NULL);
        pthread_join(pid, NULL);
        return 0;
    }
    

结果

    
    
    in main thread: a = 345, b = 456, c = 0x7f5e4bf04738
    in main thread: &a = 0x7f5e4bf04728, b = 0x7f5e4bf04730
    
    in thread test: a = 123, b = 234, c = 0x7f5e4b7096f8
    in thread test: &a = 0x7f5e4b7096e8, b = 0x7f5e4b7096f0
    

（来源于知乎）

##  **查看 fs 寄存器中的值**

`Linux x64`使用`fs`段寄存器来存储`TLS`的位置

`Stack Canary`就是保存在`TLS`中

但在`GDB`调式程序通过`pwntools`插件提供的寄存器寄存器界面直接查看`fs`寄存器时，会发现其中的值为`0`，这是由于权限问题，用户态不能直接访问`fs`寄存器，但可以使用内核提供的系统调用`arch_prctl`获得`fs`寄存器中段选择子所指向的`Segment
base address`

    
    
    int arch_prctl(int code, unsigned long addr);
    int arch_prctl(int code, unsigned long *addr);
    

`arch_prctl`设置特定于体系结构的进程或线程状态

  * `code`选择一个子函数并将参数`addr`传递给它：
    * 对于`set`操作：`addr`被解释为`unsigned long`
    * 对于`get`操作：`addr`被解释为`unsigned long*`

`arch_prctl`只适用于`X86/X86-64`平台

其中`code`有如下几种：

  * `ARCH_SET_CPUID`
  * `ARCH_GET_CPUID`
  * `ARCH_SET_FS`设定 FS
  * `ARCH_GET_FS``0x1003`拿 FS
  * `ARCH_SET_GS`
  * `ARCH_GET_GS`

返回值

  * On success,`arch_prctl()`returns 0
  * on error, -1

则在`GDB`中`arch_prctl(0x1003,$rsp-8)`的含义就是将`fs`寄存器中的值拿出来放到`$rsp-8`这个栈空间中

在`GDB`中输入

    
    
    print (void)arch_prctl(0x1003,$rsp-8)
    x/xg $rsp-8 即可查看到 fs 中的值
    

之后在`fs + 0x28`的位置就能可能到`canary`的值

###  **举例**

随便拿来一段有`canary`的程序举例：

![1671633343_63a319bf43004b2bbc17f.png!small?1671633339305](https://image.3001.net/images/20221221/1671633343_63a319bf43004b2bbc17f.png!small?1671633339305)

  * 启动`gdb`打断点启动该程序后，随便执行几句后，查看 fs 寄存器中的值

![1671633349_63a319c5db6546ac86602.png!small?1671633346012](https://image.3001.net/images/20221221/1671633349_63a319c5db6546ac86602.png!small?1671633346012)

发现查看不到`fs`中的值

  * 将程序运行到将`canary`的值放入当前栈空间之前

![1671633354_63a319ca316daac30e4f7.png!small?1671633350339](https://image.3001.net/images/20221221/1671633354_63a319ca316daac30e4f7.png!small?1671633350339)

  * 此时`canary`存于`rax`中，查看得到当前的随机值为`0xaacf72bca3851000`

![1671633360_63a319d0511a14790d7f1.png!small?1671633356489](https://image.3001.net/images/20221221/1671633360_63a319d0511a14790d7f1.png!small?1671633356489)

  * 现在执行`arch_prctl`系统调用，将`fs`中`TLS`的地址放入`$rsp-8`栈空间中
    
        print (void)arch_prctl(0x1003,$rsp-8)
    

并查看这个值`x/xg $rsp-8`为`0x00007ffff7d80740`

![1671633364_63a319d4942059670e273.png!small?1671633360650](https://image.3001.net/images/20221221/1671633364_63a319d4942059670e273.png!small?1671633360650)

  * 再由之前的语句得知，`canary`的值是从`qword ptr fs:[0x28]`取到的，而当前知道了`fs`中保存着的`TLS`的地址，所以`$fs + 0x28`地址下的`8`字节数据应该就是这个`canary`值`0xaacf72bca3851000`

`x/xg 0x00007ffff7d80740 + 0x28`查看该值

![1671633367_63a319d7e4243a1a4639a.png!small?1671633364030](https://image.3001.net/images/20221221/1671633367_63a319d7e4243a1a4639a.png!small?1671633364030)

 **验证完毕**

