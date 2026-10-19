原创：kale合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

最近HTB上新出来了一个靶场OneTwoSeven，所以我对它进行了测试，发现整个思路挺有意思，所以记录下来。

![v2-da71a0f87803be4850eddc9752b1e5bc_hd.p](https://pic2.zhimg.com/80/v2-da71a0f87803be4850eddc9752b1e5bc_hd.png)

## 信息搜集  

## MASSCAN  

像往常一样，我们先masscan扫描然后再用nmap。

![v2-e9c0aa559e3d9b2624b0d3c6b77bb81e_hd.p](https://pic3.zhimg.com/80/v2-e9c0aa559e3d9b2624b0d3c6b77bb81e_hd.png)

## NMAP  

![v2-1eb87bc177976129f40e523f639bc668_hd.p](https://pic1.zhimg.com/80/v2-1eb87bc177976129f40e523f639bc668_hd.png)

## 过程分析  

通常，这是我们执行强制浏览或某种形式的自动Web扫描的地方。但是，由于存在速率限制，因此我们需要手动浏览该站点。

![v2-831c262c82adc014388ed912ed70ea2e_hd.p](https://pic4.zhimg.com/80/v2-831c262c82adc014388ed912ed70ea2e_hd.png)

浏览时，我们http://10.10.10.133/signup.php发现它为我们提供了凭据sftp。

![v2-89d240165bd9b77db53f8030a7e85e56_hd.p](https://pic4.zhimg.com/80/v2-89d240165bd9b77db53f8030a7e85e56_hd.png)

我们还看到了域名的使用onetwoseven.htb。在继续之前，需要更新本地DNS条目/etc/hosts。否则访问不了域名

![v2-4e2afd5b1c3801c1b40567f079f87922_hd.p](https://pic3.zhimg.com/80/v2-4e2afd5b1c3801c1b40567f079f87922_hd.png)

完成之后，让我们检查一下远程文件系统上可以访问的内容。

我们将从以预先生成的用户身份访问sftp服务器开始。由于无法上传和执行Web Shell，因此让我们检查一下该命令可用的help命令。

![v2-dfe9de1ab9a58ad1f651dbb08bd2d590_hd.p](https://pic3.zhimg.com/80/v2-dfe9de1ab9a58ad1f651dbb08bd2d590_hd.png)

我们创建一个符号链接，并且public_html文件夹可写；让我们看看它带我们到哪里。

Nmap网络扫描：

![v2-cc2661757e956e5ef2b08ca5a6620694_hd.p](https://pic4.zhimg.com/80/v2-cc2661757e956e5ef2b08ca5a6620694_hd.png)

## 源代码恢复  

让我们从一些源代码恢复开始。我们将利用symlink命令来浏览原始的php文件。我们可以检查一些有意思的文件是signup.php和index.php。如果我们尝试使用相同的名称（即php扩展名）符号链接到这些文件，则服务器在尝试执行php时会遇到问题。相反，我们将删除php扩展名，以便我们可以恢复源代码。

![v2-60f638ca2fbd8141528e6147bab130eb_hd.p](https://pic2.zhimg.com/80/v2-60f638ca2fbd8141528e6147bab130eb_hd.png)

让我们先来看一看index。我们无法从sftp shell中查看/获取文件。这里的窍门是我们需要view-source:http://10.10.10.133/~ots-yZjFkZWY/index在浏览器中输入。在其中，我们可以发现，如果要从服务器本身（127.0.0.1）或104.24.0.54访问此页面，则将显示指向服务器的链接。服务器本身似乎正在监听port
60080。

![v2-cdfcb5fa248a060c0c93e0b3f26ae4e5_hd.p](https://pic1.zhimg.com/80/v2-cdfcb5fa248a060c0c93e0b3f26ae4e5_hd.png)

下一个文件signup包含有趣的信息。具体来说，它向我们展示了如何为sftp登录生成用户名和密码。

![v2-d93a397fb3af0c34361625051eccc789_hd.p](https://pic4.zhimg.com/80/v2-d93a397fb3af0c34361625051eccc789_hd.png)

让我们确认用户名功能如何处理我们的IP地址。

![v2-49dde39dcc32fc313449b0033b1f0ce0_hd.p](https://pic1.zhimg.com/80/v2-49dde39dcc32fc313449b0033b1f0ce0_hd.png)

  * 第1行：生成给定IP地址的md5sum   

  * 第5行：获取哈希IP的前8个字符   

  * 第9行：base64对缩短的哈希进行编码  

  * 第13行：从字符串中删除所有等号  

  * 第17行：返回缩短/替换后的哈希的子字符串，从第四个字符开始，一直到字符串末尾  

  * 第21行：将字符串“ ots-”与上述所有操作的结果连接起来，为我们提供用户名  

密码要简单得多。

![v2-4183a6c13ce295a8676665f4822c6e57_hd.p](https://pic4.zhimg.com/80/v2-4183a6c13ce295a8676665f4822c6e57_hd.png)

如果还有其他用户遵循ots-模式，我们可以获取他们的密码！我们来/etc/passwd看看是否有感兴趣的用户。

回到sftp shell，我们可以进行符号链接/etc/passwd并检出内容。

![v2-296be21cdde8b8ca1ce03adba0ec45a4_hd.p](https://pic2.zhimg.com/80/v2-296be21cdde8b8ca1ce03adba0ec45a4_hd.png)

![v2-fcfea04e740edc808505880afd173b84_hd.p](https://pic3.zhimg.com/80/v2-fcfea04e740edc808505880afd173b84_hd.png)

在上面的输出中，我们可以看到我们的用户名。这里的好处是，每个/etc/passwd条目的GECOS字段中记录了IP地址。让我们进行下一步，并获取与127.0.0.1关联的用户的密码！

![v2-f45c7521fd5216734875db87d54f6cb1_hd.p](https://pic2.zhimg.com/80/v2-f45c7521fd5216734875db87d54f6cb1_hd.png)

那里有一套凭据！让我们在sftp服务上使用它们。

![v2-500159cf62ac3b38feeccebfbca2e5bf_hd.p](https://pic4.zhimg.com/80/v2-500159cf62ac3b38feeccebfbca2e5bf_hd.png)

登录后，我们看到user.txt。剩下的就是下载并打开它！

![v2-160394574a82e4b3299ac47798d1d4c5_hd.p](https://pic2.zhimg.com/80/v2-160394574a82e4b3299ac47798d1d4c5_hd.png)

![v2-e4a52ee4f1b65188a4a9f9b9a8e5708d_hd.p](https://pic4.zhimg.com/80/v2-e4a52ee4f1b65188a4a9f9b9a8e5708d_hd.png)

让我们再次重新访问sftp服务器。这次，我们将链接文件系统的根。

![v2-54364b4db438ab8b700115bf6475c345_hd.p](https://pic2.zhimg.com/80/v2-54364b4db438ab8b700115bf6475c345_hd.png)

我们将再次使用浏览器来查看结果。

![v2-0ab74920d51d29b71982705bff1f12c9_hd.p](https://pic1.zhimg.com/80/v2-0ab74920d51d29b71982705bff1f12c9_hd.png)

观察文件夹，目前我们唯一有权浏览的有用的的文件.login.php.swp位于http://onetwoseven.htb/~ots-mODVhZTM/var/www/html-admin/。

![v2-e81bcdf950f4e0aa6ba66165a77000ca_hd.p](https://pic3.zhimg.com/80/v2-e81bcdf950f4e0aa6ba66165a77000ca_hd.png)

让我们下载文件并分析其内容。运行file命令可以分析.login.php.swp告诉我们这是一个vim隐藏文件。

![v2-eb3ff29c28652054eba477a5f97e2b2a_hd.p](https://pic3.zhimg.com/80/v2-eb3ff29c28652054eba477a5f97e2b2a_hd.png)

当vim打开login.php文件进行编辑时，它会创建一个隐藏的交换文件.login.php.swp。并且这个文件是可以恢复的！

![v2-723400c1e0bfefe667212b9a215b2823_hd.p](https://pic4.zhimg.com/80/v2-723400c1e0bfefe667212b9a215b2823_hd.png)

出现上述提示后，我们可以按Enter键并查看我们新恢复的文件。我们要关注几行；我们将从第一行开始。

![v2-02c1ab7d716c1bed78d8c1b3ffa1ec59_hd.p](https://pic4.zhimg.com/80/v2-02c1ab7d716c1bed78d8c1b3ffa1ec59_hd.png)

第1行告诉我们，可以预期运行此php文件的服务器位于端口60080上。

接下来，第26行让我们知道该php文件与他们的后端管理相关。

![v2-8915d9c3dfd881132669364bba7d3b4f_hd.p](https://pic1.zhimg.com/80/v2-8915d9c3dfd881132669364bba7d3b4f_hd.png)

有趣的东西在第78行；管理员用户名和哈希密码！

![v2-d19688a5791713f1c3e2326577a09c16_hd.p](https://pic1.zhimg.com/80/v2-d19688a5791713f1c3e2326577a09c16_hd.png)

我们可以使用crackstation.net获取明文密码。

![v2-219be58b56356e6abd9679954509792b_hd.p](https://pic4.zhimg.com/80/v2-219be58b56356e6abd9679954509792b_hd.png)

## SSH连接  

我们尝试开启ssh隧道。

![v2-90a9ff59ecf087cdda581973c8fce925_hd.p](https://pic3.zhimg.com/80/v2-90a9ff59ecf087cdda581973c8fce925_hd.png)

我们使用ssh -v命令看看。

![v2-312f2118fcf77cdc6090fee840d8b0fc_hd.p](https://pic4.zhimg.com/80/v2-312f2118fcf77cdc6090fee840d8b0fc_hd.png)

我们可以从上述输出中得出的结论是，在服务器断开连接之前，连接成功并且ssh连接已建立。所以我们可以来建立ssh转发隧道，以到达服务器回送地址上的端口60080。

两个ssh选项将帮助我们在没有交互式shell的情况下建立隧道。让我们检查一下。

![v2-e6ed93337be426e63295a71f0f7be70f_hd.p](https://pic3.zhimg.com/80/v2-e6ed93337be426e63295a71f0f7be70f_hd.png)

![v2-c4f26a8997f19e6cd889916bf3cd5f27_hd.p](https://pic4.zhimg.com/80/v2-c4f26a8997f19e6cd889916bf3cd5f27_hd.png)

下面我们看到使用的隧道选项。

![v2-364d3ff160e460364e6c7d0ce60768aa_hd.p](https://pic1.zhimg.com/80/v2-364d3ff160e460364e6c7d0ce60768aa_hd.png)

运行完上面的命令后，我们运行kali上的netstat命令。我们应该在端口60080上看到一个侦听器。

![v2-e9a79c3818337d067adccf7a136653e1_hd.p](https://pic1.zhimg.com/80/v2-e9a79c3818337d067adccf7a136653e1_hd.png)

我们可以看到我们的kali机器上有一个60080的监听器。在那里发送的所有流量都将转发到端口60080上的10.10.10.133的localhost接口。知道这一点，我们可以浏览到本地隧道，该隧道将把所有流量通过该隧道移至目标。

## 拿到WEB SHELL  

设置好隧道后，我们可以浏览到[http://127.0.0.1:60080](http://127.0.0.1:60080/)。

![v2-dd9b6b381e4425e38391821a93c50d1e_hd.p](https://pic4.zhimg.com/80/v2-dd9b6b381e4425e38391821a93c50d1e_hd.png)

![v2-6ecaa5c390881e068127beb073aa6428_hd.p](https://pic4.zhimg.com/80/v2-6ecaa5c390881e068127beb073aa6428_hd.png)

最明显的点是底部的插件上传”部分。我们可以使用开发人员工具来启用该Submit Query按钮。

当我们在开发工具中查看按钮时，会在标记上看到禁用的属性\<input\>。

![v2-eb20c6375fecee18a0e791e49924c5bd_hd.p](https://pic3.zhimg.com/80/v2-eb20c6375fecee18a0e791e49924c5bd_hd.png)

我们可以简单地删除属性以启用按钮。

![v2-5033baabe8fc3ac47497e2351c6c35e1_hd.p](https://pic4.zhimg.com/80/v2-5033baabe8fc3ac47497e2351c6c35e1_hd.png)

让我们尝试上传一个简单的php web shell，尝试一下乐趣。在此过程中，让我们在Burp中捕获POST请求，因为稍后会派上用场。

![v2-d4cdd31d84f7c4489e477b4be5fabff6_hd.p](https://pic3.zhimg.com/80/v2-d4cdd31d84f7c4489e477b4be5fabff6_hd.png)

![v2-280acb98bbfabcc44ecb6f76915daa2e_hd.p](https://pic1.zhimg.com/80/v2-280acb98bbfabcc44ecb6f76915daa2e_hd.png)

网站回应404错误。

![v2-12dec5bfd59a43c1ed440b78bb7e151f_hd.p](https://pic1.zhimg.com/80/v2-12dec5bfd59a43c1ed440b78bb7e151f_hd.png)

如果浏览到127.0.0.1:60080/menu.php?addon=addons/ots-man-addon.php，则会看到一条说明，告知我们禁用的功能会导致404错误。我们可以假设已经尝试禁用文件上传功能。

上面的页面上还有一条注释：

> 插件管理器不能直接执行，而只能通过提供的RewriteRules执行  
>

因此，当我们要下载菜单上列出的文件之一时，我们通过类似于以下网址的URL进行请求http://127.0.0.1:60080/addon-download.php?addon=[SOME_PLUGIN]。每当addon-download.php请求时，Web服务器都会在内部将请求重写为addons/ots-man-addon.php。请注意，两者addon-upload.php和addon-download.php都由同一个文件处理：ots-man-addon.php。

由于我们对负责处理文件上载和下载的文件最感兴趣，下面分析ots-man-addon.php源码。

以下是我们关注的代码片段。

<?php session_start(); if (!isset ($_SESSION['username'])) { header("Location:
/login.php"); }; if ( strpos($_SERVER['REQUEST_URI'], '/addons/') !== false )
{ die(); }; # OneTwoSeven Admin Plugin # OTS Addon Manager switch (true) { #
Upload addon to addons folder. case preg_match('/\/addon-upload.php/',$_SERVER['REQUEST_URI']): if(isset($_FILES['addon'])){ $errors=
array(); $file_name = basename($_FILES['addon']['name']); $file_size
=$_FILES['addon']['size']; $file_tmp =$_FILES['addon']['tmp_name'];
if($file_size > 20000){ $errors[]='Module too big for addon manager. Please
upload manually.'; } if(empty($errors)==true) {
move_uploaded_file($file_tmp,$file_name); header("Location: /menu.php");
header("Content-Type: text/plain"); echo "File uploaded successfull.y"; } else
{ header("Location: /menu.php"); header("Content-Type: text/plain"); echo
"Error uploading the file: "; print_r($errors); } } break;

有用的是第一段代码的第一行。

1 <?php 2 session_start(); 3 4 if (!isset ($_SESSION['username'])) 5 { 6
header("Location: /login.php"); 7 }; 8 if ( strpos($_SERVER['REQUEST_URI'],
'/addons/') !== false ) 9 { 10 die(); 11 }; 12

  * 第8行：如果/addons/在我们网址的任何位置找到该字符串，服务器将切断我们的连接  

这意味着我们不能直接使用php文件，但是可以使用上面讨论的RewriteRules来获取对该文件的请求。

接下来，我们将看看case语句，该case语句控制进入发生文件上传的代码分支的输入。

6 case preg_match('/\/addon-upload.php/',$_SERVER['REQUEST_URI']):

preg_match正则表达式的工作原理，因此与strpos上面讨论的稍有不同。只有第6行的代码的值为true才能满足。这意味着我们需要/addon-upload.php在URL中的某个位置包含字符串。使用regex
[https://regex101.com](https://regex101.com/)时，会很方便，可以处理一些正则。在下面的屏幕截图中，检查了左侧的单选按钮以指定php样式的正则表达式。正则表达式本身不包括first和last
/。这些正斜杠表示正则表达式的开头和结尾。

![v2-74e5697cdc0780cbeacb8244d6de33d1_hd.p](https://pic1.zhimg.com/80/v2-74e5697cdc0780cbeacb8244d6de33d1_hd.png)

回想一下我们先前在Burp中捕获的请求。我们向发送了一个请求，http://127.0.0.1:60080/addon-upload.php并收到404响应。我们需要一种方法来包含所需的字符串，但不能获取404。

从对RewriteRules的讨论中，我们知道有两种方法可以请求该文件。我们将不得不请求http://127.0.0.1:60080/addon-download.php甚至通过文件获得请求。然后，我们只需要在请求中包括所需的字符串即可。

![v2-c2b6b33c6c9c7c5e641d25dc19b36c1b_hd.p](https://pic1.zhimg.com/80/v2-c2b6b33c6c9c7c5e641d25dc19b36c1b_hd.png)

让我们回到在Burp中捕获的请求，并更改URL以匹配我们找到的内容。

![v2-2bf108325e07645665ae6f224034288a_hd.p](https://pic3.zhimg.com/80/v2-2bf108325e07645665ae6f224034288a_hd.png)

我们所做的唯一更改在左侧突出显示。我们更改了URL，并重新发送了先前捕获的文件上传请求。这次，我们清楚地看到了成功的响应消息。

剩下要做的就是检查我们的shell.php是否按预期工作。

![v2-df51fcd56f0fea1e9e086c4e88ca8435_hd.p](https://pic3.zhimg.com/80/v2-df51fcd56f0fea1e9e086c4e88ca8435_hd.png)

为了拿到一个交互式shell。我们使用nc监听

![v2-6dbbaa35cd6109b25a8d1ba3de2a1530_hd.p](https://pic3.zhimg.com/80/v2-6dbbaa35cd6109b25a8d1ba3de2a1530_hd.png)

然后，触发回调。

![v2-7c5b7ba6475f6b47820a61c063ae332e_hd.p](https://pic2.zhimg.com/80/v2-7c5b7ba6475f6b47820a61c063ae332e_hd.png)

最后，让我们获取一个TTY。

![v2-4f0e8fa1f025790682bd36139dc49876_hd.p](https://pic3.zhimg.com/80/v2-4f0e8fa1f025790682bd36139dc49876_hd.png)

访问级别：www-admin-data

## 提权  

运行sudo -l。

![v2-bee09d77c6c90e6e77c4cd35329cf416_hd.p](https://pic2.zhimg.com/80/v2-bee09d77c6c90e6e77c4cd35329cf416_hd.png)

我们看到使用sudo时会保留一些有趣的环境变量。首先想到的是能够以一种易于利用的方式代理连接。这是之前看到的一篇利用sudo提权的方法。

我们需要检查一下源。我们可以通过查看/etc/apt/sources.list.d/onetwoseven.list文件来做到这一点。这些文件包含存储库URL和一些其他元数据。

![v2-730487c5ef307528b6499ba73df561a1_hd.p](https://pic4.zhimg.com/80/v2-730487c5ef307528b6499ba73df561a1_hd.png)

这里有个有趣的东西！未使用的存储库。我们需要记住此URL，以备后用。

软件包管理器（如apt-get等）从远程存储库请求软件/库/更新等。基于这样的情况，我们可以同时调用apt-get update并apt-get
upgrade在没有密码的情况下，我们可以控制代理相关的环境变量，并且有配置的未使用的资源库;
我们能够对软件包管理器进行中间人攻击。可以使用MitM攻击在计算机上安装后门软件。

让我们首先选择系统上安装的合法软件包。这样做是因为可以运行的命令是update和upgrade。这意味着我们无法安装新软件。当我们运行时update，程序包管理器将看到一个新程序包。当我们运行时upgrade，软件包管理器将下载并安装该更新的（后门）软件包。我们将用于dpkg获取已安装软件的列表。

![v2-fd0d12598793872577e16cb6a6f1c619_hd.p](https://pic3.zhimg.com/80/v2-fd0d12598793872577e16cb6a6f1c619_hd.png)

让我们使用whois软件包。为了找到我们需要的软件包的正确版本，我们将查询软件包管理器当前安装了什么。

![v2-d8ff3e198fb8018da3e8ec559413a75d_hd.p](https://pic1.zhimg.com/80/v2-d8ff3e198fb8018da3e8ec559413a75d_hd.png)

使用Google搜索5.2.17~deb9u1将我们带到packages.debian.org/stretch/whois。点击下载AMD64，将获得我们将要修改的合法.deb文件。使用wget命令下载下来

![v2-6dda771692d2017781fb26659547dce0_hd.p](https://pic3.zhimg.com/80/v2-6dda771692d2017781fb26659547dce0_hd.png)

现在我们有了我们的程序包，我们可以进行恶意修改。我们将从提取包开始。

![v2-b07463dee4c2fef2029841a0ed9186b8_hd.p](https://pic1.zhimg.com/80/v2-b07463dee4c2fef2029841a0ed9186b8_hd.png)

上面的命令应为我们提供以下目录结构。

![v2-d06db690dfec7b32107ee1154e6ace5e_hd.p](https://pic2.zhimg.com/80/v2-d06db690dfec7b32107ee1154e6ace5e_hd.png)

下一步是创建后门文件；我们将使用进行此操作msfvenom。

![v2-5f7308a9e9e89cf0be9087be9de809ed_hd.p](https://pic2.zhimg.com/80/v2-5f7308a9e9e89cf0be9087be9de809ed_hd.png)

不要忘了使./usr/bin/revshell成为可执行文件！

![v2-78a8a324a2db18daacbb871ac84b525d_hd.p](https://pic4.zhimg.com/80/v2-78a8a324a2db18daacbb871ac84b525d_hd.png)

接下来，我们将创建我们的postinst bash脚本。解压缩软件包的所有内容后，将运行postinst脚本。我们将使用脚本来调用二进制后门文件。

![v2-ccfb67ec719acdc57914a205f2f09887_hd.p](https://pic2.zhimg.com/80/v2-ccfb67ec719acdc57914a205f2f09887_hd.png)

不要忘记使postinst可执行！

![v2-2c6727410cb425a9de08396181a5881c_hd.p](https://pic1.zhimg.com/80/v2-2c6727410cb425a9de08396181a5881c_hd.png)

完成此操作后，我们可以重新打包恶意的Whois更新。

![v2-e2ad8158915aea0d227c49a771afdc66_hd.p](https://pic4.zhimg.com/80/v2-e2ad8158915aea0d227c49a771afdc66_hd.png)

现在我们需要构建存储库结构。

回想一下，目标的软件包管理器将与我们联系，就好像我们是软件包存储库一样。软件包管理器将期望某个目录结构以及一些文件存在。我们将继续进行创建。

首先，让我们backdoored-whois.deb为存储库创建一个工作目录并将其移至其中。

![v2-9aa38c4289238926269aa4cbda3520fe_hd.p](https://pic1.zhimg.com/80/v2-9aa38c4289238926269aa4cbda3520fe_hd.png)

接下来，我们将在中创建一个Release文件barebones-repo。根据Debian
Wiki，“发行文件应包含有关分发和校验和的元信息。”要创建Release文件，我们只需复制并粘贴apt-cache show whois目标系统的输出。

![v2-d735dab56613c0b61c2bd25b39598678_hd.p](https://pic2.zhimg.com/80/v2-d735dab56613c0b61c2bd25b39598678_hd.png)

现在，我们需要更改文件中的一些字段Release。具体来说，我们需要更新Version，Filename，Size，MD5sum和SHA256字段。

前两个更改很简单。我们只增加版本号和文件名。我们这样做是为了使程序包管理器认识到需要更新此特定程序包。即，目标系统上安装的程序包比回购程序中的程序包更旧。

![v2-dbd1f1e367392b83b5267f0741077fe2_hd.p](https://pic4.zhimg.com/80/v2-dbd1f1e367392b83b5267f0741077fe2_hd.png)

![v2-7e8b42b08a700742c6017119a5d2a56b_hd.p](https://pic2.zhimg.com/80/v2-7e8b42b08a700742c6017119a5d2a56b_hd.png)

之后，我们将更新“ 大小”字段。我们只需要新大小的恶意.deb文件即可。

![v2-2670cb02f2236b6260ddfca5c5d2d7f2_hd.p](https://pic2.zhimg.com/80/v2-2670cb02f2236b6260ddfca5c5d2d7f2_hd.png)

![v2-cb0c3ec12ebff7672e04463db0e4ef3e_hd.p](https://pic1.zhimg.com/80/v2-cb0c3ec12ebff7672e04463db0e4ef3e_hd.png)

接下来，我们更新MD5sum字段。要对其进行更新，我们需要获取.deb的md5哈希值。

![v2-730d2558f3fa82d0bac0229332e8b9b0_hd.p](https://pic3.zhimg.com/80/v2-730d2558f3fa82d0bac0229332e8b9b0_hd.png)

![v2-dde80a7be8b74419009f9e8657653ad4_hd.p](https://pic3.zhimg.com/80/v2-dde80a7be8b74419009f9e8657653ad4_hd.png)

最后是SHA256字段。

![v2-14501ac38dfc89c34ce263f42fad2a0a_hd.p](https://pic2.zhimg.com/80/v2-14501ac38dfc89c34ce263f42fad2a0a_hd.png)

![v2-575dd49dfa1f7837cb9d58414f134e81_hd.p](https://pic2.zhimg.com/80/v2-575dd49dfa1f7837cb9d58414f134e81_hd.png)

太好了，现在我们的Release文件已完成！接下来，我们需要一个Packages文件。

幸运的是，内容与Release相同，因此简单的复制就足够了。

![v2-f62b203d6f07866d2f9157c02c19e91d_hd.p](https://pic4.zhimg.com/80/v2-f62b203d6f07866d2f9157c02c19e91d_hd.png)

我们需要满足的另一个要求是我们需要一个gzip压缩Packages文件。同样，这是一个简单的步骤。

![v2-fc612d454e88033cb24075f234c8d109_hd.p](https://pic1.zhimg.com/80/v2-fc612d454e88033cb24075f234c8d109_hd.png)

我们即将接近存储库设置步骤。现在，我们需要创建包管理器希望看到的目录结构。

下面的两个mkdir命令将设置我们的仓库目录。

![v2-6c9c585c8fd00174c2c9b4cd8781723a_hd.p](https://pic2.zhimg.com/80/v2-6c9c585c8fd00174c2c9b4cd8781723a_hd.png)

最后，我们需要将所有文件放在适当的位置。部分重命名是backdoored-whois.deb为了匹配我们在Release文件中使用的文件名。

![v2-992dbde31e5e8a9c5afc07df630aec6a_hd.p](https://pic1.zhimg.com/80/v2-992dbde31e5e8a9c5afc07df630aec6a_hd.png)

现在应该看起来像这样。

![v2-64f36bbcb0fe9ebde8382406ac54a187_hd.p](https://pic4.zhimg.com/80/v2-64f36bbcb0fe9ebde8382406ac54a187_hd.png)

现在，我们有一个最小的存储库，可以用来提供恶意软件包。

我们需要采取一些小步骤来正确处理将源于目标计算机的请求。首先，我们将建立反向ssh隧道，以将发送到“代理”的流量返回到本地计算机。

![v2-f2bf6d273b1239f027c60aa0a8dceb7d_hd.p](https://pic4.zhimg.com/80/v2-f2bf6d273b1239f027c60aa0a8dceb7d_hd.png)

我们使用端口8002。我们的代理将在端口kali的8080上侦听

![v2-ede540471306a80e7d0c3826a08ec213_hd.p](https://pic1.zhimg.com/80/v2-ede540471306a80e7d0c3826a08ec213_hd.png)

接下来，我们将设置代理。我们将使用BurpSuite作为代理。，Burp侦听端口8080。我们需要做的就是启动它。

![v2-24625c96c14beef8e443e2c2eb2f8bb4_hd.p](https://pic3.zhimg.com/80/v2-24625c96c14beef8e443e2c2eb2f8bb4_hd.png)

我们已设置代理！现在，还记得当我们查看目标计算机配置为使用的存储库时吗？我们找到了URL
http://packages.onetwoseven.htb/devuan。发送给我们的代理的所有请求最终都将寻找该packages.onetwoseven.htb域名。由于我们正在模拟该存储库，因此需要告诉Burp
是deb packages.onetwoseven.htb。我们将通过修改来实现/etc/hosts。

![v2-6e44210c4090a667df0333dcadab6f5c_hd.p](https://pic4.zhimg.com/80/v2-6e44210c4090a667df0333dcadab6f5c_hd.png)

利用之前的最后一步是启动Web服务器。

![v2-809eba30e3614698dde186460438c55b_hd.p](https://pic1.zhimg.com/80/v2-809eba30e3614698dde186460438c55b_hd.png)

现在，所有内容都已经准备就绪，可供我们MitM软件包管理器使用。让我们来看看它的作用！

## Getshell成功  

在这之前，我们需要用 nc 开启ipv6监听

![v2-c591a63afaee37b23fb3ead151670881_hd.p](https://pic1.zhimg.com/80/v2-c591a63afaee37b23fb3ead151670881_hd.png)

现在，在目标计算机上，我们首先运行apt-get update，然后运行apt-get upgrade

![v2-63cd8b4b88e7c47681425051d2b8e645_hd.p](https://pic1.zhimg.com/80/v2-63cd8b4b88e7c47681425051d2b8e645_hd.png)

我们在上面的输出中看到了一些警告和错误，但是可以忽略它们。

对于该upgrade命令，如果我们看到whois要升级的软件包中列出的内容，则表明我们的漏洞利用至少已部分起作用；软件包管理器将尝试升级软件包。

![v2-5a5c0e9e7900ce45d65609c861a954bc_hd.p](https://pic3.zhimg.com/80/v2-5a5c0e9e7900ce45d65609c861a954bc_hd.png)

如果一切顺利，我们应该看到连接返回到我们的netcat上。

![v2-b89581346df89f4e2db1006bb9aede3d_hd.p](https://pic2.zhimg.com/80/v2-b89581346df89f4e2db1006bb9aede3d_hd.png)

现在，我们已经成功地将MitM打包为一个包管理器，以提升特权。最后我们成功拿到root权限。

Web渗透测试综合项目：

![v2-2c3d15c77d37ce45ee0962bf43f4052f_hd.p](https://pic2.zhimg.com/80/v2-2c3d15c77d37ce45ee0962bf43f4052f_hd.png)

（利用自己的学习到的知识对目标进行Web安全测试，拿到特定的文件，那么恭喜你，你已经完成了从Web安全小白到Web安全工程师的蜕变。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

