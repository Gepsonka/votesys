from Crypto.PublicKey import RSA


key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

print("Private key: ", private_key)
print("typeof private key: ", type(private_key))
imorted_key = RSA.import_key(private_key)
