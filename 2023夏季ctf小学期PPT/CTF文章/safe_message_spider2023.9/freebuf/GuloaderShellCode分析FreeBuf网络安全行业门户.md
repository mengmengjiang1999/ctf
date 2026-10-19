根据上一张追踪的流程 可以分析ShellCode部分  
这一节分析对ShellCode第一部分 反虚拟机进行关键部分分析

 **具体流程如下:**

通过fs:[0x30]PEB 找到Kernel32.dll模块 ---> 根据Kernle32.dll模块 找到LoadLibraryA函数 --->
通过LoadLibraryA加载ntdll.dll模块  
\--->通过ntdll.dll模块 然后获取到NtQueryVirtualMemory函数 --->通过调用NtQueryVirtualMemory
获取自身内存 然后对内存里面的数值 进行算法运算 得到一个特征码--->比较压入堆栈的特征码 如果比较成功证明在虚拟机环境中运行 否者就是 在真实物理机运行

堆栈里面压入的是虚拟机特征码  
![image](https://image.3001.net/images/20210423/1619178830_6082b54edfac357ebeaa7.png!small)

获取到NtQueryVirtualMemory函数  
![image](https://image.3001.net/images/20210424/1619234506_60838eca1ff29936d47b7.png!small)

调用NtQueryVirtualMemory函数 从0x10000开始检查 内存地址  
![image](https://image.3001.net/images/20210423/1619179807_6082b91fcda7f055de6d1.png!small)

看看关键位置  
![image](https://image.3001.net/images/20210424/1619233887_60838c5f9e554e678001b.png!small)

将这里条件改为无条件 就能绕过反虚拟机

其实里面获取 ntdll.dll模块 获取函数 都是通过一个函数加密模块名/函数名 达到静态分析 肉眼不能直接看出。。。

