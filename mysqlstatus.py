#!/usr/local/bin/python3.6
# _*_ coding: utf-8 _*_
"""
Author: Vincent.He
Version: 1.2
CreateDate: 2019-10-20
"""
import datetime
import pymysql
import sys
import getopt

#<editor-fold desc="get input parameters">
def usage():
    print('Please usage ./script -u|--user -p|--password -H|--host -P|--port ')

try:
    # ':' has value
    opts,args = getopt.getopt(sys.argv[1:], "-u:-p:-H:-P:", ["user=","password=","host=","port="])
    if len(sys.argv) == 1:
        print("Incorrect number of parameter digits!")
        usage()
        exit()
    if len(sys.argv) != 9:
        print("Incorrect number of parameter digits!")
        usage()
        exit()
except getopt.GetoptError:
    usage()
    exit()

for opt,arg in opts:
    if opt in ('-h', "--help"):
        usage()
    elif opt in ('-u', "--user"):
        user = arg
    elif opt in ('-p', "--password"):
        passwd = arg
    elif opt in ('-H', "--host"):
        host = arg
    elif opt in ('-P', "--port"):
        port = arg
    else:
        usage()
#</editor-fold>

#<editor-fold desc="common function">
# dict contain tuple print
def dictcontaintupleprint(dicts):
    for key in dicts:
        print(key + ": " + dicts[key][0][1])
# dict print
def dictprint(dicts):
    for key in dicts:
        print(key + ": " + str(dicts[key]))
# unit convert
def unitconvert(tuple,unit):
    if unit == "M":
        value = int(tuple[0][1]) / 1024 / 1024
        return ((tuple[0][0], str(round(value)) + "M"),)
    elif unit == "G":
        value = int(tuple[0][1]) / 1024 / 1024 / 1024
        return ((tuple[0][0], str(round(value)) + "G"),)
    else:
        value = 0
        return ((tuple[0][0], value),)
#</editor-fold>

#<editor-fold desc="operation database base function">
def getsingle(sql,db="mysql"):
    conn = pymysql.connect(host="{0}".format(host), port=int(port), user="{0}".format(user),passwd="{0}".format(passwd), db="{0}".format(db),charset="utf8")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchone()
        return results[1]
    except Exception as e:
        print(str(e))
    finally:
        cursor.close()
        conn.close()

def getall(sql,db="mysql"):
    conn = pymysql.connect(host="{0}".format(host), port=int(port), user="{0}".format(user), passwd="{0}".format(passwd),db="{0}".format(db), charset="utf8")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(str(e))
    finally:
        cursor.close()
        conn.close()
#</editor-fold>

#<editor-fold desc="get status function">
# TPS
def gettps():
    com_commit = getsingle("SHOW GLOBAL STATUS LIKE 'Com_commit';")
    com_rollback = getsingle("SHOW GLOBAL STATUS LIKE 'Com_rollback';")
    uptime = getsingle("SHOW GLOBAL STATUS LIKE 'Uptime';")
    return round((int(com_commit) + int(com_rollback)) / int(uptime))
# QPS
def getqps():
    questions = getsingle("SHOW GLOBAL STATUS LIKE 'Questions';")
    uptime = getsingle("SHOW GLOBAL STATUS LIKE 'Uptime';")
    return round(int(questions) / int(uptime))
# all users
def getalluser():
    users = getall("SELECT DISTINCT CONCAT('user: ''',USER,'''@''',HOST,''';') AS QUERY FROM user;")
    return users
# threads
def getthreads():
    threads_cached = getall("show status like 'Threads%';")
    return threads_cached
# function by key_buffer hits
def getkeybuffer():
    read_requests = getall("show status like 'Key_read_requests';")
    reads = getall("show status like 'Key_reads';")
    write_requests = getall("show status like 'Key_write_requests';")
    writes = getall("show status like 'Key_writes';")
    if reads[0][1] > "0" and read_requests[0][1] > "0" and writes[0][1] > "0" and write_requests[0][1]:
        readhits = round((1 - int(reads[0][1]) / int(read_requests[0][1])) * 100)
        writehits = round((1 - int(writes[0][1]) / int(write_requests[0][1])) * 100)
        return {"key_buffer_read_hits":str(readhits) + "%","key_buffer_write_hits":str(writehits) + "%"}
    else:
        return {"key_buffer_read_hits": "0%", "key_buffer_write_hits": "0%"}
