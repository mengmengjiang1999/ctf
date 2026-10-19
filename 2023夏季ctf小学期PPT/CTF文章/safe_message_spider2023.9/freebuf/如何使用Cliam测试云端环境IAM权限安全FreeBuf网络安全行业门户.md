![](https://image.3001.net/images/20220605/1654428144_629c91f00e0ba62e6fb0d.jpeg!small)

## 关于Cliam

Cliam是一款针对云端安全的测试工具，在该工具的帮助下，广大研究人员可以轻松枚举目标云端环境的IAM权限。当前版本的Cliam支持下列云端环境：AWS、Azure、GCP和Oracle。

Cliam同时也是一个云端权限识别工具，该工具是一个命令行接口工具，不仅可以枚举目标云环境的特定权限，而且还可以检测云服务提供商的服务或资源子集。

## 工具安装

广大研究人员可以直接访问项目的【[
_Releases页面_](https://github.com/securisec/cliam/releases)】下载最新版本的Cliam（开发版，非稳定版）。

或者，也可以使用下列命令将该项目源码克隆至本地，然后切换到项目的“cli”目录，并构建代码：

    
    
    git clone https://github.com/securisec/cliam.git
    
    cd cliam
    
    make dev

## 工具使用

Cliam使用了从envars服务获取到的凭证或直接通过命令行接口传递参数来完成其操作。我们建议广大用户在使用该工具时，提供指定的枚举参数：

    
    
    ❯❯ cliam --help
    
    Cloud Enumerate is a tool to enumerate cloud credentials for their permissions.
    
     
    
    Usage:
    
      cliam [command]
    
     
    
    Available Commands:
    
      aws         枚举目标AWS凭证的权限
    
      completion   生成自动化Shell脚本
    
      gcp         枚举目标GCP服务账号的权限
    
      help         查看工具帮助信息
    
     
    
    Flags:
    
      -h, --help   查看工具帮助信息
    
     
    
    Additional help topics:
    
      cliam azure      枚举目标Azure凭证的权限
    
     
    
    Use "cliam [command] --help" for more information about a command.

### AWS

使用AWS Rest
API和传递给工具的凭证信息来发送签名请求。工具支持从AWS配置文件、选项参数或类似AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY和
AWS_SESSION_TOKEN这样的默认AWS环境变量来获取凭证：

    
    
    cliam aws --help
    
    Enumerate AWS credentials for their permissions.
    
     
    
    Usage:
    
      cliam aws [command]
    
     
    
    Available Commands:
    
      common      枚举常见AWS资源的权限
    
      compute      枚举常见计算AWS资源的权限
    
      databases    枚举常见AWS数据库资源的权限
    
      enumerate    枚举指定AWS资源的权限
    
      serverless    枚举常见无服务AWS资源的权限
    
      storage      枚举常见存储AWS资源的权限
    
     
    
    Flags:
    
          --access-key-id string       AWS访问密钥ID
    
      -h, --help                       AWS帮助信息
    
          --profile string               AWS账号信息
    
          --region string              AWS Region (默认为"us-east-1")
    
          --secret-access-key string   AWS敏感信息访问密钥
    
          --session-token string       AWS会话令牌
    
     
    
    Global Flags:
    
          --max-threads int       使用的最大线程数量 (默认为5)
    
          --request-timeout int    每次请求的间隔秒数 (默认为10)

## 工具使用样例

使用一个AWS账号爆破所有无服务资源：

    
    
    ❯❯ cliam aws serverless --profile=my-profile

使用获取到的临时会话令牌来检查所有的EC2权限：

    
    
    ❯❯ cliam aws enumerate ec2 --session-json=creds.json
    
     
    
    Where creds.json has
    
    {
    
      "Type" : "AWS-HMAC",
    
      "AccessKeyId" : "ASIA...",
    
      "SecretAccessKey" : "...",
    
      "Token" : "...",
    
    }

枚举S3、IAM和EC2权限：

    
    
    ❯❯ cliam aws enumerate s3 iam ec2

### 调试

Cliam支持使用下列两个环境变量来显示调试输出：

> DEBUG=true（显示请求的状态码）
>
> VERBOSE=true（显示请求的Body信息）

## 工具运行截图

![](https://image.3001.net/images/20220605/1654428234_629c924a1b7087ae6c627.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/securisec/cliam/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Cliam：** 【[ _GitHub传送门_](https://github.com/securisec/cliam)】

