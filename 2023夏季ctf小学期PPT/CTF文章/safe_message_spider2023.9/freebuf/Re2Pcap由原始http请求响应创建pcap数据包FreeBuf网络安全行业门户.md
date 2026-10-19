![](https://image.3001.net/images/20190814/1565739588_5d534a4426d14.png!small)

**Re2Pcap是英文单词Request2Pcap和Response2Pcap的缩写。Community版的用户可以使用Re2Pcap快速的创建PCAP文件，并根据Snort规则对其进行测试。**

Re2Pcap允许你为raw HTTP request（如下）快速的创建PCAP文件。

    
    
    POST /admin/tools/iplogging.cgi HTTP/1.1
    
    Host: 192.168.13.31:80
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
    
    Accept: text/plain, */*; q=0.01
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Referer: http://192.168.13.31:80/admin/tools/iplogging.html
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Content-Length: 63
    
    Cookie: token=1e9c07e135a15e40b3290c320245ca9a
    
    Connection: close
    
    tcpdumpParams=tcpdump -z reboot -G 2 -i eth0&stateRequest=start

## 使用

    
    
    git clone https://github.com/Cisco-Talos/Re2Pcap.git
    
    cd Re2Pcap/
    
    docker build -t re2pcap .
    
    docker run --rm --cap-add NET_ADMIN -p 5000:5000 re2pcap

在Web浏览器中打开localhost:5000访问Re2Pcap，或使用Re2Pcap-cmd脚本与Re2Pcap容器（container）交互以在当前工作目录中获取PCAP文件。

## 必要条件

Docker

HTTP Raw Request / Response

Web 浏览器（为达到最佳效果，请使用基于Chromium的Web浏览器）

## 优势

易于安装。无需复杂的多VM设置

Re2Pcap运行在基于Alpine Linux的docker镜像上，体积小于90MB

## Dockerfile

    
    
    FROM alpine
    
    # Get required dependencies and setup for Re2Pcap
    
    RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
    
    RUN apk update && apk add python3 tcpdump tcpreplay
    
    RUN pip3 install --upgrade pip
    
    RUN pip3 install pexpect flask requests httpretty requests-toolbelt
    
    COPY Re2Pcap/ /Re2Pcap
    
    RUN cd Re2Pcap && chmod +x Re2Pcap.py

## Walkthrough

下图显示的是，使用Re2Pcap为Sierra Wireless AirLink ES450 ACEManager
iplogging.cgi[命令注入漏洞](https://www.talosintelligence.com/reports/TALOS-2018-0746)创建pcap文件的视频演示。

![](https://image.3001.net/images/20190814/1565739606_5d534a56c85c5.jpg!small)

## Re2Pcap 开发（dev）分支（开发中）

目前，Re2Pcap dev分支具有以下附加功能

> 模拟raw HTTP request和对PCAP的响应
>
> 更好的输入验证

下图显示的是，使用Re2Pcap dev为Sierra Wireless AirLink ES450 ACEManager
iplogging.cgi[命令注入漏洞](https://www.talosintelligence.com/reports/TALOS-2018-0746)创建PCAP文件：

![](https://image.3001.net/images/20190814/1565739622_5d534a66803a2.jpg!small)

![](https://image.3001.net/images/20190814/1565739622_5d534a6688a39.jpg!small)

## Re2Pcap Workflow

![](https://image.3001.net/images/20190814/1565739641_5d534a7945230.png!small)

如上图所示，Re2Pcap是基于Alpine Linux的Python3应用程序，拥有基于Flask的Web界面。

Re2Pcap将输入数据解析为raw HTTP
request或response，并在捕获数据包时实际执行client/server交互。在交互后，Re2Pcap会将捕获的数据包以PCAP文件格式呈现。

## 建议

请使用Linux作为主机操作系统，因为Re2Pcap已在Linux上经过了充分的测试。

如果为主机Host: somedomain:5000创建PCAP，请通过修改Re2Pcap.Py
app.run调用将Flask应用程序更改为在其他端口上运行，否则PCAP将包含Flask应用程序响应

## 限制

如果raw HTTP request中没有Accept-Encoding标头，则Accept-Encoding:
identity标头会被添加到reqeust中。

python请求存在[已知的问题](https://github.com/psf/requests/issues/2234)

那真是太可怕了。Accept-Encoding: identity始终有效，RFCs如是说。发送它应该是完全无害的。否则，删除它需要我们替换httplib

以下是来自Re2Pcap PCAP中的源地址（source）和目的地（desitnation）IP

> 源地址 IP: 10.10.10.1
>
> 目的地 IP: 172.17.0.2，请使用tcprewrite -D选项根据需要将desitnation
> IP修改为其他IP地址。你还可以使用tcpprep和tcprewrite将其他IP设置为端点。由于tcprewrite的结果不一致，我使用了另一种方法来设置不同的SRC/DST
> IP

将HTTP/1.1
302指定为响应将生成PCAP，并以最大可能重试次数访问Location:header中指定的资源。你也可以在测试中使用wireshark只导出第一个HTTP流，排除其他可能会影响你的流。

 ***参考来源：[GitHub](https://github.com/Cisco-Talos/Re2Pcap)，FB小编secist编译，转载请注明来自FreeBuf.COM**

