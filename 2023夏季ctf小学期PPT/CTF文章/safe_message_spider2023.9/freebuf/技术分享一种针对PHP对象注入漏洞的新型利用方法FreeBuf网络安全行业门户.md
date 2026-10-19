![页首配图](https://image.3001.net/images/20180826/1535297040_5b82c610756bd.png!small)

## 前言

 **就在前段时间的BlackHat黑客大会上，来自Secarma的安全研究专家Sam
Thomas介绍了一种可导致严重PHP对象注入漏洞出现的新型漏洞利用技术，这种技术不需要使用到unserialize()这个PHP函数，虽然这是一种PHP反序列化漏洞，但它并不像大家所知道的那样。在这种技术的帮助下，攻击者将能够提升相关漏洞的文件严重性，并最终实现远程代码执行。**

不过大家不用担心，RIPS已经将这种新型的攻击类型增加到RIPS代码分析引擎之中了，感兴趣的同学可以点击【[这里](https://demo.ripstech.com/)】查看RIPS代码分析Demo。

## 流封装器

在访问一条文件路径时，大多数PHP文件操作都允许使用各种URL风格的封装器，例如data://、zlib://或php://。其中的某些封装器通常都会被攻击者用来利用某些潜在的远程文件包含漏洞，一旦利用成功，攻击者将能够控制目标文件的完整文件路径。比如说，封装器可以注入某些资源路径，或注入需要直接执行的恶意PHP代码：

    
    
    include($_GET['file'])
    
    include('php://filter/convert.base64-encode/resource=index.php');
    
    include('data://text/plain;base64,cGhwaW5mbygpCg==');

## Phar元数据

但是目前为止，还没有人关注过phar://封装器。之所以我们注意到了Phar文件（一种PHP文档），是因为这种文件所包含的元数据采用的是一种序列化格式。接下来，我们一起创建一个Phar文件，并向其中添加一个包含数据的对象来作为元数据：

    
    
    //create new Phar
    
    $phar= new Phar('test.phar');
    
    $phar->startBuffering();
    
    $phar->addFromString('test.txt','text');
    
    $phar->setStub('<?php__HALT_COMPILER(); ? >');
    
     
    
    //add object of any class as meta data
    
    classAnyClass {}
    
    $object= new AnyClass;
    
    $object->data= 'rips';
    
    $phar->setMetadata($object);
    
    $phar->stopBuffering();

我们新创建的这个test.phar文件现在拥有如下所示的内容，我们可以看见我们新添加的对象会以序列化字符串的形式进行存储：

![以序列化字符串的形式进行存储](https://image.3001.net/images/20180826/1535297077_5b82c635e0497.png!small)

## PHP对象注入

如果一个文件操作是通过phar://封装器来对我们的Phar文件进行的话，文件所包含的序列化元数据将会被反序列化。这也就意味着，我们在元数据中注入的对象将会被加载到应用程序上下文中，如果目标应用程序有一个名叫AnyClass的类，并且定义了类似__destruct()或__wakeup()这样的方法，那么这些方法将会自动被调用。因此，我们将能够触发代码中任意的销毁方法或唤醒方法。更严重的是，如果这些方法能够直接对我们注入的数据对象进行操作的话，将导致更严重的漏洞出现。

    
    
    class AnyClass {
    
           function __destruct() {
    
                  echo $this->data;
    
           }
    
    }
    
    // output:rips
    
    include('phar://test.phar');

## 漏洞利用

首先，攻击者必须要制作一个Phar文件，并将其存储在目标Web服务器中。但是Sam
Thomas发现原来可以将Phar文件隐藏在一个JPG文件之中，所以这一步可以直接利用常见的图片上传功能来实现。

目前来说，还不足以造成严重的影响，因为如果攻击者可以在类似include()、fopen()、file_get_contents()和file()这样的操作中控制完整的文件路径，那么这已经暴露了一个严重的安全漏洞了。因此，这些函数在处理用户输入数据时肯定会进行各种验证。

不过，phar://封装器在进行任意文件操作时都会触发反序列化行为，因此类似file_exists()这样的文件操作虽然只会检查文件是否存在，这样的实现不仅没有考虑安全风险之类的问题，而且也没有采取任何的保护措施。因此，攻击者将能够注入phar://封装器并获取到代码执行权限。

下面给出的是目前看似无害的代码段：

    
    
    file_exists($_GET['file']);
    
    md5_file($_GET['file']);
    
    filemtime($_GET['file']);
    
    filesize($_GET['file']);

## RIPS的自动检测机制

在RIPS的帮助下，我们将能够对未经过滤或验证的用户输入数据（针对PHP文件的操作）进行自动化检测。这样一来，我们就可以检测文件删除、文件披露、文件写入、文件篡改、文件创建和文件包含漏洞。

![RIPS的自动检测机制](https://image.3001.net/images/20180826/1535297121_5b82c66140a71.png!small)

除此之外，RIPS的上下文敏感字符串分析功能也可以帮助我们精准判断文件路径是否可以被攻击者部分或完全控制，以及是否可以注入phar://封装器。更加重要的是，RIPS甚至还可以检测到潜在的对象注入漏洞利用链。

RIPS的研究人员已将这种类型的PHP对象注入攻击标记为了Phar Deserialization，RIPS代码分析器目前已支持检测这种类型的代码风险。

 *** 参考来源：[ripstech](https://blog.ripstech.com/2018/new-php-exploitation-technique/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

