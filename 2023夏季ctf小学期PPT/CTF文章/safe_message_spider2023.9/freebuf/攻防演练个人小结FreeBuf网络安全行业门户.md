## 一、扯

转眼之间这场安全圈的大戏已经落幕，回想活动结束前夕，艰难的防守方还在不停的打探着消息，A\B\C\D如何如何，当然我也是其中一员，每天打开微信第一个看到的，都是各路大神分享的各种心得，各种0day预警。

得知特定的0day后，发动所有业务运维人员、开发公司确认是否使用相关代码，演练期间视乎一切都要为攻防演练让步，忙忙碌碌的一个阶段过后我想到几个问题：

> 今年的活动结束了我们有什么收获呢？
>
> 我们的收获是或否有助于后期网络安全管理的工作呢？
>
> 是否可有以遗留下来为明年的防守带来改善呢？

带着这三个问题步入正文。

## 二、现状分析

作为一个上了年纪的网络安全从业者，回首过去，总能发现一些事情（被打穿）惊人的相似之处。在这里我就大概说一下我所经历的一些活动及过程出现思考。

> 时间：2017年 ***单位
>
> 监控方式：盯设备告警包括（IDS、IPS、WAF）
>
> 应对方式：封IP
>
> 收获：超过50个IP地址进入黑名单

> 时 间：2018年 ***单位
>
> 监控方式：盯设备告警包括（IDS、IPS、WAF）
>
> 应对方式：封IP
>
> 收获：超过200网段进入黑名单（活动结束后删掉）

> 时间：2019年7月 ***单位
>
> 监控方式：盯设备告警包括（IDS、IPS、WAF）、ACCESS日志、服务器部分文件监控
>
> 应对方式：封IP、编写安全设备检测规则、尝试日志SIEM 关联使用
>
> 收获：超过20B段、无数个C段进入黑名单（活动结束后删掉）、安全设备检测再某些情况下存在绕过（非特殊方式）

> 时间：2019年12月 ***单位（特定行业）
>
> 监控方式：SIEM监控、蜜罐
>
> 应对方式：编写安全设备检测规则、动态防御
>
> 收获：监控系统后台互联网开放、TRS后台互联网可见、超过5处敏感信息泄露

> 时间：2020年9月 ***单位
>
> 监控方式：SIEM监控、蜜罐
>
> 应对方式：编写安全设备检测规则、动态防御
>
> 收获：信息泄露N处、溯源报告一份、漏洞POC若干

### 1、关于信息收集

早期通过安全设备还能够发现NMAP类探测行为，但最近两次几乎没有出现大量端口探测行为，估计资产的信息收集各红队早有准备，且此类活动资产收集活动猜测也是以被动式为主，通过fofa、shodan、zoomeye等空间引擎进行，即使用了主动探方式来识别资产端口，探测的端口也数量也会受到严格的控制。

### 2、关于漏洞识别

早期红队行为还可通以过常规安全设备感知对方工作，如对方扫描器可能触发大量告警信息，如使用AWVS、APPSCAN等大型扫描器进行漏洞探测，由于扫描器指纹、POC特征等内容很容易被识别。所以前期依靠安全设备基于特征检测告警，还能看到红队痕迹。但随着游戏规则升级、大牛们的加入以及其他因素，越来越多的团队抛弃商用扫描器的使用，转而使用规小、请求少、低线程的方式进行。

如今年演练活动，除第一天被发现某地址外，未发现其他明显扫描行为，深入分析网络访问状态发现某攻击者用了6个小时扫描了我们某服务器不到200个url，每个次请求之间会随机间隔3-60分钟。

