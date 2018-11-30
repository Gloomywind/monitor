import time, os, commands, socket
class Monitor():
        cpu_info = {}

        _cpu_info_path = "/proc/cpuinfo"
        _cpu_usage_info_path = "/proc/stat"
        _mem_usage_info_path = "/proc/meminfo"
        _net_usage_info_path = "/proc/net/dev"
        _load_avg_info_path = "/proc/loadavg"


        _f_cpu_usage = None
        _f_mem_usage = None
        _f_net_usage = None
        _p_io_usage = None

        _last_cpu_total = None
        _last_cpu_idle = None 


        _last_net_record_time = None
        _last_net_insize_1 = None
        _last_net_outsize_1 = None



        def __init__(self):
                self._open_files()
                self._init_calc_cpu()
                self._init_calc_net()
                self.band_width = 1000
                self.open_ports = []
                self.df = None

        def set_band_width(self, band):
                self.band_width = band 


        def _init_calc_cpu(self):
                if not self._f_cpu_usage:
                        self._open_files("_f_cpu_usage")

                line_arr = self._f_cpu_usage.readline().split()
                cpu_stat_arr1 = list(map(int, line_arr[1:]))

                self._last_cpu_total = sum(cpu_stat_arr1)
                self._last_cpu_idle = cpu_stat_arr1[3]
                self._f_cpu_usage.seek(0, 0)


        def _init_calc_net(self):
                if not self._f_net_usage:
                        self._open_files("_f_net_usage")
                self._last_net_record_time = time.time()
                net_info1 = []
                i = 1
                for line in self._f_net_usage.readlines():
                        if i == 3:
                                net_info1 = line.split()
                                break
                        else:
                                i += 1
                self._last_net_insize_1 = int(net_info1[1])
                self._last_net_outsize_1 = int(net_info1[9])
                self._f_net_usage.seek(0, 0)



        def _open_files(self, files=None):
                if not files:
                        self._f_cpu_usage = open(self._cpu_usage_info_path, 'r')
                        self._f_mem_usage = open(self._mem_usage_info_path, 'r')
                        self._f_net_usage = open(self._net_usage_info_path, 'r')
                        if not self._f_cpu_usage or not self._f_mem_usage or not self._f_net_usage:
                                exit(1)
                else:
                        if files == "_f_cpu_usage":
                                self._f_cpu_usage = open(self._cpu_usage_info_path, 'r')
                                if not self._f_cpu_usage:
                                        exit(1)
                        elif files == "_f_mem_usage":
                                self._f_mem_usage = open(self._mem_usage_info_path, 'r')
                                if not self._f_mem_usage:
                                        exit(1)
                        elif files == "_f_net_usage":
                                self._f_net_usage = open(self._net_usage_info_path, 'r')
                                if not self._f_net_usage:
                                        exit(1)
                        else:
                                return

        def get_cpu_info( self,  category ):
                if self.cpu_info and category in self.cpu_info:
                        return self.cpu_info[category]
                elif self.cpu_info:
                        print(self.cpu_info)
                        return None
                else:
                        with open( self._cpu_info_path, 'r' ) as f:
                                for line in f.readlines():
                                        line_arr = line.split(':')
                                        if len(line_arr) > 1:
                                                self.cpu_info[line_arr[0].strip()] = line_arr[1].strip()
                return self.cpu_info[category]

        def get_cpu_usage_info(self):
                if not self._f_cpu_usage:
                        self._open_files("_f_cpu_usage")

                cpu_stat_arr2 = []
                line_arr = self._f_cpu_usage.readline().split()
                cpu_stat_arr2 = list(map(int, line_arr[1:]))
                cur_cpu_total = sum(cpu_stat_arr2)
                cur_cpu_idle = cpu_stat_arr2[3]

                total = cur_cpu_total - self._last_cpu_total 
                if total == 0:
                        return 0.0
                idle = cur_cpu_idle - self._last_cpu_idle
                pcpu = 100 * (total - idle) / total

                self._last_cpu_total = cur_cpu_total
                self._last_cpu_idle = cur_cpu_idle
                #print("total = %d idle = %d pcpu = %f%% " % (total, idle, pcpu))
                self._f_cpu_usage.seek(0, 0)
                return pcpu

        def get_mem_usage_info(self):
                if not self._f_mem_usage:
                        self._open_files("_f_mem_usage")

                mem_info_dic = {}
                for line in self._f_mem_usage.readlines():
                        line_arr = line.split(':')
                        mem_info_dic[line_arr[0]] = int(line_arr[1].split()[0])
                #print(mem_info_dic)
                MemTotal = mem_info_dic["MemTotal"]
                MemFree = mem_info_dic["MemFree"]
                Buffers = mem_info_dic["Buffers"]
                Cached = mem_info_dic["Cached"]
                pmem = 100 * (MemTotal - (MemFree+Buffers+Cached)) / MemTotal
                self._f_mem_usage.seek(0, 0)
                return pmem

        def get_net_usage_info(self):
                if not self._f_net_usage:
                        self._open_files("_f_net_usage")
                cur_net_record_time = time.time()

                i = 1 
                net_info2 = []

                for line in self._f_net_usage.readlines():
                        if i == 3:
                                net_info2 = line.split()
                                break
                        else:
                                i += 1
                insize_2 = int(net_info2[1])
                outsize_2 = int(net_info2[9])

                numbers = (insize_2 + outsize_2 - self._last_net_insize_1 - self._last_net_outsize_1) * 8
                time_width = cur_net_record_time - self._last_net_record_time
                pnet = 100 * (numbers/time_width)/(1000000*self.band_width)
                if pnet > 100: pnet = 100.00
                self._f_net_usage.seek(0, 0)

                self._last_net_insize_1 = insize_2
                self._last_net_outsize_1 = outsize_2
                self._last_net_record_time = cur_net_record_time

                return pnet

        def get_io_usage_info(self):
                if self._last_io_usage > 100:
                        self._last_io_usage = 100.00
                return self._last_io_usage

        def get_load_avg_info(self):
                load_avg_info = []
                with open(self._load_avg_info_path, 'r' ) as f:
                        load_avg_info = f.read().split()
                return float(load_avg_info[0])

        def get_port(self):
            output = commands.getoutput("netstat -ntpl| grep -v tcp6 | grep -v 127.0.0.1|awk {'print $4'}")
            port_res = output.split('\n')[2:]
            open_ports = []
            for i in port_res:
                port = i.split(':')[1]
                open_ports.append(port)
            return open_ports

        def get_df(self):
            df_res = commands.getoutput("df -h | awk {'print $5, $6'}").split('\n')[1:]
            for i in df_res:
                df = i.split(' ')
                if df[1] == '/':
                    return df[0]

        def get_hostname(self):
            return socket.gethostname()
        
        def get_time(self):
            return time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(time.time()))



monitor = Monitor()
