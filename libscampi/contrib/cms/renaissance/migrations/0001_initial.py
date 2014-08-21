# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaInlineTemplate'
        db.create_table(u'renaissance_mediainlinetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'renaissance', ['MediaInlineTemplate'])

        # Adding M2M table for field stylesheet on 'MediaInlineTemplate'
        m2m_table_name = db.shorten_name(u'renaissance_mediainlinetemplate_stylesheet')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mediainlinetemplate', models.ForeignKey(orm[u'renaissance.mediainlinetemplate'], null=False)),
            ('stylesheet', models.ForeignKey(orm[u'communism.stylesheet'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mediainlinetemplate_id', 'stylesheet_id'])

        # Adding M2M table for field javascript on 'MediaInlineTemplate'
        m2m_table_name = db.shorten_name(u'renaissance_mediainlinetemplate_javascript')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mediainlinetemplate', models.ForeignKey(orm[u'renaissance.mediainlinetemplate'], null=False)),
            ('javascript', models.ForeignKey(orm[u'communism.javascript'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mediainlinetemplate_id', 'javascript_id'])

        # Adding model 'MediaPlaylistTemplate'
        db.create_table(u'renaissance_mediaplaylisttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('stylesheet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['communism.StyleSheet'], null=True, blank=True)),
            ('javascript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['communism.Javascript'], null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'renaissance', ['MediaPlaylistTemplate'])

        # Adding model 'ImageType'
        db.create_table(u'renaissance_imagetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inline_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaInlineTemplate'], db_column='template_id')),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'renaissance', ['ImageType'])

        # Adding model 'VideoType'
        db.create_table(u'renaissance_videotype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inline_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaInlineTemplate'], db_column='template_id')),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'renaissance', ['VideoType'])

        # Adding model 'AudioType'
        db.create_table(u'renaissance_audiotype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inline_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaInlineTemplate'], db_column='template_id')),
        ))
        db.send_create_signal(u'renaissance', ['AudioType'])

        # Adding model 'DocumentType'
        db.create_table(u'renaissance_documenttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inline_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaInlineTemplate'], db_column='template_id')),
        ))
        db.send_create_signal(u'renaissance', ['DocumentType'])

        # Adding model 'ObjectType'
        db.create_table(u'renaissance_objecttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inline_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaInlineTemplate'], db_column='template_id')),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'renaissance', ['ObjectType'])

        # Adding model 'Image'
        db.create_table(u'renaissance_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.ImageType'])),
        ))
        db.send_create_signal(u'renaissance', ['Image'])

        # Adding model 'Video'
        db.create_table(u'renaissance_video', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.VideoType'])),
            ('thumbnail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Image'], null=True)),
        ))
        db.send_create_signal(u'renaissance', ['Video'])

        # Adding model 'Audio'
        db.create_table(u'renaissance_audio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.AudioType'])),
        ))
        db.send_create_signal(u'renaissance', ['Audio'])

        # Adding model 'Document'
        db.create_table(u'renaissance_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.DocumentType'])),
        ))
        db.send_create_signal(u'renaissance', ['Document'])

        # Adding model 'Object'
        db.create_table(u'renaissance_object', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.ObjectType'])),
        ))
        db.send_create_signal(u'renaissance', ['Object'])

        # Adding model 'External'
        db.create_table(u'renaissance_external', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'renaissance', ['External'])

        # Adding model 'RankedImage'
        db.create_table(u'renaissance_rankedimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Image'])),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.ImagePlaylist'])),
        ))
        db.send_create_signal(u'renaissance', ['RankedImage'])

        # Adding model 'RankedVideo'
        db.create_table(u'renaissance_rankedvideo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Video'])),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.VideoPlaylist'])),
        ))
        db.send_create_signal(u'renaissance', ['RankedVideo'])

        # Adding model 'RankedAudio'
        db.create_table(u'renaissance_rankedaudio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('audio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Audio'])),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.AudioPlaylist'])),
        ))
        db.send_create_signal(u'renaissance', ['RankedAudio'])

        # Adding model 'RankedDocument'
        db.create_table(u'renaissance_rankeddocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Document'])),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.DocumentPlaylist'])),
        ))
        db.send_create_signal(u'renaissance', ['RankedDocument'])

        # Adding model 'RankedObject'
        db.create_table(u'renaissance_rankedobject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.Object'])),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.ObjectPlaylist'])),
        ))
        db.send_create_signal(u'renaissance', ['RankedObject'])

        # Adding model 'ImagePlaylist'
        db.create_table(u'renaissance_imageplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaPlaylistTemplate'])),
        ))
        db.send_create_signal(u'renaissance', ['ImagePlaylist'])

        # Adding model 'VideoPlaylist'
        db.create_table(u'renaissance_videoplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaPlaylistTemplate'])),
        ))
        db.send_create_signal(u'renaissance', ['VideoPlaylist'])

        # Adding model 'AudioPlaylist'
        db.create_table(u'renaissance_audioplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaPlaylistTemplate'])),
        ))
        db.send_create_signal(u'renaissance', ['AudioPlaylist'])

        # Adding model 'DocumentPlaylist'
        db.create_table(u'renaissance_documentplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaPlaylistTemplate'])),
        ))
        db.send_create_signal(u'renaissance', ['DocumentPlaylist'])

        # Adding model 'ObjectPlaylist'
        db.create_table(u'renaissance_objectplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['renaissance.MediaPlaylistTemplate'])),
        ))
        db.send_create_signal(u'renaissance', ['ObjectPlaylist'])


    def backwards(self, orm):
        # Deleting model 'MediaInlineTemplate'
        db.delete_table(u'renaissance_mediainlinetemplate')

        # Removing M2M table for field stylesheet on 'MediaInlineTemplate'
        db.delete_table(db.shorten_name(u'renaissance_mediainlinetemplate_stylesheet'))

        # Removing M2M table for field javascript on 'MediaInlineTemplate'
        db.delete_table(db.shorten_name(u'renaissance_mediainlinetemplate_javascript'))

        # Deleting model 'MediaPlaylistTemplate'
        db.delete_table(u'renaissance_mediaplaylisttemplate')

        # Deleting model 'ImageType'
        db.delete_table(u'renaissance_imagetype')

        # Deleting model 'VideoType'
        db.delete_table(u'renaissance_videotype')

        # Deleting model 'AudioType'
        db.delete_table(u'renaissance_audiotype')

        # Deleting model 'DocumentType'
        db.delete_table(u'renaissance_documenttype')

        # Deleting model 'ObjectType'
        db.delete_table(u'renaissance_objecttype')

        # Deleting model 'Image'
        db.delete_table(u'renaissance_image')

        # Deleting model 'Video'
        db.delete_table(u'renaissance_video')

        # Deleting model 'Audio'
        db.delete_table(u'renaissance_audio')

        # Deleting model 'Document'
        db.delete_table(u'renaissance_document')

        # Deleting model 'Object'
        db.delete_table(u'renaissance_object')

        # Deleting model 'External'
        db.delete_table(u'renaissance_external')

        # Deleting model 'RankedImage'
        db.delete_table(u'renaissance_rankedimage')

        # Deleting model 'RankedVideo'
        db.delete_table(u'renaissance_rankedvideo')

        # Deleting model 'RankedAudio'
        db.delete_table(u'renaissance_rankedaudio')

        # Deleting model 'RankedDocument'
        db.delete_table(u'renaissance_rankeddocument')

        # Deleting model 'RankedObject'
        db.delete_table(u'renaissance_rankedobject')

        # Deleting model 'ImagePlaylist'
        db.delete_table(u'renaissance_imageplaylist')

        # Deleting model 'VideoPlaylist'
        db.delete_table(u'renaissance_videoplaylist')

        # Deleting model 'AudioPlaylist'
        db.delete_table(u'renaissance_audioplaylist')

        # Deleting model 'DocumentPlaylist'
        db.delete_table(u'renaissance_documentplaylist')

        # Deleting model 'ObjectPlaylist'
        db.delete_table(u'renaissance_objectplaylist')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'communism.javascript': {
            'Meta': {'object_name': 'Javascript'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'base': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'external': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'precedence': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communism.Theme']"})
        },
        u'communism.stylesheet': {
            'Meta': {'object_name': 'StyleSheet'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'base': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'for_ie': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'precedence': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communism.Theme']"})
        },
        u'communism.theme': {
            'Meta': {'object_name': 'Theme'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'renaissance.audio': {
            'Meta': {'object_name': 'Audio'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.AudioType']"})
        },
        u'renaissance.audioplaylist': {
            'Meta': {'object_name': 'AudioPlaylist'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['renaissance.Audio']", 'through': u"orm['renaissance.RankedAudio']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaPlaylistTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.audiotype': {
            'Meta': {'object_name': 'AudioType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaInlineTemplate']", 'db_column': "'template_id'"}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.document': {
            'Meta': {'object_name': 'Document'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.DocumentType']"})
        },
        u'renaissance.documentplaylist': {
            'Meta': {'object_name': 'DocumentPlaylist'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['renaissance.Document']", 'through': u"orm['renaissance.RankedDocument']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaPlaylistTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.documenttype': {
            'Meta': {'object_name': 'DocumentType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaInlineTemplate']", 'db_column': "'template_id'"}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.external': {
            'Meta': {'object_name': 'External'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.image': {
            'Meta': {'object_name': 'Image'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.ImageType']"})
        },
        u'renaissance.imageplaylist': {
            'Meta': {'object_name': 'ImagePlaylist'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['renaissance.Image']", 'through': u"orm['renaissance.RankedImage']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaPlaylistTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.imagetype': {
            'Meta': {'object_name': 'ImageType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaInlineTemplate']", 'db_column': "'template_id'"}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.mediainlinetemplate': {
            'Meta': {'object_name': 'MediaInlineTemplate'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'javascript': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['communism.Javascript']", 'symmetrical': 'False', 'blank': 'True'}),
            'stylesheet': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['communism.StyleSheet']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'renaissance.mediaplaylisttemplate': {
            'Meta': {'object_name': 'MediaPlaylistTemplate'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'javascript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communism.Javascript']", 'null': 'True', 'blank': 'True'}),
            'stylesheet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communism.StyleSheet']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'renaissance.object': {
            'Meta': {'object_name': 'Object'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.ObjectType']"})
        },
        u'renaissance.objectplaylist': {
            'Meta': {'object_name': 'ObjectPlaylist'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['renaissance.Object']", 'through': u"orm['renaissance.RankedObject']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaPlaylistTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.objecttype': {
            'Meta': {'object_name': 'ObjectType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaInlineTemplate']", 'db_column': "'template_id'"}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.rankedaudio': {
            'Meta': {'ordering': "['rank']", 'object_name': 'RankedAudio'},
            'audio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Audio']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.AudioPlaylist']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.rankeddocument': {
            'Meta': {'ordering': "['rank']", 'object_name': 'RankedDocument'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.DocumentPlaylist']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.rankedimage': {
            'Meta': {'ordering': "['rank']", 'object_name': 'RankedImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Image']"}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.ImagePlaylist']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.rankedobject': {
            'Meta': {'ordering': "['rank']", 'object_name': 'RankedObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Object']"}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.ObjectPlaylist']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'renaissance.rankedvideo': {
            'Meta': {'ordering': "['rank']", 'object_name': 'RankedVideo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.VideoPlaylist']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Video']"})
        },
        u'renaissance.video': {
            'Meta': {'object_name': 'Video'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.Image']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.VideoType']"})
        },
        u'renaissance.videoplaylist': {
            'Meta': {'object_name': 'VideoPlaylist'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['renaissance.Video']", 'through': u"orm['renaissance.RankedVideo']", 'symmetrical': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaPlaylistTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'renaissance.videotype': {
            'Meta': {'object_name': 'VideoType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['renaissance.MediaInlineTemplate']", 'db_column': "'template_id'"}),
            'keyname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['renaissance']