## 前言

在我们平时做渗透测试的时候，难免会遇到各种WAF的阻挡。这时一款良好的绕过WAF的渗透测试工具就显得很受渗透测人员欢迎，在这里我们推荐一款绕过WAF的实用渗透工具，希望对大家平时做渗透有所帮助。

## 简介

    
    
    WAFNinja是一款用python写的命令行工具，它可以帮助渗透测试人员免去部分手动输入的烦恼。此外，WAFNinja强大的扩展性，在团队协作中显得非常适用。通过自动化步骤来帮助渗透测试者来绕过WAF，而这些步骤对于绕过输入验证来说是必需的。该工具的编写目标是方便扩展、易于使用和在团队环境下也可使用。众多的载荷和模糊字符串是存储在本地的数据库，并且伴随着该工具一同发布出来。 WAFNinja 支持HTTP连接、GET/POST请求、可以使用cookie去访问那些只限于授权用户的页面。当然，必要的时候，我们还可以设置代理。

## 下载安装

### 下载方式：

github下载地址：<https://github.com/khalilbijjou/WAFNinja>  
![](https://image.3001.net/images/20220302/1646202949_621f1045e116b999549d4.png!small)  
可用git clone <https://github.com/khalilbijjou/WAFNinja>  
![](https://image.3001.net/images/20220302/1646202950_621f1046a2df89cda03e8.png!small)  
或者直接用浏览器下载并且解压到本地文件。

### 安装

直接进入该文件夹，输入如下命令：  
python wafninja.py -h  
如果出现正常的文档说明，该结果证明安装成功；  
![](https://image.3001.net/images/20220302/1646202951_621f10476f71ef27a214f.png!small)  
如果出现类似“ ImportError: No module named progressbar ”，请自行安装相关的包。  
![](https://image.3001.net/images/20220302/1646202951_621f1047e5266819b08f2.png!small)  
例如本处的解决方式为：root@kali:~/#pip install processbar （ 或者在终端输入：easy_install
processbar）  
![](https://image.3001.net/images/20220302/1646202952_621f1048644d59949303b.png!small)

## 使用

### 查看帮助信息

python wafninja.py -h  
![](https://image.3001.net/images/20220302/1646202952_621f1048d177d7f88fe39.png!small)  
python wafninja.py fuzz -h # 我们可以把fuzz 换成 bypass,insert-fuzz,insert-bypass,set-db 这几个关键词，便可以查看相对应的帮助信息。  
Fuzz是什么？  
Generally speaking fuzz is a brute force method which used to break
software，就是用大量的测试用例一个一个试，尽可能多的找出有可能出问题的地方。  
bypass就是绕过。  
![](https://image.3001.net/images/20220302/1646202953_621f10495b89b11ddcaaa.png!small)

![](https://image.3001.net/images/20220302/1646202953_621f1049d405814b6a6c5.png!small)

### 使用示例

fuzz（模糊测试）:  
python wafninja.py fuzz -u “<http://www.target.com/index.php?id=FUZZ>“ -c
“phpsessid=value” -t xss -o output.html  
![](https://image.3001.net/images/20220302/1646202954_621f104a5970a016171fe.png!small)  
结果如下  
![](https://image.3001.net/images/20220302/1646202954_621f104acf7100d061848.png!small)  
比如  
![](https://image.3001.net/images/20220302/1646202955_621f104b7e71c53ef1ac5.png!small)  
不会被waf检测  
![](https://image.3001.net/images/20220302/1646202956_621f104c27779201ef289.png!small)  
被检测到  
![](https://image.3001.net/images/20220302/1646202960_621f1050b01daf0a76516.png!small)  
bypass（绕过WAF）:  
python wafninja.py bypass -u “<http://www.target.com/index.php>“ -p
“Name=PAYLOAD&Submit=Submit” -c “phpsessid=value” -t xss -o output.html  
![](https://image.3001.net/images/20220302/1646202961_621f10514aa6610ab12d9.png!small)  
![](https://image.3001.net/images/20220302/1646202962_621f105243f09d0143d38.png!small)  
![](https://image.3001.net/images/20220302/1646202964_621f10540e15167ff612a.png!small)  
![](https://image.3001.net/images/20220302/1646202964_621f1054c8e63358af0e8.png!small)  
insert-fuzz（用户自定义模糊测试载荷）:  
python wafninja.py insert-fuzz -i select -e select -t sql

## 参数介绍

 **其他参数：**  
{fuzz,bypass,insert-fuzz,insert-bypass,set-db}  
fuzz 检查WAF允许通过的符号和关键词。.  
bypass 从数据库中发送载荷到目标。  
insert-fuzz 添加一个模糊字符串。  
insert-bypass 添加一个载荷到绕过列表。  
set-db 设置另外一个数据库文件。对于别人分享的相同载荷数据库时，这个特别有用。

 **可选参数：**  
-h, —help 显示帮助信息并且退出。  
-u URL 目标URL（例如： “www.target.com/index.php?id=FUZZ”)注意：用关键词FUZZ来指定模糊测试的位置。  
-p POST PARAMETER 通过post参数发送模糊测试载荷 Send fuzz through post parameter  
-c COOKIE HTTP Cookie 头部  
-t TYPE 载荷的类型 [sql|xss]  
-d DELAY 每个请求的等待时间。默认是0秒  
-o OUTPUT FILE 保存输出到html 文件  
—proxy PROXY 使用代理；Use a proxy. Format: IP:PORT  
—prefix PROXY 增加前缀；Add a prefix to every fuzz.  
—postfix PROXY 增加postfix；Add a postfix to every fuzz.  
-w WAF 发送特定WAF的有效载荷；Send payloads of certain WAF [default=generic]  
-e EXPECTED 目标站点的预期输出。如果输入是编码的或类似的，请使用此选项。  
-p PATH sqlite数据库的路径。默认位置为“db/db.sqlite”

