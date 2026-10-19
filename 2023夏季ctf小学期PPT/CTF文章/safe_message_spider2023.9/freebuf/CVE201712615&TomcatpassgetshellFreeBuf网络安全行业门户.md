## CVE-2017-12615

### 漏洞描述

当存在漏洞的Tomcat运行在Windows/Linux主机上，且启用了HTTP PUT请求方法（
例如，将readonly初始化参数由默认值设置为false），攻击者将有可能可通过精心构造的攻击请求数据包向服务器上传包含任意代码的JSP的webshell文件，JSP文件中的恶意代码将能被服务器执行，
导致服务器上的数据泄露或获取服务器权限。

### 漏洞原理

漏洞的产生是由于配置不当（非默认配置），当在Tomcat的conf（配置目录下）/web.xml配置文件中添加readonly设置为false时，将导致该漏洞产
生，（需要允许put请求）。

![1653034939_62874fbb1db2e1ebb288c.png!small?1653034940841](https://image.3001.net/images/20220520/1653034939_62874fbb1db2e1ebb288c.png!small?1653034940841)

### 影响范围

Apache Tomcat 7.0.0 - 7.0.79

Apache Tomcat/8.5.19

### 漏洞复现

采用的是在线靶场VULFOCUS

![1653034960_62874fd00bc37ca299135.png!small?1653034961731](https://image.3001.net/images/20220520/1653034960_62874fd00bc37ca299135.png!small?1653034961731)

打开靶场给的地址，看到tomcat默认页面。

![1653034976_62874fe073b21b6610c29.png!small?1653034978604](https://image.3001.net/images/20220520/1653034976_62874fe073b21b6610c29.png!small?1653034978604)

刷新页面抓包。

![1653034988_62874fec84ad2ae2d0139.png!small?1653034989975](https://image.3001.net/images/20220520/1653034988_62874fec84ad2ae2d0139.png!small?1653034989975)

在请求包写入利用PUT上传的文件和内容，但上传G，出现404。

![1653035023_6287500fe695243797fbe.png!small?1653035025518](https://image.3001.net/images/20220520/1653035023_6287500fe695243797fbe.png!small?1653035025518)

绕过文件上传的限制：

/x.jsp%20

/x.jsp/

/x.jsp::$DATA

绕过上传成功。

![1653035037_6287501d4dd3d0b3c1989.png!small?1653035038952](https://image.3001.net/images/20220520/1653035037_6287501d4dd3d0b3c1989.png!small?1653035038952)

webshell连接。

![1653035051_6287502b07e778b6f3531.png!small?1653035053016](https://image.3001.net/images/20220520/1653035051_6287502b07e778b6f3531.png!small?1653035053016)

## tomcat-pass-getshell

### 漏洞原理

在tomcat8环境下默认进入后台的密码为tomcat/tomcat，未修改造成未授权即可进入后台，或者管理 员把密码设置成弱口令。

### 漏洞复现

采用VULFOCUS在线靶场。

![1653035065_628750395bad3dba05c70.png!small?1653035067026](https://image.3001.net/images/20220520/1653035065_628750395bad3dba05c70.png!small?1653035067026)

输入靶场给的地址，看到tomcat默认页面。

![1653035079_628750475b38b3c7d5818.png!small?1653035081471](https://image.3001.net/images/20220520/1653035079_628750475b38b3c7d5818.png!small?1653035081471)

通过弱口令登陆，Success。

![1653035090_628750521f2b8aad81235.png!small?1653035091753](https://image.3001.net/images/20220520/1653035090_628750521f2b8aad81235.png!small?1653035091753)

登陆后在下面WAR file to depioy 上传后缀为war的文件。

(war制作：将密码文件压缩为zip，将其后缀修改为war即可)

![1653035128_62875078be55352a6f84c.png!small?1653035130483](https://image.3001.net/images/20220520/1653035128_62875078be55352a6f84c.png!small?1653035130483)

上传的请求包和响应包。

![1653035140_62875084b2fea1d94f75e.png!small?1653035142538](https://image.3001.net/images/20220520/1653035140_62875084b2fea1d94f75e.png!small?1653035142538)

连接webshell。

![1653035156_62875094d3fda45a2f7ac.png!small?1653035158787](https://image.3001.net/images/20220520/1653035156_62875094d3fda45a2f7ac.png!small?1653035158787)

