![](https://image.3001.net/images/20210719/1626705461_60f58e35e72a24a3d824b.png!small)

## 关于S3 Account Search

S3 Account Search可以帮助广大研究查找目标S3 Bucket属于哪一个账号ID。为了实现这个功能，我们需要拥有至少下列权限之一：

> 从Bucket下载一个已知文件的权限（s3:getObject）；
>
> 枚举Bucket内容列表的权限（s3:ListBucket）；

除此之外，你还需要一个角色，能够包含上述之一权限。

## 工具安装

我们可以通过pypi来安装S3 Account Search工具包，比如说，我们可以使用下列其中一个命令来完成安装，这里推荐使用pipx：

    
    
    pipx install s3-account-search
    
    
    pip install s3-account-search

## 工具使用样例

 **# 使用一个bucket进行查询**

    
    
    s3-account-search arn:aws:iam::123456789012:role/s3_read s3://my-bucket

 **# 使用一个对象进行查询**

    
    
    s3-account-search arn:aws:iam::123456789012:role/s3_read s3://my-bucket/path/to/object.ext

 **# Y还可以去掉s3://**

    
    
    s3-account-search arn:aws:iam::123456789012:role/s3_read my-bucket

 **# 或者提供一个指定的源配置文件进行查询**

    
    
    s3-account-search --profile source_profile arn:aws:iam::123456789012:role/s3_read s3://my-bucket

## 工具运行机制

S3中有一个IAM策略条件-s3:ResourceAccount，这个条件用来给指定账号提供目标S3的访问权，但同时也支持通配符。通过构建正确的模式，我们就可以查看哪些模式将导致拒绝访问或允许访问，这样就能够找出目标账号ID了。

## 项目开发

我们使用Poetry来管理这个项目，首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/WeAreCloudar/s3-account-search

然后，运行下列安装命令：

    
    
    poetry install

最后，使用下列命令激活虚拟环境：

    
    
    poetry shell

或

    
    
    poetry run $command

### 向pypi发布一个新版本

编辑toml并更新版本号；

提交版本号；

运行下列命令：

    
    
    poetry publish --build

推送至GitHub；

在GitHub上创建一个新的Release；

## 项目地址

 **S3 Account Search：** 【[
_GitHub传送门_](https://github.com/WeAreCloudar/s3-account-search)】

## 参考资料

> [ _https://www.cloudar.be/awsblog/finding-the-accountid-of-any-> public-s3-bucket/_](https://www.cloudar.be/awsblog/finding-the-accountid-of-> any-public-s3-bucket/)

