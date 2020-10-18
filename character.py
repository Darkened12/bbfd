import requests
from bs4 import BeautifulSoup

# All sprites and frame data are gotten from dustloop.com"


class Character:
    def __init__(self, find_name, game_page):
        """data contains a dict with all needed links.
        fd and sprites contain specific links, not bs4 objects or a list"""
        self._dustloop = 'http://www.dustloop.com'
        self._main_page = Character._get_main_page(game_page)
        self._find_name = find_name if find_name.lower() != 'nu' else "Nu-13"
        self._data = self._get_specific_character()

        self.name = [key for key in self._data.keys()][0]
        self.icon = self._data[self.name]['icon']

        self._fd = self._data[self.name]['fd']
        self._sprites = self._data[self.name]['sprites']

    def get_move(self, find_move_name):
        """Get a specific move using all other methods"""
        frame_data = self._get_frame_data()
        sprites = self._get_sprites()

        # Need to check both names separately
        for move in frame_data.keys():
            if '"' in find_move_name:
                temp_move_name = find_move_name.replace('"', '')
                if temp_move_name == move:
                    frame_data_name = move
                    break
                else:
                    continue
            elif find_move_name.lower() == move.lower():
                frame_data_name = move
                break

        else:
            for move in frame_data.keys():
                if find_move_name.lower() in move.lower():
                    frame_data_name = move
                    break
            else:
                raise MoveNotFound

        sprite_name = None

        # temporary fix for the 214/236B/22x/5AD meme
        if '214b' in frame_data_name.lower() and not '214bc' in frame_data_name.lower():
            for move in sprites.keys():
                if '214A/B' in move:
                    sprite_name = move
                    break
        elif '236b' in frame_data_name.lower() and not '236bc' in frame_data_name.lower():
            for move in sprites.keys():
                if '236A/B' in move:
                    sprite_name = move
                    break

        elif '22' in frame_data_name.lower():
            for move in sprites.keys():
                if '22A/B' in move and '22c' not in frame_data_name.lower():
                    sprite_name = move
                    break
                elif '22A/B/C' in move and '22c' in frame_data_name.lower():
                    sprite_name = move
                    break

        elif 'reversal' in frame_data_name.lower():
            for move in sprites.keys():
                if '5AD' in move:
                    sprite_name = move
                    break

        for move in sprites.keys():
            if sprite_name is not None:
                break
            if 'j.' in frame_data_name.lower() and ' ' in frame_data_name:
                for split_name in frame_data_name.split(' '):
                    if move.lower() == split_name.lower():
                        sprite_name = move
                        break
            elif move.lower() == frame_data_name.lower():
                sprite_name = move
                break
        else:
            for move in sprites.keys():
                if sprite_name is not None:
                    break
                if 'j.' in frame_data_name.lower() and ' ' in frame_data_name:
                    for split_name in frame_data_name.split(' '):
                        if move.lower() in split_name.lower():
                            sprite_name = move
                            break
                elif move.lower() in frame_data_name.lower() and '22' not in find_move_name:
                    print('ok')
                    sprite_name = move
                    break
                elif find_move_name.lower() in move.lower():
                    sprite_name = move
                    break
            else:
                sprite_name = None

        if sprite_name is None:
            sprite = ''
        else:
            sprite = self._get_high_quality_sprite(sprites[sprite_name])

        return {
            frame_data_name: {
                'fd': frame_data[frame_data_name],
                'sprite': sprite
            }
        }

    def get_movelist(self):
        """Return the character movelist"""
        return [move for move in self._get_frame_data()]

    @staticmethod
    def _get_main_page(website):
        """Return a BeautifulSoup object given an website"""
        return BeautifulSoup(requests.get(website).content, 'html.parser')

    def _get_all_characters(self, main_page):
        """Get the main page, frame data page and icon.png from all characters"""

        heading_div = main_page.find('div', {'class': 'heading'})  # dustloop changed its code so this is necessary
        character_div = heading_div.next.next

        if character_div is None:  # CF fix
            character_div = main_page.find_all('div', {'class': 'center'})[1]

        result = {}

        for a_tag, img_tag in zip(character_div.find_all('a'), character_div.find_all('img')):
            # a tag contain the frame data and sprites link, img contain the icon
            title = a_tag.get('title')
            result.update({
                title[title.index('/') + 1:]: {
                    'sprites': self._dustloop + a_tag.get('href'),
                    'fd': self._dustloop + a_tag.get('href') + '/Frame_Data',
                    'icon': self._dustloop + img_tag.get('src')
                }
            })

        return result

    def _get_specific_character(self):
        """Find the specific character given a name"""
        characters = self._get_all_characters(self._main_page)
        for character in characters.keys():
            if self._find_name.lower() in character.lower():
                return {character: characters[character]}
        else:
            raise CharacterNotFound

    def get_general_info(self):
        """Parse general information about the character"""
        table = Character._get_main_page(self._sprites).find('table', {'class': 'stripe'})

        result = []
        for td in table.find_all('td'):
            if td.get_text() != '':
                result.append(td.get_text())

        return {
            result[0]: result[1],
            result[2]: result[3],
            result[4]: result[5]
        }

    def _get_high_quality_sprite(self, sprite_link):
        sprite_div = Character._get_main_page(sprite_link).find('div', {'class': 'fullImageLink'})
        img_tag = sprite_div.find('img')

        return self._dustloop + img_tag.get('src')

    def _get_sprites(self):
        """Parse a bs4 object cointaining the character's page and extract its sprite links"""
        character = self._get_main_page(self._data[self.name]['sprites'])
        result = {}

        for big_tag in character.find_all('big'):
            # big contain the move name. Its next siblings contain the sprite link.
            move_name = big_tag.get_text()
            sprite = ''
            auto_combo = {}

            # the if statement below checks if big tag siblings contain more than one sprite link. If so,
            # it's an auto combo and all must be added
            if len([i for i in big_tag.next_siblings if i not in ['\n', ' ']]) > 2 or 'j.' in move_name:
                for sibling in big_tag.next_siblings:
                    if sibling.name == 'small':
                        move_name += ' ' + sibling.get_text()
                    if sibling.name == 'div':

                        if len(auto_combo) == 0:
                            sprite = self._dustloop + sibling.find('a').get('href')
                            auto_combo.update({move_name.replace('+', ''): sprite})  # B+C fix
                        else:
                            move_name += move_name[-1]
                            sprite = self._dustloop + sibling.find('a').get('href')
                            auto_combo.update({move_name.replace('+', ''): sprite})  # B+C fix
            else:
                for sibling in big_tag.next_siblings:
                    if sibling.name == 'small':
                        move_name += ' ' + sibling.get_text()
                    elif sibling.name == 'div':
                        sprite = self._dustloop + sibling.find('a').get('href')

            if len(auto_combo) == 0:
                move_name = move_name.replace('+', '')  # B+C fix
                result.update({move_name: sprite})
            else:
                result.update(auto_combo)

        return result

    def _get_frame_data(self):
        """Parse all frame data from the given character"""

        def _text_formatting(bs4_tag):
            """Simple formatting that will be called a lot"""
            return bs4_tag.get_text().replace('\n', '')

        tables = Character._get_main_page(self._fd).find_all('table', {'class': 'wikitable'})
        result = {}
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                move = row.find('th')

                if move is not None:
                    move_small = move.find('small')
                else:
                    continue

                if move_small is not None:
                    move_name = move.get_text().replace(move_small.get_text(), ' ' + move_small.get_text()).replace(
                        '\n', '')
                else:
                    move_name = _text_formatting(move)

                move_name = move_name.replace('+', '')  # B+C fix
                fd = row.find_all('td')

                try:
                    result.update({
                        move_name: {
                            "Damage": _text_formatting(fd[0]),
                            "Cancel": _text_formatting(fd[1]),
                            "Attribute": _text_formatting(fd[4]),
                            "Guard": _text_formatting(fd[5]),
                            "Startup": _text_formatting(fd[6]),
                            "Active": _text_formatting(fd[7]),
                            "Recovery": _text_formatting(fd[8]),
                            "Frame Adv": _text_formatting(fd[9]),
                            "Blockstun": _text_formatting(fd[11]),
                            "Invul/GP": _text_formatting(fd[19])
                        }
                    })
                except (AttributeError, IndexError):
                    continue

        return result

		
class MoveNotFound(Exception):
    """Couldn't find a matching move name"""


class CharacterNotFound(Exception):
    """Couldn't find a matching character name"""

