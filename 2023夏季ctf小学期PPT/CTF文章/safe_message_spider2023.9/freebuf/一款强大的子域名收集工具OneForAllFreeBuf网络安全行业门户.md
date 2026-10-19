**搬运** 自项目地址：  
https://github.com/shmilylty/OneForAll

相比整理好多收藏网址去查子域名或者用字典去跑，这款工具是非常强大的

# 功能

![图片.png](https://image.3001.net/images/20210524/1621863415_60ababf7105453ff4985d.png!small)

# 子域名字典来源

![图片.png](https://image.3001.net/images/20210524/1621863527_60abac67a64628d216f35.png!small)

# 安装步骤

1.下载  
由于该项目处于开发中，会不断进行更新迭代，下载时请使用git
clone克隆最新代码仓库，也方便后续的更新，不推荐从Releases下载，因为Releases里版本更新缓慢，也不方便更新，
本项目已经在码云(Gitee)镜像了一份，国内推荐使用码云进行克隆比较快：

git clone https://gitee.com/shmilylty/OneForAll.git

或者：

git clone https://github.com/shmilylty/OneForAll.git

2.安装

cd OneForAll/

python3 -m pip install -U pip setuptools wheel -i
https://mirrors.aliyun.com/pypi/simple/

pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

python3 oneforall.py --help

3.更新

git stash # 暂存本地的修改  
git fetch --all # 拉取项目更新  
git pull # 下载覆盖  
git stash pop # 释放本地修改

# 使用

python3 oneforall.py --target example.com run  
python3 oneforall.py --targets ./example.txt run

我们以  
python3 oneforall.py --target example.com run  
命令为例  
![图片.png](https://image.3001.net/images/20210524/1621864101_60abaea5ade93e7f821c1.png!small)

![图片.png](https://image.3001.net/images/20210524/1621864134_60abaec6630d08436a949.png!small)

OneForAll在默认参数正常执行完毕会在results目录生成相应结果：

![图片.png](https://image.3001.net/images/20210524/1621863895_60abadd7291281dbc5236.png!small)  
example.com.csv是每个主域下的子域收集结果。

all_subdomain_result_1583034493.csv是每次运行OneForAll收集到子域的汇总结果，包含example.com.csv，方便在批量收集场景中获取全部结果。

result.sqlite3是存放每次运行OneForAll收集到子域的SQLite3结果数据库，其数据库结构如下图：

![图片.png](https://image.3001.net/images/20210524/1621863924_60abadf46b22f369d95ab.png!small)

其中类似example_com_origin_result表存放每个模块最初子域收集结果。

其中类似example_com_resolve_result表存放对子域进行解析后的结果。

其中类似example_com_last_result表存放上一次子域收集结果（需要收集两次以上才会生成）。

其中类似example_com_now_result表存放现在子域收集结果，一般情况关注这张表就可以了。

