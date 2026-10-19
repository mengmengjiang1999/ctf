![](https://image.3001.net/images/20210719/1626694796_60f5648ca2de5af656ca3.jpg!small)

## 关于BlobHunter

BlobHunter是一款针对Azure的安全扫描工具，BlobHunter目前是一个开源项目，可以帮助广大研究人员扫描Azure
Blob存储账号中的公开Blob或其他泄露数据。

BlobHunter可帮助广大研究人员识别Azure blob存储容器，并扫描出Bolb存储中对任何具有网络访问权的用户公开可用的文件。

该工具将通过识别存储敏感数据的配置不当的容器来帮助降低存储的安全风险，这对于较大规模的Azure
Blob存储来说尤其有用，因为这些容器中可能会存在大量的账号，并增加扫描或跟踪的难度。

扫描完成之后，BlobHunter将生成一个包含丰富结果的CSV文件，并提供扫描环境中每个公开/开放容器的相关详细信息。

## 工具要求

  * Python 3.5+
  * Azure命令行接口
  * [ _requirements.txt_](https://github.com/cyberark/BlobHunter/blob/main/requirements.txt)中枚举的软件包
  * 拥有下列[ _内置权限_](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)之一的Azure用户： _Owner_、 _Contributor_、 _Storage Account Contributor_
  * 或者，拥有能够执行下列Azure操作的Azure用户角色：

    
    
    Microsoft.Resources/subscriptions/read
    
    Microsoft.Resources/subscriptions/resourceGroups/read
    
    Microsoft.Storage/storageAccounts/read
    
    Microsoft.Storage/storageAccounts/listkeys/action
    
    Microsoft.Storage/storageAccounts/blobServices/containers/read
    
    Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read

## 项目构建

以Ubuntu系统为例，我们可以使用下列命令完成BlobHunter的安装和配置：

    
    
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

接下来，安装依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

我们只需要运行下列命令，即可使用BlobHunter：

    
    
    python3 BlobHunter.py

如果你没有在Azure命令行接口中登录的话，此时将会弹出一个浏览器窗口，并提醒你输入Azure用户的凭证信息。

## 工具运行演示

GIF动画：【[
_点我观看_](https://github.com/cyberark/BlobHunter/blob/assets/BlobHunterDemo.gif)】

## 项目地址

BlobHunter：【[ _GitHub传送门_](https://github.com/cyberark/BlobHunter)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/cyberark/BlobHunter/blob/main/LICENSE)开源许可证协议。

## 参考资料

[ _https://www.cyberark.com/resources/threat-research-blog/hunting-azure-blobs-exposes-millions-of-sensitive-files_](https://www.cyberark.com/resources/threat-research-blog/hunting-azure-blobs-exposes-millions-of-sensitive-files)

[ _https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles_](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)

