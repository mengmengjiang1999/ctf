作者：Qftm合天智汇

## CBC 简介  

## 现代密码体制  

现代密码中的加密体制一般分为对称加密体制(Symmetric Key Encryption)和非对称加密体制(Asymmetric Key
Encryption)。对称加密又分为分组加密和序列密码。

分组密码

分组密码：也叫块加密(block
cyphers)，一次加密明文中的一个块。是将明文按一定的位长分组，明文组经过加密运算得到密文组，密文组经过解密运算（加密运算的逆运算），还原成明文组，有
ECB、CBC、CFB、OFB 四种工作模式。

序列密码

序列密码：也叫流加密(stream
cyphers)，一次加密明文中的一个位。是指利用少量的密钥（制乱元素）通过某种复杂的运算（密码算法）产生大量的伪随机位流，用于对明文位流的加密。解密是指用同样的密钥和密码算法及与加密相同的伪随机位流，用以还原明文位流。

## CBC 模式  

CBC (Cipher Block Chaining, 密码分组链接)
模式中每一个分组要先和前一个分组加密后的数据进行XOR异或操作，然后再进行加密。这样每个密文块依赖该块之前的所有明文块，为了保持每条消息都具有唯一性，第一个数据块进行加密之前需要用初始化向量IV进行异或操作。CBC模式是一种最常用的加密模式，它主要缺点是加密是连续的，不能并行处理，并且与ECB一样消息块必须填充到块大小的整倍数。

## CBC 模式的优缺点  

CBC算法优点：

串行运算、相同明文不同密文。

CBC算法缺点：

需要初始向量、加密是连续的，不能并行处理。

## CBC 工作模式  

## Encryption  

