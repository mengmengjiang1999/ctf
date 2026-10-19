***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![livestream-company-webcast-event-uk.jpg](https://image.3001.net/images/20190401/1554122303_5ca2063f49a51.jpg!small)**
**最近，我发现了一个关于Livestream网站的漏洞，利用该漏洞可以获取其上任意注册用户的未公开或定期排播流视频内容。**

[Livestream](https://livestream.com/)是一个视频流媒体平台，允许用户使用相机和计算机通过互联网直播视频，观众则通过PC、iOS、Android、Roku和Apple
TV观看。Livestream的商业用户有Spotify、Gannett、世界经济论坛、特斯拉汽车、SpaceX、NBA、罗德岛设计学院、克林顿基金会以及超过200家地方电视分支。

用户注册了Livestream之后，可以在上面发起基于视频、图片或文字的一些相关操作发贴，这些发贴可以在个人用户管理区内保存为草稿或定期排播内容，以备后续公开发布之用。

## 漏洞分现

起初，我以注册用户身份向Livestream网站上传了一个视频，并把它预设编排在下周进行公开发布，上传过程中，我用Burp进行了拦截抓包，经过查看分析，发现可以从其中一个请求获取到上传视频的ID号，并且从中也能发现服务端的一个在用API。如下：

    
    
    POST /owner/accounts/28088370/events/8514908/videos HTTP/1.1
    Host: api.new.livestream.com

这个请求中，28088370代表了用户ID，8514908则代表操作事件ID，这两个ID号都能用公开方式通过访问相应的用户账户获得。

服务端对上述请求的JSON格式响应如下：

    
    
    {"id":188597955,"event_id":8598251,"event":{"id":8598251,"short_name":null,"full_name":"testerx","description":null,"owner_account_id":28301059,"owner":{"id":28301059,"full_name":"abs ...................................
    ....................................
    .........................."asset"{"qualities":null,"akamai_stream_id..................................................................................................................*{Lots of other initially unobserved stuff}*...

从该响应中可以看出与视频相关的一些ID信息。另外，还能发现服务端采用了Akamai media services的多媒体服务。

为了收集到更多服务端信息，我对上传视频进行了在线播放，并对播放过程进行抓包，其中有一个请求指向了.m3u8流视频文件，如下：

    
    
    GET /owner/auth/b0128101059............................4bd802ced1b90c02e9c75e6284c87a02........................................1552398275601...........1552571075602...........4UEXC0RJKwnt0cXEI1y0yA~~00000000000000..................................../accounts/28088370/events/8514908/videos/185422358.secure.m3u8
    Host: player-api.new.livestream.com

服务端对上述请求返回了以下响应，该响应包含了内容类型为application/vnd.apple.mpegurl的[视频回放路径](https://learn.akamai.com/en-us/webhelp/media-services-live/media-services-live-hls-hds-and-dash-ingest-user-guide-v3.2/GUID-B4654D3F-CBC2-4FBC-AA0C-BFCA550E7093.html)（Backup
playback path），如下：

    
    
    HTTP/1.1 200 OK
    Server: openresty
    Content-Type: application/vnd.apple.mpegurl; charset=utf-8
    {other headers..}
    #EXTM3U
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=150000,RESOLUTION=480x272,CODECS="avc1.77.31,mp4a.40.2"
    https://vod.livestream.com/5c87f404_a2ba525be7719d247853a38ab4fae8e260148a8e/events/00000000008332eb/be94b4a1-ee64-4159-a83e-2a8c42e28ce3_150.m3u8
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=550000,RESOLUTION=768x432,CODECS="avc1.77.31,mp4a.40.2"
    https://vod.livestream.com/5c87f404_a2ba525be7719d247853a38ab4fae8e260148a8e/events/00000000008332eb/be94b4a1-ee64-4159-a83e-2a8c42e28ce3_550.m3u8
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1500000,RESOLUTION=848x480,CODECS="avc1.77.31,mp4a.40.2"
    https://vod.livestream.com/5c87f404_a2ba525be7719d247853a38ab4fae8e260148a8e/events/00000000008332eb/be94b4a1-ee64-4159-a83e-2a8c42e28ce3_1500.m3u8
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2000000,RESOLUTION=1280x720,CODECS="avc1.77.31,mp4a.40.2"
    https://vod.livestream.com/5c87f404_a2ba525be7719d247853a38ab4fae8e260148a8e/events/00000000008332eb/be94b4a1-ee64-4159-a83e-2a8c42e28ce3_2000.m3u8

上述响应可以看出，其视频被切片为了m3u8格式文件储存在服务器中，其编码格式为utf-8，并以明文路径进行存储，像播放列表一样被在线播放。

出于好奇，我查了一下，发现application/vnd.apple.mpegurl是m3u8格式流视频对应的HLS（ HTTP Live
Streaming）内容类型，它主要是存放整个视频的基本信息和分片(Segment)组成，是由苹果公司率先提出的，可以在给定的播放器中进行播放。

当一个m3u8文件提供给像VLC的播放器之后，播放器会首先解析这个m3u8文件，然后从其回放路径（ backup
urls）中获取（或者说下载）播放列表视频。在处理m3u8文件时，播放器不能有任何预取操作（pre-fetched）。

## 深入发现

现在，我再接着以之前同样的方法上传另外一个视频，但是，整个上传过程中还是有一些细微的异常，之前第一个视频中涉及的3个ID号，在这里都存在一个偏移量的不同。另外，在我继续上传了第三个视频之后，我发现其中的视频video
id号会每次都增加1。

在细细地检查了每个请求响应之后，我得到了另外一条线索。在初次响应video id和Akamai media services服务的第一个上传视频请求，如下：

    
    
    POST /owner/accounts/28088370/events/8514908/videos/
    Host: api.new.livestream.com

该请求的服务端响应中，除了能发现video id和Akamai media
services服务之外，还存在一个包含有处理不同比特率的SMIL文件（同步多媒体集成语言）的相关服务端。在一开始的响应分析中，由于其内容非常之多，迷乱了我的思路，所以我并没有注意到这个服务端。

这个服务端相关的响应上下文消息如下：

    
    
    {rest of the response}..........................................................................{"smil_url":"http://api.new.livestream.com/accounts/28088370/events/8514908/videos/185422358.smil","secure_smil_url":"https://api.new.livestream.com/accounts/28088370/events/8514908/videos/185422358.secure.smil","secure_progressive_url":null,"m3u8_url":null,

我在浏览器打开了其中的这个SMIL文件，我得到的是一个未授权响应，如下：

>
> <http://api.new.livestream.com/accounts/28088370/events/8514908/videos/185422358.smil>

![下载Livestream网站中用户未公开或定期排播视频](https://image.3001.net/images/20190401/1554122120_5ca20588d2713.png!small)响应中的“Can't
access draft video
post”貌似说明smil格式视频不能通过这种手段获取，但是，我意识到.smil毕竟只是一种视频文件格式，那上述发现的/accounts/28088370/events/8514908/videos/185422358.secure.m3u8也是一种视频格式啊，所以我尝试着把上述链接中的.smil更改为.m3u8。这一改竟然可以下载视频对应的.m3u8文件了，如下：

![下载Livestream网站中用户未公开或定期排播视频](https://image.3001.net/images/20190401/1554122142_5ca2059e7bb3a.png!small)如果更改为其它mp4和flv的通用视频格式，Livestream服务端会进行阻拦，只会出现一个黑屏显示，唯独.m3u8格式可以下载。

所以，前面说过，用户ID和事件ID都可以从公开的Livestream帖子中获得，最后只需知道的就是video
id，而且这个id会按照上传次数依次增加1。作为攻击者来说，最简单的方法就是，先以自己的用户身份上传一个视频，上传后可以从请求包中获悉video
id的一个值，然后顺序加1迭代以下请求，如果m3u8文件可以下载，就能跳出上述保存页面，或是在响应中返回200 OK状态码。（这里的y值就是视频video
id值）

> <http://api.new.livestream.com/accounts/public-> account_id/events/public_event_id/videos/>"+y+".m3u8"

基于上述分析，我可以针对特定用户Livestream用户，写出一个脚本来查找用户上传的，一些可能正在编辑且未发布的流视频，并对它们进行下载。脚本的大概工作原理如下：

> iterate y requests to =>
>
> <http://api.new.livestream.com/accounts/public-> account_id/events/public_event_id/videos/>"+y+".m3u8"

## 漏洞上报进程

2019.1.7 漏洞初报

2019.1.21 漏洞修复 并发放$1000赏金

 ***参考来源：[medium](https://medium.com/@abss_tbh/ls-disclose-scheduled-bacc90d6c1f5)，clouds编译，转载请注明来自FreeBuf.COM**

