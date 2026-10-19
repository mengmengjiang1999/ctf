#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
#include <sys/time.h>
 
#include "data_type.h"
#include "cube.h"
#include "cube_define.h"
#include "cube_record.h"

#include "user_define.h"
#include "key_event_user.h"
// add para lib_include
RECORD(MESSAGE,INSTANCE_INFO) * _create_instance_info();
int key_event_user_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int key_event_user_start(void * sub_proc, void * para)
{
	int ret;
	void * recv_msg;
	int type;
	int subtype;
	// add yorself's module exec func here
	while(1)
	{
		usleep(time_val.tv_usec);
		ret=ex_module_recvmsg(sub_proc,&recv_msg);
		if(ret<0)
			continue;
		if(recv_msg==NULL)
			continue;
		type=message_get_type(recv_msg);
		subtype=message_get_subtype(recv_msg);
		if(!memdb_find_recordtype(type,subtype))
		{
			printf("message format (%d %d) is not registered!\n",
			message_get_type(recv_msg),message_get_subtype(recv_msg));
			ex_module_sendmsg(sub_proc,recv_msg);
			continue;
		}
		if((type==TYPE(GENERAL_RETURN))&&(subtype==SUBTYPE(GENERAL_RETURN,STRING)))
		{
            		ret=proc_pcrquote_user_cmd(sub_proc,recv_msg);
		}
        	else
			ex_module_sendmsg(sub_proc,recv_msg);
	}
	return 0;
}

int proc_pcrquote_user_cmd(void * sub_proc,void * recv_msg)
{
	int ret;
   	MSG_HEAD * msg_head;
	RECORD(GENERAL_RETURN,STRING) * keyevent_cmd;
        RECORD(GENERAL_RETURN,UUID) * external_data;
	MSG_EXPAND * msg_expand;
	printf("enter pcrquote report in key_event_user\n");
	ret=message_get_record(recv_msg,&keyevent_cmd,0);
	if(ret<0)
		return ret;
        ret=message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(GENERAL_RETURN,UUID));
        if(msg_expand != NULL)
        {
 		external_data=msg_expand->expand;   		
	}
        void * send_msg = message_create(TYPE_PAIR(GENERAL_RETURN,STRING),NULL);
        if(send_msg == NULL)
              return -EINVAL;
	RECORD(GENERAL_RETURN,STRING) * pcrquote_cmd;
        pcrquote_cmd = Talloc0(sizeof(*pcrquote_cmd));
        if(pcrquote_cmd==NULL)
            return -ENOMEM;
        pcrquote_cmd->name=dup_str("pcrquote",0);
        pcrquote_cmd->return_value = dup_str(keyevent_cmd->return_value,0);
        message_add_record(send_msg,pcrquote_cmd);
        message_add_expand_data(send_msg,TYPE_PAIR(GENERAL_RETURN,UUID),external_data);
        RECORD(MESSAGE,INSTANCE_INFO) * instance_info = _create_instance_info();
        if(instance_info!=NULL)
	{
             message_add_expand_data(send_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),
		instance_info);
	}
    	return ex_module_sendmsg(sub_proc,send_msg);
}

RECORD(MESSAGE,INSTANCE_INFO) * _create_instance_info()
{
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	
    RECORD(USER_DEFINE,CLIENT_STATE) * client_state;

    printf( " enter _create_instance_info\n");
    instance_info = Talloc0(sizeof(*instance_info));
    if(instance_info == NULL)
        return NULL;
    // get client state
	client_state = proc_share_data_getpointer();
    // file the instance_info struct 
    printf( " client_state addr %p\n",client_state);
	proc_share_data_getvalue("proc_name",instance_info->proc_name);
	Strncpy(instance_info->user_name,client_state->user_name,DIGEST_SIZE);
	proc_share_data_getvalue("uuid",instance_info->node_uuid);
    printf( " create instance_info finished\n");

    return instance_info;
    // file the instance_info struct 
}
