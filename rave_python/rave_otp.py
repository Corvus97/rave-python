#updated for v3
import json, requests, copy
from rave_python.rave_base import RaveBase
from rave_python.rave_misc import checkIfParametersAreComplete
from rave_python.rave_exceptions import ServerError, IncompleteCardDetailsError, CardCreationError, CardStatusError

class Otp(RaveBase):
    def __init__(self, publicKey, secretKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(Otp, self).__init__(publicKey, secretKey, production, usingEnv)

    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, name):
        #check if we can get json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "name": name, "errMsg": response})

        #check for data parameter in response 
        if not responseJson.get("data", None):
            raise TypeOfErrorToRaise({"error": True, "name": name, "errMsg": responseJson.get("message", "Server is down")})

        #check for 200 response
        if not response.ok:
            errMsg = response["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "errMsg": errMsg})

        return responseJson

    # def _handleCreateResponse(self, response, details):
    #     responseJson = self._preliminaryResponseChecks(response, CardCreationError, details["billing_name"])

    #     if responseJson["status"] == "success":
    #         return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

    #     else:
    #         raise CardCreationError({"error": True, "data": responseJson["data"]})

    def _handleStatusRequests(self, type, endpoint, method, data=None):
        #check if response is a post response
        if method == 'GET':
            if data == None:
                response = requests.get(endpoint, headers=self.headers)
            else:
                response = requests.get(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'POST':
            response = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
        elif method == 'PUT':
            response = requests.put(endpoint, headers=self.headers)
        elif method == 'PATCH':
            response = requests.patch(endpoint, headers=self.headers, data=json.dumps(data))
        else:
            response = requests.delete(endpoint, headers=self.headers, data=json.dumps(data))
        
        #check if it can be parsed to JSON
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "errMsg": response.text})

        if response.ok:
            return {"error": False, "returnedData": responseJson}
        else:
            raise CardStatusError(type, {"error": True, "returnedData": responseJson })


    #function to list and fetch settlements
    
    def create(self, details):
        requiredParameters = ["length", "customer", "sender", "send", "medium"]
        checkIfParametersAreComplete(requiredParameters, details)
        endpoint = self._baseUrl + self._endpointMap["otp"]["create"]
        data = details
        method = 'POST'
        return self._handleStatusRequests("Create-OTP", endpoint, method, data = data)

    