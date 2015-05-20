import subprocess
import traceback
from flask import Flask, request
from flask.ext.restful import abort, Api, Resource
import json
import iptc
import logging
import os
import sys

ss_lists = ["proxy = ss://aes-256-cfb:password@10.0.0.0:1080",
            "proxy = ss://aes-256-cfb:password@10.0.0.0:1080"]

headquarter_app = Flask(__name__)
headquarter_controller = Api(headquarter_app)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("headquarter")

cow_process = {}

# URL: /cl-containers/<int:port>
class CrossLanContainers(Resource):
    def post(self, port):
        try:
            log.debug("CrossLanContainers.POST")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))

            # Add rc File into User's Home.
            cl_container_home = os.environ["CL_CONTAINERS_HOME"]
            filename = cl_container_home + "/cl_container_" + str(port) + "/rc"

            if os.path.exists(filename):
                os.remove(filename)

            filter_table = iptc.Table(iptc.Table.FILTER)

            output_chain = iptc.Chain(filter_table, "OUTPUT")
            rule_del = None
            for rule in output_chain.rules:
                sport = str(rule.matches[0].parameters["sport"])
                if sport == str(port):
                    rule_del = rule
                    break

            if rule_del is not None:
                output_chain.delete_rule(rule_del)

            f = open(filename, 'a')
            f.write("listen = http://202.117.15.79:" + str(port) + "\n")
            f.write("loadBalance = hash\n")
            for ss in ss_lists:
                f.write(ss + "\n")
            f.close()

            # New Rule.
            rule = iptc.Rule()
            rule.protocol = "tcp"

            # Add match to the rule.
            match = iptc.Match(rule, "tcp")
            match.sport = str(port)
            rule.add_match(match)

            # Add target to the rule.
            target = iptc.Target(rule, "ACCEPT")
            rule.target = target

            # Insert rule to the OUTPUT chain in filter Table.
            output_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
            output_chain.insert_rule(rule)
            return 201
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

            cl_container_home = os.environ["CL_CONTAINERS_HOME"]
            if action == "start":
                wd = cl_container_home + "/cl_container_" + str(port) + "/"

                # FIXME: there is some bug when I want to kill it.
                # cow = subprocess.Popen([cmd + " -rc " + rc_file], shell=True)
                # FIXME: if use the abs path, it can not be called.
                # cow_process[port] = subprocess.Popen([cmd, "-rc", rc_file])

                cow_process[port] = subprocess.Popen(["./cow", "-rc", "./rc"], cwd=wd)
                return 201
            if action == "stop":
                cow_p = cow_process[port]
                log.debug(cow_p)
                cow_p.terminate()
                cow_process[port] = None
                return 201
            if action == "restart":
                wd = cl_container_home + "/cl_container_" + str(port) + "/"

                cow_p = cow_process[port]
                cow_p.terminate()
                cow_process[port] = subprocess.Popen(["./cow", "-rc", "./rc"], cwd=wd)
                return 201
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
                return json.dumps({"status": "running"}), 201
            else:
                return json.dumps({"status": "stop"}), 201

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
            log.debug(ipsets)

            cl_container_home = os.environ["CL_CONTAINERS_HOME"]

            f = open(cl_container_home + "/cl_container_" + str(port) + "/rc", "r")
            log.debug(cl_container_home + "/cl_container_" + str(port) + "/rc")

            lines = f.readlines()
            log.debug(lines)
            if len(lines) == 2 + len(ss_lists) + 1:
                lines = lines[:-1]
            log.debug(lines)
            last_line = "allowedClient = "

            for i in range(0, len(ipsets) - 1):
                last_line = last_line + ipsets[i] + ","

            # Last One omit the comma.
            last_line = last_line + ipsets[len(ipsets) - 1] + "\n"

            lines.append(last_line)
            f.close()

            f = open(cl_container_home + "/cl_container_" + str(port) + "/rc", "w")
            log.debug(lines)
            f.writelines(lines)
            f.close()
            # TODO restart.

            return 201
        except Exception, e:
            log.error(traceback.format_exc())
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            abort(400, message="Exception")


# URL: cl-containers/<int:port>/data-usage
class CrossLanContainerDataUsage(Resource):
    def get(self, port):
        try:
            log.debug("CrossLanContainerDataUsage.get")
            log.debug("ARGS:  " + str(port) + " type: " + str(type(port)))

            filter_table = iptc.Table(iptc.Table.FILTER)
            filter_table.refresh()

            output_chain = iptc.Chain(filter_table, "OUTPUT")

            bytes = 0
            for rule in output_chain.rules:
                sport = str(rule.matches[0].parameters["sport"])
                log.debug(rule.get_counters())
                if sport == str(port):
                    counter = rule.get_counters()
                    packets = counter[0]
                    log.debug("packet #:" + str(packets))
                    log.debug("bytes #:" + str(bytes))
                    bytes = counter[1]
                    break
                raise Exception("NotFoundPort")

            json_bytes = json.dumps({"data-usage": bytes})

            return json_bytes, 201
        except Exception, e:
            log.error(e.message)
            log.error("ARGS:  " + str(port))
            log.error(traceback.format_exc())
            abort(400, message="Exception")


headquarter_controller.add_resource(CrossLanContainers, "/cl-containers/<int:port>")
headquarter_controller.add_resource(CrossLanContainerRunningStatus, "/cl-containers/<int:port>/running-status")
headquarter_controller.add_resource(CrossLanContainerBindingIps, "/cl-containers/<int:port>/binding-ips")
headquarter_controller.add_resource(CrossLanContainerDataUsage, "/cl-containers/<int:port>/data-usage")

if __name__ == "__main__":
    username = os.environ["USER"]
    if ("CL_CONTAINERS_HOME" not in os.environ) or username != "root":
        log.critical("Permission or Env Variables Check Error, Exit.")
        sys.exit(2)
    headquarter_app.run(debug=True)
