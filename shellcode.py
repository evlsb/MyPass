import os
import sys
import random
from OpenSSL import crypto

k = b'-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCoKOQ5KqiLCEOF\nuhnbrPMBrOXqq0qbmDa2rBo+d6cUm2Jp7a/PVsN8Scf3c7hCYtzjuPi12/Zp2zUU\nUTsNOHtrXsArnyRecTD7AmD5duEeDNgy2GyXOSaIajbR3m8g5aiyPAro81Q0PpLz\nFR47eSgQT6Xe67uhLgtQLrpjHVCvnWCu4qkr/tALEzk1JPUI4gRJ7JDOLriE0fdN\nUATKn0XvF5OKhuPoBjNKNgLU2drYgb1G46wds0M2D42DDHyOXLXmMCJRf3fvyNKD\nnB2k4+2y5agmZgIRB91yzxFFwf3MDIvYOyKPzbjw1Z4niJ6TeW8ax+3dkCW46RIO\nMEsPhfoFAgMBAAECggEACtf2MunZYVEeBOJ7C+N4w8fPMgUr2WGPolMcmctz8qbR\ndLoPH1GS51xyS2FC2sRkG5WAM5P0rXSlVS3RdG5gZmGqBotrguE4MsYqFDQdBf0h\n4jzQBdFkNsw97uXHKJR+qXL96McrdndULl4ogKvKUFZJKy6W1Gjdxw94VUSyQQdh\neJubJeb/YP4Ans7gyWNqbQcmNmL97LbEwGatxrJ7tphuY8sBRl9HZ76uFKh1UhLY\nGZfy+pgk2hXQAc7IVh5wcjnmrxZgLvubM4tpHc1BBc2hWpNFYglgN5mIqaLX76zi\nU9nUdKdUE2cGLR68svbifXN+OtqOqvrcxBHdDXy1GQKBgQDSzJ407kJX0B8wDv4d\njik404fGTZkslNUfeFDGlpYyuE0kAU53KBlS7VJMan/f4iQWHfcZxTMuGgssyZEO\nYePiGUlTlJ2b51bCqFj4UqaVRWsnifTJDP96zG5/7Fzs1VAKMDr/VZGfVXs1oOk6\nmXPjqGdAKwbJ8UHbkkLabWxRDQKBgQDMN6pAgjLb3l6ofGhCHNd85L5rS2aqw2gz\nigSeVH0S4t0iafwPwzp+N8gLe/tZ/UQ+8oYShv7FTTSBTBGuTLEhA9FvRocmg9Ja\nDZ1QU9uYn/WiWDnWovQu1qvonTG+ZwKSn6BeR7iTQpfISHTd7fZAgkPIZUJghx9g\nQ/zWzxze2QKBgCwleBiDsVcsmet5qFROOmnROwUXqTWB8eRGUTxVuxziJh2dPG6N\n8kfAtdSVFTSw6nfLTL2T4/UKtT5q9Dr72zq1qvqbDCrjVvMrSH6w6Hwobpl4NdCJ\nLVPtTlLyED/1KG8JzME+jWG+CDCiA1YnXvLViNIScLiIEw/F4MRX2DBdAoGAHfE3\ndDfizxv+kwOSocbqzXQYe1DV38nA2HWvEavfnspGlAooHAOK6wCwwwZNpzccL4KN\np9/FMRaN0TtfCEhUXDvcFE2p+Tqwt+VxIFr7QpiJgmEfMdo4pTlygSuzJHCkDu16\nrPglFupXqNT+1Z9TUMgIujQmlFKbhhjR1IkPeZkCgYAQqCv7CUoBhVMt5CN25xmb\nHOfVj4SLKTfuhhBZ+JSAuobHbuK3/jBJRMTmVVWM8OloBaC/YgBt3vsCvSl8muEq\ndy8myi4vc4gA0xsSXojsM5EpphKL9rWAVCcIuLTNn7S9d1t6vKhwI3D+5IxLr/2o\nM25Q+yuS8CbT1/DAAnJC8g==\n-----END PRIVATE KEY-----\n'



a = crypto.load_privatekey(type=crypto.FILETYPE_PEM, buffer=k)
print(crypto.dump_privatekey(crypto.FILETYPE_PEM, a))
###########
# CA Cert #
###########

ca_key = crypto.PKey()
ca_key.generate_key(crypto.TYPE_RSA, 2048)

ca_cert = crypto.X509()
ca_cert.set_version(2)
ca_cert.set_serial_number(random.randint(50000000,100000000))

ca_subj = ca_cert.get_subject()
ca_subj.commonName = "My CA"

ca_cert.set_issuer(ca_subj)
ca_cert.set_pubkey(ca_key)
ca_cert.sign(ca_key, 'sha256')

ca_cert.gmtime_adj_notBefore(0)
ca_cert.gmtime_adj_notAfter(10*365*24*60*60)

print(crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert))
print(crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key))



client_key = crypto.PKey()
client_key.generate_key(crypto.TYPE_RSA, 2048)

client_cert = crypto.X509()
client_cert.set_version(2)
client_cert.set_serial_number(random.randint(50000000,100000000))

client_subj = client_cert.get_subject()
client_subj.commonName = "Client"

client_cert.set_issuer(ca_subj)
client_cert.set_pubkey(client_key)
client_cert.sign(ca_key, 'sha256')

client_cert.gmtime_adj_notBefore(0)
client_cert.gmtime_adj_notAfter(10*365*24*60*60)


print(crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert))
print(crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key))