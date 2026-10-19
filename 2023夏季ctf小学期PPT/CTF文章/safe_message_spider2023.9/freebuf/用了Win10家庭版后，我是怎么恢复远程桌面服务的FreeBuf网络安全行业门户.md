###
由于学习的需要，要使用到远程桌面服务。但是我电脑用的是Win10家庭版，微软取消了该服务，所以就想着恢复远程桌面服务。自己在网上也试了很多的方法，遇到了很多的坑，最后终于解决了，特此记录下来帮助需要的人。

1.在<https://github.com/stascorp/rdpwrap/releases>上下载最新的压缩包。![](https://image.3001.net/images/20210321/1616328332_6057368c1d71e44c774e9.png!small)

在电脑上解压得到：

![](https://image.3001.net/images/20210321/1616328646_605737c67d68e155b7097.png!small)

在文件夹中以管理员权限运行install.bat。

2.运行RDPConf.exe，查看相关信息。如果显示如下图，则服务已开启，但是如果Listener
state是红色的，请继续向下看（一般如果是Win10家庭版，估计都是红色的）。

![](https://image.3001.net/images/20210321/1616328958_605738fe94781f5ddf4d4.png!small)3.由上图可以知道我的版本是10.0.19041.789，我们来到<https://github.com/stascorp/rdpwrap/issues/1342>，发现有人已经解决，我只有使用下图的方法才能成功，大家也可以试试其他的（如果版本不一样的，可以找一下自己版本对应的解决方法<https://github.com/stascorp/rdpwrap/issues>）。

![](https://image.3001.net/images/20210321/1616329329_60573a714f9cd72037894.png!small)

4.下载该师傅的rdpwrap.zip，解压之后替换C:\Program Files\RDP
Wrapper\rdpwrap.ini即可。直接替换不会成功，会出现该问题：

![](https://image.3001.net/images/20210321/1616330474_60573eeabaa006211120e.png!small)

所以在替换之前，需要先关闭远程桌面的服务，具体操作：打开任务管理器，找到FrameServer：

![](https://image.3001.net/images/20210321/1616330600_60573f68794a1bda133b1.png!small)

右键-打开服务，找到该服务关闭。

![](https://image.3001.net/images/20210321/1616330684_60573fbcca8551e5e9979.png!small)5.做完之后我们再运行RDPConf.exe发现就成功了，此时运行RDPCheck.exe，如下图所示，我们就恢复了远程桌面服务。

![](https://image.3001.net/images/20210321/1616330929_605740b1b32b1d2bd1eec.png!small)

  