# function by Innodb buffer hits
def getinnodbbuffer():
    innodbbufferpoolreads = getall("show status like 'Innodb_buffer_pool_reads';")
    innodbbufferpoolreadrequests = getall("show status like 'Innodb_buffer_pool_read_requests';")
    if innodbbufferpoolreads[0][1] > "0" and innodbbufferpoolreadrequests[0][1] > "0":
        innodbbufferreadhits = round((1 - int(innodbbufferpoolreads[0][1]) / int(innodbbufferpoolreadrequests[0][1])) * 100)
        return {"innodb_buffer_read_hits": str(innodbbufferreadhits) + "%"}
    else:
        return {"innodb_buffer_read_hits": "0%"}
# function by Query cache hits
def getquerycachehits():
    qcache_hits = getall("show status like 'Qcache_hits';")
    qcache_inserts = getall("show status like 'Qcache_inserts';")
    if qcache_hits[0][1] > "0" and qcache_inserts[0][1] > "0":
        querycachehits = round((int(qcache_hits[0][1]) / (int(qcache_hits[0][1]) + int(qcache_inserts[0][1]))) * 100)
        return {"query_cache_hits": str(querycachehits) + "%"}
    else:
        return {"query_cache_hits": "0%"}
# function by table cache
def gettablecache():
    tablecache = getall("show status like 'open%';")
    return tablecache
# function by thread cache
def getthreadcache():
    threads_created = getall("show status like 'Threads_created';")
    connections = getall("show status like 'Connections';")
    if int(threads_created[0][1]) > 0 and int(connections[0][1]) > 0:
        thread_cache_hits = round((1 - int(threads_created[0][1]) / int(connections[0][1])) * 100)
        return {"thread_cache_hits":str(thread_cache_hits) + "%"}
    else:
        return {"thread_cache_hits": "0%"}
# function by lock status
def getlockstatus():
    lockstatus = getall("show status like '%lock%';")
    return lockstatus
# function by tmp table
def gettmptable():
    tmptable = getall("SHOW STATUS LIKE 'Created_tmp%';")
    return tmptable
# function by binlog cache
def getbinlogcache():
    binlogcache = getall("SHOW STATUS LIKE 'Binlog_cache%';")
    return binlogcache
# function by innodb log waits
def getinnodblogwaits():
    innodblogwaits = getall("SHOW STATUS LIKE 'innodb_log_waits';")
    return innodblogwaits
#</editor-fold>

#<editor-fold desc="get config function">
# data dir config
def getdatadir():
    datadir = getsingle("show variables like '%datadir%';")
    return datadir
# charcter config
def getcharcter():
    characters = getall("show variables like 'character%';")
    return characters
# collation config
def getcollation():
    collaction = getall("show variables like 'collation%';")
    return collaction
# connection config
def getconnectionconfig():
    max_connections = getall("show global variables like 'max_connections';")
    max_connect_errors = getall("show global variables like 'max_connect_errors';")
    interactive_timeout = getall("show global variables like 'interactive_timeout';")
    wait_timeout = getall("show global variables like 'wait_timeout';")
    skip_name_resolve = getall("show global variables like 'skip_name_resolve';")
    back_log = getall("show global variables like 'back_log';")
    return {"max_connections":max_connections,"max_connect_errors":max_connect_errors,"interactive_timeout":interactive_timeout,"wait_timeout":wait_timeout,"skip_name_resolve":skip_name_resolve,"back_log":back_log}
# log config
def getlogconfig():
    # general log
    general_log = getall("SHOW GLOBAL VARIABLES LIKE 'general_log';")
    general_log_file = getall("SHOW GLOBAL VARIABLES LIKE 'general_log_file';")
    # slow log
    slow_query_log = getall("SHOW GLOBAL VARIABLES LIKE 'slow_query_log';")
    slow_query_log_file = getall("SHOW GLOBAL VARIABLES LIKE 'slow_query_log_file';")
    long_query_time = getall("SHOW GLOBAL VARIABLES LIKE 'long_query_time';")
    log_queries_not_using_indexes = getall("SHOW GLOBAL VARIABLES LIKE 'log_queries_not_using_indexes';")
    # error log
    log_error = getall("SHOW GLOBAL VARIABLES LIKE 'log_error';")
    # binlog
    log_bin = getall("SHOW GLOBAL VARIABLES LIKE 'log_bin';")
    binlog_format = getall("SHOW GLOBAL VARIABLES LIKE 'binlog_format';")
    sync_binlog = getall("show global variables like 'sync_binlog';")
    expire_logs_day = getall("SHOW GLOBAL VARIABLES LIKE 'expire_logs_days';")
    max_binlog_size = getall("show global variables like 'max_binlog_size';")
    return {"general_log":general_log,"general_log_file":general_log_file,"slow_query_log":slow_query_log,"slow_query_log_file":slow_query_log_file,
            "long_query_time":long_query_time,"log_queries_not_using_indexes":log_queries_not_using_indexes,"log_error":log_error,"log_bin":log_bin,
            "binlog_format":binlog_format,"sync_binlog":sync_binlog,"expire_logs_day":expire_logs_day,"max_binlog_size":unitconvert(max_binlog_size,"G")}
