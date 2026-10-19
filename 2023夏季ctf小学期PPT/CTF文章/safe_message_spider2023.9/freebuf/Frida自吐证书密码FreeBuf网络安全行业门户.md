## 双向认证APP自吐密码

在许多业务非常聚焦比如行业应用、银行、公共交通、游戏等行业，C/S架构中服务器高度集中，对应用的版本控制非常严格，这时候就会在服务器上部署对app内置证书的校验代码。  
抓包出现如下提示时，我们确定出此APP为服务器校验app客户端证书。  
![16109571246016.jpg](https://image.3001.net/images/20220427/1651050263_62690717ad6020ec4779a.jpg!small)  
对于此类APP抓包而言通常需要完成两项内容：

    
    
    找到证书文件
    找到证书密码

服务器对客户端进行校验过程中，客户端将证书公钥发送给服务器，以及从服务器获取session和私钥解密过程中，需要API进行操作，API存在于java层框架内，所以hook框架层代码`java.security.KeyStore`，使密码自吐

    
    
    # frida -U -f cn.soulapp.android -l ssl.js  --no-pause

![16073502829536.jpg](https://image.3001.net/images/20220427/1651050265_6269071947279c18e79f1.jpg!small)密码}%2R+\OSsjpP!w%X

然后首先使用常规方式解压搜索app包里的证书文件。一般apk进行解包，直接过滤搜索后缀名为p12的文件即可，一般常用的命令为tree -NCfhl
|grep -i p12，直接打印出p12文件的路径.  
![16073512819331.jpg](https://image.3001.net/images/20220427/1651050268_6269071c7d779bee711e7.jpg!small)  
如果在安装包内找不到证书的话，也可以进行hook`java.io.File`

    
    
    # android hooking watch class_method java.io.File.$
    init

![16073515077217.jpg](https://image.3001.net/images/20220427/1651050269_6269071da2f3a0a12e435.jpg!small)  
通过hook也可以找到该证书文件。

    
    
    # objection -g cn.soulapp.android explore --startup-command "android hooking watch class_method java.io.File.$init  --dump-args"

使用抓包工具点击导入证书  
![16073520401809.jpg](https://image.3001.net/images/20220427/1651050271_6269071fb7dd4f7001fd0.jpg!small)密码随意设置

然后进去之后导入p12证书和密码（自吐出的密码），host和port输入*  
![16073521893292.jpg](https://image.3001.net/images/20220427/1651050272_6269072079cdac126c6b2.jpg!small)  
可以看到可以成功抓到了数据包  
![16073523304294.jpg](https://image.3001.net/images/20220427/1651050273_626907218799c5712f4be.jpg!small)

## hook抓包

1、首先确定使用的框架，主流框架okhttp、HttpURLconnection  
使用objection打印内存中所有的类

    
    
    # android hooking list classes

然后搜索过滤类文件中值得怀疑的框架

    
    
    .objection # cat objection.log |grep -i volley
    .objection # cat objection.log |grep -i okhttp
    .objection # cat objection.log |grep -i

![16110423560128.jpg](https://image.3001.net/images/20220427/1651050275_62690723d0dbdcfe48633.jpg!small)  
![16110425584094.jpg](https://image.3001.net/images/20220427/1651050277_6269072507ea79c5dca77.jpg!small)  
![16110425790976.jpg](https://image.3001.net/images/20220427/1651050277_626907259b7185bd69af7.jpg!small)  
找到APP使用的框架后，最后通过frida加载js脚本来进行绕过。

## ZenTracer

批量hook查看调用轨迹的工具ZenTracer

    
    
    # git clone https://github.com/hluwa/ZenTracer

点击Action之后，会出现匹配模板（Match RegEx）和过滤模板（Black
RegEx）,将`M:java.net.HttpURLConnection`填入后会将该类的所有方法进行hook并运行  
![16110453059250.jpg](https://image.3001.net/images/20220427/1651050278_626907267669aac6034ec.jpg!small)  
同时手机点击登录、注册等功能模块时，发现经过了该方法`java.net.HttpURLConnection.getFollowRedirects()`：  
![16110454137918.jpg](https://image.3001.net/images/20220427/1651050279_62690727497a44b17b899.jpg!small)  
然后使用`objection`hook该方法

    
    
    # android hooking watch class_method java.net.HttpURLConnection.getFollowRedirects --dump
    -args --dump-return --dump-backtrace

![16110464267917.jpg](https://image.3001.net/images/20220427/1651050280_6269072873ec66d6dd87e.jpg!small)  
根据打印出的`com.cz.babySister.c.a.a(HttpClients.java:22)`  
直接定位到了收发包函数的地址，然后查看收发包的内容如下：

    
    
    # android hooking watch class_method com.cz.babySister.c.a.a --dump-args --dump-backtrace --dump-return

![16111086981296.jpg](https://image.3001.net/images/20220427/1651050282_6269072a4a198b7e62a3c.jpg!small)

## 强混淆APP

使用工具OkHttpLogger-Frida  
1、首先将okhttpfind.dex 拷贝到手机 /data/local/tmp/目录下

    
    
    # adb push okhttpfind.dex /data/local/tmp/
    # chmod 777 *

2、执行命令启动frida -U -l okhttp_poker.js -f com.example.demo --no-pause 可追加 -o
[output filepath]保存到文件

    
    
    # frida -U -l okhttp_poker.js -f org.sfjboldyvukzzlpp --no-pause

![16111301516468.jpg](https://image.3001.net/images/20220427/1651050284_6269072c645bea0767b0d.jpg!small)  
然后复制被混淆后的类名，粘贴到okhttp_poker.js文件中，重新运行后运行`hold()`开启hook拦截，然后操作App后，会出现拦截的内容如下

    
    
    # nano okhttp_poker.js

![16111308848904.jpg](https://image.3001.net/images/20220427/1651050286_6269072e7f33deee1e486.jpg!small)  
当然除了ZenTracer，也可以直接使用objection工具进行批量hook，  
首先将怀疑的类复制保存到文件中，并在保存内容前加上`android hooking watch class`

    
    
    # android hooking list classes
    # objection -g com.cz.babySister explore -c "/root/Desktop/2.txt"

## 参考资料

<https://www.anquanke.com/post/id/197657>  
<https://bbs.pediy.com/thread-258776.html>

