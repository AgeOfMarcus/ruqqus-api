import requests, warnings, atoma, urllib.parse, datetime

class InvalidLogin(BaseException):
    pass
class Server500(BaseException):
    pass

class Post(object):
    def __init__(self, ruqqus, json):
        self.ruqqus = ruqqus
        self.author = ruqqus.user(json['author'])
        self.body = json['body']
        self.body_html = json['body_html']
        self.created = datetime.datetime.utcfromtimestamp(json['created_utc'])
        self.domain = json['domain']
        self.edited = 0 if json['edited_utc'] == 0 else datetime.datetime.utcfromtimestamp(json['edited_utc'])
        self.embed_url = json['embed_url']
        self.guild = ruqqus.guild(json['guild_name'])
        self.id = json['id']
        self.is_archived = json['is_archived']
        self.is_banned = json['is_banned']
        self.is_deleted = json['is_deleted']
        self.is_nsfl = json['is_nsfl']
        self.is_nsfw = json['is_nsfw']
        self.is_offensive = json['is_offensive']
        self.original_guild = ruqqus.guild(json['original_guild_name'])
        self.permalink = "https://ruqqus.com" + json['permalink']
        self.thumb_url = json['thumb_url']
        self.title = json['title']
        self.url = json['url']
        self.voted = json.get('voted')
        self.json = json
    def vote(self, v=1):
        if not v in [-1, 0, 1]: raise ValueError("Vote must be -1, 0, or 1")
        return self.ruqqus.vote_post(self.id, v)
    def reply(self, body):
        return self.ruqqus.api_comment(self.id, "t2"+self.id, body)
    def __str__(self):
        return self.title
    def __repr__(self):
        return "Post(%s)" % self.id

class User(object):
    def __init__(self, ruqqus, json):
        self.ruqqus = ruqqus
        self.badges = json['badges']
        self.banner_url = "https://ruqqus.com" + json['banner_url']
        self.comment_count = json['comment_count']
        self.comment_rep = json['comment_rep']
        self.created = datetime.datetime.utcfromtimestamp(json['created_utc'])
        self.id = json['id']
        self.is_banned = json['is_banned']
        self.permalink = "https://ruqqus.com" + json['permalink']
        self.post_count = json['post_count']
        self.post_rep = json['post_rep']
        self.profile_url = "https://ruqqus.com" + json['profile_url']
        self.title = json['title']
        self.username = json['username']
        self.json = json
    def follow(self):
        return self.ruqqus.follow_user(self.username)
    def unfollow(self):
        return self.ruqqus.unfollow_user(self.username)
    def listing(self):
        return self.ruqqus.user_listing(self.username)
    def __str__(self):
        return self.username
    def __repr__(self):
        return "User(%s)" % self.username

class Guild(object):
    def __init__(self, ruqqus, json):
        self.ruqqus = ruqqus
        self.banner_url = json['banner_url']
        self.color = json['color']
        self.created = datetime.datetime.utcfromtimestamp(json['created_utc'])
        self.description = json['description']
        self.description_html = json['description_html']
        self.id = json['id']
        self.is_banned = json['is_banned']
        self.is_private = json['is_private']
        self.is_restricted = json['is_restricted']
        self.mods_count = json['mods_count']
        self.name = json['name']
        self.over_18 = json['over_18']
        self.permalink = "https://ruqqus.com" + json['permalink']
        self.profile_url = json['profile_url']
        self.subscriber_count = json['subscriber_count']
        self.json = json
    def subscribe(self):
        return self.ruqqus.subscribe_board(self.name)
    def unsubscribe(self):
        return self.ruqqus.unsubscribe_board(self.name)
    def listing(self):
        return self.ruqqus.board_listing(self.name)
    def __str__(self):
        return self.name
    def __repr__(self):
        return "Guild(%s)" % self.name

