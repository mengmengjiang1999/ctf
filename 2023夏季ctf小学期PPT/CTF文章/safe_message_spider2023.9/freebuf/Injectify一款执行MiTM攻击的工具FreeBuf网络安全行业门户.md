**今天给大家介绍一款功能强大的高级中间人攻击工具，该工具名叫Injectify，而这款工具将可以帮助我们轻松地对目标网站进行渗透测试。**

![a.png](https://image.3001.net/images/20180224/15194545383706.png!small)

Injectify是一款基于现代Web开发的中间人攻击工具，该工具跟BeEF的功能类似，并且能够在多种客户端平台运行（Web端、桌面端、或浏览器插件）。

## 功能介绍

> 1\. 在目标用户跟攻击者之间创建一个反向JavaScript Shell。
>
> 2\. 记录目标用户的键盘信息并将其存储在数据库中。
>
> 3\.
> 从浏览器中提取出[已保存的密码](https://twitter.com/thesamdd/status/947251299262836741)；

### 项目地址

【[GitHub主页](https://github.com/samdenty99/injectify)】

【[官网传送门](https://injectify.js.org/)】

## 工具安装

注：完整的使用文档目前正在开发中，敬请期待…【[官方文档](https://injectify.js.org/getting-started/installation/mongodb/)】

### 创建一个MongoDB数据库

【选项1】创建一个mLab数据库：

1\. 访问mLab网站【[传送门](https://mlab.com/signup/)】并创建一个账号

2\. 点击右上角的“Create new”按钮

3\. 选择“Sandbox”，然后点击“Continue”

![b.png](https://image.3001.net/images/20180224/15194545629430.png!small)

4\. 选择相应的地区，然后点击“Continue”

5\. 输入数据库名称-injectify，点击“Continue”，然后提交表单

6\. 选择你刚刚创建的数据库，点击“User”，然后选择“Add database user”

![c.png](https://image.3001.net/images/20180224/15194545701871.png!small)

7\. 输入用户名和密码，然后点击“Create”（不要勾选read-only）

【选项2】设置专用的MongoDB数据

文档正在制作中…

### 创建一个GitHub应用

1\. 访问GitHub.com并创建一个账号（如果已有账号请忽略）

2\. 创建一个新的GitHub应用，然后设置以下值：

![d.png](https://image.3001.net/images/20180224/15194545885821.png!small)

![e.png](https://image.3001.net/images/20180224/15194546023029.png!small)

## 项目配置

> 1\. [克隆代码库](https://injectify.js.org/getting-> started/installation/git@github.com:samdenty99/injectify.git)；
>
> 2\. 进入repo，然后把server.config.example.js复制到项目中并改名为server.config.js；
>
> 3\. 在文本编辑器中打开server.config.js；
>
> 4\. 将新创建的应用信息替换掉GitHub中的client_id和client_secret值；

![f.png](https://image.3001.net/images/20180224/1519454618897.png!small)

![g.png](https://image.3001.net/images/20180224/15194546266285.png!small)

5\. 用新建的mLab URL（或专用MongoDB数据库的URL）替换mongodb值：

    
    
    mongodb://<dbuser>:<dbpassword>@XXXX.mlab.com:XXXX/injectify

![h.png](https://image.3001.net/images/20180224/15194546622577.png!small)

![i.png](https://image.3001.net/images/20180224/1519454669177.png!small)

## 设置服务器

要求：

> 1\. 按照下列步骤操作；
>
> 2\. NodeJS
>
> 3\. Yarn数据包管理器；
>
> 4\. （可选项）[swap文件](https://unix.stackexchange.com/a/295852/216455)；

## 安装

Windows

    
    
    npm i-g yarn
    yarn global add typescript
    yarn global add pm2
    yarn run install:all
    yarn run deploy  
    

Linux

    
    
    sudo npm i -g yarn
    sudo yarn global add typescript
    sudo yarn global add pm2
    yarn run install:all
    yarn run deploy  
    

## 操作演示

标签页

![j.png](https://image.3001.net/images/20180224/15194547412864.png!small)

实时更新

![k.png](https://image.3001.net/images/20180224/15194547502356.png!small)

终端复制

![l.png](https://image.3001.net/images/20180224/1519454759280.png!small)

终端数据类型

![m.png](https://image.3001.net/images/20180224/15194547692913.png!small)

模块智能感知

![n.png](https://image.3001.net/images/20180224/15194547836900.png!small)

编辑器智能感知

![o.png](https://image.3001.net/images/20180224/15194547927822.png!small)

更多演示样例，请参考Injectify官方文档：【[传送门](https://injectify.js.org/demos/interface/)】

 ***
参考来源：[injectify](https://github.com/samdenty99/injectify)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

