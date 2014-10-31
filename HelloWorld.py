# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
from db import Db
import hashlib
import time
import os
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# create a Flask instance, arg is name of package or module
webApp = Flask(__name__)    
webApp.secret_key = os.urandom(24)

# route() combine url and function, so we can use a function to handle a url
@webApp.route('/', methods = ['GET'])
def index():
    articles.sort(lambda x, y: cmp(y['date'], x['date']))
    return render_template("hello.html", articles = articles)
    
@webApp.route('/<username>', methods = ['GET', 'POST'])
def home(username):
    if "!" not in username:
        return "fuck"
    articles = getArticle()
    args = username.split("*")
    un = args[0]
    if "no" in username:
        if un == "!":
            return render_template("hello.html", info = "No result")
        else:
            return render_template("hello.html", info = "No result", username = un[1:])
    if len(args) > 1:
        blogs = [articles[int(i)] for i in args[1:]]
        blogs.sort(lambda x, y: cmp(y['date'], x['date']))
    else:
        articles.sort(lambda x, y: cmp(y['date'], x['date']))
        blogs = articles
    if un == "!":
        return render_template("hello.html", articles = blogs)
    else:
        hasstared = False;
        for article in articles:
            staredusers = article['stareduser'].split(";")
            staredusers
            if username[1:] in staredusers:
                hasstared = True
            else:
                hasstared = False
            article['hasstared'] = hasstared
        return render_template("hello.html",
                               articles = blogs,
                               username = un[1:],
                               hasstared = hasstared)

@webApp.route('/s', methods = ['GET'])
def signinform():
    return render_template("form.html")

@webApp.route('/s', methods = ['POST'])
def signin():
    username = request.form['username'].strip()
    md = hashlib.md5()
    md.update(request.form['password'].strip())
    pw = md.hexdigest()
    result = database.selectWhere("userinfo", "username", username)[0]
    if result != None and result["password"] == pw:
        return redirect(url_for("home", username = "!" + username))
    return "!"

@webApp.route('/so', methods = ['GET', 'POST'])
def signout():
    return redirect(url_for("index"))

@webApp.route("/r", methods = ['GET'])
def registerform():
    return render_template("register.html")

@webApp.route("/r", methods = ['POST'])
def register():
    un = request.form['username']
    results = database.selectCol("username", "userinfo")
    if un in results:
        return "!"
    md = hashlib.md5()
    md.update(request.form['password'].strip())
    pw = md.hexdigest()
    em = request.form['email']
    avatar = "default.jpg"
    cover = "default.jpg"
    database.insert("userinfo", un, pw, em, avatar, cover)
    return redirect(url_for("home", username = "!" + un))

@webApp.route('/writeblog/<username>', methods = ['GET', 'POST'])
def writeBlog(username):
    if username == "!":
        return "!"
    return render_template("write.html", username = username[1:])

def getArticle(userid = -1):
    articles = []
    if userid == -1:
        allData = database.selectAll("blog")
    else:
        allData = database.selectWhere("blog", "userid", userid)
        if not allData:
            return None
    for data in allData:
        data.pop("content")
        data['date'] = time.ctime(float(data['date']))
        articles.append(data)
    return articles

@webApp.route('/sb/<username>', methods = ['POST'])
def submitBlog(username):
    if username == "":
        return "!"
    title = request.form['title']
    abstract = request.form['abstract']
    content = request.form['text']
    date = str(time.time()) 
    database.insert("blog", title, content, abstract, date, username)
    return redirect(url_for("home", username = "!" + username))

