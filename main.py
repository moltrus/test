import os
import re
import yaml
import subprocess
import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def get_user_input():

    website = input("\nwebsite: ")
    while not website:
        print("website can't be empty")
        password = input("website: ")

    email = input("\nemail: ")
    while email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Invalid email format")
        email = input("email: ")
    if not email:
        email = ''

    username = input("\nusername: ")
    if not username:
        username = ''

    password = input("\npassword: ")
    while not password:
        print("password can't be empty")
        password = input("password: ")

    passphrase = input("\npassphrase: ")
    if not passphrase:
        passphrase = ''

    return {
        'website': website,
        'email': email,
        'username': username,
        'password': password,
        'passphrase': passphrase
    }


def encrypt_file(file_path, master_password):
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode())

    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        file_data = f.read()

    encrypted_data = encryptor.update(file_data) + encryptor.finalize()

    with open(file_path + '.enc', 'wb') as f:
        f.write(salt + iv + encrypted_data)


def decrypt_file(file_path, master_password):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_data = encrypted_data[32:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode())

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    try:
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return yaml.safe_load(decrypted_data)
    except Exception:
        print("incorrect master password")
        return None

def add_account(data):
    new_account = get_user_input()
    data['accounts'].append(new_account)
    print("\nadded\n")

def find_account(data, search_term):
    if search_term == '*':
        return data['accounts']

    if search_term == '':
        return None

    results = []
    for account in data['accounts']:
        if (search_term.lower() in account.get('website', '').lower() or
                search_term.lower() in account.get('username', '').lower()):
            results.append(account)
    if results:
        return results
    return None

