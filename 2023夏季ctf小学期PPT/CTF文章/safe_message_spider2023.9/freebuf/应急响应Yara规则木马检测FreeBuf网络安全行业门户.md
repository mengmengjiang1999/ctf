最近小编在研究应急响应中用到的相关技术，应急响应中必然要和恶意程序、webshell打交道，下面小编来给同学们推荐一款开源的恶意程序检测工具，让我们来一起动手实践一下吧~

##  **Yara规则介绍**

Yara是一个基于规则的恶意样本分析工具，可以帮助安全研究人员和蓝队分析恶意软件，并且可以在应急取证过程中自定义检测规则来检测恶意软件，Yara支持有木马文件落盘和无木马文件落盘(内存马)的检测，由一组字符串和一个确定的布尔表达式组成。

##  **下载安装**

1\.
Windows环境下可直接下载编译好的exe程序进行检测分析，当前使用的版本为4.1.3。下载地址：https://github.com/VirusTotal/yara

![](https://image.3001.net/images/20211230/1640845857_61cd5221a82a6401b74c3.png!small)

程序运行截图

### 2.Yara检测程序运行中使用的参数。

![](https://image.3001.net/images/20211230/1640845896_61cd5248c1978dabe5565.png!small)

运行参数

##  **Yara规则语法**

###  **1.Yara规则内容支持字符串、正则表达式、十六进制进行匹配。**

字符串：定义一个变量 $a = “字符串内容”

正则表达式：定义一个变量 $a = /正则表达式内容/

十六进制：定义一个变量 $a = {十六进制内容}

###  **2.Yara规则条件**

and：与 or：或 not：非

all of them：所有条件匹配即告警

any of them：有一个条件匹配即告警

$a and $b and $c：abc同时匹配即告警

($a and $b) or $c：匹配a和b或c即告警

###  **3．Yara规则常用修饰符**

nocase：不区分大小写

base64：base64字符串

xor：异或字符串

wide：宽字符

###  **4.下面是一条Yara规则的demo。**

![](https://image.3001.net/images/20211230/1640845932_61cd526c9fcf667d883c9.png!small)

yara规则demo

##  **恶意程序检测案例**

###  **1** 、挖矿程序检测

1、下载xmrig挖矿程序，https://github.com/xmrig/xmrig/

2、编写xmrig挖矿程序检测规则，利用010 Editor、die等PE文件编辑工具进行特征的提取。此规则使用PE文件的文件头4D
5A、挖矿程序专用协议stratum、xmrig挖矿的程序的名称、矿池域名xx.pool.xx等特征进行关联匹配。

![](https://image.3001.net/images/20211230/1640845951_61cd527f0823ee8ea8125.png!small)

xmrig挖矿程序检测规则

3、xmrig挖矿程序扫描，利用-r参数对目录下的文件进行递归扫描，可发现利用检测规则扫描出xmrig.exe挖矿程序。

![](https://image.3001.net/images/20211230/1640845966_61cd528e1adc06729c48d.png!small)

挖矿程序扫描

### 2、 无文件检测-python flask内存马

1.命令行运行python flask内存马脚本。

![](https://image.3001.net/images/20211230/1640845986_61cd52a24bfa356d0159f.png!small)

内存马脚本

2.浏览器访问执行payload，完成内存马的注入。

http://172.16.120.115:5000/test?param={{url_for.__globals__['__builtins__']['eval']("app.add_url_rule('/shell1',
'shell', lambda
:__import__('os').popen(_request_ctx_stack.top.request.values.get('cmd',
'whoami')).read())",{'_request_ctx_stack':url_for.__globals__['_request_ctx_stack'],'app':url_for.__globals__['current_app']})}}

3.查看命令执行的效果。

![](https://image.3001.net/images/20211230/1640846005_61cd52b5b69b8b2c3c45d.png!small)

whoami命令执行

4.利用procdump.exe dump内存。

![](https://image.3001.net/images/20211230/1640846019_61cd52c3a16095620c61f.png!small)

procdump dump内存命令

5.检测内存中的明文特征，如payload中的_request_ctx_stack、exec|eval、url_for.__globals__、add_url_rule、__import__(‘os’).popen等函数在内存中全部明文显示，利用此特征编写检测规则。

![](https://image.3001.net/images/20211230/1640846032_61cd52d0c51c4ce898f95.png!small)

python flask内存马检测规则

6.利用python flask内存马检测规则扫描出python.exe进程中被注入内存马。

![](https://image.3001.net/images/20211230/1640846049_61cd52e12774bf5f88447.png!small)

python flask内存马检测

