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
  
  def loadUsersFromFile(self, file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        for user_data in data:
          if "user_id" in user_data and "key" in user_data:
            user = User(user_id=user_data["user_id"], key=user_data["key"])
            self.addUser(user)
          else:
            print(f"Pominięto niekompletny wpis: {user_data}")
    except FileNotFoundError:
      print(f"Plik {file_path} nie został znaleziony.")
    except json.JSONDecodeError:
      print(f"Plik {file_path} zawiera błędny format JSON.")

file_path = "users.json"
example_data = [
    {"user_id": 1, "key": "klucz123"},
    {"user_id": 2, "key": "klucz456"},
    {"user_id": 3, "key": "klucz789"}
]
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(example_data, file, ensure_ascii=False, indent=4)

u1 = User(user_id=4, key="klucz222")
u2 = User(user_id=5, key="klucz444")

user_list = UserList()
user_list.addUser(u1)
user_list.addUser(u2)
user_list.loadUsersFromFile(file_path)

user_list.showUsers()