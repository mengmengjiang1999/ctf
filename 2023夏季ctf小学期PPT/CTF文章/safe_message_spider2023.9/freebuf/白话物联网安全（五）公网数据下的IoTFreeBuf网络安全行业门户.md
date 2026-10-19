## 白话物联网安全系列往期回顾

> 一、[什么是物联网的信息安全](https://www.freebuf.com/column/191098.html)
>
> 二、[物联网的安全检测](https://www.freebuf.com/articles/wireless/191065.html)
>
> 三、[IoT设备的安全防御](https://www.freebuf.com/articles/wireless/192086.html)
>
> 四、[泛在电力物联网](https://www.freebuf.com/articles/wireless/197575.html)

## 前提回顾

**第一章《什么是物联网的信息安全”》，我们讲了什么物联网，包含了哪几方面的东西，物联网的信息安全会涉及到什么，第二章《物联网的安全检测》，我们从一个IoT漏洞自动化利用工具AutoSploit讲起，讲到我们该如何检测我们常见的物联网存在的安全问题。第三章《IoT设备的安全防御》，我们从三个方向去谈了IoT设备的安全，物理，近场和远程，和现在市场上缺少的物联网安全防御体系。第四章，我们探讨一个概念性的话题，泛在物联网，在这个基础上我们在试试站在甲方爸爸的角度上谈一谈泛在物联网的安全怎么做。**

第五章，站在公网的数据角度上我们来看看现在的IoT安全。

## 正文：公网数据下的IoT

分析IoT数据之前，先简单说近期的一个安全事件，2020年1月底，APT228组织爆出来50万被攻击IP地址，交换机，路由器，物联网设备都有，国内国外都有，地址账号密码，撸了一份回来后，共16个txt文件，14M的文件，啧啧啧，14M的txt文件。

![img](https://image.3001.net/images/20200413/1586764900_5e941c64e7476.jpg!small)

​ 图：消息信息

![img](https://image.3001.net/images/20200413/1586764902_5e941c664116d.jpg!small)

​ 图：泄露数据

![img](https://image.3001.net/images/20200413/1586764902_5e941c663445e.jpg!small)

图：部分数据截图  

 ** _（互联网分析很多了，我这就不给各位大佬献丑了）_**

工欲善其事必先利其器，我们的先来看看现在主流的IoT设备包含的品类，在各大检索数据平台上，我发现物联网设备指纹共有1161条（数据来自互联网，不是完全包含现有指纹信息），粗略统计了一下，国内和国外的指纹比例如下图：

![img](https://image.3001.net/images/20200413/1586764901_5e941c65650a9.jpg!small)

在这个基础上，国内的指纹信息我拿过来分析了一下，发现了非常有意思的一个事情，现在物联网平台不仅集中在交通，物流，农业，运营商，工控，家居，还在电梯，消防，建筑，地质，气象，畜牧，医药等等，甚至于义务商城都有一个自己的物联网感控平台，在我们生活的方方面面，其实已经被整个物联网包围着，出门的电梯，快递的盒子，运送的蔬菜，晚餐里面的炖排骨，都夹着物联网的应急，树立了一下，国内的指纹的信息分布见下图：

![img](https://image.3001.net/images/20200413/1586764901_5e941c657a209.jpg!small)

说完了指纹上面的事情，我们分析下物联网设备在公网的开放情况，不可否认，绝大部分的物联网设备其实都是内网环境，内网系统，公网上暴漏出来的甚少，比例甚至不到1%，基于有限的公网数据，咱们其实可以得出来一些简单的结论，比如国家分布啊，端口，协议等等，现在能找到的数据为3,608,647条，美国最多，共计有683,415条，下来是中国，英国，法国，德国等等

![img](https://image.3001.net/images/20200413/1586764901_5e941c657a008.jpg!small)

通过分析，发现主要开放的端口为：80，443，8001，8080，8003，554，81，82，83，7547，22，21，23，5060，8080，49152，1024，8000，9002等等，主要涉及到的协议http，rtsp，https，http-proxy，telnet，irc，ftp，ssh，cwmp，sip等等，结合刚才我们说到的案例，其实物联网设备的安全，还没等提到挖掘漏洞，就已经被弱口令搞完了，随便试了试，真的是一大堆，说句心里话，起码改改12345这个密码，举个例子如下：

![img](https://image.3001.net/images/20200413/1586764901_5e941c65510bd.jpg!small)

写到这突然发现搞一个简单的小脚本就可以实现批量的IoT弱口令探测，增加一个任意ip地址生成的脚本，然后探测存活（设计不合理，大佬轻喷），然后把地址扔给Hydra，在corntab设置Hydra定期执行，5分钟执行一次

    
    
    def randomip():
        random=[]
        for i in range(4):
            random.append(randomom.randomint(0, 256))
        while True:
            if random[0] == 127 or random[0]==192 or random[0]==10 or random[0]==172:
                random[0]=randomom.randomrange(0, 256)
            else:
                break
        ipadd = '%d.%d.%d.%d' % (random[0], random[1], random[2], random[3])
        random.clear()
        return (ipadd)  
    

最后放一个rapid7发出来的一些指纹信息和弱口令，大佬们想自己写一个小脚本玩可以直接扔进去

    
    
    	"axis":  
    	{
    		"devTypePattern": [["body", "title"], ["regex", "(?i)axis", "(?i)camera"]],
    		"loginUrlPattern": "document\\.write\\(\"([^\"\\]+)[^\\r\\n]+>Setup<\/a>",
    		"auth": ["basic", "admin:admin"]
    	},
    	"mobotix": {
    		"devTypePattern": [["body", ""], ["regex", "content=\"MOBOTIX AG"]],
    		"nextUrl": ["string",  "/control/userimage.html" ],
    		"auth": ["basic", "admin:meinsm"]
    	},
    	"basler": {
    		"devTypePattern": [["body", "title"], ["regex", "Basler AG"]],
    		"nextUrl": ["string",  "/cgi-bin/auth_if.cgi?Login" ],
    		"auth": ["form", "", "Auth.Username=admin&Auth.Password=admin", "body", "regex", "success: true"]
    	},
    	"IQinVision": {
    		"devTypePattern": [["body", ""], ["substr", "<meta name=\"author\" content=\"Brian Lau, IQinVision\">"]],
    		"nextUrl": ["string",  "/imageset.html" ],
    		"auth": ["basic", "root:system"]
    	},
    	"JVC": {
    		"devTypePattern": [["header", "server"], ["regex", "^JVC "]],
    		"nextUrl": ["string",  "/cgi-bin/c20display.cgi?c20encodeencode.html" ],
    		"auth": ["basic", "admin:jvc"]
    	},
    	"SAMSUNG TECHWIN NVR": { 
    		"devTypePattern": [["body", "title"], ["==", "SAMSUNG TECHWIN NVR Web Viewer"]],
    		"nextUrl": ["string",  "/index.php/auth/login_confirm" ],
    		"auth": ["form", "", "id=YWRtaW4%3D&pwd=2558a34d4d20964ca1d272ab26ccce9511d880579593cd4c9e01ab91ed00f325", "body", "substr", "\"is_login_ok\":2"]
    	},
    	"Sentry360": { 
    		"devTypePattern": [["header", "server"], ["==", "Sentry360 "]],
    		"nextUrl": ["string",  "/user.set?name=admin1&pwd=admin1&type=1" ],
    		"auth": ["basic", "admin:1234"]
    	},
    	"Speco": { 
    		"devTypePattern": [["body", "title"], ["==", "Speco IP Camera"]],
    		"nextUrl": ["string",  "/httpapi?GetUserLevel&ipAddress=" ],
    		"auth": ["basic", "admin:1234"]
    	},
    	"Stardot": {"comment": "",
    		"devTypePattern": [["body", "title"], ["==", "NetCamSCD Live Image"]],
    		"nextUrl": ["string",  "/admin.cgi?0" ],
    		"auth": ["basic", "admin:admin"]
    	},
    	"Toshiba eStudio": { 
    		"devTypePattern": [["body", "TITLE"], ["regex", "^TOSHIBA e.STUDIO"]],
    		"nextUrl": ["string",  "/cgi-bin/exportfile/printer/config/secure/settingfile.ucf" ],
    		"auth": ["expect200"]
    	},
    	"Ubiquiti": {"comment": "",
    		"devTypePattern": [["body", "title"], ["==", "EdgeOS"]],
    		"nextUrl": ["string",  "" ],
    		"auth": ["form", "", "username=ubnt&password=ubnt", "body", "!substr", "form id=\"LoginForm\""]
    	},
    	"W-Box": {
    		"devTypePattern": [["body", "title"], ["regex", "^W\\-BOX :"]],
    		"nextUrl": ["string",  "" ],
    		"auth": ["form", "", "action=top&account=admin&password=wbox123&login=Login&parent_id=&app_path=", "body", "!substr", "input type=\"password\""]
    	},
    	"Brickcom": {
    		"devTypePattern": [["header", "www-authenticate"], ["substr", "realm=\"Brickcom"]],
    		"nextUrl": ["string",  "" ],
    		"auth": ["basic", "admin:admin"]
    	},
    	"Arecont": {
    		"devTypePattern": [["header", "www-authenticate"], ["substr", "realm=\"Arecont Vision"]],
    		"nextUrl": ["string",  "" ],
    		"auth": ["basic", ""]
    	},
    	"American Dynamics": {
    		"devTypePattern": [["body", "title"], ["substr", "American Dynamics: Video Management Solutions"]],
    		"nextUrl": ["string",  "/video.htm" ],
    		"auth": ["basic", "admin/admin"]
    	},
    	"ACTi": {
    		"devTypePattern": [["body", "title"], ["substr", "Web Configurator - Version"]],
    		"nextUrl": ["string",  "/video.htm" ],
    		"auth": ["form", "", "LOGIN_ACCOUNT=admin&LOGIN_PASSWORD=123456&LANGUAGE=0&btnSubmit=Login", "body", "!substr", ">Password<"]
    	},
    	"GeoVision": {
    		"devTypePattern": [["header", "server"], ["==", "GeoHttpServer"]],
    		"nextUrl": ["string",  "/webcam_login" ],
    		"auth": ["form", "", "id=admin&pwd=admin&ViewType=2&Login=Login", "body", "!substr", "<title>Invalid</title>"]
    	},
    	"Grandomstream": {
    		"devTypePattern": [["body", "title"], ["==", "Grandomstream Device Configuration"]],
    		"nextUrl": ["string",  "/cgi-bin/dologin" ],
    		"extractFormData": ["type=hidden value=(.*?)>"],
    		"auth": ["form", "substitute", "P2=admin&Login=Login&gnkey=$1", "body", "!substr", "Your Login Password is not recognized"]
    	}  
    

 ***本文作者：大胖，转载请注明来自FreeBuf.COM**

