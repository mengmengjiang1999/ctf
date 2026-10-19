DRM 全称Digital Rights
Management，即数字版权管理，目的是为了防止带有版权的多媒体内容不被非法访问的访问控制技术，被DRM保护的视频即使下载也无法正常观看。全球现有三大实现方案，分别为谷歌的Widevine、苹果的FairPlay和微软的PlayReady。其中Widevine实现简单，免费，市场占有率最高，应用最广泛。Widevine客户端主要内置于手机、电视、各大浏览器、播放器等，用于解密被保护的视频。本篇文章重点介绍Widevine的工作原理与绕过保护的方法。

## 一、原理

流媒体服务商先将加密视频内容放在自己的内容服务器，将密钥key放置在谷歌提供的Widevine认证服务器。用户播放时，先与Widevine服务器完成认证，得到key之后从内容服务器下载视频，并用key解密播放。

Widevine拥有三个安全级别——L1、L2和L3。L1是最高的安全级别，解密全过程在硬件中完成，需要设备支持。L3的安全级别最低，解密全程在CDM（Content
Decryption Module ）软件中完成。L2介于两者之间， 核心解密过程在硬件完成，视频处理阶段在软件中完成。本文只讨论L3级视频的解密方式。

播放L3级加密视频需要CDM模块，主流的视频播放设备均已内置CDM。播放器调用DRM进行解密时，有以下过程：

  1. 用户开始播放视频时，客户端从视频服务器中下载mpd文件。在解析mpd之后，播放器根据相关字段确定该视频是否使用Widevine加密视频。

  2. 播放器将加密音视频流初始化信息发送给内置的CDM模块解密。

  3. CDM接收到来自播放器的初始化信息，并创建“许可证请求”，然后将其发送回给播放器

  4. 播放器接收到许可证请求后，将该请求发送给Widevine license服务器。许可证请求为全报文加密，抓包改包的方式无法进行攻击。

  5. license服务器接收到播放器发送的请求后解密，提取初始化信息，并通过初始化信息找到其数据库中的播放key。之后将key加密，返回给播放器。

  6. 播放器接收到license服务器返回的key，将它传递给CDM。所有往来流量均被加密，播放器和中间人都无法读取相关信息。

  7. CDM调用相关的解密工具，将加密视频分段解密，实时传送到播放器播放，不在本地存储。

过程图如下：

![](https://image.3001.net/images/20230804/1691135872_64ccaf8099cae24697217.png)

## 二、解密视频的方法

根据上述原理，只要我们能拿到CDM、抓到license服务器请求url，即可构造解密请求报文，获得解密key。但CDM作为播放器的预置模块，没有任何下载渠道，且官方会实时监测滥用情况，CDM解密太频繁会被吊销，故互联网上没有现成的解密工具，也没有任何CDM供下载。所以我们需要自己提取CDM。

### 2.1 提取CDM

最简单的方式是购买一个可root的旧安卓手机，安卓版本需低于11，root后用wvdumper的工具即可提取：<https://github.com/wvdumper/dumper>

操作方法：

  * 安卓安装frida，运行

  * 电脑连接adb调试

  * 电脑运行dump_keys.py

  * 手机浏览器随便播放一个drm视频，例如<https://bitmovin.com/demos/drm>

电脑的key_dumps文件夹里就有两个设备文件了。

注意：DRM视频需要播放成功，才能提取到CDM。若播放失败一般是由于网络问题，可能需要挂代理。如果沒抓到可以多换几个浏览器。![](https://image.3001.net/images/20230804/1691135572_64ccae54324c497afae7a.png)

### 2.2 根据两个设备文件，生成一个设备文件

    
    
    from pywidevine.device import Device
    from pathlib import Path
    
    # e.g., for an Android L3:
    device = Device(
        type_=Device.Types.ANDROID,
        security_level=3,
        flags=None,
        private_key=Path(r"private_key.pem").read_bytes(),
        client_id=Path(r"client_id.bin").read_bytes()
    )
    # save it to a .wvd file for easier loading next time
    device.dump(r"./device.wvd")
    

### 2.3 获取key

所需的材料：

  * mpd 链接。通过抓包或者app逆向获取。

  * PSSH。大部分mpd文件会包含PSSH字符串，少部分mpd只包含了KID，需要用其他工具将KID转换成PSSH，或通过hook等方式抓取播放器内部运算出来的结果。

  * 获取license服务器地址。通过抓包或者app逆向获取。

将参数填入以下脚本可获得key

    
    
    from pywidevine.cdm import Cdm
    from pywidevine.device import Device
    from pywidevine.pssh import PSSH
    
    import requests
    
    # prepare pssh
    pssh = PSSH("AAAAW3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADsIARIQ62dqu8s0Xpa7z2FmMPGj2hoNd2lkZXZpbmVfdGVzdCIQZmtqM2xqYVNkZmFsa3IzaioCSEQyAA==")
    
    # load device
    device = Device.load("./device.wvd")
    
    # load cdm
    cdm = Cdm.from_device(device)
    
    # open cdm session
    session_id = cdm.open()
    
    # get license challenge
    challenge = cdm.get_license_challenge(session_id, pssh)
    
    # send license challenge (assuming a generic license server SDK with no API front)
    proxies = {
      'http': 'http://127.0.0.1:1080',
      'https': 'http://127.0.0.1:1080',
    }
    licence = requests.post("https://cwip-shaka-proxy.appspot.com/no_auth", data=challenge,proxies=proxies)
    licence.raise_for_status()
    
    # parse license challenge
    cdm.parse_license(session_id, licence.content)
    
    # print keys
    for key in cdm.get_keys(session_id):
        print(f"[{key.type}] {key.kid.hex}:{key.key.hex()}")
    
    # close session, disposes of session data
    cdm.close(session_id)
    

得到的key数量不固定，需要全部保存下来。

![](https://image.3001.net/images/20230804/1691136040_64ccb02818022c9827f9e.png)

### 2.4 下载并解密视频：

推荐使用N_m3u8DL-RE+shaka工具：

  * https://github.com/nilaoda/N_m3u8DL-RE

  * https://github.com/shaka-project/shaka-packager

将N_m3u8DL-RE和packager-linux-x64放在同一目录，运行以下命令即可下载+解密。

    
    
    ./N_m3u8DL-RE -M format=mp4 "https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd" --key ccbf5fb4c2965be7aa130ffb3ba9fd73:9cc0c92044cb1d69433f5f5839a159df --key 9bf0e9cf0d7b55aeb4b289a63bab8610:90f52fd8ca48717b21d0c2fed7a12ae1 --key eb676abbcb345e96bbcf616630f1a3da:100b6c20940f779a4589152b57d2dacb --key 0294b9599d755de2bbf0fdca3fa5eab7:3bda2f40344c7def614227b9c0f03e26 --key 639da80cf23b55f3b8cab3f64cfa5df6:229f5f29b643e203004b30c4eaf348f4 --use-shaka-packager --save-name day6.mp4 --live-real-time-merge -sv best -sa best
    

![](https://image.3001.net/images/20230804/1691136120_64ccb0784c4e3019e4866.png)![](https://image.3001.net/images/20230804/1691136146_64ccb092946499fd4bd6c.png)

## 三、总结

L3级的加密保护相对于无保护的视频更安全，大大提高了解密门槛。但安全性不足，理论上都可以解密，流媒体内容商若想进一步提高安全性，建议使用L1级加密、将license
server等关键信息加密隐藏、检验播放环境是否root等方式，进一步提高解密门槛。

