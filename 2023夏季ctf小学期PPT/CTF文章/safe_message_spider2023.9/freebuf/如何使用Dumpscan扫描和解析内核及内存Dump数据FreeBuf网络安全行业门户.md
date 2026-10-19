![](https://image.3001.net/images/20220808/1659959982_62f0faae23dcb54965aec.png!small)

## 关于Dumpscan

Dumpscan是一款功能强大的命令行工具，该工具可以帮助广大研究人员从内核以及Windows Minidump格式提取和导出敏感数据。

## 功能介绍

> 1、支持x509公钥和私钥（PKCS #8/PKCS #1）解析；
>
> 2、支持[ _SymCrypt_](https://github.com/microsoft/SymCrypt)解析；
>
> 3、支持提取和解析环境变量；
>
> 4、支持通过命令行参数控制工具运行；

## 工具组件

> [volatility3](https://github.com/volatilityfoundation/volatility3)
>
> [construct](https://github.com/construct/construct)
>
> [yara-python](https://github.com/VirusTotal/yara-python)
>
> [typer](https://github.com/tiangolo/typer)
>
> [rich](https://github.com/Textualize/rich)
>
> [rich_click](https://github.com/ewels/rich-click)

## 工具安装

我们推荐广大研究人员通过[ _pipx_](https://github.com/pypa/pipx)来安装Dumpscan：

    
    
    pipx install dumpscan
    
    pipx inject dumpscan git+https://github.com/volatilityfoundation/volatility3#39e812a

## 工具使用

    
    
    Usage: dumpscan [OPTIONS] COMMAND [ARGS]...
    
     
    
     Scan memory dumps for secrets and keys
    
     
    
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                  │
    
    │  --help         显示帮助信息和退出                                                      │
    
    │                                                                                                  │
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
    
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                  │
    
    │  kernel       使用volatility扫描内核dump                                                    │
    
    │  minidump   扫描用户模式minidump                                                            │
    
    │                                                                                                  │
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯

针对那些能够提取证书的子命令，我们可以使用“--output/-o <dir>”选项来指定将扫描到的证书提取到指定目录。

### 内核模式

该工具实现的内核分析功能是通过Volatility3实现的，“cmdline”、“envar”和“pslist”命令都将直接调用Volatility3插件，而“symcrypt”和“x509”都是自定义插件：

    
    
    Usage: dumpscan kernel [OPTIONS] COMMAND [ARGS]...
    
     
    
     Scan kernel dump using volatility
    
     
    
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                  
    
    │  --help         显示帮助信息和退出                                                      
    
    │                                                                                                  
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
    
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                  
    
    │  cmdline    枚举进程命令行信息 (仅Windows支持)                                   
    
    │  envar      枚举进程环境变量 (仅Windows支持)                                
    
    │  pslist       枚举所有进程和相应的命令行参数                              
    
    │  symcrypt   扫描内核模式dump中的SymCrypt对象                                        
    
    │  x509       扫描内核模式dump中的x509证书                                       
    
    │                                                                                                  
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯

### Minidump模式

该工具还支持Windows Minidump格式，但该功能只在Windows 10+的64位进程上进行过测试，32位进程可能还需要做其他处理。

    
    
    Usage: dumpscan minidump [OPTIONS] COMMAND [ARGS]...
    
     
    
     Scan a user-mode minidump
    
     
    
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                
    
    │  --help   显示帮助信息和退出
    
    │
    
    │                                                                                              
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
    
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
    
    │                                                                                                  
    
    │  cmdline    导出命令行字符串
    
    │
    
    │  envar      导出环境变量                                        
    
    │  symcrypt   扫描minidump中的symcrypt对象                                                
    
    │  x509      扫描 minidump中的x509对象                                                    
    
    │                                                                                               
    
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/daddycocoaman/dumpscan/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Dumpscan** ：【[ _GitHub传送门_](https://github.com/daddycocoaman/dumpscan)】

## 参考资料

> [
> _https://github.com/volatilityfoundation/volatility3_](https://github.com/volatilityfoundation/volatility3)
>
> [
> _https://github.com/microsoft/SymCrypt_](https://github.com/microsoft/SymCrypt)
>
> [ _https://github.com/pypa/pipx_](https://github.com/pypa/pipx)

