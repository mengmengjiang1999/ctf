![](https://image.3001.net/images/20230522/1684743798_646b267658f57227c87bb.png!small)

## 关于Nuclear Pond

Nuclear Pond是一个功能强大的网络扫描工具，该工具基于[
_Nuclei_](https://github.com/projectdiscovery/nuclei)实现其功能，可以利用Nuclei执行速度快、扩展性强的互联网范围大规模扫描任务。

Nuclear Pond利用[ _AWS
Lambda_](https://aws.amazon.com/lambda/)作为后端并行调用Nuclei扫描，能够将扫描结果以JSON形式存储在S3中以使用[
_AWS_ __ _Athena_](https://aws.amazon.com/athena/)进行查询，这也是在云端执行扫描任务成本最低的方式之一。

## 功能介绍

> 1、支持将结果输出到终端窗口、JSON或S3；
>
> 2、在任意所需数量的批处理中指定线程和并行调用；
>
> 3、支持指定任意Nuclei参数，与本地使用相同；
>
> 4、指定单个目标主机，或通过文件列表输入目标主机；
>
> 5、运行HTTP服务器并从API执行扫描；
>
> 6、运行HTTP服务器并获取扫描状态；
>
> 7、通过Athena扫描S3并查询结果；
>
> 8、指定一个自定义Nuclei并报告配置；

## 工具安装

如需安装Nuclear Pond，你需要先配置后端[
_terraform模块_](https://github.com/DevSecOpsDocs/terraform-nuclear-pond)。我们可以通过运行命令“terraform applay”或利用[
_terragrunt_](https://terragrunt.gruntwork.io/)来完成配置。

接下来，广大研究人员可以直接运行下列命令下载并安装最新版本的Nuclear Pond：

    
    
    $ go install github.com/DevSecOpsDocs/nuclearpond@latest

## 环境变量

我们可以通过参数选项或环境变量来传递后端控制参数，可以使用-f或--function-name来指定Lambda函数，或使用-r或--region来指定区域。下面给出的是我们可以使用的环境变量：

> AWS_LAMBDA_FUNCTION_NAME：扫描需要执行的Lambda函数名称；
>
> AWS_REGION：资源部署的区域；
>
> NUCLEARPOND_API_KEY：认证所需的API密钥；
>
> AWS_DYNAMODB_TABLE：存储API扫描结果的dynamodb表；

## 命令行选项

我们所需的针对目标的主要参数为-t或-l，-a为nuclei参数，-o用于指定输出。当指定Nuclei参数时，需要以Base64编码字符串来传递，例如“-a
$(echo -ne "-t dns" | base64)”。

### 命令

下面给出的是可以在Nuclear Pond中执行的子命令：

> run：执行Nuclei扫描；
>
> service：使用基础API执行Nuclei扫描；

## 工具运行

    
    
    $ nuclearpond run -h
    
    Executes nuclei tasks in parallel by invoking lambda asynchronously
    
     
    
    Usage:
    
      nuclearpond run [flags]
    
     
    
    Flags:
    
      -a, --args string            以Base64编码字符串形式传递Nuclei参数
    
      -b, --batch-size int         每次执行的批处理目标数量，默认为1
    
      -f, --function-name string   AWS Lambda函数名称
    
      -h, --help                   查看工具帮助信息
    
      -o, --output string         存储Nuclei结果的输出类型，可选为S3、cmd和JSON，默认为cmd
    
      -r, --region string          运行Nuclei的AWS实例区域
    
      -s, --silent                 开启命令行输出静默模式
    
      -t, --target string           指定单个目标
    
      -l, --targets string          设置目标列表文件路径
    
      -c, --threads int           运行Lambda函数的线程数量，默认为1

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/DevSecOpsDocs/nuclearpond/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Nuclear Pond** ：【[
_GitHub传送门_](https://github.com/DevSecOpsDocs/nuclearpond)】

## 参考资料

> [
> _https://github.com/projectdiscovery/nuclei_](https://github.com/projectdiscovery/nuclei)
>
> [ _https://devsecopsdocs.com/blog/nuclear-> pond/_](https://devsecopsdocs.com/blog/nuclear-pond/)
>
> [ _https://aws.amazon.com/athena/_](https://aws.amazon.com/athena/)

