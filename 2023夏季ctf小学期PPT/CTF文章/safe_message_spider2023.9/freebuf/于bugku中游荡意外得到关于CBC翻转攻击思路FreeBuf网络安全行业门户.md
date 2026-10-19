个人简介：  
渣渣一枚，萌新一个，会划水，会喊六六  
今天在`bugku`遇到关于`CBC翻转攻击`的题目，总结了一下关于`CBC翻转攻击`的原理，以及关于这道题目的解题思路  
个人博客：<https://www.cnblogs.com/lxz-1263030049/>

`CBC翻转攻击`的主要目的：通过损坏密文字节来改变明文字节。(注：借助`CBC内部的模式`)
通过添加单引号等恶意字符来绕过过滤器，或通过将用户ID更改为admin来提升权限，或者更改应用程序所需的明文的任何其他后果。

### 加密过程：

![image.png](https://image.3001.net/images/20180821/1534835346_5b7bba9262583.png!small)  

>   1. 首先将明文分组(常见的以16字节为一组)，位数不足的使用特殊字符填充。
>   2. 生成一个随机的初始化向量(IV)和一个密钥。
>   3. 将IV和第一组明文异或。
>   4. 用密钥对3中xor后产生的密文加密。
>   5. 用4中产生的密文对第二组明文进行xor操作。
>   6. 用密钥对5中产生的密文加密。
>   7. 重复4-7，到最后一组明文。
>   8. 将IV和加密后的密文拼接在一起，得到最终的密文。
>

从第一块开始，首先与一个初始向量IV异或（IV只在第一处作用），然后把异或的结果配合Key进行加密，得到第一块的密文，并且把加密的结果与下一块的明文进行异或，一直这样进行下去。因此这种模式最重要的特点就是：前一块的密文用来产生后一块的密文。  
![image.png](https://image.3001.net/images/20180821/1534835355_5b7bba9b58b53.png!small)  

### 解密过程:

解密的过程其实只要理解了加密，反过来看解密过程就也很简单了，同样的，前一块密文参与下一块密文的还原。

>   1. 从密文中提取出IV，然后将密文分组。
>   2. 使用密钥对第一组的密文解密，然后和IV进行xor得到明文。
>   3. 使用密钥对第二组密文解密，然后和2中的密文xor得到明文。
>   4. 重复2-3，直到最后一组密文。
>

下图是为解释翻转攻击的原理图：  
![image.png](https://image.3001.net/images/20180821/1534835369_5b7bbaa97f3a4.png!small)  

    
    
    A = B ^ C
    C = A ^ B
    A ^ B ^ C = 0
    A ^ B ^ C ^ C' = C'

根据关系式可以得到：`A' = A ^ C ^ C'`  
所以说我们只需要修改前一组密文所对应的本组明文相同位置的字符，即可得到想要的明文

下面就是关于Bugku的题目  
<http://118.89.219.210:49168/>  
这一题属于常规思路，可是不容易想到，我记得以前做过类似的题目，毕竟是萌新总会有很多知识点会忘记(QAQ)  
使用备份文件脚本进行扫描就会得到：脚本代码：

    
    
    [hide]import requests
    import sys
    url = 'http://118.89.219.210:49168/'
    import threading
    a = ['bak','zip','rar','tar.gz','txt']
    b = ['swp','swo','swn']
    c = ['index.php', 'flag.php', 'profile.php','login.php']
    s = requests.session()
    proxies = {
        'http':None,
        'https':None
    }
    headers = {"Cookie": "PHPSESSID=sclfgjri76captre7cvq6g4170","Accept": "text/html,application/xhtml+xml,application/xml;", "Accept-Encoding": "gzip", "Accept-Language": "zh-CN,zh;q=0.8",
               "Referer": "http://www.example.com/", "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}
    for i in c:
        nurl = url +i+ '~'
        r = s.get(nurl,proxies=proxies)
        if str(r) != '<Response [404]>':
            print nurl
            sys.stdout.flush()
        for j in range(0,len(a)):
            nurl = url + i +'.'+ a[j]
            r = s.get(nurl, proxies=proxies)
            if str(r) != '<Response [404]>':
                print nurl
                sys.stdout.flush()
        for j in range(0, len(b)):
            nurl = url + '.'+ i +'.'+ b[j]
            r = s.get(nurl, proxies=proxies)
            if str(r) != '<Response [404]>':
                print nurl
                sys.stdout.flush()
    print 'finish'[/hide]

运行之后就会得到：  
![image.png](https://image.3001.net/images/20180821/1534835385_5b7bbab972409.png!small)

打开链接发现是应该可以下载的文件并且文件是以`.swp`为后缀名

关于`.swp`文件：

使用`vi`，经常可以看到`.swp`这个文件。那这个文件是怎么产生的呢，当打开一个文件，`vi`就会生成这么一个.`(filename)swp`文件
以备不测（比如非正常退出），如果你正常退出，那么这个这个`.swp`文件将会自动删除

怎么恢复`.swp`：

可以使用

    
    
     vim -r：命令来查看当前目录下的所有swp文件 
     vi -r {your file name} ：命令恢复文件
     rm .{your file name}.swp：命令删除swp文件，不然每一次编辑时总是有这个提示。

![image.png](https://image.3001.net/images/20180821/1534835417_5b7bbad997782.png!small)就会得到html文档：看到该题的代码：  

    
    
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">;
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Login Form</title>
    <link href="static/css/style.css" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="static/js/jquery.min.js"></script>
    <script type="text/javascript">
    $(document).ready(function() {
        $(".username").focus(function() {
            $(".user-icon").css("left","-48px");
        });
        $(".username").blur(function() {
            $(".user-icon").css("left","0px");
        });
        $(".password").focus(function() {
            $(".pass-icon").css("left","-48px");
        });
        $(".password").blur(function() {
            $(".pass-icon").css("left","0px");
        });
    });
    </script>
    </head>
    <?php
    define("SECRET_KEY", file_get_contents('/root/key'));
    define("METHOD", "aes-128-cbc");
    session_start();
    function get_random_iv(){
        $random_iv='';
        for($i=0;$i<16;$i++){
            $random_iv.=chr(rand(1,255));
        }
        return $random_iv;
    }
    function login($info){
        $iv = get_random_iv();
        $plain = serialize($info);
        $cipher = openssl_encrypt($plain, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv);
        $_SESSION['username'] = $info['username'];
        setcookie("iv", base64_encode($iv));
        setcookie("cipher", base64_encode($cipher));
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
    function show_homepage(){
        if ($_SESSION["username"]==='admin'){
            echo '<p>Hello admin</p>';
            echo '<p>Flag is $flag</p>';
        }else{
            echo '<p>hello '.$_SESSION['username'].'</p>';
            echo '<p>Only admin can see flag</p>';
        }
        echo '<p><a href="loginout.php">Log out</a></p>';
    }
    if(isset($_POST['username']) && isset($_POST['password'])){
        $username = (string)$_POST['username'];
        $password = (string)$_POST['password'];
        if($username === 'admin'){
            exit('<p>admin are not allowed to login</p>');
        }else{
            $info = array('username'=>$username,'password'=>$password);
            login($info);
            show_homepage();
        }
    }else{
        if(isset($_SESSION["username"])){
            check_login();
            show_homepage();
        }else{
            echo '<body class="login-body">
                    <div id="wrapper">
                        <div class="user-icon"></div>
                        <div class="pass-icon"></div>
                        <form name="login-form" class="login-form" action="" method="post">
                            <div class="header">
                            <h1>Login Form</h1>
                            <span>Fill out the form below to login to my super awesome imaginary control panel.</span>
                            </div>
                            <div class="content">
                            <input name="username" type="text" class="input username" value="Username" />
                            <input name="password" type="password" class="input password" value="Password" />
                            </div>
                            <div class="footer">
                            <input type="submit" name="submit" value="Login" class="button" />
                            </div>
                        </form>
                    </div>
                </body>';
        }
    }
    ?>
    </html>

`GO`一下可以看到`cookie`中返回的`iv`和`cipher`

将输入序列化得`s:2:{s:8:"username";s:5:"adcin";s:8:"password";s:3:"123";}`  
然后每16字节分组得

> 1: a : 2 : { s : 8 : " u s e r n a  
> 2: m e " ; s : 5 : " a d c i n " ;  
> 3: s : 8 : " p a s s w o r d " ; s  
> 4: 3 : " 1 2 3 " ; }

可见，如果我们想要将2中的`c`变成m就需要对1中的`s`进行改变,使用脚本：

    
    
    [hide]# -*- coding: utf-8 -*-    import base64,urllib
    
    def get_newCipher():
        cipher = ''#输入所得cipher
        cipher = base64.b64decode(urllib.unquote(cipher))
        newCipher = cipher[0:x] + chr(ord(cipher[x])^ord('')^ord('')) + cipher[x+1:]#x为需要改变值所在的字节数，第二个ord中为输入值，第三个ord中为目标值
        print urllib.quote(base64.b64encode(newCipher))
    
    def get_newIV():
        cipher = ''#get_newCipher提交后所得的无法反序列化密文
        iv = ''#所得iv
        #cipher = urllib.unquote(cipher)
        cipher = base64.b64decode(cipher)
        iv = base64.b64decode(urllib.unquote(iv))
        newIv = ''
        right = ''#被损坏前正确的明文
        for i in range(16):
            newIv += chr(ord(right[i])^ord(iv[i])^ord(cipher[i]))
        print urllib.quote(base64.b64encode(newIv))
    
    if __name__ == '__main__':
        #get_newCipher()
        #get_newIV()[/i][/i][/i][/hide][i][i][i]

发现新密文无法反序列化，这是因为，我们将c修改成m时破坏1中的结构

于是我们将新得到的密文复制，通过`base64解密`过后的iv与新密文解密的明文与原1中数据对应异或![image.png](https://image.3001.net/images/20180821/1534835475_5b7bbb1363b7c.png!small)提交新的`iv`和刚才得到的`cipher`即可![image.png](https://image.3001.net/images/20180821/1534835485_5b7bbb1db2304.png!small)

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

