#The following code snippet posts message to the AWS IoT Core using Https and Sigv4.
import sys, os, base64, datetime, hashlib, hmac
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# ************* Load .env file*************
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# ************* REQUEST VALUES *************
method = os.getenv('method')
service = os.getenv('service')

content_type = os.getenv('contenttype')
request_parameters = """{"message":"Hello world"}"""
host = os.getenv('host')
region = os.getenv('region')
endpoint = os.getenv('endpoint')
access_key = os.getenv('accesskey')
secret_key = os.getenv('secretkey')
canonical_uri = os.getenv('canonicaluri')
canonical_querystring = os.getenv('canonicalquerystring')



# Function for signing. Refer the AWS documentation below for more details.
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python.
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

# Function for computing signature key. Refer the AWS documentation below for more details.
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python.

def getSignatureKey(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


# Fetch AWS access key from env. variables or configuration file. 
if access_key is None or secret_key is None:
    print
    'No access key is available.'
    sys.exit()

# Create date for headers and the credential string.
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ')
date_stamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope


# Frame the canonical_header by concatenating content-type, host and x-amz-date at its values, in the required format.
canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n'

#Concatenate content-type, host and x-amz-date literals seperated by semi-colon and asign it to signed_headers.
signed_headers = 'content-type;host;x-amz-date'

#Hash the body of the request messaging using SHA256 algorithm.
payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

# Step 7: Combine elements to create create canonical request
canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

#Algorithm should be 'AWS4-HMAC-SHA256'.
#credential_scope and string_to_sign should be computed in the below format.
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' + amz_date + '\n' + credential_scope + '\n' + hashlib.sha256(
    canonical_request.encode('utf-8')).hexdigest()

#Compute the signing key.
signing_key = getSignatureKey(secret_key, date_stamp, region, service)

# Compute signature by invoking hmac.new method by passing signingkey, string_to_sign.
signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

# Frame the authorization header by concatenating alogorithm, access_key, credential_scope, signed_headers and the actual signature in the required format.
authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

# For publishing to AWS Iot Core using HTTPs and SigV4, you only need to add three headers. They are 'Content-Type', 'X-Amz-Date' and 'Authorization'. You don't need to explicity set the 
# host header. It is automatically added by the python http request library.
headers = {'Content-Type': content_type,
           'X-Amz-Date': amz_date,
           'Authorization': authorization_header}

# ************* SEND THE REQUEST *************
print('\nBEGIN REQUEST------------------------------')

print( 'Request URL = ' + endpoint)


r = requests.post(endpoint, data=request_parameters, headers=headers)

print('\nRESPONSE------------------------------------')
print('Response code: %d\n' % r.status_code)
print(r.text)