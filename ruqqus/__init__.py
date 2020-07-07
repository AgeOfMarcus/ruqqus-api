import requests, warnings, atoma

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
    # </unofficial v1>

    # <unofficial>
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
    # </unofficial>