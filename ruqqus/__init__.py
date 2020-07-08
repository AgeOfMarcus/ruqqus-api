import requests, warnings, atoma, urllib.parse

class InvalidLogin(BaseException):
    pass
class Server500(BaseException):
    pass

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
        return self.session.get(self.base + "/guild/" + boardname).json()
    def user(self, username):
        return self.session.get(self.base + "/user/" + username).json()
    def post(self, pid):
        return self.session.get(self.base + "/post/" + pid).json()
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
        return self.handle(self.session.get(f"{self.base}/guild/{name}/listing"))
    
    def user_listing(self, username):
        return self.handle(self.session.get(f"{self.base}/user/{username}/listing"))
    
    def home(self, only=None, sort="hot", t="all", page=1):
        return self.session.get(f"{self.base}/front/listing?sort={sort}&t={t}&page={page}" + ("" if not only else f"&only={only}")).json()
    
    def front_all(self, page=1, sort="hot", t="all"):
        return self.session.get(f"{self.base}/all/listing?page={page}&sort={sort}&t={t}").json()
    # </unofficial v1>

    # <unofficial>
    def get_post_title(self, url):
        return self.session.get("https://ruqqus.com/api/submit/title?url=" + urllib.parse.quote_plus(url)).json()

    def giphy(self, searchTerm="", limit=""):
        return self.session.get(f"https://ruqqus.com/giphy?searchTerm={searchTerm}&limit={limit}").json()
    
    def me(self):
        return self.session.get("https://ruqqus.com/me").url

    def random_post(self):
        return self.session.get("https://ruqqus.com/random/post").url
    
    def random_guild(self):
        return self.session.get("https://ruqqus.com/random/guild").url
    
    def random_user(self):
        return self.session.get("https://ruqqus.com/random/user").url

    def feeds_public(self, sort="hot"):
        r = self.session.get("https://ruqqus.com/feeds/" + sort)
        try:
            return atoma.parse_atom_bytes(r.content)
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
        return self.session.post("https://ruqqus.com/api/vote/post/%s/%s" % (post_id, x)).status_code == 204
    
    def vote_comment(self, comment_id, x="1"):
        return self.session.post("https://ruqqus.com/api/vote/comment/%s/%s" % (comment_id, x)).status_code == 204
    
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