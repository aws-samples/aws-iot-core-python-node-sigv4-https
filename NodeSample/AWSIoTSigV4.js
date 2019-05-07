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