扫描url路径如下：

    
    
    /config.inc.jsp.bak  
    /ewebwditor/upload.asp  
    /info.asp  
    /search/was5/web/css/manage.aspx  
    /hdjl2019/nsfwts/6dllmiln3h9d.php  
    /admin.aspx  
    /shop/goods/search.aspx  
    /search/was5/web/c99shell.php  
    /1.asp  
    /2.asp  
    /bsfw2019/sscx/eWebEditor/php/upload.php  
    /1.aspx  
    /config.inc.php.bak  
    /shell.php  
    /SbsqWW/gxcx.do  
    /ewebwditor/php/upload.php  
    /info.jsp  
    /config.jsp~  
    /index.jsp.bak  
    /saaspt/mobileshield.do  
    /kd/asp/file_manager_json.asp  
    /data/cache/ctx.php  
    /SbsqWW/gxcx.do  
    /memadmin/index.php  
    /.settings.asp.swp  
    /database.aspx  
    /saaspt/mobileshield.do  
    /d.php  
    /bsfw2019/bszn/gjss/y2hjl5wwtoaj.jsp  
    /debug.jsp  
    /debug.asp  
    /search/was5/web/advanced_2016.jsp.orig  
    /907b0a1bb2c218e97654e1f738ced127.jsp  
    /info.aspx  
    /ewebeditor/admin_login.asp  
    /ewebwditor/upload.asp  
    /inc/config.asp  
    /search/was5/web/filterword_error.jsp  
    /SbsqWW/gxcx.do  
    /ewebwditor/php/upload.php  
    xxgk2019/eWebEditorNet/upload.aspx  
    /database.asp  
    /db.asp.bak  
    /SbsqWW/gxcx.do  
    /SbsqWW/gxcx.do  
    /index.php  
    /search/was5/web/lol.php  
    /saaspt/mobileshield.do  
    /resourcedata/southidceditor/upload.asp  
    /version/2019/sswj/dz9yuqeqs88m.php  
    /search/was5/web/advanced_2016.jsp/js/jquery.min.js  
    /search/was5/login.jsp.bak  
    /SbsqWW/gxcx.do  
    /ssxc2019/tpxw/6jmbbkc3ihzq.jsp  
    /SbsqWW/gxcx.do  
    /xxgk2019/eWebEditorNet/upload.aspx  
    /config.asp~  
    /db.php.bak  
    /SbsqWW/gxcx.do  
    /ebook2019/202005/eWebEditor/php/upload.php  
    /config.inc.jsp.bak  
    /xxgk2019/sstj/eWebEditor/php/upload.php  
    /SbsqWW/gxcx.do  
    /clip/JobHistoryList.do  
    /index.php~  
    /phpMyAdmin/index.php  
    /config.php~  
    /config.jsp~  
    /adminer-4.4.0.php  
    /info.jsp  
    /config.jsp.bak  
    /SbsqWW/gxcx.do  
    /info.php  
    /saaspt/mobileshield.do  
    /resourcedata/ATpjv1LaOV.jsp  
    /SbsqWW/gxcx.do  
    /.settings.asp.swp  
    /w/index.php  
    /hdjl2019/zxft/wqhg/isyu9gticgvh.php  
    /saaspt/mobileshield.do  
    /qdsw_shinan/bsfw2019/ewebwditor/upload.asp  
    /search/was5/web/!advanced_2016.jsp  
    /search/was5/web/pi.php5  
    /new/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php  
    /saaspt/mobileshield.do  
    /SbsqWW/gxcx.do  
    /bbs/convert/index.php  
    /SbsqWW/gxcx.do  
    /search/was5/web/advanced_2016.jsp_old  
    /bsfw2019/xzzx/bdxz/yhbl/8lxh3zjavw56.jsp  
    /saaspt/mobileshield.do  
    /bsfw2019/12366pt/eWebEditor/php/upload.php  
    /2020/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php  
    /SbsqWW/gxcx.do  
    /SbsqWW/gxcx.do  
    /bsfw2019/ewebwditor/php/upload.php  
    /shell.php  
    /eadmin/news/keditor/asp/file_manager_json.asp  
    /907b0a1bb2c218e97654e1f738ced127.jsp  
    /config.aspx.bak  
    /SbsqWW/gxcx.do  
    /hdjl2019/zxft/wqhg/isyu9gticgvh.jsp  
    /hdjl2019/zxft/ewebwditor/php/upload.php  
    /login.aspx  
    /search/was5/web/nstview.php  
    /shop/pages/tenso.aspx  
    /test.aspx  
    /bsfw2019/bszn/cktms/69xk7ng1h9mr.jsp  
    /xxgk2019/tztg/dra.php  
    /was5/web/ewebwditor/php/upload.php  
    /bsfw/xzzx/czsc/201909/P020190918604300469247.docx%20  
    /qdsw_huangdao/bsfw2019/southidceditor/upload.asp  
    /ssxc2019/402rvt4y1sxq.jsp  
    /SbsqWW/gxcx.do  
    /saaspt/mobileshield.do  
    /kindeditor/asp/file_manager_json.asp  
    /config.inc.jsp.bak  
    /guanli/login

