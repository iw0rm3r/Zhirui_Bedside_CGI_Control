# Zhirui_Bedside_CGI_Control
**Set of Python scripts to control Xiaomi Philips Zhirui Bedside Lamp via any web browser**

![Zhirui_Bedside_CGI_Control](https://raw.githubusercontent.com/iw0rm3r/Zhirui_Bedside_CGI_Control/main/screenshot.png)

Simple set of Python scripts allowing you to control your **Xiaomi Philips Zhirui Bedside Lamp** from any device capable of showing basic HTML pages, or at least, capable of sending HTTP requests (for toggling the lamp). No internet connection required. Scripts have to be placed on any Python-capable device with a web-server configured to support CGI.

**Requirements:**
1.	**Server device** - can be even a Raspberry Pi, computing power doesn't matter.
2.	**Python 3.6** installation. Required by a library.
3.	**python-miio** library for communication with devices using Xiaomi miIO protocol. Located here: https://github.com/rytilahti/python-miio "How to install" manual can be found here: https://python-miio.readthedocs.io/en/latest/discovery.html#installation
4.	**Web-server** like **Apache** or **NGINX**, configured to allow CGI processing. "How to tutorial" for Apache 2 can be found here: https://httpd.apache.org/docs/2.4/howto/cgi.html All `.py` files have to be executable, so you'll need to do `chmod +x *.py` in Linux, for example.
5.	**Your lamp's IP address and token** that have to be inserted into `zhirui_settings.ini` file prior to server upload. You can find information on how to get token from your device here: https://python-miio.readthedocs.io/en/latest/discovery.html#installation There are multiple ways.
6.	**Some task scheduler**, like **cron**. It's optional, but it's a requirement for the "alarm" function. You have to set it to execute `alarm_script.py` every minute. For **cron**, the line should be something like this: `* * * * * /path/to/scripts/alarm_script.py`.

**List of scripts:**
- `zhirui_control.py` - main script, that generates HTML page for you to control the lamp. Has an icon so it can be pinned to iOS home screen like an app.
- `toggle_light.py` - one-purpose script just to toggle the lamp. Has no settings, so it's perfect for some small widget that can only generate HTTP GET requests, like **Shortcuts** (formerly **Workflow**) for iOS can create.
- `alarm_script.py` - non-CGI script that implements alarm function. Has to be executed via scheduler every minute. At the beginning of the file you can adjust settings: min/max brightness/color temperature values, turn on or off exponential-like light progression.