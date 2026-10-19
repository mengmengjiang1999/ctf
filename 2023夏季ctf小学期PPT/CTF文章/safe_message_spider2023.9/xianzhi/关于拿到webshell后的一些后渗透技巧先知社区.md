关于拿到webshell后的一些后渗透技巧：

## 1：利用长亭牧云主机管理助手做权限维持

优点：免杀，C2该有的都有，开机后自动重启

缺点：对于windows主机有操作系统要求，不出网无法利用

使用方法：

<https://rivers.chaitin.cn/app/collie/>

liunx：

登录平台运行命令就行，

![](./img/3508134392306851177.png)

windows:

![](./img/5993469625411992721.png)

之后复制连接到浏览器下载exe安装

对于这个windwos还有一个缺陷就是你运行后，必须要上桌面点ok才能上线

![](./img/6690941331318649113.png)

从这里可以知道 目前之支持如下操作系统，当然一般做权限也是用linux做，windows做的太少

## 2：利用suo5注入内存马来达到代理稳定

下载地址：

<https://github.com/zema1/suo5>

优点：代理稳定，不出网和出网都能用，支持sock5全局代理，支持图形化，支持在 Nginx 反向代理和负载均衡场景使用

缺点：只支持jsp类，中间件

对于目前的攻防演练中，suo5已经成为了新型代理方法，拿到webshell后，只需找到web路径上传一个suo5.jsp就能代理进内网，不过也存在管理员删除jsp的情况，对于这种情况我们只需要将suo5注入内存

<https://github.com/zema1/suo5/blob/main/assets/Suo5Filter.java>

将Suo5Filter.java编译之后利用反序列化链生成payload即可

这里有个快速生成payload的方法

利用yakit的Yso-java

![](./img/2109822286964240525.png)

也可以利用

https: _//github.com/pen4uin/java-memshell-generator_

来注入内存马

参考文章：<https://mp.weixin.qq.com/s/oAiGWY9ABhn2o148snA_sg>

## 3：利用netspy快速探测内网存活网段

下载地址：<https://github.com/shmilylty/netspy>

优点：快速探测，方便fscan后续利用

缺点：流量太大，容易GG

进入内网后，如果内网很大，你总部能直接fscan -h 10.0.0.0/8直接扫吧，所以通过netspy来探测内网那些段可达，之后通过-hf指定可达内网段这样不好吗？

## 4：密码收集

这里不详细讲了直接丢个链接

<https://www.wangan.com/p/11v7106f0571bb5c>

![](./img/3782792020116754516.png)  
有些工具还有必要的，毕竟谁给你在现在开ide解密

## 5：政务电子网的进入方法

这里介绍一个最简单的方法，从县级入手，拿nday某些oa的直接咂进去，再看是否通59.xx.xx..xx的段

一般都是用友或者泛微,进去后直接拿netspy扫看通不通

