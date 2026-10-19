![a.png](https://image.3001.net/images/20200502/1588405690_5ead25ba09c42.png!small)

## RMS-Runtime-Mobile-Security

 **Runtime Mobile Security (RMS)是一款功能强大的Web接口，在它的帮助下，研究人员可以在运行时对Android
Java类和方法进行分析和修改。**

Runtime Mobile Security (RMS) 由[
_Frida_](https://github.com/frida/frida)驱动，并且提供了功能强大且简单易用的Web接口，我们可以使用RMS在程序运行时轻松导出所有加载的类已经相对应的方法，并对函数设置钩子，追踪方法参数和返回值，加载自定义脚本以及其他各种实用功能。

### 工具信息

Runtime Mobile Security (RMS)当前仅支持Android设备，并在macOS平台上进行过测试，目前支持下列运行设备：

> 1、AVD模拟器；
>
> 2、Genymotion模拟器；
>
> 3、Amazon Fire Stick 4K；

理论上该工具也能够在Windows以及Linux平台上运行，但还需要配置一些其他的依赖组件。

### 工具依赖

Runtime Mobile Security (RMS)的正常使用要求在目标设备上开启和运行Frida服务器。

关于Frida服务器的安装和配置，请参考Frida官方文档：【[ _传送门_](https://frida.re/docs/android/)】。

## 工具安装

1、（可选）创建一个Python虚拟环境。

2、然后运行下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security.git

3、然后运行下列代码安装工具依赖组件：

    
    
    pip3 install -r requirements.txt

4、使用下列命令运行Runtime Mobile Security (RMS)：

    
    
    python3 mobilesecurity.py

## 工具使用

第一步：通过输入应用包名来运行你的目标App。

请注意，RMS会绑定一个名叫`com.android.systemui`的持久化进程来获取已加载进内存中的所有类（在运行目标App之前）。当然了，你也可以通过Config标签页或编辑`config.json`文件来设置其他的默认包。

![Image](https://image.3001.net/images/20200502/1588408873_5ead32299cb14.gif)

第二步：检测已加载进内存中的类和方法。

![Image](https://image.3001.net/images/20200502/1588408886_5ead3236c24a9.gif)

第三步：实施挂钩类/方法，并追踪相应参数以及返回值。

![Image](https://image.3001.net/images/20200502/1588408937_5ead326969649.gif)

第四步：搜索堆中特定的类实例以及调用的方法。

![Image](https://image.3001.net/images/20200502/1588408937_5ead326969649.gif)

第五步：选择一个类，并针对所有的方法动态生成钩子模板。

![Image](https://image.3001.net/images/20200502/1588408983_5ead329712abd.gif)

第六步：检测已加载进内存的新增类。

![Image](https://image.3001.net/images/20200502/1588409014_5ead32b685a8f.gif)

第七步：动态注入Frida自定义脚本。

![Image](https://image.3001.net/images/20200502/1588409038_5ead32ce5540a.gif)

你可以选择在`custom_script`文件夹中添加自定义的`.js`文件，这些脚本将会自动加载进Web接口中并随时可以执行。

## Demo应用

[ _RootBeer
Sample_](https://play.google.com/store/apps/details?id=com.scottyab.rootbeer.sample)是一个能够演示RMS工作机制的样例App。RootBeer是一款root检测库，我打算将其作为一个样例应用来演示RMS，它可以作为客户端检测实例，其root检测逻辑的绕过可以在不需要服务器端验证的情况下实现。

## 项目地址

Runtime Mobile Security (RMS)：【[
_GitHub传送门_](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)】

 ***参考来源：[ _m0bilesecurity_](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

