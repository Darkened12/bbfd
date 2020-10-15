# bbfd
## An webscrapping tool to get information from dustloop about blazblue charatecters from BBCF and BBTAG
### Library Requeriments: requests, bs4
### Usage:

```python
from character import Character

bbtag_gamepage = 'https://www.dustloop.com/wiki/index.php?title=BlazBlue_Cross_Tag_Battle'

char = Character(
    find_name='ruby', # here you put the character's name
    game_page=bbtag_gamepage # here the gamepage link
)

print(char.name)  # print the character's name
print(char.icon)  # print the character's icon link
print(char.get_general_info())  # print basic status
print(char.get_movelist())  # get a list of all move names
print(char.get_move(find_move_name='5a'))  # get the desired move
```
