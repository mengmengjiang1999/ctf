## **01** **判断SSRF是否存在**

### 1\. 访问http://www.badu.com网站。

  

![](https://image.3001.net/images/20230705/1688549150_64a5371e86d48fd1d1ebf.png!small)  
  

### 2\. dnslog平台收到回显，存在ssrf。

  

![](https://image.3001.net/images/20230705/1688549167_64a5372fd2ffc9268ab9c.png!small)  
  

### 3\. 尝试读取文件/etc/passwd，并返回内容，可以判断出是回显型ssrf。

  

![](https://image.3001.net/images/20230705/1688549226_64a5376a59ff0fe89e864.png!small)  
  

### 4\. 读取/etc/hosts文件，当前机器ip是172.72.23.21。

  

![](https://image.3001.net/images/20230705/1688549261_64a5378d4e0f4851e3a66.png!small)  
  

5\. 尝试读取/etc/shadow 和/root/.bash_histor，发现无权限。

  

  

 **02** **探测内网存活主机服务**

使用dict协议对内网主机进行存活探测。

![](https://image.3001.net/images/20230705/1688549277_64a5379d5b291087c58e4.jpg!small)  
  

 **03** **172.72.23.22—代码注入**

1\. 利用ssrf访问内网http://172.72.23.22，提示CodeExec。

![](https://image.3001.net/images/20230705/1688549471_64a5385f3eacd4d01b607.png!small)  
  

2\. 使用burp的Intruder模块对网站进行目录爆破，存在phpinfo.php和shell.php。注意：此处需要去除特殊字符编码。

![](https://image.3001.net/images/20230705/1688549484_64a5386c0f5833f64e9d1.png!small)  
  

3\. 查看shell.php，可以直接穿参执行系统命令查看flag。

![](https://image.3001.net/images/20230705/1688549500_64a5387c172f4881f656e.png!small)  
  

 **04** **172.72.23.23—sql注入**

访问http://172.72.23.23，提示是get型sql注入。

![](https://image.3001.net/images/20230705/1688549517_64a5388d2f249de425e91.png!small)  
  

![](https://image.3001.net/images/20230705/1688549529_64a538992bcf370a3293a.jpg!small)  
  

![](https://image.3001.net/images/20230705/1688549543_64a538a75ab96ebf17a55.png!small)  
  

 **05** **172.72.23.24—命令执行**

1\.
访问http://172.72.23.24，网站是一个网络测试功能接口。一般来说，这种会存在命令执行漏洞。但是系统也可能会过滤一些特殊字符，需要我们进行绕过。

![](https://image.3001.net/images/20230705/1688549565_64a538bd64b8aefb12a3d.png!small)  
  

2\. 这里是post请求，需要利用gopher协议发送post请求。此处要求必须有4个参数为必要参数，用于传递Content-Type，Content-Length，host，post的参数。如果有多个参数，则参数之间的&也需要进行URL编码。

  

3\. 将数据包进行两次url编码。

![](https://image.3001.net/images/20230705/1688549581_64a538cd41bf42e468560.png!small)  
  

![](https://image.3001.net/images/20230705/1688549593_64a538d978ebdbba8fbfe.jpg!small)  
  

4\. 利用gopher协议发送post请求，成功执行命令。

  

![](https://image.3001.net/images/20230705/1688549609_64a538e9b9eb012d3fe3c.png!small)  
  

![](https://image.3001.net/images/20230705/1688549625_64a538f96ab87317a9ca6.png!small)  
  

5\. 执行命令查看flag，这里提示flag在/tmp目录，但是查看后发现flag并不存在此处。

![](https://image.3001.net/images/20230705/1688549640_64a539086621c3c9a13cf.png!small)

  

 **06** **172.72.23.25—xml**

1\. 访问http://172.72.23.24，跳转一个登录界面。

![](https://image.3001.net/images/20230705/1688549659_64a5391b4613ef7d2d340.png!small)  
  

2\. 成功读取文件。

  

![](https://image.3001.net/images/20230705/1688549676_64a5392c740b991c23468.png!small)  
  

3\. 此处测试命令执行，结果显示无法执行。

  

 **07** **172.72.23.26—Tomcat**

1\. 访问http://172.72.23.26:8080，地址是一个Tomcatyang li界面。构造PUT请求包，将数据包进行二次url编码。

![](https://image.3001.net/images/20230705/1688549704_64a53948639cb45b1b342.png!small)  
  

2\. 使用gopher协议发送请求，响应包返回201说明写入成功。

![](https://image.3001.net/images/20230705/1688549727_64a5395fecfbc256fcb57.png!small)  
  

3\. 利用ssrf，直接访问shell文件执行命令即可。

![](https://image.3001.net/images/20230705/1688549750_64a53976d4e28782b114a.png!small)  
  

 **08** **172.72.23.27—Redis**

1\. 172.72.23.27机器开放了6379端口，测试存在未授权，redis版本为5.0.5。

![](https://image.3001.net/images/20230705/1688549768_64a53988aa82704b10dc5.png!small)  
  

2\.
redis的shell一般可以用写入计划任务(Centos)、写入公钥、写webshell(知道网站物理路径)。因为这台机器没有开放web服务，可以先尝试写入计划任务。

  

3\. 使用脚本。

![](https://image.3001.net/images/20230705/1688549785_64a53999f2da866ea3109.png!small)

![](https://image.3001.net/images/20230705/1688549802_64a539aa27ab2e41bdda5.png!small)

  

  
4\. 成功反弹shell。

![](https://image.3001.net/images/20230705/1688549822_64a539bec7c23c624a44d.png!small)  
  

5\. 或者手工输入。

![](https://image.3001.net/images/20230705/1688550158_64a53b0e77e9acfa8d2e9.jpg!small)  
  

 **09** **172.72.23.28—Redis**

1\. 前面通过探测服务，得知这台机器已开放80和6379端口。

  

2\.
使用dict协议访问6379端口的服务，redis需要验证密码。如果在内网redis需要认证的情况下，我们可以使用dict或gopher协议对密码进行爆破。

![](https://image.3001.net/images/20230705/1688549837_64a539cd98ea0bfa7cec7.png!small)

  
  

3\. 访问80端口存在文件包含，这里可以尝试读取redis的配置文件来获取密码。

![](https://image.3001.net/images/20230705/1688549878_64a539f65f88d265fd839.jpg!small)  
![](https://image.3001.net/images/20230705/1688549858_64a539e2eb0b74aff3aba.png!small)

  

4\. 成功读取redis的密码。

![](https://image.3001.net/images/20230705/1688549961_64a53a4997583a1acf7a5.png!small)  
  

5\. 使用dict协议进行认证，可以确定读取的密码是正确的。

![](https://image.3001.net/images/20230705/1688549947_64a53a3bb36c8f202d82c.png!small)  
  

6\. 使用Gopherus生成payload。

![](https://image.3001.net/images/20230705/1688549980_64a53a5c522e39f3a870b.png!small)  
  

![](https://image.3001.net/images/20230705/1688549991_64a53a672ba6e0582b077.jpg!small)  
  

7\. 将gopher://127.0.0.1:6379/_后面的payload进行url解码后，在上方添加验证密码并增加换行，然后进行两次url编码。

  

![](https://image.3001.net/images/20230705/1688550007_64a53a77e68acb005b550.png!small)

8\. 发送数据包。

![](https://image.3001.net/images/20230705/1688550023_64a53a87998957c9172bc.png!small)  
  

9.访问 **http://172.72.23.28/shell.php，** 成功执行命令。

![](https://image.3001.net/images/20230705/1688550037_64a53a95eea2d0ad77b4f.png!small)  
  

10\. 此外，大家也可以写入计划任务，方法和写shell一样——利用gophers生成脚本，进行url解码，并添加auth后，再进行两次url编码即可。

