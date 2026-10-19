# Sonar Qube环境搭建

![](./img/6071126089685534221.png)

## 安装

### docker-compose

使用docker搭建

    
    
    version: "3.1"
    services:
      db:
        image: postgres
        container_name: db
        ports:
          - 5432:5432
        networks:
          - sonarnet
        environment:
          POSTGRES_USER: sonar
          POSTGRES_PASSWORD: sonar
      sonarqube:
        image: sonarqube:8.9.3-community
        container_name: sonarqube
        depends_on:
          - db
        ports:
          - "9000:9000"
        networks:
          - sonarnet
        environment:
          SONAR_JDBC_URL: jdbc:postgresql://db:5432/sonar
          SONAR_JDBC_USERNAME: sonar
          SONAR_JDBC_PASSWORD: sonar
    networks:
      sonarnet:
        driver: bridge
    

直接docker-compose 启动会有报错

![](./img/2110281908326190241.png)

需要设置sysctl.conf文件信息  
设置vm.max_map_count

![](./img/5864111645593152750.png)

    
    
    vm.max_map_count=262144
    

并执行命令刷新

    
    
    Sysctl -p
    

重新启动需要一定时间启动，可以可以查看容器日志，看到如下内容代表启动成功

![](./img/8219859668856549842.png)

## 初始化

访问Sonar Qube首页

![](./img/685272736331876431.png)  
还需要重新设置一次密码

![](./img/7743333803352182105.png)

### 安装中文插件

![](./img/4055632644592282621.png)

安装成功后需要重启，安装失败重新点击install重装即可。  
安装成功后，会查看到重启按钮，点击即可

![](./img/9140558051356476689.png)  
重启后查看效果

![](./img/8853294441317331161.png)

# Sonar Qube基本使用

## Maven实现代码检测

本地需要有maven的环境  
![](./img/5438527913689153230.png)

在idea中也要配置好

![](./img/4793533069621891310.png)  
修改Maven的settings.xml文件配置Sonar Qube信息

    
    
    <profile>
        <id>sonar</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <sonar.login>admin</sonar.login>
            <sonar.password>123456789</sonar.password>
            <sonar.host.url>http://192.168.11.11:9000</sonar.host.url>
        </properties>
    </profile>
    

在当前项目终端(idea)位置执行命令：mvn sonar:sonar

![](./img/1797244857444424029.png)  
查看Sonar Qube界面检测结果

![](./img/2360148575912064269.png)

## Sonar-scanner实现代码检测

  * 下载Sonar-scanner：<https://binaries.sonarsource.com/?prefix=Distribution/sonar-scanner-cli/>
  * 下载最新版本即可，要求Linux版本
  * 解压并配置sonar服务端信息
    * 由于是zip压缩包，需要安装unzip解压插件
        
                apt install unzip
        

解压压缩包

        
                unzip sonar-scanner-cli-5.0.1.3006-linux.zip
        

配置sonarQube服务端地址，修改conf下的sonar-scanner.properties

![](./img/7247821292293372778.png)

生成令牌

![](./img/2241316960582130472.png)  
执行命令检测代码

    
    
    # 在项目所在目录执行以下命令
    /usr/local/docker/jenkins_docker/data/sonar-scanner/bin/sonar-scanner  -Dsonar.sources=./ -Dsonar.projectname=demo -Dsonar.projectKey=demo -Dsonar.java.binaries=target/ -Dsonar.login=[填在sonar中生成的令牌]
    

![](./img/7486975427985027567.png)

![](./img/4541326194186025920.png)  
查看SonarQube界面检测结果

![](./img/2469605409849817232.png)

# Jenkins集成Sonar Qube

Jenkins继承Sonar Qube实现代码扫描需要先下载整合插件

## Jenkins安装插件

![](./img/8707133848207311728.png)

![](./img/1166032851050215649.png)

![](./img/2494259096284692600.png)

## Jenkins配置Sonar Qube

开启Sonar Qube权限验证

![](./img/1820556311581105720.png)  
获取Sonar Qube的令牌

![](./img/7067560886506595389.png)

配置Jenkins的Sonar Qube信息

![](./img/8303565126295135810.png)

![](./img/3033532804866033137.png)

![](./img/6607081271451728440.png)

![](./img/8471924464691014715.png)

## 配置Sonar-scanner

将Sonar-scaner添加到Jenkins数据卷中并配置全局配置

![](./img/8365160230227490174.png)

配置任务的Sonar-scanner

![](./img/6778012018388621959.png)

    
    
    -Dsonar.projectname=${JOB_NAME}
    -Dsonar.projectKey=${JOB_NAME}
    -Dsonar.source=./
    -Dsonar.java.binaries=target/
    -X
    

## 构建任务

记得给工作目录加权 不然会提示`Unable to create root temp directory
/var/jenkins_home/workspace/mytest/.scannerwork/.sonartmp`

    
    
    Chmod 777 -R /usr/local/docker/jenkins_docker/data/workspace/
    

![](./img/3796490249942631380.png)

