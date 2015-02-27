from django.conf.urls import patterns, include, url
from django.contrib import admin
from records.views import *

urlpatterns = patterns('',
    url(r'^$', index_page, name='index'),
    url(r'^logout$', logout, name='logout'),

    url(r'^login/$', login_page, name='login'),
    url(r'^loggingin$', loggingin, name='loggingin'),

    url(r'^signup/$', signup_page, name='signup'),
    url(r'^adduser$', adduser, name='adduser'),

    url(r'^keypairs/$', keypairs_page, name='keypairs'),
    url(r'^addpair$', addpair, name='addpair'),
    url(r'^editname$', editname, name='editname'),
    url(r'^editpin$', editpin, name='editpin'),
    url(r'^edituid$', edituid, name='edituid'),
    url(r'^deletekeypair$', deletekeypair, name='deletekeypair'),
    url(r'^toggleactivekeypair$', toggleactivekeypair, name='toggleactivekeypair'),
    url(r'^addrfid$', addrfid, name='addrfid'),
    url(r'^printpdf$', printpdf, name='printpdf'),

    url(r'^logs/$', logs_page, name='logs'),
)
