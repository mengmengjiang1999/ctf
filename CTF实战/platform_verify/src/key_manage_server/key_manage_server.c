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

#include "tcm_constants.h"
#include "tcm_structures.h"
#include "tcmfunc.h"
#include "tcm_cube_struct.h"
#include "tcm_key_manage.h"
#include "tcm_key_desc.h"
#include "tcm_pik_desc.h"

#include "key_manage_server.h"
// add para lib_include

RECORD(TCM_KEY_DESC,LOCAL_KEYSET) * local_keyset_get (char * name);
RECORD(TCM_KEY_DESC,REMOTE_KEYSET) * remote_keyset_get (BYTE *uuid,char * name);

BYTE external_data_store[DIGEST_SIZE];

int key_manage_server_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int key_manage_server_start(void * sub_proc, void * para)
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
			continue;
		}
		if((type==TYPE(GENERAL_RETURN))&&(subtype==SUBTYPE(GENERAL_RETURN,STRING)))
		{
			ret=proc_keymanage_cmd(sub_proc,recv_msg);
		}
        else
        {
	        ret=ex_module_sendmsg(sub_proc,recv_msg);
        }
	}
	return 0;
}

int proc_keymanage_cmd(void * sub_proc,void * recv_msg)
{
	int ret;
	RECORD(GENERAL_RETURN,STRING) * keymanage_cmd;
	ret=message_get_record(recv_msg,&keymanage_cmd,0);
	if(ret<0)
		return ret;
    	printf("enter the keymanage server  cmd!\n");

    	if(Strcmp(keymanage_cmd->name,"pcrquote-req")==0)
        	return proc_keymanage_quote_nonce(sub_proc,keymanage_cmd,recv_msg);
    	else if(Strcmp(keymanage_cmd->name,"pcrquote")==0)
        	return proc_keymanage_quote_store(sub_proc,keymanage_cmd,recv_msg);
    	return ex_module_sendmsg(sub_proc,recv_msg);
}
	
int proc_keymanage_quote_nonce(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    	MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    	printf("enter pcr quote nonce function!\n");

                // generate external random data
        RECORD(GENERAL_RETURN,UUID) * external_data;
        external_data=Talloc0(sizeof(*external_data));
        external_data->name=dup_str("pcrquote",0);
        RAND_bytes(external_data->return_value,DIGEST_SIZE);
        Memcpy(external_data_store,external_data->return_value,DIGEST_SIZE);
        ret = message_add_expand_data(recv_msg,TYPE_PAIR(GENERAL_RETURN,UUID),
		external_data);
	if(ret<0)
		return ret;
	ret=ex_module_sendmsg(sub_proc,recv_msg);
	return ret;
}

int proc_keymanage_quote_store(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    	MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	
        RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;

    	printf("enter pcr quote store function!\n");

    	ret = message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE));
	if(ret<0)
        	return ret;
        // prepare to verify quote report

        quote_report=msg_expand->expand;
        DB_RECORD * db_record;
        db_record = memdb_store(quote_report,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),NULL);
        if(db_record == NULL)
        {
        	printf("server: store quote report failed!\n");
        }
        void * type_msg = message_gen_typesmsg(TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),NULL);  
	ex_module_sendmsg(sub_proc,type_msg);
	usleep(100*1000);
	
	ret=ex_module_sendmsg(sub_proc,recv_msg);
    	return ret;
}
RECORD(TCM_KEY_DESC,LOCAL_KEYSET) * local_keyset_get (char * name)
{
	int ret;
	RECORD(TCM_KEY_DESC,LOCAL_KEYSET ) * local_keyset;
	DB_RECORD * db_record;
	char buf[DIGEST_SIZE];
	int i;
	db_record=memdb_find_first(TYPE_PAIR(TCM_KEY_DESC,LOCAL_KEYSET),"user_name",name);
	if(db_record==NULL)
		return NULL;
	return db_record->record;
}

RECORD(TCM_KEY_DESC,REMOTE_KEYSET) * remote_keyset_get (BYTE *uuid,char * name)
{
	int ret;
	RECORD(TCM_KEY_DESC,REMOTE_KEYSET ) * remote_keyset;
	DB_RECORD * db_record;
	char buf[DIGEST_SIZE];
	int i;
	remote_keyset=memdb_get_first_record(TYPE_PAIR(TCM_KEY_DESC,REMOTE_KEYSET));
	while(remote_keyset!=NULL)
	{
		ret=0;
		if(uuid!=NULL)
		{
			if(Memcmp(uuid,remote_keyset->node_uuid,DIGEST_SIZE)==0)
				ret=1;
			else
				ret=-1;
		}
		if(name!=NULL)
		{
			if(Strncmp(name,remote_keyset->user_name,DIGEST_SIZE)==0)
			{
				if(uuid==NULL)
					ret=1;
			}
			else
				ret=0;

		}
		if(ret==1)
			break;
		remote_keyset=memdb_get_next_record(TYPE_PAIR(TCM_KEY_DESC,REMOTE_KEYSET));
		
	}

	return remote_keyset;
}
