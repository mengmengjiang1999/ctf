python使用pydub进行音频视频处理

[ 逍遥_yjz](https://www.jianshu.com/u/6d15f00023f9)关注赞赏支持

# python使用pydub进行音频视频处理

# 1.合并两个语音文件

    
    
    # coding:utf-8
    from pydub import AudioSegment
    
    
    enPath1 = r'D:\PythonFiles\2018second\speechMerge\testData\nishi.mp3' # 文件的路径
    enPath2 = r'D:\PythonFiles\2018second\speechMerge\testData\linvshi.wav' # 文件的路径
    targetPath = r'D:\PythonFiles\2018second\speechMerge\resultData\output12.wav' # 合并文件的路径
    # 加载MP3文件
    
    song1 = AudioSegment.from_mp3(enPath1)
    song2 = AudioSegment.from_wav(enPath2)
    
    # 取得两个MP3文件的声音分贝
    db1 = song1.dBFS
    db2 = song2.dBFS
    
    # song1 = song1[300:]  # 从300ms开始截取英文MP3
    
    # 调整两个MP3的声音大小，防止出现一个声音大一个声音小的情况
    dbplus = db1 - db2
    if dbplus < 0:  # song1的声音更小
        song1 += abs(dbplus)
    elif dbplus > 0:  # song2的声音更小
        song2 += abs(dbplus)
    
    # 拼接两个音频文件
    song = song1 + song2
    
    print(song)
    
    # 导出音频文件
    print(song.export(targetPath, format="wav") )
    song.export(targetPath, format="wav")  # 导出为MP3格式
    

第二种方式：

    
    
    # coding:utf-8
    from pydub import AudioSegment
    import os, re
    
    slash = '\\'
    
    def test():
        d_merger_path = {'OG37TR-3': ['D:\PythonFiles\\2018second\speechMerge\\addPinyinPackage\\test\HS3-1.wav',
                'D:\PythonFiles\\2018second\speechMerge\\addPinyinPackage\\test\yu_xian_sheng_ma.wav']}
        targetPath_Folder = r'D:\PythonFiles\\2018second\speechMerge\\addPinyinPackage\\test'
        for key ,value in d_merger_path.items():
            name = key
            print(name)
            firstlist = AudioSegment.empty()
            pathList = value
            for path0 in pathList:
                print(path0)
    
                song = AudioSegment.from_wav(path0)
                firstlist += song
    
        targetPath = os.path.join(targetPath_Folder + slash, name + '.wav')
        firstlist.export(targetPath, format="wav")  # 导出为WAV格式
    
    test()
    

# 2.切割语音

    
    
    # 循环目录下所有文件
    for each in os.listdir('.'):
        filename = re.findall(r"(.*?)\.mp3", each) # 取出.mp3后缀的文件名
        if filename:
            filename[0] += '.mp3'
            mp3 = AudioSegment.from_mp3(filename[0]) # 打开mp3文件
            mp3[17*1000+500:].export(filename[0], format="mp3") # 切割前17.5秒并覆盖保存
    

<https://www.jb51.net/article/115584.htm>  
<https://ptorch.com/news/112.html>  
<https://blog.csdn.net/qq_25883823/article/details/52749279>  
<https://github.com/jiaaro/pydub>

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Vue 基本使用](https://www.jianshu.com/p/06e4af9e04e3)

特点 1.基于MVVM模式（Model-View-ViewModel），中间通过viewmodel层实现了双向绑定...

[dawsonenjoy](https://www.jianshu.com/u/c3a9e18b5a82)阅读 573评论 0赞 1

  * [2019-08-24 Java与MySQL 中 日期、时间 的使用](https://www.jianshu.com/p/dff605501d0a)

在MySQL中，与时间相关的类型有： 可以这样赋值： Java判断今天星期几 我是使用以下方式获得的： [参考]J...

[枫叶落尽](https://www.jianshu.com/u/8a5e2f349b7b)阅读 139评论 0赞 0

  * [VMware虚拟机中Ubuntu18.04无法连接网络和突然断网的解决办法以及VMwareTo...](https://www.jianshu.com/p/503ce4a03f76)

一、虚拟机中Ubuntu18.04无法连接网络和突然断网的解决办法，具体内容如下对VMware虚拟机进行恢复默认网...

[JIAWEIJIAWEI](https://www.jianshu.com/u/14afe1e0c81c)阅读 2,145评论 0赞 0

  * [网络安全学习，及CTF学习资料整理](https://www.jianshu.com/p/0c9d7a7f808f)

php代码解密https://zhaoyuanma.com/Python https://docs.python....

[kepler404](https://www.jianshu.com/u/7432f0153fe4)阅读 10,467评论 4赞 31

  * [Python pathlib subprocess fstring](https://www.jianshu.com/p/f936c9040e4b)

介绍 记录一下几个工具的使用方法 pathlib subprocess fstring shutil pathli...

[zestloveheart](https://www.jianshu.com/u/498a4d778abe)阅读 314评论 0赞 0

 