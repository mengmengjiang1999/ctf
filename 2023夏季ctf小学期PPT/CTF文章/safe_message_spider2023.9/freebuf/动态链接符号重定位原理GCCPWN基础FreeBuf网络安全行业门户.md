# 动态链接介绍

之前所说的静态链接有诸多优化的地方（但并不意味着静态链接无人使用，在某些情况下还是要使用静态链接的）比如说：

>  **过分浪费磁盘与内存的空间**
>
>  **无法进行动态的更新**

为了解决上述的问题，使用动态链接。

## 动态链接要解决的问题

所有动态链接，就是 **将链接的过程推迟到运行时进行**

静态链接得到的可执行程序，被操作系统加载后便可执行，因为如上篇文章所述，在链接的时候就已经将所有目标文件中的代码、数据等Section合并到可执行文件中了。在这个过程中还会将目标文件中所使用的外部符号（变量、函数等）全部进行了重定位，指向了其在虚拟地址中的位置，所以可执行程序执行的时候无需依赖外部模块就可运行（所需要的”外部模块”都已经合并到可执行文件中了），总结一下：
**对于静态链接，在链接阶段，符号重定位过程中会直接对可执行文件中需要重定位的符号进行修改完成重定位。**

但这种事情到了动态链接就不那么容易完成了，由于动态链接要将链接的过程推迟到运行时，也就是说运行过程中：
**当前可执行文件与所依赖的动态链接库被加载进内存后，调用可执行程序的入口函数前，才会对可执行文件中引用的外部符号进行重定位（也就是将这些符号在动态链接库中的虚拟地址填到对应调用的位置）**

此时就会产生一个很关键的问题：

 **代码段是不可写的！！**

原因就不用解释了，若代码段可写将毫无安全性可言，而且会扰乱代码的执行逻辑（早期出现过代码段可写的机制）

所以想像静态重定位那样， **直接修改代码中对应调用外部函数/变量的位置的地址是绝对不可能的！**

所以如何解决这个问题，就是 **动态链接的核心**

## 动态链接的核心

Butler Lampson 曾说过这样一句话：

Every problem in computer science can be solved by **adding another level of
indirection**

计算机科学中的所有问题都可以通过增加另一层来间接解决

虽然代码段在加载后是不可写的，但哪个地方是可写的呢？

 **数据段！**

虽然无法直接改写代码段中外部变量/函数的实际地址，但我们可以
**将外部变量/函数的实际地址放到数据段的某个位置中，让代码段先引用数据段中的内容，重定位时直接修改这个数据段中保存的地址到外部变量/函数的虚拟地址即可完成重定位，就完成了动态链接**

而这个思路就是实现动态链接的最优思路，他有另一个名称：

 **地址无关代码** （`PIC, Position-independent Code`）也就是 GCC 会默认加上的选项`-fPIC`

此时使用到的共享库在虚拟内存中仅存一份，若使用到了共享库中的数据则会复制到各自的进程中

但这种思路会有安全问题的产生：既然数据段存放了可执行文件中要执行函数重定位后的实际虚拟地址，数据段又有 写
权限，这就意味着通过一些手段（比如说溢出）我们也可以覆盖其地址达到定位到其他函数的目的，比如若可执行文件本身调用了一个`libc`中的函数，通过修改这个地址，就有可能定位并使用`libc`中的另一个函数
system 达到出弹`shell`的目的

### 另一种实现动态链接的方式

地址无关代码无疑是最优的动态链接解决方案，但若只使用`-shared`选项 而没有开启`-fPIC`则使用了另一种动态链接的方式： **装载时重定位**

共享对象也就是动态链接库在被装载到物理内存后，始终是只有一份的，不管有多少个进程使用它。但是对于每一个进程，共享对象会映射一次到虚拟地址空间，也就是每个进程空间都有一份共享对象的映射，但是，对于不同的进程，映射的地址（基址）是不一样的（大部分情况下），
**所以在装载时将动态链接库映射到每一个进程中时，是需要根据该进程空间的地址修改物理内存中动态库中的指令中的地址（比如说跳转指令或是变量的访问等）**

所以这就产生了缺点： **没有办法做到同一份指令被多个进程共享**

# 实验观察

## 一些可能会用到的函数

  * `dlopen()`
  * `dlsym()`
  * `dlerror()`
  * `dlclose()`

### `dlopen()`

用于打开一个共享对象（动态库）将其加载进进程空间中，完成初始化

