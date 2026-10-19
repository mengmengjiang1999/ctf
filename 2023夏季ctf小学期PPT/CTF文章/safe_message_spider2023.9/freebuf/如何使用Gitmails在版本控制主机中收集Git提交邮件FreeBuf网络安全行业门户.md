![](https://image.3001.net/images/20230828/1693227116_64ec986cc393f206e6290.png!small)

## 关于Gitmails

Gitmails是一款能够在Git版本控制主机服务中收集Git提交电子邮件的信息收集工具，该工具可以帮助广大研究人员扫描和识别Git提交中包含的作者名称、电子邮件配置和版本控制主机服务是否存储了多个项目。

## 工具功能

当前版本的Gitmails功能如下：

> 1、向版本控制主机服务查询有关组织、团队、组、用户或单个存储库的信息；
>
> 2、如果不是在单一存储库模式下，则列出所有存储库（受身份验证限制）；
>
> 3、克隆存储库或查询版本控制主机服务以获取提交历史记录；
>
> 4、分析提交历史以确定唯一的作者，其中作者是由姓名和电子邮件来定义的；

通过上述操作，Gitmails可以收集特定目标提交历史记录中的所有电子邮件信息；

## 工具安装

### 源码获取

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令直接将该项目源码克隆至本地：

    
    
    git clone https://github.com/giovanifss/Gitmails.git

然后切换到项目目录中，使用pip3命令和requirements.txt文件安装该工具所需的依赖组件：

    
    
    cd Gitmails/
    
    pip3 install -r requirements.txt

其中的pygit2工具（其中一个依赖组件）则需要通过操作系统的包管理器进行手动安装。

### Docker使用

我们还可以使用该工具的Docker版本，操作命令如下：

    
    
    docker run -it giovanifss/gitmails --help

需要注意的是，如果你想要将结果写入到文件中，你还需要加载一个Docker卷宗：

    
    
    docker run -v /tmp/output:/opt -it giovanifss/gitmails -f /opt/result.txt

## 工具使用

首先，你必须选择一个操作方法：即收集组织电子邮件（-organization）、用户（-u或--username）或单个代码库（-r或--repository）。

接下来就需要设置目标了，你需要在执行下列代码后将目标以参数的形式传递给Gitmails：

    
    
    python3 gitmails.py -u some_username,
    
    python3 gitmails.py -o some_org
    
    python3 gitmails.py -r some_repo_url

注意，Gitlab用户名是大小写敏感的，请记住这一点。

有了这个基本配置，Gitmails将克隆指定目标的所有存储库（或克隆url中的存储库），并分析其提交历史。然后，它将打印用户或组织的高级信息，并最终在“fancy_grid”表中打印分析过程中发现的所有名称电子邮件部分。

## 工具参数选项

    
    
    --raw：以纯文本形式输出结果，以逗号分隔值；
    
    -f | --file：将结果存储到指定文件中，格式为CSV且无Header；
    
    --include-repositories：让Gitmails打印结果，其中包含电子邮件对应的代码库信息；
    
    -p | --path：指定克隆代码库的临时路径；
    
    -e | --exclude：忽略指定的代码库；
    
    --no-cleanup：不删除已克隆的代码库；
    
    --include-forks：在分析中引入Fork的代码库（仅适用于GitHub）；
    
    --include-users：收集目标组织中的公开成员信息（仅适用于GitHub）；
    
    --no-[gitlab|github|bitbucket]：不收集指定主机服务的相关信息；
    
    --run-plugins：在收集结果中执行插件分析；
    
    --api：尝试仅通过API收集信息，并且不克隆目标代码库；

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/giovanifss/Gitmails/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Gitmails** ：【[ _GitHub传送门_](https://github.com/giovanifss/gitmails)】

## 参考资料

> [ _https://github.com/giovanifss/Gitmails-> sh_](https://github.com/giovanifss/Gitmails-sh)

