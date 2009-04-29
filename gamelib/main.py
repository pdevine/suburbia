'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pyglet
import sky
import sound
import rabbyt

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

game_window = None

def main(sound_on=True):
    global game_window

    game_window = pyglet.window.Window(width=800, height=600)
    show_fps = True

    pyglet.clock.schedule(rabbyt.add_time)
    rabbyt.set_default_attribs()

    scene = sky.Background()

    if show_fps:
        fps_display = pyglet.clock.ClockDisplay()


    if sound_on:
        soundtrack = sound.queue_soundtrack()
        soundtrack.play()

    while not game_window.has_exit:
        tick = pyglet.clock.tick()
        game_window.dispatch_events()

        scene.update(tick)
        rabbyt.clear((scene.color))

        scene.draw()

        if show_fps:
            fps_display.draw()

        game_window.flip()


if __name__ == '__main__':
    main()