`void *dlopen(const char *filename, int flags);`

  * `const char *filename`要打开动态库的路径

If filename is NULL, then the returned handle is for the main program.

若文件名为空，返回该进程的全局符号表

**如果`filename`是`0`,那么`dlopen`会返回全局符号表的句柄，我们可以在运行时找到全局符号表里的任何符号，并可执行他们**。全局符号表包含了程序的可执行文件本身，被动态链接器加载到进程中的所有共享模块已经在运行时通过`dlopen`打开并使用`RTLD_GLOBAL`方式的模块中的符号。

  * `const char *filename`函数符号的解析方式

    * `RTLD_LAZY`延迟绑定（具体内容会在后面说，现在简单说一下）

当函数第一次被用到时才由动态链接器进行绑定（符号查找，重定位等），没用到的不绑定。这提高了程序的启动速度

    * `RTLD_NOW` **当模块被加载时完成所有的函数绑定工作** ，如果有任何未定义的符号引用的绑定工作没法完成，那么`dlopen()`就返回错误

上述选项 二选一

 **RETURN VALUE**

最终返回值返回一个动态库的指针

On success,`dlopen()`return a non-NULL handle for the loaded object. On error
(file could not be found, was not readable, had the wrong format, or caused
errors during loading), these functions return NULL

### `dlsym()`

使用该函数从通过`dlopen()`打开动态库获得的句柄（`handle`）中找到指定的符号

`void *dlsym(void *handle, const char *symbol);`

  * `void *handle`动态库句柄
  * `const char *symbol`要查找符号

 **RETURN VALUE** On success, these functions return the address associated
with symbol. On failure, they return NULL; the cause of the error can be
diagnosed using dlerror(3).

成功返回查找符号的地址，失败返回`NULL`

### `dlerror()`

判断上一次调用是否成功

`char *dlerror(void);`

每次调用`dlopen()`、`dlsym()`或`dlclose()`以后，都可以调用`dlerror()`函数来判断上一次调用是否成功。`dlerror()`的返回值类型是`char*`，如果返回`NULL`，则表示上一次调用成功；如果不是，则返回相应的错误消息

### `dlclose()`

关闭一个动态库，将一个已经加载的模块卸载

`int dlclose(void *handle);`

## 实验代码

当前代码关系：

  * `b.c → libb.so`
  * `a.c → liba.so`
  * `main.c → main`

`liba.so`依赖于`libb.so`

`main.c`与`liba.so libb.so`一起动态链接为`main`

