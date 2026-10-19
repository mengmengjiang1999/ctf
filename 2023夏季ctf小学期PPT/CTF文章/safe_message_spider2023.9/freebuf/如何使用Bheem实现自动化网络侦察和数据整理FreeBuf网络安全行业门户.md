![](https://image.3001.net/images/20210411/1618143752_6072ea087bb32eed9f68f.jpg!small)

## Bheem项目

Bheem项目是一套小型Bash脚本的合集，它能够以迭代方式运行并执行各种工具，然后以有组织的方式重新处理和存储网络侦察过程中的数据输出。这个项目最早是为个人使用的侦察自动化任务而创建的，并且从未打算开源。但考虑到社区的需求，Bheem项目现在正式公开给大家。

广大研究人员可以根据需要来对其进行修改，Bheem项目其实只是由现有命令和工具组成的，所有的脚本均采用Bash编写，可以帮助广大研究人员实现自动化网络侦察任务。

 **Bheem项目支持基于范围的网络侦察方法，当前的Bheem项目支持执行下列任务：**

> 小范围（URL范围）：执行有限的侦察扫描任务，目标为少量范围内的URL。
>
> 中范围（*.target.com范围）：执行网络侦察任务并枚举更多资产，提供更多的攻击选项。
>
> 大范围（定义范围内的一切实体）：执行所有可能的网络侦察向量，包含从子域名枚举到模糊测试。

像端口扫描这样的一些特性在当前版本中可能暂不支持，还有一些新发布的工具可能也无法及时包含进去。我们的开发人员也一直在努力升级该工具，社区的广大用户也可以贡献自己的代码。

## 依赖环境

确保已经在系统中安装并配置好了最新版本的Go环境，并确保路径已正确设置。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/harsh-bothra/Bheem.git

然后运行下列脚本来安装工具所需的依赖组件：

    
    
    sh install.sh

项目中的arsenal目录包含了一系列脚本，可以帮助Bheem实现自动化任务，因此我们需要给这个目录中的脚本赋予可执行权限。

接下来，切换到~/arsenal目录中，运行下列命令来查看Bheem支持的所有选项：

    
    
    ./Bheem.sh -h

如果你想在vps上针对大量目标执行网络侦察任务的话，可以执行下列命令：

    
    
    screen -S <screen_name> ~/arsenal/Bheem.sh -h

此时，Bheem将会运行。即使SSH链接断开或你关闭了本地设备，Bheem的任务也仍会保持运行。

## Docker安装

当然了，如果你不想自己去配置各种依赖环境的话，你也可以在Docker环境中使用Bheem。

我们已经将Bheem与Hacktools（https://github.com/xavier9909/IIEC-RISE-DOCKER-1.0-HackTools）进行了整合：

    
    
    docker pull xavier9909/hacktools_bheem
    
    docker run -it xavier9909/hacktools_bheem
    
    cd arsenal && ./Bheem.sh
    
    or just simply type bheem from any directory

接下来，我们就可以直接在容器终端窗口中进行操作了。

## 工具使用样例

小范围网络侦察扫描任务：

    
    
    Bheem -t targetfile -S

中范围网络侦察扫描任务：

    
    
    Bheem -t targetfile -M

大范围网络侦察扫描任务：

    
    
    Bheem -t targetfile -L

其中，targetfile包含了需要执行网络侦察任务的目标域名列表，比如说targettest.com。

### 排除超范围外的子域名

Bheem提供了一个参数来移除扫描任务中超出范围的子域名。我们可以使用“-e”参数，并使用逗号分隔子域名：

    
    
    Bheem -t targetfile -S -e sub.ex.com,sub1.ex.com

## 注意事项

如果你不想使用特定模块，可以直接注释掉相关代码；

如需修改XSS盲注Payload，请修改/Bheem/arsenal/autoxss.sh文件。你可以访问XSS
Hunter来获取你的XSS盲注Payload。

## Bheem使用的工具

    
    
    Nuclei
    
    HTTPX
    
    GF & GF-Patterns
    
    Secret Finder
    
    Heartbleed Oneliner
    
    AMASS
    
    Subfinder
    
    Assetfinder
    
    JSScan
    
    FavFreak
    
    Waybackurls
    
    Gau
    
    Parallel
    
    asnip
    
    dirsearch
    
    gowitness
    
    subjack
    
    CORS Scanner
    
    git-hound
    
    Shuffledns
    
    Massdns

## 项目地址

Bheem：https://github.com/harsh-bothra/Bheem

