## 0x00 前言

**在我们平时做渗透测试的时候，难免会遇到各种WAF的阻挡。这时一款良好的绕过WAF的渗透测试工具就显得很受渗透测人员欢迎，在这里我们推荐一款绕过WAF的实用渗透工具，希望对大家平时做渗透有所帮助。**

##  0x01简介

WAFNinja
是一款采用[Python](http://lib.csdn.net/base/python)编写的命令行工具。它通过自动化步骤来帮助渗透测试者来绕过WAF，而这些步骤对于绕过输入验证来说是必需的。该工具的编写目标是方便扩展、易于使用和在团队环境下也可使用。众多的载荷和模糊字符串是存储在本地的[数据库](http://lib.csdn.net/base/mysql)，并且伴随着该工具一同发布出来。
WAFNinja 支持HTTP连接、GET/POST请求、可以使用cookie去访问那些只限于授权用户的页面。

## 0x02 下载安装

### 下载方式

github下载地址：<https://github.com/khalilbijjou/WAFNinja>

可用git clone <https://github.com/khalilbijjou/WAFNinja>

或者直接用浏览器下载并且解压到本地文件。

### 安装

直接进入该文件夹，输入如下命令：

    
    
    root@kali:~/WAFNinja# python wafninja.py -h

如果出现正常的文档说明，该结果证明安装成功；

如果出现类似“ ImportError: No module named progressbar ”，请自行安装相关的包。

例如本处的解决方式为：root@kali:~/#pip install processbar （ 或者在终端输入：easy_install
processbar）

## 0x03 使用

## 1 查看帮助信息

root@kali:~/WAFNinja# python wafninja.py -h

root@kali:~/WAFNinja# python wafninja.py fuzz -h # 我们可以把fuzz 换成 bypass,insert-fuzz,insert-bypass,set-db 这几个关键词，便可以查看相对应的帮助信息。

## 2 使用示例

fuzz（模糊测试）:

python wafninja.py fuzz -u "<http://www.target.com/index.php>?id=FUZZ" -c
"phpsessid=value" -t xss -o output.html

![test.PNG](https://image.3001.net/images/20160614/14658792355516.png!small)

![WAF.PNG](https://image.3001.net/images/20160614/14658788428933.png!small)

>  
> bypass（绕过WAF）:  
> python wafninja.py bypass -u "<http://www.target.com/index.php>" -p
> "Name=PAYLOAD&Submit=Submit" -c "phpsessid=value" -t xss -o output.html  
>  
> insert-fuzz（用户自定义模糊测试载荷）:  
> python wafninja.py insert-fuzz -i select -e select -t sql

> 其他参数：  
>  {fuzz,bypass,insert-fuzz,insert-bypass,set-db}  
>  
>  fuzz 检查WAF允许通过的符号和关键词。.  
>  bypass 从数据库中发送载荷到目标。  
>  insert-fuzz 添加一个模糊字符串。  
>  insert-bypass 添加一个载荷到绕过列表。  
>  set-db 设置另外一个数据库文件。对于别人分享的相同载荷数据库时，这个特别有用。  
>  
> 可选参数：  
>  -h, --help 显示帮助信息并且退出。  
>  -v, --version 显示程序版本号并且推出。

## 3 备注

0x01中的第一步时，当我们使用root@kali:~/WAFNinja# python wafninja.py fuzz -h

  

    
    
    usage: wafninja.py fuzz [-h] -u URL [-p POST PARAMETER] [-c COOKIE] -t TYPE      
                           [-d DELAY] [-o OUTPUT FILE] 

  

可选参数：

> -u URL 目标URL（例如：
> "[www.target.com/index.php?id=FUZZ](http://www.target.com/index.php?id=FUZZ)")注意：用关键词FUZZ来指定模糊测试的位置。  
>  -p POST PARAMETER 通过post参数发送模糊测试载荷  
>  -c COOKIE HTTP Cookie 头部  
>  -t TYPE 载荷的类型 [sql|xss]  
>  -d DELAY 每个请求的等待时间,默认是0秒  
>  -o OUTPUT FILE 保存输出到html 文件

-h, --help 显示帮助信息并且退出。

  

 ***本文投递作者：ymmy，转载须注明来自FreeBuf黑客与极客（FreeBuf.COM）**

