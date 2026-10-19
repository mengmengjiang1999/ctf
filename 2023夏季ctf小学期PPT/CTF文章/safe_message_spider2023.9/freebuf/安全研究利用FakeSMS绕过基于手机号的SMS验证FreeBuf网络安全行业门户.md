![](https://image.3001.net/images/20210316/1615903827_6050bc536279d6b1fef3b.jpg!small)

## 关于Fake-SMS

Fake-SMS是一款简单但功能十分强大的命令行工具，该工具可以帮助广大研究人员使用一个临时手机号并将其作为代理的形式来绕过基于手机号的SMS短信验证机制。

该工具目前只是一个实验性工具，请不要将其用于任何银行转账操作中！除此之外，也不要将其用于恶意目的。

该工具使用的是欧洲服务提供商Upmasked的消息服务，数据将存储在Upmasked的服务器上，因此需要确保同意欧盟数据治理法和GDPR。开发者建议广大研究人员不要将此用于任何暴露自己身份的个人交易。

## 功能介绍

> 该工具基于Go v1.15开发，并启用了模块支持；
>
> 提供了交互式命令行接口，易于使用；
>
> 提供了基于数据库的本地文件存储支持，可以帮助我们更好地管理、记录和复用伪造手机号列表；
>
> 提供了Upmasked非官方客户端；

## 环境要求

Go编程语言环境v 1.15+。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Narasimha1997/fake-sms.git

## 代码构建

Fake-SMS的构建也非常简单，跟其他Go模块的构建方式相同。我们可以运行下列命令来构建Fake-SMS：

    
    
    export GOBIN=$PWD/bin
    
    go install

上述命令将完成代码构建，并将构建好的项目存储在bin/目录下。我们也可以考虑使用bin/目录下已提供的预编译代码。

## 工具使用

第一步，在本地数据库中注册一个手机号，我们也可以选择已有的其中一个手机号进行注册，具体如下图所示：

![](https://image.3001.net/images/20210316/1615903857_6050bc71cc908e31b6522.gif!small)

第二步，利用注册的手机号获取信息。我们可以选择第一步存储的手机号，然后以列表的形式查看其消息。该工具还可以将数据以JSON格式导出，即“${PWD}/selected-phone-number.json”。具体如下图所示：

![](https://image.3001.net/images/20210316/1615903886_6050bc8e0e6f06257b5be.gif!small)

第三步是可选项，我们可以选择删除已记录的手机号或列表项。

## 项目地址

Fake-SMS：【[ _GitHub传送门_](https://github.com/Narasimha1997/fake-sms)】

## 参考资料

> [
> _https://github.com/sdushantha/tmpsms_](https://github.com/sdushantha/tmpsms)
>
> [ _https://upmasked.com/_](https://upmasked.com/)

