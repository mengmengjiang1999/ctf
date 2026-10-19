## 0x00 前言

得到通知需要对某单位内部员工进行一次钓鱼邮件演练，因为之前接触的不多，钓鱼只是娱乐性的自己钓自己，记录下思路和踩坑。

## 0x01 信息

通过沟通得到了以下信息：

钓鱼形式为外部链接钓鱼

共计千余个邮箱，全量测试

统计时间从发送邮件到第二天上班前

统计结果，需要统计哪个邮箱点击链接，哪个邮箱输入了数据

## 0x02 部署

结合需求信息，采取Gophish+ewomail，Gophish钓鱼服务，可记录到每个邮箱收信之后的操作，ewomail邮箱网关服务，主要记录下部署过程和踩坑。

首先是Gophish，无需安装，项目仓库直接下载对应的版本即可[gophish](https://github.com/gophish/gophish)

修改config.json，主要就是两个端口，注意下默认监听端口不要和已有服务冲突即可：

> {  
> "admin_server": {  
> "listen_url": "0.0.0.0:3333",  
> "use_tls": true,  
> "cert_path": "gophish_admin.crt",  
> "key_path": "gophish_admin.key"  
> },  
> "phish_server": {  
> "listen_url": "0.0.0.0:8083",  
> "use_tls": false,  
> "cert_path": "example.crt",  
> "key_path": "example.key"  
> },  
> "db_name": "sqlite3",  
> "db_path": "gophish.db",  
> "migrations_prefix": "db/db_",  
> "contact_address": "",  
> "logging": {  
> "filename": "",  
> "level": ""  
> }  
> }

根目录运行./gophish即可运行。

> 建议首次运行不加nohub，首次登陆需要随机生成的密码，当然，也可直接查看nohub文件查看

部署完成大体如下：

![](https://image.3001.net/images/20220705/1657001522_62c3d63257689faffba4a.png!small)首先配置Sending
Profiles，配置发件箱、smtp服务器信息，这里用163邮箱测试：

![](https://image.3001.net/images/20220705/1657001623_62c3d6979f86ffb05e947.png!small)

smtp端口默认25，但云主机默认封掉25端口，需要改变为465端口；

smtp服务的用户名就是邮箱账号，密码需要邮箱开启smtp服务之后得到的授权码，以163为例，设置→POP3/SMTP/IMAP选项开启SMTP服务，认证之后即可得到授权码，填入Password字段

然后发送测试邮件测试连通性，只需要填第三项的邮箱地址，其余选项可随意填写：

![](https://image.3001.net/images/20220705/1657001645_62c3d6ade6167eb868eb8.png!small)发送成功后，目标邮箱会收到如下邮件，证明连通性OK：

![](https://image.3001.net/images/20220705/1657001663_62c3d6bf921f26e5ee8f5.png!small)

接着配置Landing Pages，也就是钓鱼页面，可通过直接导入Site或直接编辑HTML两种方法配置页面：

实际中发现，有些网站导入效果不是很理想，例如使用mip22生成对外链接导入，它就变成了这个样子

![](https://image.3001.net/images/20220705/1657001683_62c3d6d32d750d6699034.png!small)预览一下页面，emmmmm：

![](https://image.3001.net/images/20220705/1657001694_62c3d6ded90f010ae0603.png!small)

很难受，有的网站导入效果好，有的网站导入效果就不好，比如说本次钓鱼是想用甲方的邮箱登录地址做链接，但是导进去发现，页面只有一个框框，一片漆黑，连登录框都没出来，暂时还没发现有什么特别好的办法。

然后是Email Templates，主要配置邮件正文内容，为了后续记录邮件是否打开，可勾选上
AddTrackingImage，它将会在发送的每份邮件源码上插⼊⼀个唯⼀特定的隐藏图⽚，当邮件被打开时，此隐藏图⽚则也会被请求，以此来检测该邮件是否被打开，AddFiles
则是给邮件添加附件。

如下是官⽅提供的其他可以使⽤的参数：

> {{.RId}}  
> {{.FirstName}}  
> {{.LastName}}  
> {{.Position}}  
> {{.Email}}  
> {{.From}}  
> {{.TrackingURL}}  
> {{.Tracker}}  
> {{.URL}}  
> {{.BaseURL}}

可先对上述参数进行测试：

![](https://image.3001.net/images/20220705/1657001736_62c3d7084f670a6aca70f.png!small)

Users & Groups就容易理解了，添加目标邮箱即可，不再赘述。

最终Campaigns下发任务

注意这里的URL，需要对应Gophish服务端监听的地址端口

![](https://image.3001.net/images/20220705/1657001752_62c3d718ddfc934afcc00.png!small)

确认无误之后，点击Launch，发送邮件，成功发送后，目标邮箱效果：

![](https://image.3001.net/images/20220705/1657001769_62c3d7290957ed776d7fc.png!small)如果用户点击了链接，在Gophish服务端，即可看到信息：

![](https://image.3001.net/images/20220705/1657001781_62c3d7357737007933307.png!small)

然后是Ewomail搭建：

项目地址：<https://gitee.com/laowu5/EwoMail><https://github.com/gyxuehu/EwoMail>

官方文档：<http://doc.ewomail.com/docs/ewomail/jianjie>

docker地址：<https://hub.docker.com/r/bestwu/ewomail>

源码安装，需要准备一台干净的CentOS系统

> 尝试此种方法，未知原因导致服务很不稳定，启动了一会儿webmail就登不上去了。

Docker简便安装，无需CentOS，xxx.com为申请的域名：

> docker run -d -h mail.xxx.com --restart=always \  
> -p 25:25 \  
> -p 109:109 \  
> -p 110:110 \  
> -p 143:143 \  
> -p 465:465 \  
> -p 587:587 \  
> -p 993:993 \  
> -p 995:995 \  
> -p 80:80 \  
> -p 8080:8080 \  
> -v `pwd`/mysql/:/ewomail/mysql/data/ \  
> -v `pwd`/vmail/:/ewomail/mail/ \  
> -v `pwd`/ssl/certs/:/etc/ssl/certs/ \  
> -v `pwd`/ssl/private/:/etc/ssl/private/ \  
> -v `pwd`/rainloop:/ewomail/www/rainloop/data \  
> -v `pwd`/ssl/dkim/:/ewomail/dkim/ \  
> \--name ewomail bestwu/ewomailserver

如果提示25端口被占用，执行systemctl stop postfix，之后再次安装；

或是修改10024端口，（执行上面那个应该就可以，此条留作备选）

![](https://image.3001.net/images/20220705/1657001818_62c3d75a2ae6527bb084f.png!small)

接着配置解析：<http://doc.ewomail.com/docs/ewomail/main_domain>

spf这里设置VP*S的地址，如果是127.0.0.1发件的时候可能提示spf check failed

一定是mail.xxx，不能直接解析xxx.com

DKMI这里，首先通过docker执行`docker exec ewomail amavisd
showkeys`获取，根据文档进行整理之后填入解析等待十分钟，再次执行`docker exec ewomail amavisd
testkeys`出现`TESTING#1: dkim._domainkey.xxx.com => pass`字样即为正确

![](https://image.3001.net/images/20220705/1657001837_62c3d76d34e31623568e4.png!small)

解析配置好之后，可通过域名进行访问，如果没配置也可直接IP访问

前端地址，重要！！需要先进行配置：

> http://mail.xxx.com.cn:8080/ //ewomail后台管理页面,admin/ewomail，管理smtp地址邮箱
>
>  
>
>
> http://mail.xxx.com.cn/?admin
> //rainloop管理后台，admin/12345，需要先登录进行域名添加及smtp服务联通测试
>
>  
>
>
> http://mail.xxx.com.cn/ //webmail邮箱页面，配置好前两步，可登录邮箱账户进行收发邮箱

![](https://image.3001.net/images/20220705/1657001872_62c3d790d076cf5da0e9d.png!small)![](https://image.3001.net/images/20220705/1657001880_62c3d798b8f87a5b6d1bc.png!small)![](https://image.3001.net/images/20220705/1657001891_62c3d7a390dcbfae8be70.png!small)

实际测试中发现，给企业邮箱发邮件可能会收到系统邮件提示550 Ip frequency limited，可能需要进行白名单设置，QQ邮箱可直接发送。

测试smtp服务，可通过以下脚本：

> #coding: utf-8  
> import time  
> import smtplib  
> from email.mime.multipart import MIMEMultipart  
> from email.mime.text import MIMEText  
> from email.header import Header
>
> smtpserver = 'smtp.xxx.com.cn:465'  
> username = 'admin@xxx.com.cn'  
> password = 'Admin123'  
> sender = 'admin@xxx.com.cn'  
> receiver = ['sssss@163.com']  
> # receiver = ['username1@qq.com', 'username2@163.com']
>
> msg = MIMEMultipart('mixed')  
> subject = '发送主题'  
> subject = Header(subject, 'utf-8').encode()  
> msg['Subject'] = subject  
> msg['From'] = 'admin <admin@xxx.com.cn>'  
> msg['To'] = '<sss@163.com>'  
> # msg['To'] = 'username1 <username1@163.com>; username2 <username2@163.com>'  
> msg['Date'] = '2021-1-26'
>
> text = "邮件正文"  
> text_plain = MIMEText(text, 'plain', 'utf-8')  
> msg.attach(text_plain)
>
> total = 1  
> send = 0  
> error = 0  
> while error < 2 and send < total:  
> try:  
> smtp = smtplib.SMTP()  
> smtp.connect('smtp.xxx.com.cn')  
> smtp.login(username, password)  
> while send < total:  
> smtp.sendmail(sender, receiver, msg.as_string())  
> print("第{}封邮件发送成功！".format(send+1))  
> send += 1  
> error = 0  
> time.sleep(0)  
> smtp.sendmail(sender, receiver, msg.as_string())  
> smtp.quit()  
> except Exception as e:  
> print("发生错误，重新发送",e)  
> error += 1  
> continue

![](https://image.3001.net/images/20220705/1657001922_62c3d7c24681a5451d557.png!small)

## 0x03 联动

经过实际测试，Gophish和Ewomail要在同一台VP*S下！

原本的想法是Ewomail在国外的VP*S，Gophish在阿里云，但是测试中发现这样配置Gophish无法通过Ewomail的smtp服务发送邮件，报错Max
connection attempts exceeded - dial tcp 127.0.0.1:465: connect: connection
refused

![](https://image.3001.net/images/20220705/1657001948_62c3d7dc01a0abba3c4f8.png!small)而在同一台VP*S下操作，就可以正常发送：

![](https://image.3001.net/images/20220705/1657001960_62c3d7e8a538e0044bae3.png!small)![](https://image.3001.net/images/20220705/1657001970_62c3d7f22ad692433cfdb.png!small)

至此，Gophish和Ewomail已经部署完成，接下来就是配置钓鱼页面准备猎杀时刻。

需要注意，一定要把Gophish的VP*S地址加白，原以为通过smtp发件显示的是smtp邮箱的地址，但实际上却是Gophish的地址，如果不加白会导致触发邮箱服务黑名单。

