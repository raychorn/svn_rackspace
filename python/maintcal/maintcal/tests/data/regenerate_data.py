"""
regenerate computer_detail and other data used to mock responses from CORE XMLRPC Computer calls
Should only be run when the XMLRPC interface returned data structure has changed.
"""
from xmlrpclib import Server,Fault
import os
import pprint

computer_numbers = ['110004', '110005', '110006', '110007', '117773', '110001', '110002', '110003', '110008', '117775', '117779', 
    '117778','111436', '111437', '111434', '111435', '122530', '109989', '111431', '109987', '119572', '140558', '117772', '117771', 
    '121907', '176989', '117770', '131002', '154593', '117805', '117804', '117807', '117806', '117801', '117800', '117803', '117802',
    '112411', '117809', '117808', '177001', '177000', '111425', '111424', '111427', '111426', '148479', '111423', '140665', '122033',
    '122034', '122035', '122036', '122037', '117788', '117789', '115775', '115777', '115776', '115779', '115778', '115805', '115804', 
    '115803', '115802', '115801', '115800', '117782', '179969', '176995', '117783', '110899', '110898', '110945', '117780', '110947',
    '117781', '117715', '111430', '117717', '117786', '130817', '109988', '130813', '117787', '119573', '130772', '117784', '140557',
    '117799', '117798', '140555', '140554', '117776', '140552', '140551', '117791', '117790', '117793', '117792', '117794', '117797',
    '117796', '130820', '189544', '127534', '183077', '127535', '121488', '127529', '121484', '130821', '121486', '121487', '130824',
    '121483', '119728', '127531', '117774', '117768', '128751', '117769', '161305', '153337', '183294', '130776', '145349', '127588',
    '117738', '123378', '127528', '110288', '110287', '127527', '121490', '117737', '117736', '153336', '112412', '117760', '117761', 
    '189547', '189546', '189545', '165599', '117762', '184609', '130818', '130777', '117765', '110914', '110912', '122528', '110911',
    '140553', '115780', '115781', '130816', '176993', '177002', '153338', '117746', '129997', '117744', '117743', '117741', '176994',
    '130822', '123382', '129303', '110905', '110904', '110901', '110900', '110903', '110902', '189548', '140559', '118693', '118692',
    '115799', '115798', '115797', '115796', '115795', '115794', '115793', '115792', '115791', '115790', '127587', '117759', '117758',
    '127586', '123550', '123551', '117567', '121474', '121476', '123048', '160424', '163782', '130823', '118616', '127521', '130814',
    '176999', '123547', '123546', '123049', '140556', '121981', '121980', '165483', '121982', '123549', '123548', '109990', '109991',
    '109992', '109993', '109994', '109995', '109996', '109997', '109998', '109999', '117573', '117763', '117764', '117574', '117766',
    '122529', '176992', '121441', '176990', '176991', '176996', '121914', '121915', '139470', '139472', '139473', '139474', '128656',
    '117777', '140564', '140565', '140562', '140563', '140560', '140561', '241910', '220587'] # these last two are managed win/linux

xmlrpcAuthHost = ''.join(('https://',os.uname()[1],'/xmlrpc/Auth/'))
xmlrpcComputerHost = ''.join(('https://',os.uname()[1],'/xmlrpc/Computer/'))

test_user = 'nath6150'
test_pass = 'qwerty'

computer_detail_fh = open('generated_data.py','w')

def get_login_token():
    server = Server(xmlrpcAuthHost)
    try:
        token = server.userLogin(test_user, test_pass)
    except Fault, e:
        raise e
    return token

def generate_detail():
    # get the login token
    token = get_login_token()
    server = Server('::'.join((xmlrpcComputerHost,'session_id',token)))
    computer_detail = server.getDetailsByComputers(computer_numbers)
    computer_detail_fh.write("# automatically generated from regenerate_data.py DO NOT EDIT.  Copy manually edited data to frozen_data.py\ncomputer_detail =")
    computer_detail_fh.write(pprint.pformat(massage_xmlrpc_return(computer_detail)))
    computer_detail_fh.close()

def make_strings_unicode(d):
    for k,v in d.items():
        if isinstance(v,str):
            d[k] = unicode(v)

    return d

def massage_xmlrpc_return(list_of_detail_dicts):
    """The XMLRPC returns an anonymous list of dicts.
       We want the data structure to be keyed on the computer number.
       This method does that."""
    return dict([(i['server'], make_strings_unicode(i)) for i in list_of_detail_dicts])
    
if __name__ == '__main__':
    generate_detail()

