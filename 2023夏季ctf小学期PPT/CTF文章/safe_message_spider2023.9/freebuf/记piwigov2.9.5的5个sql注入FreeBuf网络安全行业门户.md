**0x0 项目介绍**

项目地址：<https://github.com/Piwigo/Piwigo>

项目介绍：piwigo是用于网络的开源照相馆软件。 专为组织，团队和个人管理您的照片库而设计。

官网地址：piwigo.org

####  **0x1 准备工作**

Linux下下载<https://github.com/Piwigo/Piwigo/archive/2.9.5.zip>解压、赋权、进入目录后使用docker安装：

    
    
    docker run -d --name piwigo_mysql -e MYSQL_DATABASE=piwigo -e MYSQL_ROOT_PASSWORD=123456 mysql:5.7
    docker run -d -p 3000:80 -v $(pwd)/:/var/www/html/ --link piwigo_mysql:mysql --name piwigo nimmis/apache-php5
    

即可看到启动界面

####  **0x2 审计**

 **一 admin/group_perm.php中selection和parent参数存在的注入：**

selection值未经验证进入到move_categories函数中

![1.1.png](https://image.3001.net/images/20200115/1579053769_5e1e72c9a11f4.png!small)

追踪move_categories函数可以看到函数把该值分解后直接接入到sql语句中

![1.2.png](https://image.3001.net/images/20200115/1579053778_5e1e72d2ed3b0.png!small)

测试下即可发现漏洞存在

![1.3.png](https://image.3001.net/images/20200115/1579053788_5e1e72dc426a6.png!small)![image.png](https://image.3001.net/images/20200115/1579053833_5e1e73091aa77.png!small)

 **二 admin/group_list.php中group_selection参数存在的sql注入：**

图中可以看到group_selection值被放入到$groups中，selectAction值被放入到$action里

![2.1.png](https://image.3001.net/images/20200115/1579053859_5e1e73238f85c.png!small)

代码中$action对应多个动作，但是在多个动作里$group都被直接粘结到sql语句中，这儿我举delete方法看下：

![image.png](https://image.3001.net/images/20200115/1579053894_5e1e7346040fb.png!small)

这儿很直观看到被放进了sql语句中，试验下

![image.png](https://image.3001.net/images/20200115/1579053909_5e1e73552fa77.png!small)

 **三 admin/user_perm.php中cat_false参数存在的sql注入：**

图中可以看到cat_false被放入到函数中，

![image.png](https://image.3001.net/images/20200115/1579053941_5e1e737548486.png!small)

我们追踪下这个函数，在admin/include/functions.php中找到函数，$cat_false值变为$category经过判断是否是数组判断数量后被放入get_uppercat_ids函数中处理，

![image.png](https://image.3001.net/images/20200115/1579053953_5e1e7381a3c0a.png!small)

继续追踪get_uppercat_ids函数，上述存在漏洞的参数变为$cat_ids,图中可以看到该$cat_ids经过简单判断被放入sql语句并开始查询，

![image.png](https://image.3001.net/images/20200115/1579053963_5e1e738b07cfd.png!small)

这种漏洞函数跳转比较多，且没有明显的看到回显地方，这种场合特别适合时间注入，我们使用

`1 and
if(ascii(substr(database(),1,1))>97,1,sleep(5))`验证可以发现网页打开时间延迟，证明漏洞存在，使用sqlmap跑一波

![image.png](https://image.3001.net/images/20200115/1579053974_5e1e739668a5f.png!small)

![image.png](https://image.3001.net/images/20200115/1579053990_5e1e73a69eab3.png!small)

 **四 admin/group_perm.php存在的sql漏洞：**

这个漏洞跟上面三种admin/user_perm.php漏洞相同，调用的同一个函数，只是用户和组的区别，看张入口图意思一下：

![image.png](https://image.3001.net/images/20200115/1579054003_5e1e73b338fce.png!small)

sqlmap跑一下

![image.png](https://image.3001.net/images/20200115/1579054013_5e1e73bdc1af5.png!small)

![image.png](https://image.3001.net/images/20200115/1579054023_5e1e73c71f8db.png!small)

 **五 admin/batch_manager.php中filter_category参数存在的注入：** 我们看具体代码：

当post包中存在'filter_category_use'键时将'filter_category'值给xx['category']

![image.png](https://image.3001.net/images/20200115/1579054033_5e1e73d141d9a.png!small)

往下走，找到xx['category']被调用的地方，可以看到该值未被过滤直接被放到sql语句中。

需要注意的是这个请求链接在网页中并未找到，需要手工在post包添加`filter_category_use=on&filter_category=1`

![image.png](https://image.3001.net/images/20200115/1579054043_5e1e73dbec862.png!small)

sqlmap跑一下

![image.png](https://image.3001.net/images/20200115/1579054054_5e1e73e63a491.png!small)

![image.png](https://image.3001.net/images/20200115/1579054065_5e1e73f1300fe.png!small)

