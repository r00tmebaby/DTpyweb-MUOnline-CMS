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
# DTPyWeb Created for educational purposes only
# Original Release on DarksTeam.net = > https://darksteam.net/
# @author  r00tme 16/02/2019
# @version: 1.0
###############################################

from flask import Flask, render_template, flash, redirect, url_for, request, session
from classes.forms import RegistrationForm
from classes.functions import Main
import Config, datetime, textwrap

main = Main()
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.Secret_Key


@app.context_processor
def _processor():
    return dict(
        date_now=datetime.datetime.now().strftime("%d.m.%Y %H:%M:%S"),
        author="© 2019  r00tme - DTpyWeb. All rights reserved.",
        theme=main.themes_check()[0],
        theme_switch_form=main.themes_check()[1],
        top10=main.rankings(" TOP 10 "),
        header="header.html",
        server=Config.Server_Name,
    )


@app.route('/userinfo', methods=['GET'])
@app.route('/userinfo<path:path>', methods=['GET', 'POST'])
def users_info(path):
    main.theme_switcher()
    if main.user_exist(path[1:], False):

        item_image = []
        item_info = []

        for i in range(0, 12):
            user_items = textwrap.wrap(main.return_items(path[1:]), Config.Item_Hex_Len)[i]
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
    return render_template("modules/" + request.path + ".html", title=u"%s" % request.path[1:].capitalize(),
                           download_links=Config.Dl_Links)


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


if __name__ == '__main__':
    app.run(debug=Config.Web_Debug, host=Config.Web_IP, port=Config.Web_Port)
