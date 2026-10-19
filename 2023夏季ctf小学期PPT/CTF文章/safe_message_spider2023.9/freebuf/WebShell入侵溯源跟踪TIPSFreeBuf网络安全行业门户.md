## 前言

WebShell是以asp、php、jsp或者cgi等网页文件形式存在的一种命令执行环境，也可以将其称做为一种网页后门。本篇文章是以作者经验总结，从多个角度阐述挖掘多种不同层次的
WebShell、 溯源黑客（攻击者）如何一步一步在服务器植入
WebShell、最后如何通过网络跟踪技术定位到黑客（攻击者）IP、社交账户、系统环境、兴趣爱好、好友信息等信息。

>
> 注：通过网络跟踪技术可以获取到黑客的一些基本信息如：IP、社交账户、系统环境、兴趣爱好、好友信息、键盘记录、甚至可以与黑客直接交流、获取黑客样貌等信息，但不是绝对可以获取以上信息，如果黑客（攻击者）反跟踪意识较强很有可能无功而返！

## 第一步：定位WebShell文件路径

1、通过关键查找如：eval、system、assert、phpspy、c99sh、milw0rm、gunerpress、shell_exec、passthru、bash等等！

### 代码示例

    
    
    find /www/ -name "*.php" |xargs egrep 'assert|phpspy|c99sh|milw0rm|eval|\(gunerpress|\(base64_decoolcode|spider_bc|shell_exec|passthru|\(\$\_\POST\[|eval \(str_rot13|\.chr\(|\$\{\"\_P|eval\(\$\_R|file_put_contents\(\.\*\$\_|base64_decode'
    
    # 命令解释：
    # find 是linux一个文件搜索工具
    # /www/ 为项目目录
    # -name 是指定搜索文件名如 "*.php" 意思就是以php结尾的文件
    # | xargs egrep linux下的管道符意为搜索文件是否存在以上关键词

2、对于加密的webshell，就很难通过关键词搜索到，对于此类 webshell 可以通过目前比较好的 webshell
扫描工具如：[河马webshell](http://www.shellpub.com/doc/hm_linux_usage.html)
、[WebShellkiller3.3](http://edr.sangfor.com.cn/backdoor_detection.html) 等。

3、webshell + 代码混淆加密 + 隐写术，此类木马几乎可以绕过所有 websehll
扫描工具，搜索或者扫描难易发现。针对此类木马可以使用逆向思维， 既然是 WebSehll
，那么攻击者肯定要通过访问该木马才能使用木马的功能，那么只要访问肯定会留下痕迹，无论是 Apache、Nginx 都会保存请求日志，
通过分析请求日志便可定位 WebSehll！

> 注： 通过日志定位 WebShell
> 时有一下几点需要注意：web项目文件被修改时间、数据被篡改时间等，知道大概时间可以缩小日志分析范围，方便快速定位到木马文件路径;

### 代码示例

`shellcat /var/log/nginx/[www.exploit-db.today.access.log](http://www.exploit-db.today.access.log) | grep 'HTTP/1.1" 200'| grep 'POST'`

### 示例截图

![WebShell
过滤截图](https://image.3001.net/images/20181031/1540946577_5bd8fa913e2e1.png!small)

### WebShell页面截图

![WebShell
过滤截图](https://image.3001.net/images/20181031/1540946593_5bd8faa15b039.png!small)

> 注：截图域名为测试展示使用，如有雷同纯属巧合！

## 第二步：记录备份 WebShell 文件及文件属性

无论是那种方法定位到 WebShell ，均需要记录保存 WebShell 的上传时间、文件所属用户 (一般情况是 Apache/Nginx)，备份
WebShell 文件等！

### 代码示例

    
    
    stat .bootstrap.php
    
    # 注释
    # stat  linux获取文件属性工具
    # .bootstrap.php  WebShell 文件
    

### 示例截图

![webshell文件属性.png](https://image.3001.net/images/20181031/1540946939_5bd8fbfba925c.png!small)

![](/data/Article/img/webshell%E6%96%87%E4%BB%B6%E5%B1%9E%E6%80%A7.png)

> 注：如果是做要为司法证据使用，需要对服务器做镜像（采用位对位只读设备，镜像格式如E01、DD等），所有操作需要在副本镜像上操作。

## 第三步：根据需求编写部署跟踪代码

WebShell 跟踪技术较多本次是通过 js 脚本远程获取黑客（攻击者）基本信息，在定位到 WebShell 后，打开 WebShell 源代码加入写好的
js 脚本，为确保脚本是否有效需要是自己先测试一下，看看是否可以获取浏览者信息，确认无误根据之前记录的 WebShell
文件属性，恢复文件修改时间为写入时间！

### js跟踪代码测试效果

![ycjt.png](https://image.3001.net/images/20181031/1540947123_5bd8fcb3c7583.png!small)

> 注：具体 js 脚本可根据自己的需求编写，或者根据网上的开源脚本自行扩展，开源工具如 BeeF 、或其他开源工具等！

## 第四步： 定位可利用漏洞文件

通过前面的分析获取到访问 WebShell 的IP，通过该IP检索 Apache / Nginx
前后三个月的日志文件，过滤出该IP都访问过那些文件，发送请求什么参数了，请求时间等，根据请求日志分析出具体存在漏洞的文件，并提交到研发部修该漏洞！

