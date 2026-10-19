![](https://image.3001.net/images/20220105/1641382478_61d5824e1f7ecb9da7ec3.png!small)

## 关于Umay

Umay是一款功能强大的物联网恶意软件相似性分析平台，该项目可以帮助广大研究人员针对基于共享代码的物联网恶意软件相似性进行分析，以识别与目标分析文件共享代码的其他恶意软件。

在Umay的帮助下，广大研究人员可以更好地了解目标恶意软件家族。而在当前的物联网生态系统中有各种具有不同体系结构的设备，那么在解决多体系结构问题时，基于静态的分析方法将更加有效。

该项目中使用了IoTPOT提供的1000个恶意软件二进制文件。Radare2负责提取每个二进制文件的基本代码块和函数，并将这些数据的哈希值存储在SQL数据库中。接下来，工具会从SQL数据库中查询并获取需要分析的样本基本代码块和函数，并给广大研究人员枚举出所有具有共享代码的恶意软件。

## 当前功能

1、基于静态代码分析技术分析恶意软件的共享代码；

2、支持ARM、MIPS、x86-64、i386、PowerPC、m68k和Renesas SH；

## 工具依赖组件

> 1、Python 3+
>
> 2、[ _Radare2_](https://github.com/radareorg/radare2)：r2pipe

## 工具下载&安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地，并在终端中切换至项目根目录：

    
    
    git clone https://github.com/mucoze/Umay
    
    cd Umay

接下来，创建并激活Python虚拟环境（virtualenv）：

    
    
    virtualenv venv
    
    source venv/bin/activate

使用pip命令安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

此时，我们就可以使用下列命令配置工具，创建用户并启动服务器了：

    
    
    python manage.py makemigrations
    
    python manage.py migrate
    
    python manage.py createsuperuser
    
    python manage.py runserver

启动之后，广大研究人员就可以通过浏览器访问“127.0.0.1:8000”来使用Umay了。

## 创建我们自己的数据集文件

    
    
    python create_dataset.py samples/

在上述命令中，我们需要通过命令行参数的形式将存储了所有样本的目录路径提供给Umay，此时Umay将会帮助我们生成一份dataset.db文件。

## 许可证协议

本项目的开发与发布遵循[ _Apache
v2.0_](https://github.com/mucoze/Umay/blob/main/LICENSE)开源许可证协议。

## 工具线上体验平台

 **Umay：** 【[ _在线体验_](https://umay.xyz/)】

## 项目地址

 **Umay：** 【[ _GitHub传送门_](https://github.com/mucoze/Umay)】

## 参考资料

> [ _https://umay.xyz/_](https://umay.xyz/)
>
> [ _https://sec.ynu.codes/iot/_](https://sec.ynu.codes/iot/)
>
> [
> _https://github.com/radareorg/radare2_](https://github.com/radareorg/radare2)

