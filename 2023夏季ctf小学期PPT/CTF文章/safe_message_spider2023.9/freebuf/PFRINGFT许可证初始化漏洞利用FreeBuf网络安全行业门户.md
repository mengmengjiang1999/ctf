***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x00 PF_RING FT功能介绍

github地址：<https://github.com/ntop/PF_RING>

 **PF_RING是一个Linux内核模块和用户空间框架，可以高速率处理网络数据包，同时为处理数据包的应用程序提供一套API。**

PF_RING FT实现了一个优化的流表，由于与nDPI的本机集成，可以用来跟踪流并提取包括7层协议的流元数据。使用PF_RING
FT可以编写一个事件驱动的流处理应用程序，专注于实际的流处理而不是流表管理和性能，实际上它提供了许多钩子，可用于定制和扩展核心流表用来构建流分析的应用程序，包括探针、IDS和IPS。

其中详细的介绍及使用方法可参见文档：<https://github.com/ntop/PF_RING/blob/dev/doc/ft.rst>

![1.png](https://image.3001.net/images/20190215/1550223690_5c66894a91e8d.png!small)由于FT是收费的模块，购买网址：<https://shop.ntop.org/>，售价为199.95欧元/年。

![2.png](https://image.3001.net/images/20190215/1550223706_5c66895a6565d.png!small)

## 0x01 运行环境介绍

破解过程在CentOS7系统下，我们使用PF_RING中的pfcount命令读取网络数据，将PF_RING_FT_CONF=/usr/local/etc/ndpi/ndpi.conf环境变量导入到系统中后将自动启用FT功能。

如果系统中没有FT模块的license文件则会出现如下提示，并且五分钟后程序自动退出。

![3.png](https://image.3001.net/images/20190215/1550223725_5c66896d29a23.png!small)

## 0x02 爆破许可过程

首先我们使用objdump工具将pfcount二进制文件反汇编并存放在pf.s文件中：

![4.png](https://image.3001.net/images/20190215/1550223826_5c6689d2b1903.png!small)

然后我们来查看根据上面ft.rst文件描述的，使用ft时首先调用pfring_ft_create_table函数，我们打开pf.s文件来查看这个函数的实现。

![5.png](https://image.3001.net/images/20190215/1550223843_5c6689e3587c9.png!small)

可以发现在pfring_ft_create_table函数中调用了license_init函数，并且调用的二进制指令为："e8 36 e9 ff
ff"，然后使用gdb动态调试pfcount命令。首先将断点设置在0x43fff5位置，然后单步执行，如下图所示：

![6.png](https://image.3001.net/images/20190215/1550223857_5c6689f135573.png!small)

可见license_init函数中对设备的license进行校验。我们跳过这个函数实验一下有可能直接绕过license限制，跳转思路如下图所示：

![7.png](https://image.3001.net/images/20190215/1550223871_5c6689ff7d546.png!small)

首先在gdb中0x43fff5处设置断点，然后修改rip寄存器指向下一个指令的地址0x43fffa，然后继续执行。

![8.png](https://image.3001.net/images/20190215/1550223883_5c668a0b189da.png!small)

发现license的报错信息没有显示，我们继续等待五分钟限制，发现pfcount可以一直运行，至此我们破解点就寻找成功了，但是不能每次运行都进入调试模式修改寄存器，这样使用本不方便，我们可以修改二进制文件，将调用license_init指令删除。

前文在pf.s文件中可以查看到调用license_init函数的二进制指令为"e8 36 e9 ff
ff"，我们通过hexdump查找调用license_init指令在二进制文件中的位置。

![9.png](https://image.3001.net/images/20190215/1550223901_5c668a1d1a85d.png!small)

可以看出0003fff0处是调用license_init函数的行号。然后我们使用vim -b
参数打开pfcount二进制文件，然后输入:%!xxd，则可以看见文件的二进制形式，然后找到003fff0位置处，如下图所示。

![10.png](https://image.3001.net/images/20190215/1550223913_5c668a29e8ed4.png!small)

将这5个字节修改为nop指令，nop指令的二进制码是0x90：

![11.png](https://image.3001.net/images/20190215/1550223929_5c668a390a893.png!small)

然后输入:%!xxd
-r恢复二进制模式，并保存，然后我们使用objdump命令重新反汇编一下pfcount，发现0x43fff5地址处的指令变为nop跳过指令。

![12.png](https://image.3001.net/images/20190215/1550223942_5c668a4639d78.png!small)

然后我们手动执行一下pfcount命令查看结果：

![13.png](https://image.3001.net/images/20190215/1550223958_5c668a567d53f.png!small)

此时已经不提示license无效的信息，然后我们继续观察是否会在5分钟退出。

![14.png](https://image.3001.net/images/20190215/1550223976_5c668a68a0c7e.png!small)

由上图可见对PF_RING FT模块的破解是成功的。

## 0x03 总结

本文主要介绍Linux系统下破解二进制文件的思路，本文并没有对汇编语指令进行分析，应该有助于刚刚进入破解门槛的小伙伴进一步学习，也为后续ntop注册机的实现做一些简单的铺垫。

这种暴力破解也存在缺陷，例如没有考虑到调用license_init函数返回后寄存器的值，有可能导致后续流程出现异常错误。

这个漏洞已向ntop官方反馈，后续版本应该会修复，此漏洞仅限学习交流，切勿用于非法用途。  

 ***本文作者：小2黑hei，转载请注明来自FreeBuf.COM**

