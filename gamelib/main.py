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
import data
import title
import grill
import grass

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
    game_title = title.Title()

    #frontload a big png
    blah_ = data.pngs['codesnip.png']
    mini_grill = grass.MiniGrill()
    big_grill = grill.Grill()

    if show_fps:
        fps_display = pyglet.clock.ClockDisplay()

    if sound_on:
        soundtrack = sound.queue_soundtrack()
        soundtrack.play()

    while not game_window.has_exit:
        tick = pyglet.clock.tick()
        game_window.dispatch_events()

        if big_grill.active:
            big_grill.update(tick)
            scene.color = (0.2, 0.7, 0.2)
        else:
            scene.update(tick)

        leafGenerator.update(tick)
        leafGroup.update(tick)
        wind.update(tick)
        dawg.update(tick)
        pooMaster.update(tick)
        floaterGenerator.update(tick)
        codeGenerator.update(tick)
        bubbles.bubbleMaker.update(tick)
        mowr.update(tick)

        game_title.update(tick)


        if mini_grill.active:
            big_grill.active = True
            mini_grill.active = False

        rabbyt.clear((scene.color))

        events.ConsumeEventQueue()

        if not big_grill.active:
            scene.draw()
            mini_grill.draw()
            mowr.draw()
            leafGroup.draw()
            pooMaster.draw()
            dawg.draw()
            floaterGenerator.draw()
            bubbles.bubbleMaker.draw()
            guage.draw()
            codeGenerator.draw()
        else:
            big_grill.draw()
            bubbles.bubbleMaker.draw()

        game_title.draw()

        if show_fps:
            fps_display.draw()

        game_window.flip()


if __name__ == '__main__':
    main()
