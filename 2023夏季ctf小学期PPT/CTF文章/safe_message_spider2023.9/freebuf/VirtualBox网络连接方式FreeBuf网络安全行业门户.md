### 概览

VirtualBox网络连接方式主要有下面的四种：NAT、Bridge、Internal和Host-only
Adapter。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614105311863.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

### NAT

这种方式下，虚拟机的网卡连接到宿主的 VMnet8 上。此时系统的 VMWare NAT Service 服务就充当了路由器的作用，负责将虚拟机发到
VMnet8 的包进行地址转换之后发到实际的网络上，再将实际网络上返回的包进行地址转换后通过 VMnet8 发送给虚拟机。VMWare DHCP
Service 负责为虚拟机提供 DHCP 服务。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614105650792.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)在下面的图中，展示了主机和虚拟机相互访问的情况。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614110221101.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

### Bridged

这种方式下，虚拟机就像一台真正的计算机一样，直接连接到实际的网络上，与宿主机没有任何联系。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614105804480.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

### Host-only

这种方式下，虚拟机的网卡连接到宿主的 VMnet1
上，但系统并不为虚拟机提供任何路由服务，因此虚拟机只能和宿主机进行通信，而不能连接到实际网络上。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614105823204.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

### Internal

内网模式，顾名思义就是内部网络模式：虚拟机与外网完全断开，只实现虚拟机于虚拟机之间的内部网络模式。

### 公众号

对于日常的学习使用，前面的两种已经够用，搭建靶机的话，使用Bridge方式比较好，当然如果你有钱，不用虚拟机，自己买电脑或者租用阿里云当然更好，至于阿里云如何使用，我在前面的文章https://blog.csdn.net/helloworlddm/article/details/104487231中有所介绍。更多内容，欢迎关注我的公众号码![在这里插入图片描述](https://img-blog.csdnimg.cn/20200614110741530.jpg)

  

