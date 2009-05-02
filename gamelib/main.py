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
import narrative
import mower
import leaves
import dog
import glitches

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main(sound_on=True, show_fps=True):
    global game_window

    game_window = pyglet.window.Window(width=800, height=600)
    window.set_window(game_window)

    pyglet.clock.schedule(rabbyt.add_time)
    rabbyt.set_default_attribs()

    storyteller = narrative.StoryTeller()

    wind = leaves.Wind()
    leafGenerator = leaves.LeafGenerator()
    leafGroup = leaves.LeafGroup()

    bubbles.init()
    bubbles.win = game_window
    storyteller = narrative.StoryTeller()

    mowr = mower.Mower()
    guage = mower.Guage(mowr)

    dawg = dog.Dog()
    pooMaster = dog.PooMaster()

    floaterGenerator = glitches.FloaterGenerator()
    codeGenerator = glitches.SourcecodeGenerator()

    scene = sky.Background(mowr)

    if show_fps:
        fps_display = pyglet.clock.ClockDisplay()

    if sound_on:
        soundtrack = sound.queue_soundtrack()
        soundtrack.play()

    while not game_window.has_exit:
        tick = pyglet.clock.tick()
        game_window.dispatch_events()

        scene.update(tick)
        leafGenerator.update(tick)
        leafGroup.update(tick)
        wind.update(tick)
        dawg.update(tick)
        floaterGenerator.update(tick)
        codeGenerator.update(tick)

        bubbles.bubbleMaker.update(tick)
        mowr.update(tick)

        rabbyt.clear((scene.color))

        events.ConsumeEventQueue()

        scene.draw()
        mowr.draw()
        leafGroup.draw()
        pooMaster.draw()
        dawg.draw()
        floaterGenerator.draw()
        bubbles.bubbleMaker.draw()
        guage.draw()
        codeGenerator.draw()

        if show_fps:
            fps_display.draw()

        game_window.flip()


if __name__ == '__main__':
    main()
