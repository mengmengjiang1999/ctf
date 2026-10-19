![](https://image.3001.net/images/20220818/1660798920_62fdc7c851edbfcd515f3.png!small)

## 关于Kage

Kage是一款针对Metasploit
RPC服务器的图形化用户交互工具，该工具可以帮助广大研究人员通过图形化的用户UI界面与Meterpreter会话进行交互，并生成Payload。需要注意的是，当前版本的Kage仅支持windows/meterpreter和android/meterpreter。

## 工具要求

本地设备上安装并配置好了[ _Metasploit_ _-_
_Framework_](https://github.com/rapid7/metasploit-framework)，PATH环境变量中包含下列组件：

> Msfrpcd
>
> Msfvenom
>
> Msfdb

## 工具安装

### 预编译安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/Zerx0r/Kage/releases)】下载预编译好的工具代码。

### 源码获取

针对开发人员，也可以直接下载该项目的源代码，并进行手动构建。

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/WayzDev/Kage.git

接下来，切换到项目目录并安装该工具所需的依赖组件：

    
    
    cd Kage
    
    yarn # 或npm install
    
    yarn run dev # 或npm run dev

下列命令即可构建项目代码：

    
    
    yarn run build

注意，如需生成APK Payload，请在下拉菜单中选择Raw格式。

我们推荐使用electron-vue，因为它可以更好地处理工具依赖组件，并减少最终生成的构建代码大小。

## 工具运行截图

### 工具仪表盘

![](https://image.3001.net/images/20220818/1660798997_62fdc8152364c6768b582.png!small)

### 工具控制面板

![](https://image.3001.net/images/20220818/1660799004_62fdc81c1249c0c210485.png!small)

### 服务器状态

![](https://image.3001.net/images/20220818/1660799011_62fdc8234976d9f0fd122.png!small)

### 文件管理

![](https://image.3001.net/images/20220818/1660799017_62fdc829d7a014947bed9.png!small)

### 会话管理

![](https://image.3001.net/images/20220818/1660799070_62fdc85ecad155ce97208.png!small)

## 工具使用演示

 **视频地址** ：【[ _点我观看_](https://vimeo.com/319338721)】

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3_ _._
_0_](https://github.com/Zerx0r/Kage/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Kage** ：【[ _GitHub传送门_](https://github.com/Zerx0r/Kage)】

## 参考资料

> [ _https://github.com/AhMyth/AhMyth-Android-> RAT_](https://github.com/AhMyth/AhMyth-Android-RAT)
>
> [ _https://github.com/rapid7/metasploit-> framework_](https://github.com/rapid7/metasploit-framework)
>
> [ _https://simulatedgreg.gitbooks.io/electron-> vue/content/en/getting_started.html_](https://simulatedgreg.gitbooks.io/electron-> vue/content/en/getting_started.html)
>
> [ _https://yarnpkg.com/en/_](https://yarnpkg.com/en/)
>
> [ _http://www.metasploit.com/_](http://www.metasploit.com/)
>
> [ _https://github.com/tomasgvivo/node-> msfrpc_](https://github.com/tomasgvivo/node-msfrpc)
>
> [ _https://github.com/SimulatedGREG/electron-> vue_](https://github.com/SimulatedGREG/electron-vue)
>
> [ _https://github.com/vuejs/vue-cli_](https://github.com/vuejs/vue-cli)
>
> [ _https://simulatedgreg.gitbooks.io/electron-> vue/content/index.html_](https://simulatedgreg.gitbooks.io/electron-> vue/content/index.html)

