import PySimpleGUI as sg
import os, re, subprocess
from flask import Flask, render_template, flash, redirect, url_for, request, session
from classes.forms import RegistrationForm
from classes.functions import Main
import datetime, textwrap
from configparser import ConfigParser
from multiprocessing import Process
import webbrowser

import threading

configPath = "config.ini"
config = ConfigParser()
config.read(configPath)


def validipv4(ip):
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip) is not None


sqlRefference = "Windows Drivers Reference\n" \
                    "{SQL Server} - released with SQL Server 2000\n" \
                    "{SQL Native Client} - released with SQL Server 2005 (also known as version 9.0)\n" \
                    "{SQL Server Native Client 10.0} - released with SQL Server 2008\n" \
                    "{SQL Server Native Client 11.0} - released with SQL Server 2012\n" \
                    "{ODBC Driver 11 for SQL Server} - supports SQL Server 2005 through 2014\n" \
                    "{ODBC Driver 13 for SQL Server} - supports SQL Server 2005 through 2016\n" \
                    "{ODBC Driver 13.1 for SQL Server} - supports SQL Server 2008 through 2016\n" \
                    "{ODBC Driver 17 for SQL Server} - supports SQL Server 2008 through 2017"

sqlConnect =  [
                [sg.Text("SQL Driver", size=(10,1)), sg.DropDown(
                  enable_events=True,
                  readonly=True,
                  font=10,
                  default_value=config.get("sqlConfig", "sql_driver"),
                  size=(24,1),
                  tooltip=sqlRefference, pad=(0,5),
                  values=["{SQL Server}",
                          "{SQL Native Client}",
                          "{SQL Server Native Client 10.0}",
                          "{SQL Server Native Client 11.0}",
                          "{ODBC Driver 11 for SQL Server}",
                          "{ODBC Driver 13 for SQL Server}",
                          "{ODBC Driver 13.1 for SQL Server}",
                          "{ODBC Driver 17 for SQL Server}"])],
              [sg.Text("Instance",size=(10,1),pad=(0,5) ), sg.InputText(default_text=(config.get("sqlConfig", "SQL_SERVER"))), ],
              [sg.Text("Port", size=(10,1) ,pad=(0,5) ),sg.InputText(default_text=(config.get("sqlConfig", "SQL_PORT")))],
              [sg.Text("Username", size=(10,1),pad=(0,5)),sg.InputText( default_text=(config.get("sqlConfig", "SQL_USER")))],
              [sg.Text("Password", size=(10,1),pad=(0,5)), sg.InputText(password_char="*",default_text=(config.get("sqlConfig", "SQL_PASS")))],
              [sg.Text("Database", size=(10,1),pad=(0,5)), sg.InputText(default_text=(config.get("sqlConfig", "SQL_DBASE")))]]


def isPortFree(host,port):
    import socket, errno

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as e:
        return False
    finally:
        return True
    s.close()


