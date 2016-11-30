# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

ERRORS = {
    100: "Incorrect Header Information in '{filename:}'.",
    101: "Instrument Calibration Issues in '{filename:}'.",
    102: "No Useable data in the input file '{filename:}.",
    103: "The instrument type {} is not recognised. '{filename:}'",
    104: "Data timeliness Error.",
    105: "Problem decoding header, summary, status or backscatter data line '{filename:}'.",
    106: "Unknown/Unsupported Instrument or Unrecognised file '{filename:}'.",
    107: "Error opening or reading configuration file '{filename:}'.",
    108: "Site not found or has multiple entries.",
    109: "Problems opening/reading input files.",
    110: "Number of range gates specified in the data {:d} exceeds th maximum expected.",
}


def get_error_msg(msg_id, fmt_dict, comments=None):
    """ return an error message based on the id number of the message and
    format it to send it to logger"""

    if msg_id is not ERRORS.keys():
        msg = "{} is not a valid error message id. Check it".format(msg_id)

    msg = "{:d} ".format(msg_id)
    msg += ERRORS[msg_id]

    if comments is not None:
        msg += " " + comments

    return msg
