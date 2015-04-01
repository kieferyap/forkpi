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
    url(r'^keypairs/edit/uid$', edit_keypair_uid, name='edit keypair uid'),
    url(r'^keypairs/delete$', delete_keypair, name='delete keypair'),
    url(r'^keypairs/toggleactive$', keypair_toggle_active, name='keypair toggle active'),
    url(r'^keypairs/scanrfid$', scan_rfid, name='scan rfid'),
    url(r'^keypairs/printpdf$', print_pdf, name='print pdf'),

    url(r'^logs/$', logs_page, name='logs'),

    url(r'^options/$', options_page, name='options'),
    url(r'^options/edit/value$', edit_option_value, name='edit option value'),
    url(r'^options/regenerate$', regenerate_secret_key, name='regenerate secret key'),

    url(r'^users$', all_users, name='users'),
    url(r'^users/toggleactiveuser$', user_toggle_active, name='user toggle active'),
    url(r'^users/togglestaff$', user_toggle_staff, name='user toggle staff'),
    url(r'^users/delete$', delete_user, name='delete user'),
    url(r'^users/approveuser$', approve_user, name='approve user'),
)
