****一. 原理分析****

动态链接库预加载机制是系统提供给用户运行自定义动态链接库的一种方式，在可执行程序运行之前就会预先加载用户定义的动态链接库的一种技术。

该技术可用于重写系统中有漏洞的库函数，从而达到修复漏洞的目的，如get_host_byname导致ghost漏洞的这类函数。攻击者同样可利用该技术写rootkit，通过重写系统文件、网络、进程相关的库函数，达到隐藏文件或进程的目的。

相较于普通的用户空间rootkit，该技术更加隐蔽，难以被发现，相较于内核模块rootkit，该技术的兼容性更好，编写难度更低。因此，这种类型的rootkit逐年增多，难以查杀。

由于动态链接库的预加载机制和全局符号介入机制,可控制程序运行时的链接（Runtime
linker），允许用户在程序运行前优先加载自定义的动态链接库，使得恶意动态链接库优先于正常动态链接库加载，根据全局符号介入的顺序原理来”短路”正常函数，最终优先执行攻击者定义的恶意函数。

 ** **恶意动态链接库主要有3种利用方式：****

将恶意动态链接库通过LD_PRELOAD环境变量进行加载。

将恶意动态链接库通过/etc/ld.so.preload配置文件进行加载。

修改动态链接器来实现恶意功能，例如修改动态链接器中默认的用于预加载的配置文件路径/etc/ld.so.preload为攻击者自定义路径，然后在里面写入待加载的恶意动态链接库，当然修改的方法还有很多，如修改默认环境变量，直接将要hook的动态链接库写入动态链接器中。

 ** **二. LD_PRELOAD劫持****

这种劫持相对较简单，可以通过以下方法实现:

 ** **劫持方法：****

1) LD_PRELOAD=/lib/f1c8d7.so

将LD_PRELOAD的值设置为要预加载的动态链接库

2) export LD_PRELOAD

导出环境变量使该环境变量生效

3) 一般情况下相关的库文件会被加上隐藏属性

