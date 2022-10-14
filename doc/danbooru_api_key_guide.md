# Danbooru API Key Guide

## Introduction

This guide will help you access your API Key in order to make API calls to Danbooru.

If you are planning on accessing posts that are public (for example, posts not part of Danbooru Gold), you can skip this step by entering `"0"` into the console.

## Prerequisites

- You must have a Danbooru account.
- You are running Cultured Downloader as you follow this guide.

## Step 1: Logging in to Danbooru

<img src="/res/guide/dabooru_api_key/step-1.webp" alt="step 1" style="width: 70%;">

By using the [link][1] provided by the console, you will be prompted by Danbooru to log into the site. This may occur even if you have already logged in.

Upon logging in, you should be redirected to the [API keys page][2].

## Step 2: Generating an API key
<span style="color:red; font-weight:bolder">Please do not share your API key with anyone; this will allow them access to your account!</span>

<img src="/res/guide/dabooru_api_key/step-2.1.webp" alt="step 2.1" style="width: 70%;">

Click on the "Add" button at the top right of the page.

You will be directed to a page to create your API key, where you can:
- Provide an optional name.
- List IP addresses that can receive the key, or leave blank to allow all IPs.
   - You can find your public IP [here][3].
- Specify permissions for the key. Only the following are used by Cultured-Downloader:
   - artist:show
   - pools:show
   - posts:show
   - posts:index
   - users:profile

<img src="/res/guide/dabooru_api_key/step-2.2.webp" alt="step 2.2" style="width: 70%;">

Once you are satisfied with your API key, you create it and paste the key ID into the terminal.

## Further Info
For more information on how to get your API key, check out [this guide][4] by Danbooru themselves.


[1]: https://danbooru.donmai.us/login?url=%2Fapi_keys
[2]: https://danbooru.donmai.us/api_keys
[3]: https://whatismyipaddress.com
[4]: https://danbooru.donmai.us/wiki_pages/help:api#:~:text=returned%20during%20downbooru)-,Authentication,-You%20will%20need