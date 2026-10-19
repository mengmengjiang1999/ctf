***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

前段时间，FastAdmin 爆出了前台传的CVE，于是想着将 FastAdmin 曾经的漏洞进行一个汇总

通过参看网上的文章，发现大部分利用点为后台漏洞，后台漏洞点目前有两种情况

## 插件漏洞

插件漏洞，其实并不是一个很难利用的方式，在 wordpress 的网站中，拥有安装插件的功能的话，就会有无数个插件都可以上传 shell
以至获得网站的管理权限

Fastadmin 所拥有的插件并不是很多，登录后台之后，访问插件管理功能

> http://test.test/nkmphlDGrv.php/addon?ref=addtabs

![image](https://image.3001.net/images/20210429/1619685519_608a708f394fcd0ba3030.png!small)

目前最新版本已经不支持直接离线或者在线安装插件，还需要拥有 Fastadmin 官网的账号。

看到网上采用的插件为 ：command-1.0.6-regular.zip && Filexi文件管理器(已经无法下载) && 自写的插件

### 在线命令

首先是`在线命令`这个插件  
![image](https://image.3001.net/images/20210429/1619685541_608a70a5a308174c72028.png!small)

我们在接口生成文件处填入 php 的文件名，在文档标题处填入 php 文件

![image](https://image.3001.net/images/20210429/1619685561_608a70b9bd0f392678541.png!small)

先点击生成命令行，再点击立即执行，执行完成后会在`fastadmin/public`目录下生成 api.php

![image](https://image.3001.net/images/20210429/1619685591_608a70d729dd17cbada09.png!small)

![image](https://image.3001.net/images/20210429/1619685611_608a70eb8ef20fc034f02.png!small)

我们分析一下为什么如此操作就可以获得网站权限呢

从官网下载一份插件的源代码

![image](https://image.3001.net/images/20210429/1619685629_608a70fdd5bc3a6e6513e.png!small)

安装完插件之后 fastadmin 项目的结构

![image](https://image.3001.net/images/20210429/1619685654_608a7116128c0d5550a12.png!small)

大致我们仅仅需要关注application/admin/controller/Command.php就ok

我们执行的步骤为两步，首先是生成命令行，其次是立即执行，在相关位置添加断点，并在 Burpsuite
请求包`Cookie`字段添加`XDEBUG_SESSION=PHPSTROM`

    
    
    \app\admin\controller\Command::command

![image](https://image.3001.net/images/20210429/1619685673_608a7129eb1374f7aca48.png!small)

第一步生成命令行中，并没有进行命令执行的相关操作，只是将我们设定的参数，保存起来`php think api --output=api.php
--title=<?php phpinfo();?>`

点击立即执行，发现相较于前一步生成命令行，只在`$action == 'execute'`有所不同

    
    
    \app\admin\controller\Command::command

![image](https://image.3001.net/images/20210429/1619685694_608a713edb3b062c13b7a.png!small)

判定路由为`execute`之后会执行`doexecute`方法

    
    
    \app\admin\controller\Command::doexecute

![image](https://image.3001.net/images/20210429/1619685714_608a7152c6c223076fa7a.png!small)

调试跟进函数执行的 run 方法

    
    
    \think\console\Command::run

![image](https://image.3001.net/images/20210429/1619685737_608a71698b3a21cfa2d2d.png!small)

    
    
    \app\admin\command\Api::execute

![image](https://image.3001.net/images/20210429/1619685753_608a7179392fc55d246b3.png!small)

获取`output`对应的值，拼接为文件名  
![image](https://image.3001.net/images/20210429/1619685783_608a719735d70c3fe8e32.png!small)

利用`file_put_contents`把内容写入到文件中，这个插件漏洞本质上是一个任意文件写入漏洞

只用发送如此数据包就可以成功

    
    
    POST /nkmphlDGrv.php/command/command/action/execute HTTP/1.1
    Host: test.test
    Content-Length: 106
    Accept: application/json, text/javascript, */*; q=0.01
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Origin: http://test.test
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=helipv5455s7i64l4vq72j9nen; think_var=zh-cn;XDEBUG_SESSION=PHPSTROM
    Connection: close
    
    commandtype=api&force=0&url=&output=api.php&template=&title=%3C%3Fphp+phpinfo()%3B%3F%3E&author=&language=
    

### 文件管理器

然后是文件管理器插件漏洞，这个插件漏洞应该不用过多的描述，wordpress
上有类似的插件，拥有这个插件的控制权限之后就相当于获取了整个服务器上的文件的控制权限

![image](https://image.3001.net/images/20210429/1619685805_608a71ad49948ac31cd1e.png!small)

### 自构造恶意插件

最新版本已经不支持采用这种方法了，上传插件压缩包之后，跟着代码流程，会校验压缩包的相关信息，不支持上传自定义的插件压缩包，只能采用官方的插件，将官方插件压缩包进行修改也无法绕过校验

![image](https://image.3001.net/images/20210429/1619685823_608a71bfa7a5286dfdd03.png!small)

如果针对低版本的话，可以直接找一个普通插件压缩包，在其`assets`文件夹下直接添加 shell，再上传。  
![image](https://image.3001.net/images/20210429/1619685838_608a71ce9eef13cc1c495.png!small)![image](https://image.3001.net/images/20210429/1619685851_608a71db43d4bd90209b0.png!small)

## 配置GetShell

在最新版本上进行了验证，发现无法成功，官网已经不支持下载一些老版本的安装文件，利用 github 上的过去分支，安装并没成功，gitee
也是只有核心代码，所以先下载一个完整的项目，再将老版本的核心代码替换进去。找了好几个版本都无法验证，就先附上师傅的操作链接吧

> https://www.t00ls.net/viewthread.php?tid=60410

后来采用与网上操作并不完全相同的操作进行尝试

管理员登录后台之后，选择菜单规则，为其中的权限管理添加规则条件

![image](https://image.3001.net/images/20210429/1619685889_608a7201a9567a88cca1c.png!small)

创建一个低权限的用户

![image](https://image.3001.net/images/20210429/1619685909_608a72159caa30fb2605b.png!small)

登录低权限用户

就会发现接收到了下载请求  
![image](https://image.3001.net/images/20210429/1619685928_608a722849b23d57b052c.png!small)

经过验证最新版本也是存在这个问题的  
![image](https://image.3001.net/images/20210429/1619685947_608a723b6181935270da5.png!small)

修改的规则不应该是 菜单规则，而应该直接是权限管理的规则

对相关代码进行一个分析

首先是对规则的编辑过程，只是将相关字段存储保存进入了数据库

    
    
    \app\admin\controller\auth\Rule::edit

![image](https://image.3001.net/images/20210429/1619685973_608a7255511c2b2db31a8.png!small)

![image](https://image.3001.net/images/20210429/1619685985_608a7261650678cfe49a0.png!small)

fastadmin 的描述是`基于Auth验证的权限管理系统`

在管理员登录时，登录成功之后，会把用户的信息写入session

    
    
    \app\admin\library\Auth::login

![image](https://image.3001.net/images/20210429/1619685999_608a726faedaaa66a08e4.png!small)

会在登录成功之后，跳转到新的 url
链接`http://test.test/nkmphlDGrv.php/index/index`的过程中，会根据用户的session 返回用户所拥有的权限信息

![image](https://image.3001.net/images/20210429/1619686015_608a727f81d6d353c0eca.png!small)

因为创建的低权限的管理员并没有菜单规则的权限，所以直接按照网络上的方法无法利用成功，我们可以修改另一个`常规管理`的规则条件进行尝试，是可以利用成功的，间接证实了我们的想法。

