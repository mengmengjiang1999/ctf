![](https://image.3001.net/images/20191111/1573482316_5dc96f4cc3092.png!small)

##  GCPBucketBrute

 **GCPBucketBrute是一款能够枚举Google Storage
Bucket的强大脚本，该脚本能够帮助你识别目标Bucket的访问权限，并判断是否能够在目标上实现提权。**

> 1、该脚本（可选）能够接受GCP用户/服务账号凭证以及关键词。
>
> 2、接下来，该脚本会根据传入的关键词生成一份置换组合列表，脚本会使用该列表来扫描现有的Google Storage Bucket。
>
>
> 3、即使提供了访问凭证，大部分的枚举仍然会以非认证状态执行，一旦非认证枚举状态扫描到了任何Bucket，该脚本都会尝试使用TestIamPermissions
> API以及提供的访问凭证来枚举Bucket权限。
>
> 4、但是无论是否提供了访问凭证，该脚本都会尝试使用TestIamPermissions
> API来枚举Bucket权限。这也就意味着，如果你没有输入访问凭证，你将只能看到非认证用户所拥有的权限，但是当你输入了凭证之后，你将会看到认证用户拥有的权限，方便我们进行权限对比。

##  工具简述

> 1、提供一个关键词，该脚本便会根据该关键词生成一套置换组合列表，然后根据列表进行Google Storage Bucket枚举。
>
> 2、接下来，输出所有扫描到的Bucket。
>
> 3、然后，输出目标Bucket的相关访问权限。
>
> 4、最后，脚本会检查这些权限，并尝试进行权限提升（storage.buckets.setIamPolicy），并输出结果。

##  工具要求

> Linux/OS X：Windows下只能进行非认证用户权限扫描，因为脚本在使用subprocess模块扫描时会出现问题。
>
> Python3
>
> Pip3

##  工具安装

> git clone <https://github.com/RhinoSecurityLabs/GCPBucketBrute.git>
>
> cd GCPBucketBrute/
>
> pip3 install -r requirements.txt or python3 -m pip install -r
> requirements.txt

##  工具使用

首先，判断需要枚举的认证类型，如果我们使用的是一个服务账号，则需要通过“-f/--service-account-credential-file-path”参数来以文件形式提供私钥。如果使用的是一个用户账号，则不需要提供任何的认证参数。运行后工具将提示你输入用户账号的访问令牌以访问GCP
API。如果你想以非认证状态进行完整扫描的话，需要使用“-u/--unauthenticated”参数。

以非认证状态进行完整扫描，使用关键词“test”扫描Bucket：

    
    
    python3 gcpbucketbrute.py -k test -u

以认证服务账号和关键词“test”扫描Bucket，将结果保存到out.txt并输出到当前目录：

    
    
    python3 gcpbucketbrute.py -k test -f ../sa-priv-key.pem -o ./out.txt

使用关键词“test”扫描Bucket，使用用户账号令牌，运行10个子进程：

    
    
    python3 gcpbucketbrute.py -k test -s 10

###  可用参数

    
    
    -k/--keyword

该参数可以指定用于生成置换组合列表的关键词。

    
    
    --check

该参数可以接收一个字符串，并针对特定Bucket进行权限检测。

    
    
    --check-list

该参数可以检测文件列表中Bucket的权限，txt文件中每一个Bucket占一行。

    
    
    -s/--subprocesses

该参数用于指定Bucket枚举过程中要使用的子进程数量，默认为5。

    
    
    -f/--service-account-credential-file-path

该参数指定了GCP服务账号的私钥文件的路径，该参数为可选项。

    
    
    -u/--unauthenticated

该参数可用于强制进行非认证枚举。

    
    
    -o/--out-file

该参数允许我们指定输出文件的路径，如果目标路径文件不存在，则会自动创建一个新文件，如果目标路径文件存在，则会将输出结果追加至文件结尾。

##  项目地址

>
> GCPBucketBrute：【[GitHub传送门](https://github.com/RhinoSecurityLabs/GCPBucketBrute)】

##  参考资料

> 1、<https://google-auth.readthedocs.io/en/latest/user-guide.html#service-> account-private-key-files>
>
> 2、<https://google-auth.readthedocs.io/en/latest/user-guide.html#user-> credentials>

***参考来源：[RhinoSecurityLabs](https://github.com/RhinoSecurityLabs/GCPBucketBrute)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

