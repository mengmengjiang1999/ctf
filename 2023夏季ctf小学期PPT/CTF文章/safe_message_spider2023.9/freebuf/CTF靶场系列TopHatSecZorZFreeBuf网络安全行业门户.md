# 下载地址

注：只能使用vmbox打开，新增一张网卡修改为桥接模式

    
    
    https://download.vulnhub.com/tophatsec/Zorz.ova

# 实战演练

查找靶机IP

![image.png](https://image.3001.net/images/20191114/1573721686_5dcd1656d39a9.png!small)扫描靶机开放了那些端口？

![image.png](https://image.3001.net/images/20191114/1573721845_5dcd16f5934ed.png!small)看到了靶机开放了80端口，在浏览器打开80端口

![image.png](https://image.3001.net/images/20191114/1573721901_5dcd172d6c39b.png!small)点击超链接就会发现
**有三种上传的页面**

 **phpwebshell，<https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php>**

 **第一种**

**![image.png](https://image.3001.net/images/20191114/1573722111_5dcd17ff298f5.png!small)**直接上传就可以上传成功

![image.png](https://image.3001.net/images/20191114/1573722143_5dcd181f11f98.png!small)
问题是不知道路径是哪一个，需要我们爆破一下目录，找到了一个uploads2文件夹

![image.png](https://image.3001.net/images/20191114/1573724542_5dcd217e3c0e6.png!small)打开之后，发现不是在这里面，发散一下思维，我们试试打开uploads1，成功获得反弹shell

![image.png](https://image.3001.net/images/20191114/1573724624_5dcd21d0a2bbc.png!small)

查看源代码，我们可以发现这里面只是简简单单上传文件，没有做任何的校验

    
    
    $ cat uploader.php
    <?php
    
    $uploaddir = '/var/www/html/uploads1/';
    $uploadfile = $uploaddir . basename($_FILES['upfile']['name']);
    
    echo "<p>";
    
    if (move_uploaded_file($_FILES['upfile']['tmp_name'], $uploadfile)) {
      echo "File is valid, and was successfully uploaded.\n";
    } else {
       echo "Upload failed";
    }
    
    echo "</p>";
    echo '<pre>';
    echo 'Here is some more debugging info:';
    print_r($_FILES);
    print "</pre>";
    
    ?> 
    
    

**第二种**

当我直接上传webshell的时候，系统提示只能上传图片文件![image.png](https://image.3001.net/images/20191114/1573726401_5dcd28c15a239.png!small)

绕过的方法也很简单，在webshell添加gif98

![image.png](https://image.3001.net/images/20191114/1573726510_5dcd292ee3479.png!small)上传失败，修改后缀名

![image.png](https://image.3001.net/images/20191114/1573726559_5dcd295f1bbf3.png!small)上传成功

![image.png](https://image.3001.net/images/20191114/1573726640_5dcd29b009cf8.png!small)![image.png](https://image.3001.net/images/20191114/1573726652_5dcd29bc9e3b6.png!small)反弹shell连接成功

![image.png](https://image.3001.net/images/20191114/1573726679_5dcd29d742d48.png!small)查看源代码，发现是`imageFileType`参数控制上传

    
    
    $ $ cat uploader2.php
     <?php
    $target_dir = "/var/www/html/uploads2/";
    $target_file = $target_dir . basename($_FILES["upfile"]["name"]);
    $uploadOk = 1;
    $imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);
    // Check if image file is a actual image or fake image
    if(isset($_POST["submit"])) {
        $check = getimagesize($_FILES["upfile"]["tmp_name"]);
        if($check !== false) {
            echo "Success! " . $check["mime"] . ".";
            $uploadOk = 1;
        } else {
            echo "File is not an image.";
            $uploadOk = 0;
        }
    }
    // Check if file already exists
    if (file_exists($target_file)) {
        echo "Sorry, file already exists.";
        $uploadOk = 0;
    }
    // Check file size
    if ($_FILES["upfile"]["size"] > 5000000) {
        echo "Sorry, your file is too large.";
        $uploadOk = 0;
    }
    // Allow certain file formats
    if($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg"
    && $imageFileType != "gif" ) {
        echo "Sorry, only JPG, JPEG, PNG & GIF files are allowed.";
        $uploadOk = 0;
    }
    // Check if $uploadOk is set to 0 by an error
    if ($uploadOk == 0) {
        echo "Sorry, your file was not uploaded.";
    // if everything is ok, try to upload file
    } else {
        if (move_uploaded_file($_FILES["upfile"]["tmp_name"], $target_file)) {
            echo "The file ". basename( $_FILES["upfile"]["name"]). " has been uploaded.";
        } else {
            echo "Sorry, there was an error uploading your file.";
        }
    }
    ?> 
    

**第三种**

不过第三个网址打不开，jq连接是在google的，尴尬！！！

![image.png](https://image.3001.net/images/20191114/1573726981_5dcd2b0598ed6.png!small)  

算了，直接查看源代码。发现上传文件应为扩展名为.jpeg，jpg和png且小于100kb的图像

    
    
    $ cat uploader3.php
    <?php
    
    header('Content-Type: text/plain; charset=utf-8');
    
    try {
       
        // Undefined | Multiple Files | $_FILES Corruption Attack
        // If this request falls under any of them, treat it invalid.
        if (
            !isset($_FILES['upfile']['error']) ||
            is_array($_FILES['upfile']['error'])
        ) {
            throw new RuntimeException('Invalid parameters.');
        }
    
        // Check $_FILES['upfile']['error'] value.
        switch ($_FILES['upfile']['error']) {
            case UPLOAD_ERR_OK:
                break;
            case UPLOAD_ERR_NO_FILE:
                throw new RuntimeException('No file sent.');
            case UPLOAD_ERR_INI_SIZE:
            case UPLOAD_ERR_FORM_SIZE:
                throw new RuntimeException('Exceeded filesize limit.');
            default:
                throw new RuntimeException('Unknown errors.');
        }
    
        // You should also check filesize here.
        if ($_FILES['upfile']['size'] > 1000000) {
            throw new RuntimeException('Exceeded filesize limit.');
        }
    
        // DO NOT TRUST $_FILES['upfile']['mime'] VALUE !!
        // Check MIME Type by yourself.
        $finfo = new finfo(FILEINFO_MIME_TYPE);
        if (false === $ext = array_search(
            $finfo->file($_FILES['upfile']['tmp_name']),
            array(
                'jpg' => 'image/jpeg',
                'png' => 'image/png',
                'gif' => 'image/gif',
            ),
            true
        )) {
            throw new RuntimeException('Invalid file format.');
        }
    
        // You should name it uniquely.
        // DO NOT USE $_FILES['upfile']['name'] WITHOUT ANY VALIDATION !!
        // On this example, obtain safe unique name from its binary data.
        if (!move_uploaded_file(
            $_FILES['upfile']['tmp_name'],
            sprintf('./uploads/%s.%s',
                sha1_file($_FILES['upfile']['tmp_name']),
                $ext
            )
        )) {
            throw new RuntimeException('Failed to move uploaded file.');
        }
    
        echo 'File is uploaded successfully.';
    
    } catch (RuntimeException $e) {
    
        echo $e->getMessage();
    
    }
    
    ?>
    
    

  

