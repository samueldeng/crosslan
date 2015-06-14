import getopt
import subprocess
from time import sleep
import traceback
import json
import logging
import os
import sys

from flask import Flask, request
from flask.ext.restful import abort, Api, Resource
import iptc
import signal

import rcparser
import iptman

headquarter_app = Flask(__name__)
headquarter_controller = Api(headquarter_app)

# Common Logger.
logging.basicConfig(format='[%(levelname)s]\t%(asctime)s\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
log = logging.getLogger("headquarter")

# Data Usage Logger.
du_log = logging.getLogger("du_logger")
du_log.setLevel(logging.INFO)
fh = logging.FileHandler('du.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter('%(asctime)s\t %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
du_log.addHandler(fh)


# Proxy Server List [str]
ss_lists = []
cl_container_home = os.environ["CL_CONTAINERS_HOME"]

# Cow Process and Port Mapping. int{port}--->Process
cow_process = {}
for i in range(10001, 10100):
    cow_process[i] = None


# URL: /cl-containers/<int:port>
class CrossLanContainers(Resource):
    def post(self, port):
        try:
            log.debug("CrossLanContainers.POST")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))

            iptables_manager = iptman.IptMan()
            conf_parser = rcparser.ConfParser()

            # Add rc File into User's Home.
            filename = cl_container_home + "/cl_container_" + str(port) + "/rc"

            if os.path.exists(filename):
                os.remove(filename)
            iptables_manager.delete_rule(port)

            # New Configuration File for this User.
            rc_conf = [
                ('listen', ['http://202.117.15.79:' + str(port)]),
                ('loadBalance', ['hash']),
            ]
            for ss in ss_lists:
                rc_conf.append(("proxy", ss))

            conf_parser.write(rc_conf, filename)

            # New Rule for port.
            iptables_manager.insert_rule(port)

            return None, 201

        except Exception, e:
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            log.error(traceback.format_exc())
            abort(400, message="Exception")


# URL: /cl-containers/<int:port>/running-status
class CrossLanContainerRunningStatus(Resource):
    def put(self, port):
        try:
            log.debug("CrossLanContainerRunningStatus.PUT")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))
            data = json.loads(request.get_data())
            log.debug("POST DATA JSON: " + str(data))
            action = data["action"]

            if action == "start":
                if cow_process[port] is None:
                    sleep(0.5)
                    wd = cl_container_home + "/cl_container_" + str(port) + "/"
                    cow_process[port] = subprocess.Popen(["./cow", "-rc", "./rc"], cwd=wd, stdout=subprocess.PIPE)
                    return None, 201
                else:
                    return {"error": "AlreadyStart"}, 201

            if action == "stop":
                if cow_process[port] is not None:
                    sleep(0.5)
                    cow_p = cow_process[port]
                    log.debug(cow_p)
                    cow_p.terminate()
                    cow_process[port] = None
                    return None, 201
                else:
                    return {"error": "AlreadyStop"}, 201

            if action == "restart":
                if cow_process[port] is not None:
                    wd = cl_container_home + "/cl_container_" + str(port) + "/"

                    cow_p = cow_process[port]
                    cow_p.terminate()
                    sleep(0.5)
                    cow_process[port] = subprocess.Popen(["./cow", "-rc", "./rc"], cwd=wd)
                    return None, 201
                else:
                    return {"error": "AlreadyStop"}, 401
            else:
                abort(400, message="Wrong Action.")
        except Exception, e:
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            log.error(traceback.format_exc())
            abort(400, message="Exception")

    def get(self, port):
        log.debug("CrossLanContainerRunningStatus.get")
        log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))

        try:
            if cow_process.get(port) is not None:
                return {"status": "running"}, 201
            else:
                return {"status": "stop"}, 201
        except Exception, e:
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            log.error(traceback.format_exc())
            abort(400, message="Exception")


# URL: cl-containers/<int:port>/binding-ips
class CrossLanContainerBindingIps(Resource):
    def put(self, port):
        try:
            log.debug("CrossLanContainerBindingIps.put")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))
            ipsets = json.loads(request.get_data())["ipset"]
            ipsets = [x.encode('UTF8') for x in ipsets]
            log.debug(ipsets)

            rc_parser = rcparser.ConfParser()
            rc_file = cl_container_home + "/cl_container_" + str(port) + "/rc"
            conf_for_ipsets = rc_parser.read(rc_file)

            exist_flag = False
            for index, (key, value) in enumerate(conf_for_ipsets):
                if key == "allowedClient":
                    conf_for_ipsets[index] = ("allowedClient", ipsets)
                    exist_flag = True

            if not exist_flag:
                conf_for_ipsets.append(("allowedClient", ipsets))

            log.debug(conf_for_ipsets)
            rc_parser.write(conf_for_ipsets, rc_file)

            return None, 201

        except Exception, e:
            log.error(traceback.format_exc())
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            abort(400, message="Exception")


# URL: cl-containers/<int:port>/data-usage
class CrossLanContainerDataUsage(Resource):
    def get(self, port):
        # TODO logging module.
        try:
            log.debug("CrossLanContainerDataUsage.get")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))

            iptables_manager = iptman.IptMan()
            bytes_counts = iptables_manager.get_rule_counter(port)

            # Reset Counter
            iptables_manager.delete_rule(port)
            iptables_manager.insert_rule(port)

            # Logger
            du_log.info("port:" + str(port) + "\t" + "data:" + str(bytes_counts))

            return {"data-usage": bytes_counts}, 201
        except Exception, e:
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            log.error(traceback.format_exc())
            abort(400, message="Exception")

