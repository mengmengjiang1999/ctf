![687474703a2f2f7777772e70776e616476656e747572652e636f6d2f696d672f6c6f676f2e706e67.png](https://image.3001.net/images/20180627/15300608328360.png!small)

**Pwn Adventure 3是一款专为黑客而开发的，易受攻击的第一人称MMORPG游戏，其目的旨在提升游戏开发人员的安全编码能力。**

Pwn Adventure 3的游戏场景设置在一座美丽的岛屿上，在这个岛上任何情况都有可能发生，例如飞行，无限游戏虚拟币等。

  * 官方网站：<http://www.pwnadventure.com/>

## 视频系列

以下是该视频系列的一部分，涵盖了游戏中各类不同的挑战任务。

  * [使用Docker创建私人服务器 - Pwn Adventure 3：part 2](https://v.qq.com/x/page/w0704yxfl53.html)
  * [信息收集/侦察 - Pwn Adventure 3：part 3](https://v.qq.com/x/page/r07047b589s.html)
  * [使用gdb恢复游戏类 - Pwn Adventure 3：part 4](https://v.qq.com/x/page/n0704sdi3g9.html)
  * [使用LD_PRELOAD Hooking Linux - Pwn Adventure 3：part 5](https://v.qq.com/x/page/a0704ahz7nr.html)
  * [飞行以及我们的第一个flag！- 大冒险3：part 6](https://v.qq.com/x/page/d0704z23oq5.html)
  * [远程跳转和悬停（难以承受的复仇） - Pwn Adventure 3：part 7](https://v.qq.com/x/page/s07042z4h7v.html)
  * [找到隐藏的金蛋 - Pwn Adventure 3：part 8](https://v.qq.com/x/page/c0704vs0eqq.html)
  * [开发一个TCP网络代理 - Pwn Adventure 3：part 9](https://v.qq.com/x/page/z0704nll6iz.html)

## 服务器安装

 **安装条件**

来自官方README文档：

  * 至少需要2GB的内存，内存越大则能运行的实例越多。
  * 游戏服务器不需要任何的图形硬件，纯粹运行在控制台上。 我们推荐你使用Amazon AWS和Digital Ocean VPS。
  * 游戏服务器的运行需要占用大量内存，使用fork和写时复制将允许在单个主机上运行更多的实例。
  * 对于内存仅为2GB的服务器，我们建议运行的实例不要超过5个。而具有8GB RAM的服务器通常可以运行的实例数量与CPU可以处理的数量相同。
  * 如果有足够的RAM，建议每个CPU core只运行2-3个实例，以免造成游戏的卡顿现象。
  * 客户端和服务器的文件也超过了2GB，因此需要你的磁盘有足够的空闲空间。

你可以通过以下3种方法来构建和部署自己的服务器。

1.官方文档

根据官方提供的文档说明来构建和部署服务器。官方文档：<http://www.pwnadventure.com/#server>

2.指南

[@Beaujeant](https://twitter.com/Beaujeant)创建了一个简易的分步指南，你可以参考该指南来构建和部署服务器。<https://github.com/beaujeant/PwnAdventure3/blob/master/INSTALL-server.md>

3.Docker

如果你的主机上已安装了docker和docker-compose，那么这个方法应该说是最简便的了。它可以轻松运行和TEARDOWN服务器，而无需更改实际的主机系统。

首先，我们下载并安装PwnAdventure3：

    
    
    git clone https://github.com/LiveOverflow/PwnAdventure3.git
    cd PwnAdventure3
    wget http://pwnadventure.com/pwn3.tar.gz
    tar -xvf pwn3.tar.gz

想要运行服务器，必须要安装docker和docker-compose。Docker的更新发展速度较快，因此建议大家最好通过PwnAdventure3的官方文档安装部署。

  * Docker CE Ubuntu: <https://docs.docker.com/install/linux/docker-ce/ubuntu/>.
  * `docker-compose`: <https://docs.docker.com/compose/install/>
  * 确保当前用户为docker组：sudo usermod -a -G docker $ USER。重启或重新登录并使用id验证用户是否为docker组。

然后在项目目录下运行docker-compose build来重新构建服务，并启动主服务器和游戏服务器：

    
    
    docker-compose build
    docker-compose up

你也可以在docker-compose up后添加-d参数，使其在后台运行。

## 客户端安装

首先从官方网站下载客户端：<http://www.pwnadventure.com/#downloads>

要使客户端连接到新服务器，必须修改客户端的server.ini文件。docker启动的服务器主机名master.pwn3和game.pwn3（理论上是可以在docker/setup文件中进行修改的）。

客户端的server.ini文件必须遵循以下内容格式：

    
    
    [MasterServer]
    Hostname=master.pwn3
    Port=3333
    
    [GameServer]
    Hostname=game.pwn3
    Port=3000
    Username=
    Password=
    Instances=

确保客户端可以访问这些主机，例如将它们添加到/etc/hosts文件。在本例中，服务器运行在192.168.178.57上：

    
    
    192.168.178.57  master.pwn3
    192.168.178.57  game.pwn3

 **警告：** 在server.ini中使用IP作为主机名将不起作用！在这个问题上我被折腾了2个多小时。

终止服务器，只需输入docker-compose。

 **警告：** 数据库文件并不是永久保存的 - 取下容器将会重置所有内容。所以为了以防万一，请提前做好备份。

## 故障排除

### Error: docker-compose build

    
    
    $ docker-compose build
    Building init
    ERROR: Error processing tar file(exit status 1): write /client/PwnAdventure3_Data/PwnAdventure3/PwnAdventure3/Content/Paks/Characters.pak: no space left on device

原因：你的磁盘空间可能不足。

    
    
    $ docker-compose build
    Building init
    ERROR: Couldn't connect to Docker daemon at http+docker://localunixsocket - is it running?

原因：你的用户可能不属于docker组。sudo usermod -a -G docker pwn3，用id验证。或service docker
restart重启docker服务。

 **文件完整性**

检查文件是否已损坏：

    
    
    $ md5sum pwn3.tar.gz
    d3f296461fa57996018ce0e4e5a653ee  pwn3.tar.gz
    $ sha1sum pwn3.tar.gz
    022bd5174286fd78cd113bc6da6d37ae9af1ae8e  pwn3.tar.gz

### PwnAdventure3 Client Errors

 **Connection Error: Unable to connect to master server**

这可能意味着MasterServer不可访问。

客户端问题：

  * 检查客户端server.ini中的[MasterServer]条目
  * 你是否能从系统中的主机ping通master.pwn3？
  * /etc/hosts文件中的IP是否正确？

服务器问题：

  * 服务器没有运行并在3333端口侦听？
  * 通过sudo netstat -tulpn命令检查   

    * 主服务器侦听：tcp6 0 0 :::3333 :::* LISTEN 31913/docker-proxy
  * 如果两个容器都在运行，请检查docker ps   

    * 主服务器运行？880f93374070 pwn3server "/opt/pwn3/setup/mas…" 0.0.0.0:3333->3333/tcp, 5432/tcp pwnadventure3_master_1

**Waiting in connection queue...**

这说明MasterServer可以访问，现在正在等待一个可以提供给客户端的免费GameServer。这可能意味着没有GameServer正在运行，或者无法连接到MasterServer。

服务器问题：

  * 游戏服务器是否在端口3000-3005上运行并侦听？
  * 使用sudo netstat -tulpn命令查看服务及监听端口
  * tcp6 0 0 :::3000 :::* LISTEN 32160/docker-proxy
  * pwnadventure3_game_1容器是否正在运行？使用docker ps -a命令进行检查   

    * 84343f81034f pwn3server "/opt/pwn3/setup/gam…" 0.0.0.0:3000-3010->3000-3010/tcp, 5432/tcp pwnadventure3_game_1
  * 你是否在docker-compose up中看到以下内容：line 1: 7 Killed ./PwnAdventure3Server; pwnadventure3_game_1 exited with code 137 
    * 获取更多内存

### Docker版本

以下是在测试期间的主机版本：

    
    
    $ uname -a
    Linux ubuntu 4.4.0-31-generic #50~14.04.1-Ubuntu SMP Wed Jul 13 01:07:32 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
    $ docker-compose version
    docker-compose version 1.19.0, build 9e633ef
    docker-py version: 2.7.0
    CPython version: 2.7.13
    OpenSSL version: OpenSSL 1.0.1t  3 May 2016
    $ docker --version
    Docker version 17.12.1-ce, build 7390fc6

 *******参考来源：[GitHub](https://github.com/LiveOverflow/PwnAdventure3/)， FB小编
secist 编译，转载请注明来自FreeBuf.COM**

