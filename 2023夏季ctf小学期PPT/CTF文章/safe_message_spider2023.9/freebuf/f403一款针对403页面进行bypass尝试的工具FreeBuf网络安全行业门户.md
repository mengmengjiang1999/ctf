## 介绍

f403是一款针对403页面进行bypass尝试的工具，payload可自定义，采用golang编写，通过并发的方式发送payload，高效快捷。

## 用法

![image.png](https://image.3001.net/images/20221002/1664694600_633939487132f0ed779ac.png!small)

    
    
    -a, --AddHeader strings   the headers you will add,for explame cookie: 123,Referer: https://www.baidu.com
      -b, --bypassip strings    the ip or ips you will add behind some header like x-client-ip: 192.168.1.1,for example,-b 192.168.1.1,30.1.1.1 and the default values are 127.0.0.1,localhost
      -h, --help                help for f403
      -p, --proxy string        the proxy you will use,support http and socks5 ,for example: -p http://127.0.0.1:8080 or -p socks5://127.0.0.1:8080
      -u, --url string          the target url
    

  1. -a 参数添加自定义http头，例如需要在后台某页面进行bypass403尝试便可添加cookie头

  2. -b参数设置X-Client-IP,X-Forward-For等http头后的ip地址，默认为127.0.0.1和localhost

  3. -p参数设置发送请求时的代理，支持http和socks5

  4. -u参数设置url路径

其中payload配置文件在f403.yaml中，可自由添加或删除。

## 功能

测试常见http方法

![image.png](https://image.3001.net/images/20221002/1664695499_63393ccb3a0156ab51d66.png!small)

添加常见的http头

![image.png](https://image.3001.net/images/20221002/1664695575_63393d176b1175bcc9131.png!small)  
![image.png](https://image.3001.net/images/20221002/1664695590_63393d261f55cb8988603.png!small)

在url末尾添加部分字符

![image.png](https://image.3001.net/images/20221002/1664695647_63393d5f2ef741e807523.png!small)

在url中间添加部分字符

![image.png](https://image.3001.net/images/20221002/1664695708_63393d9c33c2ab5751d41.png!small)

## 使用实例

简单用法:

    
    
    ./f403 -u http://www.google.com/admin/
    

全参数用法:

    
    
    ./f403 -u http://www.google.com/admin/ -a cookie:123,Origin:https://30.110.0.0 -p http://127.0.0.1:60090 -b 39.122.1.1
    

![image.png](https://image.3001.net/images/20221002/1664695871_63393e3f0fc0076837336.png!small)

## 实战

在挖掘某src时使用该工具成功发现某api接口存在权限绕过  
若直接访问该api接口会被拦截  
![image.png](https://image.3001.net/images/20221002/1664696324_6339400452884fc4ce635.png!small)

使用f403进行尝试，由于此处厂商已修复，所以未能再次复现保存使用工具时的截图。使用工具发现添加http头X-Forwarded-For:
localhost 可成功绕过限制

![image.png](https://image.3001.net/images/20221002/1664696728_6339419879e881f007fca.png!small)

## 工具地址:

    
    
    https://github.com/carl1l/f403
    

