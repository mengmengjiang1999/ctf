![](https://image.3001.net/images/20221213/1670898971_6397e51bb57ad32a4aca8.png!small)

## 关于r4ven

r4ven是一款功能强大的用户敏感信息安全检测工具，该工具可以托管一个伪造的网站，而这个网站使用了一个iframe来显示一个合法网站的信息，如果目标允许其运行，那么它将会获取目标的GPS地理位置信息（坐标经纬度）、IP地址和设备其他信息。

简而言之，我们可以使用该工具来尝试获取目标用户手机或电脑的IP地址以及GPS地理位置信息，并以此来检查和判断用户的敏感信息安全态势。

在该工具的帮助下，我们可以更好地了解恶意网站能够收集到的关于用户设备的各种信息，以及为何要求你不要点击或允许任何未知来源链接的原因。

该工具仅可用于教育用途，请不要将其用于恶意目的。

## 功能介绍

> 1、用户只需要点击链接，该工具便会自动获取目标设备的IP地址以及设备相关信息；
>
> 2、如果用户允许了网站获取定位权限，该工具则会提取目标设备的GPS地理位置信息；

## 工具限制

> 1、目标设备GPS功能损坏；
>
> 2、浏览器禁用JavaScript；
>
> 3、用户使用了GPS定位模拟；
>
> 4、Safari和Brave浏览器自动会屏蔽定位获取权限请求；
>
> 5、Firefox：新版本更新后会它允许定位权限请求，但定位并不准确；
>
> 6、效果最好的是Chrome浏览器，如果使用的是智能手机则定位更加准确；

## IP地址 vs GPS地理位置

> 1、基于IP地址的地理位置信息其实并不准确，因为返回的位置信息并不是目标设备的信息，而是互联网服务提供商的大概位置；
>
> 2、而GPS定位信息使用的是设备所在位置的经纬度，因此更加准确，大约只有20-30米的偏差；

## 操作系统支持

> 1、Windows；
>
> 2、Linux；
>
> 3、Android；
>
> 4、macOS；

## 工具要求

> 1、Python 3；
>
> 2、Git；
>
> 3、Discord Webhook；

## 工具安装

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/spyboy-productions/r4ven.git

接下来，切换到项目目录中，然后使用下列命令安装该工具所需的依赖组件：

    
    
    cd r4ven
    
    pip3 install -r requirements.txt
    
    python3 r4ven.py

## 工具使用

接下来，输入你的Discord Webhook地址【[ _参考资料_](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)】，如果没有Discord账号的话，可以自己注册一个【[
_参考资料_](https://discord.com/)】。

工具运行后，一旦用户点击了链接，那么追踪数据将会发送到你的Discord Webhook中。

如需修改网站模板。可以打开index.html文件并定位到12行，替换iframe中的src属性值即可。注意，并非所有网站都支持iframe。

## 工具运行截图

![](https://image.3001.net/images/20221213/1670899050_6397e56ab63ba27364886.png!small)![](https://image.3001.net/images/20221213/1670899093_6397e595586f8971a932d.png!small)

![](https://image.3001.net/images/20221213/1670899102_6397e59e0248c4611a23b.png!small)

![](https://image.3001.net/images/20221213/1670899113_6397e5a97083da2644c82.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/spyboy-productions/r4ven/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **r4ven** ：【[ _GitHub传送门_](https://github.com/spyboy-productions/r4ven)】

## 参考资料

> [ _https://support.discord.com/hc/en-us/articles/228383668-Intro-to-> Webhooks_](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-> Webhooks)
>
> [ _https://discord.com/_](https://discord.com/)

  

