![](https://image.3001.net/images/20200415/1586944417_5e96d9a156cf0.jpg!small)

##  Chromepass

**Chromepass是一款功能强大的Chrome保存密码收集工具，本质上来说Chromepass是一个基于Python的控制台终端应用程序，它也可以生成一个Windows可执行程序，并且可以给广大研究人员提供下列功能：**

> 1、解密Chrome浏览器已存储的密码；
>
> 2、远程发送包含了登录用户名和密码的文件（通过电子邮件或反向HTTP）；
>
> 3、自定义图标；
>
> 4、反病毒引擎完全无法检测到；

##  反病毒检测

由于Chromepass所采用的编码技术，目前版本的Chromepass是反病毒引擎完全无法检测到的。下面给出的是我们使用当前热门的三款反病毒分析引擎扫描的测试结果：

> [VirusTotal
> Scan](https://www.virustotal.com/gui/file/b4780b4712f494dc9856ff23ce29415445ad5eea3776663da28c556645f0e202/detection)（0/68）
>
> [AntiScan](https://antiscan.me/scan/new/result?id=kmpsMNccfuRJ)（0/26）
>
> [Hibird Analysis](https://www.hybrid-> analysis.com/sample/9ca69d2c60f0db6c09e9959b6f9c8bfdf66ddbe2e28f9f7539fd2856b62315c0)（All
> Clean全部安全-CrowdStrike Falcon、MetaDefender和Virustotal）

##  工具下载

广大研究人员可以使用下列命令将Chromepass项目源码客隆至本地：

    
    
    git clone https://github.com/darkarp/chromepass.git

##  工具环境

该工具其实安装和使用都非常简单，我们只需要安装并搭建好Python环境即可：

[Python](https://www.python.org/downloads/)：该工具目前仅在Python
v3.7.4环境下进行了测试，但理论上支持3.6+环境。

##  工具安装

Chromepass要求在[Python](https://www.python.org/downloads/)
3.6+环境下运行，首先运行下列命令完成依赖组件的安装：

    
    
    cd chromepass
    
    pip install -r requirements.txt

如果安装过程中弹出了错误提醒，请先检查工具的运行环境是否配置正确，如果仍然弹出错误，请尝试运行下列命令：

    
    
    python -m pip install --upgrade pip
    
    python -m pip install -r requirements.txt

##  工具使用

正如刚才所说的，Chromepass的使用非常简单，只需要运行下列命令即可：

    
    
    > python create_server.py

运行之后，工具将会询问用户选择两个选项中的一个：

###  1、通过电子邮件（存在问题，暂不推荐使用）

> 首先，工具会要求用户输入一个电子邮件地址和一个密码；
>
> 接下来，工具会询问用户是否想要发送至其他地址或发给自己；
>
>
> 然后，工具会询问用户是否需要显示错误信息，这是一条伪造的消息，启用该功能之后，当用户打开一个可执行文件时便会显示该消息，之后用户的密码便会被发送给攻击者；
>
> 此时，我们将能够自行编写错误消息，或直接留空；
>
> OK，一切就绪，我们只需等待可执行程序生成并发送给目标用户即可；

###  2、通过client.exe（推荐使用）

>
> 首先，工具会要求用户输入一个IP地址来处理反向链接，这个地址属于攻击者。该地址可以是一个本地IP地址或一个远程IP地址。如果选择使用远程IP地址，则需要涉及到[端口转发](https://www.noip.com/support/knowledgebase/general-> port-forwarding-guide/)。
>
>
> 接下来，工具会询问用户是否需要显示错误信息，这是一条伪造的消息，启用该功能之后，当用户打开一个可执行文件时便会显示该消息，之后用户的密码便会被发送给攻击者；
>
> 此时，我们将能够自行编写错误消息，或直接留空；
>
> OK，一切就绪，我们只需等待可执行程序生成并发送给目标用户即可；
>
> client.exe必须在server_ip.exe执行前运行，server_ip.exe就是目标用户接收到的文件；
>
> 注意事项：如需使用自定义图标，直接使用相同的文件名和格式替换掉icon.ico文件即可。

##  项目地址

> Chromepass：【[GitHub传送门](https://github.com/darkarp/chromepass)】

 ***
参考来源：[darkarp](https://github.com/darkarp/chromepass)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

