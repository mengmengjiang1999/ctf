本文作者：Lof-X

本文将带你如何通过家庭网络生成 2TB/s 的反射型 DDoS 数据流~~~

我们都听说过DOS攻击，DDOS攻击，那什么是DRDos攻击呢？ R是反射的意思。

这里我们就来实践一下基于Memcache 作为 DRDoS 反射放大器进行 DDoS 攻击。

![Memcache-DRDos实践-实现核弹级DDoS攻击164.png](https://image.3001.net/images/20180305/15202165445933.png!small)

图片来源：thehackernews

 **实验环境：**

1、Memcache 开启udp监听

2、Memcache 不开启认证

先安装一下Memcache

![image.png](https://image.3001.net/images/20180305/15202165745815.png!small)  

install memcached  

启动memcached服务，memcached服务默认端口是11211，可以自定义，这里就设置为6666吧

![image.png](https://image.3001.net/images/20180305/15202167345401.png!small)  

开启服务  

这里需要用到python的memcache模块，先安装一下，用pip安装就好

![image.png](https://image.3001.net/images/20180305/15202167806390.png!small)  

install python-memcached  

先开启memcache的调试，然后插入一些数据

  
![image.png](https://image.3001.net/images/20180305/15202168205634.png!small)  

Insert Data  

来看一下发生数据和返回数据的差距，构建请求发出去

![image.png](https://image.3001.net/images/20180305/15202168491721.png!small)  

发生数据  

![image.png](https://image.3001.net/images/20180305/1520216870818.png!small)  

服务端  

可以看到发出去16字节，但是返回的字节是1937个字节

1937/16=121.0625倍

还不够大么，那再来个大的

![image.png](https://image.3001.net/images/20180305/15202169062065.png!small)  

发生数据  

![image.png](https://image.3001.net/images/20180305/15202169317616.png!small)  

服务端  

发出去58字节，收到543224字节

543224/58=9365.93倍

这一个就那么厉害，如果更多那后果可想而知~~~~

全球开放的Memcache有数十万之多

![image.png](https://image.3001.net/images/20180305/15202169674045.png!small)  

图片来源：thehackernews  

 **修复建议：**

1、禁用UDP

2、禁止外网访问

3、启用授权访问

  

参考：

[简单实践传说中的2T/S的DRDoS | giantbranch's
blog](http://www.giantbranch.cn/2018/01/21/%E7%AE%80%E5%8D%95%E5%AE%9E%E8%B7%B5%E4%BC%A0%E8%AF%B4%E4%B8%AD%E7%9A%842T%E6%AF%8F%E7%A7%92%E7%9A%84DRDoS/)

[Deluge – How to generate 2TB per seconds reflection DDoS data flow via a
family network]()

