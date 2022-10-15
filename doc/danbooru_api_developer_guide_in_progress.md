### Test Values

┌─┬─┐
│ │ │
├─┼─┤
│ │ │
└─┴─┘
     
<!--
<table>
<tr><th>Post ID</th><th>Comments</th><th>Effects</th></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/4979439">4979439</a></td><td>Control; Pixiv Source</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/3500674">3500674</a></td><td>Non-Pixiv Source</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/5459745">5459745</a></td><td>Bad Pixiv ID</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/5563124">5563124</a></td><td>Bad Twitter ID</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/4836157">4836157</a></td><td>MD5 Hash Mismatch</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/5522273">5522273</a></td><td>Low Resolution; Only 1 Image Source</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/5700082">5700082</a></td><td>Danbooru Gold Exclusive</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/5099296">5099296</a></td><td>Video File [.mp4]</td></tr>
<tr><td><a href="https://danbooru.donmai.us/posts/1223651">1223651</a></td><td>Flash Game [.swf]</td></tr>
</table>

<table>
<tr><td></td><td></td></tr>
<tr><td></td><td></td></tr>
<tr><td></td><td></td></tr>
<tr><td></td><td></td></tr>
<tr><td></td><td></td></tr>
</table>-->


┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Post ID ┃ Comments                                    ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 4979439 │ Control; Pixiv Source                       │
├─────────┼─────────────────────────────────────────────┤
│ 1370619 │ Alternative Control; Lesser Tags            │
├─────────┼─────────────────────────────────────────────┤
│ 3500674 │ Non-Pixiv Source                            │
├─────────┼─────────────────────────────────────────────┤
│ 5459745 │ Bad Pixiv ID                                │
├─────────┼─────────────────────────────────────────────┤
│ 5563124 │ Bad Twitter ID                              │
├─────────┼─────────────────────────────────────────────┤
│ 4836157 │ MD5 Hash Mismatch                           │
├─────────┼─────────────────────────────────────────────┤
│ 5522273 │ Low Resolution; Only 1 Image Source         │
├─────────┼─────────────────────────────────────────────┤
│ 5700082 │ Danbooru Gold Exclusive                     │
├─────────┼─────────────────────────────────────────────┤
│ 594502  │ Danbooru Gold Exclusive; Bad Pixiv ID       │
├─────────┼─────────────────────────────────────────────┤
│ 728304  │ Banned Post                                 │
│         │ Several Characters, artists                 │
│         │ (Alternate Source: Gelbooru, Post 5093788)  │
├─────────┼─────────────────────────────────────────────┤
│ 5731350 │ "Deleted" Post                              │
├─────────┼─────────────────────────────────────────────┤
│ 5099296 │ Video File [.mp4]                           │
├─────────┼─────────────────────────────────────────────┤
│ 1223651 │ Flash Game [.swf]                           │
├─────────┼─────────────────────────────────────────────┤
│ 5199083 │ 1 artist, some characters. Most common.     │
├─────────┼─────────────────────────────────────────────┤
│ 5666026 │ 1 artist, some copyrights.                  │
├─────────┼─────────────────────────────────────────────┤
│ 1384660 │ Some artists, some character.               │
├─────────┼─────────────────────────────────────────────┤
│ 1747730 │ No artist, no characters                    │
├─────────┼─────────────────────────────────────────────┤
│         │                                             │
├─────────┼─────────────────────────────────────────────┤
│         │                                             │
└─────────┴─────────────────────────────────────────────┘

Banned and Danbooru Gold posts (without the allowed permissions) will not have the following json data:
- id
- md5
- file_url
- large_file_url
- preview_file_url

┏━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pool ID ┃ Posts ┃ Comments for Developers                     ┃
┡━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 8       │ 4     │ Testbooru Subdomain Used; Initial Testing   │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 5668    │ 6     │ 3 of 6 are Danbooru Gold Exclusive          │ [Process complete in 1.3957653s] 3 only
├─────────┼───────┼─────────────────────────────────────────────┤
│ 13182   │ 40    │                                             │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 2802    │ 50    │ Small Scale Test                            │ [Process complete in 3.7464037s]
│         │       │ Supported 10 concurrent async requests      │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 3734    │ 195   │ Medium Scale Test                           │ [Process complete in 9.0410813s]
│         │       │ Supported 5 concurrent async requests       │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 2420    │ 3857  │ Large Scale Test (Consistent)               │ 
│         │       │ Supported up to 3 concurrent async requests │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 9268    │ 144   │ Post IDs not in chronological order         │
├─────────┼───────┼─────────────────────────────────────────────┤
│ 11180   │ 122   │ Long title; must be wrapped                 │
├─────────┼───────┼─────────────────────────────────────────────┤
│         │       │                                             │
└─────────┴───────┴─────────────────────────────────────────────┘

Banned Artist: 190511
Deleted Artist: 73875
> 300 posts, many names: 25351
not many posts, some names: 64294



Assume 500KB for small images (highest found was ~300KB)

### For Developers
To increase query speed without overloading the server, posts are asynchronously queried in this way:
1. Posts 1-50 are queried in groups of 10.
2. Posts 50-100 are queried in groups of 5.
3. Posts 100-500 are queried in groups of 4.
4. All posts beyond this are queried in groups of 3.

As seen, the server is able to handle 3 asynchronous requests at a time without overloading. However, take note that the initial burst, if repeatedly queried, may result in server overloading.

Changes to how queries are controlled by the "group_generation" variable.