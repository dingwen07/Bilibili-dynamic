# Bilibili-dynamic
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdingwen07%2FBilibili-dynamic.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdingwen07%2FBilibili-dynamic?ref=badge_shield)


[中文版本](./README_CN.md)

### Disclaimer

**This project is only for study purpose, DO NOT use this project and any part of this project for illegal purposes. There is no warranty of any kind for this project. Project developers assume zero liability for this project, please read the [LICENSE](./LICENSE) for this project for exact terms. Please note that the services available in this project are not the officially provided by Bilibili, and may fail at any time!**

### TL;DR

Bilibili dynamic getter. User only need to provide UID / topic name to get the latest dynamic push.

---

### Components

### API

*API documentation available in [doc](./doc/api.md).*

#### Dynamic Watch

*Dynamic getter for certain UID*

- **dynamic_watch.py**

  - Compatible with: 

    - Windows
    - macOS
    - Linux

  - Requirement: 

    - `requests`

  - Way to notify user when get new dynamic(s): 

    - Commandline Output

  - Usage: 

    - Input the following in the PowerShell/CMD/Terminal: 

      ```bash
      python3 dynamic_watch.py
      ```

    - Input uploader's UID when the following text appears: 

      ```bash
      UP主UID: 
      ```

- **dynamic_watch_sound.py**

  - Compatible with: 

    - Windows

  - Requirements: 

    - `requests`
    - `playsound`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Alert Sound

  - Usage: 

    - Put the alert sound in the repository's root folder, rename it into `alert.mp3`

    - Input the following in the PowerShell/CMD: 

      ```bash
      python3 dynamic_watch_sound.py
      ```

    - Input uploader's UID when the following text appears: 

      ```bash
      UP主UID: 
      ```

- **dynamic_watch_toast_win10.py**

  - Compatible with: 

    - Windows 10

  - Requirement(s): 

    - `requests`
    - `win10toast`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Toast Notifications

  - Usage: 

    - Input the following in the PowerShell/CMD: 

      ```bash
      python3 dynamic_watch_toast_win10.py
      ```

    - Input uploader's UID when the following text appears: 

      ```bash
      UP主UID: 
      ```

- **dynamic_watch_macOS.py**

  - Compatible with: 

    - macOS

  - Requirement: 

    - `requests`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Notification Box
    - TTS for dynamics(Optional)

  - Usage: 

    - Input the following in the terminal: 

      ```bash
      python3 dynamic_watch_macOS.py
      ```

    - Input uploader's UID when the following text appears: 

      ```bash
      UP主UID：
      ```

    - Select whether turn on TTS for dynamics using letter `Y` or `N`(`Y` stands for turn on, `N` stands for close): 

      ```bash
      是否开启语音提醒功能？(Y/N)
      ```

#### Dynamic Topic Watch

*Dynamic getter for certain topic name*

- **dynamic_topic_watch.py**

  - Compatible with: 

    - Windows
    - macOS
    - Linux

  - Requirement: 

    - `requests`

  - Way to notify user when get new dynamic(s): 

    - Commandline Output

  - Usage: 

    - Input the following in the PowerShell/CMD/Terminal: 

      ```bash
      python3 dynamic_topic_watch.py
      ```

    - Input the topic name when the following text appears: 

      ```bash
      话题名称: 
      ```

- **dynamic_topic_watch_sound.py**

  - Compatible with: 

    - Windows

  - Requirements: 

    - `requests`
    - `playsound`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Alert Sound

  - Usage: 

    - Put the alert sound in the repository's root folder, rename it into `alert.mp3`

    - Input the following in the PowerShell/CMD: 

      ```bash
      python3 dynamic_topic_watch_sound.py
      ```

    - Input the topic name when the following text appears: 

      ```bash
      话题名称: 
      ```

- **dynamic_topic_watch_toast_win10.py**

  - Compatible with: 

    - Windows 10

  - Requirements: 

    - `requests`
    - `win10toast`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Toast Notifications

  - Usage: 

    - Input the following in the PowerShell/CMD: 

      ```bash
      python3 dynamic_topic_watch_toast_win10.py
      ```

    - Input the topic name when the following text appears: 

      ```bash
      话题名称: 
      ```

- **dynamic_topic_watch_macOS.py**

  - Compatible with: 

    - macOS

  - Requirement: 

    - `requests`

  - Ways to notify user when get new dynamic(s): 

    - Commandline Output
    - Notification Box
    - TTS for dynamics(Optional)

  - 使用方式：

    - Input the following in the terminal: 

      ```bash
      python3 dynamic_topic_watch_macOS.py
      ```

    - Input the topic name when the following text appears: 

      ```bash
      话题名称: 
      ```

    - Select whether turn on TTS for dynamics using letter `Y` or `N`(`Y` stands for turn on, `N` stands for close): 

      ```bash
      是否开启语音提醒功能？(Y/N)
      ```



## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdingwen07%2FBilibili-dynamic.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdingwen07%2FBilibili-dynamic?ref=badge_large)