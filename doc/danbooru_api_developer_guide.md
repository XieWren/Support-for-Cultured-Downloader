#### Test Values
:exclamation: *Please take note that all values enclosed in double quotes refer to the data values found in the json/xml data associated with the image.* :exclamation:

<table>
<tr>
    <th>Post ID</th>
    <th>Notes</th>
    <th>Related Data</th>
    <th>Type</th>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/4979439">4979439</a></td>
    <td>Pixiv Source</td>
    <td>"pixiv_id" in <a href="https://danbooru.donmai.us/posts/4979439.json">JSON file</td>
    <td rowspan=6>JSON file data</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/3500674">3500674</a></td>
    <td>Non-Pixiv Source</td>
    <td>"pixiv_id" is null.</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5459745">5459745</a></td>
    <td>Dead Pixiv Source</td>
    <td>"pixiv_id" is not null, "bad_id" in "tag_string_meta".</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5563124">5563124</a></td>
    <td>Dead Twitter Source</td>
    <td>"pixiv_id" is null, "bad_id" in "tag_string_meta".</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5522273">5522273</a></td>
    <td>Low Resolution</td>
    <td>"file_url" and "large_file_url" have the same url, "preview_file_url" is different.</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/4836157">4836157</a></td>
    <td>MD5 Hash Mismatch</td>
    <td>"md5" is not null, "md5_mismatch" in "tag_string_meta".</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/728304">728304</a></td>
    <td>Banned Post<br>[Alternate Source: <a href="https://gelbooru.com/index.php?page=post&s=view&id=5093788">5093788</a>]</td>
    <td>"md5", file_url", "large_file_url" and "preview_file_url" not available to users, but "source" and "pixiv_id" are still available. "is_banned" is set to True.</td>
    <td rowspan=4>Unique Posts</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5731350">5731350</a></td>
    <td>"Deleted" Post</td>
    <td>"is_deleted" is set to True. Image can still be accessed.</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5700082" alt="5747270">5700082</a></td>
    <td>Danbooru Gold Exclusive</td>
    <td>"md5", "file_url", "large_file_url" and "preview_file_url" not available to users, but "source" and "pixiv_id" are still available. May appear for Gold tiers and higher.</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/594502">594502</a></td>
    <td>Danbooru Gold Exclusive, Dead Pixiv Source</td>
    <td>Both effects.</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/5099296">5099296</a></td>
    <td>Video File [.mp4]</td>
    <td rowspan=2>All file types can be saved (by writing bytes to file).</td>
    <td rowspan=2>File Types</td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/1223651">1223651</a></td>
    <td>Flash Game [.swf]</td>
</tr>
<tr>
    <td><a>5199083</a></td>
    <td>1 artist, some characters</td>
    <td>Most common</td>
    <td rowspan=6>Working with Tags</td>
</tr>
<tr>
    <td><a>1370619</a></td>
    <td>1 artist, 1 character</td>
    <td></td>
</tr>
<tr>
    <td><a>5666026</a></td>
    <td>1 artist, some copyrights</td>
    <td></td>
</tr>
<tr>
    <td><a>1384660</a></td>
    <td>A few artists and copyrights</td>
    <td></td>
</tr>
<tr>
    <td><a href="https://danbooru.donmai.us/posts/728304">728304</a></td>
    <td>Many artists, many characters (but banned)</td>
    <td></td>
</tr>
<tr>
    <td><a>1747730</a></td>
    <td>No artists and characters</td>
    <td></td>
</tr>
</table>

<br>

| Pool ID      | Posts | Notes                                                               |
|--------------|-------|---------------------------------------------------------------------|
| [8][1]       | 4     | Testbooru subdomain; initial testing                                |
| [5668][2]    | 6     | 3 of 6 are Danbooru Gold exclusive                                  |
| [13182][3]   | 40    |                                                                     |
| [2802][4]    | 50    | **Small Scale Test**<br>Supported 10 concurrent async requests      |
| [3734][5]    | 195   | **Medium Scale Test**<br>Supported 5 concurrent async requests      |
| [2420][6]    | 3857  | **Large Scale Test**<br>Supported up to 3 concurrent async requests |
| [9268][7]    | 144   | Post IDs not in chrnonological order                                |
| [11180][8]   | 122   | Long title; must be wrapped                                         |

<br>

| Artist ID       | Notes                                              |
|-----------------|----------------------------------------------------|
| [25351][9]      | Has aliases, > 300 posts                           |
| [64294][10]     | Has aliases, < 300 posts                           |
| [190511][11]    | Banned artist (tagged posts automatically removed) |
| [73875][12]     | Deleted artist (still has posts)                   |

#### Async Queries
To increase query speed without overloading the server, posts are asynchronously queried in this way:
1. Posts 1-50 are queried in groups of 10.
2. Posts 50-100 are queried in groups of 5.
3. Posts 100-500 are queried in groups of 4.
4. All posts beyond this are queried in groups of 3.

As seen, the server is able to handle 3 asynchronous requests at a time without overloading. However, take note that the initial burst, if repeatedly queried, may result in server overloading.

Changes to how queries are controlled by the 'group_generation' variable in [danbooru.py][13].

#### Image Size
"image_url" contains the main image url. On the contrary, "large_image_url" contains the smaller resized image.
"size" only contains image size for the main image, but not for the smaller image, nor the percentage resized. The highest size found was only ~300KB.
This may be relevant for http query timeouts, though should not affect the current implementation.

#### Further Info
Danbooru Documentation can be found [here][14].

*[double quotes]: ""

[1]: https://testbooru.donmai.us/pools/8
[2]: https://danbooru.donmai.us/pools/5668
[3]: https://danbooru.donmai.us/pools/13182
[4]: https://danbooru.donmai.us/pools/2802
[5]: https://danbooru.donmai.us/pools/3734
[6]: https://danbooru.donmai.us/pools/2420
[7]: https://danbooru.donmai.us/pools/9268
[8]: https://danbooru.donmai.us/pools/11180
[9]: https://danbooru.donmai.us/artists/25351
[10]: https://danbooru.donmai.us/artists/64294
[11]: https://danbooru.donmai.us/artists/190511
[12]: https://danbooru.donmai.us/artists/73875
[13]: /src/utils/danbooru.py
[14]: https://danbooru.donmai.us/wiki_pages/help:api