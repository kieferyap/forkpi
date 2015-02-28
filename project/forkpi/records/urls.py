from django.conf.urls import patterns, include, url
from django.contrib import admin

from views import *

urlpatterns = patterns('',
    url(r'^$', index_page, name='index'),

    url(r'^login/$', login_page, name='login'),
    url(r'^loggingin$', loggingin, name='logging in'),
    url(r'^logout$', logout, name='logout'),
    url(r'^mustbeloggedin$', mustbeloggedin, name='must be logged in'),

    url(r'^signup/$', signup_page, name='signup'),
    url(r'^adduser$', adduser, name='add user'),

    url(r'^keypairs/$', keypairs_page, name='keypairs'),
    url(r'^addpair$', addpair, name='add keypair'),
    url(r'^keypairs/edit/name$', editname, name='edit keypair name'),
    url(r'^keypairs/edit/pin$', editpin, name='edit keypair pin'),
    url(r'^keypairs/edit/uid$', edituid, name='edit keypair uid'),
    url(r'^deletekeypair$', deletekeypair, name='delete keypair'),
    url(r'^toggleactivekeypair$', toggleactivekeypair, name='keypair toggle active'),
    url(r'^scanrfid$', addrfid, name='scan rfid'),
    url(r'^printpdf$', printpdf, name='print pdf'),

    url(r'^logs/$', logs_page, name='logs'),
    url(r'^options/$', options_page, name='options'),
)
