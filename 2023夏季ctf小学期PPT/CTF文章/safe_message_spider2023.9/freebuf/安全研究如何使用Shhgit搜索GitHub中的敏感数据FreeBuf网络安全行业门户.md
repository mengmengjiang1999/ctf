![](https://image.3001.net/images/20200802/1596344658.png!small)

## Shhgit

Shhgit能够帮助广大研究人员以近乎实时的方式寻找GitHub（包括Gists）、GitLab和BitBucket提交代码中的敏感数据和敏感文件。实际上，在GitHub中发现敏感数据并不算什么新鲜事了。目前也有很多很好的工具可以帮助我们去寻找开源代码库中的敏感信息。比如说，类似gitrob和truggleHog这样的工具，可以帮助我们挖掘commit历史记录并寻找特定代码库的机密令牌。除此之外，GitHub本身也可以通过他们的令牌搜索项目来寻找敏感信息。它们的目标是实时识别提交代码中的秘密令牌，并通知服务提供商采取行动。所以从理论上讲，如果任何AWS密钥被提交到了GitHub，Amazon就会收到通知并自动撤销它们。

Shhgit的主要目标是唤起用户的安全意识，并能够主动采取行动。虽然我不知道[
_GitHub令牌扫描项目_](https://help.github.com/en/articles/about-token-scanning)的内部工作机制，但是社区也可以做出很多努力来防止网络犯罪分子利用这个信息宝库。

通过对签名的一些调整，Shhgit将能够给我们提供非常优秀的功能。

## 工具安装

广大用户可以直接使用[
_预编译的代码_](https://www.github.com/eth0izzle/shhgit/releases)或使用Go来进行源码编译。

1、在用户设备上安装Go环境。

2、执行下列命令下载并构建Shhgit：

    
    
    go get github.com/eth0izzle/shhgit

3、或者使用下列命令将项目源码克隆至本地，并进行手动构建：

    
    
    git clone https://github.com/eth0izzle/shhgit.git
    
    GO111MODULE=on CGO_ENABLED=0 go build -v -i -o shhgit

除此之外，广大用户也可以直接在Docker环境中使用Shhgit。首先，获取config.yaml文件副本，并插入到你GitHub凭证中，然后执行下列命令：

    
    
    docker run -v $(pwd)/config.yaml:/config.yaml:ro eth0izzle/shhgit

## 工具使用

Shhgit可以通过两种方式工作：通过GitHub、GitLab和BitBucket公共代码库搜索，或处理本地目录种的文件。

默认配置下，Shhgit能够以前者，也就是公共模式运行，并且需要访问公共GitHub
API。此时，我们将需要一个令牌和访问权限，无论使用哪一种令牌，API的速率限制为每个账户每小时5000次请求。提供的账户唯一令牌越多，处理事件的速度就越快。大家可以按照这篇【文档】来生成一个灵台，并且不需要任何权限。接下来，将其写入config.yaml文件中的github_access_tokens域。

跟其他工具不同的是，我们不需要给Shhgit传递目标，我们只需要运行“$ shhgit”就可以获取所有匹配120种自带规则的GitHub
commit并寻找敏感数据/文件了。

如需以本地模式运行工具的话，则需要传递“--local”参数。

## 选项

    
    
    --clone-repository-timeout
    
            Maximum time it should take to clone a repository in seconds (default 10)
    
    --config-path
    
            Searches for config.yaml from given directory. If not set, tries to find if from shhgit binary's and current directory
    
    --csv-path
    
            Specify a path if you want to write found secrets to a CSV. Leave blank to disable
    
    --debug
    
            Print debugging information
    
    --entropy-threshold
    
            Finds high entropy strings in files. Higher threshold = more secret secrets, lower threshold = more false positives. Set to 0 to disable entropy checks (default 5.0)
    
    --local
    
            Specify local directory (absolute path) which to scan. Scans only given directory recursively. No need to have Github tokens with local run.
    
    --maximum-file-size
    
            Maximum file size to process in KB (default 512)
    
    --maximum-repository-size
    
            Maximum repository size to download and process in KB) (default 5120)
    
    --minimum-stars
    
            Only clone repositories with this many stars or higher. Set to 0 to ignore star count (default 0)
    
    --path-checks
    
            Set to false to disable file name/path signature checking, i.e. just match regex patterns (default true)
    
    --process-gists
    
            Watch and process Gists in real time. Set to false to disable (default true)
    
    --search-query
    
            Specify a search string to ignore signatures and filter on files containing this string (regex compatible)
    
    --silent
    
            Suppress all output except for errors
    
    --temp-directory
    
            Directory to store repositories/matches (default "%temp%\shhgit")
    
    --threads
    
            Number of concurrent threads to use (default number of logical CPUs)

## 配置

config.yaml文件由七个元素组成，项目以提供了[
_默认配置文件_](https://github.com/eth0izzle/shhgit/blob/master/config.yaml)：

    
    
    github_access_tokens: # provide at least one token
    
      - 'token one'
    
      - 'token two'
    
    webhook: '' # URL to a POST webhook.
    
    webhook_payload: '' # Payload to POST to the webhook URL
    
    blacklisted_extensions: [] # list of extensions to ignore
    
    blacklisted_paths: [] # list of paths to ignore
    
    blacklisted_entropy_extensions: [] # additional extensions to ignore for entropy checks
    
    signatures: # list of signatures to check
    
      - part: '' # either filename, extension, path or contents
    
        match: '' # simple text comparison (if no regex element)
    
        regex: '' # regex pattern (if no match element)
    
        name: '' # name of the signature

## 签名

Shhgit自带了120种签名方案，我们可以通过编辑config.yaml文件来进行签名的添加和删除：

    
    
    Chef private key, Potential Linux shadow file, Potential Linux passwd file, Docker configuration file, NPM configuration file, Environment configuration file, Contains a private key, AWS Access Key ID Value, AWS Access Key ID, AWS Account ID, AWS Secret Access Key, AWS Session Token, Artifactory, CodeClimate, Facebook access token, Google (GCM) Service account, Stripe API key, Google OAuth Key, Google Cloud API Key
    
    Google OAuth Access Token, Picatic API key, Square Access Token, Square OAuth Secret, PayPal/Braintree Access Token, Amazon MWS Auth Token, Twilo API Key, MailGun API Key, MailChimp API Key, SSH Password, Outlook team, Sauce Token, Slack Token, Slack Webhook, SonarQube Docs API Key, HockeyApp, Username and password in URI, NuGet API Key, Potential cryptographic private key, Log file, Potential cryptographic key bundle, Potential cryptographic key bundle
    
    Potential cryptographic key bundle, Potential cryptographic key bundle, Pidgin OTR private key, OpenVPN client configuration file, Azure service configuration schema file, Remote Desktop connection file, Microsoft SQL database file, Microsoft SQL server compact database file, SQLite database file, SQLite3 database file, Microsoft BitLocker recovery key file
    
    Microsoft BitLocker Trusted Platform Module password file, Windows BitLocker full volume encrypted data file, Java keystore file, Password Safe database file, Ruby On Rails secret token configuration file, Carrierwave configuration file, Potential Ruby On Rails database configuration file, OmniAuth configuration file, Django configuration file
    
    1Password password manager database file, Apple Keychain database file, Network traffic capture file, GnuCash database file, Jenkins publish over SSH plugin file, Potential Jenkins credentials file, KDE Wallet Manager database file, Potential MediaWiki configuration file, Tunnelblick VPN configuration file, Sequel Pro MySQL database manager bookmark file, Little Snitch firewall configuration file, Day One journal file, Potential jrnl journal file, Chef Knife configuration file, cPanel backup ProFTPd credentials file
    
    Robomongo MongoDB manager configuration file, FileZilla FTP configuration file, FileZilla FTP recent servers file, Ventrilo server configuration file, Terraform variable config file, Shell configuration file, Shell configuration file, Shell configuration file, Private SSH key, Private SSH key, Private SSH key, Private SSH key, SSH configuration file, Potential cryptographic private key, Shell command history file
    
    MySQL client command history file, PostgreSQL client command history file, PostgreSQL password file, Ruby IRB console history file, Pidgin chat client account configuration file, Hexchat/XChat IRC client server list configuration file, Irssi IRC client configuration file, Recon-ng web reconnaissance framework API key database, DBeaver SQL database manager configuration file, Mutt e-mail client configuration file, S3cmd configuration file, AWS CLI credentials file, SFTP connection configuration file, T command-line Twitter client configuration file, Shell configuration file
    
    Shell profile configuration file, Shell command alias configuration file, PHP configuration file, GNOME Keyring database file, KeePass password manager database file, SQL dump file, Apache htpasswd file, Configuration file for auto-login process, Rubygems credentials file, Tugboat DigitalOcean management tool configuration, DigitalOcean doctl command-line client configuration file, git-credential-store helper credentials file, GitHub Hub command-line client configuration file, Git configuration file

## 工具运行截图

![](https://image.3001.net/images/20200802/1596344725.png!small)

![](https://image.3001.net/images/20200802/1596344741.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/eth0izzle/shhgit/blob/master/LICENSE)开源许可证协议。

## 项目地址

Shhgit：【[ _GitHub传送门_](https://github.com/eth0izzle/shhgit)】