def ExecuteCommandSubprocess(command, wait=False, quiet=True, *args):
    try:
        sp = subprocess.Popen([command,*args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if wait:
            out, err = sp.communicate()
            if not quiet:
                if out:
                    print(out.decode("utf-8"))
                if err:
                    print(err.decode("utf-8"))
    except Exception as e:
        print('Exception encountered running command ', e)
        return ''

    return (out.decode('utf-8'))

def listThemes():
    themes_list = []
    for themes in os.listdir('templates/themes/'):
        themes_list.append(themes)
    return  themes_list

def seasons(vars):
      if vars == "Season 0-1":
          return 20
      elif vars == "Season 2-8":
          return 32
      elif vars == "Season 9-13":
          return 64
      else:
          return 20
def season_reverse(value):
    if value ==  20:
        return "Season 0-1"
    elif value == 32:
        return "Season 2-8"
    elif value == 64:
        return "Season 9-13"
    else:
        return "Season 0-1"

webSettings = [

               [sg.Text("Server Name", size=(10, 1), pad=(0, 5)), sg.InputText(default_text=(config.get("webConfig", "server_name"))), ],
               [sg.Text("Secret Key", size=(10, 1), pad=(0, 5)), sg.InputText(default_text=(config.get("webConfig", "secret_key")))],
               [sg.Text("Season", size=(10, 1), pad=(0, 5)), sg.DropDown(default_value=season_reverse(config.getint("webConfig", "item_hex_len")),
                                                                         values=["Season 0-1", "Season 2-8", "Season 9-13"], readonly=True)],
               [sg.Text("Web Debug", size=(10, 1), pad=(0, 5)), sg.Checkbox(text="", default=config.getboolean("webConfig", "web_debug"))],
               [sg.Text("Web IP", size=(10, 1), pad=(0, 5)), sg.InputText(default_text=(config.get("webConfig", "web_ip")))],
               [sg.Text("Web PORT", size=(10, 1), pad=(0, 5)), sg.InputText(default_text=(config.getint("webConfig", "web_port")))],
               [sg.Text("Web Theme", size=(10, 1), pad=(0, 5)), sg.DropDown(default_value=config.get("webConfig", "web_theme"),values=listThemes(), readonly=True)],
               [sg.Text("Theme Switcher", size=(10, 1), pad=(0, 5)), sg.Checkbox(text="", default=config.getboolean("webConfig", "theme_switcher"))]
]



layout = [[sg.TabGroup([[sg.Tab('SQL Settings', sqlConnect), sg.Tab('WEB Settings', webSettings)]])],
                         [sg.Button('Start Server', disabled=False,auto_size_button=False),
                          sg.Button('Stop Server', disabled=True, auto_size_button=False)]
          ]

window = sg.Window('DTpyWeb GUI v2', icon="static/default-images/favicon.ico",
                   auto_size_text=False,
                   default_element_size=(30, 1),
                   return_keyboard_events=True,
                   use_default_focus=False,
                   text_justification="left"
                   ).Layout(layout).Finalize()



def runWeb():
    configPath = "config.ini"
    config = ConfigParser()
    config.read(configPath)

    main = Main()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get("webConfig", "secret_key")
    @app.context_processor
    def _processor():
        return dict(
            date_now=datetime.datetime.now().strftime("%d.m.%Y %H:%M:%S"),
            author="© 2020  r00tme - DTpyWeb. All rights reserved.",
            theme=main.themes_check()[0],
            theme_switch_form = main.themes_check()[1],
            theme_switch_active = config.getboolean("webConfig", "theme_switcher"),
            top10=main.rankings(" TOP 10 "),
            header="header.html",
            server=config.get("webConfig", "server_name"),
        )

    @app.route('/userinfo', methods=['GET'])
    @app.route('/userinfo<path:path>', methods=['GET', 'POST'])
    def users_info(path):
        main.theme_switcher()
        if main.user_exist(path[1:], False):

            item_image = []
            item_info = []

            for i in range(0, 12):
                user_items = textwrap.wrap(main.return_items(path[1:]), config.getint("webConfig", "item_hex_len"))[i]
                if main.item_info(user_items):
                    item_image.append(main.item_info(user_items)[1])
                    item_info.append(main.item_info(user_items)[0])
                else:
                    item_image.append("")
                    item_info.append("")
            return render_template("modules/userinfo.html", title="Character Information Page",
                                   item_info=item_info, item_image=item_image, character=path[1:])

        else:
            flash(r'This user does not exist', 'error')
            return redirect(url_for('home'))

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        # TODO news System
        # * This route will be removed after the news system is completed
        main.login()
        main.theme_switcher()
        stripin = main.themes_check()[0].split('/')
        return render_template("%s/%s/home.html" % (stripin[0], stripin[1]), title="News")

    @app.route('/download', methods=['GET', 'POST'])
    @app.route('/about', methods=['GET', 'POST'])
    @app.route('/rules', methods=['GET', 'POST'])
    @app.route('/rankings', methods=['GET', 'POST'])
    def main_pages():
        main.login()
        main.theme_switcher()
        var = config.get("dl_links", "dl_links")
        cors = str(var).split("\n")
        return render_template("modules/" + request.path + ".html", title=u"%s" % request.path[1:].capitalize(),
                               download_links=cors)

    @app.route('/buy-credits', methods=['GET', 'POST'])
    @app.route('/my-auction', methods=['GET', 'POST'])
    @app.route('/buy-credits', methods=['GET', 'POST'])
    @app.route('/my-account', methods=['GET', 'POST'])
    @app.route('/my-characters', methods=['GET', 'POST'])
    @app.route('/vip-modules', methods=['GET', 'POST'])
    @app.route('/my-market', methods=['GET', 'POST'])
    def user_pages():
        main.theme_switcher()
        if 'username' not in session:
            flash(r'You do not have an access to this page', 'error')
            return redirect(url_for('home'))
        else:
            return render_template("modules/user/" + request.path + ".html",
                                   title=u"%s %s Page" % (request.path.split("-")[0][1:].title(),
                                                          request.path.split("-")[1].title()))

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash('You were logged out', 'info')
        return redirect('/home')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        main.theme_switcher()
        form = RegistrationForm()
        if form.validate_on_submit():
            main.register(
                form.username.data,
                form.password.data,
                form.email.data,
                form.question.data,
                form.answer.data)
        return render_template("modules/register.html", title="Register", form=form)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("modules/404.html", title="Page does not exist"), 404

    from flask import request
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'


    app.run(debug=False, host=config.get("webConfig", "web_ip"),
                port=config.getint("webConfig", "web_port"))

def thegui():
    while True:
        event, values = window.Read(timeout=0)
        if event is None or event == "Exit":           # always,  always give a way out!
            break
        if event is not sg.TIMEOUT_KEY:
            config.set("sqlConfig", str("sql_driver"), str(values[0]))
            config.set("sqlConfig", str("sql_server"), str(values[1]))
            if values[2].isdigit():
                config.set("sqlConfig", "sql_port", values[2])
            else:
                sg.Popup("Type a valid and not in use port number")
                window.FindElement(values[2]).Update(values[2][:-1])
            config.set("sqlConfig", str("sql_user"), str(values[3]))
            config.set("sqlConfig", str("sql_pass"), str(values[4]))
            config.set("sqlConfig", str("sql_dbase"), str(values[5]))


            config.set("webConfig", str("server_name"), str(values[6]))
            config.set("webConfig", str("secret_key"), str(values[7]))
            config.set("webConfig", str("item_hex_len"), str(seasons(values[8])))
            config.set("webConfig", str("web_debug"), str(values[9]))
            if validipv4(values[10]):
               config.set("webConfig", str("web_ip"), str(values[10]))
            else:
                sg.Popup("Type a valid IP address")
                window.FindElement(values[10]).Update(values[10][:-1])
            if values[11].isdigit():
                config.set("webConfig", "web_port", values[11])
            else:
                sg.Popup("Type a valid and not in use port number")
                window.FindElement(values[11]).Update(values[11][:-1])
            config.set("webConfig", str("web_theme"), str(values[12]))
            config.set("webConfig", str("theme_switcher"), str(values[13]))

            with open(configPath, "w+") as f:
                config.write(f)
            if event == "Start Server":
                window.Element('Start Server').Update(disabled=True)
                window.Element('Stop Server').Update(disabled=False)
                if isPortFree(values[10], int(values[11])):
                    threading.Thread(target=runWeb).start()
                    os.startfile("http://" + config.get("webConfig","web_ip") + ":" + config.get("webConfig","web_port"))
                else:
                    sg.Popup("Port %s is already in use, \nchange the port or close the program that use it" % values[10])
            if event == "Stop Server":
                    os.system('taskkill /f /im DTpyWeb.exe')
                    os.system('taskkill /f /im python.exe')
                    os.system('start DTpyWeb.exe')

if __name__ == '__main__':
    thegui()