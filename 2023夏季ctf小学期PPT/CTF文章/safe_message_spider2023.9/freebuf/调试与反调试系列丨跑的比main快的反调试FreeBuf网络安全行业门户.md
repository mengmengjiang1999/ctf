**首先要了解“进程—线程”的关系**

 **进程：可以理解为一个内存块，是一块虚拟内存。在3环（应用层）的结构是PEB，在内核的结构是EPROCESS。**

 **线程：在CPU上根据时间片进行抢占切换，是为进程工作的。在3环（应用层）的结构是TEB，在内核的结构是ETHREAD。**

 **进程本身没有任何执行能力，只是通过结构来描述。进程创建的时候，一定会有一个主线程运行。运行多线程有很多子线程，子线程的生命周期是由主线程决定的。**

 **今天要讲的反调试是TLS(线程局部存储)：可以简单理解为一个线程的CALLBACK。**

 **一般情况：**

 **进程创建 ->主线程运行代码**

 **如果程序里存在TLS(线程局部存储)：**

 **进程创建 ->主线程创建->执行TLS回调函数->主线程运行代码**

 **我们先来创建一个DLL项目。步骤如下：**

 **1.选择新建项目**

![](https://image.3001.net/images/20220620/1655716821_62b03bd53ac47aef25e38.png!small)

 **2.创建 win32控制台应用程序->点击确定**

![](https://image.3001.net/images/20220620/1655716823_62b03bd7273feb71946a4.jpg!small)

 **3.勾选空项目，完成**

![](https://image.3001.net/images/20220620/1655716823_62b03bd79369ce8bfaf19.jpg!small)

 **4.新建源文件 entry.cpp**

![](https://image.3001.net/images/20220620/1655716824_62b03bd80b4f969063cb1.jpg!small)

 **5.配置**

5.1 选择属性

![](https://image.3001.net/images/20220620/1655716824_62b03bd86653ad5305a95.jpg!small)

5.2修改运行库，应用

![](https://image.3001.net/images/20220620/1655716824_62b03bd8d5d6e3c9a6e28.jpg!small)

6.添加#include、#include

![](https://image.3001.net/images/20220620/1655716825_62b03bd94ca744f56587e.png!small)

7.向链接器声明，要使用TLS

![](https://image.3001.net/images/20220620/1655716825_62b03bd9a42f25316941d.jpg!small)

8.复制PIMAGE_TLS_CALLBACK里的三个参数

![](https://image.3001.net/images/20220620/1655716825_62b03bd9e8a207219a1e8.jpg!small)

9.完成注册TLS函数的回调

![](https://image.3001.net/images/20220620/1655716826_62b03bda51f3d975f001d.png!small)

10.重新生成->运行

![](https://image.3001.net/images/20220620/1655716826_62b03bdacd827ced43c31.png!small)

发现没有运行到main函数

11.加断点，再运行

![](https://image.3001.net/images/20220620/1655716827_62b03bdb983d15727eb58.png!small)

发现还是运行不起来.但是直接运行，可以正常打印，正常停止

![](https://image.3001.net/images/20220620/1655716828_62b03bdc1862062c34984.png!small)

12.试下其他调试器

12.1在od里运行：

![](https://image.3001.net/images/20220620/1655716828_62b03bdc7b11afa91b12b.jpg!small)

发现不能进入主模块

12.2在IDA里打开：

![](https://image.3001.net/images/20220620/1655716831_62b03bdf392961aa6bdce.jpg!small)

Ida会自动停在main函数上，意味着静态调试也发现不了TLS

动态调试没进入主模块，静态调试看不到。想找到TLS需要先了解一个原理，Windows下可执行文件都是PE文件（包含exe、dll、sys、com等）

PE结构里->数据目录表（常见的导出表、导入表等）->TLS表

所以，加入TLS_CALLBACK，在TLS表里会找到TLS回调函数，这是找到TLS回调的一个方法，但是常规方法找不到TLS回调函数。

