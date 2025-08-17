# Creating ledetour-membres SSL client files

## Testing the certificates

The following command ran on the Vagrant host should return a JSON file containing non-anonymized data:

```
curl --cert-type P12 --cert ledetour-membres-client.p12 -Lk https://membres.localhost:4430/members.json
```

## Important points

Two points are important:

1. We don't use the `-des3` option as to not require user passwords
2. It is *crucial* that the Organisation Name for the CA and the client certificates are *different*. No idea why.

## Script to generate the certificates

```
# Create the CA Key and Certificate for signing Client Certs

openssl genrsa -out ledetour-membres-ca.key 4096
openssl req -new -x509 -days 3650 -key ledetour-membres-ca.key -out ledetour-membres-ca.crt

# A few questions are going to be asked.
# We keep the defaults apart for Organization Name: membres.epicerieledetour.org
#
# The example output should be like:
#
# You are about to be asked to enter information that will be incorporated
# into your certificate request.
# What you are about to enter is what is called a Distinguished Name or a DN.
# There are quite a few fields but you can leave some blank
# For some fields there will be a default value,
# If you enter '.', the field will be left blank.
# -----
# Country Name (2 letter code) [AU]:
# State or Province Name (full name) [Some-State]:
# Locality Name (eg, city) []:
# Organization Name (eg, company) [Internet Widgits Pty Ltd]:membres.epicerieledetour.org
# Organizational Unit Name (eg, section) []:
# Common Name (e.g. server FQDN or YOUR name) []:
# Email Address []:

# Create the Client Key and CSR

openssl genrsa -out ledetour-membres-client.key 4096
openssl req -new -days 3650 -key ledetour-membres-client.key -out ledetour-membres-client.csr

# A few questions are going to be asked again.
# We keep the defaults apart for Organization Name: membres.epicerieledetour.org CLIENT
# Also, challenge password and optional company name are kept empty.
#
# The example output should be like:
#
# You are about to be asked to enter information that will be incorporated
# into your certificate request.
# What you are about to enter is what is called a Distinguished Name or a DN.
# There are quite a few fields but you can leave some blank
# For some fields there will be a default value,
# If you enter '.', the field will be left blank.
# -----
# Country Name (2 letter code) [AU]:
# State or Province Name (full name) [Some-State]:
# Locality Name (eg, city) []:
# Organization Name (eg, company) [Internet Widgits Pty Ltd]:membres.epicerieledetour.org CLIENT
# Organizational Unit Name (eg, section) []:
# Common Name (e.g. server FQDN or YOUR name) []:
# Email Address []:
# 
# Please enter the following 'extra' attributes
# to be sent with your certificate request
# A challenge password []:
# An optional company name []:

# Sign the client certificate with our CA cert

openssl x509 -req -days 3650 -in ledetour-membres-client.csr -CA ledetour-membres-ca.crt -CAkey ledetour-membres-ca.key -set_serial 01 -out ledetour-membres-client.crt

# Convert to .p12 so import in OSX works
# Again, here we don't specify a password. The output should look like:
#
# Warning: -clcerts option ignored with -export
# Enter Export Password:
# Verifying - Enter Export Password:

openssl pkcs12 -export -clcerts -inkey ledetour-membres-client.key -in ledetour-membres-client.crt -out ledetour-membres-client.p12 -name "membres.epicerieledetour.org"
```

## Example in Stack Overflow

We followed [those instructions](https://stackoverflow.com/questions/45628601/client-authentication-using-self-signed-ssl-certificate-for-nginx). In case this page disapears, here was it:

```
I just stumbled over this and discovered a small pitfall which caused the same error you encountered:

    error 18 at 0 depth lookup: self signed certificate

There are plenty of guides how to create a self signed client certificate, I used the following (adapted from here):

# Create the CA Key and Certificate for signing Client Certs
openssl genrsa -des3 -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Create the Client Key and CSR
openssl genrsa -des3 -out client.key 4096
openssl req -new -key client.key -out client.csr

# Sign the client certificate with our CA cert
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt

# Convert to .p12 so import in OSX works
openssl pkcs12 -export -clcerts -inkey client.key -in client.crt -out client.p12 -name "MyKey"

However, if you use the same Organization Name (eg, company) for both your ca and your client certificate, you will see above error! (edited: important)

If openssl verify -verbose -CAfile ca.crt client.crt does not complain about a self-signed certificate, you're good to go.
```
