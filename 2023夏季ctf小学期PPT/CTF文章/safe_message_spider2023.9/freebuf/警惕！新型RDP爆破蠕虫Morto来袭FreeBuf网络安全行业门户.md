**近期，千里目安全实验室EDR安全团队接到多个企业用户反馈，其企业内网近百台计算机在使用过程中会突然跳出到windows登录界面，且再次登录就提示远程桌面繁忙，同时深信服防火墙检测到内网存在大量的RDP访问请求。**

这次蠕虫病毒事件严重阻碍到企业办公，安全团队紧急介入，发现这是Morto蠕虫病毒的最新变种，它通过爆破内网、外网主机的RDP密码，登陆到受害主机，进行自我复制并运行，来实现病毒的传播。

##  **0x01 攻击场景**

![图片1.png](https://image.3001.net/images/20180403/15227209763397.png!small)

病毒的攻击流程如下：

###  **母体（Morto.exe）**

1\.
将伪装clb.dll释放到C:\Windows，这样就会比C:\Windows\System32下的合法clb.dll先加载（Windows寻找文件的特性，根目录的先被读取）

2\. 写入恶意代码HKLM\System\WPA\md

3-4. 运行regedit，regedit会自动加载恶意的clb.dll

###  **Loader（clb.dll）**

5.将自己备份一份cache.txt到C:\Windows\offline web pages下

6.运行\md下的恶意代码

###  **Payload**

7.释放\\\tsclient\a\%smoto

8.释放\\\tsclient\a\a.dll和\\\tsclient\a\r.reg

9.DNS请求和进行RDP爆破

10.修改注册表

11.将cache.txt注册为服务

沦陷主机上已经找不到母体和Loader了（应该病毒进行了自删除），但是cache.txt和payload还遗留在主机上，我们从这两个文件入手分析：

##  **0x02 技术分析**

###  **cache.txt**

cache.txt打开后发现其其实是一个DLL（clb.dll的克隆，即Loader），我们通过解密相关的函数地址，得到对应的函数列表，如下图所示：

![图片2.png](https://image.3001.net/images/20180403/15227210147604.png!small)

解密出来的函数如下所示：

![图片3.png](https://image.3001.net/images/20180403/15227210311789.png!small)

### **Loader**

1\.
cache.txt运行前首先做一个判断，若程序不是通过rundll32.exe加载运行的，则尝试读取用户电脑系统目录下的winhlp32.exe或write.exe这两个程序（检测运行环境是否为沙箱），如果用户电脑中存在这两个文件，才进行后面的操作，如下图所示：

![图片4.png](https://image.3001.net/images/20180403/15227210466433.png!small)

2\. 验证不是沙箱环境后，cache.txt开始读取恶意注册表项的值（payload），并加载运行，如下图所示：

![图片5.png](https://image.3001.net/images/20180403/1522721066379.png!small)  

相应的恶意注册表键值为：

 ****

    
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA**

名称：md

里面包含一大串二进制数据，通过内存解密之后，发现其实也是一个dll，主要的恶意操作也在其中，如下图所示：

![图片6.png](https://image.3001.net/images/20180403/15227210877408.png!small)

3\.
为了进行传播，payload会将自己复制一份到\\\tsclient\a\%smoto，Loader后续会从\\\tsclient\a\%smoto读取恶意代码：

![图片7.png](https://image.3001.net/images/20180403/15227211078431.png!small)

### **Payload**

1\. payload开始运行后，会对下面这些域名的DNS发起请求，检索可下载的组件信息，如下图所示：

![图片8.png](https://image.3001.net/images/20180403/15227211291742.png!small)  

相关的域名地址：

> wht%d.jifr.net
>
> dos%d.jifr.net
>
> ms.jifr.net
>
> ms.jifr.info
>
> ms.jifr.co.cc
>
> ms.jifr.co.be

2\.
然后payload对HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU进行修改：

![图片9.png](https://image.3001.net/images/20180403/15227211494258.png!small)  

RunMRU注册表项的作用是存储用户最近运行的命令，payload修改它的目的是为了清除记录，防止恶意行为被发现。

![图片10.png](https://image.3001.net/images/20180403/15227211741264.png!small)

3\. 修改注册表项HELM\CurrentControlSet\Control\Sessin
Manager\PendingFileRenameOperations的值为病毒母体cache.txt，如下图所示：

![图片11.png](https://image.3001.net/images/20180403/15227211912887.png!small)

修改PendingFileRenameOperations键值的作用是使cache.txt开机自动重命名为C:\Windows\Temp\ntshrui.dll，这其中跟上面一样的技术，系统合法的ntshrui.dll在C:Windows\System32目录下，由于cache.txt开机自动伪装成了Temp\ntshrui.dll（Temp目录下的ntshrui.dll先被加载），导致cache.txt开机自动被加载。

![图片12.png](https://image.3001.net/images/20180403/15227212197051.png!small)  

4\. 添加一些注册表恶意项：

 ****

    
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA\id**
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA\ie**
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA\it**
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA\sn**
    
     **HKEY_LOCAL_MACHINE\SYSTEM\WPA\sr**

 ****

![图片13.png](https://image.3001.net/images/20180403/15227212399402.png!small)  

5\. 然后到了关键的RDP爆破：

![图片14.png](https://image.3001.net/images/20180403/15227212596573.png!small)

![图片15.png](https://image.3001.net/images/20180403/15227212789303.png!small)  

6\. 爆破成功后，登陆到受害主机上进行Payload的复制传播：

![图片16.png](https://image.3001.net/images/20180403/15227212977657.png!small)  

7\. 然后进行Loader（\\\tsclient\a.dll和\\\tsclient\r.reg）的复制传播：

![图片17.png](https://image.3001.net/images/20180403/15227213172606.png!small)  

8\. 最后将cache.txt（ntshrui.dll）注册为服务，对用户主机进行持久化攻击：

![图片18.png](https://image.3001.net/images/20180403/15227213424702.png!small)

![图片19.png](https://image.3001.net/images/20180403/15227213821879.png!small)  

9\. 最后，就是我们看到的可疑现象，有一个恶意svchost.exe进程一直在发送3389端口的请求：

![图片20.png](https://image.3001.net/images/20180403/15227214006837.png!small)

## **0x03 解决方案**

1\. 删除右边所有键值，如图，只保留默认键值

![图片21.png](https://image.3001.net/images/20180403/15227214319803.png!small)

2\. 使用任务管理器结束不断发出3389请求的svchost.exe进程：

PS：使用tcpview等工具可确定爆破3389的svchost.exe

![图片22.png](https://image.3001.net/images/20180403/1522721450193.png!small)  

3\. 删除病毒cache.txt：

![图片23.png](https://image.3001.net/images/20180403/15227214832249.png!small)

4\. 删除成功后重启电脑确认是否还存在该病毒

5\. 更改用户登录密码，通过设置高强度密码避免再次被RDP爆破

以上解决方案主要针对单台主机。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

