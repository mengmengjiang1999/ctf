## 问题是怎么发现的

最近有个java应用在做压力测试  
压测环境配置：  
CentOS系统 4核CPU 8g内存 jdk1.6.0_25，jvm配置-server -Xms2048m -Xmx2048m  
出现问题如下  
执行300并发，压测持续1个小时后内存使用率从20%上升到100%,tps从1100多降低到600多。

## 排查问题的详细过程

首先使用top命令查看内存占用如下  
![image.png](https://image.3001.net/images/20230817/1692237985_64dd80a13a57c46bff54b.png!small)

然后查看java堆内存分布情况，查看堆内存占用正常，jvm垃圾回收也没有异常。  
![image.png](https://image.3001.net/images/20230817/1692237986_64dd80a2510ef7aa77980.png!small)

然后想到了是堆外内存泄漏，由于系统中用的jsf接口比较多，底层都是依赖的netty。

  * 首先考虑的是java中nio包下的DirectByteBuffer,可以直接分配堆外内存，不过该类分配的内存也有大小限制的，可以直接通过-XX:MaxDirectMemorySize=1g 进行指定，并且内存不够用的时候代码中会显式的调用System.gc()方法来触发FullGC,如果内存还是不够用就会抛出内存溢出的异常。

  * 为了验证这一想法，于是在启动参数中通过-XX:MaxDirectMemorySize=1g指定了堆外内存大小为1g，然后再次进行压测，发现内存还是在持续增长，然后超过了堆内存2g和堆外内存1g的总和，并且也没有发现有内存溢出的异常，也没有频繁的进行FullGC。所以可能不是nio的DirectByteBuffer占用的堆外内存。

为了分析堆外内存到底是谁占用了，不得不安装google-perftools工具进行分析。它的原理是在java应用程序运行时，当调用malloc时换用它的libtcmalloc.so，这样就能做一些统计了。  
安装步骤如下:

  * 下载http://download.savannah.gnu.org/releases/libunwind/libunwind-0.99-beta.tar.gz，

  * ./configure

  * make

  * sudo make install //需要root权限

  * 下载http://google-perftools.googlecode.com/files/google-perftools-1.8.1.tar.gz,

  * ./configure --prefix=/home/admin/tools/perftools --enable-frame-pointers

  * make

  * sudo make install //需要root权限

  * 修改lc_config: sudo vi /etc/ld.so.conf.d/usr-local_lib.conf，加入/usr/local/lib(libunwind的lib所在目录)

  * 执行sudo /sbin/ldconfig，使libunwind生效

  * 在应用程序启动前加入：

  * export LD_PRELOAD=/home/admin/tools/perftools/lib/libtcmalloc.so

  * export HEAPPROFILE=/home/admin/heap/gzip

  * 启动应用程序，此时会在/home/admin/heap下看到诸如gzip_pid.xxxx.heap的heap文件

  * 使用/home/admin/tools/perftools/bin/pprof --text $JAVA_HOME/bin/java test_pid.xxxx.heap来查看

  * /home/admin/tools/perftools/bin/pprof --text $JAVA_HOME/bin/java gzip_22366.0005.heap > gzip-0005.txt

  * 然后查看分析结果如下

    
    
    Total: 4504.5 MB
    4413.9 98.0% 98.0% 4413.9 98.0% zcalloc
    60.0 1.3% 99.3% 60.0 1.3% os::malloc
    16.4 0.4% 99.7% 16.4 0.4% ObjectSynchronizer::omAlloc
    8.7 0.2% 99.9% 4422.7 98.2% Java_java_util_zip_Inflater_init
    4.7 0.1% 100.0% 4.7 0.1% init
    0.3 0.0% 100.0% 0.3 0.0% readCEN
    0.2 0.0% 100.0% 0.2 0.0% instanceKlass::add_dependent_nmethod
    0.1 0.0% 100.0% 0.1 0.0% _dl_allocate_tls
    0.0 0.0% 100.0% 0.0 0.0% pthread_cond_wait@GLIBC_2.2.5
    0.0 0.0% 100.0% 1.7 0.0% Thread::Thread
    0.0 0.0% 100.0% 0.0 0.0% _dl_new_object
    0.0 0.0% 100.0% 0.0 0.0% pthread_cond_timedwait@GLIBC_2.2.5
    0.0 0.0% 100.0% 0.0 0.0% _dlerror_run
    0.0 0.0% 100.0% 0.0 0.0% allocZip
    0.0 0.0% 100.0% 0.0 0.0% __strdup
    0.0 0.0% 100.0% 0.0 0.0% _nl_intern_locale_data
    0.0 0.0% 100.0% 0.0 0.0% addMetaName
    

可以看到是Java_java_util_zip_Inflater_init这个函数一直在进行内存分配，查看java源码原来是

    
    
    public GZIPInputStream(InputStream in, int size) throws IOException {
        super(in, new Inflater(true), size);
     usesDefaultInflater = true;
     readHeader(in);
    }
    
    
    
    原来是java中gzip解压缩类耗尽了系统内存，然后跟踪源码到了系统里边使用的jimdb客户端SerializationUtils类，jimdb客户端使用该工具类对保存在jimdb中的key和对象进行序列化和反序列化操作，并且在对Object类型的进行序列化和反序列化的时候用到了gzip解压缩,也就是在调用jimdb客户端的getObject和setObject方法时，内部会使用java的GZIPInputStream和GZIPOutputStream解压缩功能，当大并发进行压测的时候，就会造成内存泄漏，出现内存持续增长的问题，当压测停止后，内存也不会释放。
    

## 如何解决问题

1、升级jdk版本为jdk7u71
，压测一段时间后，发现内存增长有所减慢，并且会稳定在一定的范围内，不会把服务器的所有内存耗尽。猜测可能是jdk1.6版本的bug  
2、尽量不要使用jimdb客户端的getObject和setObject方法，如果真的需要保存对象，可以自己实现序列化和反序列化，不要解压缩功能，因为对象本来就不大，压缩不了多少空间。如真的需要解压缩功能，最好设置解压缩阀值，当对象大小超过阀值之后在进行解压缩处理，不要将所有对象都进行解压缩处理。

> 作者：京东零售 曹志飞
>
> 来源：京东云开发者社区

