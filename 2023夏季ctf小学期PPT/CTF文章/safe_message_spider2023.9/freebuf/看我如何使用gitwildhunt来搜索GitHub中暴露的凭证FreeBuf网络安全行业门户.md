![](https://image.3001.net/images/20210127/1611740536_60113578d8915991e4f69.jpg!small)

## 写在前面的话

在这篇文章中，我们将使用git-wild-hunt来搜索暴露在GitHub上的用户凭证信息。接下来，我们需要按照下列步骤安装和使用git-wild-hunt。

> 安装工具
>
> 配置GitHub令牌
>
> 搜索凭证
>
> 查看结果：cat results.json | jq

## 工具安装

该工具的使用需要主机预先安装好Python3和Virtualenv。

接下来，广大研究人员需要使用下列命令将该项目源码克隆至本地，然后使用cd命令切换到项目目录中，并运行安装脚本完成工具和依赖组件的安装：

    
    
    git clone https://github.com/d1vious/git-wild-hunt
    
    cd git-wild-hunt
    
    pip install virtualenv && virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt

完成工具的安装和配置之后，我们还需要配置一个GitHub API密钥。

## 配置git-wild-hunt.conf

请确保你[ _正确配置_](https://github.com/d1vious/git-wild-hunt/blob/master/git-wild-hunt.conf)了GitHub令牌，如果你没有创建的话，请参考这篇【[
_指引_](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)】。

    
    
    [global]
    
    github_token = ''
    
    # GitHub token for searching
    
     
    
    output = results.json
    
    # stores matches in JSON here
    
     
    
    log_path = git-wild-hunt.log
    
    # Sets the log_path for the logging file
    
     
    
    log_level = INFO
    
    # Sets the log level for the logging
    
    # Possible values: INFO, ERROR
    
     
    
    regexes = regexes.json
    
    # regexes to check the git wild hunt search against

## GitHub搜索样例

注意：-s选项可以接受任意GitHub高级搜索语句，具体请参考下列使用样例。

### 查找GCP JWT令牌文件：

    
    
    python git-wild-hunt.py -s "extension:json filename:creds language:JSON"

### 查找AWS API凭证：

    
    
    python git-wild-hunt.py -s "path:.aws/ filename:credentials"

### 查找Azure JWT令牌：

    
    
    python git-wild-hunt.py -s "extension:json path:.azure filename:accessTokens language:JSON"

### 查找GSUtils配置：

    
    
    python git-wild-hunt.py -s "path:.gsutil filename:credstore2"

### 查找Kubernetes配置文件：

    
    
    python git-wild-hunt.py -s "path:.kube filename:config"

### 搜索Jenkins credentials.xml文件：

    
    
    python git-wild-hunt.py -s "extension:xml filename:credentials.xml language:XML"

### 查找.circleci中的敏感信息：

    
    
    python git-wild-hunt.py -s "extension:yml path:.circleci filename:config language:YAML"

### 通用credentials.yml搜索：

    
    
    python git-wild-hunt.py -s "extension:yml filename:credentials.yml language:YAML"

## 工具使用

    
    
    usage: git-wild-hunt.py [-h] -s SEARCH [-c CONFIG] [-v]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -s SEARCH, --search SEARCH
    
                            search to execute
    
      -c CONFIG, --config CONFIG
    
                            config file path
    
      -v, --version         shows current git-wild-hunt version

## regexes.json文件

这个文件中包含所有可以用来检测 _搜索_返回结果文件元数据的正则表达式。我们可以根据自己的需要去添加或修改其中的正则表达式，以匹配我们所要查询的内容。

当前可以通过正则表达式验证的凭证包括：

    
    
    AWS API密钥
    
    Amazon AWS Access密钥 ID
    
    Amazon MWS Auth令牌
    
    Facebook访问令牌
    
    Facebook OAuth
    
    Generic API密钥
    
    Generic Secret
    
    GitHub
    
    Google (GCP) Service-account
    
    Google API密钥
    
    Google Cloud Platform API密钥
    
    Google Cloud Platform OAuth
    
    Google Drive API密钥
    
    Google Drive OAuth
    
    Google Gmail API密钥
    
    Google Gmail OAuth
    
    Google OAuth访问令牌
    
    Google YouTube API密钥
    
    Google YouTube OAuth
    
    Heroku API密钥
    
    MailChimp API密钥
    
    Mailgun API密钥
    
    PGP 私钥 block
    
    Password in URL
    
    PayPal Braintree访问令牌
    
    Picatic API密钥
    
    RSA 私钥
    
    SSH (DSA) 私钥
    
    SSH (EC) 私钥
    
    Slack令牌
    
    Slack Webhook
    
    Square访问令牌
    
    Square OAuth Secret
    
    Stripe API密钥
    
    Stripe Restricted API密钥
    
    Twilio API密钥
    
    Twitter访问令牌
    
    Twitter OAuth

## 项目地址

git-wild-hunt：【[ _GitHub传送门_](https://github.com/d1vious/git-wild-hunt)】

