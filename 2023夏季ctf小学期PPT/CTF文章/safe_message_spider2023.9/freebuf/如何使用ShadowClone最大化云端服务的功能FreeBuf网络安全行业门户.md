![](https://image.3001.net/images/20220601/1654081245_629746dd6ab48f4db70d8.jpeg!small)

## 关于ShadowClone

ShadowClone是一个云端服务整合工具，在该工具的帮助下，广大研究人员可以轻松使用多种云服务提供的serverless功能来长时间运行各种任务，同时也支持动态分配运行时间，并在几秒钟之内拿到自己想要的结果。但在ShadowClone出现之前，完成这些任务可能需要好几个小时的时间。

ShadowClone可以帮助我们充分利用云服务商提供的Free Tier，并极大程度地增强命令行工具的功能。

## 工作机制

ShadowClone的开发人员创建了一个容器，并将其注册为AWS/GCP/Azure中函数的运行时。在计算机上执行ShadowClone时，该容器的实例将自动激活，并且仅在其执行期间处于活动状态。而要激活的实例数量在运行时将根据提供的输入文件大小和拆分因子来动态决定。接下来，工具将对输入分块，并在所有实例之间平均分布，以实现并行执行。比如说，如果我们的输入文件有10000行，并且将分割因子设置为100行，那么它将被分割为100个块，每个块100行，同时100个实例将并行运行。

## 工具要求

> AWS/GCP/Azure/IBM云服务账号
>
> Docker
>
> Python 3.8+

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/fyoorer/ShadowClone.git

## 工具配置

### 云端配置

1、登录你的AWS账号，获取API凭证；

2、在AWS控制台进入IAM，创建下列策略：

    
    
    {
    
        "Version": "2012-10-17",
    
        "Statement": [
    
            {
    
                "Sid": "VisualEditor0",
    
                "Effect": "Allow",
    
                "Action": [
    
                    "s3:*",
    
                    "lambda:*",
    
                    "ec2:*",
    
                    "ecr:*",
    
                    "sts:GetCallerIdentity"
    
                ],
    
                "Resource": "*"
    
            }
    
        ]
    
    }

3、使用“Lambda”用例创建一个新的角色，并赋予上述权限策略；

4、进入S3，在同一空间创建两个Bucket，用于执行Lambda；

### 本地配置

1、本地设备上确保安装并配置好了Docker；

2、运行下列命令克隆代码库，并安装好Python依赖：

    
    
    git clone https://github.com/fyoorer/ShadowClone.git
    
    cd ShadowClone
    
    python -m venv env
    
    source env/bin/activate
    
    pip install -r requirements.txt

3、验证lithops命令行工具是否可用：

    
    
    ⚡ lithops test
    
    2022-01-18 08:08:45,832 [INFO] lithops.config -- Lithops v2.5.8
    
    2022-01-18 08:08:45,833 [INFO] lithops.storage.backends.localhost.localhost -- Localhost storage client created
    
    2022-01-18 08:08:45,833 [INFO] lithops.localhost.localhost -- Localhost compute client created
    
    2022-01-18 08:08:45,833 [INFO] lithops.invokers -- ExecutorID b9419a-0 | JobID A000 - Selected Runtime: python
    
    2022-01-18 08:08:45,833 [INFO] lithops.invokers -- Runtime python is not yet installed
    
    2022-01-18 08:08:45,833 [INFO] lithops.localhost.localhost -- Extracting preinstalled Python modules from python
    
    2022-01-18 08:08:46,110 [INFO] lithops.invokers -- ExecutorID b9419a-0 | JobID A000 - Starting function invocation: hello() - Total: 1 activations
    
    2022-01-18 08:08:46,111 [INFO] lithops.invokers -- ExecutorID b9419a-0 | JobID A000 - View execution logs at /tmp/lithops/logs/b9419a-0-A000.log
    
    2022-01-18 08:08:46,111 [INFO] lithops.wait -- ExecutorID b9419a-0 - Getting results from functions
    
      100%|████████████████████████████████████████████████████████████| 1/1
    
    2022-01-18 08:08:48,125 [INFO] lithops.executors -- ExecutorID b9419a-0 - Cleaning temporary data
    
    Hello fyoorer! Lithops is working as expected :)

### 构建&注册镜像

    
    
    lithops runtime build sc-runtime -f Dockerfile
    
    lithops runtime create sc-runtime --memory 512 --timeout 300
    
    lithops runtime list

## 工具使用帮助

    
    
    ⚡ python shadowclone.py -h
    
    usage: shadowclone.py [-h] -i INPUT [-s SPLITNUM] [-o OUTPUT] -c COMMAND
    
    optional arguments:
    
      -h, --help                              显示帮助信息和退出
    
      -i INPUT, --input INPUT                 输入参数 
    
      -s SPLITNUM, --split SPLITNUM         分割因子，文件块每块多少汗N
    
      -o OUTPUT, --output OUTPUT           输出数据
    
      -c COMMAND, --command COMMAND  需要执行的命令

## 工具使用演示

### 使用一个43MB的文件执行DNS爆破（34秒）

 **视频地址：**[
_https://asciinema.org/a/lISleX6xohoiEx8N7PozjySEq_](https://asciinema.org/a/lISleX6xohoiEx8N7PozjySEq)

### 对94K子域名与您httpx（1分钟内）

 **视频地址：**[
_https://asciinema.org/a/GSwuqyd9X4JfXGlqQEFiDdefi_](https://asciinema.org/a/GSwuqyd9X4JfXGlqQEFiDdefi)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/fyoorer/ShadowClone/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **ShadowClone：** 【[ _GitHub传送门_](https://github.com/fyoorer/ShadowClone)】

## 参考资料

> [ _https://lithops-cloud.github.io/docs/index.html_](https://lithops-> cloud.github.io/docs/index.html)
>
> [ _https://cloud.google.com/free/docs/gcp-free-tier/#cloud-> functions_](https://cloud.google.com/free/docs/gcp-free-tier/#cloud-> functions)
>
> [ _https://aws.amazon.com/free/_](https://aws.amazon.com/free/)
>
> [ _https://azure.microsoft.com/en-ca/free/_](https://azure.microsoft.com/en-> ca/free/)
>
> [ _https://github.com/pry0cc/axiom_](https://github.com/pry0cc/axiom)
>
> [
> _https://github.com/FleexSecurity/fleex_](https://github.com/FleexSecurity/fleex)
>
> [
> _https://github.com/0xdevalias/gopherblazer_](https://github.com/0xdevalias/gopherblazer)