![1623310909_60c1c23d5b450b3c071c4.png!small](https://image.3001.net/images/20210610/1623310909_60c1c23d5b450b3c071c4.png!small)

 ** **检测方法****

查看环境变量即可检测是否存在劫持：

![1623310934_60c1c256f29b08fb555f4.png!small](https://image.3001.net/images/20210610/1623310934_60c1c256f29b08fb555f4.png!small)

 ** **三. /etc/ld.so.preload劫持****

 ** **劫持方法：****

这种劫持方式是目前最主流的，通过修改配置，将其加载恶意库文件实现劫持。可使用github里面的工具来实现（https://github.com/mempodippy/cub3）

![1623310957_60c1c26d7049c954231b6.png!small](https://image.3001.net/images/20210610/1623310957_60c1c26d7049c954231b6.png!small)

 ** **检测方法：****

使用cat无法查看相应的内容；使用busybox可以看到相应的内容，说明存在库劫持。并且其类型是修改/etc/ld.so.preload内容，增加恶意库文件实现劫持。

由于cat命令被劫持了，因此我们可以使用strace来追踪/bin/cat命令的加载情况，可以看到其访问/etc/ld.so.preload，并且打开了/lib/cub3.so这个库文件。

 ** **修复方法：****

通过去掉隐藏属性来处理修复：

./busybox lsattr -ia /etc/ld.so.preload

./busybox chattr -ia /etc/ld.so.preload

./busybox rm -rf/etc/ld.so.preload /lib/cub3.so

 ** **四. 修改动态链接器****

修改动态链接器实现恶意功能目的有多种方法，这里使用替换动态链接器中的默认预加载配置文件/etc/ld.so.preload路径的rootkit，来实现更加隐蔽的恶意动态链接库预加载,安装的方法是修改动态链接器中配置文件路径/etc/ld.so.preload为自定义的路径，然后再在该路径中写入要预加载的恶意动态链接库的绝对路径。测试使用的恶意rootkit名称为Vlany,

下载地址为：https://github.com/mempodippy/vlany。

实验环境:

靶机ubuntu16 内核：Linux 4.4.0-31-generic x86_64

攻击机：Kali2020 内核：4.17.0-kali1-amd64 架构：x86_64 #不支持

 ** **劫持方法：****

 ** **创建文件：****

quick_install.sh：

![1623311059_60c1c2d30d156a0e036c9.png!small](https://image.3001.net/images/20210610/1623311059_60c1c2d30d156a0e036c9.png!small)

install.sh：

![1623311073_60c1c2e192c557c0b1aa7.png!small](https://image.3001.net/images/20210610/1623311073_60c1c2e192c557c0b1aa7.png!small)

 ** **编译安装****

quick_install.sh下载项目后解压调用install.sh脚本，首先会检测SElinux是否关闭。如果没关闭，脚本会关闭SElinux。此时需要重启机器。

检验完SElinux，程序出现提示框，选择grub配置位置，来确认当机器重启后后门依然生效。根据机器实际情况填写，默认/etc/grub.conf。

等待gcc等依赖安装完成，设置通过ssh连接的PAM用户名，记住此后门用户名：

![1623311100_60c1c2fc9f78018d6249e.png!small](https://image.3001.net/images/20210610/1623311100_60c1c2fc9f78018d6249e.png!small)

设置PAM密码：

![1623311126_60c1c31664e9e4d1093a0.png!small](https://image.3001.net/images/20210610/1623311126_60c1c31664e9e4d1093a0.png!small)

设置PAM端口：

![1623311147_60c1c32b0d14db8a52d5d.png!small](https://image.3001.net/images/20210610/1623311147_60c1c32b0d14db8a52d5d.png!small)

设置连接是否使用SSL加密：

![1623311159_60c1c337e84fb6044872e.png!small](https://image.3001.net/images/20210610/1623311159_60c1c337e84fb6044872e.png!small)

设置accept()后门密码：

![1623311173_60c1c3459a98d539e718f.png!small](https://image.3001.net/images/20210610/1623311173_60c1c3459a98d539e718f.png!small)

设置accept()后门隐藏端口：

![1623311213_60c1c36dcc624fc7eedb5.png!small](https://image.3001.net/images/20210610/1623311213_60c1c36dcc624fc7eedb5.png!small)

完成后，脚本会提示是否安装作者新研究的snodew后门这里选择NO

全部配置完成后，呈现出如下连接信息：

![1623311251_60c1c3932a87b5a3fa95f.png!small](https://image.3001.net/images/20210610/1623311251_60c1c3932a87b5a3fa95f.png!small)

 ** **连接后门****

在攻击机创建文件ssh.sh

![1623311272_60c1c3a83bf8aa8618554.png!small](https://image.3001.net/images/20210610/1623311272_60c1c3a83bf8aa8618554.png!small)

使用其他机器连接后门：sh ssh.sh kionf 192.168.43.167 4397

![1623311309_60c1c3cd833215604e282.png!small](https://image.3001.net/images/20210610/1623311309_60c1c3cd833215604e282.png!small)![1623311330_60c1c3e2555f77726a5c5.png!small](https://image.3001.net/images/20210610/1623311330_60c1c3e2555f77726a5c5.png!small)

显示连接成功

在被攻击端查看是否有异常连接，完全隐藏没有显示出任何连接信息，并且查看/etc/passwd文件，没有我们所使用的kionf用户

![1623311347_60c1c3f3c093ece94fa74.png!small](https://image.3001.net/images/20210610/1623311347_60c1c3f3c093ece94fa74.png!small)

https://github.com/mempodippy/detect_preload上的检测程序未能检测出：

![1623312196_60c1c7444998bade36e65.png!small](https://image.3001.net/images/20210610/1623312196_60c1c7444998bade36e65.png!small)

 ** **检测方法:****

使用strace命令来查看预加载的配置文件是不是/etc/ld.so.preload文件，如下图：

![1623312214_60c1c7566fc2d7ebb1f2c.png!small](https://image.3001.net/images/20210610/1623312214_60c1c7566fc2d7ebb1f2c.png!small)

动态链接库预加载的配置文件是/sbin/.XqASUKZb而不是原有的配置文件，我们即可确认系统中存在修改动态链接器的rootkit

 ** **清除方法****

清除修改动态链接器的rootkit，需要使用相同系统的相同版本动态链接器替换被修改了的动态链接器，才能达到彻底清除的目的。![1623312226_60c1c7625730eeb4a9e20.png!small](https://image.3001.net/images/20210610/1623312226_60c1c7625730eeb4a9e20.png!small)![1623312226_60c1c7625b59106de7c7c.png!small](https://image.3001.net/images/20210610/1623312226_60c1c7625b59106de7c7c.png!small)

暂时缓解的方式则是将上方检测过程中看到的恶意动态链接库删除，以及将对应的动态链接库配置文件中的内容清除。

 ** **五. 参考链接****

https://kionf.com/2018/10/25/rookit-vlany/

https://www.freebuf.com/column/162604.html

https://www.freebuf.com/articles/system/223311.html

