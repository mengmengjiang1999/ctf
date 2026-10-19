**User pwn学了一部分了，想要学习一下Kernel
pwn，然后查了好多资料都是关于编译Linux内核的。但是网上很多内容教的不是很全，只能多查一查然后缝合了。**

# 下载Linux内核

首先要下载上内核的源码，可以去Linux官网，另外我是在Ubuntu的虚拟机上面下的，速度太慢，可以考虑使用清华的源。

    
    
    curl -O -L https://mirrors.tuna.tsinghua.edu.cn/kernel/v5.x/linux-5.4.98.tar.xz
    unxz linux-5.4.98.tar.xz
    tar -xf linux-5.4.98.tar
    

下载下来以后一步一步解包，最后就能得到源码，一般源码可以放到src目录下面，我是用来调试的，干脆就放在了家目录下面了。

![image.png](https://image.3001.net/images/20211027/1635335302_61793c8659b993b83c7d1.png!small)

# 安装一些依赖

Linux的某些版本需要安装一些依赖，可以根据提示来安装。但是如果对Linux的了解比较少，可以对这些依赖都进行安装，除了占点内存没啥坏处。

    
    
    sudo apt-get install build-essential
    sudo apt-get install libelf-dev
    sudo apt-get install libncurses-dev
    sudo apt-get install flex
    sudo apt-get install bison
    

# 编译

首先进入linux的目录里面，就是我们下载内核代码解包之后的目录。

然后我们需要配置一下.config文件，一般的话我们自己虚拟机的config文件就可以用，.config文件是编译Linux的一些选项，我暂时还不知道怎么用，我们可以直接使用我们自己Linux虚拟机的选项。首先到`/boot`目录下

然后输入ls看一下  
![image.png](https://image.3001.net/images/20211027/1635336290_617940622e64f3e4cd1b2.png!small)大家应该也有类似这样的文件。我们选择一个然后进行复制，我选的0-89的那个。

    
    
    首先回到我们的linux目录
    cd linux-5.4.98/
    然后复制一下
    sudo cp /boot/config-5.4.0-87-generic .config
    注意这个是我自己的，不要直接cv，去自己boot目录看一下，应该差不多
    为什么使用-87的，这里建议大家使用一下uname -a来查看一下，尽量和自己的虚拟机配置程一样的
    

有了.config文件之后我们使用`sudo make oldconfig`，然后安装已有的module`sudo make
localmodconfig`，接下来进行配置`sudo make menuconfig `

由于我们是要进行调试的，所以配置的时候进入Kernel Hacking，然后勾选上Kernel debuging选项。

最后我们使用sudo make -j4进行编译。编译的时间比较长，即便开多线程也长。耐心地等待。

 **中间出了好多次错误，快把我恶心吐了，查了一两个小时的文档，这东西对小白不太友好。**

 **本文参考自[Linux - 内核编译安装](https://blog.hyperzsb.tech/linux-kernel-compile-install/)、[CTFwiki](https://ctf-wiki.org/pwn/linux/kernel-mode/environment/build-kernel/)、[在Ubuntu18.04下编译Linux内核](https://rimson.top/2019/03/14/ubuntu-make-kernel/)、[linux编译内核步骤与错误解决](https://blog.51cto.com/xiguanmin/1553714)....感谢大佬们**

