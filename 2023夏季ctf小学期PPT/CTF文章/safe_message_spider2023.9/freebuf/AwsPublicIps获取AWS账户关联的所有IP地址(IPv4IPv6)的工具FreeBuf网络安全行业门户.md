****

![获取AWS账户关联的所有IP地址\(IPv4IPv6\)的工具](https://image.3001.net/images/20180829/1535509795_5b86052345b58.png!small)

**[Aws_Public_Ips](https://github.com/arkadiyt/aws_public_ips)是一个可帮助你获取与AWS账户关联的，所有IP地址(IPv4/IPv6)
的工具。它可以被作为库和CLI使用，并支持以下[AWS](https://www.kitploit.com/search/label/AWS)服务（均支持Classic和VPC平台）：**

> APIGateway
>
> CloudFront
>
> EC2（ECS, EKS, Beanstalk, Fargate, Batch, NAT 实例）
>
> ElasticSearch
>
> ELB (Classic ELB)
>
> ELBv2 (ALB/NLB)
>
> Lightsail
>
> RDS
>
> Redshift

如果服务未被列出（如S3，ElastiCache等），则很可能是因为它没有任何的支持（即它可能无法公开部署，并可能将所有IP地址解析到全局AWS基础架构等）。

##  **快速启动**

安装 gem 并运行：

    
    
    $ gem install aws_public_ips
    
    # Uses default ~/.aws/credentials
    $ aws_public_ips
    52.84.11.13
    52.84.11.83
    2600:9000:2039:ba00:1a:cd27:1440:93a1
    2600:9000:2039:6e00:1a:cd27:1440:93a1
    
    # With a custom profile
    $ AWS_PROFILE=production aws_public_ips
    52.84.11.159

##  **CLI 命令**

    
    
    $ aws_public_ips --help
    Usage: aws_public_ips [options]
        -s, --services <s1>,<s2>,<s3>    要检查的AWS服务列表。可用服务：apigateway,cloudfront,ec2,elasticsearch,elb,elbv2,lightsail,rds,redshift。默认为全部。
        -f, --format <format>            设置输出格式。支持的格式有：json,prettyjson,text。默认以文本格式输出。
        -v, --[no-]verbose               启用 debug/trace 输出
            --version                    打印版本
        -h, --help                       显示帮助信息

##  **配置**

对于身份验证，aws_public_ips会使用默认的[aws-sdk-ruby](https://github.com/aws/aws-sdk-ruby)配置，检查顺序及内容如下：

1\. 环境变量：

> AWS_ACCESS_KEY_ID
>
> AWS_SECRET_ACCESS_KEY
>
> AWS_REGION
>
> AWS_PROFILE

共享[凭证](https://www.kitploit.com/search/label/Credentials)文件：

> ~/.aws/credentials
>
> ~/.aws/config

如果运行在EC2, ECS, EKS, 或 Fargate上，则会检查实例配置文件（通过元数据端点）。

有关[更多信息](https://www.kitploit.com/search/label/Information)，请参阅AWS
SDK文档中的[配置部分](https://github.com/aws/aws-sdk-ruby#configuration)。

##  **IAM 权限**

想要从所有AWS服务中查找公网IP， IAM user所需的最小策略如下：

    
    
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "apigateway:GET",
            "cloudfront:ListDistributions",
            "ec2:DescribeInstances",
            "elasticloadbalancing:DescribeLoadBalancers",
            "lightsail:GetInstances",
            "lightsail:GetLoadBalancers",
            "rds:DescribeDBInstances",
            "redshift:DescribeClusters"
          ],
          "Resource": "*"
        }
      ]
    }

 ** *参考来源：[github](https://github.com/arkadiyt/aws_public_ips)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

