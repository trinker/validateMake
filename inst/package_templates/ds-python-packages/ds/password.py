import keyring
import getpass
from ds.paths import Paths
from cryptography.fernet import Fernet
from hashlib import blake2b
import base64


class Password:
    """Secure Password Storage

    Uses a vault_password to securely encrypt and store service 
    passwords in your system key chain that can be retrieved and 
    decrypted with the same vault_password.

    Methods:
        new_password: Add a new password to the keychain
        update_password: Update an existing service password
        get_password: Retrieve the password for a service
        pw: An alias for get_password

    Examples::
        
        ## Adding Common DS Config Passwords
        from ds import Password
        pw =  Password()
        pw.new_password('CampusLabs')
        pw.get_password('CampusLabs')
        pw.new_password('Anthology')
        pw.get_password('Anthology')
        pw.new_password('DataScience')
        pw.get_password('DataScience')

    """   

    def __init__(self, username:str = Paths().user):
        self.vault_password = getpass.getpass('Vault Password')
        self.username = username


    def new_password(self, service: str, password:str = None):
        if password is None: password = getpass.getpass('Service Password')
        encPassword = _encrypt(self.vault_password, password)
        keyring.set_password(service, self.username, encPassword.decode('utf8', 'strict'))

    update_password = new_password

    def get_password(self, service: str):
        password = keyring.get_password(service, Paths().user)
        return _Hidden(_decrypt(self.vault_password, password.encode()))

    pw = get_password

def _encrypt(main, second):
    h = blake2b(digest_size=16)
    h.update(main.encode())
    key = base64.b64encode(str(h.hexdigest()).encode())
    fernet = Fernet(key)
    return fernet.encrypt(second.encode())

def _decrypt(main, second):
    h = blake2b(digest_size=16)
    h.update(main.encode())
    key = base64.b64encode(str(h.hexdigest()).encode())
    fernet = Fernet(key)    
    return fernet.decrypt(second).decode()

class _Hidden(str):
    def __init__(self, x):
        self.x = x
        
    def __repr__(self): 
        return '*****'
