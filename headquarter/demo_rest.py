from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource
import json

headquater_app = Flask(__name__)
headquater_controller = Api(headquater_app)

# URL: /cl-containers/<int:port>
class CrossLanContainers(Resource):
    def post(self, port):
        print "CrossLanContainers.put"
        print 'the url arg port:  ' + str(port) + "type: " + str(type(port))
        return 201
        # abort(400, message="failed")

# URL: /cl-containers/<int:port>/running-status
class CrossLanContainerRunningStatus(Resource):
    def put(self, port):
        print "CrossLanContainerRunningStatus.put"
        print 'the url arg port:  ' + str(port) + "type: " + str(type(port))
        data = json.loads(request.get_data())
        print data
        return 201
    def get(self, port):
        print "CrossLanContainerRunningStatus.get"
        print 'the url arg port:  ' + str(port) + "type: " + str(type(port))
        return 201
# URL: cl-containers/<int:port>/binding-ips
class CrossLanContainerBindingIps(Resource):
    def put(self, port):
        print "CrossLanContainerBindingIps.put"
        print 'the url arg port:  ' + str(port) + "type: " + str(type(port))
        data = json.loads(request.get_data())
        print data
        return 201
# URL: cl-containers/<int:port>/data-usage
class CrossLanContrainerDataUsage(Resource):
    def get(self, port):
        print "CrossLanContrainerDataUsage.get"
        print 'the url arg port:  ' + str(port) + "type: " + str(type(port))
        return 201


headquater_controller.add_resource(CrossLanContainers, '/cl-containers/<int:port>')
headquater_controller.add_resource(CrossLanContainerRunningStatus, '/cl-containers/<int:port>/running-status')
headquater_controller.add_resource(CrossLanContainerBindingIps, '/cl-containers/<int:port>/binding-ips')
headquater_controller.add_resource(CrossLanContrainerDataUsage, '/cl-containers/<int:port>/data-usage')

if __name__ == '__main__':
    headquater_app.run(debug=True)
