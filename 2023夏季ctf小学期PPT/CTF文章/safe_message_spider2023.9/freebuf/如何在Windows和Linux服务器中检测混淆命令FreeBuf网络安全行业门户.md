![1.png](https://image.3001.net/images/20190517/1558027084_5cdd9b4c53f4c.png!small)

## 工具介绍

**在目前的无文件恶意软件或网络犯罪领域中，命令行混淆已经是很常见的了。为了绕过基于签名的安全检测机制，红队渗透测试以及APT攻击活动都会使用各种专用的混淆/模糊技术。同时，许多代码混淆工具（即执行语法转换工具）都已开源，这也使得网络攻击者们对给定命令进行混淆处理变得越来越容易了。**

然而，针对这类技术的防御工具却仍然很少。针对Linux的命令行混淆，我们几乎找不到任何可以使用的检测工具。在防范Windows命令混淆方面，现有的方案要么是缺乏相应工具，要么只是解决了部分问题，并没有彻底解决所有问题。

为了更好地检测相关威胁，我们设计并开发了Flerken，这是一个工具化的平台，可以用来检测Windows（CMD和PowerShell）和Linux（Bash）命令。Flerken可分为Kindle和Octopus这两个模块，其中Kindle针对的是Windows模糊检测工具，而Octopus针对的是Linux模糊测试工具。除此之外，为了优化Flerken的分类性能，我们还引入了机器学习、双向特征过滤和脚本沙盒等技术。

## 工具安装&使用

### 工具安装

1、 确保服务器端已安装了Python 3.x，你可以使用下列命令来检测：

    
    
    [root@server:~$]python –V

2、 安装依赖组件，所有的依赖组件已在requirement.txt中声明：

    
    
    [root@server:~$]python –V

3、 登录MySQL控制台，导入数据库：

    
    
    source/your path/Flerken/flerken/lib/flerken.sql

4、 自定义配置Flerken App：

    
    
    Path:flerken/config/global_config.py

5、 运行工具：

    
    
    [root@server:~$]python runApp.py

6、（可选）为了降低假阳性，可根据需要构建白名单规则：

    
    
    Path:flerken/config/whitelists/

### 工具使用

工具的使用如下图所示，我们还可以使用API接口：

![2.gif](https://image.3001.net/images/20190517/1558027146_5cdd9b8a6e1a5.gif!small)

## 获取帮助信息

如果你对Flerken的使用有任何疑问，可以直接创建issue并进行标注，我们会尽快解决大家提出的问题：

![3.png](https://image.3001.net/images/20190517/1558027164_5cdd9b9c884e2.png!small)

### 内置的第三方库

> [Flask](http://flask.pocoo.org/)
>
> [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable)
>
> [Flask-Limiter](https://flask-limiter.readthedocs.io/)
>
> [frankie-huang/pythonMySQL](https://github.com/frankie-huang/pythonMySQL)
>
> [jQuery](https://jquery.org/)
>
> [Swiper](https://idangero.us/swiper)

## 许可证协议

Flerken遵循Apache 2.0许可证协议。

## 项目地址

Flerken：【[GitHub传送门](https://github.com/We5ter/Flerken)】

### 工具文档

如需了解关于Flerken的细节内容，可查看Flerken的官方文档：【[点我获取](https://github.com/We5ter/Flerken/blob/master/doc/Flerken_v1.0.2_Specification_%20Document.pdf)】

***参考来源：[We5ter](https://github.com/We5ter/Flerken)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

