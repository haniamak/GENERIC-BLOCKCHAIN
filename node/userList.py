import json

class User:
  def __init__(self, user_id, key):
    self.user_id = user_id
    self.key = key

  def __str__(self):
    return f"Użytkownik(ID: {self.user_id}, Klucz: {self.key})"
    
class UserList:
  def __init__(self):
    self.users = []

  def __str__(self):
    return '\n'.join([str(user) for user in self.users])
  
  def addUser(self, user):
    if isinstance(user, User):
      self.users.append(user)
      print(f"Użytkownik o ID {user.user_id} został dodany.")
    else:
      print("Obiekt nie jest instancją klasy Uzytkownik.")

  def showUsers(self):
    if not self.users:
      print("Lista użytkowników jest pusta.")
    else:
      for user in self.users:
        print(user)
  
  def toJson(self):
    return json.dumps([{'user_id': user.user_id, 'key': user.key} for user in self.users])
  
  def fromJson(self, jsonStr):
      self.users = [User(user['user_id'], user['key']) for user in json.loads(jsonStr)]

  def fromFile(self, file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as file:
        # data = json.load(file)
        self.fromJson(file.read())
    except FileNotFoundError:
      print(f"Plik {file_path} nie został znaleziony.")
    except json.JSONDecodeError:
      print(f"Plik {file_path} zawiera błędny format JSON.")

  def toFile(self, file_path):
    try:
      with open(file_path, "w", encoding="utf-8") as file:
        file.write(self.toJson())
    except FileNotFoundError:
      print(f"Plik {file_path} nie został znaleziony.")
    except json.JSONDecodeError:
      print(f"Plik {file_path} zawiera błędny format JSON.")
