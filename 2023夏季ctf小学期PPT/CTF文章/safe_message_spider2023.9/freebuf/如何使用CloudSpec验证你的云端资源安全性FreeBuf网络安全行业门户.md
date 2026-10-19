![](https://image.3001.net/images/20220106/1641458807_61d6ac775737cba4fce66.png!small)

## 关于CloudSpec

CloudSpec是一款功能强大的开源工具，可以帮助广大研究人员通过普通人都能理解的逻辑语言来验证你托管在云服务提供商那里的云端资源安全。该工具支持通过相当简单的语法，来验证云端资源的配置情况，以避免出现那些可能导致云服务可用性受损或安全性问题出现的错误问题。

## 项目介绍

CloudSpec支持验证云服务提供商托管的资源，这种资源可以是EC2实例或SES规则，实际上CloudSpec可以对云服务提供商实现的任何内容进行验证。

资源具有属性和关联。属性定义资源的形式或配置，而关联定义的是它与其他资源的关系。使用CloudSpec，我们不仅可以验证资源的配置，还可以验证其关联资源的配置。比如说，我们以一个EC2实例为例。它具有定义其资源形式的属性，如其唯一实例ID、名称、类型等。但它也有关联，比如它所属的子网、连接到它的EBS卷、它使用的AMI等等。我们不仅可以验证EC2实例是否属于特定实例类型，或者是否启用了删除终止选项，还可以验证其附加卷的大小、其子网的CIDR块或其关联资源中的任何其他属性，或其关联资源的关联资源等等。

我们的云端资源可能是交杂在一起的，CloudSpec可以帮助我们捋清资源之间的关系，并创建图表。并根据我们自己的最佳实践或法规遵从性策略，在有需要的时候通过CloudSpec以及简单的逻辑语言去遍历和验证这份图表。

    
    
    set aws:regions = ["us-east-1", "eu-west-1"]
    
     
    
    use "./my_module" as my_module
    
     
    
    rule "Buckets must have access logs enabled"
    
        on aws:s3:bucket
    
        assert access_logs is enabled
    
    end rule
    
     
    
    rule "Instances must use 'gp2' volumes and be at least 50GiBs large."
    
        on aws:ec2:instance
    
        with tags["environment"] equal to "production"
    
        assert devices (
    
            > volume (
    
                type equal to "gp2" and
    
                size gte 50
    
            )
    
        )
    
    End
    
     

## "Provider"

CloudSpec本身不支持任何资源，CloudSpec的核心是一个针对规范文件的语法解释器及其验证引擎。为了知此恨不同类型的资源，CloudSpec专门引入了“Provider”的概念。

一个“Provider”定义了不同资源类型的概述、属性和关联，以及加载这些资源的逻辑。

## 工具下载&安装

我们可以自行构建并运行CloudSpec Jar，首先我们需要在本地主机上安装并配置好下列依赖组件：

> Git
>
> Maven 3
>
> OpenJDK 8
>
> Docker

接下来，获取项目源码，并构建CloudSpec：

 **# 克隆GitHub项目源码**

    
    
    git clone https://github.com/efoncubierta/cloudspec
    
    cd cloudspec

# **构建CloudSpec**

    
    
    mvn clean install

# **运行CloudSpec**

    
    
    java -jar runner/target/cloudspec-${VERSION}.jar -h

## 运行CloudSpec Docker镜像

当然了，我们也可以直接从Docker Hub拉取并运行最新版本的Docker镜像。

如需使用Docker镜像，我们首先需要在一个目录内存储一个规范文件（例如“specs/my_module”），并将其加载进Docker容器中。否则，CloudSpec将无法读取容器外的规范文件：

    
    
    export AWS_ACCESS_KEY_ID=***
    
    export AWS_SECRET_ACCESS_KEY=***
    
    export AWS_REGION=eu-west-1
    
    docker run -v "/my_module:/my_module" -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_REGION efoncubierta/cloudspec run -d my_module

如果你是在AWS环境中运行的Docker镜像，并使用了绑定的专用IAM角色，你就可以忽略上述代码中的AWS环境变量了。

如需了解更多的CloudSpec命令信息，可以使用下列命令：

    
    
    docker run efoncubierta/cloudspec -h

## 工具运行演示

![](https://image.3001.net/images/20220106/1641458928_61d6acf054ec838b2a1f1.gif)

## 项目地址

 **CloudSpec：** 【[ _GitHub传送门_](https://github.com/efoncubierta/cloudspec)】

## 参考资料

> [ _https://cloudspec.pro/docs_](https://cloudspec.pro/docs)

