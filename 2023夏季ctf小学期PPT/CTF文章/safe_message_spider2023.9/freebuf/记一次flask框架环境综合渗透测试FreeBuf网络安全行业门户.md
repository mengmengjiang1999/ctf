## **PART.01 登入过程**

1\. 访问靶场地址http://101.43.22.226/?name=2023，框架为Flask。

![](https://image.3001.net/images/20230803/1691026569_64cb0489bc0dbd33936f0.png!small)2\.
测试存在ssti注入。

![](https://image.3001.net/images/20230803/1691026579_64cb04936201cd71c425f.png!small)3\.
直接执行以下命令。

http://101.43.22.226/?name={% for c in [].__class__.__base__.__subclasses__()
%}

{% if c.__name__ == 'catch_warnings' %}

{% for b in c.__init__.__globals__.values() %}

{% if b.__class__ == {}.__class__ %}

{% if 'eval' in b.keys() %}

{{b['eval'('__import__("os").popen("whoami").read()') }}

{% endif %}

{% endif %}

{% endfor %}

{% endif %}

{% endfor %}

![](https://image.3001.net/images/20230803/1691026589_64cb049dc61a6c6afebe2.png!small)4\.
测试目标可以出网，直接执行命令反弹shell和上线msf。

5\. 对当前机器进行信息搜集，存在双网卡172.25.1.3和10.10.10.100。

6\. 添加路由。  
![](https://image.3001.net/images/20230803/1691026600_64cb04a86bbfe09a0eedb.png!small)7.对10.10.10.0段存活主机进行扫描，

![](https://image.3001.net/images/20230803/1691026618_64cb04ba744285c155539.png!small)8\.
存活主机有10.10.10.101、10.10.10.102、10.10.10.200
和10.10.10.201。其中，200，201这两台机器开放了445端口，在此探测是否存在永恒之蓝漏洞。

![](https://image.3001.net/images/20230803/1691026630_64cb04c64a093139606f6.png!small)9\.
对200这台机器进行漏洞利用。由于不确定200这台机器是否出网，所以payload要设置成正向shell，最后成功获取到这台机器的权限。

![](https://image.3001.net/images/20230803/1691026638_64cb04ce9a111391c7e3f.png!small)![](https://image.3001.net/images/20230803/1691026647_64cb04d7c88e141b2974f.png!small)10\.
因为10.10.10.100这台机器是可以出网的，将它作为我们的跳板机。远程下载frp，搭建socks5代理。

![](https://image.3001.net/images/20230803/1691026658_64cb04e2b53c91f027ba4.png!small)11\.
对10.10.10.101进行端口扫描，开放22和80端口，访问80的web服务。

![](https://image.3001.net/images/20230803/1691026668_64cb04ecd514a5501ff6d.png!small)12\.
测试存在文件，文件包含漏洞(不存在远程文件包含)。

![](https://image.3001.net/images/20230803/1691026684_64cb04fc0343111e53755.png!small)13\.
经过fuzz读取到配置文件config.php，从中获取到数据库的账户密码。

![](https://image.3001.net/images/20230803/1691026702_64cb050e046ae0bb3ea76.png!small)14\.
base64解码后的数据库用户名为catcat，密码为wannatobeacat。但是由于数据库还是不能连接，因此想到了密码复用——使用ssh，登录上catcat的账户。

![](https://image.3001.net/images/20230803/1691026712_64cb0518f312ebb6221c1.png!small)15\.
当前用户权限较低，尝试提权。使用pspy扫描后发现，root用户每分钟会执行一次backup.sh，且当前用户catcat可以修改此文件。

![](https://image.3001.net/images/20230803/1691026721_64cb05218a780598c485c.png!small)16\.
在backup.sh文件中添加 chmod 4475 /bin/bash，执行bash -p后成功提权。

![](https://image.3001.net/images/20230803/1691026730_64cb052acf114f505f0bd.png!small)17\.
对10.10.10.102机器进行扫描，发现开放了22和5000端口。访问5000后发现，其是web服务。

![](https://image.3001.net/images/20230803/1691026739_64cb053357e6ab24a13f1.png!small)18\.
存在用户名枚举，但是未爆破出密码，sql注入也不存在。

![](https://image.3001.net/images/20230803/1691026748_64cb053cd9b5b011d71a8.png!small)19\.
这里发现用的框架为Express。通常情况下，用的是mongdb数据库，尝试nosql注入。参考链接如下：

<https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection#exploits>

20\. 修改payload。

注意：需改动未Content-Type: application/json。

{"user": {"$ne": null}, "password": {"$ne": null}}

21.成功进入后台。

![](https://image.3001.net/images/20230803/1691026762_64cb054a07f7619188832.png!small)

##  **PART.02 渗透过程**

1\. 新建文章。

![](https://image.3001.net/images/20230803/1691026773_64cb055500d9ae70f3b38.png!small)2\.
提交后服务报错，从报错信息中获取到了网站的物理路径。

![](https://image.3001.net/images/20230803/1691026786_64cb056290370aab63ada.png!small)3\.
存在上传功能点测试，返回非法的XML格式，并且发现数据库的请求头也是/articles/xml。查看是否存在xxe漏洞。

![](https://image.3001.net/images/20230803/1691026795_64cb056bcd1590ac8a499.png!small)4\.
尝试读取/etc/passwd文件，成功读取后确定存在xxe漏洞。

![](https://image.3001.net/images/20230803/1691026806_64cb057602ca2d2344743.png!small)5\.
就刚才获取到的网站物理路径，读取配置文件server.js的内容。

![](https://image.3001.net/images/20230803/1691026816_64cb05805d0c85a50c9ac.png!small)6\.
执行命令反弹shell到主机10.10.10.100。

![](https://image.3001.net/images/20230803/1691026827_64cb058b5245a4f73f887.png!small)![](https://image.3001.net/images/20230803/1691026836_64cb0594c2be418a1b24c.png!small)7\.
发现当前用户可以凭借root权限执行/bin/check文件。

![](https://image.3001.net/images/20230803/1691026850_64cb05a2bd8f5f7853b08.png!small)8\.
查看/bin/check文件，引用os.py。

![](https://image.3001.net/images/20230803/1691026861_64cb05ad6b2feae1ce3e5.png!small)9\.
此处直接修改os.py文件内容，以sudo的权限执行check文件即可提权（由于此处获取交互式shell就会系统停顿，所以没有继续提权）。

10\. 主机10.10.10.201开放了比较多的端口，首先访问80端口，但其web服务需要进行验证，利用弱口令admin，admin成功进入后台。

![](https://image.3001.net/images/20230803/1691026874_64cb05ba86b54b48b3a73.png!small)11\.
存在文件上传功能点，但是无论上传任何格式都能够成功返回，只是无法找到上传的路径。

![](https://image.3001.net/images/20230803/1691026884_64cb05c4af5c1632aed36.png!small)12.此处提示样本会上传到文件共享服务器，测试团队将手动审查上传的内容，构造SCF文件以索取ntlm
hash，并将文件上传到目标服务器。

![](https://image.3001.net/images/20230803/1691026893_64cb05cddab0aedb270c0.png!small)13\.
在跳板机上安装Respondr，并对其进行监听。

![](https://image.3001.net/images/20230803/1691026903_64cb05d70e6f9467e9b64.png!small)14\.
成功抓取到NTLMv2 Hash。

![](https://image.3001.net/images/20230803/1691026912_64cb05e0abc1e1f481d54.png!small)15\.
使用hashcat破解。

hashcat -m 5600 hash.txt rockyou.txt

![](https://image.3001.net/images/20230803/1691026924_64cb05ecb63a729e74e27.png!small)16\.
破解出密码为tobyallison31。此外，目标机器开放了5985端口，使用evil-winrm进行连接。

![](https://image.3001.net/images/20230803/1691026935_64cb05f74a4f97f601f5d.png!small)17\.
生成正向木马bind.exe，上传到该目标机器后获取到meterpreter。

![](https://image.3001.net/images/20230803/1691026946_64cb06020ea1b42b313a7.png!small)18\.
查看powershell的历史记录，发现他下载并开启了Goservice服务，我们可以替换文件来进行提权。

![](https://image.3001.net/images/20230803/1691026958_64cb060e16ad420971615.png!small)19\.
暂时停止服务。

![](https://image.3001.net/images/20230803/1691026970_64cb061aa0d7cdf89c166.png!small)![](https://image.3001.net/images/20230803/1691026980_64cb06247f882176fc6d4.png!small)20\.
将bind.exe上传到目录，并重命名为service.exe。

![](https://image.3001.net/images/20230803/1691026990_64cb062e9622f5bd899cc.png!small)21\.
重新启动GoService服务。

![](https://image.3001.net/images/20230803/1691026998_64cb0636e0391cd5943f6.png!small)22\.
成功返回一个meterpreter且权限为system权限。

![](https://image.3001.net/images/20230803/1691027008_64cb06405402a6ff89d9c.png!small)

