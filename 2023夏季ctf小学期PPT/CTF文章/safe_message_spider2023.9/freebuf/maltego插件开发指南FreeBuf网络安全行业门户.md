# 0x00 前言

##
maltego是一个图形化的信息收集工具，在很多人的印象中是一个社会工程学工具，但是由于api大部分都是国外的，使用起来不管是易用性还是效率上都不理想，今天给大家介绍下如何自己编写maltego的适用于国内环境的插件以方便大家使用。

# 0x01 maltego-trx库简介

今天我们用到的这个插件开发的工具叫maltego-trx，是python里的一个库，作用是专门用于编辑maltego中的transform。

下载：pip install maltego-trx

踩坑：推荐在kali下使用，windows中使用如果之前安装过vs环境可能会报错如下：

ERROR: Could not build wheels for cryptography which use PEP 517 and cannot be
installed directly

解决方式：

    
    
    C:\> \path\to\vcvarsall.bat x86_amd64
    C:\> set LIB=C:\OpenSSL-win64\lib;%LIB%
    C:\> set INCLUDE=C:\OpenSSL-win64\include;%INCLUDE%
    C:\> pip install cryptography

安装成功截图：

![1619612233_608952494f303f1324d3f.png!small?1619612232548](https://image.3001.net/images/20210428/1619612233_608952494f303f1324d3f.png!small?1619612232548)

  

# 0x02 使用maltego-trx新建项目并编辑代码

1.新建一个项目目录：

![1619612388_608952e437a1fdd96dd5e.png!small?1619612387435](https://image.3001.net/images/20210428/1619612388_608952e437a1fdd96dd5e.png!small?1619612387435)

2.进入到目录下在cmd或者终端命令行输入：

maltego-trx start mymaltegotransform（最后面这个参数是自己的插件名称）  

![1619612507_6089535b850ae635fc3a3.png!small?1619612506805](https://image.3001.net/images/20210428/1619612507_6089535b850ae635fc3a3.png!small?1619612506805)

看到有如上图的返回即表示创建成功。

项目结构：

-project.py（这个是用来测试项目使用的工具）

-transform（这个是代码文件夹）

-__pycache__（这个是最后生成插件后的pyc文件夹）

-__init__.py（构造文件，这个不用管）

-DNStoIP.py(提供的例子，搜索dns返回ip结果)

-GreetPerson.py（提供的例子，类似于helloworld）

-OverlayExample（提供的例子，修改元素属性及覆盖）

3.我们以DNStoIP为例修改下：

需求：通过搜索人名寻找图片搜索结果并输出图片链接

3.1 修改文件名称

maltego对插件名称有严格检查机制，这在之后的导入和测试都很重要，所以我们先修改文件名称。将DNStoIP改为PersontoImage。

3.2 原始文件代码结构分析

    
    
    #这个插件底层原理是利用socket模块的gethostbyname功能完成的，需要导入socket模块  
    import socket  
      
    # UIM_TYPES是maltego调用元素类型的基础，可写可不写
    from maltego_trx.maltego import UIM_TYPES  
      
    # 模块最后输出的元素类型是IP地址，需要输出什么类型就直接导入什么名称
    from maltego_trx.entities import IPAddress  
    # 这里是maltego-trx调用maltego的接口，不要删除
    from maltego_trx.transform import DiscoverableTransform
      
    # 定义类，注意类名一定要和文件名称一摸一样！里面的参数不用修改
    class DNSToIP(DiscoverableTransform):
        """
        Receive DNS name from the client, and resolve to IP address.
        """
    
        @classmethod  
    # 这里是创建元素的函数，主要功能写在这里
        def create_entities(cls, request, response):
            dns_name = request.Value
            # 这里是执行具体功能的函数
            try:
                ip_address = socket.gethostbyname(dns_name)  
    # 最后执行添加元素的过程
                response.addEntity(IPAddress, ip_address)  
      
    # 输出报错信息以便调试
            except socket.error as e:
                response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])
    
            # Write the slider value as a UI message - just for fun  
    response.addUIMessage("Slider value is at: " + str(request.Slider))

在上面的代码中已经把基本的插件代码结构整理出来了，这里需要注意的是类的名称一定要和文件名称一模一样，大小写都必须一样，否则在测试和导入使用的过程中会报错。

我们分析下这个代码就基本知道，在from maltego_trx.entities import
IPAddress这一行属于你需要最后输出结果的元素类型，当我们修改代码时需要输出什么元素就写什么名字，具体名称列表如下：

    
    
    Alias = "maltego.Alias"
    ASNumber = "maltego.AS"
    BuiltwithTechnology = "maltego.BuiltWithTechnology"
    BuiltWithRelationship = "maltego.BuiltWithRelationship"
    CircularArea = "maltego.CircularArea"
    Company = "maltego.Company"
    Device = "maltego.Device"
    DNS = "maltego.DNSName"
    Document = "maltego.Document"
    Domain = "maltego.Domain"
    Email = "maltego.EmailAddress"
    FlickrAffiliation = "maltego.AffiliationFlickr"
    GPS = "maltego.GPS"
    Hash = "maltego.Hash"
    Hashtag = "maltego.Hashtag"
    Image = "maltego.Image"
    IPAddress = "maltego.IPv4Address"
    Location = "maltego.Location"
    MX = "maltego.MXRecord"
    MyspaceAffiliation = "maltego.AffiliationMyspace"
    Namechk = "maltego.Namechk"
    Netblock = "maltego.Netblock"
    NS = "maltego.NSRecord"
    Organization = "maltego.Organization"
    Person = "maltego.Person"
    PhoneNumber = "maltego.PhoneNumber"
    Phrase = "maltego.Phrase"
    Port = "maltego.Port"
    Sentiment = "maltego.Sentiment"
    StockSymbol = "maltego.StockSymbol"
    Tweet = "maltego.Twit"
    TwitterAffiliation = "maltego.AffiliationTwitter"
    TwitterList = "maltego.TwitterUserList"
    UniqueID = "maltego.UniqueIdentifier"
    URL = "maltego.URL"
    Website = "maltego.Website"
    WebTitle = "maltego.WebTitle"

然后就是dns_name =
request.Value这一行表示maltego输入的内容（也就是我们查询的对象）是在这里进行编辑，后面的request.Value是固定的，不需要修改。

response.addEntity(IPAddress,
ip_address)这一行表示具体添加元素的过程，第一个参数是import的需要输出的元素类型的名称，后面是经过操作后自己定义的查询结果的变量名称。

3.3 根据需求修改代码

我们需要的是通过人名查到图片，那么我们最后查询的结果是图片，那么输出的类型应该是Image，所以需要修改import IPAddress为import
Image（参考上面的表），在最后添加元素的过程中我们同样需要修改类型为Image：

![1619616633_60896379c5ca357cc2377.png!small?1619616632905](https://image.3001.net/images/20210428/1619616633_60896379c5ca357cc2377.png!small?1619616632905)

接下来我们修改下输入和输出的变量名称方便理解：

![1619616742_608963e6ba3ca05025cad.png!small?1619616741957](https://image.3001.net/images/20210428/1619616742_608963e6ba3ca05025cad.png!small?1619616741957)

接下来就是最最最重要的修改类名和我们的文件名称一摸一样：

![1619616796_6089641ce4ca3fff904e2.png!small?1619616796137](https://image.3001.net/images/20210428/1619616796_6089641ce4ca3fff904e2.png!small?1619616796137)

我们可以在project.py的同级目录下使用命令行输入：python3 project.py list 进行测试
如果类名和文件名不一样这里会显示不出来我们的插件，如果显示成功则表示没有问题：

![1619616956_608964bcf0046e5a10c49.png!small?1619616956142](https://image.3001.net/images/20210428/1619616956_608964bcf0046e5a10c49.png!small?1619616956142)

接下来就开始正式的爬虫搜索功能的编写了，我们只需要把具体的爬虫功能写在ip_address =
socket.gethostbyname(dns_name)这一行就可以，注意查询的变量名称我们是用的person，最后输出的变量名称我们用的是image，然后我们删除掉不必要的调试信息（因为使用的时候会自动有调试）代码如下：

    
    
    #把原来的socket换成我们需要的requests和re  
    import requests
    import re
    
    from maltego_trx.entities import Image
    
    from maltego_trx.transform import DiscoverableTransform
    
    
    class PersontoImages(DiscoverableTransform):
        """
        Receive DNS name from the client, and resolve to IP address.
        """
    
        @classmethod
        def create_entities(cls, request, response):
            person = request.Value  
    #使用图片搜索然后使用re搜集图片链接
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
                "referer": "https://image.baidu.com"
            }
            url = "http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=" + person
            req = requests.get(url,headers=headers)
            f = req.text
            key = r'thumbURL":"(.+?)"'
            key1 = re.compile(key)
            for image in re.findall(key1, f):
                response.addEntity(Image,image)

至此，代码编写就完成了。

# 0x03 使用插件

打开maltego，新建一个空白图层，然后点击顶部transform菜单中的“new local transform”：

![1619617665_6089678170a923f4540f0.png!small?1619617665370](https://image.3001.net/images/20210428/1619617665_6089678170a923f4540f0.png!small?1619617665370)

会弹出一个设置框，必填项目如下：

![1619617802_6089680ae9b31d3dac57e.png!small?1619617802352](https://image.3001.net/images/20210428/1619617802_6089680ae9b31d3dac57e.png!small?1619617802352)

点击next就可以下一步：

![1619617966_608968ae840ccc9c0c693.png!small?1619617965744](https://image.3001.net/images/20210428/1619617966_608968ae840ccc9c0c693.png!small?1619617965744)

点击finish即可完成，接下来我们使用一下看看效果：

![1619618083_6089692374dac1ec86c85.png!small?1619618082907](https://image.3001.net/images/20210428/1619618083_6089692374dac1ec86c85.png!small?1619618082907)

![1619621050_608974ba034588d550a76.png!small?1619621049224](https://image.3001.net/images/20210428/1619621050_608974ba034588d550a76.png!small?1619621049224)

当然这里没有做什么反验证码的东西，大家可以根据自己的需求做修改。

# 0x04 总结

maltego是一个非常实用的图形化情报搜集和分析工具，我们除了开发图片搜索之外还可以做很多的事情，比如请求一些信息搜集的api获得返回值（maltego自带的插件就是这个逻辑）。希望大家学习之后能自己打造一个maltego适用于国内环境的武器库。

