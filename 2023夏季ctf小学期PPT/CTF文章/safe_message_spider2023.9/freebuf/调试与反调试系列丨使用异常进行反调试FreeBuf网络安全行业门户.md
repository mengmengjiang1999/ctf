使用异常进行反调试是利用异常处理的机制对调试器进行一些操作。

原理是自己处理了异常就会走正常流程，如果没有接收到自己的异常，就说明异常被调试器接收了，无法正常处理。那么就可以判断是在调试器中运行的。

我们先来创建一个DLL项目。步骤如下：

**1.选择新建项目**![](https://image.3001.net/images/20220620/1655716886_62b03c164e55228e9ae24.png!small)

 **2.创建win32控制台应用程序- >点击确定**

![](https://image.3001.net/images/20220620/1655716887_62b03c17ac267faf6cff5.png!small)

 **3.勾选空项目，完成**

![](https://image.3001.net/images/20220620/1655716888_62b03c189865d8507360e.png!small)

 **4.新建源文件entry.cpp**

![](https://image.3001.net/images/20220620/1655716889_62b03c19104ba5eb2c54d.png!small)

 **5.配置**

5.1 选择属性

![](https://image.3001.net/images/20220620/1655716889_62b03c1990e22f3172541.jpg!small)

5.2修改运行库，应用

**![](https://image.3001.net/images/20220620/1655716890_62b03c1a032e629b07d6c.png!small)**

 **6\. 添加#include、#include、主函数和默认循环**

![](https://image.3001.net/images/20220620/1655716890_62b03c1ac3aa923558545.png!small)

 **7\. 要创建一个线程，先写一个线程回调**

![](https://image.3001.net/images/20220620/1655716891_62b03c1b6b498309dc7ad.png!small)

 **8.在主函数里创建线程**

**![](https://image.3001.net/images/20220620/1655716892_62b03c1c100fc6a06c271.png!small)**

 **9.填入检测调试器用的代码**

![](https://image.3001.net/images/20220620/1655716892_62b03c1cac2585d6e15ac.png!small)

9.1在try触发异常，通过EXCEPTION_EXECUTE_HANDLER(异常处理常量)判断要自行处理异常，进入到异常处理的代码执行

![](https://image.3001.net/images/20220620/1655716893_62b03c1d4d7b362dc8f55.png!small)

9.2手动写一个异常语句_asm int 3 (软件断点)

![](https://image.3001.net/images/20220620/1655716893_62b03c1dc8b2fa3a5b314.png!small)

9.3如果被调试器接收没有处理，就会崩（int 3触发异常，调试器识别为自行下的断点）

![](https://image.3001.net/images/20220620/1655716894_62b03c1e3daf72fc2bcc6.png!small)

9.4自行处理加continue（跳出去，进行下一个循环）

![](https://image.3001.net/images/20220620/1655716894_62b03c1eaa6834fdd6ded.png!small)

9.5声明是一个已知的异常，已知异常的处理代码就是continue，没有调试器附加，这个代码就会一直运行（内部其实触发了异常，不过异常已经被自行处理掉了）

![](https://image.3001.net/images/20220620/1655716895_62b03c1f3cdc6fc7b138c.png!small)

 **10\. 在调试器里打开，没有处理的情况下，调试器一直在暂停**

![](https://image.3001.net/images/20220620/1655716895_62b03c1fa9c42d55df5b5.png!small)

处理的情况下

![](https://image.3001.net/images/20220620/1655716896_62b03c20a20a82f7fd06f.png!small)

在od打开，出现弹窗（在x32dbg没有弹窗，是因为被记录下来了）

![](https://image.3001.net/images/20220620/1655716897_62b03c213c57ed1d098a3.png!small)

利用异常进行反调试的正常情况下，在这一步识别到调试器之后

![](https://image.3001.net/images/20220620/1655716897_62b03c218b9825e711e8d.png!small)

会做一些误导分析者这里是正常执行位置的假象，从而达到利用异常进行反调试的目的。

