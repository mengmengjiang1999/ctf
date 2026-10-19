![](https://image.3001.net/images/20200224/1582545875_5e53bbd334533.jpg!small)

##  DLLPasswordFilterImplant

**DLLPasswordFilterImplant是一个自定义的密码过滤器DLL，它可以帮助广大安全研究人员捕捉目标用户的凭证信息。域中的每一次密码修改事件都将会触发一次DLL注册操作，以便在活动目录中修改用户名和新密码值之前先将它们提取出来。**

如需了解更多关于Windows密码过滤器的内容，请参考微软的这篇【[官方文档](https://msdn.microsoft.com/en-us/library/windows/desktop/ms721882\(v=vs.85\).aspx)】。

###  工具下载

广大研究人员可以使用下列命令将该项目的源码克隆至本地：

    
    
    git clone https://github.com/GoSecure/DLLPasswordFilterImplant.git

###  工具安装

首先，针对目标操作系统架构创建DLL文件，如果是64位系统，则需要编译64位DLL，如果是32位系统，则需要编译32位DLL。将生成的DLL文件拷贝至Windows安装目录，默认路径为“\Windows\System32”。接下来，通过更新下列注册表键来注册密码过滤器：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa

如果Notification
Packages这个子键已经存在的话，将DLL的名称"DLLPasswordFilterImplant"添加到现有的数据值中。记住，不要覆盖现有的值。如果子键不存在的话，创建这个子键，然后将DLL的名称"DLLPasswordFilterImplant"
写入到数据值中。这里需要注意的是，当你在Notification Packages子键中添加DLL名称时，不要将.dll后缀加进去。

然后，配置加密凭证所需的公共密钥：

    
    
    KEY=key.pem
    
        # Generate an RSA key and dump its public key. Keep the private key around for decryption
    
        openssl genrsa -out $KEY 2048
    
        # Prepare the Windows registry key entry.
    
        echo 'Windows Registry Editor Version 5.00' > addKey.reg
    
        echo >> addKey.reg
    
        echo '[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa]' >> addKey.reg
    
        # If python2 does not exist, use `python` instead.
    
        echo "Key=hex:$(openssl rsa -in $KEY -pubout | sed -E '/^\-/d' | base64 -d | python2 -c 'import sys; print(",".join(["{:02x}".format(ord(b)) for b in sys.stdin.read()]))')" >> addKey.reg

接下来，你可以运行addKey.reg文件来将元公共密钥追加至注册表中。注意，由于数据填充机制的存在，使用非对称加密算法将会显著增加提取出的数据文件的大小。为了减少数据方面的开销，我们可能还需要进行一些改进。

下一步，我们需要[重启系统](https://msdn.microsoft.com/en-us/library/windows/desktop/ms721766\(v=vs.85\).aspx)。

完成之后，我们需要为DNS提取注册相应的键以及域名。进入到下列注册表项中：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa

创建一个名为“Domain”的字符串类型的子键，在这个子键中指定你域名的值，域名值必须以”.”开头，比如说“.yourdomain.com”。

##  数据解密

填充进去的加密数据使用的是OAEP，并且能够使用下列方法来进行数据解密：

    
    
    # Convert the stitched hex string to raw bytes.
    
        xxd -r -p exfiltrated.hex > raw.bin
    
        # Decrypt using the private key.
    
        openssl rsautl -decrypt -oaep -inkey $KEY -in raw.bin -out decrypted.txt

##  卸载过滤器

为了完整地从目标系统中移除配置的密码过滤器，我们首先需要通过更新下列注册表键来注销掉密码过滤器：

    
    
    HKEY_LOCAL_MACHINE SYSTEM\CurrentControlSet\Control\Lsa

在Notification Packages这个子键中，移除子键数据值中的DLL名称，但不要移除现有的其他值，完成之后重启系统。

在Windows的安装目录中（默认路径为“\Windows\System32”），找到密码过滤器DLL-"DLLPasswordFilterImplant.DLL"，然后删除该文件。

##  兼容性

密码过滤器目前兼容/支持在以下系统平台中运行：

> Windows 7 Hosts (x64)
>
> Windows 10 Hosts (x64)
>
> Windows Server 2008 DCs (x64)
>
> Windows Server 2012 DCs (x64)
>
> Windows Server 2016 DCs (x64)

##  调试工具

如果有需要的话，下面给出的工具也许可以帮助你调试生成好的DLL文件：

> Process Explorer：【[点我获取](https://docs.microsoft.com/en-> us/sysinternals/downloads/process-explorer)】
>
> Dependency Walker：【[点我获取](http://www.dependencywalker.com/)】

##  项目地址

>
> DLLPasswordFilterImplant：【[GitHub传送门](https://github.com/GoSecure/DLLPasswordFilterImplant)】

 ***
参考来源：[GoSecure](https://github.com/GoSecure/DLLPasswordFilterImplant)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