@webApp.route("/detail/<title>/<username>", methods = ['GET'])
def detail(title, username):
    stareduser = []
    article = database.selectWhere("blog", "title", title)[0]
    staredusername = article['stareduser'].split(";")
    if "" in staredusername:
        staredusername.remove("")
    article['hasstared'] = username[1:] in staredusername
    for un in staredusername:
        data = database.selectWhatWhere("userinfo", ["avatarname"], "username", un)
        data = data[0]
        data['avatarname'] = AVATAR_FOLDER + data['avatarname']
        data['username'] = un
        stareduser.append(data)
        if len(stareduser) >= 3:
            break
    avatarname = database.selectWhere("userinfo", "username", article['userid'])[0]['avatarname']
    publisheravatarpath = "static/file/avatar/" + avatarname
    article['date'] = time.ctime(float(article['date']))
    comments = database.selectWhere("comments", "title", title)
    if comments:
        comments.sort(lambda x, y: cmp(y['date'], x['date']))
        for comment in comments:
            avatarname = database.selectWhere("userinfo",
                                              "username", comment['userid'])[0]['avatarname']
            comment['avatar'] = "static/file/avatar/" + avatarname
            comment['date'] = time.ctime(float(comment['date']))
    if username == "!":
        return render_template("detail.html",
                               article = article,
                               comments = comments,
                               publisheravatarpath = publisheravatarpath,
                               stareduser = stareduser)
    else:
        avatarname = database.selectWhere("userinfo",
                                          "username", username[1:])[0]['avatarname']
        commneteravatarpath = "static/file/avatar/" + avatarname
        return render_template("detail.html",
                               article = article,
                               username = username[1:],
                               comments = comments,
                               publisheravatarpath = publisheravatarpath,
                               commneteravatarpath = commneteravatarpath,
                               stareduser = stareduser)
    
@webApp.route("/c/<t>/<u>", methods = ['POST'])
def comment(t, u):
    date = str(time.time())
    content = request.form['content']
    database.insert("comments", date, content, u, t)
    return redirect(url_for("detail", title = t, username = "!" + u))

@webApp.route("/user/<username>")
def user(username):
    staredblogs = []
    authorsDict = {}
    authors = []
    userarticles = []
    photos = []
    msgs = []
    # select titles of the blogs which user has stared
    staredblognames = database.selectWhere("userinfo", "username", username)[0]['staredblog'].split(";")
    if '' in staredblognames:
        staredblognames.remove('')
    # select all blogs the user has stared by titles
    for sb in staredblognames:
        blog = database.selectWhere("blog", "title", sb)[0]
        blog.pop('stareduser')
        blog['date'] = time.ctime(float(blog['date']))
        # control the length of title display on html
        blog['title'] = blog['title'][0:9] + " . . ." if len(blog['title']) >= 10 else blog['title']
        staredblogs.append(blog)
        if blog['userid'] in authorsDict:
            authorsDict[blog['userid']] += 1 
        else:
            authorsDict[blog['userid']] = 1
    # sort in date
    staredblogs.sort(lambda x, y:cmp(x['date'], y['date']))
    staredblogs = staredblogs[0:3] if len(staredblogs) > 4 else staredblogs
    sorted(authorsDict.items(), lambda x, y:cmp(x[1], y[1]))
    # sort in most stared blogs' author
    authorsnames = authorsDict.keys()[0:2] if len(authorsDict) > 3 else authorsDict.keys()
    # select authors of the most stared blog
    for authorname in authorsnames:
        author = {}
        data = database.selectWhere("userinfo", "username", authorname)[0]
        author['authorname'] = data['username']
        author['avatar'] = AVATAR_FOLDER + data['avatarname']
        # select another blog of this author
        author['blog'] = database.selectWhatWhere("blog", ['title', 'date', 'abstract'], "userid", authorname)
        for blog in author['blog']:
            blog['date'] = time.ctime(float(blog['date']))
        authors.append(author)
    # blogs of user published
    articles = getArticle(userid = username)
    if articles:
        articles.sort(lambda x, y:cmp(y['star'], x['star']))
        index = 3 if len(articles) > 3 else len(articles)
        userarticles = articles[0:index]
    user = database.selectWhere("userinfo", "username", username)[0]
    photolist = database.selectWhatWhere("photo", ['photoname', 'date'], "userid", username)
    if photolist:
        photolist.sort(lambda x, y:cmp(y['date'], x['date']))
        photos = [photodict['photoname'] for photodict in photolist]
    msgdata = database.selectWhere("message", "recver", username)
    msgs = [msg for msg in msgdata if msg['readed'] == 0]
    msgs.sort(lambda x, y:cmp(float(y['date']), float(x['date'])))
    return render_template("user.html",
                           user = user,
                           avatar = AVATAR_FOLDER + user['avatarname'],
                           cover = COVER_FOLDER + user['covername'],
                           userarticles = userarticles,
                           staredblogs = staredblogs,
                           authors = authors,
                           photos = photos,
                           msgs = msgs)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
def md5Code(s):
    md5 = hashlib.md5()
    md5.update(s)
    return md5.hexdigest()

