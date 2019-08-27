import sys
import json
from datetime import datetime
import uuid
import hashlib
import base64
import requests
import ftplib

class FtpConn:
    def __init__(self, host, user, passw):
        self.host  = host
        self.user  = user
        self.passw = passw

    def connect(self):
        ftp = ftplib.FTP(self.host)
        ftp.login(self.user, self.passw)
        return ftp

    def getFiles(filepath):
        ftp = connect()

        try:
            ftp.retrbinary("RETR " + filepath, open(filepath, 'wb').write)
        except:
            print("Error downloading " + filepath)

    def pushFiles(filepath):
        ftp = connect()

        try:
            ftp.retrbinary("STOR " + filepath, open(filepath, 'rb').write)
        except:
            print("Error uploading " + filepath)

    def removeFiles(filepath):
        ftp = connect()

        try:
            ftp.delete(filepath)
        except:
            print("Error deleting " + filepath)

def main(argv):

    # Provide the input json to execute followed by output response path
    input_json_path = argv[0]
    output_file_path = argv[1]

    # get dictionary from input json path
    input_dict = json_file_to_dict(input_json_path)

    # generate X-WSSE header
    header_dict = generate_xwsse_header(input_dict['user'], input_dict['secret'])

    # make API Call
    resp = send_request(input_dict['url'], header_dict, input_dict['request'])

    # save response to file
    save_response(resp, output_file_path)
    print(resp)

def json_file_to_dict(json_path):
    json_dict = None
    with open(json_path) as json_file:
        json_dict = json.load(json_file)
    return json_dict

def generate_xwsse_header(user_name, user_secret):
    # Header follows a vendor specific format
    timestamp = datetime.utcnow().isoformat()[:-4] + 'Z'  # vendor rest api uses the Z annotation
    nonce = str(uuid.uuid4())
    password_digest = hashlib.sha1((nonce + timestamp + user_secret).encode('utf8')).digest()
    password_digest_base64 = str(base64.encodebytes(password_digest), 'utf8').rstrip()
    nonce_base64 = str(base64.encodebytes(nonce.encode('utf8')), 'utf8').rstrip()
    return {'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' %
                      (user_name, password_digest_base64, nonce_base64, timestamp)}

def send_request(url, header_dict, payload_dict, proxy_dict={}):
    # Some networks will require a proxy to make the request
    # format is proxy_dict = {'http':'user:pass@proxy.network.com:port'}
    req = requests.Request('POST', url, headers=header_dict, data=json.dumps(payload_dict))
    prepared = req.prepare()
    s = requests.Session()
    resp = s.send(prepared, proxies=proxy_dict)
    return resp

def save_response(resp, out_path):
    with open(out_path, 'w') as out_file:
        out_file.write(resp.text)


if __name__ == "__main__":
    main(sys.argv[1:])
    
