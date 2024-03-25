import sys

import eqa.lib.settings as eqa_settings


def handleException(e: Exception, e_desc: str, e_print=True, e_log=False):
    last_exec_info = sys.exc_info()[-1]

    if last_exec_info is None:
        line_no = "???"
    else:
        line_no = str(last_exec_info.tb_lineno)

    error_string = f"{e_desc}: Error on line: {line_no}: {str(e)}"

    if e_print:
        print(error_string)
    if e_log:
        eqa_settings.log(error_string)
