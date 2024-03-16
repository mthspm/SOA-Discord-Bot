from pathlib import Path
from settings import *
from utils import debug, time_now, load_json, save_json, flagger

class GameSettings:
    def __init__(self, name) -> None:
        self.gamecfg_path = Path(__file__).parent / "users" / "gamecfg.json"
        self.load_games()
        self.name = name
        self.setup(name)

    def load_games(self):
        self.data = load_json(self.gamecfg_path)

    def setup(self, name):
        if name.lower() not in self.data:
            self.support = False
            self.settings = None
        else:
            self.support = True
            self.settings = self.data[name.lower()]
            self.image = self.settings['image']

    def get_settings(self):
        feedback = ""
        for key, value in self.settings.items():
            if not isinstance(value, dict):
                feedback += f"{key} : {value}\n"
            else:
                feedback += f"{key} : \n"
                for k, v in value.items():
                    feedback += f"\t{k} : {v}\n"
        return feedback
    
    def update_settings(self,setting, new_setting, user):
        pointer = self.settings
        check_inside_dicts = False

        if pointer is None:
            return False
        elif setting not in pointer:
            for key, value in pointer.items():
                if isinstance(value, dict):
                    if setting in value.keys():
                        pointer[key][setting] = new_setting
                        pointer['editor'] = user.name
                        pointer['date'] = time_now()
                        check_inside_dicts = True
                        break
            if not check_inside_dicts:
                return False
        else:
            pointer[setting] = value
            pointer['editor'] = user.name
            pointer['date'] = time_now()

        new_settings = self.data
        new_settings[self.name.lower()] = pointer

        
        save_json(self.gamecfg_path, new_settings)

        return True
    
