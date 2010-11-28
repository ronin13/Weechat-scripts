
import weechat
import os, datetime, subprocess, re, sys, shlex
weechat.register("notify",  "lavaramano",  "0.0.5",  "GPL", 
"notify: A real time notification system for weechat",  "",  "")

# script options
settings = {
    "show_hilights"      : "on", 
    "show_priv_msg"      : "on", 
    "nick_separator"     : ": ", 
    "icon"               : "/usr/share/pixmaps/weechat.xpm", 
    "path"               : "~/logs/me.log", 
    "urgency"            : "normal", 
    "smart_notification" : "off", 
}


# Init everything
for option,  default_value in settings.items():
    if weechat.config_get_plugin(option) == "":
        weechat.config_set_plugin(option,  default_value)

# Hook privmsg/hilights
weechat.hook_print("",  "irc_privmsg",  "",  1,  "notify_show",  "")

# Functions
def notify_show(data,  bufferp,  uber_empty,  tagsn,  isdisplayed,
        ishilight,  prefix,  message):
    """Sends highlighted message to be printed on notification"""
    try:
#        if (weechat.config_get_plugin('smart_notification') == "on" and
#                bufferp == weechat.current_buffer()):
                #bufferp == weechat.current_buffer() and focussed()):
#            pass

        if (weechat.buffer_get_string(bufferp,  "localvar_type") == "private" 
        	    and weechat.config_get_plugin('show_priv_msg') == "on"):
            show_notification(prefix,  message)

        elif (ishilight == "1" and 
                weechat.config_get_plugin('show_hilights') == "on"):
            obuffer = (weechat.buffer_get_string(bufferp,  "short_name") or
                    weechat.buffer_get_string(bufferp,  "name"))
            show_notification(obuffer,  prefix +
                    weechat.config_get_plugin('nick_separator') + message)
    except:
        write_to_file(weechat.config_get_plugin('path'),  prefix,
                'FAILED:'+message, sys.exc_info()[0])

    return weechat.WEECHAT_RC_OK

def show_notification(chan,  message):
    """
        To show notifications with custom notify-send.
    """
    chan = "Weechat: "+chan
    message = "~    "+message+"     ~"
    command=shlex.split("notify-send " + chan + message) 
    try:
        subprocess.Popen(command)
    except Exception:
        pass
    finally:
        write_to_file(weechat.config_get_plugin('path'), chan, message)


def write_to_file(path, chan, message, exception=""):
    """
        Logging the notifications/exceptions to file.
    """
    fullpath = os.path.expanduser(path)
    xfile = open(fullpath, "a")
    xfile.writelines(str(datetime.datetime.now().ctime()))
    if exception:
        xfile.writelines("\n\n EXCEPTION: --------> "+str(exception)+"<------------\n")
    xfile.writelines(" \n\nWeechat priv:==============>\n")
    xfile.writelines(str(chan+" : "+message+"\n"))
    xfile.writelines("<==============\n\n")
    xfile.close()



def focussed():
    """
        To determine whether notification be sent based on tmux window and current workspace.
    """

    # tmux display-message -p and xdotool getactivewindow getwindowpid 
    same_workspace, _ = subprocess.Popen("\
            [[ $(xdotool getactivewindow getwindowpid 2>/dev/null) == $(pidof urxvtd 2>/dev/null) ]];\
            echo -n $?", shell=True, stdout=subprocess.PIPE).communicate()
    if(same_workspace == 0):
        current, _ = subprocess.Popen("tmux display-message -p",
                shell=True, stdout=subprocess.PIPE).communicate()
        if re.match(".*weechat.*", current):
            return True 
    return False

# vim: autoindent expandtab smarttab shiftwidth=4
