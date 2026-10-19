# 记攻防演练经历

首先声明 **本次演练对目标的演练测试全程有授权** ， **文章内容仅供安全研究人员学习提升所用。**

![image](https://image.3001.net/images/20210422/1619073319_60811927df0dc99bee3af.png!small)

## 一、目标选择

拿到目标肯定要先选软柿子捏，通常来说 **大学、医院** 受攻击面大，安全防护也不够重视，所以我们选择这些目标进行测试。

## 二、内网入口

首先使用开源资产发现工具进行全面的资产发现。

收集到目标域名的子域名，利用爬虫发现目标站点的敏感路径文件。

![image](https://image.3001.net/images/20210422/1619073329_608119319e7cd1c3c3ff5.png!small)

### web入口一

初步扫描中发现某站点为`thinkphp3.2.3`构建，且存在网站备份文件泄露。而在备份文件中发现已经有其他攻击者上传的`webshell`（2017年），打开发现攻击者使用的是`phpmyadmin`备份日志拿到shell，猜测目标mysql数据库存在弱口令。打开thinkphp数据库配置文件确认。

![image](https://image.3001.net/images/20210422/1619073338_6081193ae188ba30d226f.png!small)

![image](https://image.3001.net/images/20210422/1619073344_608119406bb800f520ed7.png!small)  
但是管理员备份文件应该就是为了处理这些问题，已经将数据库密码修改。所以我们下一步简单看看thinkphp的实现是否存在某些漏洞。

发现Index包public方法下的`getCurl`、`postCurl`存在ssrf请求伪造漏洞，利用该漏洞读取网站数据库文件。

![image](https://image.3001.net/images/20210422/1619073379_60811963309143bccbb87.png!small)

![image](https://image.3001.net/images/20210422/1619073390_6081196e7f30f7c6f585a.png!small)

利用`phpmyadmin`拿到`webshell`

![image](https://image.3001.net/images/20210422/1619073399_6081197729ddf1d63eda7.png!small)

### web入口二

该目标还是个THINKPHP，通过扫描发现数据库备份目录存在遍历漏洞，下载数据库备份文件拿到webshell

![image](https://image.3001.net/images/20210422/1619073405_6081197daccf91eba87db.png!small)![image](https://image.3001.net/images/20210422/1619073419_6081198ba0d71adbdb23d.png!small)

## 三、内网漫游

代理进内网扫描就可以利用弱口令做很多了，比如

THINKSYSTEM-SR650 USERID/PASSW0RD

![image](https://image.3001.net/images/20210422/1619073440_608119a0131ddd9070062.png!small)

（Oracle(R) Integrated Lights Out Manager root/changeme

![image](https://image.3001.net/images/20210422/1619073446_608119a670244312c92b5.png!small)

锐捷RG-WALL防火墙管理系统 admin/admin

![image](https://image.3001.net/images/20210422/1619073454_608119aece5afdc77b070.png!small)

## 四、结束

网络边界有多硬内网就有多脆弱，就不再提其他路由器、摄像头等等等等的弱口令了。所以在攻防演练中资产收集的重要性不言而喻，我们找到边界的脆弱点进行突破，拿到我们想要的权限。

