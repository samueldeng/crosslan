import logging

logging.basicConfig(format='[%(levelname)s]\t%(asctime)s\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
log = logging.getLogger("rcparser")


class ConfParser():
    def __init__(self):
        pass

    @staticmethod
    def read(file_path):
        try:
            conf_map = []
            f = open(file_path)
            lines = f.readlines()

            for line in lines:
                # Trim space
                line = line.replace(" ", "").strip('\n')

                parameter = line[0:line.find("=")]
                values = line[line.find("=") + 1:].split(",")

                conf_map.append((parameter, values[0])) if len(values) == 1 \
                    else conf_map.append((parameter, values))

            return conf_map
        except Exception, e:
            raise e


    @staticmethod
    def write(obj, file_path):
        try:
            lines = ""
            for (key, value) in obj:
                line = str(key) + " = "
                if not isinstance(value, list):
                    line += str(value) + "\n"
                else:
                    for v in value[:-1]:
                        line += str(v) + ","
                    line += str(value[-1]) + "\n"

                lines += line

            f = open(file_path, "w")
            f.writelines(lines)
        except Exception, e:
            raise e


def unit_test():
    confpar = ConfParser()
    map = confpar.read("/home/samuel/github/crosslan/bin/cl_container_10099/rc")

    print map
    conf = [
        ('blockedFile', './blocked'),
        ('directFile', './direct'),
        ('allowedClient', ['115.154.123.144', '202.117.10.144']),
        ('loadBalance', 'hash'),
        ('userPasswd', 'samueldeng:samueldeng'),
        ('statFile', './stat'),
        ('proxy', 'ss://aes-256-cfb:XJTU8266@1.1.1.1:12343'),
        ('proxy', 'ss://aes-256-cfb:XJTU8266@1.1.1.1:12343'),
        ('listen', 'http://202.117.15.79:10099'),
    ]
    confpar.write(map, "/home/samuel/github/crosslan/bin/cl_container_10099/rc_test")
    confpar.write(conf, "/home/samuel/github/crosslan/bin/cl_container_10099/rc_test_1")


if __name__ == "__main__":
    unit_test()
