![](https://image.3001.net/images/20210925/1632499759_614df82f7e9c0a565cc48.jpg!small)

## 关于FisherMan

FisherMan是一款功能强大的社交媒体信息收集工具，FisherMan基于Selenium实现其功能，

可以帮助广大研究人员利用Selenium来收集Facebook用户的个人资料信息。

## 工具安装

FisherMan基于Python开发，因此我们需要在本地设备上安装并配置好Python环境。

接下来，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/Godofcoffe/FisherMan

在命令行窗口中，切换至项目根目录，并安装好工具所需的依赖组件：

    
    
    $ cd FisherMan
    
    $ python3 -m pip install -r requeriments.txt

## 工具使用

    
    
    $ python3 fisherman.py --help
    
    usage: fisherman.py [-h] [--version] [-u USERNAME [USERNAME ...] | -i ID
    
                        [ID ...] | --use-txt TXT_FILE | -S USER] [-v | -q] [-sf]
    
                        [--specify {0,1,2,3,4,5} [{0,1,2,3,4,5} ...]] [-s]
    
                        [--filters]
    
                        [-work WORK | -education EDUCATION | -city CITY] [-b]
    
                        [--email EMAIL] [--password PASSWORD] [-o | -c]
    
     
    
    FisherMan: Extract information from facebook profiles. (Version 3.6.0)
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --version             Shows the current version of the program.
    
      -u USERNAME [USERNAME ...], --username USERNAME [USERNAME ...]
    
                            Defines one or more users for the search.
    
      -i ID [ID ...], --id ID [ID ...]
    
                            Set the profile identification number.
    
      --use-txt TXT_FILE    Replaces the USERNAME parameter with a user list in a
    
                            txt.
    
      -S USER, --search USER
    
                            It does a shallow search for the username. Replace the
    
                            spaces with '.'(period).
    
      -v, -d, --verbose, --debug
    
                            It shows in detail the data search process.
    
      -q, --quiet           Eliminates and simplifies some script outputs for a
    
                            simpler and more discrete visualization.
    
      -b, --browser         Opens the browser/bot.
    
     
    
    search options:
    
      --filters             Shows the list of available filters.
    
      -work WORK            Sets the work filter.
    
      -education EDUCATION  Sets the education filter.
    
      -city CITY            Sets the city filter.
    
     
    
    profile options:
    
      -sf, --scrape-family  If this parameter is passed, the information from
    
                            family members will be scraped if available.
    
      --specify {0,1,2,3,4,5} [{0,1,2,3,4,5} ...]
    
                            Use the index number to return a specific part of the
    
                            page. about: 0, about_contact_and_basic_info: 1,
    
                            about_family_and_relationships: 2, about_details: 3,
    
                            about_work_and_education: 4, about_places: 5.
    
      -s, --several         Returns extra data like profile picture, number of
    
                            followers and friends.
    
     
    
    credentials:
    
      --email EMAIL         If the profile is blocked, you can define your
    
                            account, however you have the search user in your
    
                            friends list.
    
      --password PASSWORD   Set the password for your facebook account, this
    
                            parameter has to be used with --email.
    
     
    
    output:
    
      -o, --file-output      Save the output data to a .txt file.
    
      -c, --compact         Save the output data to a .txt file and compress.

### 搜索目标用户

 **用户名搜索：**

    
    
    python3 fisherman.py -u name name.profile name.profile2

 **ID搜索：**

    
    
    python3 fisherman.py -i 000000000000

我们也可以通过一个.txt文件加载多个目标用户名，这种情况适用于暴力破解输出类型：

    
    
    python3 fisherman.py --use-txt filename.txt

注意：某些账号只能搜索有限的信息，并且受限于用户的好友列表：

    
    
    python3 fisherman.py --email youremail@email.com --password yourpass

### 大规模信息收集

    
    
    python3 fisherman.py --use-txt file -c -sf

### 基础数据收集

    
    
    python3 fisherman.py -u name --specify 0

### 家庭和关系收集

    
    
    python3 -u name --specify 2

### 获取额外信息（例如用户头像、粉丝和好友）

    
    
    python3 fisherman.py -u name [-s | --several]

### 过滤搜索结果

    
    
    python3 fisherman.py -S name -work fisherman

## 工具使用演示

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/434026)】

## 许可证协议

本项目的开发与发布遵循BSD 3-Clause开源许可证协议。

## 项目地址

 **FisherMan：** 【[ _GitHub传送门_](https://github.com/Godofcoffe/FisherMan)】

