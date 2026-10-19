# Amazon S3渗透测试笔记

被某个“爸爸”甩了一堆自己的云存储列表，其中包含S3和ECS，说希望我能找到一些问题，只能含泪收下。

其实S3的最常见问题就是权限配置错误导致的未授权执行各种操作的问题，所以就从它开始下手了。

## Amazon S3介绍

Amazon Simple Storage Service (Amazon S3)
是一种对象存储服务，提供行业领先的可扩展性、数据可用性、安全性和性能。这意味着各种规模和行业的客户都可以使用它来存储和保护各种用例（如网站、移动应用程序、备份和还原、存档、企业应用程序、IoT
设备和大数据分析）的任意数量的数据。S3提供了存储管理和监控、存储类、访问管理与安全性、随时查询、数据传输这些功能。

## 准备工作

1.注册AWS，<https://aws.amazon.com/> ，在这个网址进行注册，还要刷一刀的预授权，注册后就可以登陆：

![17.png](https://image.3001.net/images/20200309/1583746698_5e660e8a6583a.png!small)

2.下载安装Windows CLI，<https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html>

![18.png](https://image.3001.net/images/20200309/1583746758_5e660ec6c20af.png!small)

安装好之后在Powershell中输入

    
    
    aws --version
    

![19.png](https://image.3001.net/images/20200309/1583746832_5e660f107a790.png!small)  

3.配置CLI，在之前登陆好的AWS界面管理自己的安全凭证，然后选择创建新的访问密钥，如下图所示：

![20.png](https://image.3001.net/images/20200309/1583746841_5e660f1926656.png!small)

在命令行输入

    
    
    awv configure
    

会提示输入这两个密钥，正确输入相关的信息：

![21.png](https://image.3001.net/images/20200309/1583746851_5e660f235ce57.png!small)

## 权限简介

在创建存储桶（bucket）时会默认帮你勾选阻止全部公开权限，如果取消勾选，就可能会存在部分权限问题：

##
![31.png](https://image.3001.net/images/20200309/1583745600_5e660a402e140.png!small)

在创建好存储桶之后，可以单独设置该存储桶的访问控制列表（ACL），设置项如下图所示：

![32.png](https://image.3001.net/images/20200309/1583745651_5e660a73d96a6.png!small)

对对象的访问权限：

列出对象：允许访问者列出对象

写入对象：允许访问者创建和删除对象读取

存储桶权限：允许被授权者读取存储桶ACL权限

写入存储桶权限：允许被授权者编辑存储桶ACL权限

很多人为了测试或者设置方便就会把公有访问权限配置的很大，于是权限配置问题导致的S3未授权访问问题成了常见但是非常严重的问题。

## 简单尝试

AWS问题主要集中在bucket允许匿名访问，允许列出文件，允许任意文件上传和读取，允许盲上传，允许任意读取/写入对象，允许显示ACP/ACL等问题。

先从最简单的列出文件开始：假设服务器地址为freebuftest.s3-us-west-2.amazonaws.com,那么需要在configure中把自己的地区设置为us-west-2，这样就可以访问对应区域的bucket了。然后在shell中输入

    
    
    aws s3 ls s3://freebuftest
    

如果是需要权限，会返回Access Denied，如下图所示：

![22.png](https://image.3001.net/images/20200309/1583745832_5e660b28ae313.png!small)

但是如果是没有权限的，就会列出目录下的所有文件夹：

![23.png](https://image.3001.net/images/20200309/1583745851_5e660b3bbf9a3.png!small)

如果需要访问深层的文件夹，可以输入如下图的命令：

    
    
    aws s3 ls s3://freebuftest/1234567/
    

![24.png](https://image.3001.net/images/20200309/1583745905_5e660b71a42bb.png!small)

当然如果嫌麻烦，可以直接在命令后加上 --recursive ，可以看到遍历出了所有文件：

![25.png](https://image.3001.net/images/20200309/1583745926_5e660b86e77d6.png!small)

除了ls命令，还有cp,mv,rm，sync命令可以直接执行，操作方式如下：

    
    
    // Copy MyFile.txt in current directory to s3://my-bucket/path
    $ aws s3 cp MyFile.txt s3://my-bucket/path/
    
    // Move all .jpg files in s3://my-bucket/path to ./MyDirectory
    $ aws s3 mv s3://my-bucket/path ./MyDirectory --exclude "*" --include "*.jpg" --recursive
    
    // List the contents of my-bucket
    $ aws s3 ls s3://my-bucket
    
    // List the contents of path in my-bucket
    $ aws s3 ls s3://my-bucket/path/
    
    // Delete s3://my-bucket/path/MyFile.txt
    $ aws s3 rm s3://my-bucket/path/MyFile.txt
    
    // Delete s3://my-bucket/path and all of its contents
    $ aws s3 rm s3://my-bucket/path --recursive
    

参考页面：<https://docs.amazonaws.cn/cli/latest/userguide/cli-services-s3-commands.html>

其实如果权限存在问题，那么可能会导致这几个命令都可以执行。

尝试使用cp命令上传一个文件，可以看到上传成功了：

    
    
     aws s3 cp F:\2018\1.txt s3://freebuftest/1234567/
    

![26.png](https://image.3001.net/images/20200309/1583745995_5e660bcbc8055.png!small)

    
    
    aws s3 ls s3://freebuftest/1234567/
    

![27.png](https://image.3001.net/images/20200309/1583746017_5e660be1795e1.png!small)

但是尝试拼接成https地址 [https://freebuftest.s3-us-west-2.amazonaws.com/1234567/1.txt](https://freebuftest.s3-us-west-2.amazonaws.com/123456/1.txt) 下载会提示：

![28.png](https://image.3001.net/images/20200309/1583747188_5e6610747263a.png!small)  

说明存在盲写入问题,但是读取文件依然需要鉴权。

尝试用sync下载文件，还是没有权限，直接就access Denied了

    
    
    aws s3 sync s3://freebuftest/1234567/0/1234/ test --no-sign-request --region us-west-2
    

![30.png](https://image.3001.net/images/20200309/1583746065_5e660c117a23e.png!small)

尝试获取下ACL列表

    
    
    aws s3api get-bucket-acl --bucket freebuftest
    

![33.png](https://image.3001.net/images/20200309/1583746083_5e660c23e246b.png!small)

还是没有权限失败了。

## 自动化检测

简单实现了查看ACL,ls和cp上传功能的检测，但是编辑ACL，sync、cp、mv等命令会对原桶中对象造成破坏，所以暂时先不提供。

    
    
    import subprocess
    import argparse
    
    def run_command(cmd):
        p = subprocess.getstatusoutput(cmd)
        print(p[1])
        return p[1]
    
    def s3_ls(bucket):
        bucket = line.split(":", 1)
        command = "aws s3 ls s3://" + bucket[1] + " --region " + bucket[0]
        print(command)
        result = run_command(command)
        if "AccessDenied" not in result:
            if "InvalidBucketName" not in result:
                if "SSL validation" not in result:
                    print("\033[1;32;0mbucket " + bucket[0] + ":" + bucket[1] + " may has enum vulnerability")
                    print("pls recheck it by \"" + command + "\"" + "\033[0m")
    
    def s3_cp(bucket):
        bucket = line.split(":", 1)
        command = "aws s3 cp test.txt s3://" + bucket[1] + " --region " + bucket[0]
        print(command)
        result = run_command(command)
        if "AccessDenied" not in result:
            if "InvalidBucketName" not in result:
                if "SSL validation" not in result:
                    print("\033[1;32;0mbucket " + bucket[0] + ":" + bucket[1] + " may has blind upload vulnerability")
                    print("pls recheck it by \"" + command + "\"" + "\033[0m")
    
    def s3_getacl(bucket):
        bucket = line.split(":", 1)
        #aws s3api get-bucket-acl --bucket xxx --region xxx
        command = "aws s3api get-bucket-acl --bucket " + bucket[1] + " --region " + bucket[0]
        print(command)
        result = run_command(command)
        if "AccessDenied" not in result:
            if "InvalidBucketName" not in result:
                if "SSL validation" not in result:
                    print("\033[1;32;0mbucket " + bucket[0] + ":" + bucket[1] + " may has get_acl vulnerability")
                    print("pls recheck it by \"" + command + "\"" + "\033[0m")
    
    if __name__ == "__main__":
    
        parser = argparse.ArgumentParser(description="探测脚本")
        parser.add_argument('-f', '--file' ,type=str, default="s3-list", help="以文件的形式引入目标列表,格式为\"地区:存储桶名\"")
        parser.add_argument('-r', '--run' ,nargs='*', type=str, default=["acl,ls,cp"], help="需要指定执行的检测类型，acl，ls以及cp,默认三个都会进行")
    
        args = parser.parse_args()
        if args.file is None:
            print("请指定有效的IP或文件。程序退出。")
        else:
            #仅指定了文件
            bucket_list = open(args.file, 'r')
            for line in bucket_list.readlines():
                line = line.rstrip('\n')
                if "ls"in args.run:
                    s3_ls(line)
                if "cp"in args.run:
                    s3_cp(line)
                if "acl"in args.run:
                    s3_getacl(line)
            if args.list is None and args.upload is None and args.get_acl is None:
                print("没有指定功能")
            bucket_list.close()
    

没有使用官方提供的API接口而是使用Python调用命令行的方式可能会对结果分析造成不便。以后可能会研究下使用API进行操作。

## 总结

随着云使用的越来越广泛，更多的数据从物理服务器上被迁移到了云存储中。虽然网上爆出了很多S3等云存储的未授权问题，但是很多公司依然不重视这些问题，导致很多机密信息泄露，比如个人身份信息，公司商业信息以及图片视频等。

