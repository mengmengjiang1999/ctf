![](https://image.3001.net/images/20211008/1633684359_61600b8736561ee3ee32f.png!small)

## 关于CrowdSec

CrowdSec是一个功能强大的行为检测引擎，CrowdSec当前处于开放源代码状态，能够通过参与式IPS来分析访客行为，并且能够为用户针对各种攻击提供适应性响应。除此之外，CrowdSec还可以利用群组功能生成一个全局CTI数据库，以保护用户网络。

CrowdSec是一个免费的、现代的、协作性的行为检测引擎，它遵循fail2ban的理念，但与IPV6兼容，速度快了将近60倍（Go和Python对比）。CrowdSec使用Grok模式解析日志，使用YAML场景识别行为。CrowdSec专为基于云/容器/虚拟机的现代基础设施而设计，一旦检测到威胁，我们就可以使用各种保护机制来缓解威胁。而攻击性IP将会被发送至CrowdSec进行治理，然后在所有用户之间共享，以进一步提高每个人的安全性。

Crowdsec是一款开源的轻量级软件，可检测具有攻击性行为的对等方，以阻止他们访问你的系统。Crowdsec的操作非常简单，可以为广大研究人员提供一个低技术壁垒但高安全增益的安全保护基础设施。

 **该项目的体系架构如下图所示：**

![](https://image.3001.net/images/20211008/1633684373_61600b9539dc3976bf4d5.png!small)

## 工具安装

### 通过包安装（Debian）

    
    
    curl -s https://packagecloud.io/install/repositories/crowdsec/crowdsec/script.deb.sh | sudo bash
    sudo apt-get update
    sudo apt-get install crowdsec

### 通过包安装（RHEL/CentOS/Amazon Linux）

    
    
    curl -s https://packagecloud.io/install/repositories/crowdsec/crowdsec/script.rpm.sh | sudo bash
    sudo yum install crowdsec

### 通过包安装（FreeBSD）

    
    
    sudo pkg update
    sudo pkg install crowdsec

### 源码安装

    
    
    wget https://github.com/crowdsecurity/crowdsec/releases/latest/download/crowdsec-release.tgz
    tar xzvf crowdsec-release.tgz
    cd crowdsec-v* && sudo ./wizard.sh -i

## 工具使用演示

### 自动初始化配置，提供了功能性的开箱即用设置

![](https://image.3001.net/images/20211008/1633684424_61600bc8a6d5f98a2d789.gif!small)

### 基线检测开箱即用，无需微调配置

![](https://image.3001.net/images/20211008/1633684550_61600c46e84407b95a87b.gif!small)

### 轻松部署强制性安全措施

![](https://image.3001.net/images/20211008/1633684653_61600cadbf632ac8954e7.gif)

### 轻松部署元数据界面，可使用cscli轻松查看数据

![](https://image.3001.net/images/20211008/1633684691_61600cd3055ed963f3e00.gif)

### 日志处理，支持取证和测试

![](https://image.3001.net/images/20211008/1633684718_61600cee059e0dfdd54bc.gif)

## 项目地址

 **CrowdSec：** 【[ _GitHub传送门_](https://github.com/crowdsecurity/crowdsec)】

## 参考资料

> [
> _https://github.com/crowdsecurity/hub_](https://github.com/crowdsecurity/hub)
>
> [ _http://github.com/crowdsecurity/crowdsec-> docs_](http://github.com/crowdsecurity/crowdsec-docs)
>
> [
> _https://hub.crowdsec.net/browse/#bouncers_](https://hub.crowdsec.net/browse/#bouncers)

