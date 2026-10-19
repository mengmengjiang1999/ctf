![1592995611_5ef32f1b85512.jpg!small](https://image.3001.net/images/20200624/1592995611_5ef32f1b85512.jpg!small)

## EvilDLL

 **EvilDLL是一款专门针对DLL劫持攻击而开发并设计的恶意DLL（反向Shell）生成器。**

DLL劫持指的是，病毒通过一些手段来劫持或者替换正常的DLL，欺骗正常程序加载预先准备好的恶意DLL。由于输入表中只包含DLL名而没有它的路径名，因此加载程序必须在磁盘上搜索DLL文件。首先会尝试从当前程序所在的目录加载DLL，如果没找到，则在Windows系统目录中查找，最后是在环境变量中列出的各个目录下查找。利用这个特点，先伪造一个系统同名的DLL，提供同样的输出表，每个输出函数转向真正的系统DLL。程序调用系统DLL时会先调用当前目录下伪造的DLL，完成相关功能后，再跳到系统DLL同名函数里执行，这个过程用个形象的词来描述就是系统DLL被劫持了。

![1592995617_5ef32f2115a5b.jpg!small](https://image.3001.net/images/20200624/1592995617_5ef32f2115a5b.jpg!small)

## 功能介绍

> 1、使用Ngrok.io实现反向TCP端口转发；
>
> 2、自定义端口转发选项（LHOST、LPORT）；
>
> 3、包含了DLL劫持样本（Half-Life（半条命）启动文件）；
>
> 4、已在Windows 7（7601）和Windows 10平台上测试；

## 工具要求

Mingw-w64编译器：

    
    
    apt-get install mingw-w64

Ngork认证令牌（TCP隧道需要使用到）：

    
    
    https://ngrok.com/signup

你的认证令牌Authtoken需要在仪表盘中可访问：

    
    
    https://dashboard.ngrok.com

安装你的认证令牌：

    
    
    ./ngrok authtoken <YOUR_AUTHTOKEN>

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/thelinuxchoice/evildll

## 工具使用

满足上述工具运行条件之后，就可以使用下列命令运行EvilDLL了：

``cd evildll``

``

````

``

``bash evildll.sh``

``

### 工具运行截图

![2.jpg](https://image.3001.net/images/20200624/1592995650_5ef32f42ec4f2.jpg!small)

## 项目地址

> EvilDLL：【[ _GitHub传送门_](https://github.com/thelinuxchoice/evildll)】

## 参考来源

>  _[thelinuxchoice](https://github.com/thelinuxchoice/evildll)_

