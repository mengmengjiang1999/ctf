## 一、背景

前段时间在做代码审计，发现很多项目都存在安全隐患，大多数是来自于参数未过滤所造成的；为了解决这个问题，我将[Web安全开发规范手册V1.0](https://segmentfault.com/a/1190000017090860)进行了培训，但是效果并不是太理想，原因是培训后开发者的关注点主要在功能完成度上，安全编码对于他们来说并不是核心指标；

为了能让开发者时时刻刻关注安全问题，我在gitlab服务端放了一个钩子，这个钩子主要是将本次提交的代码文件进行了检测，遇到可能存在安全风险的问题将其输出出来，这样开发者能够对培训的内容有更深的感受，更注重编码时候的安全问题。

## 二、操作步骤

1.搭建环境

2.创建项目

3.创建钩子

4.钩子实验

## 三、搭建环境

### 3.1 安装gitlab

在正式部署到服务器之前，我需要在本地搭建一个gitlab服务，用于钩子的开发和测试，这里我用docker搭建速度比较快，执行的命令如下

    
    
    docker run --detach  --publish 443:443 --publish 80:80  --name gitlab --restart always  gitlab/gitlab-ce
    

命令执行之后，返回的信息如下所示

![](https://image.3001.net/images/20210603/1622710213_60b897c5e7e6fdfdf4072.png!small)

在上图中可以看到容器已经运行成功，使用浏览器访问gitlab的地址

    
    
    http://127.0.0.1
    

访问之后需要设置一个管理员的密码，如下图所示

![](https://image.3001.net/images/20210603/1622710214_60b897c69e3a020b9ed0a.png!small)

填写密码之后，确认修改密码，会跳转到gitlab的主页，如下图所示  
![](https://image.3001.net/images/20210603/1622710215_60b897c74afcef326aada.png!small)

这gitlab中创建一个项目用于钩子测试，如下图所示  
![](https://image.3001.net/images/20210603/1622710215_60b897c7e145de9b8552c.png!small)

创建项目成功之后，注意留意页面中的`Project
ID:2`,把这个`2`记录一下，后续会使用到；接下来需要开始钩子的开发和部署，钩子可以使用各种语言开发，这里我比较熟悉php，因此采用php开发。

### 3.2 安装依赖

gitlab的容器默认不支持php语言，需要先安装php，安装命令如下所示

    
    
    apt update -y && apt install php -y
    
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710216_60b897c88a677eed737ae.png!small)

在上图中可以看到php已经安装成功，为了验证php命令是否可以运行，这里我使用如下命令进行验证

    
    
    php -v
    

命令执行之后，返回的信息如下所示

![](https://image.3001.net/images/20210603/1622710216_60b897c8e78efbb86e8cc.png!small)

在上图中可以看到php的版本是7.4.3 ，说明php已经安装成功。

### 3.3 安装semgrep

钩子程序中需要调用semgrep，这个程序gitlab中也没有安装，需要安装一下，这里采用pip安装，不过需要先升级pip的版本才行，升级的命令如下所示

    
    
    pip3 install --upgrade pip
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710218_60b897ca87bdb778a9c47.png!small)  
在上图中可以看到pip的版本已经升级到21.1.2,说明升级成功了

semgrep还依赖setuptools模块，需要用pip先升级一下，升级的命令如下所示

    
    
    pip3 install --upgrade setuptools
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710218_60b897cae25632525aa7c.png!small)在上图中可以看到setuptools模块已经升级成功

接下来就可以正式安装semgrep了，安装的命令如下所示

    
    
    cd /usr/local/bin/ && python3 -m pip install semgrep
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710219_60b897cb7a83396233d7b.png!small)

在上图中可以看到semgrep已经安装完成，这里我需要再次使用semgrep命令来验证一下，执行的命令如下所示

    
    
    semgrep --version
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710219_60b897cbec49654f8be7b.png!small)  
在上图中可以看到semgrep的版本信息为0.52.0，确认安装成功了。

### 3.4 查看hash

现在我们需要在刚才创建的项目中添加钩子，这里需要找到项目的存放路径，在项目页中

    
    
    echo -n 2 | sha256sum
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710220_60b897cc5cf8a33974015.png!small)

    
    
    find / -iname d4
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710220_60b897ccc9f7825b6ce30.png!small)在上图中可以看到项目存放的位置，返回了两个路径，这两个路径其中有一个是软连接，通过`cd`命令进入进入项目的存放位置

    
    
    cd /var/opt/gitlab/git-data/repositories/@hashed/d4
    

