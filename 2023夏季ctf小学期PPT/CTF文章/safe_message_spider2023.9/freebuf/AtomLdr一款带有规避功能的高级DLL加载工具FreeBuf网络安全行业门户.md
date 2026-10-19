![](https://image.3001.net/images/20230803/1691072429_64cbb7adbb8dec0ca7005.jpg!small)

## 关于AtomLdr

AtomLdr是一款带有规避功能的高级DLL加载工具，在该工具的帮助下，广大研究人员可以轻松地以隐蔽性极强的形式在目标设备上实现DLL加载。

## 功能介绍

> 1、独立的CRT库；
>
> 2、最后的DLL文件可以通过加载DLL（执行其入口点）或通过命令行执行导出的“Atom”函数来运行Payload；
>
> 3、DLL从\KnwonDlls目录解除钩子，而且没有RWX字段；
>
> 4、加密的Payload存储在资源字段，可以通过自定义代码进行检索；
>
> 5、使用AES256-CBC对Payload加密；
>
> 6、AES密钥和IV加密；
>
> 7、间接系统调用，使用了带有ROP小工具的[ _HellHall_](https://github.com/Maldev-> Academy/HellHall)；
>
> 8、使用APC调用实现Payload注入；
>
> 9、使用APC实现Payload执行；
>
> 10、使用了两种不同的CRC32字符串哈希算法实现API哈希；
>
> 11、整个工具代码提及非常小；

## 工作机制

![](https://image.3001.net/images/20230803/1691072447_64cbb7bf3ee5ebf7a7129.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/NUL0x4C/AtomLdr.git

## 工具使用

> 1、[
> _PayloadBuilder_](https://github.com/NUL0x4C/AtomLdr/tree/main/PayloadBuilder)需要使用指定的Payload进行编译和执行，它将输出一个PayloadConfig.pc文件，该文件包含加密的有Payload及其加密密钥和IV；
>
> 2、生成的PayloadConfig.pc文件接下来需要替换AtomLdr项目中的【[
> _PayloadConfig.pc_](https://github.com/NUL0x4C/AtomLdr/blob/main/AtomLdr/PayloadConfig.pc)】；
>
> 3、将AtomLdr项目编译为x64版本；
>
> 4、若要启用调试模式，请在【 _此处_】取消注释；

## 工具使用样例

### 样例一

执行AtomLdr.dll，运行rundll32.exe，运行[
_Havoc_](https://github.com/HavocFramework/Havoc)Payload，工具界面如下图所示：

![](https://image.3001.net/images/20230803/1691072474_64cbb7da5b8dfb894eedf.png!small)

AtomLdr.dll的导入地址表：

![](https://image.3001.net/images/20230803/1691072480_64cbb7e0c1445b885c0d2.png!small)

### 样例二-调试模式

运行PayloadBuilder.exe，加密demon[111].bin（一个Havoc Payload文件）：

![](https://image.3001.net/images/20230803/1691072488_64cbb7e854ba34703062d.png!small)

使用rundll32.exe来运行AtomLdr.dll：

![](https://image.3001.net/images/20230803/1691072494_64cbb7ee6f446022d67cd.png!small)

![](https://image.3001.net/images/20230803/1691072500_64cbb7f464fc8edcdb6e8.png!small)

Payload执行后，Havoc获取屏幕截图：

![](https://image.3001.net/images/20230803/1691072506_64cbb7faec543c1f819c6.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/NUL0x4C/AtomLdr/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **AtomLdr** ：【[ _GitHub传送门_](https://github.com/NUL0x4C/AtomLdr)】

## 参考资料

> [
> _https://github.com/NUL0x4C/AtomLdr/blob/main/maldevacademy.com_](https://github.com/NUL0x4C/AtomLdr/blob/main/maldevacademy.com)
>
> [ _https://github.com/bitcoin-core/ctaes_](https://github.com/bitcoin-> core/ctaes)
>
> [ _https://github.com/Maldev-Academy/HellHall_](https://github.com/Maldev-> Academy/HellHall)
>
> [
> _https://www.x86matthew.com/view_post?id=writeprocessmemory_apc_](https://www.x86matthew.com/view_post?id=writeprocessmemory_apc)
>
> [ _https://github.com/vxunderground/VX-> API_](https://github.com/vxunderground/VX-API)
>
> [
> _https://github.com/HavocFramework/Havoc_](https://github.com/HavocFramework/Havoc)

