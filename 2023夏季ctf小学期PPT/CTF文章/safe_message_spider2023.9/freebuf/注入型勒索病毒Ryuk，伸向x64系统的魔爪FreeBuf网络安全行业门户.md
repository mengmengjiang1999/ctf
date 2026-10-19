## **一、** **背景介绍**

**Ryuk是一款通过垃圾邮件和漏洞利用工具包传播的勒索病毒，最早在2018年8月由国外某安全公司报道，其代码结构与HERMES勒索病毒十分相似；早前，深信服安全团队针对32位的Ryuk勒索病毒进行了详细的技术分析，并密切关注该勒索家族的发展动向，对捕获的针对64位系统版本的Ryuk勒索病毒进行了详细的技术分析。**

##  **二、** **信息概述**

1.勒索病毒的运行流程如图：

![Ryuk勒索病毒.png](https://image.3001.net/images/20190221/1550716789_5c6e0f753b408.png!small)

2.勒索信息如图：

![24.png](https://image.3001.net/images/20190221/1550716818_5c6e0f9278579.png!small)3.加密后文件如图：

##
![29.png](https://image.3001.net/images/20190221/1550716832_5c6e0fa0ee726.png!small)
**三、** **详细分析**

1.获取系统版本进行判断：

![image.png](https://image.3001.net/images/20190221/1550716864_5c6e0fc006291.png!small)

2.线程功能-终止xchange相关进程：

![image.png](https://image.3001.net/images/20190221/1550716876_5c6e0fcccf0de.png!small)

![image.png](https://image.3001.net/images/20190221/1550716883_5c6e0fd314c03.png!small)

3.线程功能-查找spooler相关服务进行删除：

![image.png](https://image.3001.net/images/20190221/1550717085_5c6e109d755d3.png!small)![image.png](https://image.3001.net/images/20190221/1550717089_5c6e10a18e4d3.png!small)

4.提升进程权限：

![image.png](https://image.3001.net/images/20190221/1550716923_5c6e0ffb08307.png!small)

5.获取进程的登录用户信息：

![image.png](https://image.3001.net/images/20190221/1550717058_5c6e1082aa511.png!small)

6.查找"csrss.exe"、"explorer.exe"、"lsaas.exe"进程中的一个进行注入：

![image.png](https://image.3001.net/images/20190221/1550716976_5c6e10301f354.png!small)

7.执行注入进程的代码，根据系统版本在系统目录下创建文件夹：

![image.png](https://image.3001.net/images/20190221/1550716997_5c6e1045d45ba.png!small)

![image.png](https://image.3001.net/images/20190221/1550717009_5c6e1051c853b.png!small)

8.获取API地址：

![image.png](https://image.3001.net/images/20190221/1550717029_5c6e1065be5d0.png!small)

9.提升注入进程的权限：

![image.png](https://image.3001.net/images/20190221/1550717105_5c6e10b190a0e.png!small)

10.生成AES密钥并使用RSA公钥进行加密：

![image.png](https://image.3001.net/images/20190221/1550717114_5c6e10bab6287.png!small)

11.解密出勒索文件信息：

![image.png](https://image.3001.net/images/20190221/1550717124_5c6e10c424e9e.png!small)

![image.png](https://image.3001.net/images/20190221/1550717129_5c6e10c9c3fee.png!small)

12.遍历磁盘，对文件进行加密：

![image.png](https://image.3001.net/images/20190221/1550717137_5c6e10d15dc82.png!small)

13.在根目录释放勒索文件“RyukReadMe.txt”：

![image.png](https://image.3001.net/images/20190221/1550717147_5c6e10db7c77e.png!small)

14.排除”$Recycle.Bin”、”AhnLab”、”Chrome”、”Mozilla”、”WINDOWS”、"RyukReadMe.txt"、"UNIQUE_ID_DO_NOT_REMOVE"、"PUBLIC"目录或文件，以及”dll/Dll/hrmlog/exe/EXE”类型的文件：

![image.png](https://image.3001.net/images/20190221/1550717156_5c6e10e4e65b5.png!small)

![image.png](https://image.3001.net/images/20190221/1550717161_5c6e10e9b6a14.png!small)

15.加密满足条件的文件：

![image.png](https://image.3001.net/images/20190221/1550717171_5c6e10f3c8956.png!small)

16.对加密文件设置已加密标识：

![image.png](https://image.3001.net/images/20190221/1550717182_5c6e10fe73bbe.png!small)

17.重命名加密后的文件，添加”.RYK”后缀：

##
![image.png](https://image.3001.net/images/20190221/1550717190_5c6e11060c006.png!small)
**四、** **解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

###  **病毒检测查杀**

1.深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>

2.深信服EDR产品及防火墙等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![image.png](https://image.3001.net/images/20190221/1550717204_5c6e1114dced2.png!small)

###  **病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.及时给电脑打补丁，修复漏洞。

2.对重要的数据文件定期进行非本地备份。

3.不要点击来源不明的邮件附件，不从不明网站下载软件。

4.尽量关闭不必要的文件共享权限。

5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6.如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

7.深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。

8.深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

