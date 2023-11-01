import requests
import monsters
r = requests.get(' https://www.dnd5eapi.co/api/monsters/adult-black-dragon/')
print(r.status_code)
print(r.headers['Content-Type'])
print(r.json(object_hook=monsters.decode))
