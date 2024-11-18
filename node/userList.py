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

u1 = User(user_id=1, key="klucz123")
u2 = User(user_id=2, key="klucz456")

user_list = UserList()
user_list.addUser(u1)
user_list.addUser(u2)

user_list.showUsers()