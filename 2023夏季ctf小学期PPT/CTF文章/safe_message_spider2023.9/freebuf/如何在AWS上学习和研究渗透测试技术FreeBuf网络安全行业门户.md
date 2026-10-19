![](https://image.3001.net/images/20210719/1626704225_60f5896152bb9946fd9ca.png!small)

## 平台介绍

今天给大家带来的是一个名为“AWS Pen-Testing
Laboratory”的渗透测试实验室，这个渗透测试平台使用了Terraform（laC）部署在AWS上，并且提供了一个可以通过SSH或VP*N直接访问的Kali
Linux实例。除此之外，还在一个私有子网中提供了其他存在安全漏洞的实例以供研究人员使用。

## 功能组件

> Kali
> 2021.2实例（私钥已存储在pem中）：VP*N服务（客户端文件client_vp*n.wg）、可通过SSH/SCP访问、公共子网为10.0.0.5/24。
>
> 存在漏洞的Metasploitable设备，私有子网为0.1.5/24。
>
> 即将上线更多漏洞实验平台，比如说Docker等。

## 使用要求

> Terraform命令行接口：【[ _安装指引_](https://learn.hashicorp.com/terraform/getting-> started/install.html)】；
>
> AWS命令行接口：【[ _安装指引_](https://docs.aws.amazon.com/cli/latest/userguide/cli-> chap-install.html)】；
>
> 配置好AWS和Terraform命令行接口的$PATH参数；
>
> AWS账号，并通过AWS命令行接口配置凭证：aws configure；
>
> AWS商店中订阅Kali Linux；
>
> 构建好Metasploitable3 AMI镜像（[ _参考资料_](https://github.com/juanjoSanz/aws-> pentesting-lab/blob/main/metasploitable3)）；

## 实验平台架构

![](https://image.3001.net/images/20210719/1626704317_60f589bd37d401a606274.png!small)

## 平台使用部署

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/juanjoSanz/aws-pentesting-lab

接下来，我们需要在variables.tf文件中通过设置0或1来启用或禁用漏洞实例：

    
    
    variable "deploment-control" {
    
      type = map
    
      default = {
    
        #"instance" = 0 or 1, to disable or enable
    
        "metasploitable3" = 1
    
        "dvca" = 0
    
      }
    
      description = "Control which EC2 instances are deployed, 0 for none or 1"
    
    }

然后，使用Terraform来部署基础设施：

    
    
    terraform init
    
    terraform plan
    
    terraform apply -auto-approve   

## 输出数据

 **Terraform输出将会包含下列内容：**

> 针对Kali用户的SSH连接命令（使用sudo）；
>
> 针对Kali用户的Wireguard VP*N客户端文件竟会自动从Kali服务器获取；
>
> SCP命令用于获取Wireguard客户端文件；
>
> 针对Kali实例中创建的每一个普通用户，显示SSH连接所用的私钥文件和VP*N连接所用的Wireguard客户端文件；

## 实验室使用

### 通过SSH连接至Kali

    
    
    KALI_IP=<KALI_IP>     # configure kali public ip
    
    ssh -i kali.pem -o StrictHostKeyChecking=no -o IdentitiesOnly=yes kali@${KALI_IP}

### 通过Wireguard连接至本地Kali实例（查看client_vp*n.wg生成文件）

    
    
    KALI_IP=<KALI_IP>     # configure kali public ip
    
    scp -i kali.pem -o StrictHostKeyChecking=no IdentitiesOnly=yes kali@${KALI_IP}:/home/kali/client_vp*n.wg .
    
     
    
    ####
    
    (local_kali)$ sudo apt-get install –y wireguard
    
    (local_kali)$ sudo gedit /etc/wireguard/wg0.conf # copy contents of client_vp*n.wg
    
    (local_kali)$ sudo chmod 700 /etc/wireguard/wg0.conf
    
    (local_kali)$ sudo wg-quick up wg0
    
     
    
    (local_kali)$ ping 10.0.0.5  # test connectivity with kali instance in AWS

## 卸载部署

    
    
    terraform destroy -auto-approve

## 参考资料

> [
> _https://github.com/rapid7/metasploitable3_](https://github.com/rapid7/metasploitable3)
>
> [
> _https://aws.amazon.com/marketplace/pp/B08LL91KKB_](https://aws.amazon.com/marketplace/pp/B08LL91KKB)
>
> [ _https://github.com/offensive-terraform/terraform-aws-ec2-kali-> linux_](https://github.com/offensive-terraform/terraform-aws-ec2-kali-linux)

