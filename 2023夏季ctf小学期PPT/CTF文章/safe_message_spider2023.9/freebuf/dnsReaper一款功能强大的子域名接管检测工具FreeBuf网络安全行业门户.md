![](https://image.3001.net/images/20220830/1661861320_630dfdc8d1856323432d2.jpg!small)

## 关于dnsReaper

dnsReaper是一款功能强大的子域名接管检测工具，该工具专为蓝队研究人员和漏洞猎人设计，并且能够在保证运行速度的情况下，提供较高的检测准确率。

该工具每秒大约可以扫描50个子域名，并能针对每个子域名执行50次接管签名检测。这也就意味着，我们只需要大约10秒钟，即可扫描完成整个组织的全部DNS资产。

## 运行机制

我们可以直接将目标域名列表以文件的形式提供给dnsReaper，也可以直接在命令行窗口中扫描单个域名。接下来，dnsReaper便会对目标域名进行扫描，并生成CSV结果文件。

除此之外，该工具还可以帮我们获取DNS记录，dnsReaper支持连接DNS服务提供商，并获取和测试目标域名的所有DNS记录。

当前版本的dnsReaper支持AWS Route53、Cloudflare和Azure，当然我们也可以自行添加其他的DNS服务商。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/punk-security/dnsReaper.git

## 工具使用

如需运行dnsReaper，你可以使用Docker镜像或直接以Python脚本的方式运行。

首先，我们需要在本地设备上安装并配置好Python
3.10环境，该工具扫描到的所有信息都会以输出文件的形式提供，输出文件会在本地以“results.csv”文件存储，当然也可以支持通过JSON输出进行存储。

### 使用Docker运行

    
    
    docker run punksecurity/dnsreaper --help

### 使用Python运行

    
    
    pip install -r requirements.txt
    
    python main.py --help

## 工具使用

### 扫描AWS账号

    
    
    docker run punksecurity/dnsreaper aws --aws-access-key-id <key> --aws-access-key-secret <secret>

### 通过文件扫描全部域名

    
    
    docker run -v $(pwd):/etc/dnsreaper punksecurity/dnsreaper file --filename /etc/dnsreaper/<filename>

### 扫描单个域名

    
    
    docker run punksecurity/dnsreaper single --domain <domain>

### 扫描当个域名并将结果输出至STDOUT

    
    
    docker run punksecurity/dnsreaper single --domain <domain> --out stdout --out-format=json > output

## 工具运行演示

![](https://image.3001.net/images/20220830/1661861388_630dfe0c8b287e4202b58.png!small)

## 许可证协议

本项目的开发与发布遵循[ _AGPL_ _-3.0_](https://github.com/punk-security/dnsReaper/blob/main/LICENSE)开源许可证协议。

## 项目地址

dnsReaper：【[ _GitHub传送门_](https://github.com/punk-security/dnsReaper)】

## 参考资料

> [ _https://www.punksecurity.co.uk/_](https://www.punksecurity.co.uk/)

