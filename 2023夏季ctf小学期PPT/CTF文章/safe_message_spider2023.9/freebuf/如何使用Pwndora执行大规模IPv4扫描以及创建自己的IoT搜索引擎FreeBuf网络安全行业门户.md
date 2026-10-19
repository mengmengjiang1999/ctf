![](https://image.3001.net/images/20220208/1644310675_62023093e3c3ebde12836.png!small)

## 关于Pwndora

Pwndora是一款功能强大的网络安全扫描工具以及物联网搜索引擎，在该工具的帮助下，广大研究人员可以快速实现大规模的IPv4地址扫描，而且该工具还支持多线程任务。

Pwndora使用了套接字（Socket）实现其功能，能够分析目标地址设备的开放端口，并收集有关目标设备的更多详细信息，随后还会将扫描结果存储至Elasticsearch中。

除此之外，广大研究人员还可以将该工具与Kibana集成以实现数据的可视化（操作），相当于在家中也可以拥有一个自己的物联网搜索引擎。

## 功能介绍

> 1、使用不同选项进行端口扫描，并检索软件标题信息。
>
> 2、使用[ _Webtech_](https://github.com/ShielderSec/webtech)集成检测服务器上运行的一些Web技术。
>
> 3、从Maxmind free数据库检索IP地理位置，并定期更新。
>
> 4、可以使用[
> _Rendertron_](https://github.com/GoogleChrome/rendertron)从HTTP主机上获取截图。
>
> 5、在FTP服务器上检测匿名登录。
>
> 6、使用Slack API发送扫描结果通知。

## 工具下载&安装

首先，我们需要确保路径“$HOME/.local/share”存在，以避免[
_Webtech_](https://github.com/ShielderSec/webtech)出现问题。

其次，如果需要使用slack参数的话，则需要在config.py中配置[
_传入Webhook_](https://api.slack.com/messaging/webhooks)的URL地址。

现在，我们就可以使用下列命令将该项目源码克隆至本地了：

    
    
    git clone https://github.com/alechilczenko/pwndora.git

然后使用Python的pip命令安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

接下来，在[ _docker-compose.yml_](https://github.com/alechilczenko/pwndora/blob/main/scanner/Connect.py)中设置Elasticsearch和Kibana容器的密码。

在[ _connect_
_.py_](https://github.com/alechilczenko/pwndora/blob/main/scanner/Connect.py)中配置Elasticsearch连接。

在config.py中设置MaxmindASN、城市数据库和RendertronURL的路径。

使用DockerCompose在后台启动容器。

最后，运行扫描工具即可。

## 工具使用

    
    
    usage: CLI.py [-h] [-s START] [-e END] [-t THREADS] [--massive FILE] [--timeout TIMEOUT]
    
                  [--screenshot] [--top-ports] [--all-ports] [--update]
    
    options:
    
      -h, --help           显示帮助信息和退出show this help message and exit
    
      -s START           IPv4地址起始范围
    
      -e END             IPv4地址终止范围
    
      -t THREADS         线程数量[默认: 50]
    
      --massive FILE      包含IPv4地址范围的文件路径
    
      --timeout TIMEOUT  Socket超时 [默认: 0.5]
    
      --screenshot        从HTTP主机获取截图
    
      --top-ports         仅扫描前20种最常用的端口 [默认]
    
      --all-ports          扫描前1000种最常用的端口
    
      --update           从Wappalyzer更新数据库
    
      --slack             通过Slack发送通知消息

## 工具使用样例

> 注意：如果你是第一次运行Pwndora的话，别忘了使用“--update”参数进行工具更新。

仅扫描一个IPv4地址范围：

    
    
    python3 CLI.py -s 192.168.0.0 -e 192.168.0.255 -t 150 --top-ports

扫描多个IPv4地址范围（文本文件）：

    
    
    python3 CLI.py --massive Argentina.csv -t 200 --all-ports --screenshot

如果你想使用大量线程的话，一些ISP可能会检测到可疑流量，并将你的网络连接断开。

## Kibana样例

![](https://image.3001.net/images/20220208/1644310800_6202311037fe151395dd2.png!small)

## 工具使用演示

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/n1RmVV8Rq800jQlCih8ROWeaY)】

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _2_ _._
_0_](http://www.apache.org/licenses/LICENSE-2.0.html)开源许可证协议。

## 项目地址

 **Pwndora：** 【[ _GitHub传送门_](https://github.com/alechilczenko/pwndora)】

## 参考资料

> [
> _https://github.com/ShielderSec/webtech_](https://github.com/ShielderSec/webtech)
>
> [
> _https://github.com/GoogleChrome/rendertron_](https://github.com/GoogleChrome/rendertron)
>
> [
> _https://api.slack.com/messaging/webhooks_](https://api.slack.com/messaging/webhooks)
>
> [
> _https://github.com/alechilczenko/pwndora/blob/main/scanner/Connect.py_](https://github.com/alechilczenko/pwndora/blob/main/scanner/Connect.py)
>
> [
> _https://github.com/alechilczenko/pwndora/blob/main/scanner/config.py_](https://github.com/alechilczenko/pwndora/blob/main/scanner/config.py)

