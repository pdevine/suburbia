'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pyglet
import events
import sky
import bubbles
import narrative
import sound
import rabbyt
import window

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main(sound_on=True):
    global game_window

    show_fps = True

    game_window = pyglet.window.Window(width=800, height=600)
    window.set_window(game_window)

    pyglet.clock.schedule(rabbyt.add_time)
    rabbyt.set_default_attribs()

    bubbles.init()
    bubbles.win = game_window
    storyteller = narrative.StoryTeller()

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
        bubbles.bubbleMaker.update(tick)
        rabbyt.clear((scene.color))

        events.ConsumeEventQueue()

        scene.draw()
        bubbles.bubbleMaker.draw()

        if show_fps:
            fps_display.draw()

        game_window.flip()


if __name__ == '__main__':
    main()