class RuqqusAPI(object):
    def __init__(self, username, password):
        self.base = "https://ruqqus.com/api/v1"
        self.session = requests.Session()

        login = self.session.post("https://ruqqus.com/login", data={
            'username': username,
            'password': password,
        })
        if login.url == "https://ruqqus.com/":
            self.logged_in = True
        elif login.url == "https://ruqqus.com/login":
            raise InvalidLogin
        else:
            self.login = login
            warnings.warn("This result hasn't been implemented yet.")
    
    def handle(self, r):
        if r.status_code == 500:
            raise Server500(r.reason)
        else:
            try:
                return r.json()
            except:
                return r
    
    # <official v1>
    def guild(self, boardname):
        return Guild(self, self.session.get(self.base + "/guild/" + boardname).json())
    def user(self, username):
        return User(self, self.session.get(self.base + "/user/" + username).json())
    def post(self, pid):
        return Post(self, self.session.get(self.base + "/post/" + pid).json())
    def comment(self, cid):
        return self.session.get(self.base + "/comment/" + cid).json()
    # </official v1>

    # <unofficial v1>
    def post_pid_comment_cid(self, pid, cid):
        return self.handle(self.session.get(f"{self.base}/post/{pid}/comment/{cid}"))

    def delete_comment(self, cid):
        r = self.session.post(f"{self.base}/delete/comment/{cid}")
        return r.status_code == 204

    def board_listing(self, name):
        return [Post(self,x) for x in self.handle(self.session.get(f"{self.base}/guild/{name}/listing"))]
    
    def user_listing(self, username):
        return [Post(self, x) for x in self.handle(self.session.get(f"{self.base}/user/{username}/listing"))]
    
    def home(self, only=None, sort="hot", t="all", page=1):
        return [Post(self, x) for x in self.session.get(f"{self.base}/front/listing?sort={sort}&t={t}&page={page}" + ("" if not only else f"&only={only}")).json()]
    
    def front_all(self, page=1, sort="hot", t="all"):
        return [Post(self, x) for x in self.session.get(f"{self.base}/all/listing?page={page}&sort={sort}&t={t}").json()]
    # </unofficial v1>

    # <unofficial>
    def submit_post(self, title, board, url="", body="", file=None, over_18=False):
        r = self.session.post("https://ruqqus.com/submit", data={
            'title': title,
            'board': board,
            'url': url,
            'body': body,
            'over_18': over_18,
        }, files={'file': file})
        return r
    
    def delete_post(self, pid):
        return self.session.post("https://ruqqus.com/delete_post/" + pid).status_code == 204

    def create_guild(self, name, description):
        r = self.session.post("https://ruqqus.com/create_guild", data={
            'name': name,
            'description': description,
        })
        return r.url if ('+' + name) in r.url else r

    def get_post_title(self, url):
        return self.session.get("https://ruqqus.com/api/submit/title?url=" + urllib.parse.quote_plus(url)).json()

    def giphy(self, searchTerm="", limit=""):
        return self.session.get(f"https://ruqqus.com/giphy?searchTerm={searchTerm}&limit={limit}").json()
    
    def me(self):
        return self.user(self.session.get("https://ruqqus.com/me").url.split("@")[1])

    def random_post(self):
        return self.post(self.session.get("https://ruqqus.com/random/post").url.split("/")[-2])
    
    def random_guild(self):
        return self.guild(self.session.get("https://ruqqus.com/random/guild").url.split("+")[1])
    
    def random_user(self):
        return self.user(self.session.get("https://ruqqus.com/random/user").url.split("@")[1])

    def feeds_public(self, sort="hot"):
        r = self.session.get("https://ruqqus.com/feeds/" + sort)
        try:
            return [self.post(i.id_.split('/')[-2]) for i in atoma.parse_atom_bytes(r.content).entries]
        except atoma.exceptions.FeedXMLError:
            return r

    def api_comment(self, submission, parent_fullname, body):
        r = self.session.post("https://ruqqus.com/api/comment", data={
            'submission': submission,
            'parent_fullname': parent_fullname,
            'body': body
        })
        return self.handle(r)

    def board_available(self, name):
        return self.session.get("https://ruqqus.com/api/board_available/" + name).json()
    
    def subscribe_board(self, boardname):
        return self.session.post("https://ruqqus.com/api/subscribe/" + boardname).status_code == 204
    
    def unsubscribe_board(self, boardname):
        return self.session.post("https://ruqqus.com/api/unsubscribe/" + boardname).status_code == 204
    
    def name_available(self, name):
        return self.handle(self.session.get("https://ruqqus.com/api/is_available/" + name))
    
    def follow_user(self, username):
        return self.session.post("https://ruqqus.com/api/follow/" + username).status_code == 204
    
    def unfollow_user(self, username):
        return self.session.post("https://ruqqus.com/api/unfollow/" + username).status_code == 204
    
    def agree_tos(self):
        return self.session.post("https://ruqqus.com/api/agree_tos").url.endswith("/htlp/terms")
    
    def user_profile_pic(self, username):
        return self.session.get("https://ruqqus.com/@%s/pic/profile" % username).url
    
    def vote_post(self, post_id, x="1"):
        return True if (x:=self.session.post("https://ruqqus.com/api/vote/post/%s/%s" % (post_id, x))).status_code == 204 else x
    
    def vote_comment(self, comment_id, x="1"):
        return True if (x:=self.session.post("https://ruqqus.com/api/vote/comment/%s/%s" % (comment_id, x))).status_code == 204 else x
    
    def admin_image_posts_listing(self, page=1):
        return self.session.get("https://ruqqus.com/admin/image_posts?page=" + str(page)).json()
    
    def admin_ban_user(self, user_id, days=0, reason="", message=""):
        return not self.session.post("https://ruqqus.com/api/ban_user/" + user_id, data={
            "days": days,
            "reason": reason,
            "message": message
        }).status_code == 400
    
    def admin_unban_user(self, user_id, alts=False):
        return not self.session.post("https://ruqqus.com/api/unban_user/" + user_id, data={
            "alts": alts
        }).status_code == 400
    
    def admin_ban_post(self, post_id, reason=None):
        return not self.session.post("https://ruqqus.com/api/ban_post/" + post_id, data={
            "reason": reason
        }).status_code == 400
    
    def admin_unban_post(self, post_id):
        return not self.session.post("https://ruqqus.com/api/unban_post/" + post_id).status_code == 400
    
    def admin_distinguish_post(self, post_id):
        return not self.session.post("https://ruqqus.com/api/distinguish/" + post_id).status_code in [404, 403]
    
    def admin_sticky_post(self, post_id):
        return self.session.post("https://ruqqus.com/api/sticky/" + post_id).url
    
    def admin_ban_comment(self, cid):
        return self.session.post("https://ruqqus.com/api/ban_comment/" + cid).status_code == 204
    
    def admin_unban_comment(self, cid):
        return self.session.post("https://ruqqus.com/api/unban_comment/" + cid).status_code == 204
    
    def admin_distinguish_comment(self, cid):
        return self.session.post("https://ruqqus.com/api/distinguish_comment/" + cid).status_code == 204
    
    def admin_undistinguish_comment(self, cid):
        return self.session.post("https://ruqqus.com/api/undistinguish_comment/" + cid).status_code == 204
    
    def admin_ban_guild(self, bid, reason=""):
        return self.session.post("https://ruqqus.com/api/ban_guild/" + bid, data={
            "reason": reason
        }).url
    
    def admin_unban_guild(self, bid):
        return self.session.post("https://ruqqus.com/api/unban_guild/" + bid).url
    
    def admin_mod_self(self, bid):
        return self.session.post("https://ruqqus.com/api/mod_self/" + bid).url
    
    def user_stat_data(self, days=30):
        return self.session.get("https://ruqqus.com/api/user_stat_data?days=" + str(days)).json()
    
    def admin_csam_nuke(self, pid):
        return self.session.post("https://ruqqus.com/admin/csam_nuke/" + pid)
    
    def guild_profile(self, guild):
        return self.session.get("https://ruqqus.com/+%s/pic/profile" % guild).url
    # </unofficial>