## Kali-Linux-Tools-Interface

在当今这个信息时代，数据是最有价值的资产，因此，广大用户和企业已成为网络攻击的主要目标。众所周知，信息安全专业人员都会使用一系列技术工具来协助他们的活动。但是设置环境，安装这些工具，设置每个工具并保持最新状态需要花费很长的时间，最鼎鼎大名的当属Kali
Linux系统了。对于用户而言，有时找到满足特定需求的正确工具可能需要搜索或咨询系统文档。此外，为了全面了解系统，不仅需要在操作上，而且在操作每个工具时，都需要广泛而专门的学习曲线。因此，许多用户最终会使用在线课程来掌握特定工具。然而，由于每个工具都有无数独特的语法，因此文档对于使用各种工具几乎成为强制性的。考虑到上述这种情况，Kali-Linux-Tools-Interface便应运而生。

Kali-Linux-Tools-Interface是一款针对Kali
Linux的图形化Web接口，在该工具的帮助下，广大研究人员可以在无需安装和配置Kali Linux系统的情况下，轻松使用Kali
Linux中大量的信息安全工具。

本质上来说，Kali-Linux-Tools-Interface就是一个图形化接口，可以帮助广大研究人员直接通过浏览器来使用各种信息安全工具。该项目主要参考和集成的是Kali
Linux中的各种安全工具，并且最大程度地集成了Kali Linux发行版中的本地工具包。

该项目的另一个优势是对多个平台的支持。对于智能手机，将不再需要具有root用户访问权限的Nexus设备来安装NetHunter和使用Kali
Linux工具。Kali Linux工具可以在具有浏览器的任何平台上使用，甚至可以仅使用智能手机执行审核。

## 工具依赖

  * 一个基于Debian的Linux发行版系统；
  * 目标信息安全工具已安装；
  * 已运行Apache/Nginx服务；
  * 已运行SSH服务；
  * Shell In A Box-如需安装该工具，可直接运行下列命令：

    
    
    sudo apt-get install shellinabox

## 工具安装

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/lucasfrag/Kali-Linux-Tools-Interface.git

在本地的MySQL数据库中创建一个名为“kali”的数据库，并导入项目代码中的“assets/database.sql”数据库文件。接下来，编辑项目代码中的“assets/includes/config.php”文件，并完成相应的配置设置。此时，我们就可以开始使用Kali-Linux-Tools-Interface啦！

## 工具运行截图

### 工具仪表盘

![](https://image.3001.net/images/20200804/1596494704.png!small)

### 可用工具列表

![](https://image.3001.net/images/20200804/1596494713.png!small)

### 选择工具并使用

![](https://image.3001.net/images/20200804/1596494725.png!small)

## 工具构建组件

  * [Argon Dashboard](https://demos.creative-tim.com/argon-dashboard/)
  * [Bootstrap 4](https://getbootstrap.com/)
  * [PHP 7](https://php.net/)
  * [PHP Secure Communications Library](https://github.com/phpseclib/phpseclib)
  * [JQuery](https://jquery.com/)

## 许可证协议

本工具的开发与发布遵循MIT开源许可证协议。

## 项目地址

Kali-Linux-Tools-Interface：【[ _GitHub传送门_](https://github.com/lucasfrag/Kali-Linux-Tools-Interface)】

## 参考文档

Kali-Linux-Tools-Interface：【[ _参考文档-葡萄牙语_](https://medium.com/@ti.lucasfraga/documenta%C3%A7%C3%A3o-do-projeto-final-de-ads-f80a1117841f)】

