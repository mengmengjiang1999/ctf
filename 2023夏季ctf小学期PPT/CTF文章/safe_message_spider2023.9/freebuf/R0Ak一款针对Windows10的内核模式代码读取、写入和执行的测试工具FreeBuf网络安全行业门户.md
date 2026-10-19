**对于研究人员来说，今天介绍的这款工具就相当于他们的“瑞士军刀”，因为这款名叫R0ak的命令行工具可以帮助研究人员在Windows
10操作系统上读取、写入和执行任意代码，用于进一步测试。**

![R0Ak：一款针对Windows
10的内核模式代码读取、写入和执行的测试工具](https://image.3001.net/images/20180915/1537002354_5b9ccb729c2d1.png!small)

## r0ak

r0ak是一款Windows平台下的命令行工具，它可以帮助我们在命令行界面下轻松读取、写入和执行内核模式代码，而且除了管理员权限之外，不需要其他额外的东西。

## 快速使用

> r0akv1.0.0 -- Ring 0 Army Knife
>
> <http://www.github.com/ionescu007/r0ak>
>
> Copyright(c) 2018 Alex Ionescu [@aionescu]
>
> [http://www.windows-internals.com](http://www.windows-internals.com/)
    
    
    USAGE:r0ak.exe
    
           [--execute <Address |module.ext!function> <Argument>]
    
           [--write   <Address | module.ext!function><Value>]
    
           [--read    <Address | module.ext!function><Size>]

![R0Ak：一款针对Windows
10的内核模式代码读取、写入和执行的测试工具](https://image.3001.net/images/20180915/1537002365_5b9ccb7d7b962.png!small)

### 基础架构：

![R0Ak：一款针对Windows
10的内核模式代码读取、写入和执行的测试工具](https://image.3001.net/images/20180915/1537002375_5b9ccb87a3695.png!small)

## 支持的命令

> 在使用--execute选项时，这个功能和参数由用户提供。
>
> 在使用--write时，需要使用一个自定义小公举来修改内核内存中任意位置的32字节值。
>
> 在使用--read时，需要使用一个写入小公举来修改系统中HSTI缓冲区指针和大小。

接下来，需要使用HSTI查询API来将数据重新拷贝至工具的用户模式地址空间内。

## 工具使用

由于工具需要使用到Windows符号引擎，所以我们需要安装Windows软件开发套件（SDK）或Windows驱动套件（WDK），以及Windows调试工具。工具安装完成后会自动查询安装路径，并使用目录中的DbgHelp.dll和SymSrv.dll，由于这些文件是无法多次使用的，因此工具中无法内置这些文件。

或者说，如果你想使用你自己的代码库，你也可以修改工具的源代码。

在使用符号时，需要联网，除非你在本地预先缓存好数据。除此之外，你还需要设置_NT_SYMBOL_PATH变量，并指向正确的符号服务器和缓存地址。

## 工具限制

本工具需要使用正确的Windows
10内核变量以及函数功能，并且只能在64位操作系统上使用。虽然在x86架构的操作系统上没有这些限制，但是这种平台有很多传统的方法可以使用，因此这款工具主要针对的是64位的的Windows
10。

### 限制条件：

> 1\. 读取：一次只能读取4GB数据；
>
> 2\. 写入：一次只能写入32位长度的数据；
>
> 3\. 执行：函数的执行只能接收1个标量参数；

很明显，我们可以利用其它的编程手段或方法来绕过这些限制。需要注意的是，所有的命令执行（包括读取和写入命令）都需要在一个系统Worker线程（PASSIVE_LEVEL）环境下运行，因此用户模式地址不应该以参数进行传递。

***参考来源：[r0ak](https://github.com/ionescu007/r0ak)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

