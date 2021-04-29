# Hey, for our database we just have 4 Columns:
- id(int, auto_increment, primary key)
- short(varchar)
- points_to(varchar)
- added_by_host(varchar)
- clicks(int)

Added by Host is only necessary if you want to host the api on multiple domains but on the same database 