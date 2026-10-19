> 目的：解决burpsuite、冰蝎、c2、finalshell等的环境。

## 一、资源准备

### （一）进入[甲骨文官网](https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html)下载jdk

![image](https://image.3001.net/images/20210407/1617765797_606d25a5c5297918e1d55.png!small)![image](https://image.3001.net/images/20210407/1617765827_606d25c3d2c3e53b37901.png!small)首次登录需要注册一个用户  
![image](https://image.3001.net/images/20210407/1617765890_606d26020f9d6d32a1f59.png!small)![image](https://image.3001.net/images/20210407/1617765901_606d260dc2cf3ec1398d4.png!small)

## 二、安装（我这里安装的是D盘）

### （一）首先创建java文件夹，子文件夹为jdk和jre，tree示意如下(c盘空间大的同志请随意)

###
![image](https://image.3001.net/images/20210407/1617765934_606d262ef1d15b3da9b88.png!small)（二）安装

![image](https://image.3001.net/images/20210407/1617765961_606d2649913957c7932f9.png!small)![image](https://image.3001.net/images/20210407/1617765977_606d2659748272593b30b.png!small)  
![image](https://image.3001.net/images/20210407/1617765987_606d266301dc9c7eca7a2.png!small)![image](https://image.3001.net/images/20210407/1617765997_606d266d468c414aa9e2d.png!small)  
![image](https://image.3001.net/images/20210407/1617766012_606d267c297027f2da2a4.png!small)安装完成

## 三、设置环境变量

### （一）设置——搜索高级系统设置——环境变量

![image](https://image.3001.net/images/20210407/1617766037_606d26950a4df17aa0e7e.png!small)

    
    
    0x01.设置环境变量（用户变量）[win7系统的变量值为：%JAVA_HOME%\bin;%JAVA_HOME%\jre\bin;]
    
    变量名 Path:
    %JAVA_HOME%\bin
    %JAVA_HOME%\jre\bin
    

![image](https://image.3001.net/images/20210407/1617766188_606d272cc6ff7d945626c.png!small)

    
    
    0x02.系统变量(此处的JAVA_HOME变量为jdk路径,默认C盘的为C:\Program Files\Java\jdk1.8.0_241)
    
    新增CLASSPATH:
    .;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar;
    新增JAVA_HOME:
    D:\java\jdk\
    

![image](https://image.3001.net/images/20210407/1617766217_606d2749b19157d3394bf.png!small)![image](https://image.3001.net/images/20210407/1617766226_606d275290e8a57b33535.png!small)

## 四、检查环境的安装

### （一）javac

###
![image](https://image.3001.net/images/20210407/1617766250_606d276a1c372cb069cad.png!small)（二）java

![image](https://image.3001.net/images/20210407/1617766258_606d27722b8f6c6be1344.png!small)（三）java
-version  
![image](https://image.3001.net/images/20210407/1617766269_606d277dee31e8d024fb3.png!small)即为安装好并配置成功

## 五、linux环境

    
    
    yum源：
    
    yum -y install java-1.8.0-openjdk*
    
    apt源：
    
    sudo apt install default-jre
    
    sudo apt install default-jdk
    
    
    
    检验：（同上）javac / java / java -version
    无报错均可
    

