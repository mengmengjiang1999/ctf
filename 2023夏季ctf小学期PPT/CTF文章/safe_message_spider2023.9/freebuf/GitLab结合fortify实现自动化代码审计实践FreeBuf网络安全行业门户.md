## 一、背景

在甲方做安全的同学可能会有一项代码审计的工作，通常需要从gitlab把代码拉取下来，然后使用代码审计工具进行扫描，然后对结果进行人工确认；

在这个流程中需要做的事情比较繁琐，比如说gitlab如何配置token、如何自动化把代码拉取到本地、如何调用fortify实现批量扫描等诸多繁琐问题。

本篇文章以甲方安全代码安全建设为主线，分享如何让代码审计工具自动化扫描gitlab仓库里的代码。并且提供了一个便捷的实验环境供大家测试。

>
> 本文实验中调用了多款代码审计工具（包含semgrep、fortify、墨菲、河马，其中fortify软件属于商业性质，本文章无法提供该软件，如需自备此软件并存放在主机/data/share/fortify目录），完成试验后可以看到各代码审计工具的效果对比。

## 二、准备环境

为了方便大家，我把我的实验gitlab地址直接共享出来，大家可以优先使用此共享环境。

    
    
    URL：http://123.249.6.139:1880/
    用户名：root
    密码：qingtingtest
    token：glpat-SMsSWy6xzB4x8B6rFryB
    

### 配置gitlab环境

为了真实模拟fortify扫描gitlab仓库的代码，我需要快速搭建一个gitlab仓库，这里实验docker的方式最为简单，只需要执行以下的命令

    
    
    docker run --detach --hostname gitlab.thinkpad --publish 8443:443 --publish 880:80 --publish 222:22 --name gitlab --restart always --volume /data/gitlab/config:/etc/gitlab --volume /data/gitlab/logs:/var/log/gitlab --volume /data/gitlab/data:/var/opt/gitlab gitlab/gitlab-ce
    

命令执行之后，docker会自动拉取docker镜像，并创建一个gitlab的容器，服务启动之后会随机生成一个root用户的密码，可以通过以下命令查看root用户的初始化密码

    
    
    docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
    

命令执行之后，可以在终端中看到如下所示密码

    
    
    Password: UnSoOs7l8YN6dYDQRP/1/dzpKswF7dq7fpyhKBey95A=
    

现在可以使用浏览器访问gitlab的页面，访问地址是`http://x.x.x.x:880/`，然后浏览器会自动跳转到登录页面，如下图所示  
![](https://image.3001.net/images/20221208/1670492812_6391b28c0d13956b3bb54.png!small)

在登录页面，我们在用户名处输入root，密码处输入刚才得到的密码；登录成功之后会自动跳转到工作台的首页，如下图所示。  
![](https://image.3001.net/images/20221208/1670492815_6391b28fae6b67bdcbd7b.png!small)

### 创建API访问的token

为了让fortify能够访问到gitlab仓库的代码，我们需要创建一个token，用于API访问；在头像位置展开下拉菜单，选择preferences->Access
Tokens ,填下相关参数，界面如下所示  
![](https://image.3001.net/images/20221208/1670492816_6391b290941d8fed69cb0.png!small)

创建完成，把生成的token复制出来，后续要用到  
![](https://image.3001.net/images/20221208/1670492817_6391b291c729afc18d9a7.png!small)

    
    
    glpat-ggjo6Z6aQXWCZ2FNJcsz
    

gitlab搭建完后，默认里面有一个空项目，fortify无法扫除有价值的漏洞，为了方便测试，需要在新建项目的位置导入项目进去，打开URL地址  
`http://10.1.1.140:880/projects/new#import_project`,然后选择`Repository by
URL`，然后填入一个可以被拉取的仓库地址，这里我提供一个供大家实验，如下图所示

    
    
    https://gitee.com/songboy/QingScan
    

![](https://image.3001.net/images/20221208/1670492818_6391b29259eb05178125b.png!small)

导入项目之后，gitlab会自动拉取代码到服务器，如下图所示  
![](https://image.3001.net/images/20221208/1670492818_6391b292f372ffecc45cc.png!small)

## 三、配置参数

现在已经有了gitlab的实验环境，可以正式开始做实验，首先打开蜻蜓的市场页面，URL地址如下

    
    
    http://qingting.starcross.cn/scenario/store
    

可能会提示要求登录，如果是首次进入蜻蜓安全控制台，扫描登录之后会自动注册

然后需要在服务器执行添加节点的shell命令，按照提示进行操作即可，如下图所示  
![](https://image.3001.net/images/20221208/1670492819_6391b293acecf55651f65.png!small)

现在回到市场页面，找到快速挖掘0day漏洞，在下方有个按钮，添加到工作流，如下图所示  
![](https://image.3001.net/images/20221208/1670492820_6391b29455679facf9f93.png!small)

添加到工作流之后，会看到工作流的信息，这里可以把gitlab的配置信息填写进去，需要点击进入编排流程，如下图所示  
![](https://image.3001.net/images/20221208/1670492821_6391b2952d2f6cfc6b4cf.png!small)

在编排工作流页面，上方有一个设置全局变量的小图标,按照提示配置必要参数，如下图所示  
![](https://image.3001.net/images/20221208/1670492822_6391b29611b75943f8e6b.png!small)

## 四、运行程序

运行全局变量完成之后，可以右键点击第一个节点，再次点估运行选项，就可以运行这个工作流，运行过程中节点状态会发生变化  
![](https://image.3001.net/images/20221208/1670492822_6391b296ae9cf92d3d55b.png!small)

节点会按照自上而下运行，运行过程中状态图标会一直旋转，当运行完成时，可以看到成功的小图标  
![](https://image.3001.net/images/20221208/1670492823_6391b2972fa42732efdaf.png!small)

运行完成之后，可以去数据中心查看运行结果，可以根据节点和任务ID等方式筛选，如下图所示  
![](https://image.3001.net/images/20221208/1670492824_6391b2982e15453333d43.png!small)

我选中fortify代码扫描节点，筛选出来的列表页面如下所示  
![](https://image.3001.net/images/20221208/1670492824_6391b2989cb560f14bdc8.png!small)

在列表页面只展示了一小部分数据，可以点击查看按钮，在详情页查看详细的漏洞信息，用于审计标注，如下图所示。  
![](https://image.3001.net/images/20221208/1670492825_6391b2999be3d65dbd934.png!small)

上面节点的代码已经在GitHub中开源，有需要的小伙伴也可以在GitHub

    
    
    https://github.com/StarCrossPortal/QingTing
    

GitHub地址：https://github.com/StarCrossPortal/QingTing

