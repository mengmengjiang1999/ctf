## [x-patrol](https://github.com/MiSecurity/x-patrol)

docker安装

    
    
    #dockerfile
    FROM ubuntu:14.04
    
    ENV GOAPTH /opt/go
    
    RUN apt update -y
    RUN apt install -y wget golang mysql-server git 
    RUN cd /opt && git clone https://github.com/MiSecurity/x-patrol.git && cd x-patrol && wget https://github.com/MiSecurity/x-patrol/releases/download/0.3/x-patrol_linux_amd64
    RUN service mysql start && mysql -e "create database xsec;GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;use mysql;UPDATE user SET Password=PASSWORD('123456') WHERE User='root' AND Host='localhost';flush privileges;"
    RUN mv /opt/x-patrol /opt/x && mv /opt/x/x-patrol_linux_amd64 /opt/x/run && chmod +x /opt/x/run
    COPY app.ini /opt/x/conf/app.ini
    
    ENTRYPOINT service mysql start && cd  /opt/x/ && ./run web
    
    
    #app.ini
    HTTP_HOST = 0.0.0.0
    HTTP_PORT = 8000
    MAX_INDEXERS = 2
    DEBUG_MODE = true
    REPO_PATH = repos
    MAX_Concurrency_REPOS = 1
    
    [database]
    ;support sqlite3, mysql, postgres
    DB_TYPE = mysql
    HOST = 127.0.0.1
    PORT = 3306
    NAME = xsec
    USER = root
    PASSWD =123456 
    SSL_MODE = disable
    PATH = data
    

按照别人的[教程](https://www.yuque.com/mangguobing-shgcx/pmmi6a/eu99no)，无法检测。

![image.png](https://image.3001.net/images/20191130/1575111390_5de24ade19d86.png!small)![image.png](https://image.3001.net/images/20191130/1575111582_5de24b9e3b51e.png!small)![image.png](https://image.3001.net/images/20191130/1575111602_5de24bb20d257.png!small)

## [Hawkeye](https://github.com/0xbug/Hawkeye)

docker启动

    
    
    docker run -ti -p 80:80 -e MONGODB_URI=mongodb://ip:27017 -it hawkeye  
    

![image.png](https://image.3001.net/images/20191130/1575115206_5de259c6b4a98.png!small)启动成功

![image.png](https://image.3001.net/images/20191130/1575115337_5de25a49825a6.png!small)

添加监控项  
![image.png](https://image.3001.net/images/20191130/1575115571_5de25b33ec923.png!small)  

<https://github.com/FeeiCN/GSIL>  

<https://github.com/dongfangyuxiao/github_dis>  

<https://github.com/az0ne/Github_Nuggests>  

<https://github.com/shakenetwork/gitrob>  

<https://github.com/hillsbird/githubscan>  

<https://github.com/sry309/githubmonitoring>  

<https://github.com/riiyn/GithubHunter>  

