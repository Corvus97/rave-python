#updated for v3
import json, requests, copy
from rave_python.rave_base import RaveBase
from rave_python.rave_misc import checkIfParametersAreComplete
from rave_python.rave_exceptions import ServerError, IncompleteCardDetailsError, BeneficiariesCreationError, BeneficiariesStatusError

class Beneficiaries(RaveBase):
    def __init__(self, publicKey, secretKey, production, usingEnv):
        self.headers = {
            'content-type' : 'application/json',
            'authorization' : 'Bearer ' + secretKey,
        }
        super(Beneficiaries, self).__init__(publicKey, secretKey, production, usingEnv)

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

    def _handleCreateResponse(self, response, details):
        responseJson = self._preliminaryResponseChecks(response, BeneficiariesCreationError, details["account_number"])

        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"] }

        else:
            raise BeneficiariesCreationError({"error": True, "data": responseJson["data"]})

    def _handleCardStatusRequests(self, type, endpoint, method, data=None):
        #check type of response
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
            raise BeneficiariesStatusError(type, {"error": True, "returnedData": responseJson })

    #function to create a beneficiary or transfer beneficiaries 
    #Params: details - a dict containing currency, amount,
    def create(self, details):
        requiredParameters = ["account_number", "account_bank"]
        checkIfParametersAreComplete(requiredParameters, details)

        endpoint = self._baseUrl + self._endpointMap["beneficiaries"]["create"]
        response = requests.post(endpoint, headers=self.headers, data=json.dumps(details))
        return self._handleCreateResponse(response, details)

    def all(self):
        endpoint = self._baseUrl + self._endpointMap["beneficiaries"]["list"]
        method = 'GET'
        return self._handleCardStatusRequests("List-beneficiaries", endpoint, method, data = None)

    def fetch(self, beneficiaries_id):
        endpoint = self._baseUrl + self._endpointMap["beneficiaries"]["fetch"] + "/" + str(beneficiaries_id)
        method = 'GET'
        return self._handleCardStatusRequests("Fetch-beneficiaries", endpoint, method, data = None)

    def delete(self, beneficiaries_id):
        if not beneficiaries_id:
            return "beneficiaries id was not supplied. Kindly supply one"
        endpoint = self._baseUrl + self._endpointMap["beneficiaries"]["delete"] + "/" + str(beneficiaries_id)
        method = 'DELETE'
        data = {"id": beneficiaries_id}
        return self._handleCardStatusRequests("Delete-beneficiary", endpoint, method, data = data)

    