#! /usr/bin/python3
# coding=utf8

from SysMonitor import monitor
import time, json
import urllib2


def get_info():
        info_dic = {
                "model_name"    :       monitor.get_cpu_info(category="model name"),
                "cpu_usage"             :       monitor.get_cpu_usage_info(), 
                "mem_usage"             :       monitor.get_mem_usage_info(),
                "net_usage"             :       monitor.get_net_usage_info(),
                "disk_usage"            :       monitor.get_df(),
                "port_usage"            :       monitor.get_port()
                "ip"                    :       '127.0.0.1'
        }
        print(info_dic)
        return info_dic

if __name__ == "__main__":
    info = get_info()
    url = "http://127.0.0.1/api/post/status"
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',"Content-Type": "application/json"}
    post_data = json.dumps(info)
    try:
        req = urllib2.Request(url, data=post_data, headers=header)
        res = urllib2.urlopen(req)
        print res.read()
    except Exception, e:
        print e.message
