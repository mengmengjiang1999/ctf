我安装的系统是CentOS7，安装的时候选择了最小化安装，然后发现不能识别ifconfig这条指令，通常我们使用yum命令来安装所需要的插件，最坑的是，我们发现yum指令也识别不了，那我们只能先解决yum指令的问题。

1、使用root用户进入系统，使用：cd /etc/sysconfig/network-scripts 口令进入这个地址

![1652942232_6285e5987b874b3a1cd1e.png!small](https://image.3001.net/images/20220519/1652942232_6285e5987b874b3a1cd1e.png!small)

2、ls查看网卡，我的是ifcfg-ens33，不一定都是一样的，大家要看自己具体的网卡是多少

![1652942315_6285e5eb9b1e7e3f1e1dd.png!small](https://image.3001.net/images/20220519/1652942315_6285e5eb9b1e7e3f1e1dd.png!small)

3、修改root用户对网卡文件的权限，使用chmod 666 ifcfg-ens33 命令

![1652942496_6285e6a08860c8e8615c0.png!small](https://image.3001.net/images/20220519/1652942496_6285e6a08860c8e8615c0.png!small)

4、然后使用vi ifcfg-ens333 指令对（网卡文件）进行修改，将ONBOOT参数修改为yes，使用wqt退出

![1652942597_6285e705bd2124371ee8a.png!small](https://image.3001.net/images/20220519/1652942597_6285e705bd2124371ee8a.png!small)

![1652942654_6285e73e9d3dfa350806f.png!small](https://image.3001.net/images/20220519/1652942654_6285e73e9d3dfa350806f.png!small)

5、现在就可以使用yum命令了，然后使用yum search ifconfig命令，查看是什么模块对ifconfig进行控制的，我们进行安装就行

![1652942789_6285e7c51afe7dc636f3c.png!small](https://image.3001.net/images/20220519/1652942789_6285e7c51afe7dc636f3c.png!small)

6、通过查询，我们知道是使用net-tools工具进行控制的，使用yum install net-tools命令进行安装即可

![1652942939_6285e85b197e184a09eaf.png!small](https://image.3001.net/images/20220519/1652942939_6285e85b197e184a09eaf.png!small)（我这边是已经安装过了，所以显示不用再安装）

7、等待安装完成，就可以使用ifconfig命令了，安装过程一路选择y就行了

参考文章：[(22条消息) CentOS安装最小化系统后没有YUM命令，没有ifconfig该怎么办？_Travis_wong的博客-CSDN博客_没有yum](https://blog.csdn.net/qq_41527980/article/details/109558025)

