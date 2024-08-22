# RetroArch Playtime Tracker

This project is a tool to track and display playtime for various emulated games through RetroArch. It uses log files generated by RetroArch to calculate the total playtime and presents this information in a formatted table.

## Requirements

To run this project, you will need to have the following Python libraries installed:

- `tabulate`
- `colorama`

You can install these dependencies using `pip`:

```bash
pip install -r requirements.txt
````
And run the script with:

```bash
python retroarch_playtime.py your_logs_directory
```
![image](https://github.com/user-attachments/assets/90814a5a-dfed-4c73-9af6-a0e60a07c683)

this was tested on the retroarch logs obtained from MuOS on my anbernic rg35xx sp, so it may not work on other CFW or devices
