from django.conf.urls.defaults import patterns

urlpatterns = patterns('metashare.oai_pmh.views',
        (r'^$', 'oaipmh_view'),
        (r'^harvest/$', 'harvest'),
        (r'^expose/$', 'expose'),
        )
