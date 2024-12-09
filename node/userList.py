import json

class User:
  def __init__(self, user_id, key):
    self.user_id = user_id
    self.key = key

  def __str__(self):
    return f"User(ID: {self.user_id}, Key: {self.key})"
    
class UserList:
	def __init__(self):
		self.users = []

	def __str__(self):
		return '\n'.join([str(user) for user in self.users])
	
	def add_user(self, user):
		if isinstance(user, User):
			self.users.append(user)
			print(f"Added user wih id={user.user_id}.")
		else:
			print("Object is not an instance of User class.")

	def show_users(self):
		if not self.users:
			print("User list is empty.")
		else:
			for user in self.users:
				print(user)
	
	def to_json(self):
		return json.dumps([{'user_id': user.user_id, 'key': user.key} for user in self.users])
	
	def from_json(self, json_str):
		self.users = [User(user['user_id'], user['key']) for user in json.loads(json_str)]

	def from_file(self, file_path):
		try:
			with open(file_path, "r", encoding="utf-8") as file:
				self.from_json(file.read())
		except FileNotFoundError:
			print(f"File {file_path} was not found.")
		except json.JSONDecodeError:
			print(f"File {file_path} contains an invalid JSON format.")

	def to_file(self, file_path):
		try:
			with open(file_path, "w", encoding="utf-8") as file:
				file.write(self.to_json())
		except FileNotFoundError:
			print(f"File {file_path} was not found.")
		except json.JSONDecodeError:
			print(f"File {file_path} contains an invalid JSON format.")
