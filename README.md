# ruqqus-api

This is a shitty, patched-together, unoffical API for the website ruqqus.com. This library uses 3 "different" apis. Create a RuqqusAPI object like so:

```
from ruqqus import RuqqusAPI

ruqqus = RuqqusAPI("username", "password")
```

If the login is a success, you shouldn't see any message. I'm using `requests.Session()` to save cookies and stuff, so thats accessable at `ruqqus.session` if you wanna mess around. Technically the Official v1 api methods don't need authentication, and neither do some other functons.

## Official v1
This uses their official v1 json api. All of these (very limited) functions work.

* guild(boardname) - returns json info about the specified board
* user(username) - returns json info about the specified user
* post(pid) - returns json info about the specified post referred to by its id (eg: "wmi")
* comment(cid) - returns json info about specified comment by id

## Unofficial v1
These were written from me studying the [ruqqus source code](https://github.com/ruqqus/ruqqus). As of now, none of them work, all returning server errors. The only reason i called them unofficial v1 was because the request url begins with /api/v1 and they use the @api wrapper.

* post_pid_comment_cid(pid, cid)
* delete_comment(cid)
* board_listing(boardname)
* user_listing(username)

# unofficial
A lot of these routes begin with /api, some dont. I think they all mostly work with various levels of success.

* feeds_public(sort="hot") - returns atoma listing (no clue what this is, but it works). seems to work only the first time, probably because its somewhat RSS-like
* api_comment(submission, parent_fullname, body) - I haven't gotten this to work, mainly because in the source code it mentions it requires a verified form value or whatever, also because i dunno what submission and parent_fullname refer to
* board_available(name) - checks if boardname is available. works every time, 80% of the time
* subscribe_board(boardname) and unsubscribe_board(boardname) - you can guess what these do. they work
* name_available(username) - checks if username is available. i think this works when the name is not available?
* follow_user(username) and unfollow_user(username) - havent tested this but it probably works
* agree_tos - agrees to the terms of service, presumably
* user_profile_pic(username) - you can also get this info through the official api v1 `user` function
* vote_post(post_id, x="1") and vote_comment(comment_id, x="1") - these dont work, idk why, it seems like x should be either -1. 0, or 1