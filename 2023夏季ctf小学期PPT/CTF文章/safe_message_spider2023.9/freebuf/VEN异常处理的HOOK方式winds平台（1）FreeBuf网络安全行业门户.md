![](https://image.3001.net/images/20211221/1640080776_61c1a5888775fe0b887ca.png!small)

**作者** | 榴莲

 **编辑** | Racel

Windows操作系统中存在多种异常处理，我们现在需要的是其中的VEH（VectoredExceptionHandler）异常处理，也就是向量化异常处理。我们之所以可以使用VEH异常来进行HOOK的主要原因，在于两点。其一，VEH异常处理的优先级是高于SEH异常处理的，也就是说可以先手拿到异常，确保不会被其他异常处理流程将异常截获而导致HOOK失败。其二就是在VEH异常处理的回调函数中，可以获取及修改异常发生处的上下文环境，这就意味着我们可以操作的东西会非常多，例如通过上下文环境中的ESP（栈顶指针寄存器）就可以拿到HOOK位置触发异常时的堆栈数据。而我们设置的HOOK位置通常位于函数内部的起始位置，这就意味着我们可以直接通过堆栈里的数据获取到被HOOK函数的参数,并且可以对其进行修改。

首先，我们既然需要HOOK，那么我们大概率需要一个将代码写到一个DLL（动态链接库）中，然后通过注入的方式加载到目标进程的体内。我这里采用的操作系统是Windows
10 20H2（19042.1288），集成开发环境采用的是Visual Studio 2017。那么我们先来创建一个DLL项目。

01

选择新建项目

![](https://image.3001.net/images/20211221/1640080693_61c1a535d3ae83f98af15.jpeg!small)

02

选择Windows桌面->动态链接库（DLL），点击确定

![](https://image.3001.net/images/20211221/1640080984_61c1a658ccb26f3fd17fa.png!small)

03

注释#include “pch.h”,添加#include 。删除framework.h、pch.h以及pch.cpp文件。

![](https://image.3001.net/images/20211221/1640081020_61c1a67c9db47a3f65284.png!small)

04

配置

4.1
选择属性![](https://image.3001.net/images/20211221/1640081048_61c1a698d064f87b30869.png!small)

4.2 修改运行库以及Spectre缓解，选择应用

![](https://image.3001.net/images/20211221/1640081069_61c1a6ad639416d5d52fa.png!small)

4.3 修改预编译头，选择应用

![](https://image.3001.net/images/20211221/1640081089_61c1a6c16ea4425f4e6e6.png!small)

05

在每一个case中添加break关键字，并且使用AddVectoredExceptionHandler函数添加一个VEH异常的回调。VEH的回调是一个链表，挂着很多的处理程序。AddVectoredExceptionHandler函数的第一个参数就是用来指定新增VEH处理函数位于链表的哪个位置。如果第一个参数的值是0，那么新增的VEH处理函数将处于整个链表的最后。如果第一个参数的值是一个非0值，那么新增的VEH处理函数就会位于链表的头部。AddVectoredExceptionHandler函数的第二个参数就是指定新增的回调函数

5.1 函数的原型可以通过在AddVectoredExceptionHandler的函数上按F12，看到函数的原型。

​![](https://image.3001.net/images/20211221/1640081111_61c1a6d71b97df63cd8bb.png!small)

5.2 在红框的位置上，继续F12，就可以看到这个参数的原型，实际上就是一个回调函数的函数指针原型。

![](https://image.3001.net/images/20211221/1640081127_61c1a6e77c46ca35a9f27.png!small)

5.3 然后复制出来，修改成如下样式。去掉typedef，把指针修改成函数名，增加花括号的函数体，异常处理的部分就需要在函数体内实现。

![](https://image.3001.net/images/20211221/1640081143_61c1a6f788b9f9317bf72.png!small)

5.4 最后，将其添加到DLL_PROCESS_ATTACH中。

![](https://image.3001.net/images/20211221/1640081376_61c1a7e0358cc99e6430a.png!small)

06

手工在需要HOOK的位置制造异常，触发VEH异常处理。我们这里采用软件断点的方式触发异常。即是在需要HOOK的函数的第一个字节处，将其改成硬件吗0xCC，这样就会触发一个int
3异常。按照异常的接管顺序。此时异常将优先被VEH异常处理拦截。那么我们此时就可以在VEH异常处理的回调函数中对其进行HOOK代码的编写。

6.1 声明一个用来保存异常地址（HOOK地址）和被替换字节的结构体，并且声明对象。

![](https://image.3001.net/images/20211221/1640081459_61c1a833e33d29560142f.png!small)

6.2 编写设置HOOK的函数

![](https://image.3001.net/images/20211221/1640081550_61c1a88e5b56d1177e396.png!small)

6.3
如果是自定义函数，自行分析目标的函数地址，如果是系统API，可以采用如下方式获取函数地址。![](https://image.3001.net/images/20211221/1640081571_61c1a8a36b9f04d91aedd.png!small)

6.4
在DLL_PROCESS_ATTACH中，添加HOOK的调用。![](https://image.3001.net/images/20211221/1640081592_61c1a8b8b3fb9e9122bde.png!small)

07

选择在VEH异常处理的回调函数中处理HOOK![](https://image.3001.net/images/20211221/1640081623_61c1a8d71cf94d96bfa48.png!small)

在这部分代码中，之所以需要将EIP + 2。是因为在x86的函数头是如下样式的。

![](https://image.3001.net/images/20211221/1640081646_61c1a8ee706f71f1b9bf0.png!small)也就是说，我们的断点0xCC实际上就是改在了红框的位置上，替换了8B，而原本的函数中，8BFF的硬编码组成了mov
edi,edi,这里实际上别没有什么用，所以我们如果直接跳过这两个硬编码也并不会影响程序的正常执行。

08

生产DLL文件

8.1
生成文件![](https://image.3001.net/images/20211221/1640081667_61c1a9033ac716d7a32a8.png!small)

8.2
取出文件到桌面或其他位置![](https://image.3001.net/images/20211221/1640081685_61c1a9153510206e6bccf.png!small)

09

测试我们HOOK的效果

9.1
首先写一个目标程序，代码如下![](https://image.3001.net/images/20211221/1640081712_61c1a93008feeb8b2582c.png!small)

9.2 使用注入器（自行编写或网上下载，这里我用的是自己写的）将我们生成的模块注入到目标进程中。

正常情况下：![](https://image.3001.net/images/20211221/1640081727_61c1a93fa9f34b2bee14e.png!small)

HOOK后：![](https://image.3001.net/images/20211221/1640081739_61c1a94b330c2b0ad52bb.png!small)

10

如果我们需要卸载HOOK，那么需要如下操作

10.1
添加如下代码![](https://image.3001.net/images/20211221/1640081760_61c1a960cfef6627021cd.png!small)

10.2
在需要退出的位置调用即可，例如DLL_PROCESS_DETACH中。![](https://image.3001.net/images/20211221/1640081774_61c1a96e633db98b7c36c.png!small)

到了这里，VEH HOOK就已经完成了

