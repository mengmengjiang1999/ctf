> 细心到极致方可不错失漏洞。

## 事情起因

在某次难度较高的众测项目中，笔者遇到了一个看起来”绝对安全的系统“，项目上线几天后此系统仍然没有被测试出漏洞，在没有系统功能、各种访问404的、没有测试账户的情况下，仍然揪出了隐藏在角落的漏洞，获得了高额赏金，算是在挖洞的道路上越走越远了，哈哈~

本文分享在此漏洞挖掘过程中的一些心得和经验，希望大家看完能多多少少获取到一些帮助。

## 资产初步探测

首先拿到仅有的一条URL访问： **http://***.com/** ，如下图。

直接跳转到： **http://***.com/#/default**

并且页面回显：“亲！是不是迷路了。”

![](https://image.3001.net/images/20201124/1606154543_5fbbf92fa717dd1a290b9.png)

看到跳转到/#/目录下，可能会有许多渗透测试经验多的同学们，已经看出来了，可能是Webpack。

F12审计源代码：

![](https://image.3001.net/images/20201124/1606154593_5fbbf961d59ca8d4a5bbd.png)

并未发现前端Webpack打包器，应该是将其隐藏了，或者需要用户登录到后台才可以看到Webpack。

这不是摆明了让人怼404页面吗，凭本人多年大战登录框的经验来讲，还是可以搞一搞的。

使用Wappalyzer插件进一步确认前端框架：

![](https://image.3001.net/images/20201124/1606154620_5fbbf97c063a4918a5f51.png)  

不出所料，前端H5，Web容器为Nginx，JavaScript框架为Vue.js

尝试对网站的根目录进行目录扫描、以及敏感文件扫描，皆无果，没有功能点，没有测试用户，也无法进行注册，接下来要怎么办呢？

## 基础信息收集

渗透测试进行到这一步，网站基本信息也掌握了，没有功能点可以测试，也没有测试用户可以登录，可能大多数童鞋到这一步也就放弃进行下一个目标了，不可以，如果每次都不尝试进行挖掘，久而久之你就会怕了他的！

此时，发现系统自动跳转时加载了/openh5/目录：

![](https://image.3001.net/images/20201124/1606154724_5fbbf9e4762ca095a9f3e.png)

尝试直接访问这个/ **openh5/** 目录： **http://***.com/openh5/**

果不其然，又是这个令人讨厌的界面。

![](https://image.3001.net/images/20201124/1606154749_5fbbf9fdcc4866b924e78.png)

测试随便输入一个一级目录访问： **http://***.com/open/**

嗯，Nginx欢迎你~

![](https://image.3001.net/images/20201124/1606154778_5fbbfa1a45916f0709813.png)

  

但是这个访问测试让我们确信了一个事情：既然访问 **/openh5/** 和根目录都会跳转到此页面，就说明这个系统一定是存在接口调用的。

在走投无路的情况下，也只有查看JavaScript代码了。

首先对 **/openh5/MobileJS-1.0.6.js**
文件进行分析，发现大多为相似的功能函数，看代码应该是拉起手机的某些功能，并未发现敏感的路径或接口信息。

![](https://image.3001.net/images/20201124/1606154806_5fbbfa36d660c83764195.png)

 **/openh5/js/approval.b9e9dbb0.js** 、
**/openh5/js/chunk-f259caf6.24653188.js** 中仅有几行代码，无敏感信息，遂放弃；

 **/openh5/js/chunk-vue.eefbe893.js** 、 **/openh5/js/chunk-libs.722ca693.js**
为 **Vue.js** 的模板文件，放弃；

在剩下的3个JavaScript文件中，着重审计如下两种格式的信息：

    
    
    0  -  http://xxx.com/xxx 或 https://xxx.com/xxx
    1  -  /aaa/bbb

第一种为代码可能会远程调用的URL，第二种问系统可能存在的接口地址。

通过如上所述方式，共计提取到了如下几个目录信息：

    
    
    /data_marxxx
    /cloud/user_xxxxx/user/list
    /cloud/order/
    /process
    /process/hanxxx
    /process/addCounterxxxxxx
    /cloud/asset/authxxxxx/search

拼接URL访问第一个目录： **http://***.com/data_marxxx**

访问发现了一个Tomcat的404页面。

![](https://image.3001.net/images/20201124/1606154951_5fbbfac71c2d738c290c9.png)

拼接第二个URL进行访问： **http://***.com/cloud/user_xxxxx/user/list**

又是Nginx欢迎界面。

![](https://image.3001.net/images/20201124/1606154976_5fbbfae03817fb06bca71.png)

剩下的5个地址拼接后，依旧是Nginx的404 Not Found

猜测可能这几个接口之前会有个一级目录，类似于： **/api/** 、 **/manage/** 、
**/admin/**......诸如此类的一级目录，但是一番Fuzz后无果，遂放弃。

此时已经没有下一步的思路了，于是反复回档之前收集到的信息，突然发现了一个非常可疑的点，不知道细心的同学有没有发现：为什么访问
**/data_marxxx** ，回显的是Tomcat的404 Not Found而不是Nginx的呢？

![](https://image.3001.net/images/20201124/1606155013_5fbbfb05123ff6c11d239.png)![](https://image.3001.net/images/20201124/1606155029_5fbbfb15217be206b0214.png)

答案是 **SpringBoot** 。

>
> Spring框架是Java平台上的一种开源应用框架，提供具有控制反转特性的容器。尽管Spring框架自身对编程模型没有限制，但其在Java应用中的频繁使用让它备受青睐

这说明 **/data_marxxx** 目录是存在的，并且使用Tomcat搭建了SpringBoot接口服务。

但是为什么不是熟悉的SpringBoot报错页面呢？想象中的SpringBoot应该是下面这种：

![](https://image.3001.net/images/20201124/1606155070_5fbbfb3ee5fc71da4492f.png)

这说明：还有一层目录才能够到达SpringBoot的目录！

信息收集到达这一步后，瞬间燃起来对接下来挖掘漏洞的激情，已有的信息收集和多年渗透测试经验让我觉得他一定是有漏洞的。

## 拨开迷雾见光明

既然已经想明白了 **/data_marxxx** 目录实际是存在的，并且它的下一层目录就是SpringBoot，于是访问 **/data_marxxx**
并抓取GET数据包，丢在Burpsuite中进行二级目录爆破。

![](https://image.3001.net/images/20201124/1606155110_5fbbfb6640a48469ffe95.png)

放入目录字典进行Fuzz测试，这里选择使用Burpsuite的原因是，SpringBoot目录的访问报错，状态码依然是404，而使用Burpsuite的返回值Length长度，可以轻松筛选出是否成功爆破到了SpringBoot目录。

爆破URI时，需要在Burpsuite中勾掉默认的URLEncode选项：

![](https://image.3001.net/images/20201124/1606155143_5fbbfb8751a919cd436e8.png)

接下来就是静等结果了，一般爆破目录不附带恶意Payload的话，WAF基本不会拦截的，除非有防DDOS、CC攻击的设备，线程调小也可以避免被Ban自己的IP。

功夫不负有心人，成功爆破到了状态码为404的SpringBoot报错页面！

![](https://image.3001.net/images/20201124/1606155168_5fbbfba0dad182ae57f2a.png)

拼接访问： **http://***.com/data_marxxx/cloud/**

果然是你，我亲爱的SpringBoot老朋友。

![](https://image.3001.net/images/20201124/1606155333_5fbbfc4519262b32ba12b.png)

原本以为隐藏的这么深的SpringBoot页面，肯定会有SpringBoot的信息泄露漏洞，运气好的话还可能有代码执行RCE，于是使用SpringBoot敏感目录扫描：

![](https://image.3001.net/images/20201124/1606155369_5fbbfc692a7f73dd291a3.png)

但是使用SpringBoot敏感目录字典扫描后发现，一个也没有！

就连接口文档 **swagger-ui.html** 也删除的干干净净。

![](https://image.3001.net/images/20201124/1606155399_5fbbfc87cce518405e679.png)

那这样的话，就连SpringBoot信息泄露都没有了。

就在我垂头丧气的时候，突然灵光一闪想到了一开始在JavaScript文件中获取到的另外几个路径。

    
    
    /cloud/user_xxxxx/user/list
    /cloud/order/
    /process
    /process/hanxxx
    /process/addCounterxxxxx
    /cloud/asset/authxxxxxxxx/search

cloud这不是你吗？？？直接拼接访问：

 **http://***.com/data_matxxx/cloud/user_xxxxx/user/list**

这特喵的，直接当场跪了！

 **第一个漏洞：未授权调用系统接口查询全部用户数据。**

![](https://image.3001.net/images/20201124/1606156073_5fbbff291429287e4be56.png)

之后就顺利多了，拼接 **/data_marxxx/cloud/order** ，后面再跟一个ID参数，回显了如下数据。

![](https://image.3001.net/images/20201124/1606155485_5fbbfcdd14237b599ab8a.png)

需要在Cookie加入 **user_code** 参数，而 **user_code** 参数，存在于第一个漏洞的回显数据中。

![](https://image.3001.net/images/20201124/1606155506_5fbbfcf285511f404c3fb.png)

并且，只需Cookie就可以查询数据，并且数据编号可以全部遍历。

 **于是，第二个漏洞产生：越权查询全部系统流程数据。**

## 回首总结

此漏洞的挖掘到这里也可以结束了，但是回过头来才发现，一开始筛选出6个接口时，如果更细心、更脑洞大开一点的话，或许直接拼接也不用走那么多弯路。

并且，后来在审计JavaScript的代码逻辑中，细心一点是可以看出地址拼接的逻辑的，如下：

![](https://image.3001.net/images/20201124/1606155543_5fbbfd17675945415baef.png)

关键代码为：

    
    
    H="/data_marxxx"
    z.get("".concat(H,"/cloud/order/")

其实已经可以发现 **data_marxxx** 与 **cloud**
拼接了，但是面对如此复杂并且杂乱的JavaScript代码，又有几个人能静下心来慢慢审计呢？

一句话概括此次挖掘漏洞过程：细心到极致方可不错失漏洞。

希望这个简单的漏洞挖掘过程，能给大家带来一些挖洞思路~

谢谢大家！

