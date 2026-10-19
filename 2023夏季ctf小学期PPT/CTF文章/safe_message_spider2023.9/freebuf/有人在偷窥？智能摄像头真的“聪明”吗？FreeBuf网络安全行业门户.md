***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.png](https://image.3001.net/images/20180314/15210274293336.png!small)  

## 写在前面的话

**在这个物联网当道的时代，类似咖啡机、汽车、冰箱和灯泡这样的东西都开始接入互联网了，而且更加智能化了。而且很多城市甚至还出现了智能街道。智能摄像头其实早就已经出现了，比如说安全监控设备。而最新款的智能摄像头可以连接到云端，而用户就可以使用便携设备（例如手机或平板电脑）远程查看视频信息了。**

近期，卡巴斯基实验室的安全研究人员对当前一款流行智能摄像头的安全性进行了分析。跟普通摄像头相比，这款智能摄像头不仅拥有非常丰富的功能，而且还可以接入到家庭安全系统或监控系统之中。

注：根据统计显示，目前互联网中有超过2000个拥有独立公共IP地址的该型号智能相机。

### Hanwha SNH-V6410PN/PNW智能摄像头

这款设备可用的视频录制分辨率有1920×1080,
1280×720和640×360，带有夜视功能，并且配备了运动传感器，而且还支持双向通信。它不仅可以捕获视频信息，而且还可以使用内置扬声器来发出声音。这款智能摄像头可以接入云端服务，换句话说，它的正常工作并不需要跟其他设备（例如电脑）连接，用户只需配置智能摄像头创建一个无线热点，并将其通过WiFi与家庭无线路由器连接即可。此时，用户可以通过智能手机、平板电脑或计算机来控制摄像头。需要注意的是，用户跟摄像头之间的通信只能通过云端完成，别无他法。

该摄像头基于的是Ambarella
S2L系统（ARM架构），它使用了Amboot作为初始加载器。启动之后，Amboot将会使用特殊命令作为参数来加载Linux内核：

    
    
    console=ttyS0ubi.mtd=lnx root=ubi0:rootfs rw rootfstype=ubifs init=/linuxrc model=SNH-V6410PNethaddr=************ sn=ZC7D6V2H*********
    s=c  
    

当systemd运行之后，系统将会正常启动，加载不同分区，并执行rc.local中设置的命令。在执行rc.local时，mainServer文件（摄像头运行逻辑核心）将会在守护进程模式下运行。除此之外，设备还会使用PHP和CGI脚本来处理用户文件。通过对PHP脚本的研究我们发现，负责处理mainServer通信的主函数位于/work/www/htdocs_weboff/utils/ipc_manager.php文件中。

下图显示的是用户与智能摄像头的交互逻辑：

![2.png](https://image.3001.net/images/20180314/15210274538173.png!small)  

## 用户通信

当用户向摄像头发送命令（例如旋转镜头、选择监控区域或切换夜视模式）时，每一个命令或参数都有相应的标识（一个常数），主标识记录在/work/www/htdocs_weboff/utils/constant.php文件中。之后，数据包头和Payload将会被创建，并通过UNIX套接字/tmp/ipc_path向mainServer发送请求。

针对ipc_manager.php文件的分析表明，这个阶段没有部署任何的身份验证机制，而请求是直接以用户‘admin’的身份发送的。请求样本如下：

    
    
    function makeHeader($cmd, $act, $type, $len){
    $header= array();
    $header= array_fill(0, 77, 0x00);
    $header[HEADER_OFF_MAGIC_NUMBER]= 0xFE;
    $header[HEADER_OFF_MAGIC_NUMBER+1]= 0xFF;
    $header[HEADER_OFF_MAGIC_NUMBER+2]= 0xFE;
    $header[HEADER_OFF_MAGIC_NUMBER+3]= 0xFF;
    $header[HEADER_OFF_MAJOR_VERSION]= MAJOR_VERSION; //Major Version
    $header[HEADER_OFF_MINOR_VERSION]= MINOR_VERSION; //Minor Version
    int2byte($header,$cmd, HEADER_OFF_COMMAND); //Command
    $header[HEADER_OFF_ACTION]= $act; //Action
    $header[HEADER_OFF_MSG_TYPE]= $type; //Type
    $header[HEADER_OFF_ERROR_CODE]= 0xFF; //Error Code
    int2byte($header,$len, HEADER_OFF_MSG_LENGTH); //Length
    str2byte($header,“127.0.0.1“, HEADER_OFF_PEER_IP, 40); //Peer IP[40]
    int2byte($header,80, HEADER_OFF_PEER_PORT); //Peer Port
    str2byte($header,“admin“, HEADER_OFF_PEER_ACCOUNT, 16); //Peer Account[16] – Current user name
    $header= array_merge($header, array_fill(0, 8, 0xFF)); //Reserved[8]
    return $header;
    }  
    

当摄像头通信是通过HTTP
API和SmartCam应用程序实现的时候，设备便会采用这种通信方法。在之后的测试中，数据包会直接由应用程序生成，并使用XMPP协议来发送控制信息。如果用户想要从外部通过HTTP
API或SmartCam应用程序来访问这个文件的话，则必须通过Web服务器的身份验证。

## 可利用的攻击漏洞

我们在研究过程中发现了以下漏洞：

> 1\. 固件更新过程中使用了不安全的HTTP协议；
>
> 2\. 通过HTTP API实现摄像头交互时，使用了不安全的HTTP协议；
>
> 3\. 使用’dnpqtjqltm’文件更换Web接口，这是一个“隐藏功能”；
>
> 4\. 更换Web接口时，’dnpqtjqltm’文件会发生缓冲区溢出；
>
> 5\. 有一个使用root权限实现远程命令执行的功能；
>
> 6\. 可远程修改管理员账号的密码；
>
> 7\. 拒绝服务攻击；
>
> 8\. 管理员账号无法抵御暴力破解攻击；
>
> 9\. 在xmpp.samsungsmartcam.com上注册摄像头时采用的是弱密码策略；
>
> 10\. 可通过云服务器与其他摄像头交互；
>
> 11\. 阻止新的摄像头在云服务器上注册；
>
> 12\. 身份认证绕过，可修改管理员密码或远程执行命令；
>
> 13\. 从SmartCam云端账号恢复摄像头密码；

通过进一步分析后，我们发现不仅仅是这一款智能摄像头存在这些问题，几乎所有由韩华集团(Hanwha)制造的智能摄像头都有这些问题。

### “隐藏”功能

我们所发现的“隐藏”功能允许用户修改智能摄像头的Web接口，下面给出的是Hanwha智能摄像头中“隐藏”功能的代码：

![3.png](https://image.3001.net/images/20180314/1521027512174.png!small)  

### 云服务器架构中的漏洞

除了智能摄像头本身的漏洞之外，云服务器架构同样存在严重的安全漏洞。因为如果云服务器架构中存在高危漏洞，攻击者就可以通过云端控制和访问所有与之相连的智能摄像头了。

其中最主要的问题是云端架构基于的是XMPP协议，而且所有的Hanwha智能摄像头云端都是Jabber服务器。因此，攻击者就可以利用漏洞在Jabber服务器上注册任意账号，并访问服务器的资源和连接设备了。

测试账号通过XMPP协议发送的消息结构如下：

  
![4.png](https://image.3001.net/images/20180314/15210275282246.png!small)  

解码后的信息主体如下：

  
![5.png](https://image.3001.net/images/20180314/15210275431682.png!small)  

在与云端交互的过程中，摄像头会发送用户凭证和一系列常熟标识。在对数据进行分析之后，远程攻击者不仅可以伪装成摄像头来与云端通信，而且还可以通过云端来向其他摄像头发送任意控制命令。

## 总结

攻击者可以利用智能摄像头做些什么？很明显，他们的选择有很多。攻击者可以远程修改管理员的密码，在智能摄像头上执行任意代码，访问并控制云端所有的摄像头。除此之外，攻击者甚至还可以利用这些智能摄像头来组件僵尸网络。

这对用户来说意味着什么呢？说的直接一点，他将能够监视你以及你家人的一举一动…

我们已经将所有检测到的漏洞提交给了厂商，其中的某些漏洞现已得到修复，但是还有部分尚未修复。

### 已修复的漏洞CVE信息如下：

> CVE-2018-6294
>
> CVE-2018-6295
>
> CVE-2018-6296
>
> CVE-2018-6297
>
> CVE-2018-6298
>
> CVE-2018-6299
>
> CVE-2018-6300
>
> CVE-2018-6301
>
> CVE-2018-6302
>
> CVE-2018-6303

 *** 参考来源：[securelist](https://securelist.com/somebodys-watching-when-cameras-are-more-than-just-smart/84309/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