# cache config
def getcacheconfig():
    thread_cache_size = getall("show global variables like 'thread_cache_size';")
    query_cache_type = getall("show global variables like 'query_cache_type';")
    query_cache_size = getall("show global variables like 'query_cache_size';")
    query_cache_limit = getall("show global variables like 'query_cache_limit';")
    sort_buffer_size = getall("show global variables like 'sort_buffer_size';")
    read_buffer_size = getall("show global variables like 'read_buffer_size';")
    return {"thread_cache_size":thread_cache_size,"query_cache_type":query_cache_type,"query_cache_size":unitconvert(query_cache_size,"M"),"query_cache_limit":unitconvert(query_cache_limit,"M"),"sort_buffer_size":unitconvert(sort_buffer_size,"M"),"read_buffer_size":unitconvert(read_buffer_size,"M"),}
# innodb config
def getinnodbconfig():
    innodb_buffer_pool_size = getall("show global variables like 'innodb_buffer_pool_size';")
    innodb_buffer_pool_instances = getall("show global variables like 'innodb_buffer_pool_instances';")
    innodb_flush_method = getall("show global variables like 'innodb_flush_method';")
    innodb_log_buffer_size = getall("show global variables like 'innodb_log_buffer_size';")
    innodb_flush_log_at_trx_commit = getall("show global variables like 'innodb_flush_log_at_trx_commit';")
    return {"innodb_buffer_pool_size":unitconvert(innodb_buffer_pool_size,"G"),"innodb_buffer_pool_instances":innodb_buffer_pool_instances,"innodb_flush_method":innodb_flush_method,"innodb_log_buffer_size":unitconvert(innodb_log_buffer_size,"M"),"innodb_flush_log_at_trx_commit":innodb_flush_log_at_trx_commit}

#</editor-fold>

#<editor-fold desc="call function">
############################################
# MySQL status                            ##
############################################
# threads
print("####threads####")
for ths in getthreads():
    print(ths[0] + ": " + ths[1])
# tps
print("####TPS####")
print("TPS: {0}".format(gettps()))
# qps
print("####QPS####")
print("QPS: {0}".format(getqps()))
# key_buffer hits
print("####key_buffer hits####")
dictprint(getkeybuffer())
# Innodb buffer hits
print("####Innodb buffer hits####")
dictprint(getinnodbbuffer())
# Query cache hits
print("####Query cache hits####")
dictprint(getquerycachehits())
# table cache
print("####table cache####")
for tablecache in gettablecache():
    print(tablecache[0] + ": " + tablecache[1])
# thread cache hits
print("####thread cache hits####")
dictprint(getthreadcache())
# lock status
print("####lock status####")
for locks in getlockstatus():
    print(locks[0] + ": " + locks[1])
# tmp table
print("####tmp table####")
for tmp in gettmptable():
    print(tmp[0] + ": " + tmp[1])
# binlog cache
print("####binlog cache####")
for binlogcache in getbinlogcache():
    print(binlogcache[0] + ": " + binlogcache[1])
# innodb log waits
print("####innodb log waits####")
for innodblogwait in getinnodblogwaits():
    print(innodblogwait[0] + ": " + innodblogwait[1])
############################################
# MySQL config                            ##
############################################
# datadir
print("####datadir####")
for charcter in getcharcter():
    print(charcter[0] + ": " + charcter[1])
# collation
print("####collation####")
for collation in getcollation():
    print(collation[0] + ": " + collation[1])
# users
print("####users####")
for userinfo in getalluser():
    print(userinfo[0])
# connections config....
print("####connections config.....####")
connections = getconnectionconfig()
dictcontaintupleprint(connections)
# log config.....
print("####log config.....####")
logconfigs = getlogconfig()
dictcontaintupleprint(logconfigs)
# cache config....
print("####cache config.....####")
cacheconfigs = getcacheconfig()
dictcontaintupleprint(cacheconfigs)
# innodb config ....
print("####innodb config.....####")
innodbconfigs = getinnodbconfig()
dictcontaintupleprint(innodbconfigs)
#</editor-fold>