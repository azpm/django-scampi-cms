from django.dispatch import Signal

#this is the default sender for handling articles
class SolidSender(object):pass
    
class ArticleChanged(object): pass
class ArticleNotChanged(object): pass

preprocess_article = Signal(providing_args=['article','context','language'])
postprocess_article = Signal(providing_args=['article', 'context','language'])