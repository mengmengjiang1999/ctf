## 关于IDACode

IDACode是一款功能强大的代码执行和调试工具，该工具可以帮助广大研究人员在IDA环境中执行和调试Python脚本，而且无需频繁切换窗口，也无需离开Visual
Studio Code。注意，该项目的VS code插件可以直接在[
_官方插件市场_](https://marketplace.visualstudio.com/items?itemName=Layle.idacode)中下载安装。

当前版本的IDACode仍处于前期开发阶段，因此可能会出现一些bug，不过别担心，我们的开发人员会在短时间内进行修复，也欢迎大家积极提交各种issue。

## 功能介绍

> 速度快：支持快速创建和执行脚本。
>
> 调试功能强大：可随时添加Python调试器。
>
> 兼容性：IDACode不要求我们以特定的方式修改脚本，所有脚本都可以在IDA中执行，无需做任何更改。
>
>
> 模块化：IDACode没有在线程同步中使用安全封装工具，这将允许我们在任何给定的时间从任何路径导入任何模块。而IDACode会将脚本执行线程与IDA主线程同步，以避免性能和其他意外问题。
>
> 同步：由于IDACode使用debugpy进行通信，它可以直接将输出窗口与VS Code的输出面板同步。

注意：IDACode同时支持Python 2和Python 3。

## 工具安装

首先，我们需要安装好DIA插件运行所需的依赖环境。确保使用了正确的Python版本，IDACode支持最新版本的的debugpy（v3.0.0），请确保环境完成升级。

    
    
    python -m pip install --user debugpy tornado

接下来，访问该项目的【[
_Releases页面_](https://github.com/ioncodes/idacode/releases)】下载项目代码，或者使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ioncodes/idacode.git

然后将ida.zip文件中的所有内容拷贝到IDA插件目录下。

下一步，就是要设置符合我们环境的配置文件了。根据你的实际情况编辑

idacode_utils/settings.py文件：

> HOST：主机地址，一般为127.0.0.1，除非你使用了远程地址。
>
> PORT：IDA需要监听的端口号，主要用于IDA和VS Code之间的Websocket通信。
>
> DEBUG_PORT：需要监听的传入调试会话端口
>
> PYTHON：IDA所使用的Python发行版安装绝对地址。
>
>
> LOGGING：决定调试器是否将信息记录至文件中，当我们的代码遇到问题时，这个功能就非常有用了。日子文件地址位于你设备的临时目录中，Windows的话就是“%TEMP%”，日子文件命名规则为“debugpy.*.log”。

此时，你就可以在工具的插件菜单中点击“IDACode”来开启插件了。

## 工具使用

### IDA

点击插件菜单中的“IDACode”，此时你将会看到如下所示的信息：

    
    
    IDACode listening on 127.0.0.1:7065

### VS Code

当前版本的IDACode支持默认开启“Execute on save”功能，VS Code将会自动在保存（比如说按下CTRL +
S）了当前脚本文档之后在IDA中执行你的脚本代码。

工具提供了四个可用命令以供使用：

![](https://image.3001.net/images/20220228/1646024795_621c585ba63661b691f14.png!small)

接下来，打开一个文件夹，把你的脚本放进去，然后连接IDA即可。请记住，在重新启动IDA之前，调试会话是永久存在的。一旦调试器启动，就不能更改工作区文件夹了。

因此，你需要确保工作区文件夹是主脚本所在的文件夹。一旦连接建立成功，就可以在IDA中选择执行脚本了。

### 调试功能

IDACode使用了VS Code的远程调试器连接到IDA，并支持VS
Code的全部功能。但是，我们还需要使用到Python的内置功能来指定脚本的入口点，比如断点功能。这个功能可以告诉调试器暂停执行，如果没有调试器，它将忽略该功能。

IDACode还会导入一个名为dbg的辅助功能包，该包实现了一个名为bp的断点重载功能，并且支持日志记录和条件设置：

    
    
    name = idc.get_segm_name(segment)
    
    dbg.bp(name==".text", f"found {name} at {segment}")

## 工具使用样例

![](https://image.3001.net/images/20220228/1646024829_621c587d362868b0da07d.gif)

## 项目地址

 **IDACode：** 【[ _GitHub传送门_](https://github.com/ioncodes/idacode)】

## 参考资料

> [
> _https://marketplace.visualstudio.com/items?itemName=Layle.idacode_](https://marketplace.visualstudio.com/items?itemName=Layle.idacode)
>
> [
> _https://github.com/ioncodes/idacode/releases_](https://github.com/ioncodes/idacode/releases)
>
> [
> _https://marketplace.visualstudio.com/items?itemName=Layle.idacode_](https://marketplace.visualstudio.com/items?itemName=Layle.idacode)
>
> [ _https://github.com/ioncodes/idacode/tree/master/idacode#extension-> settings_](https://github.com/ioncodes/idacode/tree/master/idacode#extension-> settings)

