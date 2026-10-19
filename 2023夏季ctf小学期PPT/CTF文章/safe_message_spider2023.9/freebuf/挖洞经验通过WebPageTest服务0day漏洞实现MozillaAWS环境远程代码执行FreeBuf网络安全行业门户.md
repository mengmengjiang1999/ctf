***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![Untitled-design-5.jpg](https://image.3001.net/images/20190319/1552998073_5c90deb92d6e6.jpg!small)
**本文中，Assetnote CS安全团队在分析Mozilla
AWS云服务网络环境攻击面时，发现了部署于其中的网络性能测试工具WebPageTest存在一个0day漏洞，利用该漏洞最终实现了对Mozilla
AWS服务器的远程代码执行（RCE）。**

##  **WebPageTest介绍  
**

WebPageTest是一款开源的Web前端性能分析工具，其有在线版本和[本地搭建版本](https://github.com/WPO-Foundation/webpagetest)两种，能针对特定网站提供免费的性能评测，支持IE和Chrome浏览器，它会模拟使用真正的浏览器(IE和Chrome)连接速度，从全球多个地点运行免费网站速度测试。可以运行简单的测试或执行高级测试，包括多步骤事务、视频捕获、内容阻塞等等。还将依据测试结果提供丰富的诊断信息，包括资源加载瀑布图，页面速度优化检查和改进建议，会给每一项内容一个最终的评级。企业或组织可以下载
[开源版本](https://github.com/WPO-Foundation/webpagetest)搭建内部测试站点，对内部网站进行性能测试分析。

在内网部署的WebPageTest服务中，可以通过修改其中的[settings.ini文件](https://github.com/WPO-Foundation/webpagetest/blob/master/www/settings/settings.ini.sample#L155)来启用一些基本的用户名密码验证，所以还是建议对此进行配置，以便阻止一些匿名用户的登录访问。  

在Assetnote
CS安全团队评估的很多内网WebPageTest服务中，都缺乏基本的用户验证措施，所以，可能产生的结果就是，攻击者可以利用WebPageTest的一系列性能测试工具，来发起SSRF（服务端请求伪造）攻击，实现对目标内网资源的访问获取。

## 漏洞概况  

2017年11月，Assetnote CS安全团队在对Mozilla的AWS（亚马逊云服务）环境测试过程中，发现了以下两个网络资产：

> wpt-vpn.stage.mozaws.net
>
> wpt1.dev.mozaws.net

这两个网络资产都属Mozilla AWS环境中的WebPageTest服务测试实例，而且，Mozilla
AWS环境中部署的WebPageTest服务没有任何基本的用户名密码验证措施，在与白帽Mathias的合作下，我们对其中部署的WebPageTest服务进行了源码分析，经过数个小时的测试，我们就发现了一个可以导致远程代码执行（RCE）的攻击链。

由于在当时这算是一个0day漏洞，所以，我们及时与Mozilla公司和WebPageTest团队进行了沟通协商，修复了这个漏洞。在2018年1月17日的修复版本中可以看到[其中提交的commit信息](https://github.com/WPO-Foundation/webpagetest/commit/c026e4799455b8bc06c8e40f137d800d8d6803cc#diff-f49d3a5c5c3e48d9e57e843e3f679444)。

## 漏洞发现利用

在WebPageTest的源码中，首先引起我们注意的是[/www/work/workdone.php](https://github.com/WPO-Foundation/webpagetest/blob/master/www/work/workdone.php)脚本具备的上传和解压任意zip文件功能，该php脚本文件包含了限制127.0.0.1之外的访问源逻辑，代码如下（第110行）：

    
    
    ...
    
    !strcmp($_SERVER['REMOTE_ADDR'], "127.0.0.1")
    
    ...

同样在这个php文件中，我们发现了另外一个危险之处，那就是上传任意zip文件并解压至一个已知位置的逻辑，代码如下（第133-136行）：

    
    
    if (isset($_FILES['file']['tmp_name'])) {
    
      ExtractZipFile($_FILES['file']['tmp_name'], $testPath);
    
      CompressTextFiles($testPath);
    
    }

基于以上代码逻辑，如果我们能把IP伪装为127.0.0.1，那么是不是就可以通过它们来实现服务端代码执行了呢？但是，事实没有我们想得这么简单，在/www/work/workdone.php中的第321行，还存在这么一个方法函数：

> SecureDir($testPath);

SecureDir方法函数的代码定义在[/www/common_lib.inc](https://github.com/WPO-Foundation/webpagetest/blob/master/www/common_lib.inc)文件的第2322 - 2347行：

    
    
    /**
    
    * Make sure there are no risky files in the given directory and make everything no-execute
    
    *
    
    * @param mixed $path
    
    */
    
    function SecureDir($path) {
    
        $files = scandir($path);
    
        foreach ($files as $file) {
    
            $filepath = "$path/$file";
    
            if (is_file($filepath)) {
    
                $parts = pathinfo($file);
    
                $ext = strtolower($parts['extension']);
    
                if (strpos($ext, 'php') === false &&
    
                    strpos($ext, 'pl') === false &&
    
                    strpos($ext, 'py') === false &&
    
                    strpos($ext, 'cgi') === false &&
    
                    strpos($ext, 'asp') === false &&
    
                    strpos($ext, 'js') === false &&
    
                    strpos($ext, 'rb') === false &&
    
                    strpos($ext, 'htaccess') === false &&
    
                    strpos($ext, 'jar') === false) {
    
                    @chmod($filepath, 0666);
    
                } else {
    
                    @chmod($filepath, 0666);    // just in case the unlink fails for some reason
    
                    unlink($filepath);
    
                }
    
            } elseif ($file != '.' && $file != '..' && is_dir($filepath)) {
    
                SecureDir($filepath);
    
            }
    
        }
    
    }

它会检查过滤掉一些危险的文件，并确保无任何文件的执行操作，由于它在之后后续的代码流中才出现，因此就存在一种可利用的竞争条件（Race Condition
），即解压到web服务器的PHP文件在被过滤删除之前可被短暂地访问到。  

在我们构造的攻击链中，其前提条件非常简单，由于在目标资产wpt-vpn.stage.mozaws.net的WebPageTest服务中，执行Traceroute命令后，我们可以获取到WebPageTest生成的一个有效
test ID，有了这个ID号就比较好办了。比如，我们在其中执行执行对<https://google.com>的Traceroute命令：

![01.png](https://image.3001.net/images/20190319/1552998895_5c90e1ef24d39.png!small)之后，WebPageTest服务会跳转到一个包含test
ID的性能测试结果URL页面去：

> <http://wpt-vpn.stage.mozaws.net/result/171124_GW_9/>

这里，171124_GW_9为test ID。

到此，我们还差着127.0.0.1 IP伪造这一步，如果这步能成功，就能有效访问到workdone.php文件，发起命令执行了。

经过分析，我们在 [/www/common.inc](https://github.com/WPO-Foundation/webpagetest/blob/master/www/common.inc) 文件中的第70行发现了以下代码逻辑：

    
    
    if (isset($_SERVER["HTTP_FASTLY_CLIENT_IP"]))  
    
    
      $_SERVER["REMOTE_ADDR"] = $_SERVER["HTTP_FASTLY_CLIENT_IP"];

从这个代码段中可以发现，我们能通过发送请求的方式，把 FASTLY-CLIENT-IP 请求头设置为127.0.0.1，从而实现以远程用户身份任意更改
$_SERVER["REMOTE_ADDR"]的IP地址。

综上所述，我们可以设置两个Burp Intruder 攻击扩展来实现最终的服务端代码执行。其中一个Burp
Intruder用来实现上传一个恶意的zip文件，另外一个Burp
Intruder用来访问解压过后存在于目标系统中的php文件。我们对上述竞争条件的利用，最大Burp Intruder线程数为200。

![request
upload.png](https://image.3001.net/images/20190319/1552999245_5c90e34de0172.png!small)但好在有[高速请求插件Turbo
Intruder](https://github.com/PortSwigger/turbo-intruder)的帮助下，我们的漏洞利用链就比较稳定了。最终，我们在Mozilla AWS网络环境中成功实现了服务端代码执行。如下，我们在wpt-vpn.stage.mozaws.net中实现了对phpinfo() 的调用读取：  

![02.png](https://image.3001.net/images/20190319/1552999277_5c90e36de8e6d.png!small)现在，Mozilla官方漏洞公布网站Bugzilla已经公开了我们的漏洞报告，可以[点此查看](https://bugzilla.mozilla.org/show_bug.cgi?id=1420520)，报告中包含了具体的复现步骤、测试截图、PoC代码和协调沟通等详细要素和相关过程。最终，我们获得了Mozilla官方的$500奖励和致谢。  

***参考来源：[assetnote](https://blog.assetnote.io/bug-bounty/2019/03/19/rce-on-mozilla-zero-day-webpagetest/)，clouds编译，转载请注明来自FreeBuf.COM**

