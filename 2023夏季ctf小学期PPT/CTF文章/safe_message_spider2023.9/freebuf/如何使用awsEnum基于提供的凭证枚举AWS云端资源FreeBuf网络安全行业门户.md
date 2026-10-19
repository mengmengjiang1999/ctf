![](https://image.3001.net/images/20220709/1657301387_62c8698b744a26f8a64ac.jpeg!small)  

## 关于awsEnum

awsEnum是一款针对AWS云端资源安全的审计工具，该工具基于Python
3开发，可以帮助广大研究人员根据输入的凭证信息来枚举目标AWS云端资源和AWS服务。

当前该工具仍处于测试过程中，发布的为beta版本。该工具的主要目标是为了帮助广大研究人员更好地对AWS云端环境进行安全渗透测试，可以用于漏洞奖励计划、AWS云端安全审计或其他相关的安全研究活动。

## 功能介绍

> 1、通过boto3连接AWS服务；
>
> 2、awsEnum允许用户设置发送的请求数量，默认为1000；
>
> 3、awsEnum支持将分析结果存储为JSON文件；
>
> 4、支持将AWS凭证信息存储在awscli配置中，可以将配置文件以文件名参数的形式传递给awsEnum；
>
> 5、支持的服务：EC2、IAM、S3；

## 工具要求

> Python 3
>
> pip包管理工具

## 工具下载

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python
3环境。接下来，我们就可以使用下列命令将该项目源码克隆至本地了：

    
    
    git clone https://github.com/bassammaged/awsEnum.git

## 工具部署

下载完成后，我们需要利用项目提供的requirements.txt安装该工具所需的其他依赖组件：

    
    
    python3 -m pip install requirements.txt

## 工具使用

接下来，我们就可以直接 通过run.py脚本来运行awsEnum了：

    
    
    python3 run.py

### 帮助信息

    
    
    ▄▄▄▄▄▄ ▄     ▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄    ▄ ▄▄   ▄▄ ▄▄   ▄▄
    
    █      █ █ ▄ █ █       █       █  █  █ █  █ █  █  █▄█  █
    
    █  ▄   █ ██ ██ █  ▄▄▄▄▄█    ▄▄▄█   █▄█ █  █ █  █       █
    
    █ █▄█  █       █ █▄▄▄▄▄█   █▄▄▄█       █  █▄█  █       █
    
    █      █       █▄▄▄▄▄  █    ▄▄▄█  ▄    █       █       █
    
    █  ▄   █   ▄   █▄▄▄▄▄█ █   █▄▄▄█ █ █   █       █ ██▄██ █
    
    █▄█ █▄▄█▄▄█ █▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄█  █▄▄█▄▄▄▄▄▄▄█▄█   █▄█
    
    --------------------------------------------------------    
    If you are looking to enumerate AWS services. So, welcome
    
    to awsEnum, awsEnum is a python script trying to facilitate
    
    the enumerate phase of AWS cloud with the lowest possible
    
    headache and less noise. Therefore we are not supporting
    
    the `all` mode. ----------------------------------------    
    --------------------------------------------------------    
            developed by bassammaged (@kemet)
    
                    version: 0.1 Beta
    
    --------------------------------------------------------    
    [!] Make sure you already defined credential profile via AWS CLI.
    
     
    
    usage: run.py [-h] [-p profile_name] [-r region_name] [-v | --verbose | --no-verbose] [-t TRIES] aws_service_name
    
     
    
    positional arguments:
    
      aws_service_name      Specify the aws service for enumration. Supported services are: ['ec2', 'iam', 's3'] (default: all)
    
     
    
    options:
    
      -h, --help            show this help message and exit
    
      -p profile_name, --profile profile_name
    
                            specify aws credential profile that will be used through the enumeration. (default: default)
    
      -r region_name, --region region_name
    
                            specify aws region. (default: eu-central-1)
    
      -v, --verbose, --no-verbose
    
                            Allows the script to print out the message level start with debug. (default: False)
    
      -t TRIES, --tries TRIES
    
                            set maximum tries. (default: 1000)

### 参数解释

    
    
    aws_service_name：指定需要枚举的目标AWS服务，支持的参数：['ec2', 'iam', 's3']，默认：枚举所有资源；
    
    -h, --help：显示工具帮助信息和退出；
    
    -p profile_name, --profile profile_name：指定AWS凭证配置文件；
    
    -r region_name, --region region_name：指定AWS实例区域，默认：eu-central-1；
    
    -v, --verbose, --no-verbose：允许工具输出包含调试信息在内的所有信息，默认：False；
    
    -t TRIES, --tries TRIES：设置最大尝试次数，默认：1000；

### 输出报告

    
    
    [
    
        {
    
            "AmiLaunchIndex": 0,
    
            "ImageId": "ami-7c803d1c",
    
            "InstanceId": "i-05bef8a081f307783",
    
            "InstanceType": "t2.micro",
    
            "KeyName": "Default",
    
            "LaunchTime": "2017-02-12 22:29:24+00:00",
    
            "Monitoring": {
    
                "State": "disabled"
    
            },
    
            "Placement": {
    
                "AvailabilityZone": "us-west-2a",
    
                "GroupName": "",
    
                "Tenancy": "default"
    
            },
    
            "PrivateDnsName": "ip-172-31-41-84.us-west-2.compute.internal",
    
            "PrivateIpAddress": "172.31.41.84",
    
            "ProductCodes": [],
    
            "PublicDnsName": "ec2-35-165-182-7.us-west-2.compute.amazonaws.com",
    
            "PublicIpAddress": "35.165.182.7",
    
            "State": {
    
                "Code": 16,
    
                "Name": "running"
    
            },
    
            "StateTransitionReason": "",
    
            "SubnetId": "subnet-d962aa90",
    
            "VpcId": "vpc-1052ce77",
    
            "Architecture": "x86_64",
    
            "BlockDeviceMappings": [
    
                {
    
                    "DeviceName": "/dev/sda1",
    
                    "Ebs": {
    
                        "AttachTime": "2017-02-12 22:29:25+00:00",
    
                        "DeleteOnTermination": true,
    
                        "Status": "attached",
    
                        "VolumeId": "vol-04f1c039bc13ea950"
    
                    }
    
                }
    
            ],
    
            "ClientToken": "kTOiC1486938563883",
    
            "EbsOptimized": false,
    
            "Hypervisor": "xen",
    
            "IamInstanceProfile": {
    
                "Arn": "arn:aws:iam::975426262029:instance-profile/flaws",
    
                "Id": "AIPAIK7LV6U6UXJXQQR3Q"
    
            },
    
            "NetworkInterfaces": [
    
                {
    
                    "Association": {
    
                        "IpOwnerId": "amazon",
    
                        "PublicDnsName": "ec2-35-165-182-7.us-west-2.compute.amazonaws.com",
    
                        "PublicIp": "35.165.182.7"
    
                    },
    
                    "Attachment": {
    
                        "AttachTime": "2017-02-12 22:29:24+00:00",
    
                        "AttachmentId": "eni-attach-a4901fc2",
    
                        "DeleteOnTermination": true,
    
                        "DeviceIndex": 0,
    
                        "Status": "attached",
    
                        "NetworkCardIndex": 0
    
                    },
    
                    "Description": "",
    
                    "Groups": [
    
                        {
    
                            "GroupName": "launch-wizard-1",
    
                            "GroupId": "sg-490f6631"
    
                        }
    
                    ],
    
                    "Ipv6Addresses": [],
    
                    "MacAddress": "06:b0:7a:92:21:cf",
    
                    "NetworkInterfaceId": "eni-c26ed780",
    
                    "OwnerId": "975426262029",
    
                    "PrivateDnsName": "ip-172-31-41-84.us-west-2.compute.internal",
    
                    "PrivateIpAddress": "172.31.41.84",
    
                    "PrivateIpAddresses": [
    
                        {
    
                            "Association": {
    
                                "IpOwnerId": "amazon",
    
                                "PublicDnsName": "ec2-35-165-182-7.us-west-2.compute.amazonaws.com",
    
                                "PublicIp": "35.165.182.7"
    
                            },
    
                            "Primary": true,
    
                            "PrivateDnsName": "ip-172-31-41-84.us-west-2.compute.internal",
    
                            "PrivateIpAddress": "172.31.41.84"
    
                        }
    
                    ],
    
                    "SourceDestCheck": true,
    
                    "Status": "in-use",
    
                    "SubnetId": "subnet-d962aa90",
    
                    "VpcId": "vpc-1052ce77",
    
                    "InterfaceType": "interface"
    
                }
    
            ],
    
            "RootDeviceName": "/dev/sda1",
    
            "RootDeviceType": "ebs",
    
            "SecurityGroups": [
    
                {
    
                    "GroupName": "launch-wizard-1",
    
                    "GroupId": "sg-490f6631"
    
                }
    
            ],
    
            "SourceDestCheck": true,
    
            "VirtualizationType": "hvm",
    
            "CpuOptions": {
    
                "CoreCount": 1,
    
                "ThreadsPerCore": 1
    
            },
    
            "CapacityReservationSpecification": {
    
                "CapacityReservationPreference": "open"
    
            },
    
            "HibernationOptions": {
    
                "Configured": false
    
            },
    
            "MetadataOptions": {
    
                "State": "applied",
    
                "HttpTokens": "optional",
    
                "HttpPutResponseHopLimit": 1,
    
                "HttpEndpoint": "enabled",
    
                "HttpProtocolIpv6": "disabled",
    
                "InstanceMetadataTags": "disabled"
    
            },
    
            "EnclaveOptions": {
    
                "Enabled": false
    
            },
    
            "PlatformDetails": "Linux/UNIX",
    
            "UsageOperation": "RunInstances",
    
            "UsageOperationUpdateTime": "2017-02-12 22:29:24+00:00",
    
            "PrivateDnsNameOptions": {},
    
            "MaintenanceOptions": {
    
                "AutoRecovery": "default"
    
            }
    
        }
    
    ]

## 工具运行截图

![](https://image.3001.net/images/20220709/1657301482_62c869ea3d48c0adb1e25.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/bassammaged/awsEnum/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **awsEnum** ：【[ _GitHub传送门_](https://github.com/bassammaged/awsEnum)】