class CrossLanContainerUserPasswd(Resource):
    def put(self, port):
        try:
            log.debug("CrossLanContainerUserPasswd.put")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))
            userpasswd = json.loads(request.get_data())["userpasswd"]
            log.debug(userpasswd)

            # TODO Delete.

            # TODO verify.
            rc_parser = rcparser.ConfParser()
            conf_file = cl_container_home + "/cl_container_" + str(port) + "/rc"
            conf_for_userpasswd = rc_parser.read(conf_file)

            exist_flag = False
            for index, (key, value) in enumerate(conf_for_userpasswd):
                if key == "userPasswd":
                    conf_for_userpasswd[index] = ("userPasswd", userpasswd)
                    exist_flag = True

            if not exist_flag:
                conf_for_userpasswd.append(("userPasswd", userpasswd))

            rc_parser.write(conf_for_userpasswd, conf_file)
            log.debug(conf_for_userpasswd)

            return None, 201

        except Exception, e:
            log.error(traceback.format_exc())
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            abort(400, message="Exception")


def check_accounting_rules():
    try:
        # TODO move to iptman
        existed_port = {}
        for index in range(10001, 10100):
            existed_port[str(index)] = False

        filter_table = iptc.Table(iptc.Table.FILTER)
        output_chain = iptc.Chain(filter_table, "OUTPUT")

        # Mark Port Already Create.
        for rule in output_chain.rules:
            sport = str(rule.matches[0].parameters["sport"])
            existed_port[sport] = True

        for (port, isExist) in existed_port.iteritems():
            if not isExist:
                iptman.IptMan().insert_rule(port)

    except Exception, e:
        log.error(traceback.format_exc())
        log.error(e.message)
        sys.exit(2)


def rest_server():
    try:
        headquarter_controller.add_resource(CrossLanContainers, "/cl-containers/<int:port>")
        headquarter_controller.add_resource(CrossLanContainerRunningStatus, "/cl-containers/<int:port>/running-status")
        headquarter_controller.add_resource(CrossLanContainerBindingIps, "/cl-containers/<int:port>/binding-ips")
        headquarter_controller.add_resource(CrossLanContainerDataUsage, "/cl-containers/<int:port>/data-usage")
        headquarter_controller.add_resource(CrossLanContainerUserPasswd, "/cl-containers/<int:port>/user-passwd")
        log.info("rest server start finish.")
        headquarter_app.run(host='202.117.15.79', port=12345, debug=True, use_reloader=False)
    except Exception, e:
        log.error(e.message)
        log.error(traceback.format_exc())
        abort(400, message="Exception")


def process_cmd(argv):
    if len(argv) < 2:
        log.critical("less than 2 parameters")
        print 'USAGE:'
        print 'python headquarter.py ' \
              '--conf ss_conf_file ' \
              '--restore interruption_restore_file'
        sys.exit(2)

    try:
        interruption_restore_file = None
        ss_conf_file = None

        opts, args = getopt.getopt(argv, "hc:r:", ["conf=", "restore="])
        for opt, arg in opts:
            if opt == '-h':
                print 'USAGE:'
                print 'python headquarter.py ' \
                      '--conf ss_conf_file ' \
                      '--restore interruption_restore_file'
                sys.exit(1)
            if opt in ("-c", "--conf"):
                ss_conf_file = arg
            if opt in ("-r", "--restore"):
                interruption_restore_file = arg
                print interruption_restore_file

        return ss_conf_file, interruption_restore_file

    except getopt.GetoptError:
        print 'USAGE:'
        print 'python headquarter.py ' \
              '--conf ss_conf_file ' \
              '--restore interruption_restore_file'
        sys.exit(2)


def running_stats_save(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    log.info("running_stats_save")
    try:
        running_cow_port_list = []
        for key, value in cow_process.iteritems():
            if value is not None:
                running_cow_port_list.append(key)

        with open('restore', 'w') as outfile:
            json.dump(running_cow_port_list, outfile)
        sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)


def ss_config(conf_file):
    try:
        global ss_lists
        log.debug("ss conf file path:" + conf_file)
        with open(str(conf_file), 'r') as infile:
            ss_lists = json.load(infile)

        for index in range(0, len(ss_lists)):
            ss_lists[index] = str(ss_lists[index])

            # log.debug(ss_lists)

    except Exception, e:
        log.error(traceback.format_exc())
        log.error(e.message)
        sys.exit(2)


def interruption_restore(restore_file):
    try:
        with open(restore_file, 'r') as infile:
            cow_process_port_list = json.load(infile)

        for port in cow_process_port_list:
            port = int(port)
            sleep(0.5)
            wd = cl_container_home + "/cl_container_" + str(port) + "/"
            cow_process[port] = subprocess.Popen(["./cow", "-rc", "./rc"], cwd=wd, stdout=subprocess.PIPE)

            log.info("restore the port |" + str(port) + "| successfully")

    except Exception, e:
        log.error(traceback.format_exc())
        log.error(e.message)
        sys.exit(2)


if __name__ == "__main__":
    username = os.environ["USER"]
    if ("CL_CONTAINERS_HOME" not in os.environ) or username != "root":
        log.critical("Permission or $CL_CONTAINERS_HOME Check Error, Exit.")
        sys.exit(2)

    conf, restore = process_cmd(sys.argv[1:])

    check_accounting_rules()
    log.info("check accounting rules finish.")

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, running_stats_save)
    log.info("running stats save handler finish.")

    ss_config(conf)
    log.info("ss conf file loading finish.")
    log.info("ss server's info:" + str(ss_lists))

    if restore is not None:
        interruption_restore(restore)
        log.info("restore finish.")
    else:
        log.info("none restore file. skipping.")

    rest_server()