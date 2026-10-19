1.直接使用DIE对程序进行探测 发现是Microsoft Visual Basic 6.0 写的加载器

2.使用ProcessMom进行对程序探测 就发现查询了一次注册表 并发现是在虚拟机里面运行 就结束自身进程  
![image](https://image.3001.net/images/20210420/1618892124_607e555c0cf1a5c775ed6.png!small)

![image](https://image.3001.net/images/20210420/1618892135_607e5567c9462880d0eb6.png!small)

证实里面有检测虚拟机代码。

使用API Trace工具 进行API Trace

发现使用VirtualAlloc分配了内存空间 并将执行流 执行到新分配的内存空间 执行ShellCodo代码  
![image](https://image.3001.net/images/20210420/1618893464_607e5a98ab436af65f0ce.png!small)3.使用x64dbg
对VirtualAlloc进行下断点  
![image](https://image.3001.net/images/20210420/1618892609_607e57414e024309ee552.png!small)  
分析里面的调用参数得之 分配的内存大小是0x9000  
内存属性是PAGE_EXECUTE_READWRITE 读写执行

然后根据VirtualAlloc返回的内存地址 下硬件可执行断点 F9运行 确实到达了VirtualAlloc申请的内存空间  
根据堆栈回溯 定位到用户调用ShellCode代码的地方  
![image](https://image.3001.net/images/20210420/1618893070_607e590eb2c83e79e3ffa.png!small)

4.现在可以根据VirtualAlloc的返回参数 将ShellCode dump下来 然后使用IDA静态分析  
![image](https://image.3001.net/images/20210420/1618893248_607e59c0dfa90bc55d206.png!small)

Guloader ShellCode就提取出来了

