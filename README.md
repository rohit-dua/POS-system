The code(app.py) is a REST API(developed using Flask) to handle the change notifications.
 
--------------------------------------------------------

Requirements:
Python2.x, Flask, flask_sqlalchemy


Prior to running the code the SQL tables have to be made using file db_create.py

--------------------------------------------------------

The API supports the following functions:

* Display Item Information:
  GET request to display item information.
  Accepts: item code
  eg: GET http://127.0.0.1:5000/api/v1.0/item/1

* Create New Item:
  POST json request to create new item.
  Accepts: A dictionary in json format with required parameters: ('code', 'name', 'size', 'color', 'quality')
  eg: POST '{"quality":"Grade1","size":"XL","color":"white", "code":1, "name":"Glass", "user":"rohit"}'  http://localhost:5000/api/v1.0/item

* Create New Item Variant:
  POST json request to create new item variant.
  Accepts: A dictionary in json format with required parameters: ('cost_price', 'selling_price', 'quantity', 'code')
  eg: POST '{"cost_price":100, "selling_price":10, "quantity": 1, "code":1, "user":"Adrian"}'  http://localhost:5000/api/v1.0/variant

* Update Item Information:
  PUT json request to update item information.
  Accepts: A dictionary in json format with required target item id and information to change.
  eg: PUT '{"quality":"great","size":"XL","color":"white", "user":"Mark"}' http://localhost:5000/api/v1.0/item/1

* Update Item Variant Information:
  PUT json request to update item variant information.
  Accepts: A dictionary in json format with required target item id and information to change.
  eg: PUT '{"quantity": 10, "user":"Mark"}' http://localhost:5000/api/v1.0/variant/1

* Delete Item:
  DELETE json request to delete item information.
  eg: DELETE '{"user":"rohit"}' http://localhost:5000/api/v1.0/item/1

* Notifications:
  GET request to list all the notifications.(optional: user specific)
  eg: GET http://localhost:5000/api/v1.0/notifications  or http://localhost:5000/api/v1.0/notifications/user/1



