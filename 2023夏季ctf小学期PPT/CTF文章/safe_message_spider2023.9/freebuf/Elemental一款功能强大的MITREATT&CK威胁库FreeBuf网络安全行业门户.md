![](https://image.3001.net/images/20200502/1588398897_5ead0b3115f2d.png!small)

## Elemental

 **Elemental是一款针对MITRE攻击技术的集中式威胁库，该平台基于Python开发，其中包含了MITRE ATT
&CK技术、Atomic红队测试以及280多条Sigma规则。Elemental提供了一种探索、研究和分析ATT&CK数据集的替代方法，可以帮助研究人员将相关的Atomic红队测试用力和Sigma规则映射到各自对应的技术之中。除此之外，Elemental还可以帮助安全防御端的研究人员创建自定义MITRE
ATT&CK技术并上传Sigma规则。ATT&CK数据集可以通过Python客户端进行收集，Atomic红队测试集可以通过Atomic红队GitHub库导入，Sigma规则（包含了ATT&CK标签的规则集）则通过Sigma的GitHub规则集导入。**

这个平台这个平台被认为是加州大学伯克利分校信息与网络安全硕士项目的一个里程碑，我们期待社区反馈新的想法和改进意见。

当前版本的Elemental实例仅为实验项目，还未配置用于生产环境中，详情请参见Django文档以了解生产服务器配置项。

## 功能介绍

> 1、查看ATT&CK技术信息；
>
> 2、以Markdown和Yaml方式查看Atomic红队测试；
>
> 3、以Yaml方式查看Sigma规则；
>
> 4、添加新的ATT&CK技术信息（当前只能通过Django管理面板添加）；
>
> 5、上传新的Sigma规则（当前只能通过Django管理面板上传）；

## 工具下载&安装

广大研究人员可以使用下列命令下载和安装Elemental平台，并完成依赖组件的配置：

    
    
    git clone <https://github.com/Elemental-attack/Elemental.git>
    
    cd Elemental/elemental
    
    pip install -r requirements.txt
    
    python manage.py runserver

默认的Django管理员面板登录凭证如下：

    
    
    user: elemental | password: berkelium

## 项目运行截图

主元素查看：

![](https://image.3001.net/images/20200502/1588398931_5ead0b53ed7f6.png!small)

技术信息查看：

![](https://image.3001.net/images/20200502/1588398936_5ead0b5817bf7.png!small)

Atomic信息查看：

![](https://image.3001.net/images/20200502/1588398957_5ead0b6d0dba7.png!small)

![](https://image.3001.net/images/20200502/1588398965_5ead0b75932b3.png!small)

Sigma规则查看：

![](https://image.3001.net/images/20200502/1588398978_5ead0b82b63dd.png!small)

## 项目地址

> Elemental：【[ _GitHub传送门_](https://github.com/Elemental-attack/Elemental)】

 *** 参考来源：[ _Elemental_](https://github.com/Elemental-attack/Elemental)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