@webApp.route('/uploaduseravatar/<username>', methods = ['POST'])
def uploadAvatar(username):
    avatar = request.files['file']
    filename = avatar.filename
    if avatar and allowed_file(filename):
        # avoid same filename uploaded by different user
        fn = md5Code(filename.split(".")[0]) + "." + filename.split(".")[1]
        webApp.config['UPLOAD_FOLDER'] = AVATAR_FOLDER
        # delete old avatar...
        avatarname = database.selectWhatWhere("userinfo", ["avatarname"], "username", username)[0]['avatarname']
        # expect the default avatar
        if avatarname != "default.jpg":
            path = os.getcwd() + "/" + AVATAR_FOLDER + avatarname
            os.remove(path)
        # save the file and update database
        avatar.save(os.path.join(webApp.config['UPLOAD_FOLDER'], fn))
        database.updateWhatWhere("userinfo",
                                 "avatarname", fn,
                                 "username", username)
    return redirect(url_for("user", username = username))

@webApp.route("/uploadphoto/<username>", methods = ['POST'])
def uploadPhoto(username):
    photo = request.files['file']
    filename = photo.filename
    if photo and allowed_file(filename):
        fn = md5Code(filename.split(".")[0]) + "." + filename.split(".")[1]
        webApp.config['UPLOAD_FOLDER'] = COVER_FOLDER
        photo.save(os.path.join(webApp.config['UPLOAD_FOLDER'], fn))
        date = str(time.time())
        database.insert("photo", fn, username, date)
    return redirect(url_for("user", username = username))

@webApp.route("/search/<username>", methods = ['POST'])
def search(username):
    # the indexes ofsearching results
    indexes = username 
    index = -1
    has = False
    key = request.form['key'].encode()
    # only search in 'title' and 'abstract'
    for article in articles:
        index += 1
        a = re.search(key, article['title'])
        if a is not None:
            has = True
            indexes += "*" + str(index)
            continue
        a = re.search(key, article['abstract'])
        if a is not None:
            has = True
            indexes += "*" + str(index)
            continue
    if not has:
        indexes += "*no"
    return redirect(url_for("home", username = indexes))

@webApp.route("/star/<blogtitle>/<username>", methods = ['GET', 'POST'])
def star(blogtitle, username):
    blog = database.selectWhere("blog", "title", blogtitle)[0]
    user = database.selectWhere("userinfo", "username", username)[0]
    # in table "blog", username of who stared the blog will stored in column "stareduser", split in ";"
    stareduser = blog['stareduser']
    stareduser += username + ";"
    star = blog['star']
    star += 1
    # the same as "staredblog" in "userinfo"
    staredblog = user['staredblog']
    staredblog += blogtitle + ";"
    database.updateWhatWhere("blog",
                             "stareduser", stareduser,
                             "title", blogtitle)
    database.updateWhatWhere("blog",
                             "star", star,
                             "title", blogtitle)
    database.updateWhatWhere("userinfo",
                             "staredblog", staredblog,
                             "username", username)
    return redirect(url_for("home", username = "!" + username))

@webApp.route("/changecover/<covername>/<username>")
def changeCover(covername, username):
    database.updateWhatWhere("userinfo", "covername", covername, "username", username)
    return redirect(url_for("user" , username = username))

@webApp.route("/deletepic/<picname>/<username>")
def deletePic(picname, username):
    database.delete("photo", "photoname", picname)
    covername = database.selectWhatWhere("userinfo", ['covername'], "username", username)[0]['covername']
    if covername == picname:
        database.updateWhatWhere("userinfo", "covername", "default.jpg", "username", username)
    return redirect(url_for("user" , username = username))

@webApp.route("/sendmsg/<sender_recver>", methods = ['POST'])
def sendMsg(sender_recver):
    sender = sender_recver.split("@")[0]
    recver = sender_recver.split("@")[1]
    msg = request.form['msg']
    date = str(time.time())
    database.insert("message", msg, sender, recver, 0, date)
    return redirect(url_for("user" , username = sender))

if __name__ == "__main__":

    AVATAR_FOLDER = "static/file/avatar/"
    COVER_FOLDER = "static/file/cover/"
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    database = Db()
    articles = getArticle()
    webApp.run(host = "10.108.149.16", port = 5000, debug = True)
