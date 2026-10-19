## 简介

**GitMiner是一款自动化的高级敏感内容挖掘工具。此工具旨在通过代码或代码片段在github搜索页面进行挖掘，并以此来证明公共存储库的脆弱性，以及将包含敏感信息的代码存储在其中所带来的安全隐患。**

## 安装要求

    
    
    lxml
    
    requests
    
    argparse
    
    json
    
    re

## 安装

    
    
    $ git clone http://github.com/UnkL4b/GitMiner
    $ cd GitMiner
    ~/GitMiner $ pip3 install -r requirements.txt

## Docker

    
    
    $ git clone http://github.com/UnkL4b/GitMiner
    $ cd GitMiner
    $ docker build -t gitminer .
    $ docker run -it gitminer -h

## 帮助信息

    
    
                                     UnkL4b
      __                   Automatic search for Github
    ((OO))   ▄████  ██▓▄▄▄█████▓ ███▄ ▄███▓ ██▓ ███▄    █ ▓█████  ██▀███  
     \__/   ██▒ ▀█▒▓██▒▓  ██▒ ▓▒▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒      OO
      |^|  ▒██░▄▄▄░▒██▒▒ ▓██░ ▒░▓██    ▓██░▒██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒      oOo
      | |  ░▓█  ██▓░██░░ ▓██▓ ░ ▒██    ▒██ ░██░▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄      OoO
      | |  ░▒▓███▀▒░██░  ▒██▒ ░ ▒██▒   ░██▒░██░▒██░   ▓██░░▒████▒░██▓ ▒██▒  /oOo 
      | |___░▒___▒_░▓____▒_░░___░_▒░___░__░░▓__░_▒░___▒_▒_░░_▒░_░░_▒▓_░▒▓░_/ /
      \______░___░__▒_░____░____░__░______░_▒_░░_░░___░_▒░_░_░__░__░▒_░_▒░__/  v2.0
           ░ ░   ░  ▒ ░  ░      ░      ░    ▒ ░   ░   ░ ░    ░     ░░   ░ 
                 ░  ░                  ░    ░           ░    ░  ░   ░     
      -> github.com/UnkL4b
      -> unkl4b.github.io
      +---------------------[WARNING]---------------------+
      | DEVELOPERS ASSUME NO LIABILITY AND ARE NOT        |
      | RESPONSIBLE FOR ANY MISUSE OR DAMAGE CAUSED BY    |
      | THIS PROGRAM                                      |
      +---------------------------------------------------+ 
           [-h] [-q 'filename:shadow path:etc']
           [-m wordpress] [-o result.txt]
           [-r '/^\s*.*?;?\s*$/gm']
           [-c _octo=GH1.1.2098292984896.153133829439; _ga=GA1.2.36424941.153192375318; user_session=oZIxL2_ajeDplJSndfl37ddaLAEsR2l7myXiiI53STrfhqnaN; __Host-user_session_same_site=oXZxv9_ajeDplV0gAEsmyXiiI53STrfhDN; logged_in=yes; dotcom_user=unkl4b; tz=America%2FSao_Paulo; has_recent_activity=1; _gh_sess=MmxxOXBKQ1RId3NOVGpGcG54aEVnT1o0dGhxdGdzWVpySnFRd1dVYUk5TFZpZXFuTWxOdW1FK1IyM0pONjlzQWtZM2xtaFR3ZDdxlGMCsrWnBIdnhUN0tjVUtMYU1GeG5Pbm5DMThuWUFETnZjcllGOUNkRGUwNUtKOVJTaGR5eUJYamhWRE5XRnMWZZN3Y3dlpFNDZXL1NWUEN4c093RFhQd3RJQ1NBdmhrVDE3VVNiUFF3dHBycC9FeDZ3cFVXV0ZBdXZieUY5WDRlOE9ZSG5sNmRHUmllcmk0Up1MTcyTXZrN1RHYmJSdz09--434afdd652b37745f995ab55fc83]
    
    optional arguments:
      -h, --help            显示帮助信息并退出
      -q 'filename:shadow path:etc', --query 'filename:shadow path:etc'           指定搜索词
      -m wordpress, --module wordpress               指定搜索模块
      -o result.txt, --output result.txt             指定输出文件的保存位置
      -r '/^\s*(.*?);?\s*$/gm', --regex '/^\s*(.*?);?\s*$/gm'               设置在文件中搜索的正则
      -c _octo=GH1.1.2098292984896.153133829439; _ga=GA1.2.36424941.153192375318; 
    
    user_session=oZIxL2_ajeDplJSndfl37ddaLAEsR2l7myXiiI53STrfhqnaN; __Host-user_session_same_site=oXZxv9_ajeDplV0gAEsmyXiiI53STrfhDN; logged_in=yes; dotcom_user=unkl4b; tz=America%2FSao_Paulo; has_recent_activity=1; _gh_sess=MmxxOXBKQ1RId3NOVGpGcG54aEVnT1o0dGhxdGdzWVpySnFRd1dVYUk5TFZpZXFuTWxOdW1FK1IyM0pONjlzQWtZM2xtaFR3ZDdxlGMCsrWnBIdnhUN0tjVUtMYU1GeG5Pbm5DMThuWUFETnZjcllGOUNkRGUwNUtKOVJTaGR5eUJYamhWRE5XRnMWZZN3Y3dlpFNDZXL1NWUEN4c093RFhQd3RJQ1NBdmhrVDE3VVNiUFF3dHBycC9FeDZ3cFVXV0ZBdXZieUY5WDRlOE9ZSG5sNmRHUmllcmk0Up1MTcyTXZrN1RHYmJSdz09--434afdd652b37745f995ab55fc83, --cookie _octo=GH1.1.2098292984896.153133829439; _ga=GA1.2.36424941.153192375318; user_session=oZIxL2_ajeDplJSndfl37ddaLAEsR2l7myXiiI53STrfhqnaN; __Host-user_session_same_site=oXZxv9_ajeDplV0gAEsmyXiiI53STrfhDN; logged_in=yes; dotcom_user=unkl4b; tz=America%2FSao_Paulo; has_recent_activity=1; _gh_sess=MmxxOXBKQ1RId3NOVGpGcG54aEVnT1o0dGhxdGdzWVpySnFRd1dVYUk5TFZpZXFuTWxOdW1FK1IyM0pONjlzQWtZM2xtaFR3ZDdxlGMCsrWnBIdnhUN0tjVUtMYU1GeG5Pbm5DMThuWUFETnZjcllGOUNkRGUwNUtKOVJTaGR5eUJYamhWRE5XRnMWZZN3Y3dlpFNDZXL1NWUEN4c093RFhQd3RJQ1NBdmhrVDE3VVNiUFF3dHBycC9FeDZ3cFVXV0ZBdXZieUY5WDRlOE9ZSG5sNmRHUmllcmk0Up1MTcyTXZrN1RHYmJSdz09--434afdd652b37745f995ab55fc83                     为github指定cookie