def change_account(data, website):
    results = []
    for account in data['accounts']:
        if website.lower() in account.get('website', '').lower():
            results.append(account)
    
    if not results:
        print("does not exist")
        return

    choice = 1
    if len(results) != 1:

        for idx, account in enumerate(results):
            print(f"\nID: {idx + 1}\n--------\n{account.get('website')}\n--------\nemail: {account.get('email')}\nusername: {account.get('username')}\npassword: {account.get('password')}\npassphrase: {account.get('passphrase')}")

        choice = input("\nID number to change: ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(results):
            print("invalid")
            return

    selected_account = results[int(choice) - 1]
    print(f"\n------ site: {selected_account.get('website')} ------")
    print("enter new details. leave blank to keep current value")

    new_email = input(f"\nemail ({selected_account.get('email')}): ").strip()
    new_username = input(f"\nusername ({selected_account.get('username')}): ").strip()
    new_password = input("\npassword: ").strip()
    new_passphrase = input(f"\npassphrase ({selected_account.get('passphrase')}): ").strip()

    if new_email:
        selected_account['email'] = new_email
    if new_username:
        selected_account['username'] = new_username
    if new_password:
        selected_account['password'] = new_password
    if new_passphrase:
        selected_account['passphrase'] = new_passphrase

    print("\nupdated\n")

def delete_account(data, website):
    if website == '*':
        confirm = input("sure you wanna delete all? (yes/no): ").strip().lower()
        if confirm in ['yes','y']:
            data['accounts'].clear()
            print("all deleted")
        else:
            print("cancelled")
        return

    results = []
    for account in data['accounts']:
        if website.lower() in account.get('website', '').lower():
            results.append(account)

    if not results:
        print("does not exist")
        return

    if len(results) == 1:
        data['accounts'].remove(results[0])
        print("deleted")
        return

    for idx, account in enumerate(results):
        print(f"\nID: {idx + 1}\n--------\n{account.get('website')}\n--------\nemail: {account.get('email')}\nusername: {account.get('username')}\npassword: {account.get('password')}\npassphrase: {account.get('passphrase')}")

    choice = input("\nID number to delete: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(results):
        print("invalid")
        return

    selected_account = results[int(choice) - 1]
    data['accounts'].remove(selected_account)
    print("deleted")

def pretty_print(data):
    print()
    for item in data:
        for key, value in item.items():
            if value:
                print(" "*4+f"{key}: {value}")
        print()

def add_to_yaml(data, master_password):
    with open('zapdos.yaml', 'w') as file:
        yaml.dump(data, file)

    encrypt_file('zapdos.yaml', master_password)
    os.remove('zapdos.yaml')

def init_repo():
    try:
        subprocess.run(['git', 'init'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while initializing the git repository: {e}")

def add_files():
    try:
        subprocess.run(['git', 'add', '.'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while adding files to the git repository: {e}")

def commit_repo(commit_message):
    try:
        subprocess.run(['git', 'commit', '-m', f'{commit_message}'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while committing files to the git repository: {e}")

def push_repo(remote_url, is_init=False):
    try:
        if not is_init:
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pushing files to the git repository: {e}")

def has_changes():
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], check=True, stdout=subprocess.PIPE)
        if result.stdout:
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while checking for changes: {e}")
        return False

def sync_with_remote(commit_message, remote_url):
    init_repo()
    add_files()
    commit_repo(commit_message)
    if os.path.exists('remote_url'):
        push_repo(remote_url, is_init=True)
    else:
        with open('remote_url', 'w') as file:
            file.write(remote_url)
        push_repo(remote_url, is_init=False)

def main():
    try:
        master_password = getpass.getpass("master password: ")
    except KeyboardInterrupt:
        exit()

    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as file:
            file.write('remote_url')
            file.flush()

    if os.path.exists('zapdos.yaml.enc'):
        data = decrypt_file('zapdos.yaml.enc', master_password)
        if data is None:
            return
    else:
        data = {'accounts': []}


    print("""
 ________                            __                     
/        |                          /  |                    
$$$$$$$$/   ______    ______    ____$$ |  ______    _______ 
    /$$/   /      \  /      \  /    $$ | /      \  /       |
   /$$/    $$$$$$  |/$$$$$$  |/$$$$$$$ |/$$$$$$  |/$$$$$$$/ 
  /$$/     /    $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$      \ 
 /$$/____ /$$$$$$$ |$$ |__$$ |$$ \__$$ |$$ \__$$ | $$$$$$  |
/$$      |$$    $$ |$$    $$/ $$    $$ |$$    $$/ /     $$/ 
$$$$$$$$/  $$$$$$$/ $$$$$$$/   $$$$$$$/  $$$$$$/  $$$$$$$/  
                    $$ |                                    
                    $$ |                                    
                    $$/                                     
    """)

    print("\n\n 1. add\n 2. find\n 3. change\n 4. delete\n 5. sync\n 6. exit")

    while True:
        try:
            choice = input("\nx__> ").strip().lower()
        except KeyboardInterrupt:
            exit()

        if choice in ['add', '1', 'a']:
            add_account(data)
            add_to_yaml(data, master_password)

        elif choice in ['find', '2', 'f']:
            website = input("\nsearch: ").strip()
            account = find_account(data, website)
            if account:
                pretty_print(account)
            else:
                print("not found")

        elif choice in ['change', '3', 'c']:
            website = input("website: ").strip()
            change_account(data, website)
            add_to_yaml(data, master_password)

        elif choice in ['delete', '4', 'd']:
            website = input("website to delete: ").strip()
            delete_account(data, website)
            add_to_yaml(data, master_password)

        elif choice in ['sync', '5', 's']:
            if not os.path.exists('.git'):
                init_repo()

            if not os.path.exists('remote_url'):
                remote_url = input("repository URL: ").strip()
                commit_message = input("commit message: ").strip()
                sync_with_remote(commit_message, remote_url)
            else:
                remote_url = open('remote_url', 'r').read().strip()
                if has_changes():
                    commit_message = input("commit message: ").strip()
                    sync_with_remote(commit_message, remote_url)
                else:
                    print("all synced")

        elif choice in ['exit', '6', 'e']:
            break

if __name__ == "__main__":
    main()