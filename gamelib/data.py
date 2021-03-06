'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

from logging import info as log_info, debug as log_debug
import pyglet
from pyglet import font
import os

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))
pyglet.resource.path.append(data_dir)
pyglet.resource.reindex()

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

# DynamicCachingLoader is an **ABSTRACT** class.  It must be inherited
# from and the subclas MUST implement LoadResource( attname )
class DynamicCachingLoader(dict):
        def __init__(self):
                self._d = {}
        def __getattr__(self, attname):
                try:
                        return self.__dict__[attname]
                except KeyError:
                        log_info( 'loader got key err' )
                        try:
                                return self._d[attname]
                        except KeyError:
                                self.LoadResource( attname )
                                return self._d[attname]

        def __getitem__(self, key):
                try:
                        return self._d[key]
                except KeyError:
                        self.LoadResource( key )
                        return self._d[key]

        def LoadResource(self, resourceName):
                raise NotImplementedError()


class PngLoader(DynamicCachingLoader):
        def LoadResource(self, resourceName):
                #print pyglet.resource.path
                name = os.path.join( data_dir, resourceName )
                if not name.endswith('.png'):
                        name += '.png'
                try:
                        image = pyglet.image.load(name)
                except Exception, ex:
                        log_debug( ' Cannot load image: '+ name )
                        log_debug( 'Raising: '+ str(ex) )
                        raise

                self._d[resourceName] = image

class TextureLoader(DynamicCachingLoader):
        def LoadResource(self, resourceName):
                #print pyglet.resource.path
                name = os.path.join( data_dir, resourceName )
                if not name.endswith('.png'):
                        name += '.png'
                try:
                        image = pyglet.image.load(name)
                except Exception, ex:
                        log_debug( ' Cannot load image: '+ name )
                        log_debug( 'Raising: '+ str(ex) )
                        raise

                self._d[resourceName] = image.texture




soundPlayer = None
class OggLoader(DynamicCachingLoader):
        def LoadResource(self, resourceName):
                global soundPlayer
                if not soundPlayer:
                        try:
                            soundPlayer = pyglet.media.Player()
                        except Exception, ex:
                            log_info('Could not construct sound Player:%s' % ex)
                            return

                name = os.path.join( data_dir, resourceName )
                if not name.endswith('.ogg'):
                        name += '.ogg'

                try:
                    sound = pyglet.media.StaticSource(pyglet.media.load(name))
                except Exception, ex:
                    log_info('Could not construct sound Source: %s' % ex)
                    return

                self._d[resourceName] = sound

class Mp3Loader(DynamicCachingLoader):
        def LoadResource(self, resourceName):
                global soundPlayer
                if not soundPlayer:
                        try:
                            soundPlayer = pyglet.media.Player()
                        except Exception, ex:
                            log_info('Could not construct sound Player:%s' % ex)
                            return

                name = os.path.join( data_dir, resourceName )
                if not name.endswith('.mp3'):
                        name += '.mp3'

                try:
                    sound = pyglet.media.StaticSource(pyglet.media.load(name))
                except Exception, ex:
                    log_info('Could not construct sound Source: %s' % ex)
                    return

                self._d[resourceName] = sound

oggs = OggLoader()
mp3s = Mp3Loader()
pngs = PngLoader()
textures = TextureLoader()

class FontLoader(DynamicCachingLoader):
    def __init__(self):
        DynamicCachingLoader.__init__(self)
        font.add_directory(data_dir)

    def LoadResource(self, resourceName):
        size = 14
        if resourceName == 'ohcrud':
            name = 'Oh Crud BB'
        elif resourceName == 'ohcrud28':
            name = 'Oh Crud BB'
            size = 28
        elif resourceName == 'ohcrud32':
            name = 'Oh Crud BB'
            size = 32
        elif resourceName == 'schoolgirl':
            name = 'CatholicSchoolGirls BB'
        elif resourceName == 'default':
            name = 'SmackAttack BB'
        elif resourceName == 'hint':
            name = 'SmackAttack BB'
            size = 11
        else:
            name = resourceName
        try:
            myFont = font.load(name, size, bold=True)
        except Exception, ex:
            log_info('Failed loading font')
            myFont = font.load('Arial', 14, bold=True)
        self._d[resourceName] = myFont

fonts = FontLoader()