![v2-25dd81d4a107ad4523911c769cd3ea42_720w](https://pic2.zhimg.com/80/v2-25dd81d4a107ad4523911c769cd3ea42_720w.jpg)

### 特殊名词  

Plaintext：明文，待加密的数据。

IV ：初始向量，用于随机化加密的比特块，保证即使对相同明文多次加密，也可以得到不同的密文。

Key：对称密钥，由AES，Blowfish，DES，Triple DES等对称加密算法使用。

Ciphertext：密文数据。

固定分组：CBC在一个固定长度的位组上工作，称为块。这里使用每个16字节的块进行讲解。

### Encryption process  

1、文字流程

Main：上一组密文块用来产生下一组密文块。

    
    
    1、首先将明文分组(常见的以16字节为一组)，位数不足的使用特殊字符填充。
    
    2、生成一个随机的初始化向量(IV)和一个密钥。
    
    3、将IV和第一组明文异或产生初步密文，再用密钥对初步密文加密生成最终密文块。
    
    4、用3中产生的密文块对第二组明文进行xor操作产生初步密文，再用密钥对初步密文加密生成最终密文块。
    
    5、重复4，到最后一组明文。
    
    6、将IV和加密后的每个密文块拼接在一起，得到最终的密文。

从第一块 Plaintext
开始，首先与一个初始向量iv异或（iv只在第一处起作用），然后把异或的结果经过key进行加密，得到第一块的密文，并且把加密的结果与下一块的明文进行异或，一直这样进行下去。

2、公式描述：

    
    
    Ciphertext-0 = Encrypt(Plaintext XOR IV)—只用于第一个组块
    
    Ciphertext-N = Encrypt(Plaintext XOR Ciphertext-(N-1))—用于第二及剩下的组块  # N > 1

## Decryption  

![v2-bbeefc4a0b754572bf98314e92ccdada_720w](https://pic3.zhimg.com/80/v2-bbeefc4a0b754572bf98314e92ccdada_720w.jpg)

### Decryption process  

1、文字流程

Main：上一组密文块影响下一组密文块的还原。

    
    
    1、从密文中提取出IV，然后将密文分组。
    
    2、使用密钥对第一组的密文解密，然后和IV进行xor得到明文。
    
    3、使用密钥对第二组密文解密，然后和2中的密文xor得到明文。
    
    4、重复2-3，直到最后一组密文。

解密和加密的原理是一样的，都是

2、公式描述：

    
    
    Plaintext-0 = Decrypt(Ciphertext) XOR IV—只用于第一个组块
    
    Plaintext-N = Decrypt(Ciphertext) XOR Ciphertext-(N-1)—用于第二及剩下的组块   # N > 1

## CBC 字节反转攻击原理  

## Attack 原理  

1、在 CBC
解密的公式中可以注意到Ciphertext-(N-1)用来产生下一块明文，这就是字节翻转攻击发挥作用的地方。如果我们改变Ciphertext-N-1中的一个字节，然后和下一块解密后的密文xor，就可以得到一个不同的明文，而这个明文是我们可以控制的。

2、在1中的基础上，通过破坏密文中的字节来改变明文中的字节，由此在破坏的密文中添加单引号等恶意字符来绕过过滤器，或通过将用户ID更改为admin来提升权限，或者更改应用程序所需的明文造成其他后果。

## Attack process  

![v2-4f10984ca26b5f163015f761c5c995a0_720w](https://pic2.zhimg.com/80/v2-4f10984ca26b5f163015f761c5c995a0_720w.jpg)

通过修改第一组的密文块字节，来构造自己想要的第二组明文块，当第一组密文块字节发生改变时会影响第一组明文块和第二组明文块。

## 漏洞复现  

## 漏洞源码  

漏洞复现过程以 CTF 模式为例

    
    
    <?phpinclude 'sqlwaf.php';
    define("SECRET_KEY", "Dfa5cUiJb2Xquhgv");
    define("METHOD", "aes-128-cbc");
    session_start();
    
    function get_random_iv(){
        $iv='';
        for($i=0;$i<16;$i++){
            $iv.=chr(rand(1,255));
        }
        return $iv;
    }
    function login($info){
        $iv=get_random_iv();
        $plain = serialize($info);
        $cipher = openssl_encrypt($plain, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv);
        $_SESSION['username'] = $info['username'];
        setcookie("iv", base64_encode($iv));
        setcookie("cipher", base64_encode($cipher));
    }
    function show_homepage(){
        if ($_SESSION["username"]==='admin'){
            echo '<p>Hello admin</p>';
            echo '<p>Flag is ***************************</p>';
        }else{
            echo '<p>hello '.$_SESSION['username'].'</p>';
            echo '<p>Only admin can see flag</p>';
        }
        echo '<p><a href="loginout.php">Log out</a></p>';
        die();
    }
    function check_login(){
        if(isset($_COOKIE['cipher']) && isset($_COOKIE['iv'])){
            $cipher = base64_decode($_COOKIE['cipher']);
            $iv = base64_decode($_COOKIE["iv"]);
            if($plain = openssl_decrypt($cipher, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv)){
                $info = unserialize($plain) or die("<p>base64_decode('".base64_encode($plain)."') can't unserialize</p>");
                $_SESSION['username'] = $info['username'];
            }else{
                die("ERROR!");
            }
        }
    }
    
    if (isset($_POST['username'])&&isset($_POST['password'])) {
      $username=waf((string)$_POST['username']);
      $password=waf((string)$_POST['password']);
      if($username === 'admin'){
            exit('<p>You are not real admin!</p>');
        }else{
            $info = array('username'=>$username,'password'=>$password);
            login($info);
            show_homepage();
        }
    }
    else{
      if(isset($_SESSION["username"])){
            check_login();
            show_homepage();
        }
    }
    ?>
    <!DOCTYPE html>
    <html lang="en" >
    <head>
      <meta charset="UTF-8">
      <title>Paper login form</title>
          <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
      <div id="login">
      <form action="" method="post">
        <h1>Sign In</h1>
        <input name='username' type="text" placeholder="Username">
        <input name='password' type="password" placeholder="Password">
        <button>Sign in</button>
    </div>
    </body>
    </html>

### waf 源码  

    
    
    <?phpfunction waf($str){
    $array=array("'","\""," ","or","and","(",")","<","?");
    for ($i=0; $i < sizeof($array); $i++) {
        if(strpos($str,$array[$i])){
            echo "<script>alert('too young too simple,do not hack')</script>";
            die();
        }
    }
    return $str;
    }
    ?>

## 题目Hint  

题目Hint：Only admin can see flag！

## 漏洞利用与复现过程  

初始页面显示

![v2-1a387542f8***7084f1763543993be2c_720w](https://pic3.zhimg.com/80/v2-1a387542f8***7084f1763543993be2c_720w.jpg)

### Injection 测试  

测试

username：

    
    
    admin' or '1'='1

password：

    
    
    Random：**********

![v2-075f4f10fb86efdf9182aa0b1a9785f7_720w](https://pic3.zhimg.com/80/v2-075f4f10fb86efdf9182aa0b1a9785f7_720w.jpg)

Result

![v2-4e396fdbe902e989c2df5389b79c3df4_720w](https://pic3.zhimg.com/80/v2-4e396fdbe902e989c2df5389b79c3df4_720w.jpg)

通过测试发现存在 Injection 拦截，先不要管，接着往下走

### 网站敏感信息扫描  

通过扫描网站意外发现存在网页Bak文件

![v2-be9c950840dba3ae8f33993312f5ce1e_720w](https://pic4.zhimg.com/80/v2-be9c950840dba3ae8f33993312f5ce1e_720w.jpg)

将Bak文件Down下来，进行代码审计

    
    
    <?phpinclude 'sqlwaf.php';
    define("SECRET_KEY", "Dfa5cUiJb2Xquhgv");  //密钥key
    define("METHOD", "aes-128-cbc");   //使用AES算法128bit固定分组
    session_start();
    
    function get_random_iv(){    //初始化向量IV
        $iv='';
        for($i=0;$i<16;$i++){   //随机生成16字节长度的IV
            $iv.=chr(rand(1,255));  
        }
        return $iv;
    }
    function login($info){   
        $iv=get_random_iv();       //获取经过初始化的向量IV
        $plain = serialize($info);  //将用户提交的信息进行序列化
        $cipher = openssl_encrypt($plain, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv);  //将变量$plain的值进行加密
        $_SESSION['username'] = $info['username'];  //获取用户提交的用户名
        setcookie("iv", base64_encode($iv));    //设置cookie:iv、cipher并将其值进行base64编码
        setcookie("cipher", base64_encode($cipher));
    }
    function show_homepage(){      //判断网页提交的用户是否是"admin"
        if ($_SESSION["username"]==='admin'){  //只有admin用户才能查看Flag
            echo '<p>Hello admin</p>';
            echo '<p>Flag is *******************************</p>';
        }else{
            echo '<p>hello '.$_SESSION['username'].'</p>';  //如果不是admin用户，网页则会显示"hello <username>" 
            echo '<p>Only admin can see flag</p>';  //查询失败
        }
        echo '<p><a href="loginout.php">Log out</a></p>';
        die();
    }
    function check_login(){    //检查cookie：iv、cipher并将其值进行base64解码
        if(isset($_COOKIE['cipher']) && isset($_COOKIE['iv'])){
            $cipher = base64_decode($_COOKIE['cipher']);
            $iv = base64_decode($_COOKIE["iv"]);
            if($plain = openssl_decrypt($cipher, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv)){  //将cipher进行解密
                $info = unserialize($plain) or die("<p>base64_decode('".base64_encode($plain)."') can't  unserialize</p>"); //如果对变量$plain的值反序列化失败则会退出整个程序的执行
                $_SESSION['username'] = $info['username'];  ////获取用户名
            }else{
                die("ERROR!");
            }
        }
    }
    
    if (isset($_POST['username'])&&isset($_POST['password'])) {   //判断用户的输入
      $username=waf((string)$_POST['username']);   //对用户名进行安全检测
      $password=waf((string)$_POST['password']);   //对用户密码进行安全检测
      if($username === 'admin'){   //判断网页提交的用户是否是真实的"admin"
            exit('<p>You are not real admin!</p>');
        }else{
            $info = array('username'=>$username,'password'=>$password);
            login($info);
            show_homepage();
        }
    }
    else{
      if(isset($_SESSION["username"])){
            check_login();
            show_homepage();
        }
    }
    ?>
    <!DOCTYPE html>
    <html lang="en" >
    <head>
      <meta charset="UTF-8">
      <title>Paper login form</title>
          <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
      <div id="login">
      <form action="" method="post">
        <h1>Sign In</h1>
        <input name='username' type="text" placeholder="Username">
        <input name='password' type="password" placeholder="Password">
        <button>Sign in</button>
    </div>
    </body>
    </html>

代码审计发现用户只能够使用admin进行查询Flag，但是代码会检测出你不是真实的admin，所以需要利用网页代理对抓取的网页数据包进行两次不同的利用。

### 第一次数据包的利用  

![v2-9a8deae44e7b2e401bdf318436ebf1ba_720w](https://pic3.zhimg.com/80/v2-9a8deae44e7b2e401bdf318436ebf1ba_720w.jpg)

由于刚开始用户的输入不能是admin所以提交用户名为"ddmin"，但是只有是admin用户才能查看Flag，所以只能利用代码上的提示：define("METHOD",
"aes-128-cbc"); 利用 CBC 字节反转攻击构造admin。

分析构造admin，明文分组16字节一组

    
    
    原明文
    a:2:{s:8:"username";s:5:"ddmin";s:8:"password";s:5:"12345"}
    
    明文分组
    第一组：a:2:{s:8:"userna
    第二组：me";s:5:"ddmin";
    第三组：s:8:"password";s
    第四组：:5:"12345";}

依据上述分组，通过修改第一组明文对应密文中的第10个字节来间接性修改第二组密文解密产生的明文，以此将"ddmin"修改为"admin"

python 脚本~1

    
    
    import base64import urllib.parse
    
    cipher = base64.b64decode(urllib.parse.unquote('mqyAyGTAv4dfyqwuz0mIu7HOBhqf9xStbNQgj4XKnnlIRBEc68i%2BV8hTS6IvQxYsEjzMBpMJO1s%2BFFmbw8jYxw%3D%3D'))  //这里放burp放回的base64的cipher数据
    x = cipher[0:9]+bytes([ord(chr(cipher[9]))^ord('d')^ord('a')])+cipher[10:]
    x = urllib.parse.quote(base64.b64encode(x))
    print(x)

php 脚本~1

    
    
    <?phpheader("Content-Type: text/html;charset=utf-8");
        $cipher = base64_decode(urldecode('mqyAyGTAv4dfyqwuz0mIu7HOBhqf9xStbNQgj4XKnnlIRBEc68i%2BV8hTS6IvQxYsEjzMBpMJO1s%2BFFmbw8jYxw%3D%3D'));  //这里放burp放回的base64的cipher数据
        $temp = $cipher;
        $cipher[9] = chr(ord($cipher[9]) ^ ord('d') ^ ord('a'));
        echo urlencode(base64_encode($cipher));
    ?>

运行结果

mqyAyGTAv4dfz6wuz0mIu7HOBhqf9xStbNQgj4XKnnlIRBEc68i%2BV8hTS6IvQxYsEjzMBpMJO1s%2BFFmbw8jYxw%3D%3D

### 第二次数据包的利用  

![v2-407f5b9a0e46e479543e00c74dadf98e_720w](https://pic1.zhimg.com/80/v2-407f5b9a0e46e479543e00c74dadf98e_720w.jpg)

将username和password提交的数据清空，并且将之前的 iv 和 修改过的cipher 添加到cookie字段中。 此处利用的主要代码如下

![v2-5970c87a27e77d4a27ce21920932d210_720w](https://pic3.zhimg.com/80/v2-5970c87a27e77d4a27ce21920932d210_720w.jpg)

![v2-6154c09b2576379a1ce9a877b95d2b16_720w](https://pic3.zhimg.com/80/v2-6154c09b2576379a1ce9a877b95d2b16_720w.jpg)

对于发送的请求响应中看到对于密文解密出的明文反序列化失败，为了知道是怎么回事，我们将显示出来的base64代码进行解码。

![v2-eebfcc66973c6d0121ef1cfacfab297d_720w](https://pic1.zhimg.com/80/v2-eebfcc66973c6d0121ef1cfacfab297d_720w.jpg)

从图中发现第一组的明文出现了问题，用户已经从"ddmin"成功修改为"admin"，由于"第一次数据包利用"中修改了第一组密文，所以第一组和第二组的明文都会受到影响。要想第一组明文恢复正常，就要在"第一次数据包利用"中的基础上修改IV使之产生正确的明文。

python 脚本~2

    
    
    # -*- coding:utf8 -*-import base64
    import urllib.parse
    
    cipher = base64.b64decode('+g9Uzo1waJpEYbdiV+DYOm1lIjtzOjU6ImFkbWluIjtzOjg6InBhc3N3b3JkIjtzOjU6IjEyMzQ1Ijt9')  //这里放burp放回的base64数据
    iv = base64.b64decode(urllib.parse.unquote('tWgzNB61rHp%2BzFZCLB6KQA%3D%3D'))   //这里放cookie中的iv
    newiv = ''
    right = 'a:2:{s:8:"userna'
    for i in range(16):
        newiv += chr(ord(right[i]) ^ ord(chr(iv[i])) ^ ord(chr(cipher[i])))      //产生新的向量IV
    
    newiv = newiv.encode(encoding="utf8")
    print(urllib.parse.quote(base64.b64encode(newiv)))

php 脚本~2

    
    
    <?php
        #计算iv
        $res = base64_decode('+g9Uzo1waJpEYbdiV+DYOm1lIjtzOjU6ImFkbWluIjtzOjg6InBhc3N3b3JkIjtzOjU6IjEyMzQ1Ijt9');    //这里放burp放回的base64数据
        $iv = base64_decode(urldecode('tWgzNB61rHp%2BzFZCLB6KQA%3D%3D')); //这里放cookie中的iv
        $plaintext = 'a:2:{s:8:"userna';
        $new_iv = '';
        for ($i = 0; $i < 16; $i ++){
            $new_iv = $new_iv . chr(ord($iv[$i]) ^ ord($res[$i]) ^ ord($plaintext[$i]));  //产生新的向量IV
        }
        echo urlencode(base64_encode($new_iv));
    ?>

运行结果

    
    
    Ll1VwOi2%2FtgAj5RTHow8Gw%3D%3D

重新发送第二次请求

![v2-8ab867d41d904ae5a87dc3f8cc16a0c6_720w](https://pic3.zhimg.com/80/v2-8ab867d41d904ae5a87dc3f8cc16a0c6_720w.jpg)

get flag

    
    
    Flag is CBC{CBC is a good thing}

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

CBC字节翻转攻击

<http://hetianlab.com/expc.do?ce=718fded3-e2d8-4ad0-91f0-e1f0d44082ea>（了解CBC模式实现流程、异或运算的高级应用、python中crypto库的使用以及cbc字节翻转攻击的原理与代码实现

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