## 示例

使用密码搜索wordpress配置文件：

    
    
    $:> python3 gitminer-v2.0.py -q 'filename:wp-config extension:php FTP_HOST in:file ' -m wordpress -c pAAAhPOma9jEsXyLWZ-16RTTsGI8wDawbNs4 -o result.txt

![68747470733a2f2f322e62702e626c6f6773706f742e636f6d2f2d4762707a524f6945796e512f56744c7974664d715169492f4141414141414141626e6b2f356844706850344d6266342f73313630302f776f7264707265737345582e706e67.png](https://image.3001.net/images/20180824/1535070955_5b7f52eb47e22.png!small)

查找包含密码的巴西政府档案：

    
    
    $:> python3 gitminer-v2.0.py --query 'extension:php "root" in:file AND "gov.br" in:file' -m senhas -c pAAAhPOma9jEsXyLWZ-16RTTsGI8wDawbNs4

在etc路径下查找shadow文件：

    
    
    $:> python3 gitminer-v2.0.py --query 'filename:shadow path:etc' -m root -c pAAAhPOma9jEsXyLWZ-16RTTsGI8wDawbNs4

使用密码搜索joomla配置文件：

    
    
    $:> python3 gitminer-v2.0.py --query 'filename:configuration extension:php "public password" in:file' -m joomla -c pAAAhPOma9jEsXyLWZ-16RTTsGI8wDawbNs4

##
![68747470733a2f2f332e62702e626c6f6773706f742e636f6d2f2d3141734e6d464b66736f412f56744c79764a46793257492f4141414141414141626e6f2f433778546278747a4f6f382f73313630302f6a6f6f6d6c6145582e706e67.png](https://image.3001.net/images/20180824/1535070984_5b7f5308b0b85.png!small)

## 入侵SSH服务器

![68747470733a2f2f696d672e796f75747562652e636f6d2f76692f79494a4f6c4b5a775151772f302e6a7067.jpg](https://image.3001.net/images/20180824/1535071014_5b7f5326367c3.jpg!small)

## 演示视频

[1](https://www.youtube.com/watch?v=yIJOlKZwQQw)

## Dork搜索语法

by@techgaun (<https://github.com/techgaun/github-dorks>)

Dork | Description  
---|---  
filename:.npmrc _auth | npm 注册表验证数据  
filename:.dockercfg auth | docker 注册表验证数据  
extension:pem private | 私钥  
extension:ppk private | puttygen 私钥  
filename:id_rsa or filename:id_dsa | 私有 ssh keys  
extension:sql mysql dump | mysql dump  
extension:sql mysql dump password | mysql dump 查找密码；你也可以尝试其它相似语法  
filename:credentials aws_access_key_id | 可能会返回虚假值  
filename:.s3cfg | 可能会返回虚假值  
filename:wp-config.php | wordpress 配置文件  
filename:.htpasswd | htpasswd 文件  
filename:.env DB_USERNAME NOT homestead | laravel .env (CI, 各种基于ruby的框架)  
filename:.env MAIL_HOST=smtp.gmail.com | gmail smtp 配置 (你也可以尝试其它不同的smtp
services)  
filename:.git-credentials | git 凭证存储, 添加NOT用户名以获得更有效的结果  
PT_TOKEN language:bash | pivotaltracker tokens  
filename:.bashrc password | 在.bashrc中搜索密码等（你也可以尝试使用.bash_profile）  
filename:.bashrc mailchimp | 同上。你也可以尝试更多其它语法  
filename:.bash_profile aws | aws access 和 secret keys  
rds.amazonaws.com password | Amazon RDS 可能的凭据  
extension:json api.forecast.io |  查找 api keys/secrets  
extension:json mongolab.com | json configs中的mongolab凭据  
extension:yaml mongolab.com | yaml配置中的mongolab凭据（此外，你还可以尝试使用yml）  
jsforce extension:js conn.login | nodejs项目中可能的salesforce凭据  
SF_USERNAME salesforce | 可能的salesforce凭据  
filename:.tugboat NOT _tugboat | Digital Ocean tugboat 配置文件  
HEROKU_API_KEY language:shell | Heroku api keys  
HEROKU_API_KEY language:json | 在json文件中的Heroku api keys  
filename:.netrc password | 可能拥有敏感凭据的netrc  
filename:_netrc password | 可能拥有敏感凭据的netrc  
filename:hub oauth_token | 存储github令牌的hub配置  
filename:robomongo.json | robomongo使用的mongodb凭证文件  
filename:filezilla.xml Pass | filezilla配置文件，可能有ftp的 user/pass 信息  
filename:recentservers.xml Pass | filezilla配置文件，可能有ftp的 user/pass 信息  
filename:config.json auths | docker注册表验证数据  
filename:idea14.key | IntelliJ Idea 14 key  
filename:config irc_pass | 可能的IRC配置文件  
filename:connections.xml | 可能的数据库连接配置文件  
filename:express.conf path:.openshift | openshift配置文件，只有电子邮件和服务器  
filename:.pgpass | 包含密码的PostgreSQL文件  
filename:proftpdpasswd | cpanel创建的proftpd的用户名和密码  
filename:ventrilo_srv.ini | Ventrilo 配置文件  
[WFClient] Password= extension:ica | 用户连接到Citrix应用程序服务器所需的WinFrame-Client信息  
filename:server.cfg rcon password | 反恐精英RCON密码  
JEKYLL_GITHUB_TOKEN | Github令牌用于jekyll  
filename:.bash_history | Bash 历史文件  
filename:.cshrc | 用于csh shell的RC文件  
filename:.history | 历史文件 (经常被许多工具使用)  
filename:.sh_history | korn shell 历史  
filename:sshd_config | OpenSSH server 配置文件  
filename:dhcpd.conf | DHCP service 配置文件  
filename:prod.exs NOT prod.secret.exs | Phoenix prod 配置文件  
filename:prod.secret.exs | Phoenix prod secret  
filename:configuration.php JConfig password | Joomla 配置文件  
filename:config.php dbpasswd | PHP应用程序数据库密码（例如，phpBB论坛软件）  
path:sites databases password | Drupal网站数据库凭据  
shodan_api_key language:python | Shodan API密钥  
filename:shadow path:etc | 包含新的unix系统的加密密码和帐户信息  
filename:passwd path:etc | 包含用户帐户信息，包括传统unix系统的加密密码  
extension:avastlic | 包含Avast的许可证密钥！  
extension:dbeaver-data-sources.xml | 包含MySQL凭据的DBeaver配置  
filename:.esmtprc password | esmtp 配置  
extension:json googleusercontent client_secret | 用于访问Google API的OAuth凭据  
HOMEBREW_GITHUB_API_TOKEN language:shell | Github令牌通常由homebrew用户设置  
xoxp OR xoxb | Slack bot 和 private tokens  
.mlab.com password | MLAB托管的MongoDB凭证  
filename:logins.json | Firefox保存密码集合（key3.db通常在同一个repo中）  
filename:CCCam.cfg | CCCam Server 配置文件  
msg nickserv identify filename:config | 可能的 IRC 登录密码  
filename:settings.py SECRET_KEY | Django密钥（通常允许会话劫持，RCE等）  
  
***参考来源：[github](https://github.com/UnkL4b/GitMiner)，FB小编secist编译，转载请注明来自FreeBuf.COM**

