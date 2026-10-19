**近日看到一些关于工具的文章，很多人对于写工具类文章都是蜻蜓点水，写搭建，写基础使用，但是基础的开源工具在生产环境上的使用其实是比较困难的，有很多需要二次开发做到与生产环境适配，今天写这篇文章的目的就在于开启开源工具二次开发的思路，其中一个模块的二次开发很简单，大家基本都能看懂，就以这篇简单易懂的代码改动举例。本次开源工具二次开发以cobra代码审计为例。  
**

> 适用范围：代码初学者、有一定python基础与协议基础

## 需求明确

首先要先明确自己的需求，我们的需求是在上线前做关联性代码审计，我采用的是cobra，至于为什么要使用cobra就不多说了，这是评估期间做的事情，文章主要写二次开发。

## 显示情况

我们的生产环境使用gitlab作为代码库，仅允许ssh方式下拉代码，而不允许http公开拉代码，这么做是为了安全，但是同样的也对cobra的使用造成了一定的麻烦。因为基础的cobra是没有ssh下拉功能的，需要我们自己做二次开发

## 代码改动

首先在原基础的cobra上我们做一个拉代码的测试

![](https://image.3001.net/images/20191113/1573628767_5dcbab5fb7226.png!small)

好像很叼的样子，没有漏洞，但是有层script提示没有选择目标

![](https://image.3001.net/images/20191113/1573628892_5dcbabdc684da.png!small)

后台定位问题发现如下错误

![](https://image.3001.net/images/20191113/1573628906_5dcbabea700ed.png!small)

一般出现这个问题不是分支错误就是路径错误，反正是找不到文件的，那直接用git clone试试原路径是否存在吧

![](https://image.3001.net/images/20191113/1573628919_5dcbabf7ba954.png!small)

500，询问了gitlab负责人才知道是根本没有开放http下拉代码的功能，统一使用ssh进行下拉。

那原基础的cobra能直接用ssh拉代码吗？试试看好了

![](https://image.3001.net/images/20191113/1573628932_5dcbac04789a7.png!small)

提示请输入URL，也就是输入格式不对，那我们换一种方式输入

![](https://image.3001.net/images/20191113/1573628957_5dcbac1dc899e.png!small)

还是一样的提示，那看看后端是什么情况吧

![](https://image.3001.net/images/20191113/1573628971_5dcbac2b1ea80.png!small)

一切正常。

首先对问题进行定位

![](https://image.3001.net/images/20191113/1573628984_5dcbac38b267c.png!small)

命令为find ./ -name “*.py”|xargs grep “Please input a valid URL”

命令意思为在本级目录级下级目录搜索内容为Please input a valid URL的py脚本

找到了api.py，让我们进去看看这是什么

![](https://image.3001.net/images/20191113/1573629003_5dcbac4b2e70c.png!small)

果然只限定了http与https，那根据咱们的需求加上ssh吧

原代码：

    
    
      if re.match(r'http://|https://', t):
    
                        arg = (t, formatter, output, rule, a_sid, is_del)
    
                        producer(task=arg)
    
                    else:
    
                        return {"code": 1004, "msg": "Please input a valid URL"}
    
                result = {
    
                    'msg': 'Add scan job successfully.',
    
                    'sid': a_sid,
    
                    'total_target_num': len(target),
    
                }
    
            else:
    
                if re.match(r'http://|https://', target):
    
                    arg = (target, formatter, output, rule, a_sid, is_del)
    
                    producer(task=arg)
    
                else:
    
                    return {"code": 1004, "msg": "Please input a valid URL"}

改动后代码：

    
    
        if re.match(r'http://|https://|ssh://', t):
    
                        arg = (t, formatter, output, rule, a_sid, is_del)
    
                        producer(task=arg)
    
                    else:
    
                        return {"code": 1004, "msg": "Please input a valid URL"}
    
                result = {
    
                    'msg': 'Add scan job successfully.',
    
                    'sid': a_sid,
    
                    'total_target_num': len(target),
    
                }
    
            else:
    
                if re.match(r'http://|https://|ssh://', target):
    
                    arg = (target, formatter, output, rule, a_sid, is_del)
    
                    producer(task=arg)
    
                else:
    
                    return {"code": 1004, "msg": "Please input a valid URL"}

重新试一下吧

![](https://image.3001.net/images/20191113/1573629057_5dcbac81ddf17.png!small)

后台提示需要输入root密码

![](https://image.3001.net/images/20191113/1573629077_5dcbac95e0614.png!small)

我的环境是做了git@code.xxx的免密推送，root用户密码我不知道啊，就算有权限难道把密码写在配置文件里又安全吗？明文密码泄露的事情可是发生不少，于是继续看代码找问题

    
    
    find ./ -name "*.py" |xargs grep "git clone"

看他的推送方式是什么

配置文件为./cobra/pickup.py

![](https://image.3001.net/images/20191113/1573629094_5dcbaca699da5.png!small)

如果配置文件中没有输入用户名或密码，便是公开链接，直接clone，如果有用户名密码，则分割填入用户名和密码进行加密clone，如果这放在http协议中这个逻辑完全没有问题，但是放在ssh下拉代码里，就会存在很大的逻辑问题了

逻辑问题在于ssh的免密钥登录不需要密码，如果单纯以用户名密码作为判断依据那免密钥的作用就为零了，为了适配免密钥，实际上在代码中指定免密钥的用户即可，同时为保证其他基础功能不遭受破坏，增加的功能应使用判断前缀的方式进行代码改写，具体如下：

![](https://image.3001.net/images/20191113/1573629126_5dcbacc625f6f.png!small)

原代码：

    
    
             if self.repo_username is None or self.repo_password is None:
    
                # public repo
    
                clone_address = self.repo_address
    
            else:
    
                # private repo
    
                clone_address = self.repo_address.split('://')[0] + '://' + quote(self.repo_username) + ':' + \
    
                                quote(self.repo_password) + '@' + self.repo_address.split('://')[1]
    
            # clone repo with username and password
    
            
    
            # "http[s]://username:password@gitlab.com/username/reponame"
    
            # !!! if add password in the url, .git/config will log your url with password
    
            cmd = 'git clone ' + clone_address + ' "' + self.repo_directory + '" -b ' + self.repo_branch

改后代码：

    
    
         if self.repo_username is None or self.repo_password is None:
    
                # public repo
    
                if (self.repo_address.split('://')[0] == 'ssh'):
    
                    clone_address = 'ssh://' + 'git@' + \
    
                    self.repo_address.split('://')[1]
    
                else:
    
                clone_address = self.repo_address
    
            else:
    
                # private repo
    
                if (self.repo_address.split('://')[0] == 'ssh'):
    
                    clone_address = 'ssh://' + 'git@' + \
    
                    self.repo_address.split('://')[1]
    
                else:
    
                clone_address = self.repo_address.split('://')[0] + '://' + quote(self.repo_username) + ':' + \
    
                                quote(self.repo_password) + '@' + self.repo_address.split('://')[1]
    
            # clone repo with username and password
    
            # "http[s]://username:password@gitlab.com/username/reponame"
    
            # !!! if add password in the url, .git/config will log your url with password
    
            cmd = 'git clone ' + clone_address + ' "' + self.repo_directory + '" -b ' + self.repo_branch

增加前缀判断，如果前缀为ssh，则统一使用通用用户git进行ssh登录代码拉取

## 进行测试

![](https://image.3001.net/images/20191113/1573629158_5dcbace620fd9.png!small)

![](https://image.3001.net/images/20191113/1573629175_5dcbacf73ff57.png!small)

如此完成了一次很简单的模块二次开发。

二次开发重要是需求与实现，将自己的需求完整的实现出来即可，不一定是框架意义上的开发才算二次开发，一定要明白自己需要的是什么，代码逻辑是什么，掌握好代码逻辑，二次开发也不算是很难的事情。

 ***本文原创作者：煜阳yuyang，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

