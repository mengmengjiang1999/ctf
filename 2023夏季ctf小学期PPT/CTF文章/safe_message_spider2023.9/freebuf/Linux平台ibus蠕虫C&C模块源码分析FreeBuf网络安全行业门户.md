**近期，深信服安全团队在排查问题时，遇到一台主机不断访问恶意域名linuxsrv134.xp3.biz，尝试与之通信，通过对问题主机的排查和域名的威胁情报分析，关联到了一个2019年新型Linux蠕虫——ibus，本文针对其C
&C模块进行详细分析。**

进行第一阶段的初始化以及检测。判断/tmp/.Abe0ffdecac1a561be917bfded951a7a
pid记录文件是否存在，判断是否存在已经运行的线程。

![图片1.png](https://image.3001.net/images/20190716/1563239722_5d2d252ad6d9e.png!small)

再重新fork一个进程：

![图片2.png](https://image.3001.net/images/20190716/1563239731_5d2d2533adf37.png!small)

并将新的pid记录到/tmp/.Abe0ffdecac1a561be917bfded951a7a文件：

![图片3.png](https://image.3001.net/images/20190716/1563239752_5d2d254815258.png!small)

进行第二阶段的初始化，判断配置文件/usr/share/hplip/data/images/24x24/.rc是否存在，其中包含配置文件的hash以及休眠时间：

![图片4.png](https://image.3001.net/images/20190716/1563239779_5d2d2563d1dbc.png!small)

![图片5.png](https://image.3001.net/images/20190716/1563239763_5d2d2553b3375.png!small)

判断预定的UUID是否为空，如果为空则生产新的UUID并写到/usr/share/hplip/data/images/24x24/Remove_user.png文件。

![图片6.png](https://image.3001.net/images/20190716/1563239820_5d2d258c637d4.png!small)

完成第二阶段初始化，进入循环执行阶段：

![图片7.png](https://image.3001.net/images/20190716/1563239835_5d2d259bbf057.png!small)

MAIN为主函数，通过调用check_relay, 判断是否还存在指令：

![图片8.png](https://image.3001.net/images/20190716/1563239871_5d2d25bfa81b2.png!small)

![图片9.png](https://image.3001.net/images/20190716/1563239882_5d2d25ca6b431.png!small)

但是目前该域名已经过期了，获取不到任何的数据。

![图片10.png](https://image.3001.net/images/20190716/1563239896_5d2d25d8183d4.png!small)

如果还有未执行的指令，就会调用Knock_Knock函数上传ID信息来获取被base64编码和异或加密的指令内容，
其指令任务内容主要分为4大类，分别为needregr、newtask、notasks以及newreconfig。

![图片11.png](https://image.3001.net/images/20190716/1563239910_5d2d25e69b51b.png!small)

下图为任务处理过程：

![图片12.png](https://image.3001.net/images/20190716/1563240038_5d2d2666a0f35.png!small)

具体指令功能见下表：

功能分类 | 功能编号 | 具体功能  
---|---|---  
Needregr |  
| 上传本地信息并更新配置文件  
Newtask(任务执行) | 1 | 下载执行  
3 | 下载并且带参数执行  
6 | 退出  
9 | 进行自我更新  
10 | 卸载  
11 | 命令执行  
notasks |  
| 根据休眠时长休眠  
Newreconfig |  
| 重新配置配置文件hash以及休眠时长  
  
如果没有指令或者网络有问题，为了继续通信，就会尝试以下4种方式：

![图片13.png](https://image.3001.net/images/20190716/1563239925_5d2d25f579afe.png!small)

### 1.尝试重连：

![图片14.png](https://image.3001.net/images/20190716/1563240006_5d2d26465c04b.png!small)

### 2.从备用网络linuxservers.000webhostapp.com以及linuxsrv134.xp3.biz等获取新的C&C地址进行通信：

![图片15.png](https://image.3001.net/images/20190716/1563240052_5d2d2674aa806.png!small)![图片16.png](https://image.3001.net/images/20190716/1563240068_5d2d26849beb0.png!small)

目前该blog linuxservers.000webhostapp.com的指令如下，通过隐藏属性隐藏。手动可以访问该内容，通过该脚本直接访问得到404：

![图片17.png](https://image.3001.net/images/20190716/1563240080_5d2d2690a093d.png!small)

### 3.通过解密函数，其解密分为2个部分，首先进行base64解码，再通过异或(“#”为key)得到如下更新信息：

![图片18.png](https://image.3001.net/images/20190716/1563240090_5d2d269a30bb6.png!small)![图片19.png](https://image.3001.net/images/20190716/1563240099_5d2d26a3092b8.png!small)

根据DGA算法获取新的C2地址，但是该方法目前并没有实现。

### 4.通过查找5.196.70.86的开发端口，更新新的C2地址为5.2.73.127，端口更新为检测到的开放端口：

![图片20.png](https://image.3001.net/images/20190716/1563240112_5d2d26b008050.png!small)

最后为了长时间驻留，其创建了定时任务，分为了用户态以及内核态两种定时任务。

用户态：每小时执行一次/bin/sh “/bin/nmi”；

内核态：每天执行一次/bin/sh “/var/run/pm-utils/locks/nbus”；

每周日执行/bin/sh “/usr/lib/rpm/platform/x86_x64-linux/.dbus”。

![图片21.png](https://image.3001.net/images/20190716/1563240155_5d2d26db07698.png!small)

大多数时候，都是直接在root上查看，但是有些病毒是通过web漏洞等方式进来的，所以在排查的时候，需要确认一下目前能够使用的用户有哪些，并针对每个用户进行检查，不然会出现遗漏，不能正确定位问题所在。

## **IOC**

###  **IP &Domain：**

    
    
    5.196.70.86
    
    5.2.73.127
    
    speakupomaha.com
    
    linuxservers.000webhostapp.com
    
    linuxsrv134.xp3.biz

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

