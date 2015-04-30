from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import *

urlpatterns = patterns('',
    url(r'^$', index_page, name='index'),

    url(r'^login/$', login_page, name='login'),
    url(r'^loggingin$', logging_in, name='logging in'),
    url(r'^logout$', logout, name='logout'),
    url(r'^mustbeloggedin$', must_be_logged_in, name='must be logged in'),

    url(r'^signup/$', signup_page, name='signup'),
    url(r'^adduser$', add_user, name='add user'),

    url(r'^keypairs/$', keypairs_page, name='keypairs'),
    url(r'^keypairs/add$', new_keypair, name='add keypair'),
    url(r'^keypairs/edit/name$', edit_keypair_name, name='edit keypair name'),
    url(r'^keypairs/edit/pin$', edit_keypair_pin, name='edit keypair pin'),
    url(r'^keypairs/edit/rfid$', edit_keypair_rfid, name='edit keypair rfid'),
    url(r'^keypairs/edit/fingerprint$', edit_keypair_fingerprint, name='edit keypair fingerprint'),

    url(r'^keypairs/delete$', delete_keypair, name='delete keypair'),
    url(r'^keypairs/toggleactive$', keypair_toggle_active, name='keypair toggle active'),
    url(r'^keypairs/scan/rfid$', scan_rfid, name='scan rfid'),
    url(r'^keypairs/scan/fingerprint/3x$', scan_fingerprint_3x, name='scan fingerprint 3x'),
    url(r'^keypairs/scan/fingerprint/wait$', wait_to_remove_finger, name='wait to remove finger'),
    url(r'^keypairs/scan/fingerprint/1x$', scan_fingerprint_1x, name='scan fingerprint 1x'),
    url(r'^keypairs/search', search_keypairs, name='search keypairs'),
    url(r'^keypairs/authenticate_credential$', authenticate_credential, name='authenticate credential'),

    url(r'^keypairs/link_door$', link_door_to_keypair, name='link door to keypair'),
    url(r'^keypairs/unlink_door$', unlink_door_from_keypair, name='unlink door from keypair'),

    url(r'^doors/$', doors_page, name='doors'),
    url(r'^doors/edit/name$', edit_door_name, name='edit door name'),
    url(r'^doors/search', search_doors, name='search doors'),
    url(r'^doors/link_keypair$', link_keypair_to_door, name='link keypair to door'),
    url(r'^doors/unlink_keypair$', unlink_keypair_from_door, name='unlink keypair from door'),
    
    url(r'^logs/$', logs_page, name='logs'),
    url(r'^logs/delete$', delete_logs_older_than, name='delete logs'),

    url(r'^options/$', options_page, name='options'),
    url(r'^options/edit/value$', edit_option_value, name='edit option value'),
    url(r'^options/regenerate$', regenerate_secret_key, name='regenerate secret key'),

    url(r'^users$', all_users, name='users'),
    url(r'^users/toggleactive$', user_toggle_active, name='user toggle active'),
    url(r'^users/togglestaff$', user_toggle_staff, name='user toggle staff'),
    url(r'^users/delete$', delete_user, name='delete user'),
    url(r'^users/approve$', approve_user, name='approve user'),
)
