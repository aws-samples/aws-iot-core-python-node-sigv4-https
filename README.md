## AWS Iot Core Python Node Sigv4 Https

It provides guidance on how to publish messages to AWS IoT Core using Https, with the help of a Python sample and NodeJs sample.

# 1.Objective
The objective of this repository is to provide guidance on how to publish messages to AWS IoT Core using Https protocol and AWS SigV4 autentication. It has two reference implementations - one in Python and other in NodeJs.
The following sections cover them in detail.

# 2.Python code to publish to AWS IoT Core using HTTPs protocol and AWS Sigv4 authentication
Create a directory for solution called 'PythonSample'.

Create an environment .env file at the root of the folder  with the following configuration.

``` .env
# http method should be POST
method=POST

# Service should be 'iotdevicegateway' for connecting to AWS IoT Core
service = 'iotdevicegateway'

# Content Type to be sent as a part of HTTP request is 'application/json'
contenttype = 'application/json'

# region can be set to the AWS region that you want to connect

region = 'us-east-1'

# Set the AWS IoT host name specific to your AWS account

host = 'youriothostname.iot.us-east-1.amazonaws.com'

# endpoint is the full AWS IoT endpoint

endpoint = 'https://youriothostname.iot.us-east-1.amazonaws.com/topics/udit/test?qos=1'

# access key
accesskey = 'youraccesskey'

# secret ky
secretkey = 'yoursecretkey'

# canonical uri is the relative path to the AWS IoT Core topic. It usually starts with '/topics/yourtopicpath'
canonicaluri = '/topics/udit/test'

# canonical query string needs to be set with with a value of 1 for qos flag
canonicalquerystring = 'qos=1'


``` 

Create a python file 'AWSIoTSigV4.py' with the following implementation.

``` python
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
``` 

Install the required python packages and execute the above code. You should see that above code is publishing messages successfully to AWS IoT core, with a HTTP Status Code of 200. You can also very that in AWS IoT console.

# 3.NodeJs code to publish to AWS IoT Core using HTTPs protocol and AWS Sigv4 authentication
Create a directory for solution called 'NodeSample'.

Initialize the project and install required packages using npm.

``` bash 
npm init -y
npm install dotenv
``` 

Create an environment .env file at the root of the folder  with the following configuration.

``` .env
# http method should be POST
method=POST

# Service should be 'iotdevicegateway' for connecting to AWS IoT Core
service = 'iotdevicegateway'

# Content Type to be sent as a part of HTTP request is 'application/json'
contenttype = 'application/json'

# region can be set to the AWS region that you want to connect

region = 'us-east-1'

# Set the AWS IoT host name specific to your AWS account

host = 'youriothostname.iot.us-east-1.amazonaws.com'

# endpoint is the full AWS IoT endpoint

endpoint = 'https://youriothostname.iot.us-east-1.amazonaws.com/topics/udit/test?qos=1'

# access key
accesskey = 'youraccesskey'

# secret ky
secretkey = 'yoursecretkey'

# canonical uri is the relative path to the AWS IoT Core topic. It usually starts with '/topics/yourtopicpath'
canonicaluri = '/topics/udit/test'

# canonical query string needs to be set with with a value of 1 for qos flag
canonicalquerystring = 'qos=1'

``` 

Create a nodejs file 'AWSIoTSigV4.js' with the following implementation.

``` javascript
//The following code sample publishes messages to AWS IoT using HTTPs protocol and AWS Sigv4 authentication
const dotenv = require('dotenv');
var https = require('https');
var crypto = require('crypto');
var request = require('request');

//Load the .env file
dotenv.config();

function sign(key, message) {
  return crypto.createHmac('sha256', key).update(message).digest();
}

function getSignatureKey(key, dateStamp, regionName, serviceName) {
  kDate = sign('AWS4' + key, dateStamp);
  kRegion = sign(kDate, regionName)
  kService = sign(kRegion, serviceName);
  kSigning = sign(kService, 'aws4_request');
  return kSigning;
}

method = process.env.method
accessKey = process.env.accesskey;
secretKey = process.env.secretkey;
region = process.env.region;
serviceName = process.env.service;
content_type = process.env.contenttype;
request_parameters = "Hello World";
host = process.env.host;
region = process.env.region;
endpoint = process.env.endpoint;
canonical_uri = process.env.canonicaluri;
canonical_querystring = process.env.canonicalquerystring;

console.log(canonical_querystring);


var now = new Date();
amz_date = now.toJSON().replace(/[-:]/g, "").replace(/\.[0-9]*/, "");
date_stamp = now.toJSON().replace(/-/g, "").replace(/T.*/, "");



//The only query string that needs to be passed in the request is quality of service. Set that value as 'qos=1'
canonical_headers = "content-type:" + content_type + "\n" + "host:" + host + "\n" + "x-amz-date:" + amz_date + "\n";

//Concatenate content-type, host and x-amz-date literals seperated by semi-colon and asign it to signed_headers
signed_headers = "content-type;host;x-amz-date";

//Hash the body of the request messaging using SHA256 algorithm
payload_hash = crypto.createHash('sha256').update(request_parameters).digest('hex');

console.log(payload_hash);

//Step 7: Combine elements to create create canonical request
canonical_request = method + "\n" + canonical_uri + "\n" + canonical_querystring + "\n" + canonical_headers + "\n" + signed_headers + "\n" + payload_hash;

//Algorithm should be 'AWS4-HMAC-SHA256'
//credential_scope and string_to_sign should be computed in the below format
algorithm = 'AWS4-HMAC-SHA256';
credential_scope = date_stamp + "/" + region + "/" + serviceName + "/" + "aws4_request";
string_to_sign = algorithm + "\n" + amz_date + "\n" + credential_scope + "\n" + crypto.createHash('sha256').update(canonical_request).digest('hex');


//Compute the signing key
signing_key = getSignatureKey(secretKey, date_stamp, region, serviceName);

//Compute signature by invoking 
signature = crypto.createHmac('sha256', signing_key).update(string_to_sign).digest('hex');


//Frame the authorization header by concatenating alogorithm, access_key, credential_scope, signed_headers and the actual signature in the required format

authorization_header = algorithm + ' ' + 'Credential=' + accessKey + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature


//For publishing to AWS IoT Core using HTTPs and SigV4, you only need to add three headers. They are 'Content-Type', 'X-Amz-Date' and 'Authorization'. You don't need to explicity set the 
//host header. It is automatically added by the nodejs request library
headers1= {'Content-Type': content_type,
           'X-Amz-Date': amz_date,
           'Authorization': authorization_header}



var options1 = {"headers":headers1,"body":request_parameters}


request.post(endpoint, options1,function(error, response,body)

{

  

   if (error)
   {
      console.log('error'+'\n'+error)

   }

   if (response.statusCode==200)
   {

    console.log("sucessful");
    console.log('Http Status Code'+response.statusCode);
    console.log(body)
   }


}
);





``` 


## License

This library is licensed under the Apache 2.0 License. 
