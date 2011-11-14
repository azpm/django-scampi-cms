def static_script(url):
    html_ref = type("static_script", (object,), {
        'file': type("static_file", (object, ), {'url': u""})()
    })
    
    t = html_ref()
    t.file.url = url
    
    return t
    
def static_style(url, media = "screen", for_ie = False):
    html_ref = type("static_style", (object,), {
        'for_ie': False,
        'media': u"",
        'file': type("static_file", (object, ), {'url': u""})()
    })
    
    t = html_ref()
    
    t.media = media
    t.for_ie = for_ie
    t.file.url = url
    
    return t