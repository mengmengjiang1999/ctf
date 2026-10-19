## 1.1原理

在 **Windows 7** **，** **Windows Server 2008R2** **，** **Windows 8** 和
**Windows Server 2012** **上** ，RpcEptMapper和DnsCache（仅7 /
2008R2）服务的注册表项配置了弱权限。任何本地用户都可以创建一个Performance子项，然后利用 **Windows** **性能计数器**
在WMI服务的上下文中加载任意DLL

## 1.2影响版本

> Windows 7
>
> Windows Server 2008R2
>
> Windows 8
>
> Windows Server 2012

## 1.3提权步骤

1、下载提权工具Perfusion-master，地址为：<https://github.com/itm4n/Perfusion>；下载[调试工具visual studio
2019](https://github.com/itm4n/Perfusion%EF%BC%8C%E4%B8%8B%E8%BD%BD%E5%AE%8C%E6%88%90%E4%B9%8B%E5%90%8E%E4%BD%BF%E7%94%A8visual%20studio%202019)进行调试

![1614678258_603e08f21349c23303448.png!small?1614678241825](https://image.3001.net/images/20210302/1614678258_603e08f21349c23303448.png!small?1614678241825)

2、使用visual studio 2019工具打开Perfusion-master文件夹下的sln文件，如下图所示

![1614678268_603e08fccf97c35a44c87.png!small?1614678252518](https://image.3001.net/images/20210302/1614678268_603e08fccf97c35a44c87.png!small?1614678252518)

![1614678280_603e09082dbc471777daa.png!small](https://image.3001.net/images/20210302/1614678280_603e09082dbc471777daa.png!small)

3、选择Release / x64进行windows本地调试，如果提权系统为32位，就选择Release /
x86，选好之后点击“本地windo调试器”，如下图所示

![1614678307_603e092367432f6c1ad45.png!small?1614678290992](https://image.3001.net/images/20210302/1614678307_603e092367432f6c1ad45.png!small?1614678290992)

4、最终会在Perfusion-master生成x64文件夹，该文件夹下有“Perfusion.exe”提权程序，将该文件夹打包放到需要提权的windows主机上

![1614678329_603e09390c29c040c2aae.png!small?1614678313273](https://image.3001.net/images/20210302/1614678329_603e09390c29c040c2aae.png!small?1614678313273)

5、在命令行里面运行Perfusion.exe -c cmd –i进行提权，成功拿到system权限

![1614678374_603e0966f2bbc730a8745.png!small?1614678358543](https://image.3001.net/images/20210302/1614678374_603e0966f2bbc730a8745.png!small?1614678358543)

