**是否曾经遇到过以下情况：**

在CentOS系统启动时，有时会出现加载完某个服务后系统卡死的问题。

如图所示，系统加载完DNS缓存服务nscd后卡死。

![1682394182_64474c46350b22781eec5.png!small](https://image.3001.net/images/20230425/1682394182_64474c46350b22781eec5.png!small)

判断应为加载顺序在nscd之后的服务出现异常导致。此时可重启云主机进入单用户模式，然后进入/etc/rc.d目录，该目录下的内容如图所示 ：

![1682394195_64474c5309534b86b7ad4.png!small](https://image.3001.net/images/20230425/1682394195_64474c5309534b86b7ad4.png!small)

其中rc0.d至rc6.d这7个目录对应了系统以运行级别0至7启动时需要加载的服务。  
其中rc3.d目录为正常多用户模式下启动需要加载的服务，进入rc3.d目录。查看内容，如图所示 ：

![1682394204_64474c5c4fc3a7d74370a.png!small](https://image.3001.net/images/20230425/1682394204_64474c5c4fc3a7d74370a.png!small)

以S+数字开头的链接表明系统启动时需要启动的服务，数字编号小的先执行，编号大的后执行以K+数字开头的链接表明系统关闭时需要终止的服务，数字编号小的先执行，编号大的后执行。

可以看到nscd服务的编号是30，加载完成之后下一个加载的是50号agentboot服务。因此判断可能为agentboot服务异常导致无法完成加载，系统hung住。

![1682394218_64474c6ab155b13d6cfd5.png!small](https://image.3001.net/images/20230425/1682394218_64474c6ab155b13d6cfd5.png!small)

执行chkconfig --level 3 agentboot
off命令，在运行级别3下将agentboot服务取消随系统启动加载。执行完命令后，rc3.d下S50agentboot这个文件会被删除。

![1682394230_64474c7653ba865388d44.png!small](https://image.3001.net/images/20230425/1682394230_64474c7653ba865388d44.png!small)

执行命令chkconfig，可以看到agentboot在运行级别3下的状态是off。

退出单用户模式后重启云主机，系统在加载完nscd服务后没有加载agentboot服务，继续完成启动过程。  
如需将某个服务重新添加至某个运行级别的启动加载列表，以将agentboot添加至运行级别3为例，

执行chkconfig --level 3 agentboot
on命令，可以看到rc3.d目录下新增了S55agentboot文件，同时chkconfig命令输出agentboot在运行级别3下的状态变为on。

![1682394239_64474c7fdc3c4d2ca780e.png!small](https://image.3001.net/images/20230425/1682394239_64474c7fdc3c4d2ca780e.png!small)

