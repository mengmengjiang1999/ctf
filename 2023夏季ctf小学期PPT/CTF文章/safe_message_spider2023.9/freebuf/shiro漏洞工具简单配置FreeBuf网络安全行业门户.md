## 工具下载：

工具地址：https://github.com/feihong-cs/ShiroExploit

使用环境：java8

运行命令：java -jar ShiroExploit.jar

![1656943828_62c2f4d43c8078adeab8a.png!small?1656943828086](https://image.3001.net/images/20220704/1656943828_62c2f4d43c8078adeab8a.png!small?1656943828086)

## 工具配置：

### 配置ceye域名和对应的 Token：

当然工具中默认配置的有对应的域名和token值，如果当访问的人过多时，难免会有一些问题导致检测不准确，这里可以自己手动配置自己对应的域名和token值。

打开config目录下的config/config.properties文件，内容为

    
    
    rememberMeCookieName=rememberMe
    ceyeDomain=xxxxx.ceye.io
    ceyeToken=xxxxxxxbdb36c8d1d99a2a1
    JRMPRequestDelay=2
    fetchDNSLogResultDealy=5

将ceyeDomain和ceyeToken替换成自己的域名和token。到http://ceye.io/注册后，会获得相应的域名和token值。

![1656944369_62c2f6f1752c706d5b250.png!small?1656944369289](https://image.3001.net/images/20220704/1656944369_62c2f6f1752c706d5b250.png!small?1656944369289)

检测的时候就可以用ceye.io进行检测，自己也能实时的查看。在这里也推荐使用ceye.io进行检测，少数时候 dnslog.cn 会间隔较久才显示 DNS
解析结果导致程序无法找到 Key 或者有效的 Gadget，且 dnslog.cn 只会记录最近的10条 DNS 解析记录。

![1656944630_62c2f7f686dc0d88c375d.png!small](https://image.3001.net/images/20220704/1656944630_62c2f7f686dc0d88c375d.png!small)

![1656944699_62c2f83b56a1eac4e3ad6.png!small?1656944699286](https://image.3001.net/images/20220704/1656944699_62c2f83b56a1eac4e3ad6.png!small?1656944699286)

### cookie标识符的配置：

我们知道shiro框架最明显的特征就是返回的cookie中有rememberMe这个字样，拓展一下，如果返回的cookie有xxxrememberMe字样是不是也有可能是shiro框架，而shiro检测工具只默认检测含有rememberMe在返回包的数量来确定漏洞，打开config/config.properties文件，修改rememberMeCookieName=rememberMe为实际遇到的cookie内容，例如rememberMeCookieName=xcbgv-rememberMe等。

### key值的配置：

shiro漏洞最重要的就是这个key值，这个shiro漏洞检测工具默认情况下只会检测config/keys.conf下的这个值，打开后不难发现这个key值才几十个。

在这里有两种方法来进行配置，第一种就是在网上找shiro有关的key值然后自己把它复制到这个keys.conf文件里面；第二种方法在config/keys.conf.big文件中给出了170多个key值，一般够用了，在我们检测的时候勾选该选项就可以调动里面的key值。

![1656945216_62c2fa405aca4b6a04935.png!small?1656945216221](https://image.3001.net/images/20220704/1656945216_62c2fa405aca4b6a04935.png!small?1656945216221)

### webshell配置：

config/shell.jsp文件式shiro工具上传webshell时默认的木马文件路径，当然这里也是可以修改的，这里你可以修改成冰蝎马，哥斯拉，蚁剑等你想上传的类型。

## 检测方式：

### jrmp+dnslog检测：

最常用就是ceye.io和dnslog检测，这里主要讲一下使用jrmp+dnslog进行检测，因为该检测方式能够明显的减小cookie大小，并且经过测试发现检测的时间间隔明显变大，发包的频率明显减慢，对于这个过程可以自行抓包进行对比。这对绕waf是有一些作用。

  1. vps输入启动命令：java -cp ShiroExploit.jar com.shiroexploit.server.BasicHTTPServer [HttpSerivce Port] [JRMPListener Port] ![1656948327_62c30667794b64944fcc9.png!small?1656948327441](https://image.3001.net/images/20220704/1656948327_62c30667794b64944fcc9.png!small?1656948327441)

  2. 选择检测方式：![1656948442_62c306da8967cea4194b5.png!small?1656948442415](https://image.3001.net/images/20220704/1656948442_62c306da8967cea4194b5.png!small?1656948442415)

  3. 效果：![1656948500_62c30714e84b2275e2212.png!small?1656948500898](https://image.3001.net/images/20220704/1656948500_62c30714e84b2275e2212.png!small?1656948500898)

## 检测效果对比：

使用ceye或者dnslog检测所对应的cookie值：

![1656948607_62c3077f49165ca5a1726.png!small?1656948607368](https://image.3001.net/images/20220704/1656948607_62c3077f49165ca5a1726.png!small?1656948607368)

使用jrmp检测所对用的cookie值：

![img](https://image.3001.net/images/20220705/1656989657_62c3a7d994f37ed4e2a08.png!small)

明显小了很多，看上去更像是一个正常的cookie值的长度，这种方式对于绕过一些waf来说还是可以选择的。

