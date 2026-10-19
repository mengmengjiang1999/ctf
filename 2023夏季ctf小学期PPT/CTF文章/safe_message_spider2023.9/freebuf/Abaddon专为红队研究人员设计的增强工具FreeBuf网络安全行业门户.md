![](https://image.3001.net/images/20211225/1640400122_61c684fa254d0f4abd025.jpg!small)

## 关于Abaddon

红队研究活动中往往会涉及到各种技术技能的实现，不仅研究时间有可能会持续好几个月，而且还会涉及到大量敏感操作。因此，红队研究活动也需要进行大量的监控，并要求谨慎操作。Wavestone研发的Abaddon工具旨在帮助红队研究人员提升运营效率，并通过更高的速度和更隐蔽的方式执行某些重复操作，同时还提供了很多辅助增强工具和报告功能。

当前社区中，红队研究人员也有很多可使用的工具，但缺少了免费开源的运营管理软件，而且很多工具之间并没有办法进行聚合，操作故障等情况也很常见。

## Abaddon的功能

Abaddon旨在通过下列方法为红队研究人员提供增强服务：

> 1、减少红队构建基础设施所需的时间；
>
> 2、仅需点击一至两下鼠标，即可完成复杂的操作活动；
>
> 3、长时间红队活动可轻松生成报告；
>
> 4、降低“OPSEC错误”风险；

## Abaddon系统架构

![](https://image.3001.net/images/20211225/1640400164_61c68524c7366a71b9c9a.png!small)

> 1、三十分钟内完成基础设施部署；
>
> 2、支持认证和加密；
>
> 3、启用网络钓鱼和远程命令执行

## 其他功能

> 1、网络侦察：NMAP图形化接口、Recon-NG、HunterIO和Amass；
>
> 2、工具化：可以在开发中生成经过模糊处理的Payload；
>
> 3、快速交付：一至两次点击，即可部署EC2实例、Gophish、功能完整隐蔽性强且Docker化的C&C基础设施和其他完整功能；
>
> 4、报告生成：提供了简单的仪表盘来查看所有的操作信息；

## 工具安装&启动

当前版本的Abaddon已在Debian、LUbuntu和Kali
Linux上进行过测试，在使用Abaddon时必须要接入网络，如果你想要在本地部署C&C服务器的话，还需要一个公网IP地址。

如需配置AWS环境，可以直接点击【[
_这里_](https://docs.aws.amazon.com/fr_fr/cli/latest/userguide/install-cliv2-linux.html)】进行配置。

    
    
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    
    unzip awscliv2.zip
    
    sudo ./aws/install

首先，我们需要使用下列命令将该项目源码克隆至本地，并切换至项目根目录中：

    
    
    git clone git@github.com/wavestone-cdt/abaddon.git
    
    cd abaddon

使用我们的AWS凭证和配置来创建“~/.aws/credentials and ~/.aws/config”：

    
    
    aws configure

接下来，将settings.py.samble重命名为settings.py，然后修改数据库用户密码：

    
    
    mv abaddon/settings.py.sample abaddon/settings.py
    
    sed -i 's/yourPasswordHere/<databasepassword>/g' abaddon/settings.py

最后，使用下列命令切换至abaddon/setup目录下，并启动安装：

    
    
    bash setup/install.sh

## 工具使用

该工具的使用非常简单，我们只需运行下列命令：

    
    
    bash abaddon.sh

接下来，打开浏览器，并访问“127.0.0.1:8080”，即可开始使用。

## 项目地址

 **Abaddon：** 【[ _GitHub传送门_](https://github.com/wavestone-cdt/abaddon)】

## 参考资料

    
    
    https://www.rsaconference.com/usa/us-2020/agenda/abaddon-the-red-team-angel

