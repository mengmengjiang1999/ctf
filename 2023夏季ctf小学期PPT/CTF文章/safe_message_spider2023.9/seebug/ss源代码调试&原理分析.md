**作者：spoock**  
**来源：<https://blog.spoock.com/2019/07/06/ss-learn/>**

## 源代码调试

ss是位于iproute2这个库中，可以从[iproute2](https://github.com/CumulusNetworks/iproute2)上面下载到源代码，配置其源代码调试的方式和[netstat源代码调试](https://blog.spoock.com/2019/05/26/netstat-learn/)这篇文章一样. 在根目录下创建CMakeLists.txt文件，内容如下：

    
    
    cmake_minimum_required(VERSION 3.13)
    project(test C)
    
    set(BUILD_DIR .)
    
    #add_executable()
    add_custom_target(ss command -c ${BUILD_DIR})

同时修改Makefile文件中的45行的 **CCOPTS = -O2** 为 **CCOPTS = -O0 -g3** 在clion中配置Target:

[![clion-settings](https://images.seebug.org/content/images/2019/08/13/1565688739000-clion-settings.png-w331s)](https://blog.spoock.com/2019/07/06/ss-learn/clion-settings.png)

如此整个调试环境搭建完毕．

## 初步分析

在什么参数也没有的情况下，运行程序得到的结果如下:

    
    
    Netid  State      Recv-Q Send-Q Local Address:Port             Peer Address:Port
    tcp    ESTAB      0      0      127.0.0.1:57354                127.0.0.1:socks               
    tcp    ESTAB      0      0      127.0.0.1:37350                127.0.0.1:socks               
    tcp    ESTAB      0      0      172.16.40.154:43450                45.8.223.61:17250               
    tcp    CLOSE-WAIT 1      0      127.0.0.1:57398                127.0.0.1:socks               
    tcp    ESTAB      0      0      127.0.0.1:57062                127.0.0.1:socks

和直接运行ss命令得到的结果一样．接下来就是分析整个ss程序的执行流程

## main

main函数就是用于对各种选项进行解析，并以此判断执行什么函数．

    
    
    int main(int argc, char *argv[])
    {
        int saw_states = 0;
        int saw_query = 0;
        int do_summary = 0;
        const char *dump_tcpdiag = NULL;
        FILE *filter_fp = NULL;
        int ch;
        int state_filter = 0;
        int addrp_width, screen_width = 80;
    
        while ((ch = getopt_long(argc, argv,
                     "dhaletuwxnro460spbEf:miA:D:F:vVzZN:KHS",
                     long_opts, NULL)) != EOF) {
            switch (ch) {
            case 'n':
                resolve_services = 0;
                break;
            ......
            }
            .....
        }

在默认情况下，会进入到如下代码中

    
    
    if (do_default) {
        state_filter = state_filter ? state_filter : SS_CONN;
        filter_default_dbs(＆current_filter);
    }

程序会执行filter_default_dbs()函数，设置默认的过滤条件．

### filter_default_dbs

    
    
    static void filter_default_dbs(struct filter *f) {
        filter_db_set(f, UDP_DB);
        filter_db_set(f, DCCP_DB);
        filter_db_set(f, TCP_DB);
        filter_db_set(f, RAW_DB);
        filter_db_set(f, UNIX_ST_DB);
        filter_db_set(f, UNIX_DG_DB);
        filter_db_set(f, UNIX_SQ_DB);
        filter_db_set(f, PACKET_R_DB);
        filter_db_set(f, PACKET_DG_DB);
        filter_db_set(f, NETLINK_DB);
        filter_db_set(f, SCTP_DB);
    }

filter_default_dbs很简单就是在默认情况下设置的过滤条件．

之后程序会执行到unix_show(&current_filter);

## unix_show

函数代码如下:

    
    
    static void filter_default_dbs(struct filter *f) {
        filter_db_set(f, UDP_DB);
        filter_db_set(f, DCCP_DB);
        filter_db_set(f, TCP_DB);
        filter_db_set(f, RAW_DB);
        filter_db_set(f, UNIX_ST_DB);
        filter_db_set(f, UNIX_DG_DB);
        filter_db_set(f, UNIX_SQ_DB);
        filter_db_set(f, PACKET_R_DB);
        filter_db_set(f, PACKET_DG_DB);
        filter_db_set(f, NETLINK_DB);
        filter_db_set(f, SCTP_DB);
    }
    filter_default_dbs很简单就是在默认情况下设置的过滤条件．
    
    之后程序会执行到unix_show(&current_filter);
    
    unix_show
    函数代码如下:
    
    unix_show  Collapse source
    static int unix_show(struct filter *f)
    {
        FILE *fp;
        char buf[256];
        char name[128];
        int  newformat = 0;
        int  cnt;
        struct sockstat *list = NULL;
        const int unix_state_map[] = { SS_CLOSE, SS_SYN_SENT,
                           SS_ESTABLISHED, SS_CLOSING };
    
        if (!filter_af_get(f, AF_UNIX))
            return 0;
    
        if (!getenv("PROC_NET_UNIX") && !getenv("PROC_ROOT")
            && unix_show_netlink(f) == 0)
            return 0;
    
        if ((fp = net_unix_open()) == NULL)
            return -1;
        if (!fgets(buf, sizeof(buf), fp)) {
            fclose(fp);
            return -1;
        }
    
        if (memcmp(buf, "Peer", 4) == 0)
            newformat = 1;
        cnt = 0;
    
        while (fgets(buf, sizeof(buf), fp)) {
            struct sockstat *u, **insp;
            int flags;
    
            if (!(u = calloc(1, sizeof(*u))))
                break;
    
            if (sscanf(buf, "%x: %x %x %x %x %x %d %s",
                   &u->rport, &u->rq, &u->wq, &flags, &u->type,
                   &u->state, &u->ino, name) < 8)
                name[0] = 0;
    
            u->lport = u->ino;
            u->local.family = u->remote.family = AF_UNIX;
    
            if (flags & (1 << 16)) {
                u->state = SS_LISTEN;
            } else if (u->state > 0 &&
                   u->state <= ARRAY_SIZE(unix_state_map)) {
                u->state = unix_state_map[u->state-1];
                if (u->type == SOCK_DGRAM && u->state == SS_CLOSE && u->rport)
                    u->state = SS_ESTABLISHED;
            }
            if (unix_type_skip(u, f) ||
                !(f->states & (1 << u->state))) {
                free(u);
                continue;
            }
    
            if (!newformat) {
                u->rport = 0;
                u->rq = 0;
                u->wq = 0;
            }
    
            if (name[0]) {
                u->name = strdup(name);
                if (!u->name) {
                    free(u);
                    break;
                }
            }
    
            if (u->rport) {
                struct sockstat *p;
    
                for (p = list; p; p = p->next) {
                    if (u->rport == p->lport)
                        break;
                }
                if (!p)
                    u->peer_name = "?";
                else
                    u->peer_name = p->name ? : "*";
            }
    
            if (f->f) {
                struct sockstat st = {
                    .local.family = AF_UNIX,
                    .remote.family = AF_UNIX,
                };
    
                memcpy(st.local.data, &u->name, sizeof(u->name));
                if (strcmp(u->peer_name, "*"))
                    memcpy(st.remote.data, &u->peer_name,
                           sizeof(u->peer_name));
                if (run_ssfilter(f->f, &st) == 0) {
                    free(u->name);
                    free(u);
                    continue;
                }
            }
    
            insp = &list;
            while (*insp) {
                if (u->type < (*insp)->type ||
                    (u->type == (*insp)->type &&
                     u->ino < (*insp)->ino))
                    break;
                insp = &(*insp)->next;
            }
            u->next = *insp;
            *insp = u;
    
            if (++cnt > MAX_UNIX_REMEMBER) {
                while (list) {
                    unix_stats_print(list, f);
                    printf("\n");
    
                    unix_list_drop_first(&list);
                }
                cnt = 0;
            }
        }
        fclose(fp);
        while (list) {
            unix_stats_print(list, f);
            printf("\n");
    
            unix_list_drop_first(&list);
        }
    
        return 0;
    }

这个函数就是解析网络数据的核心函数．代码较多，还是分布分析这些代码．

### unix_show_netlink

    
    
    if (!getenv("PROC_NET_UNIX") && !getenv("PROC_ROOT")
           && unix_show_netlink(f) == 0)
           return 0;

  * getenv判断PROC_NET_UNIX和PROC_ROOT是否存在
  * unix_show_netlink(f) 创建netlink

追踪进入到unix_show_netlink()中

    
    
    static int unix_show_netlink(struct filter *f)
    {
        DIAG_REQUEST(req, struct unix_diag_req r);
    
        req.r.sdiag_family = AF_UNIX;
        req.r.udiag_states = f->states;
        req.r.udiag_show = UDIAG_SHOW_NAME | UDIAG_SHOW_PEER | UDIAG_SHOW_RQLEN;
        if (show_mem)
            req.r.udiag_show |= UDIAG_SHOW_MEMINFO;
    
        return handle_netlink_request(f, &req.nlh, sizeof(req), unix_show_sock);
    }

f是一个filter，用于设置一些简单的过滤条件．

    
    
    req.r.sdiag_family = AF_UNIX;
    req.r.udiag_states = f->states;
    req.r.udiag_show = UDIAG_SHOW_NAME | UDIAG_SHOW_PEER | UDIAG_SHOW_RQLEN;

是用于设置diag_net的netlink的请求头，之后调用handle_netlink_request(f, &req.nlh, sizeof(req),
unix_show_sock);

### handle_netlink_request

跟踪进入到handle_netlink_request的实现

    
    
    static int handle_netlink_request(struct filter *f, struct nlmsghdr *req,
            size_t size, rtnl_filter_t show_one_sock)
    {
        int ret = -1;
        struct rtnl_handle rth;
    
        if (rtnl_open_byproto(&rth, 0, NETLINK_SOCK_DIAG))
            return -1;
    
        rth.dump = MAGIC_SEQ;
    
        if (rtnl_send(&rth, req, size) < 0)
            goto Exit;
    
        if (rtnl_dump_filter(&rth, show_one_sock, f))
            goto Exit;
    
        ret = 0;
    Exit:
        rtnl_close(&rth);
        return ret;
    }

  * 调用rtnl_send(&rth, req, size)用于发送diag_net的netlink的消息头．
  * rtnl_dump_filter(&rth, show_one_sock, f) 获取netlink的返回消息，回调show_one_sock()函数．

#### rtnl_send

跟踪进入到lib/libnetlink.c

    
    
    int rtnl_send(struct rtnl_handle *rth, const void *buf, int len)
    {
        return send(rth->fd, buf, len, 0);
    }

rtnl_send直接调用send()方法发送信息．

#### rtnl_dump_filter

跟踪进入到lib/libnetlink.c

    
    
    int rtnl_dump_filter_nc(struct rtnl_handle *rth,
                 rtnl_filter_t filter,
                 void *arg1, __u16 nc_flags)
    {
        const struct rtnl_dump_filter_arg a[2] = {
            { .filter = filter, .arg1 = arg1, .nc_flags = nc_flags, },
            { .filter = NULL,   .arg1 = NULL, .nc_flags = 0, },
        };
    
        return rtnl_dump_filter_l(rth, a);
    }

在rtnl_dump_filter_nc()中设置rtnl_dump_filter_arg过滤函数，之后调用rtnl_dump_filter_l()

    
    
    int rtnl_dump_filter_l(struct rtnl_handle *rth,
                   const struct rtnl_dump_filter_arg *arg)
    {
        struct sockaddr_nl nladdr;
        struct iovec iov;
        struct msghdr msg = {
            .msg_name = &nladdr,
            .msg_namelen = sizeof(nladdr),
            .msg_iov = &iov,
            .msg_iovlen = 1,
        };
        char buf[32768];
        int dump_intr = 0;
    
        iov.iov_base = buf;
        while (1) {
            int status;
            const struct rtnl_dump_filter_arg *a;
            int found_done = 0;
            int msglen = 0;
    
            iov.iov_len = sizeof(buf);
            status = recvmsg(rth->fd, &msg, 0);
    
            if (status < 0) {
                if (errno == EINTR || errno == EAGAIN)
                    continue;
                fprintf(stderr, "netlink receive error %s (%d)\n",
                    strerror(errno), errno);
                return -1;
            }
    
            if (status == 0) {
                fprintf(stderr, "EOF on netlink\n");
                return -1;
            }
    
            if (rth->dump_fp)
                fwrite(buf, 1, NLMSG_ALIGN(status), rth->dump_fp);
    
            for (a = arg; a->filter; a++) {
                struct nlmsghdr *h = (struct nlmsghdr *)buf;
    
                msglen = status;
    
                while (NLMSG_OK(h, msglen)) {
                    int err = 0;
    
                    h->nlmsg_flags &= ~a->nc_flags;
    
                    if (nladdr.nl_pid != 0 ||
                        h->nlmsg_pid != rth->local.nl_pid ||
                        h->nlmsg_seq != rth->dump)
                        goto skip_it;
    
                    if (h->nlmsg_flags & NLM_F_DUMP_INTR)
                        dump_intr = 1;
    
                    if (h->nlmsg_type == NLMSG_DONE) {
                        err = rtnl_dump_done(h);
                        if (err < 0)
                            return -1;
    
                        found_done = 1;
                        break; /* process next filter */
                    }
    
                    if (h->nlmsg_type == NLMSG_ERROR) {
                        rtnl_dump_error(rth, h);
                        return -1;
                    }
    
                    if (!rth->dump_fp) {
                        err = a->filter(&nladdr, h, a->arg1);
                        if (err < 0)
                            return err;
                    }
    
    skip_it:
                    h = NLMSG_NEXT(h, msglen);
                }
            }
    
            if (found_done) {
                if (dump_intr)
                    fprintf(stderr,
                        "Dump was interrupted and may be inconsistent.\n");
                return 0;
            }
    
            if (msg.msg_flags & MSG_TRUNC) {
                fprintf(stderr, "Message truncated\n");
                continue;
            }
            if (msglen) {
                fprintf(stderr, "!!!Remnant of size %d\n", msglen);
                exit(1);
            }
        }
    }

rtnl_dump_filter_l()实现了通过netlink获取数据，然后根据rtnl_dump_filter_arg过滤数据．

获取数据：

    
    
    struct sockaddr_nl nladdr;
    struct iovec iov;
    struct msghdr msg = {
        .msg_name = &nladdr,
        .msg_namelen = sizeof(nladdr),
        .msg_iov = &iov,
        .msg_iovlen = 1,
    };
    .....
    status = recvmsg(rth->fd, &msg, 0);

过滤数据:

    
    
    for (a = arg; a->filter; a++) {
        struct nlmsghdr *h = (struct nlmsghdr *)buf;
        .....
        h->nlmsg_flags &= ~a->nc_flags;
        if (nladdr.nl_pid != 0 ||
                    h->nlmsg_pid != rth->local.nl_pid ||
                    h->nlmsg_seq != rth->dump)
                    goto skip_it;
    
                if (h->nlmsg_flags & NLM_F_DUMP_INTR)
                    dump_intr = 1;
    
                if (h->nlmsg_type == NLMSG_DONE) {
                    err = rtnl_dump_done(h);
                    if (err < 0)
                        return -1;
    
                    found_done = 1;
                    break; /* process next filter */
                }
                .......

之前说过，handle_netlink_request(f, &req.nlh, sizeof(req), unix_show_sock);
程序最终会回调unix_show_sock函数．

### unix_show_sock

跟踪unix_show_sock的实现

    
    
    static int unix_show_sock(const struct sockaddr_nl *addr, struct nlmsghdr *nlh,
            void *arg)
    {
        struct filter *f = (struct filter *)arg;
        struct unix_diag_msg *r = NLMSG_DATA(nlh);
        struct rtattr *tb[UNIX_DIAG_MAX+1];
        char name[128];
        struct sockstat stat = { .name = "*", .peer_name = "*" };
    
        parse_rtattr(tb, UNIX_DIAG_MAX, (struct rtattr *)(r+1),
                 nlh->nlmsg_len - NLMSG_LENGTH(sizeof(*r)));
    
        stat.type  = r->udiag_type;
        stat.state = r->udiag_state;
        stat.ino   = stat.lport = r->udiag_ino;
        stat.local.family = stat.remote.family = AF_UNIX;
    
        if (unix_type_skip(&stat, f))
            return 0;
    
        if (tb[UNIX_DIAG_RQLEN]) {
            struct unix_diag_rqlen *rql = RTA_DATA(tb[UNIX_DIAG_RQLEN]);
    
            stat.rq = rql->udiag_rqueue;
            stat.wq = rql->udiag_wqueue;
        }
        if (tb[UNIX_DIAG_NAME]) {
            int len = RTA_PAYLOAD(tb[UNIX_DIAG_NAME]);
    
            memcpy(name, RTA_DATA(tb[UNIX_DIAG_NAME]), len);
            name[len] = '\0';
            if (name[0] == '\0') {
                int i;
                for (i = 0; i < len; i++)
                    if (name[i] == '\0')
                        name[i] = '@';
            }
            stat.name = &name[0];
            memcpy(stat.local.data, &stat.name, sizeof(stat.name));
        }
        if (tb[UNIX_DIAG_PEER])
            stat.rport = rta_getattr_u32(tb[UNIX_DIAG_PEER]);
    
        if (f->f && run_ssfilter(f->f, &stat) == 0)
            return 0;
    
        unix_stats_print(&stat, f);
    
        if (show_mem)
            print_skmeminfo(tb, UNIX_DIAG_MEMINFO);
        if (show_details) {
            if (tb[UNIX_DIAG_SHUTDOWN]) {
                unsigned char mask;
    
                mask = rta_getattr_u8(tb[UNIX_DIAG_SHUTDOWN]);
                printf(" %c-%c", mask & 1 ? '-' : '<', mask & 2 ? '-' : '>');
            }
        }
        printf("\n");
    
        return 0;
    }

  * `struct unix_diag_msg *r = NLMSG_DATA(nlh); parse_rtattr(tb, UNIX_DIAG_MAX, (struct rtattr *)(r+1),nlh->nlmsg_len - NLMSG_LENGTH(sizeof(*r)));` 获取netlink的数据

  * 解析数据并赋值

``` stat.type = r->udiag_type; stat.state = r->udiag_state; stat.ino =
stat.lport = r->udiag_ino; stat.local.family = stat.remote.family = AF_UNIX;

* * *

stat.rq = rql->udiag_rqueue; stat.wq = rql->udiag_wqueue; ```

#### unix_stats_print

`unix_stats_print(&stat, f);` 获取网络的连接状态

    
    
    static void unix_stats_print(struct sockstat *s, struct filter *f)
    {
        char port_name[30] = {};
    
        sock_state_print(s);
    
        sock_addr_print(s->name ?: "*", " ",
                int_to_str(s->lport, port_name), NULL);
        sock_addr_print(s->peer_name ?: "*", " ",
                int_to_str(s->rport, port_name), NULL);
    
        proc_ctx_print(s);
    }

#### sock_state_print

跟踪进入到sock_state_print()中

    
    
    static void sock_state_print(struct sockstat *s)
    {
        const char *sock_name;
        static const char * const sstate_name[] = {
            "UNKNOWN",
            [SS_ESTABLISHED] = "ESTAB",
            [SS_SYN_SENT] = "SYN-SENT",
            [SS_SYN_RECV] = "SYN-RECV",
            [SS_FIN_WAIT1] = "FIN-WAIT-1",
            [SS_FIN_WAIT2] = "FIN-WAIT-2",
            [SS_TIME_WAIT] = "TIME-WAIT",
            [SS_CLOSE] = "UNCONN",
            [SS_CLOSE_WAIT] = "CLOSE-WAIT",
            [SS_LAST_ACK] = "LAST-ACK",
            [SS_LISTEN] =   "LISTEN",
            [SS_CLOSING] = "CLOSING",
        };
    
        switch (s->local.family) {
        case AF_UNIX:
            sock_name = unix_netid_name(s->type);
            break;
        case AF_INET:
        case AF_INET6:
            sock_name = proto_name(s->type);
            break;
        case AF_PACKET:
            sock_name = s->type == SOCK_RAW ? "p_raw" : "p_dgr";
            break;
        case AF_NETLINK:
            sock_name = "nl";
            break;
        default:
            sock_name = "unknown";
        }
    
        if (netid_width)
            printf("%-*s ", netid_width,
                   is_sctp_assoc(s, sock_name) ? "" : sock_name);
        if (state_width) {
            if (is_sctp_assoc(s, sock_name))
                printf("`- %-*s ", state_width - 3,
                       sctp_sstate_name[s->state]);
            else
                printf("%-*s ", state_width, sstate_name[s->state]);
        }
    
        printf("%-6d %-6d ", s->rq, s->wq);
    }

根据s→local.family分别输出对应的内容，代码就不做过多的解释了，就是简单的switch case的判断．全部执行完毕之后，输出的结果是:

    
    
    Netid  State      Recv-Q Send-Q Local Address:Port                 Peer Address:Port               
    u_seq  ESTAB      0      0      @00017 309855                * 309856

可以发现其实在ss的默认输出情况下也是没有pid信息．如果我们采用`ss -p`，结果是:

    
    
    Netid  State      Recv-Q Send-Q Local Address:Port                 Peer Address:Port               
    u_seq  ESTAB      0      0      @00017 309855                * 309856                users:(("code",pid=17009,fd=17))
    u_seq  ESTAB      0      0      @00012 157444                * 157445                users:(("chrome",pid=5834,fd=10))

### user_ent_hash_build

当我们加了-p参数之后，程序运行的结果：

    
    
    case 'p':
        show_users++;
        user_ent_hash_build();
        break;

show_users的值变为１，程序接着执行 user_ent_hash_build()

    
    
    static void user_ent_hash_build(void)
    {
        const char *root = getenv("PROC_ROOT") ? : "/proc/";
        struct dirent *d;
        char name[1024];
        int nameoff;
        DIR *dir;
        char *pid_context;
        char *sock_context;
        const char *no_ctx = "unavailable";
        static int user_ent_hash_build_init;
    
        /* If show_users & show_proc_ctx set only do this once */
        if (user_ent_hash_build_init != 0)
            return;
    
        user_ent_hash_build_init = 1;
    
        strlcpy(name, root, sizeof(name));
    
        if (strlen(name) == 0 || name[strlen(name)-1] != '/')
            strcat(name, "/");
    
        nameoff = strlen(name);
    
        dir = opendir(name);
        if (!dir)
            return;
    
        while ((d = readdir(dir)) != NULL) {
            struct dirent *d1;
            char process[16];
            char *p;
            int pid, pos;
            DIR *dir1;
            char crap;
    
            if (sscanf(d->d_name, "%d%c", &pid, &crap) != 1)
                continue;
    
            if (getpidcon(pid, &pid_context) != 0)
                pid_context = strdup(no_ctx);
    
            snprintf(name + nameoff, sizeof(name) - nameoff, "%d/fd/", pid);
            pos = strlen(name);
            if ((dir1 = opendir(name)) == NULL) {
                free(pid_context);
                continue;
            }
    
            process[0] = '\0';
            p = process;
    
            while ((d1 = readdir(dir1)) != NULL) {
                const char *pattern = "socket:[";
                unsigned int ino;
                char lnk[64];
                int fd;
                ssize_t link_len;
                char tmp[1024];
    
                if (sscanf(d1->d_name, "%d%c", &fd, &crap) != 1)
                    continue;
    
                snprintf(name+pos, sizeof(name) - pos, "%d", fd);
    
                link_len = readlink(name, lnk, sizeof(lnk)-1);
                if (link_len == -1)
                    continue;
                lnk[link_len] = '\0';
    
                if (strncmp(lnk, pattern, strlen(pattern)))
                    continue;
    
                sscanf(lnk, "socket:[%u]", &ino);
    
                snprintf(tmp, sizeof(tmp), "%s/%d/fd/%s",
                        root, pid, d1->d_name);
    
                if (getfilecon(tmp, &sock_context) <= 0)
                    sock_context = strdup(no_ctx);
    
                if (*p == '\0') {
                    FILE *fp;
    
                    snprintf(tmp, sizeof(tmp), "%s/%d/stat",
                        root, pid);
                    if ((fp = fopen(tmp, "r")) != NULL) {
                        if (fscanf(fp, "%*d (%[^)])", p) < 1)
                            ; /* ignore */
                        fclose(fp);
                    }
                }
                user_ent_add(ino, p, pid, fd,
                        pid_context, sock_context);
                free(sock_context);
            }
            free(pid_context);
            closedir(dir1);
        }
        closedir(dir);
    }

这个解析方法与netstat中的prg_cache_load的方式类似．都是解析/proc/pid/fd下面的内容获得socket的inode编号．得到pid,inode和fd之后，调用user_ent_add()方法．

#### user_ent_add

    
    
    static void user_ent_add(unsigned int ino, char *process,
                        int pid, int fd,
                        char *proc_ctx,
                        char *sock_ctx)
    {
        struct user_ent *p, **pp;
    
        p = malloc(sizeof(struct user_ent));
        if (!p) {
            fprintf(stderr, "ss: failed to malloc buffer\n");
            abort();
        }
        p->next = NULL;
        p->ino = ino;
        p->pid = pid;
        p->fd = fd;
        p->process = strdup(process);
        p->process_ctx = strdup(proc_ctx);
        p->socket_ctx = strdup(sock_ctx);
    
        pp = &user_ent_hash[user_ent_hashfn(ino)];
        p->next = *pp;
        *pp = p;
    }

获取inode,pid和fd信息，最终组成一个链表．

#### proc_ctx_print

程序在输出结果的时候，调用proc_ctx_print()

    
    
    static void proc_ctx_print(struct sockstat *s)
    {
        char *buf;
    
        if (show_proc_ctx || show_sock_ctx) {
            if (find_entry(s->ino, &buf,
                    (show_proc_ctx & show_sock_ctx) ?
                    PROC_SOCK_CTX : PROC_CTX) > 0) {
                printf(" users:(%s)", buf);
                free(buf);
            }
        } else if (show_users) {
            if (find_entry(s->ino, &buf, USERS) > 0) {
                printf(" users:(%s)", buf);
                free(buf);
            }
        }
    }

如果show_users>0，执行find_entry(0，根据inode编号找到对应进程的信息：

#### find_entry

    
    
    static int find_entry(unsigned int ino, char **buf, int type)
    {
        struct user_ent *p;
        int cnt = 0;
        char *ptr;
        char *new_buf;
        int len, new_buf_len;
        int buf_used = 0;
        int buf_len = 0;
    
        if (!ino)
            return 0;
    
        p = user_ent_hash[user_ent_hashfn(ino)];
        ptr = *buf = NULL;
        while (p) {
            if (p->ino != ino)
                goto next;
    
            while (1) {
                ptr = *buf + buf_used;
                switch (type) {
                case USERS:
                    len = snprintf(ptr, buf_len - buf_used,
                        "(\"%s\",pid=%d,fd=%d),",
                        p->process, p->pid, p->fd);
                    break;
                case PROC_CTX:
                    len = snprintf(ptr, buf_len - buf_used,
                        "(\"%s\",pid=%d,proc_ctx=%s,fd=%d),",
                        p->process, p->pid,
                        p->process_ctx, p->fd);
                    break;
                case PROC_SOCK_CTX:
                    len = snprintf(ptr, buf_len - buf_used,
                        "(\"%s\",pid=%d,proc_ctx=%s,fd=%d,sock_ctx=%s),",
                        p->process, p->pid,
                        p->process_ctx, p->fd,
                        p->socket_ctx);
                    break;
                default:
                    fprintf(stderr, "ss: invalid type: %d\n", type);
                    abort();
                }
    
                if (len < 0 || len >= buf_len - buf_used) {
                    new_buf_len = buf_len + ENTRY_BUF_SIZE;
                    new_buf = realloc(*buf, new_buf_len);
                    if (!new_buf) {
                        fprintf(stderr, "ss: failed to malloc buffer\n");
                        abort();
                    }
                    *buf = new_buf;
                    buf_len = new_buf_len;
                    continue;
                } else {
                    buf_used += len;
                    break;
                }
            }
            cnt++;
    next:
            p = p->next;
        }
        if (buf_used) {
            ptr = *buf + buf_used;
            ptr[-1] = '\0';
        }
        return cnt;
    }

通过遍历p = user_ent_hash[user_ent_hashfn(ino)]; 这个链表得到得到所有的节点．然后利用

    
    
    p = user_ent_hash[user_ent_hashfn(ino)];
    ptr = *buf = NULL;
    while (p) {
        if (p->ino != ino)
            goto next;

如果遍历得到inode相等，那么就说明找到了pid，最终输出的结果如下:

    
    
    switch (type) {
                case USERS:
                    len = snprintf(ptr, buf_len - buf_used,
                        "(\"%s\",pid=%d,fd=%d),",
                        p->process, p->pid, p->fd);
                    break;

最终输出的结果是:

    
    
    Netid  State      Recv-Q Send-Q Local Address:Port                 Peer Address:Port               
    u_seq  ESTAB      0      0      @00017 309855                * 309856                users:(("code",pid=17009,fd=17))

## 总结

由于`ss`和`netstat`数据获取的方式不同，导致在执行效率上面存在很大的差别．`ss`和`netstat`这两种方式也我我们需要获取主机上面的网络数据提供了一个很好的思路．

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1014/>

