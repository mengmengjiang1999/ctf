**近期“网页挖矿”出现在了我们的视野。网页挖矿是一种利用网站前端javascript进行挖矿的一种行为，目前主要利用CoinHive和JSEcoin这两个手段进行网页挖矿，除此之外还有利用Webmine，Cryptoloot，Webmine等进行挖矿。**

通过对近期出现的“网页挖矿”事件的分析，发现几乎都是利用Coinhive。

![图片1.png](https://image.3001.net/images/20181120/1542695799_5bf3ab77112d7.png!small)

整个攻击过程一般都是通过某些web漏洞对网站的文件进行篡改，这个操作往往不需要太高的系统权限，整个过程也非常容易操作。

![图片.png](https://image.3001.net/images/20181120/1542696124_5bf3acbc025e7.png!small)![图片.png](https://image.3001.net/images/20181120/1542696129_5bf3acc1e538f.png!small)
![图片.png](https://image.3001.net/images/20181120/1542696135_5bf3acc7e99e5.png!small)![图片.png](https://image.3001.net/images/20181120/1542696142_5bf3acce47ab8.png!small)

到这一步就完成了整个网页挖矿病毒的构建。

这种挖矿与普通的挖矿不同，采用coinhive网页挖矿是攻击者将自己的钱包地址给了第三方，然后通过与第三方的代理矿池交互去实现的网页挖矿。第三方会收取一定的比率的算力，是一种代理挖矿的模式。

##
![图片.png](https://image.3001.net/images/20181120/1542696149_5bf3acd5bf8ea.png!small)流程：

1.受害者访问了被黑客挂了JS挖矿代码的网站；

2.之后，受害者的浏览器会请求coinhive服务器中的coinhive.min.js文件；

3.执行coinhive的JS代码，会去请求代理矿池；

4.开始与代理矿池交互；

5.代理矿池会与总矿池交互；

6.在代理矿池中挖取的门罗币币会弄到黑客提交的钱包地址里面；

## 一、攻防演练  

为了清楚了解coinhive网页挖矿的攻击过程，我们搭建了如下的拓扑图：

![图片.png](https://image.3001.net/images/20181120/1542696205_5bf3ad0d18cfd.png!small)

PS.部署AF，仅启用访问控制，模拟真实环境，其他功能及安全感知平台仅做监控。

![图片.png](https://image.3001.net/images/20181120/1542696222_5bf3ad1e2ea4a.png!small)

目标某日访问量400+IP站点，各种扫描探测工具一通扫描，发现了目标站点存在Struts2漏洞：

![图片.png](https://image.3001.net/images/20181120/1542696229_5bf3ad25f2f9a.png!small)

一下子就发现可以直接命令执行的漏洞，赶紧看看目标站点的具体信息，方便等会修改POC脚本使用。

![图片.png](https://image.3001.net/images/20181120/1542696240_5bf3ad309d2a7.png!small)

网上找了一个s2-045的Poc，动手修改后就将攻击脚本上传到之前抓到的肉鸡上。

启动攻击脚本，输入存在漏洞的目标URL开始攻击：

![图片.png](https://image.3001.net/images/20181120/1542696251_5bf3ad3b8ddba.png!small)![图片.png](https://image.3001.net/images/20181120/1542696255_5bf3ad3fbbb19.png!small)

脚本执行完后的成功后，打开了火狐浏览器确认一下是否已经植入成功，访问目标站点的任意页面可以看到文本末尾添加了coinhive的js代码，这时候就可以等待收获了：

![图片.png](https://image.3001.net/images/20181120/1542696265_5bf3ad4933f4b.png!small)

小白作为这个网站的常客，经常在这个网站观看视频，最近发现浏览网站的时候电脑非常卡，CPU利用率很高：

![图片.png](https://image.3001.net/images/20181120/1542696276_5bf3ad54e0ac7.png!small)

但只要关闭网站，CPU就恢复正常了：

![图片.png](https://image.3001.net/images/20181120/1542696287_5bf3ad5fba19c.png!small)

## 02攻击详解  

### **漏洞利用分析** ****

Str2_045漏洞的利用代码，构造了相应的exp，能够通过输入存在漏洞页面，然后执行cmd指令：

![图片.png](https://image.3001.net/images/20181120/1542696311_5bf3ad773a794.png!small)

### **运行指令分析** ****

写入covin.js文件的base64编码，写入的文件为evil.txt，为下一步做准备：

![图片.png](https://image.3001.net/images/20181120/1542696320_5bf3ad80e4707.png!small)![图片.png](https://image.3001.net/images/20181120/1542696325_5bf3ad8520498.png!small)

对evil.txt进行base64解码，解码文件为evil.ps2，这是一个可执行的shell文件：

![图片.png](https://image.3001.net/images/20181120/1542696332_5bf3ad8c80f8c.png!small)![图片.png](https://image.3001.net/images/20181120/1542696336_5bf3ad907c7a6.png!small)

最后使用powershell执行shell文件，对网站下的文件植入挖矿代码：

![图片.png](https://image.3001.net/images/20181120/1542696344_5bf3ad985e4e1.png!small)![图片.png](https://image.3001.net/images/20181120/1542696348_5bf3ad9c27931.png!small)Powershell脚本文件如下：

![图片.png](https://image.3001.net/images/20181120/1542696356_5bf3ada448659.png!small)

植入的挖矿代码如下：

![图片.png](https://image.3001.net/images/20181120/1542696367_5bf3adaf401d2.png!small)

![图片.png](https://image.3001.net/images/20181120/1542696429_5bf3aded5c878.png!small)
**网站运营方：**

> 定时对网站进行扫描；
>
> 及时修复网站漏洞；
>
> 及时给电脑打补丁，修复漏洞；
>
> 安装专业的服务器安全防护软件；
>
> 关闭不必要的目录权限。

 **网站浏览者：**

> 开启浏览器内置拦截功能；
>
> 安装拦截插件进行防范；
>
> 安装“反挖矿”安全防护软件。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

