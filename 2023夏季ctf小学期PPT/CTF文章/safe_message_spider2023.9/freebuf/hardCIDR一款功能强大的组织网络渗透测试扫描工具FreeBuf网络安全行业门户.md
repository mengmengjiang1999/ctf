![](https://image.3001.net/images/20230605/1685971095_647de0970ad6b6c17944d.jpg!small)

## 关于hardCIDR

hardCIDR是一个功能强大的Linux
Bash脚本，但也可以在macOS操作系统中运行。该工具可以帮助广大研究人员在渗透测试的情报收集阶段扫描和发现目标组织所拥有的网块或IP地址范围（使用CIDR表示法）。这些信息由五个地区性互联网注册管理机构（RIR）维护：

> ARIN (北美)
>
> RIPE (欧洲/亚洲/中东)
>
> APNIC (亚洲/太平洋地区)
>
> LACNIC (拉丁美洲)
>
> AfriNIC (非洲)

除了网块和IP地址之外，自治系统编号（ASN）也是很多研究人员所感兴趣的。ASN被用作边界网关协议（BGP）的一部分，用于唯一识别互联网上的每个网络。由于网络的规模或对等服务提供商的冗余服务路径，目标组织可能有自己的ASN。这些ASN将显示组织拥有的其他网块。

## 工具要求

> ipcalc（用于RIPE、APNIC、LACNIC和AfriNIC查询），工具脚本会自动安装；

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/trustedsec/hardcidr.git

### 使用Docker运行

    
    
    docker build -t hardcidr .

构建hardCIDR镜像：

    
    
    docker run -v $(pwd):/tmp -it hardcidr

运行容器之后，输出结果将保存在当前目录中。

## 工具使用

需要注意的是，该脚本在不提供任何参数选项时，将会查询ARIN和一个BGP路由服务器池，其中的路由服务器是脚本在运行过程中随机选择的。

使用-h选项可以查看工具帮助菜单：

![](https://image.3001.net/images/20230605/1685971145_647de0c926f105153aa4e.png!small)

在提示下，输入组织名称、电子邮件域以及是否要给电子邮件添加国家/地区码，如果设置为Y，则系统将提示我们是在域名之前还是在TLD之后附加国家码。随后，工具将在/tmp/中为输出文件创建一个目录，如果该目录存在，则提示是否需要覆盖写入。如果设置为N，则会在目录名称后添加一个当前的时间戳以作区分：

![](https://image.3001.net/images/20230605/1685971154_647de0d206a53a56b2ef9.png!small)

该脚本查询每个RIR以及BGP路由服务器，并随时提示是否找到了相关记录。执行完成后，工具将生成三份文件：

![](https://image.3001.net/images/20230605/1685971163_647de0db8ba4bd2b06ce9.png!small)

任何时候取消脚本都将删除任何临时工作文件和为生成的输出文件创建的目录：

![](https://image.3001.net/images/20230605/1685971173_647de0e538b6cc34e0145.png!small)

需要注意的是，由于某些组织名称的相似性，可能会得到与目标无关的结果。CSV文件将提供相关的URL，以便在必要时进行进一步验证。目标组织的员工也有可能使用他们的公司电子邮件地址注册自己的域名，这些也将在结果中找到。

## 许可证协议

本项目的开发与发布遵循[ _BSD_ _-2-_
_Clause_](https://github.com/trustedsec/hardcidr/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **hardCIDR** ：【[ _GitHub传送门_](https://github.com/trustedsec/hardcidr)】

## 参考资料

> [ _https://www.trustedsec.com/blog/classy-inter-domain-routing-> enumeration/_](https://www.trustedsec.com/blog/classy-inter-domain-routing-> enumeration/)