命令执行之后，再次执行`ls`命令，得到的信息如下所示  
![](https://image.3001.net/images/20210603/1622710221_60b897cd369d823bb3434.png!small)

在上图中可以看到有一个73的文件夹，这是gitlab的命名规则，进入此文件夹，命令如下所示

    
    
    cd 73/d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35.git/
    

命令执行之后，返回的信息如下所示  
![](https://image.3001.net/images/20210603/1622710221_60b897cdbc3f21210a92f.png!small)

在上图中可以看到此项目的所有文件，我需要在这个位置开发钩子文件

## 四、创建钩子

自定义钩子需要存放在`custom_hooks`目录下，默认没有此文件夹所以需要创建此文件夹，执行命令如下所示

    
    
    mkdir custom_hooks  && cd custom_hooks
    

### 4.1 新建钩子

创建`custom_hooks`文件夹并进入之后，使用vim创建一个钩子文件，命令如下所示

    
    
    vim  pre-receive
    

进入vim编辑器界面之后，将如下钩子代码添加进去，代码如下所示

    
    
    #!/usr/bin/php
    <?php
    
    
    fwrite(STDOUT, 'please input:');
    list($oldVer, $newVer, $ref_name) = explode(" ", fgets(STDIN));
    
    //ob_start();
    $cmd = "git diff --name-only  {$oldVer}..{$newVer}";
    echo $cmd . PHP_EOL;
    exec($cmd, $result);
    
    $rand = date("Y-m-d-H-i-s");
    $baseDir = "/tmp/11/$rand/";
    $ruleFile = "/semgrep-rule.yaml";
    
    
    
    
    foreach ($result as $value) {
        if (strstr($value, ".php") !== false) {
            $randName = $baseDir . $value;
            if (!is_dir(dirname($randName))) {
    #        if (file_exists($randName) == false) {
                mkdir(dirname($randName), 0777, true);
            }
            $cmd = "git show {$newVer}:$value > $randName";
    
    #        echo $cmd . PHP_EOL;
    
    
            exec($cmd, $result);
        }
    }
    
    
    $cmd = "/opt/gitlab/embedded/bin/semgrep  -f '$ruleFile' $baseDir  -o /tmp/11.txt";
    
    exec($cmd, $result);
    
    
    //ob_clean();
    
    
    $notice = file_get_contents("/tmp/11.txt");
    echo $notice . PHP_EOL;
    
    
    file_put_contents("/tmp/11.txt", "");
    exec("rm -rf $baseDir");
    
    echo 0;
    

保存并推出此钩子文件，接着需要给自定义钩子目录设置权限，这里我简单粗暴的把权限设置为777，命令如下所示

    
    
    chmod -R 777 ../
    

权限设置好之后，我还需要创建一个`semgrep`的扫描规则文件，用于判断代码是否正确。

执行的命令如下所示

    
    
    vim /semgrep-rule.yaml 
    

进入vim编辑器之后，需要将如下规则内容复制进去

    
    
    rules:
      - id: assert-use
        patterns:
          - pattern: assert($ASSERT, ...);
          # - pattern-not: assert(<... $ASSERT ...>, ...); - https://github.com/returntocorp/semgrep/issues/2035
          - pattern-not: assert("...", ...);
        message: |
          使用用户输入调用assert等价于eval'。
        metadata:
          references:
            - https://www.php.net/manual/en/function.assert
            - https://github.com/FloeDesignTechnologies/phpcs-security-audit/blob/master/Security/Sniffs/BadFunctions/AssertsSniff.php
        languages: [ php ]
        severity: ERROR
    
      - id: backticks-use
        pattern: '`...`;'
        message: |
          使用反勾号可能导致命令注入漏洞。
        metadata:
          references:
            - https://www.php.net/manual/en/language.operators.execution.php
            - https://github.com/FloeDesignTechnologies/phpcs-security-audit/blob/master/Security/Sniffs/BadFunctions/BackticksSniff.php
        languages: [ php ]
        severity: ERROR
    

保存并推出规则文件后，需要修改此规则文件的权限，这里我以777权限距离，命令如下所示

    
    
    chmod 777 /semgrep-rule.yaml
    

设置完规则文件权限之后，还有两个缓存地方需要设置权限，否则会在运行过程当中报错，首先是semgrep的缓存文件，设置权限命令如下

    
    
    mkdir -p /var/opt/gitlab/.cache  && chmod -R 777 /var/opt/gitlab/.cache
    

另外一处是钩子本身的缓存文件，同样需要设置权限，执行的命令如下所示

    
    
    echo '' > /tmp/11.txt  && chmod 777 /tmp/11.txt
    

### 4.2 测试钩子

现在可以正式测试钩子的可用性，首先需要拉取刚才创建的项目代码，命令如下所示

    
    
    git clone http://127.0.0.1/root/test.git
    

执行命令之后，返回的信息如下所示

![](https://image.3001.net/images/20210603/1622710223_60b897cf4925517473a0e.png!small)

在上图中可以看到项目已经拉取下来，接下来我需要编辑一个php文件，命令如下所示

    
    
    vim index.php
    

命令执行完毕之后，将测试的代码存放进去

    
    
    <?php
    
    phpinfo();
    
    
    $cmd = "ls {$_GET['x']}";
    
    exec($cmd);
    

保存并退出之后，将代码提交到gitlab中去，命令如下所示

    
    
    echo ' ' >> index.php && git add . && git commit . -m 'init' && git push
    

但git往gitlab服务器推送之后，gitlab就会调用钩子，并将钩子返回的信息输出出来，如下图所示

![](https://image.3001.net/images/20210603/1622710223_60b897cfde1202fa9188f.png!small)

在上图中可以看到钩子提示了`index.php`文件第8行不安全，此致整个部署完毕。

作者：汤青松

微信：songboy8888

