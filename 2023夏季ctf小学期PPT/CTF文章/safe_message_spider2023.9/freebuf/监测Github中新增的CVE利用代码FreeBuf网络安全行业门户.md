一款每隔 3 分钟检索`github`新增的`cve`工具。

## 0x00 前言

`hw`期间的某一天，我正兴致勃勃的刷着微步上待更新的小说，忽而发现万花丛中一点绿，有一篇认真推荐工具的帖子，虽然只有个链接......

好奇心驱使我点了进去，然后就有了这篇文章......

你有没有为每次手动刷新`github`却找不到更新的`cve`而苦恼？

有的话，请往下看。

![3f13f12524393897ad90524a0fc5c346](https://image.3001.net/images/20210513/1620887631_609cc84fcecee83be5f0e.jpg!small)

## 0x01 项目介绍

该项目旨在监控`github`上新增的`cve`编号项目漏洞，每 3
分钟检索一次`github`是否有新的`cve`提交记录，有则推送钉钉群或者`server`酱（二者配置一个即可）。

项目地址`github-cve-monitor`：<https://github.com/yhy0/github-cve-monitor>

叮！您有新的消息需要阅读~

    
    
    有新的 `CVE` 送达！
    ('007', '"description":you are so beautiful！,"fork"', 'https://github.com/xxxx/cve-可以是2021年-你想要的 poc')
    

## 0x02 部署过程

### 2.1 钉钉机器人配置

1、建立钉钉群，需至少3人。

2、配置钉钉机器人：

打开电脑版钉钉，点击头像->机器人管理

![7f51fd92cf9ed75fe37b8481d1901d6a](https://image.3001.net/images/20210513/1620887636_609cc8547eff9abd7dd1e.png!small)

添加自定义机器人：

![72868ec65dba9f82f75ecc9ef88c3833](https://image.3001.net/images/20210513/1620887642_609cc85a3ef9f5f2a4177.png!small)

接收群组：推送消息的群；

安全设置要求必须选填一组；

![a54daf10fe9b8dbd529a68cf25465599](https://image.3001.net/images/20210513/1620887652_609cc864c4d2944d29e40.png!small)

安全设置：

（1）自定义关键词:

最多可以设置10个关键词，消息中至少包含其中1个关键词才可以发送成功。

例如添加了一个自定义关键词：监控报警，则这个机器人所发送的消息，必须包含监控报警这个词，才能发送成功。

（2）加签:

把`timestamp+"\n"`+密钥当做签名字符串，使用`HmacSHA256`算法计算签名，然后进行`Base64
encode`，最后再把签名参数再进行`urlEncode`，得到最终的签名（需要使用`UTF-8`字符集）。

把`timestamp`和第一步得到的签名值拼接到URL中。根据加密规则获得可以发送消息的地址，实现消息的推送。

（3）IP地址段：

设定后，只有来自IP地址范围内的请求才会被正常处理。支持两种设置方式：`IP`地址和`IP`地址段，暂不支持`IPv6`地址白名单，

3、机器人添加成功后，复制`webhook`地址。配置在`github_cve_monitor.py`34行
dingding函数中，粘贴`webhook`运行脚本即可。

![b4bfd5a04c87b0273caeae24c50a855b](https://image.3001.net/images/20210513/1620887658_609cc86a25469eb572a0f.png!small)

![d8f2b000b0059ac85b1247476a217058](https://image.3001.net/images/20210513/1620887664_609cc8701167175c9b3ae.png!small)

### 2.2`server`酱配置

1、登陆`server`酱：<https://sct.ftqq.com/>

2、`server`酱支持多个通道进行消息推送，我这里使用的`Bark ios`（因为我没有企业微信...），安卓可以选择`Android`。

![9ed027d32990785e06d7eccf48eed677](https://image.3001.net/images/20210513/1620887669_609cc875b7614715ca15f.png!small)

3、配置过程：

安装`app`；

复制服务器链接：

![310d217493c4d081e33ec33eaba6699e](https://image.3001.net/images/20210513/1620887675_609cc87b5640007569896.png!small)

点击APP右上角的`+`在服务器地址处填入以上地址，并保存：

![dbd7f3872f81189ce54016c4abe7491b](https://image.3001.net/images/20210513/1620887698_609cc892673f4d673637f.png!small)

刷新网页，再次选中`Bark`，应该已经可以看到`DeviceToken`了，此时保存即可：

![ce3628a7065453d4ccaf3310650b8a3a](https://image.3001.net/images/20210513/1620887704_609cc8985a47005d2bb71.png!small)

配置`sendkey`，注释钉钉推送即可：

![1fc203bfa92194a493aa45ff006c8589](https://image.3001.net/images/20210513/1620887711_609cc89f8f592e2ee20b5.png!small)

![b756679e80e6b09b047c07c19f549c74](https://image.3001.net/images/20210513/1620887719_609cc8a715dbd4d443925.png!small)

![545c3856e7525a536ba0fdc6beac0879](https://image.3001.net/images/20210513/1620887724_609cc8acc9dd7509be90a.png!small)

### 2.3 运行脚本

1、`vps`安装模块：

    
    
    python3 -m pip install dingtalkchatbot
    

2、`screen`运行脚本：

    
    
    screen -S github_cve			//创建一个screen，名字为github_cve，在新窗口运行本项目, 成功后直接叉掉该窗口, 项目就会在后台一直运行了
    
    screen -ls 		//查看创建的screen
    
    screen -r github_cve		//连接github_cve后台screen，如果存在的话
    

或者`nohup`运行脚本：

    
    
    nohup python3 github_cve_monitor.py &  //后台运行脚本
    

### 2.4 测试结果

钉钉推送：

![b7e6c7f368e6ea0539ee6a6dab57850c](https://image.3001.net/images/20210513/1620887735_609cc8b7c8bfba4811ae1.png!small)

`Bark`推送：

![536c9d0d09cc56fc329052c0994d7b9f](https://image.3001.net/images/20210513/1620887741_609cc8bd5f25c56d7f6cf.png!small)

推送成功！

## 0x03 总结

总的来说，过程还是挺简单的。

配置钉钉机器人的时候。开始一直以为添加的是`github`机器人，导致消息根本推送不成功，安全设置选的自定义关键词，设置的太严格导致过滤了很多推送，后来查了一下钉钉机器人的设置，很多人都喜欢使用加签，据说是比较方便的，可以自己研究一下。

配置`server`酱的话，确实踩了很多坑，因为`server`酱更新服务的原因，导致我一直在测试服务器链接和`sendkey`的区别，两者是都能推送消息的，但是服务器链接无法正常推送监测的`cve`信息。

就这样吧，总结完毕。

![adea36f1381b2e9b95df82075e9350eb](https://image.3001.net/images/20210513/1620887745_609cc8c186e47e2f1d15b.jpg!small)作者：goout

