## 前言

 **今天给大家介绍的是一款名叫MCExtractor的微代码分析工具，大家可以用它来对Intel、AMD、VIA和Freescale的微代码分析。**

## MCExtractor

![1.png](https://image.3001.net/images/20181211/1544535484_5c0fbdbc440db.png!small)

MCExtrator这款工具可以解析Intel、AMD、VIA和Freescale处理器的微代码库，终端用户可以用它来查找相关的微代码信息，例如CPU
ID、平台、版本、日期、型号、大小和校验和等等。该工具可以将Intel微代码容器（dat、inc、h、txt）转换为二进制镜像，以进行BIOS整合、检测新的/未知微代码、检测微代码健康以及更新状态等等。除此之外，我们还可以把MCExtractor当做一款研究分析工具来使用，再配合上它的扩展数据库，我们甚至可以用它来检测和分析任何形式的微代码。

## MCExtractor功能

> 1、 支持1995年至今所有正在使用的或遗留的微代码；
>
> 2、 扫描运行的Intel、AMD、VIA和Freescale微代码；
>
> 3、 通过校验和验证提取出的微代码完整性；
>
> 4、 检测Intel、AMD和VIA微代码是否为最新版本；
>
> 5、 转换Intel容器为二进制镜像；
>
> 6、 基于CPU ID搜索特定的微代码；
>
> 7、 显示微代码Header结构；
>
> 8、 快速向数据库添加新的微代码实例；
>
> 9、 报告数据库中之前不存在的微代码；
>
> 10、提供用户友好的消息；
>
> 11、遵循GNU GPL v3开源许可证协议；

微代码数据库：【[传送门](https://github.com/platomav/CPUMicrocodes)】

## 工具下载

MCExtractor由两个文件组成，即可执行文件MCE.exe和数据库文件MCE.db。Github代码库中已经有Windows平台下的编译版本了，所以大家无需再手动编译。【[下载地址](https://github.com/platomav/MCExtractor/releases)】

### 代码依赖

为了运行MCExtractor的Python脚本，你需要安装下列第三方Python库：

安装Colorama：

    
    
    pip3 install colorama

安装PTable：

    
    
    pip3 install https://github.com/platomav/PTable/archive/boxchar.zip

### 构建/编译源码

PyInstaller可以帮助我们构建支持各个平台的MCExtractor，而且运行和更新都很方便。

确保安装了Python 3.6.0+：

    
    
    python --version

使用pip安装PyInstaller：

    
    
    pip3 install pyinstaller

使用pip3安装colorama：

    
    
    pip3 install colorama

使用pip安装PTable：

    
    
    pip3 install https://github.com/platomav/PTable/archive/boxchar.zip

### 构建/编译源码：

    
    
    pyinstaller --noupx --onefile MCE.py

## 工具截图

注意：其中包含旧版本MCExtractor的使用截图。

![2.png](https://image.3001.net/images/20181211/1544535627_5c0fbe4bae90d.png!small)![3.png](https://image.3001.net/images/20181211/1544535627_5c0fbe4bc5bf6.png!small)![4.png](https://image.3001.net/images/20181211/1544535627_5c0fbe4bca8ff.png!small)![5.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c0b7b0.png!small)![6.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c1d270.png!small)![7.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c2cd30.png!small)![8.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c6f813.png!small)![9.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c757a5.png!small)![10.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4c7d965.png!small)
![11.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4cb6671.png!small)![12.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4cbdd85.png!small)![13.png](https://image.3001.net/images/20181211/1544535628_5c0fbe4ce35ce.png!small)
![14.png](https://image.3001.net/images/20181211/1544535629_5c0fbe4d0ad82.png!small)![15.png](https://image.3001.net/images/20181211/1544535629_5c0fbe4d17094.png!small)![16.png](https://image.3001.net/images/20181211/1544535629_5c0fbe4d37fe4.png!small)
![17.png](https://image.3001.net/images/20181211/1544535629_5c0fbe4d4ce8a.png!small)![18.png](https://image.3001.net/images/20181211/1544535629_5c0fbe4d53871.png!small)  

## 项目地址

> MCExtractor：【[GitHub传送门](https://github.com/platomav/MCExtractor)】

***参考来源：[MCExtractor](https://github.com/platomav/MCExtractor)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

