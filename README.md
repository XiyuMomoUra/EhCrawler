# EhCrawler

1. ## Introduction

    The project is used to get all galleries' gallery_id and gallery_token of exhentai.org, then you can use them to get extra infos of any gallery.

2. ## Download the result json file

    You can download the infos from [Release](https://github.com/XiyuMomoUra/EhCrawler/releases/latest).

3. ## How to use the script

    If you want to download the info by yourself or modify the code, you need to read the following guide.

   1. ### Config the cookies

       Confirm you can log in `exhentai.org` and view the contents correctly, and get the cookies. Create a json file named `eh_cookies.json` in the same path of `main.py`. Then copy the code and replace the value in the json with your cookies' value.
       ```json
       [
         {
           "domain": ".exhentai.org",
           "name": "ipb_member_id",
           "path": "/",
           "value": "###INPUT YOUR VALUE###"
         },
         {
           "domain": ".exhentai.org",
           "name": "ipb_pass_hash",
           "path": "/",
           "value": "###INPUT YOUR VALUE###"
         },
         {
           "domain": ".exhentai.org",
           "name": "igneous",
           "path": "/",
           "value": "###INPUT YOUR VALUE###"
         },
         {
           "domain": ".exhentai.org",
           "name": "sk",
           "path": "/",
           "value": "###INPUT YOUR VALUE###"
         }
       ]
       ```
   2. ### Add edge driver
   
      Download the `msedgedriver.exe` from [Microsoft Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/), please note that the downloaded version should be consistent with the edge version installed on your computer. Then find the variable in `main.py` and modify it to your msedgedriver's path. For example:
      ```python
      edge_driver_path = r"edgedriver_win64_v143/msedgedriver.exe"
      ```

    3. ### Run the script
   
        Run the `main.py`, then the infos will be saved to `base_info.json` at the same path of `main.py`.