![1667805063_6368af87f09e9df312b1a.png!small?1667805063994](https://image.3001.net/images/20221107/1667805063_6368af87f09e9df312b1a.png!small?1667805063994)

    
    
    gcc -m32 -fPIC -shared b.c -o libb.so
    gcc -m32 -fPIC -shared a.c -o liba.so ./libb.so
    sudo ldconfig  + 当前动态库路径
    gcc -m32 -fPIC main.c -o main ./liba.so libb.so
    # 或 gcc -m32 -fPIC main.c -L. liba.so libb.so -o main
    

`b.c`

    
    
    #include <stdio.h>
    
    int g_nVarB = 30;
    
    void fnB(void)
    {       
            printf("Processing in function B --- nVarB = %d \\n",g_nVarB);
    }       
    

`a.c`

    
    
    #include <stdio.h>
    
    // 内部静态变量
    static int s_nVarA1 = 10;
    
    // 声明全局变量
    int g_nVarA2 = 20;
    
    // 声明外部变量 g_nVarB
    extern int g_nVarB;
    
    // 声明外部函数 fnB
    extern void fnB(void);
    
    static void s_fnA2(void)
    {
            printf("Processing in function A2 \\n");
    }
    
    void fnA3(void)
    {
            printf("Processing in function A3 \\n");
    }
    
    void fnA1(void)
    {
            printf("Processing in function A1 \\n");
    
    				// 修改内部静态变量
            s_nVarA1 = 11;
    
    				// 非静态全局变量
            g_nVarA2 = 20;
    
    				// // 修改外部全局变量
            g_nVarB = 31;
    
    				// 调用内部静态函数
            s_fnA2();
    
    				// 调用内部函数
            fnA3();
    
    				// 调用外部函数
            fnB();
    
    }
    

`main.c`

该程序非常之庞大，看着可能有些费劲，其作用有如下几条：

  * 通过`dlopen`返回本进程全局符号表的句柄，并通过`dlsym`定位其中的符号
  * 定位`liba.so`中导入到`main`中的符号（若未导入则会输出`get address failed`）
  * 定位`libb.so`中导入到`main`中的符号（若未导入则会输出`get address failed`）

若存在，则会打印输出其起始地址

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <dlfcn.h>
    #include <stdlib.h>
    
    extern int g_nVarA2;
    extern void fnA1();
    
    typedef void (*pFunc)(void);
    
    int main(int argc,char** argv)
    {
    
            printf("Processing in main function \\n");
    
            // 打印进程全局符号表
            void *handle = dlopen(0,RTLD_NOW);
            if ( handle == NULL)
            {
                    dlerror("dlopen()");
                   // exit(1);
            }
    
            printf("---------------------------- main funcation ------------------------------ \\n");
    
            // 打印 main 中变量符号的地址
            pFunc addr_main = dlsym(handle,"main");
            if (addr_main == NULL)
            {
                   // dlrror("dlsym():main");
                    fprintf(stderr,"get address of main failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("main function address is : 0x%x \\n",(unsigned int)addr_main);
            }
    
    				// liba.so 中相关符号的虚拟地址
            printf("------------------------------ liba.a ------------------------------------ \\n");
    
            unsigned int *addr_s_nVarA1 = dlsym(handle,"s_nVarA1");
            if (addr_s_nVarA1 == NULL)
            {
                   // dlrror("dlsym():liba.so:s_nVarA1");
                    fprintf(stderr,"get address of s_nVarA1 failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("liba.so:s_nVarA1 address is : 0x%x \\n",addr_s_nVarA1);
    
            }
    
            unsigned int *addr_g_nVarA2 = dlsym(handle,"g_nVarA2");
            if (addr_g_nVarA2 == NULL)
            {
                   // dlerror("dlsym():liba.so:g_nVarA2");
                    fprintf(stderr,"get address of g_nVarA2 failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("liba.so:g_nVarA2 address is : 0x%x \\n",addr_g_nVarA2);
    
            }
    
            pFunc addr_fnA1 = dlsym(handle,"fnA1");
            if (addr_fnA1 == NULL)
            {
                   // dlerror("dlsym():liba.so:fnA1");
                    fprintf(stderr,"get address of fnA1 failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("liba.so:fnA1 function address is : 0x%x \\n",(unsigned int)addr_fnA1);
    
            }
    
            pFunc addr_s_fnA2 = dlsym(handle,"s_fnA2");
            if (addr_s_fnA2 == NULL)
            {
                   // dlerror("dlsym():liba.so:s_fnA2");
                    fprintf(stderr,"get address of s_fnA2 failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("liba.so:s_fnA2 function address is : 0x%x \\n",(unsigned int)addr_s_fnA2);
    
            }
    
            pFunc addr_fnA3 = dlsym(handle,"fnA3");
            if (addr_fnA3 == NULL)
            {
                   // dlerror("dlsym():liba.so:fnA3");
                    fprintf(stderr,"get address of fnA3 failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("liba.so:fnA3 function address is : 0x%x \\n",(unsigned int)addr_fnA3);
    
            }
    
    			  // libb.so 中相关符号的虚拟地址
            printf("---------------------------------- libb.so --------------------------------- \\n");
    
            unsigned int *addr_g_nVarB = dlsym(handle,"g_nVarB");
            if (addr_g_nVarB == NULL)
            {
               // dlerror("dlsym():libb.so:g_nVarB");
                fprintf(stderr,"get address of g_nVarB failed!\\n");
    
            }
            else
            {
                printf("libb.so:g_nVarB address is : 0x%x \\n",addr_g_nVarB);
            }
    
            pFunc addr_fnB = dlsym(handle,"fnB");
            if (addr_fnB == NULL)
            {
                   // dlerror("dlsym():libb.so:fnB");
                    fprintf(stderr,"get address of fnB failed!\\n");
                   // exit(1);
            }
            else
            {
                    printf("libb.so:fnB function address is : 0x%x \\n",(unsigned int)addr_fnB);
            }
    
            dlclose(handle);
    
    				// 对位于 liba 动态库的全局变量进行赋值
            g_nVarA2 = 100;
    
    				// 调用 liba 中的参数
            fnA1();
    
    				// 挂起程序防止程序退出，便于观察
            while(1)
            {
                sleep(5);
            }
    
            return 0;
    }
    

# 动态库的加载过程

## 观察动态库之间的依赖关系

根据最开始的依赖关系图可以看出`main`程序与`liba.so`与`libb.so`的依赖关系：

`main`依赖于`liba.so`

`liba.so`依赖于`libb.so`

可以使用`ldd``patchelf`这两个命令来观察其依赖关系

`ldd`

![1667805085_6368af9d342a06be6ff5e.png!small?1667805085311](https://image.3001.net/images/20221107/1667805085_6368af9d342a06be6ff5e.png!small?1667805085311)

`patchelf`

![1667805098_6368afaa6ecfadf8d597b.png!small?1667805098470](https://image.3001.net/images/20221107/1667805098_6368afaa6ecfadf8d597b.png!small?1667805098470)

## 1：动态库的自举

> 动态链接器负责在执行程序时对其依赖的对动态库进行加载

在执行`main`时，操作系统会首先将`main`加载到内存中，然后根据`.interp`段的信息来获得 **动态链接器** 的路径

`.interp`段的内容很简单，其中保存了一个字符串， **这个字符串就是可执行文件所需要的动态链接器的路径**

通过`objdump`查看该段的内容

`objdump -s main`

![1667805106_6368afb27e675ba6a4aca.png!small?1667805106604](https://image.3001.net/images/20221107/1667805106_6368afb27e675ba6a4aca.png!small?1667805106604)

可以获得动态链接器的路径为`/lib/ld-linux.so.2`

![1667805111_6368afb7334c18af6be79.png!small?1667805111353](https://image.3001.net/images/20221107/1667805111_6368afb7334c18af6be79.png!small?1667805111353)

可以看到
**动态链接器本身也是一个动态链接库（共享对象`Glibc`的一部分），但特殊的地方在于动态链接器不依赖于任何动态库**，否则当他加载的时候没有人为他来加载，并且
**动态链接器本身所要的全局和静态变量的重定位工作必须由它本身完成** ，所以这项自我重定位的代码必须在动态链接器启动时来完成，这个过程往往被称为
**自举** （`Bootstrap`），所以动态链接库的入口地址就是自举代码的开始处

![1667805115_6368afbb5eed54585533b.png!small?1667805115477](https://image.3001.net/images/20221107/1667805115_6368afbb5eed54585533b.png!small?1667805115477)

 **动态链接器本身是静态链接的**

![1667805119_6368afbf1b36ee7d21db0.png!small?1667805119147](https://image.3001.net/images/20221107/1667805119_6368afbf1b36ee7d21db0.png!small?1667805119147)

  * 所以执行`main`时，会首先将 动态链接器 映射到`main`进程的虚拟地址空间中

下面这段话在全文看完后回看会更容易理解

此时动态链接器会先执行自举代码：首先定位自己的`GOT`表，`GOT`表中的第一个入口就是`.dynamic`短偏移地址，通过该段中的信息自举代码便可以获得动态链接器本身的重定位表和符号表等，从而得到动态链接器本身的重定位入口，先将它们全部重定位。从这一步开始，动态链接器代码中才可以开始使用自己的全局变量和静态变量

  * 完成基本自举后， **动态链接器将`main`和 链接器本身的符号表合并到一个符号表中，也就是 全局符号表**

  * 随后链接器便开始寻找可执行文件所依赖的共享对象，在`.dynamic`段中有一种入口为`DT_NEEDED`指出是当前可执行文件所依赖的共享对象

  * 由此，链接器可以列出`main`所需要的所有共享对象，并将这些共享对象的名字放入到一个装载集合中

    * `liba.so`
    * `libc.so.6`
  * 然后链接器开始从集合里取一个所需要的共享对象的名字，找到相应的文件后打开该文件，读取相应的`ELF`文件头和`.dynamic`段，然后将它相应的代码段和数据段映射到进程空间中

  * 如果这个`ELF`共享对象还依赖于其他共享对象，那么将所依赖的共享对象的名字放到装载集合中。如此循环直到所有依赖的共享对象都被装载进来为止

    * `libb.so`(`liba.so`依赖 )

 **执行`main`后有两种方式可以观察其虚拟地址空间**

`cat /proc/PID/maps`

![1667805128_6368afc898a0ec25ec0d6.png!small?1667805130692](https://image.3001.net/images/20221107/1667805128_6368afc898a0ec25ec0d6.png!small?1667805130692)

`pmmp PID`

![1667805135_6368afcf74935876ed4bc.png!small?1667805135629](https://image.3001.net/images/20221107/1667805135_6368afcf74935876ed4bc.png!small?1667805135629)

###  **全局符号表 与 .dynamic 表**

>
> 在静态链接的过程中，链接器在第一遍扫描的时候会将每一个目标文件中的符号提取出来生成全局符号表，并在第二次扫描的时候查看每个目标文件中需要重定位的符号，在全局符号表中确认其位置并把这个地址填到引用的地方

而由于动态链接的特性，所以每个符号在运行时才能知道其具体地址，所以这个 **生成全局符号表的责任交给了动态链接器**

而我们`main`进程的功能就是通过`dlopen`于`dlsym`打印输出`main`进程全局符号表中相关符号的地址信息，先来看其执行结果

![1667805140_6368afd4e51f64394bae4.png!small?1667805141086](https://image.3001.net/images/20221107/1667805140_6368afd4e51f64394bae4.png!small?1667805141086)

可以看到定义的`s`开头（静态变量）的无论是变量还是函数在`main`的全局符号表中都找不到其地址，而其他的都正常，这是为什么？

在回答这个问题之前先说两个表`.dynamic`和`.symtab`

`.symtab`并不陌生，就是符号表，也就是模块中的所有符号

`.dynamic`就是所说的 **动态符号表** ，动态符号表中记录着模块中符号的导出和导入关系，是`.symtab`的一个子集

所以对于一个动态链接库，
**只有在动态符号表中的符号才会被导出，而由于`static`类型的特性，所以被其修饰的符号并不会放到动态链接表中**，这也就解释了为什么在`main`的全局符号表中找不到`liba.so`和`libb.so`中的`static`符号

`liba.so`的符号表与动态符号表

![1667805146_6368afda3cf413132ef9c.png!small?1667805146458](https://image.3001.net/images/20221107/1667805146_6368afda3cf413132ef9c.png!small?1667805146458)

`libb.so`的动态符号表

![1667805156_6368afe4b1c1f9a126542.png!small?1667805156749](https://image.3001.net/images/20221107/1667805156_6368afe4b1c1f9a126542.png!small?1667805156749)

`main.so`的动态符号表

![1667805160_6368afe873ecafa3c2982.png!small?1667805160813](https://image.3001.net/images/20221107/1667805160_6368afe873ecafa3c2982.png!small?1667805160813)

 **执行完以上过程链接器就要进行我们最关注的重定位与初始化的过程了**

## 2： **重定位与初始化**

执行完以上过程后，链接器会再次
**重新遍历可执行文件和每个共享对象的重定位表（`.rel.`），将它们的`GOT/PLT`中的每个需要重定位的位置进行修正**

由于`liba.so`具有更多的依赖与被依赖关系，所以接下来对关键的几个表的观察以`liba.so`为例

### 重定位表 .rel.

动态链接中会通过两个重定位表来告诉链接器哪些符号需要重定位：

  * `.rel.dyn`对 **数据** 引用的修正（它所修正的位置位于`GOT`表（`.got`）中以及数据段）
  * `.rel.plt`对 **函数** 引用的修正（它所修正的位置位于`GOT`表（`.got.plt`））

通过指令`readef -r liba.so`来观察 **重定位表**

![1667805171_6368aff3ed07fe28148e5.png!small?1667805172052](https://image.3001.net/images/20221107/1667805171_6368aff3ed07fe28148e5.png!small?1667805172052)

其中对于 **重定位入口** 的类型有两种分别为：

  * `R_386_GLOB_DAT`
  * `R_386_JUMP_SLOT`

这两种类型表示 **被修正的位置只需要直接填入`GOT`表中的地址即可**

### 全局偏移表 GOT

前面说过在执行程序过程中执行重定位会通过增加一个中间层来实现运行时重定位的功能，那么这个 **中间层就由
全局偏移表`GOT`来实现：比如说如上所示`liba.so`中会引用`libb.so`中的全局变量`g_nVarB`,所以在`liba.so`代码段中，会将引用`g_nVarB`的位置处`g_nVarB`的地址改为`GOT`表的地址（`GOT`对应表项的地址），这样只需在重定位时将其地址放入位于数据段的`GOT`表中即可**

### 动态链接库中的 GOT 表

动态链接库中存在两个`GOT`表：

  * 重定位 **变量** 符号`.got`
  * 重定位 **函数** 符号`.got.plt`

![1667805182_6368affe265393d507909.png!small?1667805182370](https://image.3001.net/images/20221107/1667805182_6368affe265393d507909.png!small?1667805182370)

从图中可以看到`.got`与`.got.plt`的大小均为`24`字节，说明每个里面都有`6`个表项（每个表现占 4 字节）

且可以从`Off`一项看到：

  * `.got`距离文件头的偏移为`0x002fe8`
  * `.got.plt`距离文件头的偏移位`0x003000`

再从加载器的角度来看看`.got`表 与`.got.plt`表的位置又在哪里捏？

![1667805200_6368b010901a52d2d63c0.png!small?1667805200687](https://image.3001.net/images/20221107/1667805200_6368b010901a52d2d63c0.png!small?1667805200687)

还要注意一个点，可以看出第一个段起始的`VirtAddr`（虚拟地址）为`0x00000000`，这是因为开启了位置无关代码参数（`-fPIC`），当`liba.so`的代码段和数据段被加载进内存时，动态链接器会随即找到一块空闲空间，将这块空间的起始地址作为`liba.so`的虚拟起始基地址，然后以`VirtAddr`作为其偏移地址即可

可以看到其第`4`个`LOAD`段的起始地址正是`0x003ef8`也就是`.init_array`的虚拟地址（非最终的虚拟地址，最终的虚拟地址需要在运行时加上基地址）

而根据`Section Headers`中可以算出，`.init_array`与`.got`之间的偏移为`0x2fe8 - 0x2ef8 = 0xf0`

再用`0xf0 + 0x003ef8`=`0x3fe8`这也就是`.got`的起始地址

`0x3ef8 + 18 = 0x4000`这也就是`.plt.got`的起始地址

当然这算来算去起始并没有什么意思，直接从`Section headers`中就可以获取该`Addr`

### 重定位表与GOT表的关系

细心可能会发现重定位表中要重定位符号的偏移地址正好与`.got`和`.plt.got`表中的表项重合，这也正验证了一开始所说的，因为动态链接中将要重定位的符号的地址都指向了`GOT`表某条表项，
**所以动态链接器只需要对`GOT`表中对应偏移的表项进行重定位**

其中 GOT 表的前三项为三个公共表项，这三个表项的作用分别为：

  1. `got[0]`本ELF动态段(`.dynamic`段)的装载地址
  2. `got[1]`本ELF的`link_map`数据结构描述符地址（本模块的ID）
  3. `got[2]``_dl_runtime_resolve`函数的地址

## [liba.so](http://liba.so)的反汇编代码

### <__x86.get_pc_thunk.bx> 的作用

![1667805211_6368b01bf2acb22f6420c.png!small?1667805212005](https://image.3001.net/images/20221107/1667805211_6368b01bf2acb22f6420c.png!small?1667805212005)

 **用于获取调用该函数的函数体中，下一条指令的地址**

由于调用该函数的函数在`call 1080
<__x86.get_pc_thunk.bx>`时，会将下一条指令的地址入栈用于返回，所以该指令直接将栈顶指针`esp`所指向的这个地址保存在`ebx`中

⚠️ 注意：只有`32`位环境下会这么来获取下一条指令的地址，因为`32`位环境下是不支持直接访问`eip`寄存器的，`64`位环境下就可以了

### 一个奇怪的 section`.plt.got`

> 注意注意这可不是`.got.plt`！！！！！！！不重要，可跳过

![1667805219_6368b023144ddead986f3.png!small?1667805219135](https://image.3001.net/images/20221107/1667805219_6368b023144ddead986f3.png!small?1667805219135)

a program (written with C++ in Linux) calls `__cxa_finalize`when exiting the
main function

[__cxa_finalize and
**attribute**](https://stackoverflow.com/questions/10634767/cxa-finalize-and-attribute)

gcc already provides destructors, which will be called by __cxa_finalize.

__cxa_finalize is called on library unload (either when a program is exiting
or by a dlopen)

[atexit, __cxa_atexit and __cxa_finalize
interaction](https://sourceware.org/pipermail/libc-alpha/2019-June/103977.html)

### <fnA1> 分析

![1667805224_6368b0286df6233675af8.png!small?1667805224634](https://image.3001.net/images/20221107/1667805224_6368b0286df6233675af8.png!small?1667805224634)

为了方便将其源代码再贴一份

    
    
    void fnA1(void)
    {
            printf("Processing in function A1 \\n");
    
    				// 修改内部静态变量
            s_nVarA1 = 11;
    
    				// 非静态全局变量
            g_nVarA2 = 20;
    
    				// // 修改外部全局变量
            g_nVarB = 31;
    
    				// 调用内部静态函数
            s_fnA2();
    
    				// 调用内部函数
            fnA3();
    
    				// 调用外部函数
            fnB();
    }
    

首先来看`11da`处的两行代码

    
    
    1128:       e8 53 ff ff ff          call   1080 <__x86.get_pc_thunk.bx>
    112d:       81 c3 d3 2e 00 00       add    ebx,0x2ed3
    

  * `call 1080 <__x86.get_pc_thunk.bx>`将`112d`放入`ebx`中
  * `add ebx,0x2ed3``ebx = ebx + 0x2ed3 = 0x112d + 0x2ed3 = 0x4000`

这个`0x4000`也就是`.plt.got`的偏移地址

⚠️ 在实际程序执行加载该动态库时，通过`call`获得的就是虚拟地址，通过`+ 0x2ed3`这个偏移，就可以成功算出实际`.plt.got`的虚拟地址

可以看到之后的对于重定位表中变量的操作都是借助`ebx`来进行（位处于重定位表中的变量在确认其偏移位置时也会借助`ebx`的值，因为`.data`段就在`.got.plt`之后）

但函数的调用却借用了一个另外的`Section``.plt`

![1667805233_6368b0310bc464a75f9d2.png!small?1667805233193](https://image.3001.net/images/20221107/1667805233_6368b0310bc464a75f9d2.png!small?1667805233193)

关于`.plt`就要提到另外一个功能 **延迟绑定（`PLT`)**

## 延迟绑定（PLT）

由于动态链接下对于全局数据的访问和跨模块的调用都要进行复杂的`GOT`定位，然后间接寻址或调用，导致程序的运行速度减慢大概1%~%5。又因为动态链接的链接工作在运行时完成，导致程序的启动速度减慢。

**程序运行过程中，会有很多函数没有用到（错误处理函数，没有使用的功能模块等），所以没有必要一开始就把所有函数都链接好，`ELF`采用延迟绑定的方法，基本思想是当函数第一次被用到时才由动态链接器进行绑定（符号查找，重定位等），没用到的不绑定**。这提高了程序的启动速度

### 如何实现 延迟绑定

`ELF`通过`PLT`（`Procedure Linking Table`） 来实现延迟绑定

在Glibc中，动态链接器完成绑定工作的函数叫`_dl_runtime_resolve()`，它必须知道绑定发生在哪个模块中的哪个函数，因此假设其函数原型为`_dl_runtime_resolve(module,
function)`
**当调用某个外部模块的函数时，并不直接通过`GOT`跳转，而是通过一个叫作`PLT`项的结构来进行跳转，每个外部函数在`PLT`中都有一个相应的项**

![1667805238_6368b036bba5587aa4760.png!small?1667805238881](https://image.3001.net/images/20221107/1667805238_6368b036bba5587aa4760.png!small?1667805238881)

### `<fnA3@plt>`为例

    
    
    001050 <fnA3@plt>:
        1050:       ff a3 10 00 00 00       jmp    DWORD PTR [ebx+0x10]
        1056:       68 08 00 00 00          push   0x8
        105b:       e9 d0 ff ff ff          jmp    1030 <_init+0x30>
    

为了实现延迟绑定，链接器在初始化阶段并没有将`fnA3()`的地址填入到`[ebx+0x10]`对应的`GOT`表项中，而是将`push
0x8`的地址填入到`[ebx+0x10]`对应的`GOT`表项中，这个步骤不需要查找任何符号，所以代价很低。很明显，第一条指令的效果是跳转到第二条指令，相当于没有进行任何操作

第二条指令`push 0x8`将一个`0x8`压入堆栈中，这个数字是`fnA3`这个符号引用在重定位表`.rel.plt`中的下标

然后`jmp 1030
<_init+0x30>`跳转到`_dl_runtime_resolve`这实际上就是在实现`_dl_runtime_resolve`函数调用，它在进行一系列符号解析和重定位工作以后将`fnA3()`的真正地址填入到`[ebx+0x10]`对应的`GOT`表项中

之后当我们再次调用`<fnA3@plt>`时，第一条`jmp`指令就能够跳转到真正的`fnA3()`函数中

