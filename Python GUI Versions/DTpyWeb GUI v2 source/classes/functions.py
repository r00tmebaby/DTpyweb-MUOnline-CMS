'''
Author 	: Zdravko Georgiev (r00tmebaby)
Github 	: https://github.com/r00tmebaby
License : MIT
Copyright (c) 2019 Zdravko Georgiev (r00tmebaby)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
##############################################
# DT Py Web Created for educational purposes only
# Original Release on DarksTeam.net = > https://darksteam.net/
# @author  r00tme 16/02/2019
# @version: 1.0
###############################################

import pyodbc as db, struct, zlib, base64, binascii, os
from flask import render_template, flash, session, request
from configparser import ConfigParser

configPath = "config.ini"
config = ConfigParser()
config.read(configPath)

class Main:
    @staticmethod
    def conn():
        try:
            connection = db.connect('DRIVER=%s;SERVER=%s;PORT=%s;DATABASE=%s;UID=%s;PWD=%s' %
                                    (config.get("sqlConfig", "sql_driver"), config.get("sqlConfig", "sql_server"), config.getint("sqlConfig", "sql_port"), config.get("sqlConfig", "sql_dbase"),
                                     config.get("sqlConfig", "sql_user"), config.get("sqlConfig", "sql_pass")), autocommit= True)
            connection.setdecoding(db.SQL_CHAR, encoding='utf-8')
            connection.setdecoding(db.SQL_WCHAR, encoding='utf-8')
            connection.setdecoding(db.SQL_WMETADATA, encoding='utf-8')
            connection.setencoding(encoding='utf-8')
            return connection.cursor()
        except Exception as e:
            print("Error: " + str(e))



    def theme_switcher(self):
        if request.method == 'POST' and config.getboolean("webConfig", "theme_switcher"):
            if 'theme' in request.form:
                if os.path.isfile(f'templates/themes/%s/layout.html' % request.form['theme']):
                    session['theme'] = request.form['theme']
                    return render_template("themes/" + session['theme'] + "/home.html", title="News")
                else:
                    flash('This theme does not exist', 'error')

    def themes_check(self):
        themes_list = []
        for themes in os.listdir('templates/themes/'):
            themes_list.append(themes)

        if config.getboolean("webConfig", "theme_switcher"):
            if session.get('theme') and os.path.isfile("templates/themes/" + session['theme'] + "/layout.html"):
                    return ["themes/" + session['theme'] + "/layout.html", themes_list]
            else:
                return ["themes/" + config.get("webConfig", "web_theme")  + "/layout.html", themes_list]
        elif not config.getboolean("webConfig", "theme_switcher") and os.path.isfile("templates/themes/" + config.get("webConfig", "web_theme") + "/layout.html"):
            return ["themes/" + config.get("webConfig", "web_theme")  + "/layout.html", False]
        else:
            flash("This theme does not exist, please check the directory path", 'error')
            return [False, False]

    def login(self):
        if 'login_username' in request.form and 'login_password' in request.form:
            if self.user_login(request.form['login_username'], request.form['login_password']):
                flash(r'You were successfully logged in', 'success')
            else:
                flash(r"Wrong Credentials", 'error')

    def rankings(self, selection=r"", table=r"Character", sort=r"ORDER BY Resets desc, cLevel desc", clause=r""):
        return self.conn().execute(f"SELECT { selection } * FROM { table } { sort } { clause }")

    def user_login(self, user, password):
        for rows in self.conn().execute("Select * from [Memb_Info] where [memb___id]=? and [memb__pwd] = ?", user, password):
            if rows[1] == user:
                session['username'] = user
                return session['username']
            else:
                return False

    def user_exist(self, variable, check_account=True):
        if check_account:
            query = "Select * from Memb_Info where memb___id=? "
        else:
            query = "Select * from Character where Name=?"

        for rows in self.conn().execute(query, variable):
            if rows[1] == variable:
                return True
            else:
                return False

    def register(self, username, password, email, fques, fansw):
        if self.user_exist(username, True):
            flash(f'Account {username}  is already registered  !', 'error')#
        else:
            self.conn().execute("Insert into Memb_Credits (memb___id) values (?)", username)
            self.conn().execute("Insert into MEMB_Info (memb___id,memb_name,memb__pwd,sno__numb,mail_addr,fpas_answ,fpas_ques, bloc_code,ctl1_code) Values (?,?,?,?,?,?,?,?,?)",
                                (username, username, password, '111111111', email, fansw, fques, '0', '0'))
            flash(f'Account {username}  is registered  !', 'success')
            session['username'] = username
            return render_template("Tema1/home.html", title=f"{session['username']} Page")

    @staticmethod
    def encrypt(texts, key=config.get("webConfig", "secret_key")):
        text = '{}{}'.format(texts, struct.pack('i', zlib.crc32(texts)))
        enc = []
        for i in range(len(text)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(text[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc))

    @staticmethod
    def decrypt(texts, key=config.get("webConfig", "secret_key")):
        dec = []
        encoded_text = base64.urlsafe_b64decode(texts)
        for i in range(len(encoded_text)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(encoded_text[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        dec = "".join(dec)
        checksum = dec[-4:]
        dec = dec[:-4]
        assert zlib.crc32(dec) == struct.unpack('i', checksum)[0], flash('Decode Checksum Error', 'error')
        return dec

    def return_items(self, variable, account=False):
        if not account:
            items = self.conn().execute("Select Inventory from Character where Name = ?", variable)
        else:
            items = self.conn().execute("Select Items from warehouse where memb___id = ?", variable)
        return binascii.hexlify(items.fetchval()).decode().upper()


    def hextobin(self, hexval):
        thelen = len(hexval) * 4
        binval = bin(int(hexval, 16))[2:]
        while ((len(binval)) < thelen):
            binval = '0' + binval
        return binval

    def item_info(self, items):
        if items == r"F"*config.getint("webConfig", "item_hex_len") :
            return False
        else:
            item_excellent   = ""
            colors           = ""
            addinfo          = ""
            item_req         = ""
            item_for         = ""
            item_ancient     = ""
            image_file_level = ""
            item_sk_lu       = ""
            name_color       = "#FFF"
            image_folder     = r"static/default-images/items/"
            durability_steps = [6, 8, 10, 12, 14, 17, 21, 26, 32, 39, 47]
            damage_steps     = {10: 1, 11: 3, 12: 6, 13: 10, 14: 15, 15: 21}
            # Todo defence calculations
            # defence_steps    = {10: 9, 11: 8, 12: 6, 13: 3, 14: 1, 15: 6}
            # Todo admin module or/and option for showing serial
            item_serial      = int(self.hextobin(items[6:15]), 2)
            if not (int(self.hextobin(items[0:1]), 2) % 2 == 0): change = 0b10000
            else: change = 0
            item_id   = int(self.hextobin(items[1:2]), 2) | change
            item_info = self.conn().execute("Select * from DTpyWEB_AllSeasons_Items where type =? and id=?",
                                            (int(self.hextobin(items[0:1]), 2) | int(items[14:16], 16) >> 3 & 0b10000) >>
                                            1, item_id).fetchall()
            print(item_info[0])
            item_name = item_info[0][2]
            if not item_info:
                flash("We found unknown items", "error")
                return False

            # Which Class can equip the item
            if item_info[0][0] < 12:
                if int(item_info[0][18]) > 0: item_req += "Level Requirement:" + item_info[0][18] + "<br>"
                if int(item_info[0][19]) > 0: item_req += "Strength Requirement: " + item_info[0][19] + "<br>"
                if int(item_info[0][20]) > 0: item_req += "Agility Requirement: " + item_info[0][20] + "<br>"
                if int(item_info[0][22]) > 0: item_req += "Vitality Requirement: " + item_info[0][22] + "<br>"
                if int(item_info[0][21]) > 0: item_req += "Energy Requirement: " + item_info[0][21] + "<br>"
                if int(item_info[0][23]) > 0: item_req += "Command Requirement: " + item_info[0][23]+ " <br>"
                if int(item_info[0][32]) == 1: item_for += "Can be equipped by Grow Lancer <br>"
                if int(item_info[0][31]) == 1:  item_for += "Can be equipped by Rage Fighter <br>"
                if int(item_info[0][26]) == 1:  item_for += "Can be equipped by Dark Knight <br>"
                if int(item_info[0][26]) == 2:  item_for += "Can be equipped by Blade Knight<br>"
                if int(item_info[0][26]) == 3:  item_for += "Can be equipped by Blade Master  <br>"
                if int(item_info[0][25]) == 1:  item_for += "Can be equipped by Dark Wizard<br>"
                if int(item_info[0][25]) == 2:  item_for += "Can be equipped by Soul Master<br>"
                if int(item_info[0][25]) == 3:  item_for += "Can be equipped by Grand Master<br>"
                if int(item_info[0][27]) == 1:  item_for += "Can be equipped by Fairy Elf<br>"
                if int(item_info[0][27]) == 2:  item_for += "Can be equipped by Muse Elf<br>"
                if int(item_info[0][27]) == 3:  item_for += "Can be equipped by Height elf<br>"
                if int(item_info[0][28]) == 1:  item_for += "Can be equipped by Magic Gladiator<br>"
                if int(item_info[0][28]) == 2:  item_for += "Can be equipped by Duel Master<br>"
                if int(item_info[0][28]) == 3:  item_for += "Can be equipped by Duel Master<br>"
                if int(item_info[0][29]) == 1:  item_for += "Can be equipped by Dark Lord<br>"
                if int(item_info[0][29]) == 2:  item_for += "Can be equipped by Lord Emperor<br>"
                if int(item_info[0][29]) == 3:  item_for += "Can be equipped by Lord Emperor<br>"
                if int(item_info[0][30]) == 1:  item_for += "Can be equipped by Summoner<br>"
                if int(item_info[0][30]) == 2:  item_for += "Can be equipped by Bloody Summoner<br>"
                if int(item_info[0][30]) == 3:  item_for += "Can be equipped by Dimension Master<br>"
                if len(item_for) == 328: item_for = "</br>Can be equipped by any class"

            # Item Skill, Luck, Options, Excellence and Ancient Calculations
            if int(self.hextobin(items[2:3])[0]) > 0:
                item_sk_lu += "This item has a Skill </br>"

            if int(self.hextobin(items[2:4])[5]) > 0:
                item_sk_lu += "This Item has a Luck </br>"

            if int(self.hextobin(items[2:4])[1:5], 2) > 0:
                item_name = item_name + " +%s" % int(self.hextobin(items[2:4])[1:5], 2)
                if item_info[0][0] > 11 and (item_info[0][3] == -1):
                    image_file_level = "-"+self.hextobin(items[2:4])[1:5], 2

            if int(items[2:4], 16) & 3 | ((int(items[14:16], 16) >> 6 & 0b1) << 2) > 0:
                  item_excellent+= str(self.excellent_options()[int(item_info[0][9])].split(",")[6] + " + " +
                               str(4 * (int(items[2:4], 16) & 3 | ((int(items[14:16], 16) >> 6 & 0b1) << 2)))) + "</br>"
            for i in range(0, 5):
                if self.hextobin(items[14:16])[2:][::-1][i] == "1":
                   name_color = "#93ff26"
                   item_excellent += self.excellent_options()[int(item_info[0][9])].split(",")[i] + "</br>"

            if len(item_excellent) > 0:
                item_name = " Excellent " + item_name

            # Render Images Path
            if os.path.isfile("%s%s/%s%s.gif" % (image_folder, item_info[0][0], item_info[0][1], image_file_level)):
                item_image = "%s%s/%s%s.gif" % (image_folder, item_info[0][0], item_info[0][1], image_file_level)
            else:
                item_image = "static/items/no-item.gif"

            # Durability Calculation
            if item_info[0][15]:
                if item_id == 5 and item_info[0][16]:calc_durability = item_info[0][16]
                elif item_id != 5 and item_id < 12 and item_info[0][15]:calc_durability = item_info[0][15]
                else:calc_durability = 0
                if int(self.hextobin(items[2:4])[1:5], 2) < 5:
                    calc_durability = int(calc_durability) + int(self.hextobin(items[2:4])[1:5], 2)
                else:
                    calc_durability = int(calc_durability) + int(durability_steps[int(self.hextobin(items[2:4])[1:5], 2) - 5])
                if len(item_excellent) > 0: calc_durability = int(calc_durability) + 15
                if int(item_info[0][15]) > 0:
                     item_durability = " Durability:[%s/%s]</br>" % (calc_durability, int(items[4:6], 16))
                else:
                     item_durability = " Magic Durability:[%s/%d]</br>" % (calc_durability, int(items[4:6], 16))

            # Weapon Damage Calculations
            if item_info[0][0] <= 5:
                min_dmg = int(item_info[0][12])
                max_dmg = int(item_info[0][13])
                if damage_steps.get(int(self.hextobin(items[2:4])[1:5], 2)):
                    min_dmg += int(damage_steps.get(int(self.hextobin(items[2:4])[1:5], 2)))
                    max_dmg += int(damage_steps.get(int(self.hextobin(items[2:4])[1:5], 2)))
                if len(item_excellent) > 0 and int(self.hextobin(items[17:18]), 2) == 0:
                        min_dmg += 35
                        max_dmg += 35
                else:
                        min_dmg += 25
                        max_dmg += 25

                if min_dmg > int(item_info[0][12]): dmg_color = "#99CFFF"
                if item_info[0][5] == 1:
                    addinfo += f"<span style='color:{dmg_color}'> Two handed attack power: {min_dmg} ~ {max_dmg}</span></br>"
                else:
                    addinfo += f"<span style='color: {dmg_color}'> One handed attack power: {min_dmg} ~ {max_dmg}</span></br>"
                if int(item_info[0][17]) > 0:
                    addinfo += f"</br> Magic Power: {item_info[0][17]}</br>"
                addinfo += " Attack Speed: %s</br>" % item_info[0][14]

            if item_info[0][0] == 11:
                addinfo += f" Walk Speed: {item_info[0][48]}</br>"

            # Defence Calculations
            if 12 > item_info[0][0] > 5:
                if not item_info[0][0] == 6:
                    default_def = int(item_info[0][45]) + (int(self.hextobin(items[2:4])[1:5], 2) * 3)
                    if len(item_excellent) > 0 and int(self.hextobin(items[17:18]), 2) == 0:
                          default_def += 15
                          colors = "#99CFFF"
                    else: default_def += 25
                    addinfo += f"<span style='color:{colors}'>Armor: {default_def}</span></br>"
                else:
                    default_def = int(item_info[0][45]) + int(self.hextobin(items[2:4])[1:5], 2)
                    success_block = int(item_info[0][46]) + (int(self.hextobin(items[2:4])[1:5], 2) * 3)
                    if len(item_excellent) > 0 or int(self.hextobin(items[17:18]), 2) > 0:
                        success_block += 30
                        colors = "#99CFFF"
                    addinfo += f"<span style='color:{colors}'>Armor: {default_def}</span></br>" \
                        f"<span style='color:{colors}'>Defense Rate: {success_block}</span></br>"
            if int(self.hextobin(items[17:18]), 2) > 0:
                name_color = "#ff26ff"
                item_name  = " Ancient " + item_name
                if int(self.hextobin(items[17:18]), 2) > 5: item_ancient = "Stamina +10"
                else: item_ancient = "Stamina +5"

        item_tooltip = f"<p style='color:{name_color}'><b>%s</b></p>" \
                       f"<p>%s %s %s </p><p style='opacity:0.4'>%s</p> " \
                       f"<p style='color:#ff26ff'> %s </p>" \
                       f"<p style='color:#00BFFF'>%s %s</p>" % \
                       (item_name, addinfo, item_durability, item_req, item_for,
                        item_ancient, item_sk_lu, item_excellent)

        return [item_tooltip, item_image]

    @staticmethod
    def excellent_options():
        return [
                    # Weapons
                    'Increase rate of Mana after hunting monsters +Mana/8,'
                    'Increase rate of Life after hunting monsters +life/8,'
                    'Increase Attacking(Wizardry)speed +7,'
                    'Increase Damage +2%,'
                    'Increase Damage +level/20,'
                    'Excellent Damage Rate +10%,'
                    'Additional Dmg',
                    # Armors
                    'Increases rate of Zen after hunting monsters +30%,'
                    'Defense success rate +10%,'
                    'Reflect Damage +5%,'
                    'Damage Decrease +4%,'
                    'Increase Max Mana +4%,'
                    'Increase Max HP +4%,'
                    'Additional Defense',
                    # Wings
                    '+ 115 HP,'
                    '+ 115 MP,'
                    'Ignore Enemy Defence 3%,'
                    '+ 50 Max Stamina,'
                    'Wizardly Speed +7,'
                    ','
                    'Additional Defense',
                    # Rings
                    '+ HP 4%,'
                    '+ MANA 4%,'
                    'Reduce DMG +4%,'
                    'Reflect DMG +5%,'
                    'Defence Rate +10%,'
                    'Zen After Hunting +40%,'
                    'Additional Damage',
                    # Pendants
                    '+ EXE DMG Rate +10%,'
                    '+ DMG Lvl/20,'
                    '+ DMG 2%,'
                    '+ Wizardly Speed +7,'
                    'Life After Hunting (Life/8),'
                    'Mana After Hunting (Mana/8),'
                    'Additional Defense',
                    # Todo all remaining item options to season 13
                    # Unknown 
                    'Unknown Excellent Option,'
                    'Unknown Excellent Option,'
                    'Unknown Excellent Option,'
                    'Unknown Excellent Option,'
                    'Unknown Excellent Option,'
                    'Unknown Excellent Option,'
                    'Additional Defense'
                ]


