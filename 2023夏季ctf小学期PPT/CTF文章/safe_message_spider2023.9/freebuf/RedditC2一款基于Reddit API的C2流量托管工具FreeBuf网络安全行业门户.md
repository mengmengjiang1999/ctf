![](https://image.3001.net/images/20230526/1685072015_6470288fab72c4b6f593a.png!small)  

## 关于RedditC2

RedditC2是一款基于Reddit API的C2流量托管工具，该工具能够使用Reddit
API来托管C2流量，由于大部分蓝队研究人员都会使用Reddit，因此使用Reddit API就变成了一个伪装合法流量的绝佳方式。

该项目仅出于教育目的或测试目的开发和使用，请在获得测试授权后谨慎使用。

## 工具要求

该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令安装工具所需的PRAW库：

    
    
    pip3 install praw

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/kleiton0x00/RedditC2

## 工具配置

### Teamserver

1、创建一个Reddit账号，并创建第一个App；

2、将clientid和密钥粘贴到config.json中即可；

![](https://image.3001.net/images/20230526/1685072061_647028bd671cf57d5cb80.png!small)

![](https://image.3001.net/images/20230526/1685072069_647028c53be6036aa0a8e.png!small)

最后，运行下列命令启动Teamserver：

    
    
    python3 teamserver.py

### 代理配置

首先，在Project标签中点击Manage Nuget Packages...：

![](https://image.3001.net/images/20230526/1685072086_647028d6d91e4c792810e.jpg!small)

然后选择Browse，并搜索RedditSharp，安装版本号为v1.1.13：

![](https://image.3001.net/images/20230526/1685072096_647028e067a79dafb76ce.png!small)

接下来，修改Program.cs中的凭证信息，并构建项目。

最后，编译好的可执行程序路径如下：

    
    
    /bin/Release/ILMerge/RedditAgent.exe

## 工作流程

### Teamserver

> 1、访问一个指定的Reddit Post，然后使用命令“in:”发布一个新的评论；
>
> 2、读取包含了单词“out:”的新评论；
>
> 3、如果没有找到这样的评论，则返回第二步；
>
> 4、解析并解密评论，并读取输出；
>
> 5、将现有评论编辑修改为“executed”以避免命令重复执行；

### Client

> 1、访问一个指定的Reddit Post，然后读取包含了“in:”的最新评论；
>
> 2、如果没有检测到新的评论，则返回第一步；
>
> 3、解析并解密评论中的命令，然后在本地执行；
>
> 4、加密命令的输出结果，并在相应的评论中回复（“out:”）；

## 工具使用截图

下面给出的是异或加密的C2流量演示：

![](https://image.3001.net/images/20230526/1685072193_6470294198ce0ece4895a.png!small)

## 扫描结果

由于该工具本质上属于一个自定义C2植入物，因此我们需要使用反病毒产品来进行检测和测试，下面给出的是反病毒产品的扫描结果：

![](https://image.3001.net/images/20230526/1685072203_6470294b29cbb85b407eb.png!small)

## 工具演示视频

 **演示视频** ：【[ _点我观看_](https://user-images.githubusercontent.com/37262788/206015879-589614d5-1a7a-4c21-a342-75bdfc677a61.mp4)】

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/kleiton0x00/RedditC2/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **RedditC2** ：【[ _GitHub传送门_](https://github.com/kleiton0x00/RedditC2)】

